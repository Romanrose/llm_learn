# 从策略梯度到自蒸馏：模型演化中的学习信号、遗忘与测试时适应

> 基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。本文只依据两份官方幻灯片的抽取文本写作，页面重复、页码与 OCR 失真不作为论证依据。幻灯片中图表、曲线与数值细节大量以图像形式存在，提取文本未能覆盖，本文对这些部分的不确定性予以明确保留；不虚构课堂对话、实验数值、作业要求或参考文献。

## 引言：为什么"如何学习"比"能做什么"更重要

MIT MAS.S62 Self-Evolving AI 课程 week-07 的主题是 Model evolution。两份官方幻灯片——Paul Liang 的 Lecture 6 "Test-time Training" 与 Idan Shenfeld 的 guest lecture "Continual Learning via Self-Distillation"——恰好构成一条完整的技术主线：前者从强化学习（Reinforcement Learning, RL）的基本原理讲到测试时训练（Test-Time Training, TTT），后者从灾难性遗忘（Catastrophic Forgetting）讲到自蒸馏（Self-Distillation）与持续学习（Continual Learning）。两者共享同一个核心问题：**模型如何利用自身产生的经验来更新自己？**

Guest lecture 开篇给出一个值得注意的立场转变：不要只用"AI 系统能做什么"来定义智能，而要看"它学得有多好"。幻灯片列出三条动机：个性化（personalization，系统适应用户偏好）、专业化（specialization，吸收领域文献与上下文以解决难题）、以及"下一个 scaling 前沿"——已部署的 AI 每天处理超过 300 万亿 token，约等于每天消化一个网络规模的语料。这三条动机的具体数字出自幻灯片，但背后的论证是概念性的：当部署规模远超训练规模时，持续学习能力成为瓶颈。

幻灯片把"基础模型如何继续学习"分成两大路线。记忆类方法（memory-based）：in-context learning、外部记忆、RAG、harness，以及循环神经网络与状态空间模型——幻灯片评价为"已确立但有局限"（established but limited）。参数更新类方法（parameter-update）：模型微调、adapters、模型编辑与合并，以及"新算法？"——幻灯片标注为"开放研究问题"（open research questions）。本文的主线就沿着这条"参数更新"路线展开：先理解 RL 作为学习信号的来源，再理解它为何比监督微调更不易遗忘，最后看蒸馏与自蒸馏如何把稠密反馈引入测试时与持续学习场景。

## 一、从提示到 RL：三条演化路径

Lecture 6 用一个简洁的 roadmap 框定了问题空间。输入是 prompt 与推理步骤序列，输出是答案。方法一：直接提示、不训练（如 chain-of-thought）。方法二：监督微调（Supervised Fine-Tuning, SFT），前提是拥有推理轨迹（reasoning traces）。方法三：强化学习，**不假设有推理轨迹**，但假设存在一个对推理过程与输出打分的奖励函数（reward function）。这条三分法是理解后续所有内容的地图：SFT 学习"抄答案"，RL 学习"根据后果调整行为"。

RL 的形式化基础是马尔可夫决策过程（MDP）：状态集 S、动作集 A、转移函数 P(s′|s,a)、奖励函数 r(s,a,s′)、起始状态 s0、折扣因子 γ、视界 H，以及由这些定义的回报（return）、策略（policy）与优化目标。幻灯片在此处只给出定义清单，未展开推导，本文同样不做超出幻灯片的推导。

RL 与监督学习的交集是模仿学习（imitation learning）：获取专家轨迹（如人类驾驶演示），然后做监督学习预测专家动作。幻灯片明确列出模仿学习的三个问题：分布不匹配（distribution mismatch）、难以从次优状态恢复、专家轨迹并非总是可得。这三点为后面"为什么需要 on-policy 学习"埋下伏笔。

## 二、策略梯度：从 Pong 到 REINFORCE

幻灯片用"Pong from Pixels"这个经典例子把策略梯度讲得非常具体。网络看到画面，输出"上"或"下"；得分时收到 +1，被得分时收到 −1。问题在于：我们**没有训练标签**。如果有标签，就是最大化 Σ log p(yᵢ|xᵢ) 的监督学习；但我们只有胜负。

于是做三次尝试（Run 1/2/3），分别得到 Win、Lose、Lose。对胜利的回合，最大化 Σ log p(yᵢ|xᵢ)；对失败的回合，最大化 −1·Σ log p(yᵢ|xᵢ)。推广到一般情形：最大化 Σ rᵢ log p(yᵢ|xᵢ)——奖励高的动作被提高概率，奖励低的被压低。这就是 REINFORCE 算法的直觉。幻灯片还提到 ε-greedy 探索策略：策略不好时完全随机探索，策略变好后逐渐减少探索。

