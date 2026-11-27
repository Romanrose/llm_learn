# Week-09 Model Evolution 2 学习笔记：RL 实践、Self-Distillation 与 LLM Self-Play

> 基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。本笔记只依据两份官方 PDF 的抽取文本，区分"幻灯片内容"与"我的解释"。图表的精确曲线、数值细节在文本抽取中不完整，相关处保留不确定性。

本讲由两部分组成：Lecture 6（Ao Qu，RL & Self-Distillation in Practice，含 Idan Shenfeld 的 guest lecture 介绍）与 Lecture 7（Alex Wilf，LLM Self-Play）。两讲共同回答一个问题：模型如何在没有（或很少）人工标注新数据的情况下持续进化——一条路径是把 RL / distillation 的训练循环真正跑起来，另一条路径是让模型与自己博弈、出题、解题、验证。

---

## 一、学习目标

读完本笔记后，你应当能够：

1. 复述 PPO / GRPO 作为 LLM 策略梯度方法的损失形式，并说明 advantage 的来源差异。
2. 用统一视角解释 on-policy distillation（OPD）与 self-distillation：二者与 RL 共享同一种 policy-gradient 损失，只是 advantage 的定义不同。
3. 说明 RL 与 OPD 在"信息量"和"学习目标"上的本质差别（每 episode 的 O(1) vs 每 token 的 O(N) bits）。
4. 描述一个训练 step 的五个阶段（rollout → reward → advantage → update → weight sync），并解释为什么模型要"存在两份"（推理引擎与 trainer）。
5. 区分 batch / mini-batch / micro-batch，并说明为什么只有第一个 mini-batch 是严格 on-policy。
6. 识别训练曲线中的正常形态与 red flag（无信号、reward 涨但 validation 降、entropy 崩溃等）。
7. 解释 self-play 的三元结构 Propose–Solve–Verify，并能对比 SFT、RL、self-play 三者在三元上的分工。
8. 用 AlphaZero 的 select / expand-evaluate / back up / train 四步说明搜索如何为策略与价值提供训练信号。
9. 区分 competitive self-play（PSV 类）与 cooperative self-play（SOAR、Goedel-Code-Prover 类）的激励设计与失效模式。
10. 陈述 Generation-Verification Gap（GV-Gap）的含义，以及 self-improvement 成立的三个条件。

---

## 二、核心概念（Lecture 6：RL 与 Self-Distillation 实践）

### 2.1 LLM 作为策略：PPO 与 GRPO 回顾

幻灯片把 LLM 建模为策略：prompt 为 $x$，每个 token 是一个 action $y_t \sim \pi_\theta(\cdot|s_t)$，state 为 $s_t=(x, y_{<t})$，reward 只在结尾给一次（例子：$5+(2\times3)$ 答成 21 则 $r=0$）。

policy-gradient 损失：$L(\theta)=-\sum_t A_t \log \pi_\theta(y_t|s_t)$。

实践中 PPO/GRPO 用裁剪形式：$L(\theta)=-\sum_t \min(\rho_t A_t,\ \mathrm{clip}(\rho_t,1-\epsilon,1+\epsilon)A_t)$，其中 $\rho_t=\pi_\theta(y_t|s_t)/\pi_{old}(y_t|s_t)$。

- PPO：$A_t = Q(s_t,y_t)-V(s_t)$，$V$ 是学出来的 value model（GAE）。
- GRPO：$\hat A_i=(r_i-\mathrm{mean}(r))/\mathrm{std}(r)$，对同一 prompt 的 $G$ 个答案做组内归一化，不需要 $V$。

**解释**：GRPO 用"同题多答的相对好坏"替代 critic，省掉一个与策略同规模的模型；代价是 advantage 只在组内可比。

### 2.2 On-Policy Distillation 与 Self-Distillation

幻灯片先给出 reverse KL 的逐 token 形式：

$$\mathrm{KL}(\pi_\theta\|\pi_T)=\mathbb{E}_{y_t\sim\pi_\theta}[\log\pi_\theta(y_t|s_t)-\log\pi_T(y_t|s_t)]$$

其梯度可写成 $\nabla\mathrm{KL}=-\mathbb{E}[A_t\nabla\log\pi_\theta]$，其中 $A_t=\log\pi_T(y_t|s_t)-\log\pi_\theta(y_t|s_t)$（利用 $\mathbb{E}[\nabla\log\pi_\theta]=0$）。因此它同样是一个 policy-gradient 损失。流程三步：① student 自己写出 $y$；② teacher 给每个 token 打分；③ student 向其靠近。

