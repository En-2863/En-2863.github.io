---
layout: distill
title: 视频生成 infra：瓶颈与取舍
description: LLM serving 的直觉在视频生成上逐条失效：合批、加速、质量与流式服务。
tags: video-generation mlsys diffusion
giscus_comments: false
date: 2026-11-05
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
  d-article .infra-endnote { margin-top: 2.5em; padding-top: 1em; border-top: 1px solid var(--global-divider-color); }
  d-article .infra-figure { --infra-teal: #3d8279; --infra-gray: #858b92; }
  html[data-theme="dark"] .infra-figure { --infra-teal: #7cc0b5; --infra-gray: #8d939a; }
  .bench-legend { display: flex; flex-wrap: wrap; gap: 4px 16px; margin: -8px 0 6px; color: var(--global-text-color-light); font-size: 11px; }
  .bench-legend i { display: inline-block; width: 10px; height: 10px; margin-right: 6px; border-radius: 2px; vertical-align: -1px; }
  .bench-legend .bench-swatch-bar { background: var(--infra-blue); }
  .bench-legend .bench-swatch-ideal { width: 0; height: 12px; border-left: 1px dashed var(--infra-warm); border-radius: 0; }
  .bench-row { display: grid; grid-template-columns: 96px 1fr 66px; gap: 12px; align-items: center; margin: 14px 0; font-size: 12px; }
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
    .bench-row { grid-template-columns: 70px 1fr 60px; gap: 8px; }
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
写作约束（这段 Liquid 注释不会出现在生成的页面里）：
- 匿名审稿：MLSys 结果出来之前，不写 CineFlow 的具体机制（scene-structured attention、bounded memory）和数字。第 4 节的负面结果只写现象和教训。
- AR 那篇还没投：early KV handoff、history 管理、调度这些只写“值得做”，不写“怎么做”。
- 证据强度：每个结论都写清楚条件，比如“在 X 模型 / Y 分辨率 / Z GPU 上我观察到…”。
- 发布前搜索 class="todo"，确认全部清掉。
- 英文版在 2026-11-05-video-gen-infra-en.md，改正文时同步改；改日期/文件名时两篇一起改。
{% endcomment %}

<nav class="infra-lang" aria-label="语言">
  <span class="infra-lang-switch">
    <span aria-current="page">中文</span>
    <a href="{{ page.url | replace: '/video-gen-infra/', '/video-gen-infra-en/' | relative_url }}" hreflang="en" lang="en">English</a>
  </span>
</nav>

LLM serving 已经积累了一套相对成熟的直觉：decode 受内存带宽限制，合批几乎可以白赚吞吐；speculative decoding 能在不改变输出分布的前提下加速；KV cache 是显存的主要占用；TTFT 与 TBT 刻画用户体验。视频生成推理看起来是相近的问题——同样是 Transformer，同样涉及调度、并行与显存管理——但上面这几条直觉几乎逐条失效。

本文记录这些直觉在哪里失效、为什么失效。公开材料大多是论文的成功部分或厂商的最终方案，“看起来合理却走不通”的那一层很少被写下来，而本文的起点正是一次没有收益的 batching 尝试。文中的数字分三类：按公开模型配置推得的估算、单张 A100 上的实测（图中标为“实测”），以及少量个人观察；均注明条件，都不是完整的 benchmark。

<nav class="infra-index" aria-label="文章导航">
  <a href="#batching">01 Batching</a>
  <a href="#acceleration">02 加速</a>
  <a href="#quality">03 质量</a>
  <a href="#streaming">04 AR 与流式</a>
  <a href="#frameworks">05 框架</a>
  <a href="#outlook">06 方向</a>
</nav>

<h2 id="batching"><span class="infra-section-no">01</span>Batching：算术强度决定合批空间</h2>

最初的设想是把 LLM 的 continuous batching 搬过来：即使 DiT 的主体是 compute-bound，其中的 memory-bound 操作或许仍能从合批中获益，于是按 denoising step 的边界做 co-batch。在 **5B 模型、长 chunk** 的配置下，profile 显示瓶颈仍是计算，co-batch 也没有带来预期收益。

事后看，这个结果可以从算术强度直接推出。对 M 个 token、隐藏维度 d 的线性层，计算量为 2Md²，bf16 下的读写量约为 2(2Md + d²) 字节：

<div class="infra-equation" markdown="1">

$$
I = \frac{2Md^2}{2(2Md + d^2)} = \frac{Md}{2M + d}\quad \text{FLOP/byte}
$$

</div>

| 负载 | 每次前向的 token 数 M | 强度 I |
|---|---:|---:|
| LLM decode，batch 1 | 1 | ≈ 1 |
| LLM decode，batch 32 | 32 | ≈ 31 |
| Wan 1.3B，480p、81 帧，batch 1 | 32,760 | ≈ 750 |
| 同上，batch 4 | 131,040 | ≈ 763 |

<p class="infra-note">LLM 行取 d = 4096，Wan 行取 d = 1536；81 帧经 VAE 压缩为 21 个 latent 帧，每帧 1,560 token。H100 SXM 的 bf16 稠密算力约 989 TFLOPS、HBM 带宽约 3.35 TB/s，拐点约 295 FLOP/byte。只计线性层，不含 attention 与逐元素算子。</p>

LLM decode 中，batch 从 1 增至 32，强度提高约 30 倍，仍在拐点以下，合批的收益几乎线性。视频 DiT 的单个请求已经远超拐点，batch 再大也只是把 I 推向 d/2 = 768 的上限：从 batch 1 到 4，强度只提高约 2%。

{% include video-gen-infra/fig-batch.html %}

换成更大的模型，结论不变：Wan2.2 TI2V 5B 在 720p、121 帧下（每次前向 27,280 token），batch 2 的 DiT 吞吐仍是 batch 1 的 1.00 倍；batch 3 起，即使把文本编码器移出显存，40 GB 的 A100 也放不下。合批不仅不提高吞吐，还会先撞上显存上限。

反过来解 I < 295，得到 M < 295d / (d − 590)：d = 1536 时约 480 token，d = 5120 时约 330 token。**只有单次前向的 token 数降到几百量级，线性层才回到 memory-bound 区间**，例如低分辨率的文生图，或非常短的片段。

那么“利用其中的 memory-bound 操作”为什么也不成立？norm、激活、RoPE 这类逐元素算子确实受带宽限制，但它们的强度与 batch 无关：合批只是把读写和计算按同样倍数放大，比例不变。这类开销更适合用 kernel fusion 处理，而不是合批。

因此，这类负载的调度重心不在“凑 batch”，而在**何时启动、放在哪台机器、分配多少 GPU**。SlackServe 在 SLO 约束下同时调整 GPU 资源、步数与分辨率<d-cite key="slackserve"></d-cite>；TetriServe 面向文生图，按 step 调整每个请求的序列并行度<d-cite key="tetriserve"></d-cite>；GF-DiT 研究弹性的并行分配<d-cite key="gfdit"></d-cite>。三者调的都是“给多少卡、怎么切”，而不是“合多少请求”。

<h2 id="acceleration"><span class="infra-section-no">02</span>加速：先看它改变哪一项</h2>

<figure class="infra-figure infra-pipeline" aria-labelledby="pipeline-caption">
  <div class="infra-figure-heading"><span>一次生成请求</span><span class="infra-figure-kind">流程示意 · 宽度不代表耗时</span></div>
  <div class="pipeline-flow">
    <div class="pipeline-node pipeline-fixed"><span>文本编码</span><small>一次</small></div>
    <span class="pipeline-arrow" aria-hidden="true">→</span>
    <div class="pipeline-node pipeline-dit"><span>DiT 去噪</span><div class="step-blocks" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div><small>重复 N 步</small></div>
    <span class="pipeline-arrow" aria-hidden="true">→</span>
    <div class="pipeline-node pipeline-fixed"><span>VAE 解码</span><small>一次</small></div>
  </div>
  <div class="pipeline-levers">
    <div><b>↓ N</b><span>少步蒸馏</span></div>
    <div><b>↓ t<sub>step</sub></b><span>稀疏 / 量化 / 算子优化</span></div>
    <div><b>↑ G</b><span>SP / 通信取舍</span></div>
  </div>
  <figcaption id="pipeline-caption">减少步数、缩短单步、增加 GPU：改变的是不同变量，不能直接相乘各自的加速比。</figcaption>
</figure>

<div class="infra-equation" markdown="1">

$$
\begin{aligned}
T(G) &\approx T_{\mathrm{other}}(G) + N\,t_{\mathrm{step}}(G) \\
C &= G\,T(G)
\end{aligned}
$$

</div>
<p class="infra-note">N 为步数，G 为 GPU 数；t<sub>step</sub> 含未被隐藏的通信，T<sub>other</sub> 汇总编码、解码等开销。C 为请求占用 G 张卡期间的 GPU-seconds。</p>

按这个分解，常见手段的收益大致可以排序为：**步数蒸馏 ≫ 稀疏 attention ≈ 量化 > diffusion cache > VAE 优化**。排序依据是每种手段能改变哪一项、上限在哪里，而不是某组具体实测；模型、分辨率与时长不同，排序可能变化。kernel fusion 不容易放进这个排序：它的收益主要取决于基线实现已经融合了多少。

**步数蒸馏改变 N。** DMD2、rCM 等方法可将 20–50 步压缩到 4 步左右<d-cite key="yin2024dmd2,rcm"></d-cite>，蒸馏后的模型通常也不再需要 CFG，等于再省去一半计算。它的代价在质量和训练成本上，而不在推理系统里。

**稀疏 attention 只改变 t<sub>step</sub> 中 attention 的部分**<d-cite key="zhang2025sta,xi2025svg"></d-cite>，收益受 Amdahl 定律约束。设 attention 占单步计算的比例为 p、自身加速 s 倍：

<div class="infra-equation" markdown="1">

$$
S_{\mathrm{step}} = \frac{1}{(1-p) + p/s} \;\le\; \frac{1}{1-p}
$$

</div>

按 FLOPs 估算，Wan 1.3B 在 480p、81 帧下 p 约为 0.7，即使 attention 完全消失，单步加速也不超过约 3.4×。attention 的计算随 token 数平方增长，分辨率与时长越大，p 越高，上限随之提高。

上面的 p 是按 FLOPs 估算的，按 kernel 时间算会更低。下图在 A100 上实测（bf16，PyTorch SDPA 的 FlashAttention 内核，diffusers 默认实现）：attention 约占 52%，对应的单步上限约 2.1×；另有约 29% 落在 norm、调制、类型转换等逐元素算子上，这些算子的 FLOPs 可以忽略，时间却不能。

{% include video-gen-infra/fig-profile.html %}

同样的测量换到 Wan2.2 TI2V 5B（720p、121 帧，d = 3072）上，attention 只占约 39%，单步上限约 1.6×：隐藏维度更大、token 数更少时，线性层的份额随之上升。

**量化同样作用于 t<sub>step</sub>。** FP8 相对 bf16 的峰值算力为 2 倍，这是线性层的理论上限；SageAttention 一类方法把量化延伸到 attention<d-cite key="zhang2025sageattention"></d-cite>。实际收益取决于 kernel 实现与可接受的精度损失。

**diffusion cache 跳过相邻相似步的部分计算**<d-cite key="liu2025teacache"></d-cite>。它依赖相邻步之间的相似性；少步模型中每一步的变化更大，可复用的空间相应缩小，质量也更难控制。

**kernel fusion 作用于单步之内的逐元素算子。** 这些算子的 FLOPs 可以忽略，在前面的 profile 图里却占了约 29% 的 kernel 时间；把 norm、调制、类型转换融进相邻的 kernel，能直接缩短 t<sub>step</sub>。不过这个比例来自 diffusers 的默认实现，没有开 torch.compile；在已经做过融合的推理框架里，剩下的空间会小得多。

**VAE 优化处理的是单步之外的开销。** 它在 50 步的模型上不显眼，但 N 越小，T<sub>other</sub> 的占比越高：蒸馏之后，编码、解码与数据搬运可能从可以忽略变为不可忽略。**单步快，不等于端到端同样快；延迟低，也不等于用卡更省。**

下图的 A100 实测中，50 步、带 CFG 时 VAE 解码只占端到端时间的约 3%；同一 checkpoint 只跑 4 步、关闭 CFG 时，这一比例升至约 43%（VAE 为 float32、未开 tiling）。

{% include video-gen-infra/fig-breakdown.html %}

VAE 的开销不只体现在时间上：解码阶段的激活随分辨率和帧数增长。在下图的 480p、81 帧配置下，float32 VAE 解码的显存峰值已经比 DiT 去噪高约 6.7 GB；开启 tiling 后降到与 DiT 相当，代价是解码时间（这里未测）。

{% include video-gen-infra/fig-memory.html %}

各项加速比不能直接相乘，还有一个多卡上的原因：稀疏 attention 减少了计算<d-cite key="zhang2025sta"></d-cite>，若仍传完整的 K/V，Ring 用来覆盖通信的计算时间也会缩短<d-cite key="liu2023ring"></d-cite>。单卡收益需要放回多卡配置中重新估算。

<details class="infra-tool">
  <summary><span>试算步数、GPU 数与通信开销</span><small>展开计算器</small></summary>
  <div class="infra-tool-body">
    <p class="infra-note">解析估算，用于看趋势；默认参数未经实测校准。</p>
    <iframe src="{{ '/assets/html/video-gen-cost-calculator.html' | relative_url }}" scrolling="no" height="1050" width="100%" title="视频生成推理成本计算器"></iframe>
  </div>
</details>

<h2 id="quality"><span class="infra-section-no">03</span>质量：比速度更硬的约束</h2>

LLM 推理中，最有影响力的加速之一是无损的：speculative decoding 可以保证输出分布不变。视频生成中，收益较大的加速——蒸馏、稀疏、量化、cache——几乎都是有损的。质量评估本身也缺少像准确率那样廉价、可靠的指标，这使得每一项加速都需要额外的评估成本。

**并行也可能改变结果。** 序列并行的切分方式、规约顺序、attention backend 不同，浮点结果就会不同；去噪过程可能放大这些初始差异，多卡与单卡的输出在视觉上未必一致。对需要复现或做 A/B 对比的场景，这一点需要事先确认。

**时长受训练分布限制。** 双向模型的可用时长通常接近训练时长，超出后容易出现重复或结构崩坏。直接拉长序列涉及位置编码的外推<d-cite key="su2021roformer"></d-cite>，并不是推理系统能单独解决的问题。

**改动推理流程的风险，大于看上去的程度。** 往双向模型注入上一段的 K/V、增加额外的融合模块，看起来都能补上跨段信息；但在个人的尝试中，这类改动首先带来的是画质不稳定。可能的原因包括位置编码错位与训练–推理不一致，这两点尚未逐一隔离验证。信息传进去了，不代表模型能按预期使用它。

与之相对，视频模型对文本条件非常敏感。在不重新训练的前提下，更完整、更一致的文本描述，可能比修改推理流程更有助于跨段一致性。这是现阶段实验后的选择，还不是通用结论。

<h2 id="streaming"><span class="infra-section-no">04</span>AR：算得快，还要赶上播放</h2>

CausVid、Self Forcing 等因果生成模型让视频可以逐段输出<d-cite key="yin2025causvid,huang2025selfforcing"></d-cite>。服务指标可以和 LLM 类比：首段等待近似 TTFT，段间间隔近似 TBT。区别在于播放缓冲：只要下一段在缓冲耗尽前完成，段间间隔本身对用户不可见。同样的生成速度，面对不同的缓冲余量，体验可能完全不同。

<figure class="infra-figure infra-streams" aria-labelledby="streams-caption">
  <div class="infra-figure-heading"><span>同一完成时间，不同卡顿风险</span><span class="infra-figure-kind">时序示意</span></div>
  <div class="stream-chart">
    <div class="stream-axis"><span>现在</span><span class="stream-deadline">下一 chunk 完成</span></div>
    <div class="stream-row"><span class="stream-name">流 A</span><div class="stream-track"><div class="stream-playable" style="width: 88%">可播放缓冲</div></div></div>
    <div class="stream-row"><span class="stream-name">流 B</span><div class="stream-track"><div class="stream-playable" style="width: 32%">缓冲</div><div class="stream-stall" style="left: 32%; width: 34%">等待</div></div></div>
  </div>
  <figcaption id="streams-caption">虚线处完成下一段。流 A 的缓冲足够覆盖这次生成，流 B 会先耗尽缓冲。图中长度仅用于说明关系。</figcaption>
</figure>

SlackServe 正是用剩余可播放时间组织资源分配<d-cite key="slackserve"></d-cite>。更贴近用户体验的服务目标因此是：**首段等待、播放卡顿、控制响应**，以及在这些约束下能承载多少条流。

自回归也让 KV cache 回到了视频生成中。历史 KV 直接占用多流共享的显存预算，按 bf16 普通多头 attention 估算：

<div class="infra-equation" markdown="1">

$$
M_{\mathrm{KV}} = 4 L d\,n_{\mathrm{history}}\quad\text{bytes}
$$

</div>

<figure class="infra-figure infra-kv" aria-labelledby="kv-caption">
  <div class="infra-figure-heading"><span>每条流的历史 KV</span><span class="infra-figure-kind">容量估算 · GB</span></div>
  <div class="kv-row"><span class="kv-label">1 帧</span><div class="kv-track"><span class="kv-bar" style="width: 6.25%"></span></div><strong>0.29</strong></div>
  <div class="kv-row"><span class="kv-label">4 帧</span><div class="kv-track"><span class="kv-bar" style="width: 25%"></span></div><strong>1.15</strong></div>
  <div class="kv-row"><span class="kv-label">16 帧</span><div class="kv-track"><span class="kv-bar" style="width: 100%"></span></div><strong>4.60</strong></div>
  <figcaption id="kv-caption">帧指 latent 帧。采用 <a href="https://github.com/Wan-Video/Wan2.1/blob/main/wan/configs/wan_t2v_1_3B.py">Wan2.1 1.3B 的维度</a>：L = 30、d = 1536，480 × 832 下每帧 1,560 tokens。仅估算同尺寸 AR 模型的 KV，不含权重、激活，也不意味着该双向 checkpoint 原生支持历史缓存。</figcaption>
</figure>

目前主流的 AR 视频模型大多只在局部窗口内做 attention；LongLive 额外保留首帧作为 sink<d-cite key="yang2025longlive"></d-cite>，思路与 StreamingLLM 一致<d-cite key="streamingllm"></d-cite>。窗口本身就是最简单的 KV 压缩：它给每条流的显存设了上限，代价是窗口之外的内容被遗忘。

2026 年起，生成侧开始出现更细的 KV 压缩：Quant VideoGen 将 KV 量化到 2 bit<d-cite key="quantvideogen"></d-cite>，DensityKV 与 FrameFold 在固定预算下筛选或合并历史 KV<d-cite key="densitykv,framefold"></d-cite>。视频理解侧更早开始做这件事，InfiniPot-V 等工作在流式视频问答中压缩视觉 token 的 KV<d-cite key="infinipotv"></d-cite>。

两边的问题并不相同。理解侧压缩是为了省显存，KV 只被问题读取，还可以按问题挑选 token。生成侧的窗口已经限住了显存，压缩更多是为了**在同等预算下记住更远的历史**；而每一次压缩误差，都会作为后续所有 chunk、所有去噪步的条件被反复使用，并可能逐段累积为漂移。理解侧基于重要性的筛选启发式，因此未必能直接迁移到生成侧。

history 长度、可容纳流数与生成质量，需要作为同一个服务问题来权衡。这是本文认为最值得投入的方向之一。

<h2 id="frameworks"><span class="infra-section-no">05</span>框架：并行库与服务系统</h2>

以下基于 2026 年 10 月底的开源代码，各项目迭代很快，细节可能已经变化。

- **[xDiT](https://github.com/xdit-project/xDiT)** 是单请求的并行推理库：USP（Ulysses 与 Ring 的组合）、PipeFusion、CFG 并行，封装 diffusers 的管线<d-cite key="fang2024xdit,fang2024usp"></d-cite>。它回答“一个请求如何切到多张卡上”，不负责多请求调度。SGLang Diffusion 与 vLLM-Omni 的并行状态管理代码都可以追溯到它。
- **[SGLang Diffusion](https://github.com/sgl-project/sglang)** 在类似的并行能力之上加了服务层：CFG、TP 与序列并行的组合，编码、去噪、解码可以分离部署，支持多种 attention backend，并对部分模型（如 Wan2.1）提供动态合批。它还按 exact、lossless、high 三档区分加速选项对输出的影响，这与第 03 节的问题直接相关。
- **[vLLM-Omni](https://github.com/vllm-project/vllm-omni)** 以全模态模型为目标，扩散部分有请求级与 step 级两种执行方式；step 级执行在视频模型上目前只覆盖少数几个，且为单请求。它的特色在于 AR 模型与 DiT 之间的 KV 传递，面向的是“LLM + 扩散”组合的模型。

结合第 01 节，这两个服务框架做合批与 step 级调度，价值可能主要不在提高视频请求的吞吐：图像或低分辨率请求仍处在合批有效的区间；step 粒度的执行为抢占、交错与资源调整提供了切入点；统一的请求接口也便于和 LLM 服务共用基础设施。对高分辨率视频请求，合批本身大概率不是收益来源。

<h2 id="outlook"><span class="infra-section-no">06</span>值得关注的方向</h2>

并非每个方向都有 infra 的空间，但以下几个方向会改变推理系统要解决的问题：

- **AR-DiT 与长视频。** 突破训练时长的限制，KV cache 随之回归，第 04 节的服务问题随之出现<d-cite key="yin2025causvid,yang2025longlive"></d-cite>。
- **线性注意力与混合注意力。** SANA-Video、Video DeltaNet 等工作降低长序列的成本<d-cite key="videodeltanet"></d-cite>；目前开源的视频模型仍少，系统层面的优化还缺少落地对象。
- **Agentic 生成。** LLM 规划分镜，VLM 评估质量，视频模型执行生成。多个候选可以共享文本编码，并借低成本预览提前淘汰，调度对象从单个请求变为一张工作流图。
- **3D 记忆与程序化场景。** 在显式场景表示上编辑更容易保证一致性，视频模型的角色趋近渲染器，对推理系统的要求也会随之改变。

回头看，视频生成推理与 LLM 推理共享许多组件，但瓶颈的位置不同：它不在带宽，而在计算；不在合批，而在资源分配；不在无损加速，而在质量约束。把 LLM serving 的方法直接搬过来之前，先确认它依赖的那条假设是否仍然成立。

<p class="infra-note infra-endnote">2026 年 10 月。个人观察限于所述配置；画质对照待补。示意图、强度与容量为按公开配置的估算；标有“实测”的图来自单张 A100，配置见各图图注。</p>


{% comment %}
嵌入视频的写法：
<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include video.liquid path="assets/video/xxx_baseline.mp4" class="img-fluid rounded z-depth-1" controls=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include video.liquid path="assets/video/xxx_kv_inject.mp4" class="img-fluid rounded z-depth-1" controls=true %}
  </div>
</div>
<div class="caption">左：……；右：……</div>
{% endcomment %}

{% comment %}
AR 那篇没投之前：这一节只写方向，不写 early KV handoff 的具体做法和调度设计。
{% endcomment %}

{% comment %}
原稿实验与写作备忘（保留供作者后续补充，不在页面渲染）：
开头 2–3 段：为什么写这篇（公开材料只有论文的成功部分和厂商报告的最终方案，缺“看起来合理但走不通”的那一层）；我是谁、做了什么（一句话，不涉及在审论文）；这是一份 2026 年 10 月的快照，以及我没深入跟进的部分（SGLang Diffusion、vLLM-Omni 的最新进展 —— 发布前确认名字）。

5 条判断，每条一句话加适用条件。草稿：

放实测：同一配置下 batch size 1 → 2 → 4 的吞吐（videos/s）曲线；或者用 Nsight Compute 看主要 GEMM 的 SM 利用率。理论上曲线应该接近水平。

用你使用的模型的真实 config（d、d_ff、层数）算一下分界点，并和 profiler 里 attention kernel 的时间占比对照。

用 profiler 拆一下 VAE decode 的时间：卷积 kernel 和 norm / 激活 / 拷贝各占多少。如果逐元素操作占比高，这本身就是一个 kernel fusion 有用武之地的地方，可以和第 3 节“工程优化收益小”的说法对照。

放实测：用 torch.cuda.max_memory_allocated() 分阶段记录 text encoder / DiT / VAE decode 的显存峰值（开关 tiling 各一组），配一张分阶段的显存时间线图。这张图会很有说服力。

核对数字：Wan VAE 解码器最高分辨率阶段的通道数（文中按 96 算）、14B 的 d_ff（按 13,824 算）、umT5-XXL encoder 参数量。

用你的实测数据校准计算器的默认值（MFU、VAE 每帧耗时、通信开销），并在图注里写明校准时用的硬件。

放实测：1 / 2 / 4 / 8（/ 16）张卡的端到端延迟和扩展效率曲线，标出 CFG parallel、Ulysses、Ring 各自负责的段，以及跨机的位置。最好再拆出 text encoder / DiT / VAE / 通信，验证上面四个因素各自贡献了多少。

核对假设：NVLink 和 IB 的有效 all-to-all 带宽（文中用 300 GB/s 和 40 GB/s）、各模型的 head 数和 d_ff。最好用 nccl-tests 在你的机器上实测一下。

计算器的 MFU 不随每卡 token 数变化，所以它画出的扩展曲线是乐观的上界。用实测曲线和它对照，差距本身就可以写一句。

负面结果：5B 模型、长 chunk 下跨 denoising step co-batch 没有收益。写清楚模型、chunk 长度、GPU，给出数字。

核对 SlackServe / GF-DiT / DIFlow 的准确名字、作者和出处，补全 .bib；每个工作用一句话说清它调的是哪个旋钮。

实测 50 步和 4 步下的端到端时间分解（text encoder / DiT / VAE / 通信），用数据决定第 4 类到底“收益小”还是“蒸馏之后变重要”。这一节的措辞取决于这组数。

（可选）sparse attention 的质量—速度曲线，或者 caching 在少步模型上还剩多少收益（直觉上步数越少，相邻步之间越不相似，cache 的空间越小 —— 有数据再写）。

补充第一类里那条我没写清楚的原因（原笔记里是“缺乏退化尺寸”，确认原意）。

往双向模型里注入上一段的 K/V：RoPE 位置错位，加上训推不一致。写现象，最好配并排对比视频（assets/video/ 下的 mp4，用 video.liquid 嵌入）。

fuser 不可靠：写在什么情况下失效。

shared prompt 只能管住粗粒度的风格，细粒度的一致性（人物外观、物体）管不住。

放一个观察：predicted-x0 的 KV handoff 误差会饱和而不是累积（写现象和条件，不写机制）。

放一个对比：不同 chunk 大小下每次前向的时间分解（GEMM / attention / 非 GEMM / launch 间隙），用来支撑“固定开销占比上升”。如果实测发现小 chunk 下确实接近 memory-bound，就改写上面这段。

如果有：一个具体例子（某个产品或开源 workflow 的分镜流程），说明延迟大头在哪一步。

把这张表做成一张设计过的图（最容易被单独截图传播的部分）。

结尾一段：text / agent 方向的进展会不会让 diffusion 上的投入贬值？我的看法和理由。

致谢（可选）。
{% endcomment %}

{% comment %}
精简前保留的六组实测待办：
待补实验：固定模型、分辨率、帧数、步数与 GPU，比较 batch 1 / 2 / 4 的 videos/s、单请求延迟和峰值显存，并用 profiler 区分 GEMM、attention 与非矩阵算子。

待补实验：分别记录 text encoder、DiT、VAE 的峰值 allocated / reserved 显存，注明权重驻留、CFG 执行方式、精度与 tiling；阶段计时前后同步 GPU。

待补实验：画出 1 / 2 / 4 / 8 / 16 卡的端到端延迟与 GPU-seconds，标明 CFG、SP 分组和跨机放置；用 collective benchmark 校准带宽与启动延迟。

待补实验：在质量可比的前提下，对照多步基线与少步模型的端到端分解；报告模型/checkpoint、采样器、CFG、分辨率和硬件，不只比较步数。

待补个人实验：选一个能够公开的失败案例，写清基线、唯一改变的变量、失效现象与重复次数，并配对比视频；不要把单个样本归因为普遍机制。

待补实验：扫描 chunk 大小与 history 长度，记录 TTFC、每个 chunk 的延迟分布、卡顿率、KV 容量和算子分解，并同时比较生成质量。
{% endcomment %}

{% comment %}
作者本轮补充：
- 一开始知道主体 compute-bound，但预计 memory-bound 操作仍能从 batching 获益；已设想按 denoising step 边界做 continuous batching。
- 后来 profile 发现测试负载是 compute-bound，预期的 batching 收益空间没有出现；调度重心转为请求何时、在哪台服务器、使用多少资源运行。
- 修改模型 workflow 会显著影响视频生成质量；模型对文本向量很敏感。目前作者认为提升一致性最有用的入口仍是文本。
- 不补写未提供的 GPU 型号、耗时、失败画面、调参过程或量化收益。
{% endcomment %}
