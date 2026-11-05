"""Benchmarks behind the figures in _posts/2026-10-30-video-gen-infra.md.

Four experiments, each writes a CSV under --out:
  batch      DiT time vs. batch size (output_type="latent", VAE skipped)  -> batch.csv
  breakdown  end-to-end stage times for several step/CFG configs          -> breakdown.csv
  memory     per-stage peak memory, VAE tiling off / on                   -> memory.csv
  profile    GPU kernel time of the DiT split into GEMM / attention / other -> profile.csv, profile_top.csv

The hardware and software actually used are recorded in env.json; the figures read
everything from these files and nothing is filled in by hand.

Example:
  python bench.py --exp all
  python bench.py --exp batch --model Wan-AI/Wan2.2-TI2V-5B-Diffusers --height 704 --width 1280 --frames 121
"""

import argparse
import csv
import json
import os
import platform
import subprocess
import time

import torch
import diffusers
from diffusers import AutoencoderKLWan, WanPipeline

GB = 1024**3
PROMPT = "A red fox walks through a snowy forest at dawn, cinematic lighting, slow camera pan."


class StageTimer:
    """Wraps pipeline components so every call is timed and its peak memory recorded.

    Each wrapped call synchronizes the GPU before and after; the added overhead is
    small next to a DiT forward but is included in the measured times.
    """

    def __init__(self):
        self.records = []

    def wrap(self, obj, attr, stage):
        fn = getattr(obj, attr)

        def wrapped(*args, **kwargs):
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
            start = time.perf_counter()
            out = fn(*args, **kwargs)
            torch.cuda.synchronize()
            self.records.append(
                {
                    "stage": stage,
                    "ms": (time.perf_counter() - start) * 1e3,
                    "peak_alloc_gb": torch.cuda.max_memory_allocated() / GB,
                    "peak_reserved_gb": torch.cuda.max_memory_reserved() / GB,
                }
            )
            return out

        setattr(obj, attr, wrapped)

    def reset(self):
        self.records = []

    def total_ms(self, stage):
        return sum(r["ms"] for r in self.records if r["stage"] == stage)

    def calls(self, stage):
        return sum(1 for r in self.records if r["stage"] == stage)

    def peak(self, stage, key="peak_alloc_gb"):
        values = [r[key] for r in self.records if r["stage"] == stage]
        return max(values) if values else float("nan")


def load(args):
    vae_dtype = getattr(torch, args.vae_dtype)
    vae = AutoencoderKLWan.from_pretrained(args.model, subfolder="vae", torch_dtype=vae_dtype)
    pipe = WanPipeline.from_pretrained(args.model, vae=vae, torch_dtype=torch.bfloat16).to("cuda")
    pipe.set_progress_bar_config(disable=True)
    timer = StageTimer()
    timer.wrap(pipe.text_encoder, "forward", "text")
    timer.wrap(pipe.transformer, "forward", "dit")
    timer.wrap(pipe.vae, "decode", "vae")
    return pipe, timer


def run(pipe, args, *, steps, cfg, batch=1, output_type="np", **extra):
    torch.cuda.synchronize()
    start = time.perf_counter()
    pipe(
        prompt=None if "prompt_embeds" in extra else PROMPT,
        height=args.height,
        width=args.width,
        num_frames=args.frames,
        num_inference_steps=steps,
        guidance_scale=cfg,
        num_videos_per_prompt=batch,
        output_type=output_type,
        generator=torch.Generator("cuda").manual_seed(0),
        **extra,
    )
    torch.cuda.synchronize()
    return (time.perf_counter() - start) * 1e3


def base_row(args):
    return {"model": args.model, "height": args.height, "width": args.width, "frames": args.frames}


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path} ({len(rows)} rows)")


