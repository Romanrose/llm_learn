# CMU 11-768 Fall 2026 · Lecture 12 · Training 4: RL Systems 学习笔记（候选稿）

> 待审核候选稿 · 来源：仅官方 Slides；逐字稿未就绪 · 尚未发布。

> **说明**：本文仅依据官方 Lecture 12 slides 的逐页文本提取稿撰写，属于**基于讲义的候选学习笔记**，并非完整课堂记录。讲者 Apurva Gandhi 的口述内容、课堂互动、问答、现场举例与逐字稿均未获得，因此本文不还原、不虚构上述内容。Slides 中的图示、公式排版与部分细节需对照官方 PDF 核验；凡文本提取无法确认者，本文标注为“待核”。所有论点按 Slide 页码标注来源。

---

## 一、学习目标

完成本讲后，应当能够：

1. **描述 LLM 强化学习框架必须支持的核心操作**：forward、backward、optim_step、env.verify、env.state / env.step，以及 agent harness（Slides 第 3 页）。
2. **解释为什么 RL 框架不能简单用手写 PyTorch 完成**，以及框架由哪两类本质不同的工作负载构成（Slides 第 4–5 页）。
3. **列出训练引擎与推理引擎各自的代表性优化手段**，并说明它们为何优化方向相反（Slides 第 6、9–14 页）。
4. **拆解一个训练 step 的五个阶段**：sample、verify、forward、backward、optim_step + sync（Slides 第 8 页）。
5. **解释训练–推理交互中的关键问题**：weight sync、delta weight sync、Rollout Routing Replay（R3）（Slides 第 16–17 页）。
6. **识别 agentic RL 的“尖刺问题”**：sequence extension、chat template quirks、Token-In-Token-Out、async RL 与 in-flight weight updates（Slides 第 18–26 页）。
7. **比较两种系统设计范式**：SPMD 单程序与 everything-as-a-service 单控制器，并理解后者的解耦、模块化与弹性扩展优势（Slides 第 29–36 页）。
8. **了解多策略训练、在线 RL、多租户多 LoRA 等前沿方向**，以及 Tinker 的 API 设计（Slides 第 38–41 页）。
9. **记住一组可用于调试 RL 训练的关键指标**及其告警信号（Slides 第 43 页）。

---

## 二、概念主线

本讲的主线可以概括为一句话：**LLM 强化学习系统 = 训练引擎 + 推理引擎 + 环境/验证器 + 协调层，而 agentic 场景把这条流水线的每一段都拉长了。**

主线展开如下：

- **起点**：策略梯度更新公式要求一套固定操作集合（前向、反向、优化器步、环境交互）。手写 PyTorch 虽可行，但会迅速遇到工程复杂度（Slides 第 3–4 页）。
- **分野**：RL 框架天然由两类工作负载组成——训练引擎（prefill 风格、可并行、需要 autograd）与推理引擎（decode 为主、顺序性强、无梯度）。二者依赖的优化技术几乎不重叠（Slides 第 5–6 页）。
- **连接**：两类引擎之间需要 weight sync 与 rollout/trajectory 数据流动（Slides 第 7 页）。
- **循环**：一个训练 step 是 sample → verify → forward → backward → optim_step + sync 的闭环，然后用更新后的权重重复（Slides 第 8 页）。
- **瓶颈转移**：agentic RL 中 rollout 很长，系统常是 rollout-bound，于是出现 async RL、in-flight weight update、sequence extension、TITO 等针对性设计（Slides 第 18–26 页）。
- **架构收敛**：从 SPMD 走向 everything-as-a-service + 单控制器，以获得解耦、模块化、弹性扩展与异构算力支持（Slides 第 29–36 页）。
- **前沿形态**：多策略训练、在线 RL、多租户多 LoRA，以及 Tinker 式的清晰 API（Slides 第 38–41 页）。

---

## 三、关键机制

### 3.1 必须支持的操作与更新公式

Slides 第 3 页给出的策略梯度更新形式为：

$$
\theta \mathrel{+}= \sum_t \big(R(\tau) - b(h_t)\big)\, \nabla_\theta \log \pi_\theta(a_t \mid h_t)
$$

**符号与假设（依据 Slides 第 3 页的排版，细节待核）**：
- $\theta$：策略参数。
- $\tau$：一条轨迹（trajectory）。
- $R(\tau)$：该轨迹的回报。
- $b(h_t)$：与历史 $h_t$ 相关的基线（baseline），用于降低方差。
- $\pi_\theta(a_t \mid h_t)$：在历史 $h_t$ 下选择动作 $a_t$ 的策略概率。
- $\sum_t$：对轨迹中各时间步求和。