- **OPD**：teacher 是另一个更大的模型 $\pi_T$（例：Qwen3-32B 教 Qwen3-8B），$A_t=\log\pi_T(y_t|s_t)-\log\pi_\theta(y_t|s_t)$。
- **Self-distillation**：teacher 是"模型自己 + 上下文 $c$"，用 stop-gradient：$A_t=\log\pi_\theta(y_t|c,s_t)-\log\pi_\theta(y_t|s_t)$。$c$ 可以是 demonstration（SDFT）、solution（OPSD）或 feedback（SDPO）。

**解释**：self-distillation 的关键是 $c$ 必须携带模型"单独回答时没有的信息"；否则 teacher 与 student 相同，advantage 恒为 0，无信号。

### 2.3 RL vs OPD：同一个损失，不同的 advantage

幻灯片并列两者：损失相同，区别在 advantage。

| 维度 | RL | OPD |
|---|---|---|
| advantage | $r-\text{baseline}$，一个数作用到所有 token | $\log\pi_T-\log\pi_\theta$，逐 token 一个数 |
| 信息量 | 每 episode $O(1)$ bits | $O(N)$ bits，$N$=token 数 |
| 学向 | 高 reward（可能被 hack） | teacher（及其上限） |

**解释**：这解释了 Shenfeld 的 RL's Razor 线索——on-policy RL 比 SFT 遗忘更少，因为它离原模型更近；而 OPD 用密集的逐 token 信号，样本效率更高，但天花板被 teacher 限制。

### 2.4 OpenClaw-RL：把人类反馈拆成两路

例子：TA 用 agent 批改作业，agent 回复过简，用户说"Too brief. Tell the student why each step is right."。系统在同一批 response、同一次更新中合成两种信号：

- ① RL：judge 判断回复好坏，$r=-1$，同一个 $A$ 给所有 token；
- ② Self-distillation：judge 把回复转成 hint $h$（"explain each step"），带 $h$ 的同一模型作 teacher，$A_t=\log\pi_\theta(y_t|h)-\log\pi_\theta(y_t)$，逐 token。

幻灯片总结：① 每轮都有分数但只有一个数；② 指出该改哪些 token，但只在回复带有修正时存在。

### 2.5 一个训练 step 与两份模型

五阶段：① rollout（vLLM/SGLang 推理）→ ② reward（verifier/tests/judge，每条 response 一个分）→ ③ advantage → ④ update（FSDP/Megatron）→ ⑤ weight sync。另有 frozen 的 reference 起始模型用于 KL penalty。

幻灯片自问自答：为什么模型存在于两处？因为生成需要快速 KV-cache 引擎，训练需要梯度与 optimizer state，所以每次更新后复制权重。

### 2.6 Rollout 与 Trainer 的资源画像

- **Rollout**：只做前向、保留 KV cache、PagedAttention 分页 + continuous batching。以 Qwen3-8B（8.2B 参数）为例：bf16 权重约 $2\text{B}\times8.2\text{B}\approx16$ GB，外加 KV cache（约 0.15 MB/token）。
- **Trainer**：需要 weights（bf16, 2B）+ grads（bf16, 2B）+ fp32 权重副本（4B）+ Adam 的 momentum 与 variance（各 4B），合计约 16 bytes/参数，约 130 GB，超过单张 80 GB GPU；FSDP 把权重、梯度、optimizer state 切分到多卡，用到某层前才 gather 全量。

**解释**：这组数字是数量级说明，不是性能基准；文本中"memory per parameter"表的具体字节需以原幻灯片为准。

### 2.7 术语与 verl 映射

幻灯片给出术语表（policy/actor、rollout、state、reward、advantage、old policy、reference policy、critic、step、epoch）及对应 verl 字段：`actor`、`rollout`、`token_level_scores`、`advantages`、`old_log_probs`、`ref_log_prob`、`critic/values`、`global_steps`、`total_epochs`。

### 2.8 Batch 层级与 on-policy 的边界

例子配置：$B=1024$ prompts，$n=5$ responses/prompt → 5120 responses 为一次 rollout；$M=256$ prompts 为一个 mini-batch → 4 次 optimizer step；8 卡数据并行 → 每卡 160 条；micro-batch $m=4$ → 每卡 40 个 micro-batch 作梯度累积。