但原始策略梯度" suffers from high variance"（方差很高）。幻灯片给出关键洞察：原始奖励的绝对值未必有意义，重要的是**奖励是否高于预期**——与基线（baseline）比较，使用相对改进，例如奖励的指数移动平均。这直接引出 actor-critic 方法。

## 三、Actor-Critic、PPO 与 RLHF 流水线

Actor-critic 的核心是两个价值函数：Q(s,a) 表示从状态 s 采取动作 a 预期的总奖励，V(s) 表示从状态 s 预期的总奖励。优势函数（advantage function）A(s,a) = Q(s,a) − V(s)：若某动作优于该状态的平均预期，则 A 大，我们"高兴"；否则"不高兴"。幻灯片引用 Minh et al., ICML 2016 的异步深度 RL 工作，展示 actor（决定动作）与 critic（评估动作好坏）的双模型结构。

PPO（Proximal Policy Optimization）解决的是训练稳定性：信任域策略优化（TRPO）限制新旧策略之间的 KL 散度，PPO 进一步用裁剪（clipping）近似 KL 约束，使每次更新幅度小、训练稳定（引用 Schulman et al., ICML 2015 与 2017）。

把这些组件拼起来就是 RLHF（Reinforcement Learning from Human Feedback）的四步流水线：Step 0 预训练 + SFT；Step 1 对每个 prompt 让 LLM 作为策略采样多个回复；Step 2 人类按质量排序；Step 3 训练奖励模型预测人类偏好；Step 4 用 PPO 或 GRPO 微调模型以最大化奖励模型分数（引用 Christiano et al., NeurIPS 2017）。幻灯片解释了为什么需要奖励模型：不可能让人类为一切写金标准答案。而人类偏好"有噪声、未校准"，因此采用成对比较（pairwise comparisons）做相对偏好调优——幻灯片用"剑桥是一座位於 Cambridgeshire 的历史名城……"对比"剑桥是英格兰北部一个毫无历史意义的小村庄……"的示例说明成对比较的形式。

PPO 在 RLHF 中的三组件：actor（策略，即预训练 + SFT 的 LLM）、reward model（冻结的、预测人类偏好标量的模型）、critic（可学习的价值函数，输入部分回复预测 V(s)）。算法五步：生成回复、奖励模型打分、计算优势 A(s,a) = Q(s,a) − V(s)（价值模型估计"某个词相对于平均动作好多少"）、按 PPO 目标（KL + clip）更新策略、更新价值函数。

GRPO（DeepSeek R1，引用 Guo et al., arXiv 2025）的关键差异：放弃价值模型，改用一组回复的奖励均值作为基线（需要较大的组规模才能准确估计基线）；用组内回复计算优势与梯度；放弃奖励模型，改用规则式验证器（rule-based verifiers：二元检查、测试用例、长度、格式）。这三条差异在幻灯片 26–27 中分两页呈现，本文合并叙述但保留其层次。

DPO（Direct Preference Optimization，引用 Rafailov et al., NeurIPS 2023）则被幻灯片明确"去魅"：DPO 实际上不做强化学习。它不从偏好数据推断奖励，而是直接提高偏好回复的似然、降低其他回复的似然；更接近监督学习，也称"离线偏好优化"（offline preference optimization）。

## 四、奖励 hacking 与测试时 RL

奖励设计有一个根本风险：模型最大化奖励，而奖励未必对齐目标。幻灯片给出两个例子：一个 RL agent 通过反复撞倒孤立潟湖中重生的目标，比人类得分高 20%；一个 LLM 黑掉棋类引擎让自己赢。结论是：设计奖励时要小心，**更简单的奖励往往更稳健**（simpler rewards tends to be more robust）。这为 GRPO 用规则验证器提供了注脚。

Test-Time RL（引用 Zuo et al., NeurIPS 2025）把学习信号搬到测试时：从自生成、可变化的奖励信号中学习，例如对多个采样回复做多数投票（majority vote）。Test-Time Training（引用 Akyurek et al., ICML 2025）的目标是适应部署分布，幻灯片给出的判断是"Test-time RL > In-context learning"，并指出数据增强与任务特定 adapter 都有帮助。OpenClaw-RL（引用 Wang et al., ICML 2025）则设计奖励模型，把自然语言批评（natural language critiques）翻译成可执行的奖励信号，从而"只需对话就能训练任意 agent"。