> **待核**：slides 中该公式的下标、括号与基线记法在纯文本提取后可能失真，请对照官方 PDF 确认。本文不额外补充 slides 未给出的折扣因子、优势估计或裁剪项假设。

围绕该公式，框架必须支持：`forward`、`backward`、`optim_step`，以及环境侧的 `env.verify`、`env.state / env.step`，外加 agent harness（Slides 第 3 页）。

### 3.2 为什么不用手写 PyTorch

Slides 第 4 页把 PyTorch API 与所需操作并置：`optimizer.step()`、`model.backward()`、`model.forward()`。含义是：核心操作的 API 对应关系是清晰的，但**难点不在单个算子，而在把训练与推理两类异构工作负载、环境交互与权重同步组织成一个可扩展系统**。

### 3.3 两类工作负载

Slides 第 5–6 页明确指出 RL 框架由两类根本不同的工作负载组成：

| 维度 | Trainer Engine（如 Megatron、FSDP2） | Inference Engine（如 vLLM、SGLang） |
|---|---|---|
| 调用 | `forward_backward` | `sample` |
| 特征 | Prefill 风格、可并行 | Decode 为主、顺序性强 |
| 梯度 | Autograd | No grad |
| 代表优化 | Model sharding (PP, CP, TP, EP)、Activation Checkpointing、Prefix sharing、Batch Sample Packing | KV Caching、Radix/Prefix Caching、Continuous Batching、Speculative Decoding/MTP、Model sharding (PP, CP, EP) |

> 注：Slides 第 6 页把“Model sharding (PP, CP, TP, EP, etc.)”列在训练引擎侧，把“Model sharding (PP, CP, EP, etc.)”列在推理引擎侧；两处列出的并行维度不完全相同，具体差异待对照 PDF 核验。

### 3.4 训练 step 的五阶段拆解

Slides 第 8 页给出清晰的流水线：

1. **sample**（推理 + 环境）：从当前策略采样轨迹，同时在环境中执行动作。
2. **verify**（环境）：从 verifier、测试或工具结果获得奖励。
3. **forward**（训练器）：在训练器中前向重算 logprobs，并跟踪梯度。
4. **backward**（训练器）：反向传播计算梯度。
5. **optim_step + sync**：更新训练器策略权重，发送到推理引擎并重新分片。

随后用更新后的权重重复。

### 3.5 推理侧优化

- **KV Caching（Slides 第 9 页）**：每个历史 token 保存一份 K、V。第 $t_7$ 步只对新 token 计算 q、k、v，然后对所有缓存的 k、v 做注意力，再追加自己的。代价是“用大量重算换大量显存”。示例规模：Llama-3-8B 在 bf16 下每 token 约 128 KB；一条 32k token 轨迹约 4 GB；64 条约 256 GB。
- **Prefix Caching（Slides 第 10 页）**：系统提示 + 工具、任务提示在不同 rollout 间共享；agentic RL 尤其受益，因为 GRPO 的 group rollouts 共享同一任务提示，且一条 rollout 的历史 KV 可在后续 step 复用。代表实现：SGLang RadixAttention、vLLM Automatic Prefix Caching。
- **Continuous Batching（Slides 第 11 页）**：以单个 decode step 为粒度调度，完成的序列立即离批，排队请求补位。通常配合 chunked prefill 以避免长提示造成 decode 延迟尖峰；也可选择 prefill 与 decode 分离（disaggregate）。对比静态批处理中“每个槽位都要等最长的请求 B”。引用：Yu et al., 2022（Orca, iteration-level scheduling）。
- **Speculative Decoding（Slides 第 12 页）**：廉价 drafter 猜测 k 个 token，策略在一次并行 pass 中校验全部 k 个，拒绝采样保持策略的精确分布。**RL 特有的坑**：策略每个训练 step 都在变，冻结 drafter 的接受率会衰减，需要用辅助目标（如 SFT、蒸馏）在线训练。示例中 k = 4。引用：Leviathan et al., 2023。

### 3.6 训练侧优化