幻灯片的关键问答：on-policy 指用当前权重采样；只有 mini-batch 1 是 on-policy，因为每次 mini-batch 后模型已更新，从第 2 个起 $\pi_\theta\neq\pi_{old}$。micro-batch 只是为了放进显存而切分，不改变这一点。

### 2.9 损失中的熵与 KL

损失可拆为三项：policy gradient（含 clip，$\rho_t$ 衡量 token 概率变化，$A_t>0$ 推高、$<0$ 压低）、$\beta\,\mathrm{KL}(\pi_\theta\|\pi_{ref})$（ref 为 frozen 起始模型；reasoning RL 通常关闭，RLHF 通常开启）、$-\alpha H(\pi_\theta)$（熵奖励通常关闭，但要始终观察曲线）。

### 2.10 训练曲线：正常 vs red flag

以 verl 公开的数学 baseline（Qwen2.5-Math-7B，GRPO 变体，AIME 2024）为例，幻灯片列出若干曲线形态：

- reward：正常是慢启动后稳定爬升；red flag 是从头平坦（无信号）。
- validation：正常随 reward 上升；red flag 是 reward 涨而 validation 降。
- 另一条曲线：正常保持在 0 以上；red flag 是趋向 0（collapse）。
- 随 reasoning 变化而变化的曲线：正常随推理变化；red flag 是卡在最大长度（被截断）。
- 更新幅度类：正常小而稳（此处约 1e-4）；red flag 是尖峰（一步走太远）。
- 另一条：正常先高后稳；red flag 是尖峰或 NaN（不稳定）。

**不确定性说明**：幻灯片只给出形态描述与一个公开 W&B run 链接，未在文本中给出完整数值曲线；本笔记不虚构具体数值。

### 2.11 verl 的一步（代码骨架）与使用流程

`PPOTrainer.step()`（sync 模式）顺序：加 batch 去生成 → 采样 $B$ → 释放 rollout 显存 → balance batch（让各卡 token 总量相近）→ 计算 old/ref log-prob 与 values → 计算 advantage → 更新 actor（每 mini-batch 一步）→ `update_weights` 同步回推理引擎。

使用流程五件事：① 任务转 parquet（每行一个 prompt，含 `data_source`、`prompt`、`reward_model` 的 `style` 与 `ground_truth`）；② 写 reward function（示例 `compute_score` 抽取答案后与 ground truth 比较返回 float）；③ 启动命令（`algorithm.adv_estimator=grpo`、`data.train_batch_size=1024`、`rollout.n=5`、`ppo_mini_batch_size=256`、`n_gpus_per_node=8` 等覆盖配置）；④ 看曲线；⑤ `verl.model_merger merge` 把 FSDP 分片合回 Hugging Face 格式，再用 vLLM  serving。

### 2.12 verl vs reef

- verl：先训练后部署。固定 prompt 集 + 标签，trainer 内部 rollout→reward→update 循环 N 步，产出 checkpoint，导出后单独部署给用户。
- reef：边服务边学习。live traffic（用户与 agent 的请求、回复、反馈）进入一个同时承担 Serve / Train / Evaluate 的推理服务器，产出新版本且无需重启。

幻灯片一句话：verl 是你准备好数据集上的 trainer；reef 是从自身流量中学习的 inference server。

---

## 三、核心概念（Lecture 7：LLM Self-Play）

### 3.1 定义与三元结构

Self-play 定义（引 Zhang+ 2025，及 "Alex's Edition"）：agent 通过与自身的历史版本或并发版本交互，迭代精炼策略；扩展版强调"探索新问题供历史/并发版本求解并从中学习"。

Propose–Solve–Verify 三元的分工对比：

| 范式 | Propose | Solve | Verify |
|---|---|---|---|
| SFT | Human | Human | Human |
| RL | Human | AI | Human |
| Self-play | AI | AI | Human / AI |

**解释**：self-play 把"出题"也交给模型，这是它与普通 RL 的最大结构差异；验证仍可由人或 AI 承担，这一列决定了后面 GV-Gap 的讨论。

幻灯片以 The Bitter Lesson 作为引子（仅标题，无展开文本）。

### 3.2 AlphaZero 的四步循环

简化 AlphaZero：① Select ② Expand and evaluate ③ Back up ④ Train。幻灯片用约 20 帧走完一棵小树：

