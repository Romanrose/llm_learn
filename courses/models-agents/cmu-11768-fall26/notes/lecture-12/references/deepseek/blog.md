# 把强化学习“跑起来”：CMU 11-768 Lecture 12 中的 RL 系统分层

> 待审核候选稿 · 来源：仅官方 Slides；逐字稿未就绪 · 尚未发布。

> 说明：本文基于 CMU 11-768 Fall 2026 Lecture 12《Reinforcement Learning Systems》的官方 Slides 文本提取稿写作，属于**候选稿**，并非完整课堂记录。因为没有逐字稿，本文不伪造讲者口述、课堂问答或未出现在 Slides 中的例子。凡属帮助理解的补充说明，均单独标为“学习者解释”；Slides 中仅以图示或公式呈现、文本提取无法确认细节的内容，一律标注“待核”。关键论点后标注来源页码（如“Slides 第 8 页”）。

## 一、问题：为什么“用 PyTorch 手写 RL”不够

Lecture 12 的起点是一个很朴素的问题：一个支持大语言模型（LLM）的强化学习框架，到底必须支持哪些操作？Slides 第 3 页给出了一条策略梯度更新的表达式，并把整套系统拆成几个操作名：`forward`、`backward`、`optim_step`，以及环境侧的 `env.state / env.step`、`env.verify`，再加上 agent harness。Slide 4 直接追问：既然 vanilla PyTorch 已经有 `model.forward()`、`model.backward()`、`optimizer.step()`，为什么不直接手写一套实现？

**学习者解释**：把策略梯度写成一个公式并不难，难的是让这个公式在真实 LLM 训练里高效、稳定、可扩展地执行。公式里的每一项都对应一个昂贵的工程环节：要采样轨迹、要调用环境、要重算 logprob、要反传、要把新权重送回采样端。Slides 后面几十页，本质上都在解释“为什么不能只写一个 for 循环”。

Lecture 12 给出的核心答案是：**LLM RL 框架由两种根本不同的负载组成**（Slides 第 5 页）。一边是 Trainer Engine（如 Megatron、FSDP2），负责 `forward_backward`，属于 prefill 风格、可并行、需要 autograd；另一边是 Inference Engine（如 VLLM、SGLang），负责 `sample`，属于 decode 密集、序列化、无梯度。Slide 6 进一步列出两边各自的优化手段：推理侧有 KV Caching、Radix/Prefix Caching、Continuous Batching、Speculative Decoding/MTP；训练侧有 Model sharding（PP、CP、TP、EP 等）、Activation Checkpointing、Prefix sharing、Batch Sample Packing。

**学习者解释**：这一步是整讲的“世界观”。传统训练只关心一个引擎；RL 系统必须同时关心两个引擎，而且这两个引擎的硬件偏好、并行方式、内存瓶颈都不一样。所谓“RL 系统”，很大程度上就是**协调这两个引擎**的系统。

## 二、一个训练步骤的解剖

Slides 第 8 页把一次训练步骤拆成五段：1 `sample`（推理 + 环境，采样轨迹并执行动作）；2 `verify`（从 verifier、测试或工具结果得到奖励）；3 `forward`（在 trainer 中重算 logprob 并跟踪梯度）；4 `backward`（计算梯度）；5 `optim_step + sync`（更新权重、发送到推理引擎并重新分片），然后“Repeat with the updated weights”。

**学习者解释**：这里最关键的是第 3 步“recompute logprobs”。采样时用的权重和训练时用的权重可能已经不同，而且采样端通常不保留完整梯度图。因此 trainer 必须对同一段 token 序列重新做一次前向，才能得到与当前策略一致的 logprob。这个动作把“推理”和“训练”在数据上对齐，也解释了为什么 RL 训练步骤里既有昂贵的 decode，又有昂贵的 prefill。

Slides 第 7 页则画出两个引擎之间的两条通道：`weight sync` 和 `Rollout/trajectory data`。这意味着系统设计必须回答两个问题：权重怎么从 trainer 到 inference？轨迹数据怎么从 inference 回 trainer？后面第 16、17 页专门讨论这两条通道的“尖刺”。

## 三、推理侧优化：为什么 KV Cache 会变成瓶颈

