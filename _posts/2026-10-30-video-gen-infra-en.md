---
layout: distill
title: "Video generation infra: bottlenecks and trade-offs"
description: LLM-serving intuitions fail one by one on video generation — batching, acceleration, quality and streaming.
tags: video-generation mlsys diffusion
giscus_comments: false
# TODO(before publishing): set the real date (and file name) together with the Chinese post, and remove published: false
date: 2026-10-30
published: false
featured: false

authors:
  - name: Wei Zhang
    url: "https://en-2863.github.io/"
    affiliations:
      name: UIUC

bibliography: 2026-10-30-video-gen-infra.bib

# Short sections use an inline index after the opening instead of a nested sidebar TOC.
toc: false

_styles: |
  d-title h1 { text-wrap: balance; }
  d-article > p { line-height: 1.85; }
  d-article > h2 { margin-top: 2.4em; margin-bottom: .8em; padding-bottom: .35em; font-size: 25px; line-height: 1.5; scroll-margin-top: 80px; }
  .infra-section-no { display: block; color: var(--global-text-color-light); font: 11px/1.6 ui-monospace, monospace; letter-spacing: .08em; margin-bottom: 7px; }
  .infra-index { grid-column: text; display: flex; flex-wrap: wrap; gap: 8px 22px; margin: .4em 0 1.2em; font-size: 12px; line-height: 1.7; }
  d-article .infra-index a { border-bottom: 0; }
  d-article .infra-note { color: var(--global-text-color-light) !important; font-size: 12px; line-height: 1.75; margin-top: .6em; }
  d-article .infra-figure { --infra-blue: #326a94; --infra-warm: #956326; --infra-soft: rgba(69, 121, 163, .10); margin: 1.3em 0; padding: 22px 24px 18px; border: 1px solid var(--global-divider-color); border-radius: 6px; background: transparent; min-width: 0; }
  html[data-theme="dark"] .infra-figure { --infra-blue: #86b7d9; --infra-warm: #d7ad74; --infra-soft: rgba(134, 183, 217, .11); }
  .infra-figure-heading { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 6px 12px; margin-bottom: 23px; font-size: 14px; font-weight: 600; line-height: 1.6; }
  .infra-figure-kind { color: var(--global-text-color-light); font-size: 10px; font-weight: 400; }
  d-article .infra-figure figcaption { margin: 18px 0 0; color: var(--global-text-color-light); font-size: 11px; line-height: 1.8; }
  .pipeline-flow { display: grid; grid-template-columns: 1fr 24px 1.8fr 24px 1fr; align-items: stretch; }
  .pipeline-node { display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 8px; min-height: 105px; border: 1px solid var(--global-divider-color); border-radius: 4px; font-size: 13px; }
  .pipeline-node small { font-size: 11px; color: var(--global-text-color-light); }
  .pipeline-dit { border-color: var(--infra-blue); background: var(--infra-soft); color: var(--infra-blue); }
  .pipeline-arrow { align-self: center; text-align: center; color: var(--global-text-color-light); font-size: 16px; }
  .step-blocks { display: flex; gap: 4px; width: 76%; }
  .step-blocks i { flex: 1; height: 14px; border: 1px solid var(--infra-blue); border-radius: 1px; opacity: .65; }
  .pipeline-levers { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 22px; padding-top: 16px; border-top: 1px solid var(--global-divider-color); }
  .pipeline-levers > div { display: flex; flex-direction: column; gap: 5px; }
  .pipeline-levers b { font: 20px/1.5 Georgia, serif; color: var(--infra-blue); }
  .pipeline-levers span { font-size: 11px; line-height: 1.6; }
  .infra-equation { min-width: 0; text-align: center; padding: 2px 0; }
  .infra-equation mjx-container[display="true"] { max-width: 100%; overflow-x: auto; overflow-y: hidden; }
  d-article details.infra-tool { margin: 1.5em 0 .5em; padding: 0; border: 1px solid var(--global-divider-color); border-radius: 6px; background: transparent; overflow: hidden; }
  .infra-tool summary { cursor: pointer; padding: 16px 18px; font-size: 13px; line-height: 1.6; }
  .infra-tool summary small { display: inline-block; color: var(--global-text-color-light); font-size: 11px; margin-left: 10px; }
  .infra-tool[open] summary { border-bottom: 1px solid var(--global-divider-color); }
  .infra-tool[open] summary small { display: none; }
  .infra-tool-body { padding: 6px 4px 0; }
  .infra-tool-body > .infra-note { padding: 0 14px; }
  .infra-tool iframe { display: block; border: 0; }
  .stream-chart { --stream-label-width: 38px; }
  .stream-axis { position: relative; margin: 0 0 12px var(--stream-label-width); height: 22px; color: var(--global-text-color-light); font-size: 10px; white-space: nowrap; }
  .stream-deadline { position: absolute; left: 66%; top: 0; transform: translateX(-50%); }
  .stream-row { display: grid; grid-template-columns: var(--stream-label-width) 1fr; align-items: center; padding: 12px 0; }
  .stream-name { font-size: 12px; }
  .stream-track { position: relative; height: 36px; border-left: 1px solid var(--global-divider-color); background: var(--infra-soft); border-radius: 0 3px 3px 0; }
  .stream-track::after { content: ""; position: absolute; left: 66%; top: -14px; height: 64px; border-left: 1px dashed var(--infra-warm); }
  .stream-playable, .stream-stall { position: absolute; display: flex; align-items: center; justify-content: center; top: 0; height: 100%; font-size: 11px; white-space: nowrap; box-sizing: border-box; }
  .stream-playable { left: 0; background: var(--infra-blue); color: #fff; border-radius: 2px; }
  html[data-theme="dark"] .stream-playable { color: #17232d; }
  .stream-stall { color: var(--infra-warm); border: 1px dashed var(--infra-warm); background: repeating-linear-gradient(135deg, transparent, transparent 4px, rgba(179, 126, 56, .13) 4px, rgba(179, 126, 56, .13) 6px); }
  .kv-row { display: grid; grid-template-columns: 42px 1fr 40px; gap: 12px; align-items: center; margin: 17px 0; font-size: 12px; }
  .kv-label { color: var(--global-text-color-light); }
  .kv-track { height: 20px; background: var(--infra-soft); border-radius: 2px; overflow: hidden; }
  .kv-bar { display: block; height: 100%; background: var(--infra-blue); border-radius: 2px; }
  .kv-row strong { text-align: right; font: 13px/1.5 ui-monospace, monospace; color: var(--infra-blue); }
  .infra-lang { grid-column: text; display: flex; margin: 0 0 1.4em; }
  .infra-lang-switch { display: inline-flex; padding: 2px; border: 1px solid var(--global-divider-color); border-radius: 999px; font-size: 12px; line-height: 1.6; }
  .infra-lang-switch > * { padding: 2px 14px; border-radius: 999px; }
  d-article .infra-lang-switch a { border-bottom: 0; color: var(--global-text-color-light); text-decoration: none; }
  d-article .infra-lang-switch a:hover { color: var(--global-theme-color); }
  .infra-lang-switch [aria-current] { background: var(--global-theme-color); color: #fff; }
  .kv-row { grid-template-columns: 70px 1fr 40px; }
  d-article .infra-endnote { margin-top: 2.5em; padding-top: 1em; border-top: 1px solid var(--global-divider-color); }
  d-article .infra-figure { --infra-teal: #3d8279; --infra-gray: #858b92; }
  html[data-theme="dark"] .infra-figure { --infra-teal: #7cc0b5; --infra-gray: #8d939a; }
  .bench-legend { display: flex; flex-wrap: wrap; gap: 4px 16px; margin: -8px 0 6px; color: var(--global-text-color-light); font-size: 11px; }
  .bench-legend i { display: inline-block; width: 10px; height: 10px; margin-right: 6px; border-radius: 2px; vertical-align: -1px; }
  .bench-legend .bench-swatch-bar { background: var(--infra-blue); }
  .bench-legend .bench-swatch-ideal { width: 0; height: 12px; border-left: 1px dashed var(--infra-warm); border-radius: 0; }
  .bench-row { display: grid; grid-template-columns: 124px 1fr 66px; gap: 12px; align-items: center; margin: 14px 0; font-size: 12px; }
  .bench-row-wide { grid-template-columns: 1fr; }
  .bench-label { color: var(--global-text-color-light); }
  .bench-row strong { text-align: right; font: 12px/1.5 ui-monospace, monospace; color: var(--global-text-color); }
  .bench-row strong.bench-oom { color: var(--infra-warm); }
  .bench-track { position: relative; height: 20px; background: var(--infra-soft); border-radius: 2px; }
  .bench-bar { position: absolute; left: 0; top: 0; height: 100%; background: var(--infra-blue); border-radius: 2px; }
  .bench-ideal { position: absolute; top: -4px; height: 28px; border-left: 1px dashed var(--infra-warm); }
  .bench-stack { display: flex; gap: 2px; height: 22px; }
  .bench-seg { display: flex; align-items: center; justify-content: center; min-width: 2px; height: 100%; overflow: hidden; border-radius: 2px; color: #fff; font-size: 10px; white-space: nowrap; }
  html[data-theme="dark"] .bench-seg { color: #17232d; }
  .seg-dit, .seg-gemm, .bench-legend .seg-dit, .bench-legend .seg-gemm { background: var(--infra-blue); }
  .seg-text, .seg-attn, .bench-legend .seg-text, .bench-legend .seg-attn { background: var(--infra-warm); }
  .seg-vae, .bench-legend .seg-vae { background: var(--infra-teal); }
  .seg-other, .bench-legend .seg-other { background: var(--infra-gray); }
  @media (max-width: 640px) {
    .bench-row { grid-template-columns: 92px 1fr 60px; gap: 8px; }
    d-article > h2 { font-size: 21px; margin-top: 2em; }
    d-article .infra-figure { padding: 16px 12px 14px; }
    .infra-figure-heading { font-size: 13px; margin-bottom: 18px; }
    .pipeline-flow { grid-template-columns: 1fr 16px 1.6fr 16px 1fr; }
    .pipeline-node { min-height: 94px; font-size: 12px; gap: 7px; }
    .pipeline-node small { font-size: 10px; }
    .step-blocks { gap: 3px; }
    .step-blocks i { height: 11px; }
    .pipeline-levers { gap: 6px; margin-top: 17px; padding-top: 13px; }
    .pipeline-levers b { font-size: 18px; }
    .pipeline-levers span { font-size: 10px; }
    .infra-tool summary { padding: 14px 12px; }
    .stream-chart { --stream-label-width: 32px; }
    .kv-row { gap: 8px; }
  }
---

{% comment %}
Writing constraints (this Liquid comment does not appear on the page). The Chinese post is the source; keep this one in sync with it.
- Anonymous review: until MLSys results are out, do not describe CineFlow's mechanisms (scene-structured attention, bounded memory) or numbers.
- The AR paper is not submitted yet: for early KV handoff, history management and scheduling, say only that they are worth doing, not how.
- Every conclusion states its conditions, e.g. "on model X / resolution Y / GPU Z I observed…".
- Search for class="todo" before publishing.
{% endcomment %}

<nav class="infra-lang" aria-label="Language">
  <span class="infra-lang-switch">
    <a href="{{ page.url | replace: '/video-gen-infra-en/', '/video-gen-infra/' | relative_url }}" hreflang="zh" lang="zh">中文</a>
    <span aria-current="page">English</span>
  </span>
</nav>

LLM serving has built up a fairly mature set of intuitions: decode is bound by memory bandwidth, so batching adds throughput almost for free; speculative decoding speeds things up without changing the output distribution; the KV cache is the main consumer of memory; TTFT and TBT describe the user experience. Video generation inference looks like a similar problem — the same Transformers, the same questions of scheduling, parallelism and memory — yet these intuitions fail almost one by one.

This post records where and why they fail. Public material mostly covers the parts of papers that worked or vendors' final designs; the ideas that look reasonable but do not work are rarely written down, and this post starts from exactly such a case: a batching attempt that gained nothing. The numbers here are of three kinds: estimates derived from public model configs, measurements on a single A100 (marked "Measured" in the figures), and a few personal observations. Each states its conditions, and none is a complete benchmark.

<nav class="infra-index" aria-label="Contents">
  <a href="#batching">01 Batching</a>
  <a href="#acceleration">02 Acceleration</a>
  <a href="#quality">03 Quality</a>
  <a href="#streaming">04 AR and streaming</a>
  <a href="#frameworks">05 Frameworks</a>
  <a href="#outlook">06 Directions</a>
</nav>

<h2 id="batching"><span class="infra-section-no">01</span>Batching: arithmetic intensity sets the room for batching</h2>

The original idea was to bring over LLM-style continuous batching: even though most of a DiT is compute-bound, its memory-bound operations might still gain from batching, so requests would be co-batched at denoising-step boundaries. With a **5B model and long chunks**, the profile showed compute was still the bottleneck, and co-batching did not bring the expected gain.

In hindsight, this follows directly from arithmetic intensity. For a linear layer over M tokens with hidden size d, the compute is 2Md² FLOPs and the bf16 traffic is about 2(2Md + d²) bytes:

<div class="infra-equation" markdown="1">

$$
I = \frac{2Md^2}{2(2Md + d^2)} = \frac{Md}{2M + d}\quad \text{FLOP/byte}
$$

</div>

| Workload | Tokens per forward pass M | Intensity I |
|---|---:|---:|
| LLM decode, batch 1 | 1 | ≈ 1 |
| LLM decode, batch 32 | 32 | ≈ 31 |
| Wan 1.3B, 480p, 81 frames, batch 1 | 32,760 | ≈ 750 |
| Same, batch 4 | 131,040 | ≈ 763 |

<p class="infra-note">The LLM rows use d = 4096 and the Wan rows d = 1536; the VAE compresses 81 frames into 21 latent frames of 1,560 tokens each. An H100 SXM has about 989 TFLOPS of dense bf16 compute and about 3.35 TB/s of HBM bandwidth, so its ridge point is about 295 FLOP/byte. Only linear layers are counted, not attention or elementwise ops.</p>

In LLM decode, going from batch 1 to 32 raises intensity about 30×, still below the ridge point, so batching pays off almost linearly. A single video DiT request is already far above the ridge point; a larger batch only pushes I toward its ceiling of d/2 = 768. From batch 1 to 4, intensity rises by only about 2%.

{% include video-gen-infra/fig-batch-en.html %}

A larger model does not change this. For Wan2.2 TI2V 5B at 720p and 121 frames (27,280 tokens per forward pass), batch 2 still gives 1.00× the DiT throughput of batch 1; from batch 3 on, the job no longer fits on a 40 GB A100 even with the text encoder moved off the GPU. Batching does not raise throughput, and it runs into the memory limit first.

Solving I < 295 for M gives M < 295d / (d − 590): about 480 tokens at d = 1536 and about 330 at d = 5120. **Linear layers return to the memory-bound regime only when a forward pass has a few hundred tokens**, as in low-resolution text-to-image or very short clips.

So why doesn't "exploiting the memory-bound operations" work either? Elementwise ops such as norms, activations and RoPE are indeed bandwidth-bound, but their intensity does not depend on batch size: batching scales their reads, writes and compute by the same factor, so the ratio stays the same. This overhead is better handled by kernel fusion than by batching.

For this kind of workload, then, scheduling is less about filling batches and more about **when a request starts, which machine it runs on and how many GPUs it gets**. SlackServe adjusts GPU resources, step count and resolution together under SLO constraints<d-cite key="slackserve"></d-cite>; TetriServe, for text-to-image, adjusts each request's sequence-parallel degree per step<d-cite key="tetriserve"></d-cite>; GF-DiT studies elastic parallel allocation<d-cite key="gfdit"></d-cite>. All three tune how many GPUs to give and how to split the work, not how many requests to merge.

<h2 id="acceleration"><span class="infra-section-no">02</span>Acceleration: first ask which term it changes</h2>

<figure class="infra-figure infra-pipeline" aria-labelledby="pipeline-caption">
  <div class="infra-figure-heading"><span>One generation request</span><span class="infra-figure-kind">Schematic · widths are not durations</span></div>
  <div class="pipeline-flow">
    <div class="pipeline-node pipeline-fixed"><span>Text encoder</span><small>once</small></div>
    <span class="pipeline-arrow" aria-hidden="true">→</span>
    <div class="pipeline-node pipeline-dit"><span>DiT denoising</span><div class="step-blocks" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div><small>repeated N steps</small></div>
    <span class="pipeline-arrow" aria-hidden="true">→</span>
    <div class="pipeline-node pipeline-fixed"><span>VAE decode</span><small>once</small></div>
  </div>
  <div class="pipeline-levers">
    <div><b>↓ N</b><span>Few-step distillation</span></div>
    <div><b>↓ t<sub>step</sub></b><span>Sparsity / quantization / kernels</span></div>
    <div><b>↑ G</b><span>SP / communication trade-offs</span></div>
  </div>
  <figcaption id="pipeline-caption">Fewer steps, faster steps, more GPUs: each changes a different variable, so their speedups cannot simply be multiplied.</figcaption>
</figure>

<div class="infra-equation" markdown="1">

$$
\begin{aligned}
T(G) &\approx T_{\mathrm{other}}(G) + N\,t_{\mathrm{step}}(G) \\
C &= G\,T(G)
\end{aligned}
$$

</div>
<p class="infra-note">N is the step count and G the number of GPUs; t<sub>step</sub> includes communication that is not hidden, and T<sub>other</sub> collects encoding, decoding and other overhead. C is the GPU-seconds a request occupies on G GPUs.</p>

Under this decomposition, the common techniques rank roughly as **step distillation ≫ sparse attention ≈ quantization > diffusion caching > VAE optimization**. The ranking rests on which term each technique changes and where its ceiling lies, not on a particular measurement; it can shift with model, resolution and length. Kernel fusion does not fit neatly into this ranking: its gain depends mainly on how much the baseline already fuses.

**Step distillation changes N.** Methods such as DMD2 and rCM compress 20–50 steps to about 4<d-cite key="yin2024dmd2,rcm"></d-cite>, and distilled models usually no longer need CFG, which saves another half of the compute. Its costs are in quality and training, not in the inference system.

**Sparse attention changes only the attention part of t<sub>step</sub>**<d-cite key="zhang2025sta,xi2025svg"></d-cite>, so its gain is bounded by Amdahl's law. If attention takes a fraction p of a step's compute and is itself sped up s times:

<div class="infra-equation" markdown="1">

$$
S_{\mathrm{step}} = \frac{1}{(1-p) + p/s} \;\le\; \frac{1}{1-p}
$$

</div>

Estimated by FLOPs, p is about 0.7 for Wan 1.3B at 480p and 81 frames, so even if attention vanished entirely, a step would get at most about 3.4× faster. Attention compute grows with the square of the token count, so higher resolution and longer videos raise p, and the ceiling with it.

That p is a FLOPs estimate; measured by kernel time it is lower. The figure below was measured on an A100 (bf16, the FlashAttention kernel behind PyTorch SDPA, the default diffusers implementation): attention takes about 52%, which caps the per-step speedup at about 2.1×. Another 29% goes to elementwise ops such as norms, modulation and type conversions, whose FLOPs are negligible but whose time is not.

{% include video-gen-infra/fig-profile-en.html %}

The same measurement on Wan2.2 TI2V 5B (720p, 121 frames, d = 3072) puts attention at only about 39%, a per-step ceiling of about 1.6×: with a larger hidden size and fewer tokens, the linear layers take a larger share.

**Quantization also acts on t<sub>step</sub>.** FP8 has twice the peak compute of bf16, which is the theoretical ceiling for linear layers; methods like SageAttention extend quantization to attention<d-cite key="zhang2025sageattention"></d-cite>. The real gain depends on the kernel implementation and on how much accuracy loss is acceptable.

**Diffusion caching skips part of the computation in similar adjacent steps**<d-cite key="liu2025teacache"></d-cite>. It relies on adjacent steps being similar; in few-step models each step changes more, so there is less to reuse and quality is harder to control.

**Kernel fusion targets the elementwise ops inside each step.** Their FLOPs are negligible, yet in the profile above they take about 29% of kernel time; fusing norms, modulation and type conversions into neighboring kernels directly shortens t<sub>step</sub>. That share comes from the default diffusers implementation without torch.compile, though; in an inference framework that already fuses these ops, much less is left.

**VAE optimization handles the overhead outside the steps.** It is barely visible in a 50-step model, but the smaller N gets, the larger T<sub>other</sub>'s share: after distillation, encoding, decoding and data movement can go from negligible to significant. **A faster step does not mean an equally faster request, and lower latency does not mean fewer GPU-hours.**

In the A100 measurement below, VAE decoding takes only about 3% of end-to-end time at 50 steps with CFG; running the same checkpoint for just 4 steps without CFG raises that to about 43% (float32 VAE, no tiling).

{% include video-gen-infra/fig-breakdown-en.html %}

The VAE's cost is not only time: activations in the decoder grow with resolution and frame count. At the 480p, 81-frame setting below, the float32 VAE decode already peaks about 6.7 GB above DiT denoising; with tiling it drops to about the DiT's level, at the cost of decode time (not measured here).

{% include video-gen-infra/fig-memory-en.html %}

There is one more multi-GPU reason the speedups do not multiply: sparse attention reduces compute<d-cite key="zhang2025sta"></d-cite>, but if the full K/V is still sent, the compute time that Ring uses to hide communication shrinks as well<d-cite key="liu2023ring"></d-cite>. A single-GPU gain has to be re-estimated in the multi-GPU setting.

<details class="infra-tool">
  <summary><span>Try step count, GPU count and communication overhead</span><small>Open calculator</small></summary>
  <div class="infra-tool-body">
    <p class="infra-note">An analytical estimate for seeing trends; the defaults are not calibrated against measurements.</p>
    <iframe src="{{ '/assets/html/video-gen-cost-calculator-en.html' | relative_url }}" scrolling="no" height="1050" width="100%" title="Video generation inference cost calculator"></iframe>
  </div>
</details>

<h2 id="quality"><span class="infra-section-no">03</span>Quality: a harder constraint than speed</h2>

In LLM inference, one of the most influential speedups is lossless: speculative decoding guarantees the output distribution does not change. In video generation, the speedups with large gains — distillation, sparsity, quantization, caching — are almost all lossy. Quality evaluation also lacks a cheap, reliable metric like accuracy, so every speedup carries an extra evaluation cost.

**Parallelism can change the result too.** Different sequence-parallel splits, reduction orders and attention backends give different floating-point results; denoising can amplify those initial differences, so multi-GPU and single-GPU outputs may not look the same. Where reproducibility or A/B comparison matters, check this beforehand.

**Length is limited by the training distribution.** A bidirectional model's usable length is usually close to its training length; beyond that, repetition or structural collapse is common. Simply extending the sequence means extrapolating positional encodings<d-cite key="su2021roformer"></d-cite>, which the inference system cannot solve on its own.

**Changing the inference pipeline is riskier than it looks.** Injecting the previous segment's K/V into a bidirectional model, or adding an extra fusion module, both seem to carry information across segments; in my own attempts, though, the first thing such changes brought was unstable image quality. Possible causes include misaligned positional encodings and a train–inference mismatch, which I have not yet isolated one by one. Getting information in does not mean the model uses it as intended.

By contrast, video models are very sensitive to text conditioning. Without retraining, fuller and more consistent text descriptions may help cross-segment consistency more than changing the inference pipeline. This is the choice I made after experimenting so far, not a general conclusion.

<h2 id="streaming"><span class="infra-section-no">04</span>AR: fast is not enough, it has to keep up with playback</h2>

Causal generators such as CausVid and Self Forcing let video be produced segment by segment<d-cite key="yin2025causvid,huang2025selfforcing"></d-cite>. Serving metrics map onto LLM ones: the wait for the first segment resembles TTFT, and the gap between segments resembles TBT. The difference is the playback buffer: as long as the next segment finishes before the buffer runs out, the gap itself is invisible to the user. The same generation speed can feel completely different depending on the buffer margin.

<figure class="infra-figure infra-streams" aria-labelledby="streams-caption">
  <div class="infra-figure-heading"><span>Same finish time, different stall risk</span><span class="infra-figure-kind">Timing schematic</span></div>
  <div class="stream-chart" style="--stream-label-width: 70px">
    <div class="stream-axis"><span>Now</span><span class="stream-deadline">Next chunk done</span></div>
    <div class="stream-row"><span class="stream-name">Stream A</span><div class="stream-track"><div class="stream-playable" style="width: 88%">Playable buffer</div></div></div>
    <div class="stream-row"><span class="stream-name">Stream B</span><div class="stream-track"><div class="stream-playable" style="width: 32%">Buffer</div><div class="stream-stall" style="left: 32%; width: 34%">Waiting</div></div></div>
  </div>
  <figcaption id="streams-caption">The next segment finishes at the dashed line. Stream A's buffer covers this generation; stream B runs out of buffer first. Lengths only illustrate the relationship.</figcaption>
</figure>

SlackServe organizes resource allocation around exactly this remaining playable time<d-cite key="slackserve"></d-cite>. Serving goals closer to the user experience are therefore **time to the first segment, playback stalls and control responsiveness**, plus how many streams can be served under these constraints.

Autoregression also brings the KV cache back to video generation. History KV directly consumes the memory budget that streams share; for bf16 standard multi-head attention:

<div class="infra-equation" markdown="1">

$$
M_{\mathrm{KV}} = 4 L d\,n_{\mathrm{history}}\quad\text{bytes}
$$

</div>

<figure class="infra-figure infra-kv" aria-labelledby="kv-caption">
  <div class="infra-figure-heading"><span>History KV per stream</span><span class="infra-figure-kind">Capacity estimate · GB</span></div>
  <div class="kv-row"><span class="kv-label">1 frame</span><div class="kv-track"><span class="kv-bar" style="width: 6.25%"></span></div><strong>0.29</strong></div>
  <div class="kv-row"><span class="kv-label">4 frames</span><div class="kv-track"><span class="kv-bar" style="width: 25%"></span></div><strong>1.15</strong></div>
  <div class="kv-row"><span class="kv-label">16 frames</span><div class="kv-track"><span class="kv-bar" style="width: 100%"></span></div><strong>4.60</strong></div>
  <figcaption id="kv-caption">Frames are latent frames. Uses the <a href="https://github.com/Wan-Video/Wan2.1/blob/main/wan/configs/wan_t2v_1_3B.py">dimensions of Wan2.1 1.3B</a>: L = 30, d = 1536, and 1,560 tokens per frame at 480 × 832. This estimates only the KV of a same-sized AR model, excluding weights and activations, and does not imply that this bidirectional checkpoint natively supports a history cache.</figcaption>
</figure>

Most current AR video models attend only within a local window; LongLive also keeps the first frame as a sink<d-cite key="yang2025longlive"></d-cite>, the same idea as StreamingLLM<d-cite key="streamingllm"></d-cite>. The window itself is the simplest form of KV compression: it caps each stream's memory, at the cost of forgetting whatever falls outside it.

Since 2026, finer-grained KV compression has appeared on the generation side: Quant VideoGen quantizes the KV to 2 bits<d-cite key="quantvideogen"></d-cite>, and DensityKV and FrameFold select or merge history KV under a fixed budget<d-cite key="densitykv,framefold"></d-cite>. Video understanding started earlier: work such as InfiniPot-V compresses the KV of visual tokens in streaming video QA<d-cite key="infinipotv"></d-cite>.

The two problems are not the same. On the understanding side, compression saves memory; the KV is only read by the question, and tokens can be selected based on it. On the generation side, the window already bounds memory, so compression is more about **remembering a longer history within the same budget**; and every compression error is reused as a condition for all later chunks and all denoising steps, where it may accumulate into drift segment after segment. Importance-based selection heuristics from the understanding side may therefore not carry over directly.

History length, the number of streams that fit and generation quality need to be weighed as one serving problem. This is one of the directions I consider most worth investing in.

<h2 id="frameworks"><span class="infra-section-no">05</span>Frameworks: parallel libraries and serving systems</h2>

The following is based on the open-source code as of late October 2026. These projects move quickly, and details may have changed.

- **[xDiT](https://github.com/xdit-project/xDiT)** is a single-request parallel inference library: USP (a combination of Ulysses and Ring), PipeFusion and CFG parallelism, wrapping diffusers pipelines<d-cite key="fang2024xdit,fang2024usp"></d-cite>. It answers how one request is split across GPUs, not how multiple requests are scheduled. The parallel-state code in both SGLang Diffusion and vLLM-Omni traces back to it.
- **[SGLang Diffusion](https://github.com/sgl-project/sglang)** adds a serving layer on top of similar parallelism: combinations of CFG, TP and sequence parallelism, encoding, denoising and decoding that can be deployed separately, several attention backends, and dynamic batching for some models (such as Wan2.1). It also groups acceleration options into exact, lossless and high tiers by their effect on the output, which ties directly to Section 03.
- **[vLLM-Omni](https://github.com/vllm-project/vllm-omni)** targets omni-modal models. Its diffusion part runs either per request or per step; per-step execution currently covers only a few video models, one request at a time. What sets it apart is KV transfer between an AR model and a DiT, aimed at models that combine an LLM with diffusion.

Given Section 01, the value of batching and step-level scheduling in these two serving frameworks may lie mostly outside video throughput: image and low-resolution requests are still in the range where batching works; step-level execution gives a hook for preemption, interleaving and resource adjustment; and a unified request interface makes it easier to share infrastructure with LLM serving. For high-resolution video requests, batching itself is most likely not where the gains come from.

<h2 id="outlook"><span class="infra-section-no">06</span>Directions worth watching</h2>

Not every direction leaves room for infra, but the following ones change the problems an inference system has to solve:

- **AR-DiT and long video.** Breaking the training-length limit brings back the KV cache, and with it the serving problems of Section 04<d-cite key="yin2025causvid,yang2025longlive"></d-cite>.
- **Linear and hybrid attention.** Work such as SANA-Video and Video DeltaNet lowers the cost of long sequences<d-cite key="videodeltanet"></d-cite>; few open video models use it yet, so system-level optimization still lacks a target.
- **Agentic generation.** An LLM plans the shots, a VLM judges quality, and a video model generates. Candidates can share text encoding and be pruned early with cheap previews; the unit of scheduling shifts from a single request to a workflow graph.
- **3D memory and procedural scenes.** Editing an explicit scene representation makes consistency easier to guarantee; the video model moves closer to a renderer, and what the inference system must provide changes with it.

Looking back, video generation inference shares many components with LLM inference, but the bottleneck sits elsewhere: in compute, not bandwidth; in resource allocation, not batching; in quality constraints, not lossless speedups. Before carrying an LLM serving method over, first check that the assumption it relies on still holds.

<p class="infra-note infra-endnote">October 2026. Personal observations are limited to the stated settings; quality comparisons are still to come. Schematics, intensities and capacities are estimates from public configs; figures marked "Measured" come from a single A100, with the setup in each caption.</p>