- 从状态 $S$ 开始，policy $\pi(S)$ 提议走法，展开出 A、B、C，value 函数给出 $V(A)=0.60$、$V(B)=0.78$、$V(C)=0.10$；回传估计，选 $B$ 分支。
- 展开 $B$，$\pi(B)$ 提议 F、G，二者是 terminal，实际 reward 为 0.20 与 0.00，回传得 $B$ 的均值 0.10——观测修正了 $V(B)=0.78$ 的预测。
- 再选 $A$，展开 D、E：$V(D)=0.85$，E 为 terminal reward 0.40，回传 $A$ 的临时估计 $\mathrm{mean}(0.85,0.40)=0.625$。
- 再选 $C$，展开 H、I 为 terminal，reward −0.20 与 −0.40，$C$ 均值 −0.30。
- 选 $D$，展开 J、K 为 terminal，reward 1.00 与 0.80；回传 $D$ 均值 0.90、$A$ 均值 0.73、$S$ 均值 0.26。
- 训练：policy 学 $\pi(S)\to A$、$\pi(A)\to D$、$\pi(D)\to J$；value 学 $V(S)\to0.26$、$V(A)\to0.73$、$V(D)\to0.90$。

**解释**：搜索提供"比原始 $V$ 更好的目标"（$B$ 从 0.78 被修正到 0.10），训练再把搜索的结果蒸馏回网络——这是 self-play 中"自我提升"的机制原型。幻灯片未给出该例的搜索预算、温度等细节。

### 3.3 Competitive LLM Self-Play：PSV 与形式化验证

Solver 因解出问题获 reward；Proposer 因"出对 solver 而言难的问题"获 reward。幻灯片用 Verus（形式化验证代码）与 Python 单元测试对比：传统单测只覆盖若干用例，而 spec + proof 表达对所有输入的保证。

流程：Propose（如 `has_z`、`is_odd`、`mod`）→ Solve → Verify，得到如 ✅✅✅❌ 的通过模式，并按难度标注 Easy/Medium/Hard。

结果（Dafny2Verus / MBPP / HumanEval 三组柱状图，比较 AlphaVerus·Inference、RFT·Test-time、PSV·Test-time，横轴 k=1/5/10）：幻灯片给出的 test-time pass@1 相对 RFT 的增益为 +31.17 pp（Dafny2Verus）、+32.95 pp（MBPP）、+13.51 pp（HumanEval）。**说明**：这是幻灯片明示的数值；柱状图本身在文本抽取中不完整，未列出各组绝对值，本笔记不补造。

其余幻灯片标题包括 Self-Improvement、The Effect of Verification、Scaling Laws，但文本未给出其图表内容，保留不确定性。

### 3.4 实现技巧与其他 competitive 工作

实现技巧（幻灯片列点）：大量 prompt engineering；用小模型；批量推理（vLLM/SGLang）；问题的多样性比难度更重要（demo）。

其他 competitive self-play 工作（幻灯片给了 proposer/solver reward 形式与部分数值，这里按原文摘录关键点，不扩写）：

- Language Self-Play（Kuba et al., 2025）：共享模型、开放式 prompt、学到的 reward；$R_p=-\mathbb{E}[R_s]+$ self-reward 正则防坍缩；比纯 RL 高 +0.7 pp（AlpacaEval win rate，Llama-3.2-3B：39.5% vs 38.8%）。
- Absolute Zero Reasoner（Zhao et al., 2025）：Python 验证的 deduction/induction/abduction；$R_p=(1-\bar r)\mathbb{1}[0<\bar r<1]$，$R_s=\mathbb{1}[\text{correct}]$，无人工任务数据；7B-Coder 50.4 vs 44.3（不同数据/配方）。
- R-Zero（Huang et al., 2025）：数学题、多数投票伪标签、无 executor；$R_p=\max(0,1-2|\hat p-\tfrac12|-\text{repetition penalty})$；Qwen3-4B 49.93 vs 45.01（无标准 RL-only 对照）。
- STP（Dong & Ma, 2025）：Lean/Isabelle 的猜想者–证明者；过滤 $0<$ proof pass rate $\le 1/4$；LeanWorkbook 26.3% vs 13.2%（此前 expert iteration）。
- Self-Challenging Agents（Zhou et al., 2025）：工具使用任务，用通过解与失败例过滤，不学 proposer reward；8B 23.5 vs 12.9 PAE。
- Skill Self-Play（Huang et al., 2026）：演化技能库指导出题；$R_p=\mathbb{1}[\text{valid}]\cdot(1-2|v_s-\tfrac12|)$ 加重复惩罚；工具调用 +2.8–6.5 pp（对照是 unguided SP）。