幻灯片 33–35 把这一思路推向"发现"（discovery）：LLM 可以演化自己的上下文（即解空间）来解决开放式问题（NP-hard 优化、编程、科学发现）。对比"LLMs as optimizers"与"TTT-Discover"：前者在测试时冻结，只有 archive 与外部验证器循环，更新参数为"无"；后者在测试时训练，解决方案 LLM 接收"任务 + 父解 + 分数"，输出完整解，且**训练的就是同一个 LLM**。幻灯片用表格明确对比了"更新参数 / 可训练模型输入 / 可训练模型输出 / 完整解来源"四个维度。引用为 Yuksekgonul et al., 2026 与 Jiang et al., 2026。需要说明：这两处引用年份为 2026，属于幻灯片原文，本文不额外核验；相关图表（如 archive 结构、分数曲线）的视觉细节在提取文本中缺失，本文不猜测其数值。

## 五、蒸馏：从稀疏奖励到稠密反馈

幻灯片 36 点出 RL 的关键问题：训练信号只有很少的奖励比特。如何从稠密反馈中学习？答案是蒸馏（Distillation）。

传统 teacher-student 蒸馏（即 SFT、指令微调）：teacher 写出解 w1* w2* w3* w4*，student 逐 token 抄写。问题是 student 只学会模仿答案，**从来看不到自己的错误，也学不到 teacher 如何纠正常见错误**。

On-policy 蒸馏（引用 Agarwal et al., ICLR 2024）改变顺序：student 先写自己的尝试，teacher 对尝试打分并纠正常见错误，student 再抄 teacher 的分数。幻灯片用三步图示：student 写尝试 → teacher 打分 → student 抄分数。

幻灯片 39 的对比表是理解全篇的关键，本文完整保留其结构：

| | SFT | RL | Distillation |
|---|---|---|---|
| Policy？ | Teacher 写解 | Student 写尝试 | Student 写尝试 |
| Feedback？ | Student 抄解，逐 token | 环境给尝试打分，一个标量 | Teacher 给尝试打分，逐 token |

也就是说：SFT 是 off-policy 的逐 token 模仿；RL 是 on-policy 但反馈稀疏（一个标量）；蒸馏是 on-policy 且反馈稠密（逐 token）。这三者的取舍贯穿两份幻灯片。

On-policy self-distillation（引用 Zhao et al., ICML 2026）进一步去掉外部 teacher：若要自我改进，就不应被 teacher 模型限制；在自蒸馏中，teacher 就是"student + 更多反馈"（privileged information）。图示为：student 写尝试 → student+更多反馈 打分 → student 抄分数，并标注"dense feedback"。幻灯片 41–43 展示自蒸馏用于推理与持续学习（引用 Hubotter et al., ICML 2026；Shenfeld et al., ICML 2026），但具体图表数据在提取文本中缺失。

幻灯片 45 用二维框架收束：横轴是反馈类型（稠密反馈、奖励或验证器、自生成目标、人类标签），纵轴是更新算法（全权重 SFT/RL/Distillation、部分权重 adapters），第三维是"更新什么"。这实际上是把 Lecture 6 的所有方法放进一个设计空间。

## 六、灾难性遗忘与"RL 的剃刀"

Guest lecture 进入 Part I：灾难性遗忘——神经网络在新任务上训练时丢失先前学到的信息。幻灯片给出一个实验骨架：LLM 经 RL 或 SFT 训练后在测试集评估，再在与任务无关的任务上评估遗忘程度（引用 Shenfeld et al., 2025, "RL's Razor: Why Online Reinforcement Learning Forgets Less"）。实验涉及 Qwen 3B-Instruct 在 Open-Reasoner-Zero 数据集上训练（SFT 标注来自 R1）、OpenVLA 在 SimplerEnv 模拟器中训练（SFT 标注来自 RT-1）、FashionMNIST 与 ParityMNIST 的预训练与微调。幻灯片结论是：RL 遗忘更少。但**具体的遗忘曲线与数值在提取文本中不可见**，本文只陈述幻灯片给出的定性结论，不引用任何数值。

为什么 RL 遗忘更少？幻灯片提出"预测变量"（predictive variable）：一个与目标无关的度量，能解释遗忘。结论是：遗忘几乎完美地被"微调后策略与基础策略在新任务上的 KL 散度"所预测，即 E_{x∼τ_new}[KL(π₀(·|x) ‖ π(·|x))]。换言之，策略在新任务上偏离基础策略越远，遗忘越严重。

接下来的推导是整场 guest lecture 最技术性的部分。比较策略梯度目标与交叉熵损失：

