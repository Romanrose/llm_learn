# MIT MAS.S62 · Self-Evolving AI · Fall 2026
## Week 07 学习笔记：Model Evolution 1（Test-time Training、RL、Distillation 与 Continual Learning）

> **说明**：本笔记基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。以下内容严格区分“幻灯片明确给出的内容”与“整理者的解释性归纳”。幻灯片中部分图表、公式渲染存在 OCR 提取缺失或失真（例如部分公式符号、图内插画细节、坐标轴数值），笔记中对这些位置保留不确定性，不将其当作论证依据。输入材料中的公告（作业、项目 checkpoint 等）仅作背景记录，不虚构具体要求。

---

## 0. 材料范围与讲座定位

本次 week-07 对应两份官方幻灯片：

1. `lec6 - training.pdf`（Paul Liang，Lecture 6 – Test-time Training）：主线是从 RL 基础 → RLHF/PPO/GRPO/DPO → Test-time RL/TTT → Distillation（含 on-policy self-distillation）→ 以一张“反馈类型 × 更新算法 × 更新范围”的总表收束。
2. `model_guest.pdf`（Idan Shenfeld，Continual Learning via Self-Distillation）：主线是 catastrophic forgetting、RL 与 SFT 的遗忘差异（“RL's Razor”）、on-policy vs off-policy 的统一视角，以及用 self-distillation 做 continual learning。

两讲合起来构成“Model evolution”的第一部分：**模型如何在部署时或持续学习中继续演化**——既包括用 RL 从奖励中学习，也包括用蒸馏从稠密反馈中学习，还包括在测试时自适应。

幻灯片开头的公告信息（Homework 2 关于 harness evolution、midterm report + presentation 日期、项目应完成数据集处理/基线/误差分析等）属于课程行政信息，本笔记仅记录其存在，不展开、不虚构细节。

---

## 1. 学习目标

依据幻灯片内容，学完本周应能够：

1. **复述 RL 的基本形式化**：MDP 的组成（states、actions、transition、reward、start state、discount factor、horizon）、return、policy、goal，并解释 imitation learning 与 RL 的交集及其三个问题（distribution mismatch、难以从次优状态恢复、专家轨迹不一定可得）。
2. **解释 policy gradient 的直觉**：以“Pong from Pixels”为例说明没有训练标签时如何用奖励信号调整动作概率；理解 raw reward 的方差问题与 baseline/relative improvement 的作用；理解 actor-critic 中 Q(s,a)、V(s)、advantage A(s,a)=Q(s,a)−V(s) 的角色。
3. **说明 PPO 的两个关键机制**：trust region（限制新旧策略 KL 距离）与 clipping（进一步近似 KL），以及“限制每次更新幅度 → 稳定训练”的逻辑。
4. **走通 RLHF 流程**：预训练 + SFT → 采样多回复 → 人类排序 → 训练 reward model → 用 RL（PPO/GRPO）优化；理解 pairwise preference 相对排序的动机（人类偏好 noisy、uncalibrated）。
5. **对比 PPO 与 GRPO**：GRPO 去掉 value model，用一组回复的奖励均值作为 baseline（需要较大 group size），并可用 rule-based verifier（binary checks、test cases、length、format）替代 reward model。
6. **说明 DPO 的定位**：它不是 RL，不显式推断 reward，而是直接提高偏好回复的 likelihood、降低其他回复的 likelihood，属于离线偏好优化，更像 supervised learning。
7. **识别 reward hacking**：模型最大化 reward 未必对齐目标；reward 设计越简单往往越稳健（幻灯片给出两个例子：利用漏洞反复击倒 respawn 目标、LLM 攻击棋类引擎）。
8. **理解 test-time training / test-time RL**：从自生成且变化的奖励信号（如多次采样后的 majority vote）学习；幻灯片声称 test-time RL > in-context learning，且 data augmentation 与 task-specific adapters 有帮助；OpenClaw-RL 将自然语言批评翻译为可执行 reward 信号。
9. **区分 SFT / RL / Distillation 三者**：谁写解答（teacher vs student）、反馈形态（逐 token 复制 vs 环境给一个分数 vs teacher 逐 token 打分）。
10. **理解 on-policy self-distillation**：teacher = student + 更多反馈（privileged information），从而突破外部 teacher 的限制，实现自改进；并了解其在 reasoning 与 continual learning 中的应用。
11. **解释 catastrophic forgetting 与 “RL's Razor”**：幻灯片给出的核心结论是“RL 比 SFT 遗忘更少”，并用“微调后策略与基座策略在新任务上的 KL 散度”作为几乎完美预测遗忘的 predictive variable；由此得出“要学而不忘，应做 on-policy learning”。
12. **用总表组织知识**：按 feedback 类型（dense feedback / rewards or verifiers / self-generated targets / human-given labels）与更新算法（SFT / RL / Distillation）、更新范围（full weights / adapters / partial weights）定位各类方法。