**解释**：多条工作都加了"防坍缩"或"防重复"的正则，说明纯 adversarial 出题容易退化为重复或无效难题。

### 3.5 Competitive self-play 的问题

幻灯片明确指出：proposer 被激励去出难题，它确实出了；但并非所有难题对 solver 的训练都有用。于是问题变成：如何激励 proposer 生成"难且有用"的问题？这直接引出 cooperative 路线。

### 3.6 Cooperative LLM Self-Play：SOAR 与 Goedel-Code-Prover

Cooperative 的结构：Propose → Solve → Verify → ① Train → ② Evaluate（在 test set 上看性能），用下游表现反过来评价 proposer。

幻灯片用 bi-level optimization 类比：外层超参 $\phi$（此处是 proposer/teacher），内层模型参数 $\theta$（solver/student）。Language self-play 即：teacher 生成 $(q,a)$，student 做 10 步 RL，用 student 训练前后的 accuracy 差（RLOO）更新 teacher——"用学生的进步给有用的题发奖励"。

SOAR 实验（Llama-3.2-3B-Instruct，MATH、HARP；0/128 正确，50/50 划分），test pass@32：

| 数据集 | Hard-only RL | SOAR-PQ |
|---|---|---|
| MATH | 9.6 ± 2.6 | 18.9 ± 5.3 |
| HARP | 8.2 ± 1.0 | 12.3 ± 2.0 |

幻灯片还给出一条 ICL 直觉：in-context learning 与梯度下降训练的相似性（引 von Oswald+ 2022、Akyürek+ 2022、Dai+ 2023），并提问 ICL 能否替代内层训练循环——对应图中"RL 内层训练"与"ICL 无训练循环"两条路径的对比。

Goedel-Code-Prover 结果（每个 benchmark 取最强 baseline，非 RL）：Verina(189) 上 Goedel-Code-Prover-8B 68.8% vs BFS-Prover-V2-32B 24.3%；Clever(161) 上 54.0% vs Goedel-Prover-V2-32B 25.5%；AlgoVeri(77) 上 62.3% vs DeepSeek-Prover-V2-671B 23.4%。

其他 cooperative 工作（按幻灯片摘录）：SGS 增加 Guide 给猜想打"相关性/自然性"分；LADDER 递归生成失败题的更简变体；SEAL 学自生成微调数据与更新指令；CPMöbius 用 Player 更新后的 accuracy 增益训 Coach；CompassPlay 用与目标能力的梯度对齐近似学习价值；Self-Play Pretraining 从零共训程序生成器与字节预测器。

### 3.7 验证的角色：GV-Gap

幻灯片先给直觉对比：给一张图判断 cat/dog（验证容易），与解 $2x+3=11$（求解有确定步骤）——两者难度结构不同。随后提出 Generation-Verification Gap。文本给出的 findings：

- 相对 GV-Gap 随 pretraining flops 单调增长（generator 与 verifier 为同一模型时）；
- 当 verifier 与 generator 的容量差距增大时，gap 随该比例增大。

Self-improvement 成立的三个条件（幻灯片明列）：① improvable generation（输出有方差）；② GV-Gap（验证比求解更好）；③ high-fidelity model update（能可预测地把模型拟合向被选中的样本）。

补充幻灯片：T1 标题为"Tools Can Boost Verification Capacity"（仅标题，无展开）。Verification and Error Propagation（引 Fu et al., NeurIPS 2025）：递归训练会跨代放大错误；不可靠过滤会让模型强化自身错误；足够可靠的自验证即使在完全合成数据下也能防止坍缩。Sharpening 机制（引 Huang et al., 2024）：用模型自身的打分信号选 response，再训练它更可靠地生成这些 response；sharpening 把昂贵的推理时选择摊销进权重；只有打分信号有用时，更好的自评分才意味着更好的答案。

---

## 四、方法比较

### 4.1 RL / OPD / Self-distillation（Lecture 6 表）

