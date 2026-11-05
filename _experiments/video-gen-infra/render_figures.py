"""Turns the CSVs written by bench.py into HTML figures for the blog post.

Writes _includes/video-gen-infra/fig-{batch,profile,breakdown,memory}.html for the Chinese
post and fig-*-en.html for the English one. A figure whose
CSV is missing becomes a placeholder marked class="todo", so the post builds either way
and the pre-publish search for class="todo" catches it. Standard library only.

  python render_figures.py                # reads ./results
  python render_figures.py --results other/results
  python render_figures.py --lang en      # only the English figures
"""

import argparse
import csv
import html
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
INCLUDES = os.path.join(HERE, "..", "..", "_includes", "video-gen-infra")

# All visible text, per language. Keys ending in _fmt are str.format templates.
STRINGS = {
    "zh": {
        "stages": [("text", "文本编码"), ("dit", "DiT 去噪"), ("vae", "VAE 解码"), ("other", "其他")],
        "kernels": [("gemm", "GEMM"), ("attention", "Attention"), ("other", "其他")],
        "colon": "：",
        "sep": "；",
        "end": "。",
        "no_gpu": "GPU 未记录",
        "res_fmt": "{w}×{h}，{frames} 帧",
        "pending_fmt": "待补实测：在 GPU 上运行 <code>bench.py --exp {exp}</code>，再运行 <code>render_figures.py</code>。",
        "pending_kind": "实测 · 待补",
        "pending_caption": "数据来自 _experiments/video-gen-infra/results。",
        "measured_fmt": "实测 · {gpu}",
        "batch_title": "合批后的 DiT 吞吐",
        "batch_legend": ("实测吞吐", "线性扩展"),
        "batch_tip_fmt": "每步 DiT {ms:.0f} ms，峰值 {gb:.1f} GB",
        "batch_caption": "相对 batch 1 的视频吞吐，只计 DiT，VAE 未运行；虚线为吞吐随 batch 线性增长的情形。",
        "batch_setup_fmt": "{steps} 步，CFG {cfg}（每步 {calls} 次前向）",
        "repeats_fmt": "{n} 次重复取中位数",
        "profile_title": "单步 DiT 的 GPU 时间构成",
        "profile_caption_fmt": "一次 {steps} 步、无 CFG 的 DiT 推理中 GPU kernel 时间的占比；kernel 按名称归类，归类依据见 results/profile_top.csv。",
        "breakdown_title": "端到端时间分解",
        "breakdown_row_fmt": "{steps} 步 · {cfg}",
        "cfg_on": "CFG",
        "cfg_off": "无 CFG",
        "breakdown_caption": "各阶段占端到端时间的比例，右侧为总时长。少步配置使用同一个未蒸馏的 checkpoint，只用来测时间，画质不可用。",
        "memory_title": "各阶段的显存峰值",
        "tiling": "（tiling）",
        "memory_caption_fmt": "每个阶段内 torch.cuda.max_memory_allocated() 的峰值，包含常驻的模型权重（{gb:.1f} GB）。",
        "suffix": "",
    },
    "en": {
        "stages": [("text", "Text encoder"), ("dit", "DiT denoising"), ("vae", "VAE decode"), ("other", "Other")],
        "kernels": [("gemm", "GEMM"), ("attention", "Attention"), ("other", "Other")],
        "colon": ": ",
        "sep": "; ",
        "end": ".",
        "no_gpu": "GPU not recorded",
        "res_fmt": "{w}×{h}, {frames} frames",
        "pending_fmt": "Measurement pending: run <code>bench.py --exp {exp}</code> on a GPU, then <code>render_figures.py</code>.",
        "pending_kind": "Measured · pending",
        "pending_caption": "Data from _experiments/video-gen-infra/results.",
        "measured_fmt": "Measured · {gpu}",
        "batch_title": "DiT throughput under batching",
        "batch_legend": ("Measured", "Linear scaling"),
        "batch_tip_fmt": "DiT {ms:.0f} ms per step, peak {gb:.1f} GB",
        "batch_caption": "Video throughput relative to batch 1, DiT only (the VAE does not run). The dashed line marks throughput that grows linearly with batch size. ",
        "batch_setup_fmt": "{steps} steps, CFG {cfg} ({calls} forward passes per step)",
        "repeats_fmt": "median of {n} runs",
        "profile_title": "GPU time in a DiT step",
        "profile_caption_fmt": "Share of GPU kernel time in a {steps}-step DiT run without CFG. Kernels are grouped by name; see results/profile_top.csv. ",
        "breakdown_title": "End-to-end time breakdown",
        "breakdown_row_fmt": "{steps} steps · {cfg}",
        "cfg_on": "CFG",
        "cfg_off": "no CFG",
        "breakdown_caption": "Share of end-to-end time per stage, with the total on the right. The few-step setting reuses the same undistilled checkpoint to measure time only; its output is not usable. ",
        "memory_title": "Peak memory per stage",
        "tiling": " (tiling)",
        "memory_caption_fmt": "Peak torch.cuda.max_memory_allocated() within each stage, including the resident model weights ({gb:.1f} GB). ",
        "suffix": "-en",
    },
}