---

## 2. 核心概念（按幻灯片脉络）

### 2.1 从 prompting 到 RL 的路线图

幻灯片给出一个 roadmap：输入是 `Input, (reasoning step 1, step 2, step 3…), output`，三种方法：

- **Method 1：Direct prompting，无训练**（如 CoT）。
- **Method 2：Supervised fine-tuning**，假设已有 reasoning traces。
- **Method 3：Reinforcement learning**（本讲重点），假设没有 reasoning traces，但有对推理与输出打分的 reward function。

**解释**：这条路线图把“推理轨迹是否可得”作为方法选择的分水岭——有轨迹走 SFT，没有轨迹但有评价信号走 RL。幻灯片没有讨论三者混合的工程细节，笔记不补充。

### 2.2 RL 基础：MDP、return、policy、goal

幻灯片列出 MDP 定义：状态集 S、动作集 A、转移函数 P(s′|s,a)、奖励函数 r(s,a,s′)、起始状态 s₀、折扣因子 γ、horizon H；以及 return、policy、goal 三个待定义项。**注意**：幻灯片中 return/policy/goal 的具体公式在提取文本中为空（仅有标签），属于图表/公式提取缺失，不应臆造公式；其标准含义可理解为累积折扣回报、状态到动作分布的映射、最大化期望回报，但这是解释而非幻灯片原文。

### 2.3 Imitation learning 与 supervised learning 的交集

幻灯片：获取专家轨迹（如人类驾驶/视频演示）→ 用监督学习预测专家动作。三个问题：

1. distribution mismatch；
2. hard to recover from suboptimal states；
3. expert trajectories not always available。

**解释**：这三点正是后续转向 RL（让模型自己行动、由环境评价）的动机；幻灯片未展开 derivations。

### 2.4 Policy gradients：Pong from Pixels 的直觉

幻灯片用 Atari Pong 说明：网络看到得分 +1、被得分 −1，问“能否用这个训练网络”。若有训练标签，则最大化 Σ log p(yᵢ|xᵢ)；但没有标签。于是：

- 按当前 policy 行动多次（Run 1/2/3），得到 Win / Lose / Lose；
- 对 Win 的 run 最大化 Σ log p(yᵢ|xᵢ)，对 Lose 的 run 最大化 −1·Σ log p(yᵢ|xᵢ)；
- 一般化后：最大化 Σ rᵢ log p(yᵢ|xᵢ)。

幻灯片还给出 **Reinforce algorithm** 与 **ε-greedy** 说明：策略不好时先完全随机探索，策略变好后减少探索、更多从 policy 采样。

**解释**：这实质是“好结果提高对应动作概率、坏结果降低”的加权似然；幻灯片特别指出其**高方差**，并给出补救直觉：raw reward 未必有意义，重要的是“比预期高还是低”——与 baseline 比较、使用相对改进（例如奖励的 exponential moving average）。