Slides 第 9 页讲 KV Caching：每一步只为新 token 计算 q、k、v，然后对之前缓存的 k、v 做 attention，再把自己的 k、v 追加进缓存。页面给出的代价描述是“用大量重计算换大量内存”。Slide 9 还给出一个规模示例：Llama-3-8B 在 bf16 下，每 token 约 128 KB；一条 32k-token 的 trace 约 4 GB；64 条约 256 GB。

**学习者解释**：这段数字的意义不是让人背下来，而是让人意识到 agentic RL 的 rollout 会累积很长的上下文。多轮交互、工具返回、历史观察都会进入序列，KV cache 会随轨迹长度线性增长。于是“显存够不够”往往不由模型参数量决定，而由**并发轨迹数 × 轨迹长度**决定。

Slides 第 10 页讲 Prefix Caching：system prompt + tools 在所有 rollout 中共享；在 Group Rollouts（如 GRPO）中，许多 rollout 共享同一 task prompt；一条 rollout 过去步骤的 KV 也可以在未来步骤复用。页面点名 SGLang RadixAttention 与 vLLM Automatic Prefix Caching。Slide 11 讲 Continuous Batching：以单个 decode step 为粒度调度，完成的序列立刻离开 batch，排队请求补位；通常配合 chunked prefill，或把 prefill 与 decode 分离（disaggregate）。Slide 12 讲 Speculative Decoding：廉价 drafter 猜 k 个 token，policy 一次并行打分，rejection sampling 保持策略的精确分布；页面还给出一个“RL-specific catch”：policy 每个训练步都在变，冻结 drafter 的接受率会衰减，需要用辅助目标在线训练它。

**学习者解释**：这三页合起来说明，推理引擎的优化不是“可选项”，而是 RL 系统吞吐的一部分。Prefix caching 对 agentic RL 尤其重要，因为 agent 的 prompt 往往高度重复；continuous batching 决定了长尾请求会不会拖住整批；speculative decoding 则把“自回归解码的串行性”部分转化为并行验证。Slide 12 的 catch 提醒我们：推理优化一旦与“策略在变”耦合，就会产生新的训练问题。

## 四、训练侧优化：内存与重复前缀

Slides 第 13 页讲 Activation Checkpointing：前向只保留每层输入，反向到达该层时重算内部激活，用完即释放。页面把内存收益描述为“从每层激活降到每层一个输入，外加同时只有一层的激活”，代价是“完整重算约增加一次前向，约 +33% 计算；选择性重算（只 attention）成本低得多”。Slide 14 讲 Prefix Sharing：RL batch 会重复前缀——GRPO group 内同一 prompt、多轮对话中的同一 history。做法是每个前缀只算一次前向和反向，用 tree attention mask 阻止跨分支 attention，position id 按各自独立序列处理，各分支梯度累加到共享前缀上。页面给出两个数字：长 prompt 的 GRPO batch 中 80–95% 的 token 是重复 prompt token，去重后 actor 更新可快至 6 倍；多轮 τ²-bench rollout 压缩为 prefix tree 后为 9.43 倍，DFS 逐条 root-to-leaf 走，相比 dense training 可快至 8.31 倍。

**学习者解释**：这两页是一对镜像。推理侧用 prefix caching 省 KV，训练侧用 prefix sharing 省激活和计算。它们都建立在同一个观察上：RL 数据里大量 token 是重复的。但训练侧多了一层复杂性——反向传播必须在共享前缀上正确累加梯度，还要保证 attention mask 不串味。这与后面第 19–20 页的“sequence extension”直接相关。

Slides 第 15 页讲 Parallelism，图示为 Context Parallelism：GPU 0–3 各保留自己的 Q，KV blocks 轮转。**待核**：该页主要信息在图中，文本提取只能看到“keeps its Q”“KV blocks rotate”等片段，具体并行布局需对照官方 PDF。

## 五、两个引擎之间的尖刺：Weight Sync 与 R3

Slides 第 16 页讲 Weight Sync。Full Weight Sync 是向每个 inference rank 全量广播；1T 参数模型约 2TB 同步。Delta Weight Sync 的观察是：RL 权重更新之间约 99% 参数不变（bf16 变化），因此只同步 delta。页面还提醒：参数需要为推理引擎的并行布局重新分片。Slide 17 讲 Rollout Routing Replay（R3）：问题是微小数值差异可能让 MoE 选择不同的 expert；方案是记录 rollout 时的 expert 选择，并在训练中重放这些选择；因此推理引擎必须把 routing 决策提供给训练引擎。