def read_csv(results, name):
    path = os.path.join(results, name)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return list(csv.DictReader(f))


def median(rows, key):
    return statistics.median(float(r[key]) for r in rows)


def setup(t, env, row):
    """One-line description of the measured configuration, taken from the result files."""
    model = row["model"].rstrip("/").split("/")[-1]
    parts = [
        f"{env.get('gpu', t['no_gpu'])} × 1",
        model,
        t["res_fmt"].format(w=row["width"], h=row["height"], frames=row["frames"]),
        f"DiT bf16 / VAE {env.get('vae_dtype', '?')}",
    ]
    if "diffusers" in env:
        parts.append(f"diffusers {env['diffusers']}")
    return " · ".join(html.escape(p) for p in parts)


def figure(title, kind, body, caption):
    return (
        f'<figure class="infra-figure infra-bench">\n'
        f'  <div class="infra-figure-heading"><span>{title}</span><span class="infra-figure-kind">{kind}</span></div>\n'
        f"{body}"
        f"  <figcaption>{caption}</figcaption>\n"
        f"</figure>\n"
    )


def placeholder(t, title, exp):
    body = f'  <p class="infra-note todo">{t["pending_fmt"].format(exp=exp)}</p>\n'
    return figure(title, t["pending_kind"], body, t["pending_caption"])


def measured(t, env):
    return t["measured_fmt"].format(gpu=html.escape(env.get("gpu", "")))


def legend(items):
    spans = "".join(f'<span><i class="{cls}"></i>{label}</span>' for cls, label in items)
    return f'  <div class="bench-legend">{spans}</div>\n'


def stack(t, segments):
    """segments: (css class, label, share in [0, 1], tooltip)."""
    parts = []
    for cls, label, share, tip in segments:
        if share <= 0:
            continue
        text = f"{share * 100:.0f}%" if share >= 0.08 else ""
        parts.append(
            f'<span class="bench-seg {cls}" style="flex-grow: {share:.4f}" title="{html.escape(label)}{t['colon']}{html.escape(tip)}">{text}</span>'
        )
    return f'<div class="bench-stack">{"".join(parts)}</div>'


def fig_batch(t, rows, env):
    title = t["batch_title"]
    if not rows:
        return placeholder(t, title, "batch")
    batches = sorted({int(r["batch"]) for r in rows})
    by_batch = {b: [r for r in rows if int(r["batch"]) == b] for b in batches}
    oom = {b for b in batches if any(r.get("oom") == "True" for r in by_batch[b])}
    ok = [b for b in batches if b not in oom]
    base = median(by_batch[ok[0]], "videos_per_s_dit") / ok[0]
    top = max(batches)
    body = legend(list(zip(("bench-swatch-bar", "bench-swatch-ideal"), t["batch_legend"])))
    for b in batches:
        group = by_batch[b]
        ideal = f'<span class="bench-ideal" style="left: {b / top * 100:.1f}%"></span>'
        if b in oom:
            body += (
                f'  <div class="bench-row"><span class="bench-label">batch {b}</span>'
                f'<div class="bench-track">{ideal}</div><strong class="bench-oom">OOM</strong></div>\n'
            )
            continue
        gain = median(group, "videos_per_s_dit") / base
        tip = t["batch_tip_fmt"].format(ms=median(group, "dit_ms_per_step"), gb=median(group, "peak_alloc_gb"))
        body += (
            f'  <div class="bench-row" title="{html.escape(tip)}"><span class="bench-label">batch {b}</span>'
            f'<div class="bench-track"><span class="bench-bar" style="width: {min(gain / top, 1) * 100:.1f}%"></span>'
            f"{ideal}</div>"
            f"<strong>×{gain:.2f}</strong></div>\n"
        )
    r = by_batch[ok[0]][0]
    calls = int(r["dit_calls"]) // int(r["steps"])
    caption = (
        t["batch_caption"]
        + setup(t, env, r)
        + t["sep"]
        + t["batch_setup_fmt"].format(steps=r["steps"], cfg=r["cfg"], calls=calls)
        + t["sep"]
        + t["repeats_fmt"].format(n=len(by_batch[ok[0]]))
        + t["end"]
    )
    return figure(title, measured(t, env), body, caption)