### 2.5 Actor-Critic

幻灯片：更好的 baseline 是“若某状态下某动作优于该状态的期望值，就提高该动作概率”。定义：

- Q(s,a)：从状态 s 采取动作 a 期望得到的总奖励；
- V(s)：从状态 s 期望得到的总奖励；
- advantage A(s,a) = Q(s,a) − V(s)：大则“满意”，小则“不满意”。

两个模型：**actor 学 policy（决定采取什么动作）**，**critic 学状态与动作的价值（评估动作多好）**；幻灯片引用 [Minh et al., Asynchronous Methods for Deep Reinforcement Learning, ICML 2016] 的图（图内结构细节在文本提取中不可见，保留不确定性）。

### 2.6 PPO：trust region 与 clipping

幻灯片列出两个算法：

1. **TRPO**：限制新旧策略之间的 KL divergence（距离）；
2. **PPO**：进一步用 clipping 近似 KL divergence 的约束。

核心句：**Restrict each update to be small → stable training**。引用 [Schulman et al., TRPO, ICML 2015] 与 [Schulman et al., PPO, 2017]。

**解释**：这是“别一步走太远”的稳定性思路；幻灯片未给出 clip 目标函数的具体形式，笔记不补公式。

### 2.7 RLHF 五步与 reward model

幻灯片给出 Step 0–4：

- Step 0：预训练 LLM 并做 supervised fine-tuning；
- Step 1：对每个 prompt，把 LLM 视为 policy，采样多个回复；
- Step 2：人类按质量排序；
- Step 3：训练 reward model 预测人类偏好/排序（输入完整模型回复）；
- Step 4：用 RL（如 PPO、GRPO）微调模型以最大化 reward model 分数。

随后说明动机：不可能让人类为一切写 gold answers，所以训练 reward model 预测偏好；而**人类偏好 noisy and uncalibrated**，故采用 **relative preference tuning via pairwise comparisons**。幻灯片用“剑桥的详细介绍 vs ‘剑桥是英格兰北部一个小村庄、毫无历史意义’的荒谬描述”示例，说明 pairwise “is better than” 判断比绝对打分更可靠。

### 2.8 PPO 在 LLM 中的三组件与算法

三组件：

1. **Actor model/policy**：已预训练 + SFT 的 LLM；
2. **Reward model**：训练好后**冻结**，对完整回复给出标量奖励；
3. **Critic model/value**：可学习价值函数，输入部分回复，预测 V(s)。

算法五步：生成回复 → reward model 打分 → 计算 advantage A(s,a)=Q(s,a)−V(s)（value model 估计“某动作 a（即某个词）相对平均动作好多少”，状态 s 为 prompt + 已生成词）→ 优化 policy（PPO 目标，KL + clip 惩罚大变化）→ 更新 value function。幻灯片明确提示 “Recall Actor-critic models!!”。

### 2.9 GRPO（DeepSeek R1）

关键差异（幻灯片原文要点）：

- **放弃 value model**，用一组回复奖励的平均值估计 baseline（需要较大 group size 才能准确估计 baseline）；
- 用一组回复计算 advantage 与梯度更新；
- 不用 learned value function，只用组内奖励的简单统计；
- **放弃 reward model，改用 rule-based verifiers**（binary checks、test-cases、length、format）。

引用 [Guo et al., DeepSeek-R1, arXiv 2025]。

### 2.10 DPO

幻灯片明确：**DPO 并不是在做 reinforcement learning**。它不从偏好数据推断 reward，而是直接提高 preferred responses 的 likelihood、降低其他 responses 的 likelihood；更接近 supervised learning，也称 **offline preference optimization**。引用 [Rafailov et al., DPO, NeurIPS 2023]。

### 2.11 Reward hacking