- **Activation Checkpointing（Slides 第 13 页）**：前向只保留每层输入，反向到达该层时重算内部激活。显存从“每层全部激活”降到“每层一个输入 + 任一时刻单层激活”。代价：完整重算约增加一次前向，约 +33% 计算；选择性重算（仅注意力）成本远低。引用：Chen et al., 2016（gradient checkpointing）；Korthikanti et al., 2022（selective activation recomputation）。
- **Prefix Sharing（Slides 第 14 页）**：RL 批次重复前缀——GRPO 组内共享 prompt、多轮间共享历史。只计算一次前向与反向。要点：tree attention mask（分支间不互相注意）、position IDs 按各自独立序列处理、每个分支的梯度累加回 P。数据点：长 prompt 的 GRPO 批次中 80–95% token 是重复 prompt token，去重后 actor 更新最高快 6×（Snowflake AI Research, 2026，ZoRRo / Arctic RL）；多轮 τ²-bench rollout 作为前缀树压缩 9.43×，DFS 逐条走根到叶路径，相比 dense 训练最高 8.31×（Zhang et al., 2026，AReaL-DTA: Dynamic Tree Attention, ICML）。
- **Parallelism（Slides 第 15 页）**：以 Context Parallelism 为例，各 GPU 保留自己的 Q，KV blocks 轮转。引用：NVIDIA NeMo Framework User Guide。

### 3.7 训练–推理交互

- **Weight Sync（Slides 第 16 页）**：
  - Full Weight Sync：全量广播到每个推理 rank。1T 参数模型约 2TB 同步量。
  - Delta Weight Sync：RL 权重更新之间约 99% 参数不变，只同步 delta。
  - 注意：参数需要按推理引擎的并行布局重新分片。引用：Mihai & Belilovsky (PULSE), 2026。
- **Rollout Routing Replay, R3（Slides 第 17 页）**：
  - 问题：微小数值差异可能导致 MoE 选中不同的 expert。
  - 方案：记录 rollout 时的 expert 选择，并在训练中重放这些选择。
  - 要求：推理引擎必须把 routing 决策提供给训练引擎。引用：Ma et al., 2025, R3, Fig. 1。

### 3.8 Agentic RL 的尖刺

- **Sequence Extension（Slides 第 19–20 页）**：Harness A 追加到已有历史；Harness B 每两次观测压缩一次（O₂ 之后保留 T，把 A₁ O₁ A₂ O₂ 摘要为 S）。问题：哪种 harness 对训练效率更好？训练批次上，一条轨迹的优势 $\hat{A}$ 广播到每个动作 token。Harness A 是单个拼接数据点（loss mask 在动作 token 为 1，观测与任务为 0）；Harness B 是两个数据点，都含 Task。**重复的 task token 没有直接 loss，但仍需上下文计算**。原则：尽量保留精确前缀并拼接。来源标注为“23404: Sequence Extension - Tinker Documentation”。
- **Chat Template Quirks（Slides 第 21–22 页）**：流行的 chat template 可能不满足 sequence extension 性质。例如 Qwen 3 / Qwen 3.5 默认 chat template 会从历史中移除 reasoning。Agent RL 训练框架常自带保留 sequence extension 的自定义 chat template 或 “renderers”（如 Tinker、PrimeRL）。引用：No Token Left Behind: Demystifying Token-In-Token-Out in Miles。
- **Token-In, Token-Out, TITO（Slides 第 23–24 页）**：rollout/轨迹数据在推理引擎与训练引擎之间应以什么格式存储与传输？选项：字符串 vs token。字符串空间中的小而不一致的变换会导致训练与推理之间 tokenization 不一致（例如 chat template 添加空白）；tokenization 是一对一，但 de-tokenization 是多对一。
- **Async RL（Slides 第 25 页）**：
  - Sync RL：训练与推理引擎共置（同一批 GPU 共享）。
  - Async RL：GPU 在训练与推理间拆分；agentic RL 常常 rollout-bound（长轨迹），可把更多 GPU 分给推理（例如 3:1）；需要 continuous batching 与 in-flight weight update 支持；需要 staleness / off-policy 修正。代表：Pipeline RL、AReaL。
- **In-flight Weight Updates（Slides 第 26 页）**：推理框架已演进以适配 RL 系统需求，示例来自 SGLang Docs。
- **复杂 Harness（Slides 第 27 页）**：sub-agents、context compaction 等。引用：Recursive Agent Optimization (RAO), 2026；Recursive Language Models (RLM), 2025。

### 3.9 系统设计选择

