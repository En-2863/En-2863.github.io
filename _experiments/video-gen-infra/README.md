# 视频生成 infra 博客的实测

`_posts/2026-10-30-video-gen-infra.md` 里四张“实测”图的数据来源。`_experiments/` 以下划线开头，Jekyll 不会把它发布到网站上。

## 运行

需要一张 CUDA GPU；1.3B 模型在 480p、81 帧下 24 GB 以上的卡应能放下（VAE 不开 tiling 时，峰值可能出现在解码阶段）。

```bash
pip install torch diffusers transformers accelerate ftfy
python bench.py --exp all          # 结果写到 results/
```

在本地（不需要 GPU）把结果变成博客里的图：

```bash
python render_figures.py           # 写到 _includes/video-gen-infra/
```

## 四个实验

| 实验 | 测什么 | 对应正文 |
|---|---|---|
| `batch` | batch 1/2/4 时 DiT 的吞吐，只跑 DiT（`output_type="latent"`） | 01：合批收益是否接近为零 |
| `profile` | 单步 DiT 的 GPU kernel 时间：GEMM / attention / 其他 | 02：attention 占比，对照 FLOPs 估算的约 70% |
| `breakdown` | 50 步 + CFG 与 4 步无 CFG 的端到端时间分解 | 02：少步之后编码、解码占比是否上升 |
| `memory` | 各阶段显存峰值，VAE tiling 开 / 关 | 02：显存峰值是否在 VAE |

常用参数：`--model`、`--height/--width/--frames`、`--repeats`、`--batches`、`--configs 50:5.0 4:1.0`。换成 5B 模型的示例：

```bash
python bench.py --exp all --model Wan-AI/Wan2.2-TI2V-5B-Diffusers --height 704 --width 1280 --frames 121
```

## 注意

- **GPU 型号、软件版本都从 `results/env.json` 读取，图注自动生成，不要手改。** 换机器后整组重跑，不要混用不同机器的 CSV。
- **`breakdown` 的 4 步配置用的是同一个未蒸馏 checkpoint**，只测时间，画质不可用；图注已写明。如有蒸馏后的 checkpoint，用 `--model` 单独跑一次更准确。
- **计时方式**：每个阶段前后各做一次 `cuda.synchronize()`，开销计入测量值。CFG 开启时，DiT 每步前向两次，图注会写出次数。
- **`profile` 按 kernel 名称把时间归入 GEMM / attention / 其他**，属于启发式。发布前看一眼 `results/profile_top.csv`，确认前 30 个 kernel 都归对了。
- **结果和正文的估算不一致时，应改正文，不要改图。**