def exp_batch(pipe, timer, args):
    # The DiT is all that is timed here, so the prompt is encoded up front. Passed-in embeddings are
    # not repeated by the pipeline, so they are tiled to the batch size and run() gets batch=1.
    embeds, neg = pipe.encode_prompt(PROMPT, do_classifier_free_guidance=args.cfg > 1, device="cuda")
    if args.text_encoder_cpu:
        # Detached rather than only moved: diffusers takes the execution device from the first
        # component it finds, and a CPU text encoder would put the latents on the CPU.
        text_encoder = pipe.text_encoder
        pipe.text_encoder = None
        text_encoder.to("cpu")
        torch.cuda.empty_cache()
    rows = []
    for batch in args.batches:
        extra = {"prompt_embeds": embeds.repeat(batch, 1, 1)}
        if neg is not None:
            extra["negative_prompt_embeds"] = neg.repeat(batch, 1, 1)
        try:
            run(pipe, args, steps=2, cfg=args.cfg, output_type="latent", **extra)  # warmup
            for rep in range(args.repeats):
                timer.reset()
                wall = run(pipe, args, steps=args.batch_steps, cfg=args.cfg, output_type="latent", **extra)
                dit = timer.total_ms("dit")
                rows.append(
                    {
                        **base_row(args),
                        "steps": args.batch_steps,
                        "cfg": args.cfg,
                        "batch": batch,
                        "repeat": rep,
                        "dit_calls": timer.calls("dit"),
                        "dit_ms": dit,
                        "dit_ms_per_step": dit / args.batch_steps,
                        "videos_per_s_dit": batch / (dit / 1e3),
                        "wall_ms": wall,
                        "peak_alloc_gb": timer.peak("dit"),
                        "oom": False,
                    }
                )
        except torch.cuda.OutOfMemoryError:
            nan = float("nan")
            rows.append(
                {
                    **base_row(args),
                    "steps": args.batch_steps,
                    "cfg": args.cfg,
                    "batch": batch,
                    "repeat": 0,
                    "dit_calls": 0,
                    "dit_ms": nan,
                    "dit_ms_per_step": nan,
                    "videos_per_s_dit": nan,
                    "wall_ms": nan,
                    "peak_alloc_gb": nan,
                    "oom": True,
                }
            )
        del extra
        torch.cuda.empty_cache()
        # Written after every batch size so an OOM or a time limit keeps what already ran.
        write_csv(os.path.join(args.out, "batch.csv"), rows)
    if args.text_encoder_cpu:
        pipe.text_encoder = text_encoder.to("cuda")


def exp_breakdown(pipe, timer, args):
    rows = []
    for config in args.configs:
        steps, cfg = config.split(":")
        steps, cfg = int(steps), float(cfg)
        run(pipe, args, steps=2, cfg=cfg)  # warmup
        for rep in range(args.repeats):
            timer.reset()
            wall = run(pipe, args, steps=steps, cfg=cfg)
            text, dit, vae = timer.total_ms("text"), timer.total_ms("dit"), timer.total_ms("vae")
            rows.append(
                {
                    **base_row(args),
                    "steps": steps,
                    "cfg": cfg,
                    "repeat": rep,
                    "text_ms": text,
                    "dit_ms": dit,
                    "vae_ms": vae,
                    "other_ms": wall - text - dit - vae,
                    "wall_ms": wall,
                }
            )
        torch.cuda.empty_cache()
    write_csv(os.path.join(args.out, "breakdown.csv"), rows)


def exp_memory(pipe, timer, args):
    rows = []
    torch.cuda.empty_cache()
    resident = torch.cuda.memory_allocated() / GB
    for tiling in (False, True):
        if tiling:
            if not hasattr(pipe.vae, "enable_tiling"):
                print("VAE has no enable_tiling(); skipping tiled run")
                break
            pipe.vae.enable_tiling()
        timer.reset()
        oom = False
        try:
            run(pipe, args, steps=args.memory_steps, cfg=args.cfg)
        except torch.cuda.OutOfMemoryError:
            oom = True
        for stage in ("text", "dit", "vae"):
            rows.append(
                {
                    **base_row(args),
                    "vae_tiling": tiling,
                    "stage": stage,
                    "resident_gb": resident,
                    "peak_alloc_gb": timer.peak(stage),
                    "peak_reserved_gb": timer.peak(stage, "peak_reserved_gb"),
                    # An OOM inside a stage leaves no record for it; that stage is the one that failed.
                    "oom": oom and timer.calls(stage) == 0,
                }
            )
        torch.cuda.empty_cache()
    if hasattr(pipe.vae, "disable_tiling"):
        pipe.vae.disable_tiling()
    write_csv(os.path.join(args.out, "memory.csv"), rows)