两条要点：模型学会最大化 reward，但 reward 不总对齐目标；设计 reward 要小心，**更简单的 reward 往往更稳健**。幻灯片给两个例子：某 RL agent 通过利用漏洞反复击倒孤立泻湖中 respawning 的目标，得分比人类高 20%；另一个 LLM 攻击棋类引擎使自己获胜。引用 [OpenAI, Faulty reward functions in the wild]。

**注意**：这里“20% higher scores than humans”是幻灯片转述的案例数值，非本课程实验；笔记如实保留出处语境。

### 2.12 Test-time RL 与 Test-time Training

- **Test-time RL**：从自生成且变化的奖励信号学习，例如对多次采样回复做 **majority vote** 作为奖励。引用 [Zuo et al., Test-Time Reinforcement Learning, NeurIPS 2025]。
- **Test-time Training**：适应 deployment distributions；幻灯片声称 **Test-time RL > In-context learning**，且 **data augmentation helps**、**task-specific adapters help**。引用 [Akyurek et al., The Surprising Effectiveness of Test-Time Training for Few-Shot Learning, ICML 2025]。
- **OpenClaw-RL**：给定文本反馈，设计 reward model 把自然语言批评翻译成可执行的 reward 信号用于 RL。引用 [Wang et al., OpenClaw-RL: Train Any Agent Simply by Talking, ICML 2025]。

**解释**：这一组工作把“测试时”从“只改上下文”推进到“改参数/适配器”，并用自生成信号或语言反馈替代人工标签；具体算法细节幻灯片未给，笔记不补。

### 2.13 LLMs for Discovery：RL for Test-Time Discovery

幻灯片先回顾：LLM 也能演化自己的 context（即 solution space）来解决开放式问题（NP-hard 优化、coding、scientific discovery）。然后对比两种范式：

- **LLMs as optimizers**：Archive（parent solution）→ Solution LLM → External verifier → Verifier feedback，**训练时训练、测试时冻结**（“Trained at test time / Frozen at test time”两栏对照）。
- **TTT-Discover**：Archive（task + parent + score）→ Solution LLM → External verifier；测试时**更新参数**，trainable-model 的输入为 task + parent solution + score，输出为完整 solution；与前者“frozen solution LLM”不同，这里用同一个可训练 LLM。

对照表字段（幻灯片原文）：Updated parameters（None vs Solution LLM）、Trainable-model input（— vs Task + parent solution + score）、Trainable-model output（— vs Complete solution）、Complete solution from（Frozen solution LLM vs Same trainable LLM）。引用 [Yuksekgonul et al., Learning to Discover at Test Time, 2026] 与 [Jiang et al., Evolving in Thought Space: Training a Small Model at Test-time Unlocks Better Discoveries, 2026]。

**不确定性说明**：对照表在提取文本中列对齐不完全可靠（“Trained at test time / Frozen at test time”与两列的对应关系需以原图为准）；笔记按语义保守表述，不强行断言具体列归属。

### 2.14 Distillation：从稀疏奖励到稠密反馈

幻灯片点题：RL 的关键问题是**只有很小的 reward 作为训练信号**；如何从 dense feedback 学习？答案是 distillation。引用 [Zhao et al., Self-Distilled Reasoner: On-Policy Self-Distillation for LLMs, ICML 2026]。

**Teacher-Student Distillation（即 SFT、instruction tuning）**：teacher 写出 w1* w2* w3* w4*，student 逐词复制 w1 w2 w3 w4。问题：student 只模仿答案，**从不见自己的错误，也学不到 teacher 如何纠正常见错误**。

**On-policy Distillation**：student 先写自己的尝试（w1 w2 w3 w4），teacher 对该尝试打分并纠正，student 再复制 teacher 的分数/纠正。引用 [Agarwal et al., On-policy distillation of language models: Learning from self-generated mistakes, ICLR 2024]。幻灯片强调：student 写 attempt，所以**能看到自己的错误**。

### 2.15 三方法对照表（幻灯片原表）