- 策略梯度：−Σ_{x∼D, y∼π} [R(x,y) log π(x,y)]
- 交叉熵：−Σ_{x∼D, y∼π*} [log π(x,y)]

差别在于：策略梯度在**当前策略自己的样本**上加权奖励，交叉熵在**标注答案**上做模仿。幻灯片由此引出 on-policy 与 off-policy 的区分，并借 Gokul Swamy 的图示说明：给定 teacher π_T，要拟合 student π 到其分布，off-policy 是用 teacher 的样本，on-policy 是用 student 自己的样本；没有 teacher 时用奖励函数替代，即 on-policy RL。结论是：交叉熵损失缺少"负样本"或 on-policy 成分，这正是 SFT 更容易覆盖基础策略、从而遗忘更多的原因。幻灯片反复出现同一张对比图（策略梯度 vs 交叉熵），本文视为强调而非重复论证。

## 七、自蒸馏实现持续学习

Part II 的主线：要学而不忘，应做 on-policy 学习；但 on-policy RL 只限于标量奖励，而现实中有文本反馈、提示（hints）、详细指令等多种学习信号。

In-context learning 能让大模型基于上下文改变行为，对反馈、标量奖励、提示都有效，但幻灯片指出它是" transient 效应"（瞬时效应）——上下文移除后行为回退。

Self-distillation 的例子很直观：prompt x 是"x²−9 的根是什么？"，上下文 c 是"使用 a²−b²=(a−b)(a+b)"。从 π(·|x) 采样得到错误解；从 π(·|x,c) 采样得到正确解。自蒸馏的做法是：让同一模型在有上下文与无上下文两种条件下采样（y₂ ∼ π(·|x,y₁) 与 y₂ ∼ π(·|x,y₁,c)），把有上下文时的分布作为目标来训练无上下文时的分布——把"带提示才做对"的能力内化。

持续学习实验（引用 Shenfeld et al., 2026, "Self-Distillation Enables Continual Learning"）：Qwen2.5 7B-Instruct 在 ToolAlpaca 数据集上学习专家演示。幻灯片对比两种结果：off-policy 学习导致灾难性遗忘；on-policy 学习在新任务与先前任务上表现都更好。进一步在 ToolAlpaca、ScieKnowEval Chemistry、HuatuoGPT-o1 临床推理问题三个数据集上顺序训练，对比 SFT 与 Self-Distillation。图示显示自蒸馏在顺序训练下保持更好——但同样，曲线数值在提取文本中缺失，本文只保留定性结论与实验设置。

## 结语：一条从"打分"到"内化"的演化链

把两份幻灯片串起来，可以看到 Model evolution 的一条清晰演化链。第一层是**信号来源**：从 SFT 的专家轨迹，到 RL 的标量奖励，到 RLHF 的人类偏好，到 GRPO 的规则验证器与组内统计，到 Test-Time RL 的多数投票与自然语言批评——反馈越来越便宜、越来越自生成。第二层是**反馈密度**：从 RL 的稀疏标量，到蒸馏的逐 token 稠密反馈，到自蒸馏用"带特权信息的自己"当 teacher。第三层是**更新范围**：从全权重 SFT/RL/蒸馏，到 adapters 等部分权重更新（幻灯片 45 的框架）。第四层是**遗忘控制**：RL 因 on-policy 而偏离基础策略更小、遗忘更少；自蒸馏把 on-policy 与稠密反馈结合，用于持续学习。

需要诚实指出本文的边界：所有具体实验数值、曲线形状、图表结构均以图像形式存在于幻灯片中，抽取文本只保留了定性结论与实验设置；两处 2026 年引用（Yuksekgonul et al.；Jiang et al.；Hubotter et al.；Shenfeld et al.）按幻灯片原文保留，未做外部核验；幻灯片中"20% higher scores"等数字仅出现在奖励 hacking 示例中，本文如实转述但不将其推广为课程实验结论。课程作业与项目要求（Homework 2、10 月 28 日中期报告）属于公告信息，本文仅作背景提及，不构成对读者的要求。

如果说这两讲有一个共同的技术判断，那就是：**学习的质量取决于信号与策略分布的关系**。Off-policy 的模仿学得快但忘得也快；on-policy 的学习信号稀疏却更贴近模型自身分布；蒸馏与自蒸馏则试图在 on-policy 的前提下恢复稠密反馈。Model evolution 的下一个前沿，或许正如 guest lecture 所说，不是"模型能做什么"，而是"模型能多好地、多不遗忘地继续学习"。

## 官方幻灯片来源

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec6%20-%20training.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/model_guest.pdf