def classify(name):
    n = name.lower()
    if any(k in n for k in ("flash", "fmha", "attention", "attn", "sdpa")):
        return "attention"
    if any(k in n for k in ("gemm", "cutlass", "xmma", "nvjet", "matmul", "cublas")):
        return "gemm"
    return "other"


def exp_profile(pipe, timer, args):
    from torch.profiler import ProfilerActivity, profile

    # Encode the prompt outside the profiled region so only DiT (and the scheduler) is captured.
    embeds, _ = pipe.encode_prompt(PROMPT, do_classifier_free_guidance=False, device="cuda")
    run(pipe, args, steps=2, cfg=1.0, output_type="latent", prompt_embeds=embeds)  # warmup
    with profile(activities=[ProfilerActivity.CUDA]) as prof:
        run(pipe, args, steps=args.profile_steps, cfg=1.0, output_type="latent", prompt_embeds=embeds)

    totals, per_kernel = {"gemm": 0.0, "attention": 0.0, "other": 0.0}, {}
    for evt in prof.events():
        if evt.device_type != torch.autograd.DeviceType.CUDA:
            continue
        ms = evt.time_range.elapsed_us() / 1e3
        totals[classify(evt.name)] += ms
        per_kernel[evt.name] = per_kernel.get(evt.name, 0.0) + ms

    all_ms = sum(totals.values())
    write_csv(
        os.path.join(args.out, "profile.csv"),
        [
            {**base_row(args), "steps": args.profile_steps, "category": k, "ms": v, "share": v / all_ms}
            for k, v in totals.items()
        ],
    )
    # Kept so the name-based classification can be checked by eye.
    top = sorted(per_kernel.items(), key=lambda kv: -kv[1])[:30]
    write_csv(
        os.path.join(args.out, "profile_top.csv"),
        [{"kernel": k, "category": classify(k), "ms": v, "share": v / all_ms} for k, v in top],
    )


def record_env(args):
    env = {
        "gpu": torch.cuda.get_device_name(0),
        "gpu_count": torch.cuda.device_count(),
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "diffusers": diffusers.__version__,
        "python": platform.python_version(),
        "model": args.model,
        "dit_dtype": "bfloat16",
        "vae_dtype": args.vae_dtype,
        "height": args.height,
        "width": args.width,
        "frames": args.frames,
        "repeats": args.repeats,
        "text_encoder_cpu_for_dit_only": args.text_encoder_cpu,
    }
    try:
        env["driver"] = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"], text=True
        ).splitlines()[0]
    except (OSError, subprocess.CalledProcessError):
        pass
    with open(os.path.join(args.out, "env.json"), "w") as f:
        json.dump(env, f, indent=2)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--exp", default="all", choices=["all", "batch", "breakdown", "memory", "profile"])
    p.add_argument("--model", default="Wan-AI/Wan2.1-T2V-1.3B-Diffusers")
    p.add_argument("--vae-dtype", default="float32", choices=["float32", "bfloat16"])
    p.add_argument("--height", type=int, default=480)
    p.add_argument("--width", type=int, default=832)
    p.add_argument("--frames", type=int, default=81)
    p.add_argument("--cfg", type=float, default=5.0)
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--batches", type=int, nargs="+", default=[1, 2, 4])
    p.add_argument("--batch-steps", type=int, default=8)
    p.add_argument("--text-encoder-cpu", action="store_true", help="move the text encoder off the GPU during --exp batch")
    p.add_argument("--configs", nargs="+", default=["50:5.0", "4:1.0"], help="steps:guidance_scale; guidance <= 1 disables CFG")
    p.add_argument("--memory-steps", type=int, default=4)
    p.add_argument("--profile-steps", type=int, default=2)
    p.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results"))
    args = p.parse_args()

    assert torch.cuda.is_available(), "needs a CUDA GPU"
    os.makedirs(args.out, exist_ok=True)
    record_env(args)
    pipe, timer = load(args)

    experiments = {"batch": exp_batch, "breakdown": exp_breakdown, "memory": exp_memory, "profile": exp_profile}
    for name in experiments if args.exp == "all" else [args.exp]:
        print(f"== {name}")
        experiments[name](pipe, timer, args)


if __name__ == "__main__":
    main()