| | SFT | RL | Distillation |
|---|---|---|---|
| **Policy?** | Teacher writes solution | Student writes attempt | Student writes attempt |
| **Feedback?** | Student copies solution, token by token | Environment grades attempt, one score | Teacher grades attempt, every token |

**解释**：这张表是本周的“压缩知识”：区别不在模型结构，而在**谁产生轨迹**与**反馈的粒度/来源**。SFT 是 off-policy + 稠密监督；RL 是 on-policy + 稀疏标量；蒸馏是 on-policy + 稠密教师评分。

### 2.16 On-Policy Self-Distillation

动机（幻灯片原文）：若想 self-improvement，就不想被 teacher model 限制；在 self-distillation 中，**teacher = student + more feedback（privileged information）**。图示：student 写 attempt（w1…w4），带更多反馈的同一 student 给 attempt 打分，student 复制 teacher scores；并标注 “Dense feedback”。引用同 [Zhao et al., ICML 2026]。后续两张图分别指向 **Self Distillation for Reasoning** 与 **Self Distillation for Continual Learning**，引用 [Hubotter et al., Reinforcement Learning via Self-Distillation, ICML 2026] 与 [Shenfeld et al., Self-Distillation Enables Continual Learning, ICML 2026]（图内曲线/数值在提取中不可见，保留不确定性）。

### 2.17 讲末总表：反馈类型 × 更新算法 × 更新范围

幻灯片最后一张图以二维结构收束：

- 纵轴 **Type of feedback**：Dense feedback / Rewards or verifiers / Self-generated targets / Human-given labels；
- 横轴/节点 **Update algorithm**：Full weights 下含 SFT、RL、Distillation；Partial weights 下含 Adapters；
- 另一维 **What is updated**。

**解释**：这是把本周所有方法放在“反馈形态—更新算法—参数范围”的三维坐标系里；具体每个格子填了哪些方法，幻灯片以图形呈现，文本提取不完整，笔记不臆造完整映射。

---

## 3. Continual Learning via Self-Distillation（guest 讲）

### 3.1 立意：以“学习能力”定义智能

开篇主张：**不要只以 AI 系统能做什么来定义智能，而要看它学得多好**（“Instead of defining intelligence in terms of what an AI system can do, focus on how well it can learn”）。

为什么关心学习能力（幻灯片三条）：

1. **Personalization**：学习并适应用户偏好的 AI 系统；
2. **Specialization**：解决难题需吸收相关文献、上下文与领域知识；
3. **Next Scaling Frontier**：已部署 AI 每天处理超过 **300 trillion tokens**，约等于每天一个 web-scale corpus。

**注意**：300 trillion tokens/day 是幻灯片给出的行业性数字，非本课程实验；笔记如实转述。

### 3.2 两条让 foundation model 持续学习的路线

- **Memory-based approaches**：In-context learning、external memory、RAG、harness（幻灯片标注 “Established but Limited”；另在参数更新一侧也列出 recurrent NNs、state-space models，文本排版略乱，保留不确定性）。
- **Parameter-update approaches**：model fine-tuning、adapters、model editing and merging、new algorithms?（幻灯片标注 “Open Research Questions”）。

**解释**：这构成“记忆 vs 改参数”的二分；guest 讲的主线是把后者做得“不遗忘”。

### 3.3 Catastrophic forgetting 与 “RL's Razor”