- **Harness Agnostic Design（Slides 第 29 页）**：面对 Codex、Claude Code、OpenHands、Pi、Hermes、Prime Agent 等众多 harness，反模式是为每个 harness 写自定义 rollout/env 代码；正确模式是用中间人/代理服务模拟推理 API（chat-completions、responses、anthropic 等），新增 harness 时 0 代码改动。图中组件包括 Agent Lightning Middleman、Inference Engine、Rollout Store（logprobs、r3 等）、Inference Service、Trainer。
- **SPMD（Slides 第 30 页）**：一个 Python 程序跑在每个 GPU rank 上。示例伪代码中，所有 rank 以相同顺序创建 train 组（rank 0–3）与 infer 组（rank 4–7）；训练侧循环做 forward_backward、optimizer.step()、publish_weights_async；推理侧循环做 refresh_weights_if_ready、rollout、enqueue_trajectory。协调逻辑活在每个 rank 上运行的程序里；直接控制一切，但灵活性较低。来源标注：AReaL versions < 1.0。
- **Everything-as-a-service w/ Single Controller（Slides 第 31–33 页）**：服务边界包括 Orchestrator / Controller、Inference Service、Agent Service、Trainer Service、Weight Sync Service、Env / Reward Service；API 示例包括 Open Reward Standard (ORS)、SGLang / vLLM API、Tinker training API（slides 注明为示意性服务边界与 API 示例）。
  - **解耦**：每个组件都相当复杂且专门化；轻量 orchestrator（CPU 训练循环）让研究者无需复杂依赖即可原型化不同算法；项目维护、更新与发布无需同步。
  - **模块化**：只要协议一致，服务实现可替换；可为托管服务（如 OpenReward）或自托管。
- **Elastic Scale Up（Slides 第 34–35 页）**：控制器可按需扩展出多个 Inference Service 与 Controller。
- **Multi-cluster / Heterogeneous Compute（Slides 第 36 页）**：示意 8xH100 与 4xMi350 混布。
- **Example: AstraFlow（Slides 第 37 页）**：Haizhong Zheng et al., 2026。
- **Multi-policy Training（Slides 第 38 页）**：微服务架构便于同时训练多个不同模型（例如异构策略的多智能体 rollout）。
- **Online RL（Slides 第 39 页）**：AReaL 2.0, 2026；Cursor 生产环境在线 RL：Cursor Tab、Composer（每 5 小时从真实用户交互产生新 checkpoint）。
- **Multi-Tenant, Multi-LoRA（Slides 第 40 页）**：8 个并发运行吞吐优于 8 个串行运行（但每运行 e2e 时间增加）；每个并发 LoRA 运行可以是训练服务的不同用户；需要特殊 kernel（Grouped-GEMM / SGMV）。引用：SkyRL + Trajectory Labs, 2026；Punica, 2023。
- **Tinker（Slides 第 41 页）**：开创多租户、多 LoRA RL 训练与解耦训练服务设计；API 清晰：每个训练运行一个 training client，每个 LoRA 权重 checkpoint 一个 sampling client。

### 3.10 调试指标

Slides 第 43 页列出应跟踪的指标：

| 指标 | 含义 | 告警信号 |
|---|---|---|
| Reward / pass@1 | 策略在训练任务上是否改善 | 多步持平；或训练上升而留出评估下降（reward hacking） |
| pass@k | 覆盖度：k 个样本中是否有解 | pass@1 上升而 pass@k 下降：多样性坍缩 |
| Entropy | 策略还剩多少探索 | 骤降到 0，或突跳（退化文本） |
| importance_weight_max | 最差 token 比率，如 π_train / π_rollout | 尖峰：不匹配或陈旧数据；少数 token 主导更新 |
| Grad norm | 裁剪前每次更新的规模 | 发散前尖峰；持续上行漂移 |
| Average staleness | 数据落后多少个权重版本 | 持续上升：rollout 跟不上训练 |
| Trainer MFU | 训练 GPU 利用效率 | 因 padding、不均衡或小 micro-batch 而下降 |
| Timing: rollout, update, stall, total | 一步墙钟时间的去向 | Stall > 0：训练器在等 rollout |

---

## 四、误区