**学习者解释**：这两页是“系统边界处的正确性”问题。训练和推理即使数学上应当一致，工程上也可能因为分片、精度、kernel 实现而出现微小差异；在 MoE 里这种差异会被放大成离散的 routing 分歧。R3 的思路不是消除数值差异，而是**把 rollout 时的离散决策冻结下来**，让训练复现同一条计算路径。

## 六、Agentic RL 的“sharp bits”：序列扩展、chat template、TITO

Slides 第 19 页用两个 harness 对比 sequence extension。Harness A 把每轮追加到已有 history；Harness B 每两次观察后做 compact，把 A₁ O₁ A₂ O₂ 摘要成 S。页面问：哪种 harness 对训练效率更好？Slide 20 给出训练 batch 视角：一条轨迹一个 advantage Â，广播到所有 action token。Harness A 是一个拼接的 datapoint，token span 为 Task A₁ O₁ A₂ O₂ A₃ O₃ A₄ O₄，loss mask 只有 action 位置为 1，advantage 在 action 位置为 Â；Harness B 是两个 datapoint，都含 Task。页面结论是：重复的 task token 直接 loss 为零，但仍需算 context；因此“在可行范围内尽量保留精确前缀并拼接”。

**学习者解释**：这就是“sequence extension”的实际含义——如果每一步的上下文是上一步上下文的严格扩展，那么前缀可以被共享、被缓存、被增量计算。一旦 harness 做了 compaction，历史被改写，前缀不再扩展，训练侧就无法复用之前的 KV 或激活，也会引入额外的、需要重新计算的 token。Slides 第 21–22 页进一步指出 chat template 的坑：Qwen 3 / Qwen 3.5 的默认 chat template 会从 past history 中移除 reasoning，不满足 sequence extension；agent RL 训练框架常自带自定义 chat template 或“renderers”来保留它（点名 Tinker、PrimeRL）。

Slides 第 23–24 页讲 Token-In, Token-out（TITO）：rollout 数据从推理引擎传到训练引擎，应该用字符串还是 token？页面给的理由是：字符串空间里小而不可控的变换（例如 chat template 加空格）会导致训练与推理的 tokenization 不一致；tokenization 是一对一的，但 de-tokenization 是多对一的。因此应以 token 形式存储和传输。

**学习者解释**：这几页可以看作同一条主线：**让训练看到的 token 序列，和推理实际生成的 token 序列，逐 token 一致**。chat template 改写历史、字符串往返改变 token、compaction 打乱前缀，都会破坏这条一致性。Lecture 12 把这些称为 agentic RL 的 sharp bits，是因为它们不是算法问题，而是数据管道问题。

## 七、同步、异步与系统设计

Slides 第 25 页区分 Sync RL 与 Async RL。Sync RL 把 Train 与 Inference Engines 共置（同一批 GPU 共享）；Async RL 把 GPU 拆给两边，因为 agentic RL 常常是 rollout-bound（长轨迹），可以把更多 GPU 给推理（例如 3:1），但需要 continuous batching 和 in-flight weight update 支持，并需要 staleness / off-policy 修正。页面点名 Pipeline RL、AReaL。Slide 26 讲 In-flight Weight Updates，说明推理框架已经为 RL 系统需求演化，例子来自 SGLang Docs。Slide 27 提到复杂 harness（sub-agents、context compaction 等），点名 RAO 2026、RLM 2025。