定义：神经网络在新任务上训练时丢失先前学到的信息。幻灯片给出实验设置示意：LLM 经 RL 或 SFT 训练后，在 test set 与 unrelated tasks 上评估（图中箭头/标签提取不完整）。核心引用：[Shenfeld et al., 2025, RL's Razor: Why Online Reinforcement Learning Forgets Less]。

幻灯片展示多组经验结果（图内曲线数值不可见，仅保留定性结论）：

- Qwen 3B-Instruct 在 Open-Reasoner-Zero 数据集上，SFT 标注来自 R1；
- OpenVLA 在 SimplerEnv 模拟器中，SFT 标注来自 RT-1；FashionMNIST 与 ParityMNIST 用于预训练，后在 ParityMNIST 上微调。

结论：**RL 比 SFT 遗忘更少**。为什么？

**Predictive variable**：一个 objective-agnostic 的度量，能解释遗忘。幻灯片给出关键结论：**遗忘几乎被“微调后策略与基座策略在新任务上的 KL 散度”完美预测**：𝔼_{x∼τ_new}[KL(π₀(·|x) ‖ π(·|x))]。**注意**：该公式在提取文本中有符号/上下标失真（π₀ 与 π 的先后、期望下标），笔记按语义表述为“基座策略与微调策略在新任务输入上的 KL”，不强行逐符号复刻。

### 3.4 为什么 on-policy 遗忘更少：目标函数对照

幻灯片并置两个目标：

- **Policy Gradient Objective**：−Σ_{x∼D, y∼π}[R(x,y) log π(x,y)]
- **Cross-Entropy Loss**：−Σ_{x∼D, y∼π*}[log π(x,y)]

并标注 **On-policy vs Off-policy**。**解释**：policy gradient 的样本 y 来自当前策略 π（on-policy），交叉熵的样本 y 来自固定标注 π*（off-policy）；幻灯片随后用 “Negative Examples” 与 “Negative Examples or On-Policy” 进一步对照，暗示 SFT 的监督信号包含大量负例式约束，从而把策略推离基座分布更远。

**On-policy learning 的直观（改编自 Gokul Swamy 的幻灯片，幻灯片明示）**：给定 teacher π_T，要把 student π 拟合到其分布；offline/off-policy 与 on-policy 的差异在于采样分布是否跟随 student；**没有 teacher 时用 reward function 替代**，即 on-policy RL。

### 3.5 从 on-policy RL 到更丰富的学习信号

Part II 的 takeaway（幻灯片原文）：

- 要**学而不忘，应做 on-policy learning**；
- 但 **on-policy RL 受限于 scalar rewards**；
- 而学习信号有很多种：**textual feedback、hints、detailed instructions、and more**。

**In-context learning**：大模型根据上下文改变行为的能力；不限于示例，对 feedback、scalar rewards、hints 等都有效；但效果是 **transient**（暂时的）。

**Self-Distillation 的机制（幻灯片用具体例子）**：

- Prompt x：“what are the roots of x²−9?”
- Context c：“Use the equation a²−b²=(a−b)(a+b)”
- 从 π(·|x) 采样得到**错误**解；从 π(·|x,c) 采样得到**正确**解。

于是构造 (prompt x, response y, context c) 三元组：先采样 y₁∼π(·|x)，再在带上下文条件下采样 y₂∼π(·|x,y₁,c) 作为“教师信号”，与不带上下文的 y₂∼π(·|x,y₁) 对照，让学生模仿“有 privileged context 时的自己”。**解释**：这正是“teacher = student + more feedback”的具体化；幻灯片用多步采样示意，具体损失形式未在文本中给出，不补公式。

### 3.6 实验性主张（定性，不引数值）

幻灯片展示 Qwen2.5 7B-Instruct 在 ToolAlpaca 数据集上的结果（图内数值不可见）：

- **Off-policy learning results in catastrophic forgetting**；
- **On-policy learning leads to better performance on both new and prior tasks**。

随后展示 Qwen2.5 7B-Instruct 在 ToolAlpaca、ScieKnowEval Chemistry、HuatuoGPT-o1 临床推理问题上的**顺序训练**：SFT 与 Self-Distillation 对照（曲线细节不可见）。引用 [Shenfeld et al., 2026, Self-Distillation Enables Continual Learning]。

**不确定性说明**：以上均为幻灯片定性结论；具体提升幅度、评测协议细节在提取文本中缺失，不应编造。

---

## 4. 方法比较（整合两讲）

### 4.1 一张“谁写、谁评、多密”的表

| 维度 | SFT | RL（PPO/GRPO） | On-policy Distillation | Self-Distillation |
|---|---|---|---|---|
| 轨迹由谁产生 | Teacher | Student | Student | Student |
| 反馈来源 | Gold solution | Environment / verifier / reward model | Teacher | 带 privileged info 的自己 |
| 反馈粒度 | 逐 token | 一个标量（或组内相对） | 逐 token | 逐 token（dense） |
| on/off-policy | Off-policy | On-policy | On-policy | On-policy |
| 遗忘风险 | 高（幻灯片：SFT 遗忘更多） | 低（RL's Razor） | 较低 | 幻灯片主张可持续学习 |
| 主要局限 | 不见自身错误 | 信号稀疏、reward hacking、高方差 | 受 teacher 上限约束 | 依赖 privileged info 的质量 |

（表中“遗忘风险”一行依据 guest 讲的定性结论；其余依据 lec6 原表与图示。）

### 4.2 PPO vs GRPO vs DPO

- **PPO**：actor + reward model + critic 三件套；KL + clip 稳定更新。
- **GRPO**：去掉 value model，用组内奖励均值作 baseline（需大 group）；可去掉 reward model，用 rule-based verifier。
- **DPO**：不是 RL；不推断 reward，直接提升偏好回复 likelihood；离线偏好优化。

### 4.3 Memory-based vs Parameter-update

- Memory-based（ICL、RAG、external memory、harness）：established but limited；ICL 效果 transient。
- Parameter-update（fine-tuning、adapters、editing/merging）：open research questions；核心挑战是 forgetting。

### 4.4 Test-time 谱系

- Test-time RL：自生成奖励（majority vote）→ 更新；
- Test-time Training：适配部署分布，data augmentation + task-specific adapters；
- OpenClaw-RL：语言批评 → 可执行 reward；
- TTT-Discover：测试时更新参数做开放式发现（与“冻结 LLM + 外部 verifier”的 optimizer 范式对照）。

---

## 5. 局限与风险（幻灯片明确或可直接推出）

1. **Reward hacking**：reward 最大化不等于目标对齐；简单 reward 更稳健（幻灯片原话），但“简单”本身需要设计判断。
2. **RL 信号稀疏**：幻灯片开篇即指出 RL 只有 small bits of reward，这正是 distillation 的动机。
3. **Policy gradient 高方差**：需要 baseline/relative improvement、actor-critic、PPO clipping 等手段。
4. **人类偏好 noisy、uncalibrated**：故用 pairwise relative preference，但 pairwise 也非完美（幻灯片未展开其偏差）。
5. **GRPO 的 baseline 依赖 group size**：幻灯片明确“requires large group size for accurate baseline estimation”。
6. **蒸馏受 teacher 限制**：teacher-student 蒸馏中 student 不见自身错误；on-policy 蒸馏缓解但仍有 teacher 上限；self-distillation 用 privileged info 替代外部 teacher，但其质量决定上限（解释性）。
7. **ICL 的 transient 效应**：上下文改变行为但不改参数，效果不持久（幻灯片原文 “Transient effect”）。
8. **Catastrophic forgetting**：SFT 顺序训练会遗忘；幻灯片用 KL 作为 predictive variable，但这是“解释性度量”，不等于因果机制（解释性提醒）。
9. **图表/公式提取缺失**：本周幻灯片大量关键信息在图中（Pong 训练曲线、RL's Razor 多组实验曲线、TTT-Discover 对照表列对齐、总表格子映射），文本提取不完整；本笔记对这些位置只给定性结论，不补数值。
10. **未核验口头讲述**：所有“为什么”的展开（如 PPO clip 的具体目标、self-distillation 的损失形式）可能出现在课堂讲解中，但不在本笔记可核验范围内。

---

## 6. 复习清单（自测用）

**基础**

- [ ] 写出 MDP 的七个组成，并说明 return、policy、goal 各是什么（注意幻灯片公式缺失，用文字定义）。
- [ ] 说出 imitation learning 的三个问题，并解释它们如何motivate RL。
- [ ] 用 Pong 例子复述 policy gradient：为什么 Win 最大化 Σ log p、Lose 最大化 −Σ log p，一般式是什么。
- [ ] 解释 ε-greedy 的探索退火逻辑。

**RL 算法**

- [ ] 定义 Q(s,a)、V(s)、A(s,a)，说明 actor 与 critic 各学什么。
- [ ] 说明 TRPO 与 PPO 的关系：KL 约束 → clipping 近似 → 小步更新 → 稳定训练。
- [ ] 默写 RLHF Step 0–4，并解释为什么用 pairwise relative preference。
- [ ] 列出 LLM 中 PPO 的三组件与五步算法。
- [ ] 列出 GRPO 相对 PPO 的三点关键差异（无 value model、组内统计 baseline、rule-based verifier）。
- [ ] 说明 DPO 为什么“不是 RL”，它与 SFT 的相似点。
- [ ] 举出 reward hacking 的两个幻灯片例子，并说明“简单 reward 更稳健”的含义。

**Test-time**

- [ ] 解释 test-time RL 的奖励从哪来（majority vote 等自生成信号）。
- [ ] 说明 test-time training 相对 ICL 的优势主张，以及 data augmentation / task-specific adapters 的作用。
- [ ] 描述 OpenClaw-RL 如何把自然语言批评变成 reward。
- [ ] 对比 “LLMs as optimizers（冻结）” 与 “TTT-Discover（测试时更新参数）” 的输入输出差异。

**Distillation**

- [ ] 复述 SFT / RL / Distillation 三行对照表（Policy? 与 Feedback?）。
- [ ] 解释 teacher-student 蒸馏的缺陷与 on-policy 蒸馏的修正。
- [ ] 说明 on-policy self-distillation 中 “teacher = student + privileged information” 的含义，并用 x²−9 例子说明。
- [ ] 说出 self-distillation 在 reasoning 与 continual learning 两个方向的应用（只给定性结论）。

**Continual Learning**

- [ ] 定义 catastrophic forgetting。
- [ ] 复述 “RL's Razor” 的结论与 predictive variable（新任务上基座策略与微调策略的 KL）。
- [ ] 从 policy gradient 与 cross-entropy 的目标对照解释 on-policy vs off-policy。
- [ ] 说明为什么“要学而不忘应做 on-policy learning”，以及 on-policy RL 的局限（scalar rewards）。
- [ ] 列出 memory-based 与 parameter-update 两条路线及各自代表方法。
- [ ] 用 Qwen2.5 7B / ToolAlpaca 的定性结论说明 off-policy 遗忘、on-policy 双任务更优（不引数值）。

**总表**

- [ ] 用 “feedback 类型 × 更新算法 × 更新范围” 三维坐标，把本周至少 8 个方法各归位一次，并标出哪些格子幻灯片未明确。

---

## 7. 术语表（保留英文）

MDP、return、policy、goal、imitation learning、distribution mismatch、policy gradient、Reinforce、ε-greedy、baseline、exponential moving average、actor-critic、Q(s,a)、V(s)、advantage A(s,a)、TRPO、PPO、KL divergence、clipping、RLHF、reward model、pairwise comparison、GRPO、value model、rule-based verifier、DPO、offline preference optimization、reward hacking、test-time RL、test-time training、in-context learning、majority vote、adapter、data augmentation、OpenClaw-RL、TTT-Discover、distillation、SFT、instruction tuning、on-policy distillation、self-distillation、privileged information、dense feedback、catastrophic forgetting、RL's Razor、predictive variable、on-policy / off-policy、continual learning、personalization、specialization、RAG、harness、model editing/merging。

---

## 8. 官方幻灯片 URL

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec6%20-%20training.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/model_guest.pdf
