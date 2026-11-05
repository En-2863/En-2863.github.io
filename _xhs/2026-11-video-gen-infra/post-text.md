1. 视频生成推理与 LLM 推理差异显著。双向注意力视频模型的单个请求即含数万 token，480p 以上通常已是 compute-bound，也无自回归式 KV cache。5B 模型、长 chunk 的测试中，按去噪步合批未见收益。调度因而转向何时启动、放在何处、分配多少 GPU：SlackServe 在 SLO 约束下调整 GPU 资源与步数、分辨率；TetriServe（ASPLOS'26，文生图）逐步调整请求并行度；GF-DiT 研究弹性序列并行。

2. 加速收益大致为：步数蒸馏 ≫ 稀疏 attention ≈ 量化 > diffusion cache > kernel fusion / VAE。DMD2、rCM 等蒸馏可将 20/50 步压缩至 4 步左右，通常还免去 CFG，已较常见。稀疏 attention（STA、SparseVideoGen）与量化（SageAttention、FP8）利用时空冗余，收益随分辨率与时长增加。cache 跳过相邻相似步，少步模型上空间有限，质量也难控制。DiT 提速后，编解码的占比随之上升。

3. 质量是主要约束。收益较大的加速多为有损，无法像 speculative decoding 那样保证输出不变；并行方式与 kernel 顺序也可能改变结果。双向模型的可用时长通常接近训练时长，超出后易质量坍塌。模型对文本高度敏感：不重新训练时，更完整的文本描述可能比修改推理流程更有助于质量与一致性。

4. 值得关注的方向：
① AR-DiT：突破时长限制，KV cache 随之回归（CausVid、LongLive）。首段等待近似 TTFT，段间间隔近似 TBT，但视频有播放缓冲，核心是是否卡顿。
② 线性注意力 / DeltaNet（SANA-Video、Video DeltaNet）：降低长序列成本，开源模型仍少。
③ Agentic 生成：LLM 规划分镜，VLM 评估质量，视频模型生成。多候选可共享文本编码，并借预览提前淘汰。
④ 3D 记忆 / 程序化场景：在显式场景上编辑更易保证一致性，视频模型趋近渲染器。

并非每个方向都有 infra 空间，但视频生成值得长期关注。入门可参考 xDiT、SGLang Diffusion、vLLM-Omni，以及 FastVideo 团队开源的 UniServe。