Slides 第 29 页讲 Harness Agnostic Design：流行 harness 很多（Codex、Claude Code、OpenHands、Pi、Hermes、Prime Agent 等），为每个 harness 写定制 rollout/environment 代码是 anti-pattern；harness-agnostic 模式是中间层/代理服务，模拟 inference API（chat-completions、responses、anthropic 等），从而“换新 harness 时 0 代码改动”。Slide 30 讲 SPMD：一个 Python 程序跑在每个 GPU rank 上，同一程序里创建 train group 和 infer group，rank < 4 走训练循环，否则走推理循环；页面评价是“直接控制一切时很直接，但不够灵活”，点名 AReaL versions < 1.0。Slides 第 31–33 页讲 Everything-as-a-service w/ Single Controller：编排器/控制器加上 Inference、Agent、Trainer、Weight Sync、Env/Reward 等服务，举出 Open Reward Standard（ORS）、SGLang/vLLM API、Tinker training API 作为示意；好处是 separation of concerns（各组件复杂而专门、轻量编排器便于研究者原型、发布不用同步）与 modularity（协议一致即可替换实现，hosted 或 self-hosted）。Slides 第 34–36 页展示 elastic scale up 与 multi-cluster / heterogeneous compute（8xH100、4xMi350）。Slide 37 给出示例 AstraFlow。Slide 38 讲 multi-policy training：微服务架构便于同时训练多个不同模型。Slide 39 讲 Online RL（部署后训练），点名 AReaL 2.0 2026，以及 Cursor 生产中的 Cursor Tab 与 Composer（每 5 小时从真实用户交互产生新 checkpoint）。Slide 40 讲 Multi-Tenant, Multi-LoRA Training：8 个并发 run 在吞吐上胜过 8 个串行 run（但每 run 的端到端时间变长），每个并发 LoRA run 可以是训练服务的不同用户，需要特殊 kernel（Grouped-GEMM/SGMV）。Slide 41 讲 Tinker：开创 multi-tenant、multi-LoRA RL 训练与解耦训练服务设计，API 设计为“每次训练运行一个 training client，每个 LoRA 权重 checkpoint 一个 sampling client”。

**学习者解释**：这一大段的逻辑是“从单程序到服务化”。SPMD 适合小团队完全掌控一切；但随着 harness 多样、模型多样、租户多样，把每个组件做成服务、用协议通信，才能让维护、替换、弹性扩缩和异构硬件变得可行。Slide 41 的 Tinker API 设计之所以被点名，是因为它把“训练运行的客户端”和“权重检查点的采样客户端”分开，正好对应前面“两个引擎”的世界观。

## 八、可观测性：该盯哪些指标

Slides 第 43 页列出建议跟踪/调试的指标：Reward / pass@1（策略是否在训练任务上变好；警告信号是长期平坦，或训练上升而 held-out 下降，即 reward hacking）；pass@k（覆盖度；若 pass@1 上升而 pass@k 下降，说明多样性坍塌）；Entropy（探索程度；突然趋近 0 或跳变是退化文本信号）；`importance_weight_max`（最坏 token 比 π_train / π_rollout；尖峰意味着不匹配或 stale 数据）；Grad norm（裁剪前更新大小；尖峰常在发散前，持续上行也是信号）；Average staleness（数据落后多少个权重版本；持续上升说明 rollout 跟不上训练）；Trainer MFU（trainer GPU 利用；因 padding、不均衡或小 micro-batch 下降）；Timing：rollout、update、stall、total（一步的墙钟时间去向；stall > 0 表示 trainer 在等 rollout）。

**学习者解释**：这张表把前面所有系统讨论收束成“运维视角”。例如 prefix sharing 失效会表现为 MFU 下降或 update 变慢；async 调度不当会表现为 average staleness 上升；推理与训练数值不一致会表现为 `importance_weight_max` 尖峰。指标是系统与算法之间的接口。

## 九、小结

Lecture 12 的一句话主线是：**LLM RL 系统 = Trainer Engine + Inference Engine + 它们之间的数据/权重通道 + 环境与 harness**。Slides 第 3–8 页定义问题与步骤；第 9–15 页讲两侧各自的优化；第 16–17 页讲同步与一致性；第 18–27 页讲 agentic RL 的特有麻烦（sequence extension、chat template、TITO、async、复杂 harness）；第 28–41 页讲系统设计（harness 无关、SPMD、服务化、弹性、多租户、在线 RL）；第 43 页给可观测性指标。本文所有页码依据均来自给定的 Slides 文本提取稿；公式、图示细节与未在文本中出现的数值，请以官方 PDF 为准。

## 官方来源

- 课程主页：https://www.cmu-agents.com/
- 课程日程与阅读：https://www.cmu-agents.com/#schedule
- 作业与项目要求：https://www.cmu-agents.com/#assignments
- Assignment 1 · Harness：https://github.com/cmu-agents/assignment-1
- Assignment 2 · Eval：https://github.com/cmu-agents/assignment-2
- Lecture 12 slides：https://www.cmu-agents.com/slides/lecture-12-rl-systems.pdf