1. **“RL 框架就是把 PyTorch 训练循环包一层。”** 不对。核心难点是两类异构工作负载（prefill 式训练 vs decode 式推理）的协同，以及权重同步、数据格式、并行布局的匹配（Slides 第 5–7 页）。
2. **“训练和推理可以用同一套优化。”** 不对。训练侧重 activation checkpointing、prefix sharing、batch packing；推理侧重 KV cache、prefix caching、continuous batching、speculative decoding（Slides 第 6、9–14 页）。
3. **“KV cache 只是省算力。”** 它同时是巨大的显存开销（Slides 第 9 页的具体数字）。
4. **“Prefix caching 只对推理有意义。”** 训练侧的 prefix sharing 是它的对偶，且收益可观（Slides 第 14 页）。
5. **“Speculative decoding 的 drafter 可以一直冻结。”** 在 RL 中策略每步都变，接受率会衰减，需要在线训练 drafter（Slides 第 12 页）。
6. **“Weight sync 直接全量广播就行。”** 1T 模型约 2TB，应考虑 delta sync，并注意重新分片（Slides 第 16 页）。
7. **“MoE 训练里 expert routing 是确定的。”** 微小数值差异即可改变 expert 选择，需要 R3 重放（Slides 第 17 页）。
8. **“轨迹数据用字符串传就行。”** 字符串空间的小变换会造成 tokenization 不一致，de-tokenization 多对一；应使用 TITO（Slides 第 23–24 页）。
9. **“重复的 task token 没有 loss，所以无关紧要。”** 它们仍需要上下文计算，影响训练效率（Slides 第 20 页）。
10. **“异步一定更好。”** Async RL 降低 GPU 空闲，但引入 staleness 与 off-policy 修正需求（Slides 第 25 页）。
11. **“为每个 harness 写适配层是正常做法。”** 这是反模式；harness-agnostic 的中间人模式可实现新增 harness 零代码改动（Slides 第 29 页）。
12. **“pass@1 上升就说明训练健康。”** 还需看 pass@k、entropy、grad norm、staleness 等（Slides 第 43 页）。

---

## 五、复习问题

1. 列出 LLM RL 框架必须支持的操作，并说明它们分别属于训练侧还是环境侧（Slides 第 3 页）。
2. 为什么 RL 框架由两类根本不同的工作负载构成？各自的特征是什么（Slides 第 5–6 页）？
3. 完整描述一个训练 step 的五个阶段（Slides 第 8 页）。
4. KV caching 省了什么、花了什么？用 Llama-3-8B bf16 的数字说明（Slides 第 9 页）。
5. Prefix caching 为什么对 agentic RL 特别有益？举出代表实现（Slides 第 10 页）。
6. Continuous batching 与 static batching 的差别是什么？为什么常配 chunked prefill（Slides 第 11 页）？
7. Speculative decoding 在 RL 中的特有陷阱是什么？如何缓解（Slides 第 12 页）？
8. Activation checkpointing 的显存收益与计算代价各是什么（Slides 第 13 页）？
9. Prefix sharing 中 tree attention mask 与 position IDs 如何处理？给出两个量化数据点（Slides 第 14 页）。
10. Full weight sync 与 delta weight sync 的差别？为什么还需要重新分片（Slides 第 16 页）？
11. R3 解决什么问题？对推理引擎提出什么要求（Slides 第 17 页）？
12. Sequence extension 中两种 harness 的做法有何不同？对训练批次有什么影响（Slides 第 19–20 页）？
13. 什么是 chat template quirks？举一个 slide 中提到的模型例子（Slides 第 21–22 页）。
14. TITO 为什么优于字符串传输（Slides 第 23–24 页）？
15. Sync RL 与 async RL 的取舍是什么？agentic RL 为何常是 rollout-bound（Slides 第 25 页）？
16. SPMD 与 everything-as-a-service 单控制器各自优缺点是什么（Slides 第 30–33 页）？
17. 多租户多 LoRA 训练带来什么收益、需要什么支持（Slides 第 40–41 页）？
18. 列出至少五个调试指标及其告警信号（Slides 第 43 页）。

---

## 六、待核事项

- Slide 3 的策略梯度公式的具体记法（下标、基线符号、括号范围）需对照官方 PDF 确认。
- Slide 6 中训练侧与推理侧 “Model sharding” 列出的并行维度不完全一致，需核验。
- 各图示（如 Slide 10 的 prefix caching 布局、Slide 15 的 context parallelism、Slide 30 的 SPMD 伪代码排版、Slide 31–36 的服务拓扑）仅凭文本提取无法确认布局细节。
- 部分数据点（如 6×、8.31×、9.43×、80–95%、3:1 比例）来自 slides 转述的文献，本文未独立核验原始论文。

---

## 七、官方来源

- 课程主页：https://www.cmu-agents.com/
- 课程日程与阅读：https://www.cmu-agents.com/#schedule
- 官方课程日程：https://www.cmu-agents.com/#schedule
- 作业与项目要求：https://www.cmu-agents.com/#assignments
- Assignment 1 · Harness：https://github.com/cmu-agents/assignment-1
- Assignment 2 · Eval：https://github.com/cmu-agents/assignment-2
- Lecture 12 slides：https://www.cmu-agents.com/slides/lecture-12-rl-systems.pdf