def fig_profile(t, rows, env):
    title = t["profile_title"]
    if not rows:
        return placeholder(t, title, "profile")
    share = {r["category"]: float(r["share"]) for r in rows}
    ms = {r["category"]: float(r["ms"]) for r in rows}
    classes = {"gemm": "seg-gemm", "attention": "seg-attn", "other": "seg-other"}
    body = legend([(classes[k], label) for k, label in t["kernels"]])
    segs = [(classes[k], label, share.get(k, 0), f"{ms.get(k, 0):.0f} ms") for k, label in t["kernels"]]
    body += f'  <div class="bench-row bench-row-wide">{stack(t, segs)}</div>\n'
    r = rows[0]
    caption = t["profile_caption_fmt"].format(steps=r["steps"]) + setup(t, env, r) + t["end"]
    return figure(title, measured(t, env), body, caption)


def fig_breakdown(t, rows, env):
    title = t["breakdown_title"]
    if not rows:
        return placeholder(t, title, "breakdown")
    configs = []
    for r in rows:
        key = (int(r["steps"]), float(r["cfg"]))
        if key not in configs:
            configs.append(key)
    classes = {"text": "seg-text", "dit": "seg-dit", "vae": "seg-vae", "other": "seg-other"}
    body = legend([(classes[k], label) for k, label in t["stages"]])
    for steps, cfg in configs:
        group = [r for r in rows if int(r["steps"]) == steps and float(r["cfg"]) == cfg]
        wall = median(group, "wall_ms")
        segs = []
        for k, label in t["stages"]:
            ms = median(group, f"{k}_ms")
            segs.append((classes[k], label, max(ms, 0) / wall, f"{ms / 1e3:.2f} s"))
        name = t["breakdown_row_fmt"].format(steps=steps, cfg=t["cfg_on"] if cfg > 1 else t["cfg_off"])
        body += (
            f'  <div class="bench-row"><span class="bench-label">{name}</span>{stack(t, segs)}'
            f"<strong>{wall / 1e3:.1f} s</strong></div>\n"
        )
    r = rows[0]
    caption = (
        t["breakdown_caption"]
        + setup(t, env, r)
        + t["sep"]
        + t["repeats_fmt"].format(n=len(rows) // len(configs))
        + t["end"]
    )
    return figure(title, measured(t, env), body, caption)


def fig_memory(t, rows, env):
    title = t["memory_title"]
    if not rows:
        return placeholder(t, title, "memory")
    labels = dict(t["stages"])
    entries = []
    for r in rows:
        tiled = r["vae_tiling"] == "True"
        if tiled and r["stage"] != "vae":
            continue  # tiling only changes the VAE stage
        name = labels[r["stage"]] + (t["tiling"] if tiled else "")
        oom = r["oom"] == "True"
        value = float(r["peak_alloc_gb"])
        if not oom and value != value:  # NaN: stage never ran
            continue
        entries.append((name, value, oom))
    top = max([v for _, v, oom in entries if not oom], default=1.0)
    body = ""
    for name, value, oom in entries:
        bar = "" if oom else f'<span class="bench-bar" style="width: {value / top * 100:.1f}%"></span>'
        number = '<strong class="bench-oom">OOM</strong>' if oom else f"<strong>{value:.1f} GB</strong>"
        body += (
            f'  <div class="bench-row"><span class="bench-label">{name}</span>'
            f'<div class="bench-track">{bar}</div>{number}</div>\n'
        )
    r = rows[0]
    caption = t["memory_caption_fmt"].format(gb=float(r["resident_gb"])) + setup(t, env, r) + t["end"]
    return figure(title, measured(t, env), body, caption)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", default=os.path.join(HERE, "results"))
    p.add_argument("--out", default=INCLUDES)
    p.add_argument("--lang", choices=["zh", "en", "all"], default="all")
    args = p.parse_args()

    env_path = os.path.join(args.results, "env.json")
    env = json.load(open(env_path)) if os.path.exists(env_path) else {}
    os.makedirs(args.out, exist_ok=True)
    renderers = {"batch": fig_batch, "profile": fig_profile, "breakdown": fig_breakdown, "memory": fig_memory}
    for lang in ["zh", "en"] if args.lang == "all" else [args.lang]:
        t = STRINGS[lang]
        for name, render in renderers.items():
            content = render(t, read_csv(args.results, f"{name}.csv"), env)
            path = os.path.join(args.out, f"fig-{name}{t['suffix']}.html")
            with open(path, "w") as f:
                f.write(content)
            status = " (placeholder)" if 'class="infra-note todo"' in content else ""
            print(f"wrote {os.path.relpath(path)}{status}")


if __name__ == "__main__":
    main()