| 方法 | 谁给 response 打分 | token $y_t$ 的 advantage |
|---|---|---|
| PPO | reward $r(x,y)$ | $Q(s_t,y_t)-V(s_t)$，$V$ 为学到的 critic |
| GRPO | reward $r(x,y)$ | $(r-\mathrm{mean})/\mathrm{std}$，对同 prompt 的 $n$ 条 response，均值替代 $V$ |
| OPD | 另一个更大的模型 $\pi_T$ | $\log\pi_T(y_t)-\log\pi_\theta(y_t)$，逐 token 不同 |
| Self-distillation | 同一模型 $\pi_\theta+c$ | $\log\pi_\theta(y_t|c)-\log\pi_\theta(y_t)$，唯一差别是 teacher prompt 里的 $c$ |

### 4.2 Competitive vs Cooperative self-play

| 维度 | Competitive（PSV 类） | Cooperative（SOAR、Goedel-Code-Prover 类） |
|---|---|---|
| proposer reward | 题目对 solver 的难度（solver 解不出） | 题目带来的 solver 实际进步（训练前后 accuracy 差等） |
| 优点 | 信号直接、易实现 | 直接优化"有用性"，缓解难题≠有用题的问题 |
| 风险 | 出题退化为重复/无效难题 | 需要内层训练或可靠代理，成本更高 |

### 4.3 verl vs reef

| 维度 | verl | reef |
|---|---|---|
| 数据 | 固定 prompt 集 + 标签 | live traffic（请求、回复、反馈） |
| 循环 | 先训后部署，checkpoint 导出 | 边服务边学，新版本不重启 |
| 定位 | 数据集上的 trainer | 从自身流量学习的 inference server |

---

## 五、局限与不确定性

1. **幻灯片是教学简化**：PPO/GRPO 公式省略了细节（如 GAE 的 $\lambda$、KL 的具体估计方式），verl 代码是 simplified 版本，不能当作完整实现规范。
2. **数值均为幻灯片明示值**：如 +31.17 pp、SOAR 表、Goedel-Code-Prover 柱状图数值；本笔记未补造任何未出现的实验数字，也未虚构作业与参考文献。柱状图的绝对值、误差棒在文本抽取中缺失。
3. **曲线判读依赖单例**：训练曲线一节只基于一个公开 W&B run 的形态描述，"正常/red flag"是经验规则而非定理。
4. **Self-play 的可扩展性未定**：GV-Gap 的 findings 只给出单调关系的方向，幻灯片未给出定量预测公式；"三个条件"是必要框架，不保证充分。
5. **理论引用的边界**：ICL≈梯度下降的类比（von Oswald+ 等）在幻灯片中只作为直觉，不应过度外推。
6. **OCR 风险**：部分人名/年份（如 Kaur et al., 2026；Sundaram+ 2026）与符号（$R_p$、$\bar r$、$\hat p$）按抽取文本转录，可能有失真；引用时请回原文核对。

---

## 六、复习清单

- [ ] 写出 PPO 与 GRPO 的损失，并说明 $A_t$ 分别怎么来。
- [ ] 从 reverse KL 推出 $\nabla\mathrm{KL}$ 的 policy-gradient 形式，指出 $\mathbb{E}[\nabla\log\pi_\theta]=0$ 用在哪。
- [ ] 用一句话说清 OPD 与 self-distillation 的差别（teacher 是谁、$c$ 是什么）。
- [ ] 解释 RL 的 $O(1)$ bits/episode 与 OPD 的 $O(N)$ bits 的含义及后果。
- [ ] 画出训练五阶段，并回答"为什么模型要在两处"。
- [ ] 给定 $B,n,M,G,m$，算出 optimizer step 数、每卡 response 数、梯度累积步数。
- [ ] 解释为什么 mini-batch 2 起不再是 on-policy。
- [ ] 列出至少四个训练曲线 red flag 及其含义。
- [ ] 说出 verl 使用流程五步，以及 `model_merger` 的作用。
- [ ] 对比 verl 与 reef 的数据来源与部署方式。
- [ ] 用 AlphaZero 例子说明"搜索修正 value 预测"发生在哪一步。
- [ ] 填出 SFT / RL / self-play 的 Propose–Solve–Verify 表。
- [ ] 说明 competitive self-play 的核心缺陷，以及 SOAR 如何用 student 前后 accuracy 差重设 proposer reward。
- [ ] 陈述 GV-Gap 的两条 findings 与 self-improvement 的三个条件。
- [ ] 解释 sharpening 机制，以及"自评分有用"这一前提为何关键。

---

官方幻灯片来源：

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec6%20-%20rl%20in%20practice.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec7%20-%20self%20play.pdf
