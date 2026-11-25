# Stanford CME 295 · Transformers & Large Language Models
## Lecture 3：LLM Training 课程笔记

> 说明：本笔记依据 Lecture 3 逐字稿整理。凡涉及数值（如 20 token/参数、30 万亿 token、4K/128K 上下文、知识截止日期等）均为课程中提及的示例性说法，用于说明量级与原理，不作为精确基准引用。涉及教师未展开的数学细节（如 GRPO、DPO 的完整推导）本笔记只保留直觉层面，并标注"下讲展开"。

---

## 一、学习目标

学完本讲，应能：

1. 说清 LLM 训练流水线的阶段划分：**pre-training → mid-training → long-context training → SFT → preference tuning（RLHF / DPO）→ reasoning RL**，以及每个阶段"改变的是什么、目标函数是什么、数据从哪来"。
2. 从第一性原理推导 next-token prediction 的 cross-entropy loss，并解释为什么用 log、为什么取负、为什么按 token 数平均。
3. 解释 **bits per byte（BPB）** 为什么存在：cross-entropy 的绝对值依赖 tokenizer，BPB 提供跨 tokenizer 可比的度量。
4. 说明 **teacher forcing** 的机制，以及由此产生的 training/inference mismatch。
5. 解释 **LoRA** 的动机、低秩分解形式，以及它在存储与计算上的双重优势。
6. 用 **Bradley-Terry** 模型解释 reward model 的训练目标，理解 pairwise loss 与 cross-entropy 的同构关系。
7. 区分 **on-policy / off-policy** 与 **dense / sparse reward** 两个维度，并用它们定位 RLHF、DPO、GRPO、on-policy distillation 各自的位置。
8. 理解 reasoning model 的奖励为何"可验证"，以及 chain-of-thought 为何既是能力也是需要保护的信息。

---

## 二、课程主线

本讲的主线是一条**训练流水线**，而非孤立技术点。教师反复用一个具体 prompt 贯穿全讲，展示同一问题在不同训练阶段会得到什么回答：

> "Can I put my teddy bear in the washing machine?"

- **仅预训练后**：模型不会回答，而是"自动补全"——罗列泰迪熊的材质、配件等文本中常见的内容。因为它只学过 next-token prediction。
- **SFT 后**：给出直接答案（"No, it might get damaged. Try hand washing."），但语气未必符合期望。
- **偏好调优后**：给出更友好、更符合人类偏好的措辞。

这条主线的教学意图是：**模型的"知识"和"行为"是分开获得的**。预训练/中期训练注入知识与能力，SFT 与偏好调优改变行为。理解这一点，才能理解后面每个阶段的目标函数为何不同。

课程后半段由另一位讲者以 **GLM5** 这一开放权重模型为锚点，把上述每个阶段"在真实技术报告里对应什么数据、什么 packing 策略、什么 RL 子阶段"逐一对映，并补充了 data curation、model collapse、context rot、cross-stage distillation 等工程现实。

---

## 三、核心概念

### 3.1 Pre-training：学习语言本身

**目标**：在大规模语料（网页、代码、数学、科学、多语言文本）上做 next-token prediction，让模型学习语言的模式。规模量级为**数万亿 token**（课程举例：GLM5 约 30 万亿 token）。

**迁移学习的视角**：教师用"15 年前会为每个用例单独训模型"作对比，说明 pre-training 的本质是"一次性大规模训练学到关于语言的知识，再从那里 specialize"。这是 transfer learning 的思路。

**并行化与 teacher forcing**：预训练不需要按顺序逐 token 喂入。由于 **masked self-attention** 保证位置 $t$ 只能看到 $\le t$ 的 token，整个序列可以一次前向，同时为所有位置预测下一个 token——本质上是"一次巨大的矩阵乘法"。训练时无论模型预测什么，下一步的输入永远是**数据中真实的 token**，这就是 teacher forcing。

> 课堂问答要点（课程原意）：学生指出 teacher forcing 导致训练时模型没见过自己的输出，因此 **training 与 inference 存在 mismatch**。教师确认这是好问题，并说明后续阶段（偏好调优、RL）正是缓解这一问题的途径之一。

**预训练阶段的数据细节（GLM5 案例）**：
- 网页数据常用 Common Crawl，但如今大量被 AI 生成内容污染，需要启发式规则过滤，课程提到"通常最后只保留约 1% 的输入"。
- 代码数据（GitHub 等）是推理能力的底座；教师强调当今 agent 系统本质上多为不同形式的编程问题。
- 预训练通常在**较短上下文**下进行（课程举例：约 4K token 量级），出于效率考虑。
- 数据被切块后**拼接**以填满 context length，因此 batch 不一定以 BOS token 开头，文档会被截断拼接——因为此阶段目标不是生成格式良好的句子，而是学习语言结构。

**数据重复的权衡**：课程引用研究指出，在 data-constrained 情况下，重复训练同一批 token **最多约四次**仍能带来更好性能；超过则有 trade-off。选择"更多 unique token（可能低质）"还是"重复高质量 token"是实际问题。

**Model collapse（模型坍缩）**：课程解释为——真实数据分布有很长的长尾，有限采样无法覆盖全部细节，因此模型输出分布天生不同于真实分布；再叠加模型只是近似器、以及后期阶段注入的偏好（某些措辞被大幅提高频率），会导致分布进一步偏移。这是 data curation 技术重要的原因。

### 3.2 Cross-entropy loss：从第一性原理推导

课程明确要求"不要背公式，要从第一性原理想"。推导链条：

1. 目标：找参数 $\theta$，最大化模型看到训练数据的概率。
2. 序列概率分解为链式乘积：
$$p_\theta(x_1,\dots,x_n)=\prod_{t=1}^{n} p_\theta(x_t \mid x_{<t})$$
3. 乘积中每项在 $(0,1)$，连乘趋向 0，**数值不稳定** → 取对数，变成求和。
4. 机器学习习惯**最小化** → 取负。
5. 不希望损失随序列长度缩放 → **除以 token 数**。

得到：
$$\mathcal{L}(\theta)=-\frac{1}{T}\sum_{t=1}^{T}\log p_\theta(x_t\mid x_{<t})$$

**关键理解**：$p_\theta$ 是模型最后一层输出的预测概率，$x_t$ 是目标 token，$x_{<t}$ 是过去的 token。

### 3.3 Bits per byte（BPB）

Cross-entropy 的**绝对值是 tokenizer 的函数**：不同分词方式下，同一模型同一数据的 loss 数值不可直接比较。BPB 的做法是把 loss 乘以"token 数 / 字节数"，再乘以 $1/\log 2$，使其可解释为"每字节多少比特"，从而**与 tokenizer 无关**。其中"字节数"指输入文本按字节编码后的长度。

> 课堂问答（课程原意）：masked self-attention 是**decoder-only** 设置下预测下一个 token 的必要条件，用以模拟 inference 时只能依赖已解码内容的情形；encoder-only 无法这样做，相关替代方案在第八讲讨论。

### 3.4 Mid-training 与 Long-context training

**Mid-training** 是近年出现的第二阶段，目的是**注入与用例更对齐的任务知识**：若关心推理，就让模型接触更多代码与数学数据；仍用 next-token prediction，但数据质量更高、更聚焦。

**Long-context training** 的必要性来自 RoPE 的性质：RoPE 无可学习参数，理论上可"开箱即用"，但模型在短序列上训练后从未见过长距离的旋转，直接用于长上下文会"困惑"。

**YaRN 等 RoPE 扩展方法的直觉**：对 RoPE 频率做**插值**，使长位置差落在短上下文训练时**见过的频率范围内**，从而让模型"熟悉"这些位置。

> 课堂问答（课程原意）：上下文长度是**预先规划**的（GLM5 案例：短上下文约 4K，长上下文训练拉到 128K 甚至 200K），频率按计划插值，调整后的频率用于后续推理。YaRN 不改变 RoPE 的基本设置，只改频率。

**长上下文的两个难点**：
1. 自注意力复杂度为 $n^2$，从 4K 扩到数十万，计算量大幅上升。
2. **数据难构造**：需要"很久以前的信息影响很远的未来预测"的样本，这类依赖关系不会自然大量出现，需要专门构造。

**Knowledge cutoff**：训练数据有截止日期，模型对该日期之后的事"完全不知道"。这是后续需要 retrieval 等技术的原因（课程未在本讲展开）。

### 3.5 SFT：监督微调

**目标**：改变**行为**，使模型与期望对齐（如助手式回答）。目标函数仍是 next-token prediction / cross-entropy，但**输入分布变了**：输入是 instruction（prompt）加上已解码的回答，只对**回答部分**计算 loss。

$$\mathcal{L}=-\sum_t \log p_\theta(y_t \mid x, y_{<t})$$

其中 $x$ 是 prompt，$y$ 是目标回答。

> 课堂问答（课程原意）：
> - **不惩罚预测输入**：prompt 是给定的，预测它不是目标，计算 prompt 的 loss 与意图不一致。
> - **SFT 与 mid-training 的区别**：mid-training 是更高质量、更对齐的**语料**上继续 next-token prediction；SFT 是专门针对"给定输入、模仿某种输出行为"的**行为调整**。
> - **数据规模**：远小于预训练。特定用例可能数百到数千条；通用助手行为可能数百万条，但仍比预训练少数个量级。原因之一是普通研究者没有调优数十亿参数的硬件；之二是模型已具备知识，不需要那么多自由度。

**SFT 的挑战**：
- 数据质量要求极高——模型会**完全照做**你给的数据。
- prompt 分布敏感；某类数据过多会让模型偏向特定回答方式。
- 模型行为不当（misbehavior）本身是信号：可能说明 SFT 数据里混入了非预期内容，应借机审查数据。

### 3.6 LoRA：低秩适应

**动机**：模型已有大量知识，SFT 只是"引导行为"，是否真的需要更新全部权重？

**形式**：把可学习权重矩阵分解为预训练权重 $W_0$ 加上低秩可调项：
$$W = W_0 + BA$$
其中 $B,A$ 是低秩矩阵，大幅减少可训练参数量。

**双重优势**：
1. **计算/显存高效**，且根据数据与任务规模，性能可与全参微调大致相当。
2. **存储高效**：多个用例共享 $W_0$，只需各自存储 $\Delta = BA$。对比之下，全参微调要为每个用例存一份完整权重。

**实践建议的演变**：LoRA 作者最初建议作用于 attention 层内的矩阵；后续实验表明也应作用于 **FFN 内的矩阵**——那里参数最多、计算最集中，能带来明显性能提升。

> 课堂问答（课程原意）：一般通用助手场景不会为每个问题准备不同权重，通常训练一个大模型；LoRA 主要适用于非常具体的定制用例。

### 3.7 偏好数据与 Reward Modeling

**动机**：SFT 只教会模型"该做什么"，没教"不该做什么"。且 SFT 数据是外部强加的，不是模型自己生成的。要解决 training/inference mismatch，需要引入偏好信号。

**偏好数据的三种形式**：
- 逐点绝对评分（pointwise）——人类做绝对判断较难；
- **成对比较（pairwise）**——最常用，判断"哪个更好"比"绝对多好"容易；
- 列表排序（listwise）。

**Bradley-Terry 模型**：$y_i$ 优于 $y_j$ 的概率为
$$P(y_i \succ y_j)=\sigma(r_i-r_j),\quad \sigma(x)=\frac{1}{1+e^{-x}}$$

**Reward model 的训练**：给定 prompt $x$、winning answer $y_W$、losing answer $y_L$，用 pairwise loss：
$$\mathcal{L}=-\mathbb{E}_{(x,y_W,y_L)}\left[\log\sigma\left(r_\theta(x,y_W)-r_\theta(x,y_L)\right)\right]$$

**与 cross-entropy 的同构**：要建模的事件是"$y_W$ 优于 $y_L$"；Bradley-Terry 给出该事件的概率；取 log（单调、避免下溢）；取负（转为最小化）。这与 cross-entropy 的推导逻辑完全平行。

**Reward model 的两种架构**（课程原意，两者皆可）：
1. 复用 LLM backbone，取最后一个输入 token 的表示，投影到标量；
2. 使用 **encoder-only** 模型，做自注意力后直接投影。

### 3.8 RLHF：两阶段结构

- **阶段一**：用人类偏好数据训练 reward model（人类偏好在此被建模）。
- **阶段二**：**冻结 reward model**，只更新 LLM 权重，用 RL 最大化奖励。

**目标函数的两部分**：
1. 最大化 reward；
2. **惩罚相对 reference model 的过大偏离**。

第二项的动机（课程原意）：模型已经足够好；reward model 并不完美（有时好答案被判低分）；偏离太远会破坏已有能力。reference model 通常是 **SFT 后的模型**。

**Reward hacking**：模型朝 reward model 喜欢的方向走，而这未必是真正想要的行为——因为 reward model 只是人类偏好的近似。

> 课堂问答（课程原意）：RL 阶段**只更新 LLM 权重，reward model 固定**；具体更新算法下讲展开。观测数量通常比 reward model 训练数据高数个量级。

### 3.9 DPO：把偏好优化写成监督问题

**动机**：RLHF 复杂——需要 reward model、需要调大量超参。DPO 试图用监督方式表达同一问题。

**核心思路**（课程只给直觉）：假设 $r$ 可写成"被调模型相对 reference model 的对数概率比"的函数，则推导出的 loss 与 reward model 的 pairwise loss 形式相似，其效果是：
- 相对 reference model **提高**生成 winning answer 的概率；
- 相对 reference model **降低**生成 losing answer 的概率。

**与 RLHF 的关键差异**（课程原意）：DPO 的 loss 基于**固定的输出**，不是模型当前实际生成的输出，因此是 **off-policy**；RLHF 利用 LLM 的实际输出，是 **on-policy**。这引出后面"稀疏/稠密 × on/off-policy"的分析框架。

> 记号说明：课程提到 RL 语境下把 LM 称为 **policy**，用 $\pi$ 表示其预测的概率分布。

### 3.10 Reasoning：可验证奖励与 GRPO

**推理的定义（课程给出）**：解决问题的能力。与非推理型知识问答的区别：知识题"知道就知道，不知道就不知道"；推理题（如"熊生于 2020 年，现在多大"）需要中间步骤。

**Chain-of-thought 的问题**：few-shot 提示可以让模型输出推理链，但**我们不想每次都告诉模型这么做**，希望模型自己学会。

**时间线（课程原意）**：2024 年 9 月 OpenAI 首次公开说明该技术在数学与编码任务上带来提升；此后几乎所有前沿实验室采用；2025 年 1 月 DeepSeek R1 是首个完整公开"如何训练推理模型"的开放权重模型。

**可验证奖励（verifiable reward）**：数学题可与标准答案比对；代码题可跑测试用例。因此可以对每个模型输出判定对错，奖励可设计为"答案正确 + 包含推理链"。

**GRPO 的高层直觉**（下讲展开数学）：
1. 给定 prompt，让 policy 生成**多个**响应；
2. 判定每个响应是否正确；
3. 计算**优势（advantage）**——某答案相对同组其他答案好多少；
4. 好的多鼓励、差的少鼓励，同时仍施加相对 reference model 的偏离惩罚。

**与 RLHF 的关键差异**：不需要 reward model，直接使用真实答案。

**训练效果**（课程展示的定性趋势）：随 RL 步数增加，推理任务性能上升；同时推理链的**经验长度**也上升。

**核心局限**：奖励是**序列级**的（整个输出对或错），是**稀疏信号**，没有 token 级判断。

### 3.11 On-policy Distillation：结合两者优点

课程在此处建立一个二维分析框架，值得单独记住：

| 方法 | on/off-policy | 奖励信号 |
|---|---|---|
| SFT | off-policy（固定数据） | dense（token 级） |
| RLHF / GRPO | on-policy（用模型自己的输出） | sparse（序列级） |
| **On-policy distillation** | **on-policy** | **dense** |

**On-policy distillation 的做法**：学生模型生成回答；**教师模型对每个 token 给出预测**；惩罚学生与教师在 token 级的偏差。

- **on-policy**：用的是学生自己的生成；
- **dense**：token 级信号。

**变体：on-policy self-distillation**：没有独立教师时，用同一个模型作教师，但**把答案告诉它**，让它知道如何引导回答。课程提到该技术已被多数前沿开放权重模型采用。

**多教师设置**：例如一个擅长数学、一个擅长工程的教师，对学生做稠密监督。

### 3.12 GLM5 案例：把流水线落到工程细节

**Pre-training**：
- 数据：Common Crawl（过滤后保留约 1%）、Wikipedia 等权威来源、GitHub 代码、数学/科学论文；
- 分两阶段：先粗粒度学语言结构（以网页为主），再加入代码与推理混合（网页比例降低）；
- 上下文约 4K 量级；
- 数据被切块拼接以填满 context length，batch 不一定以 BOS 开头；
- epoch 通常为 $O(1)$，被分类器判为更高质量的数据可能多跑几轮。

**Mid-training**：
- 目标：增加上下文长度，数据混合以**长篇幅**内容为主；
- 代码场景关注带 issue 的 PR 与 code diff；
- 提到 **context rot**：长上下文中模型难以记住早先的事实；合成数据可在中间注入事实、之后再引用，以训练这种能力；
- 使用 **best fit packing**：合理打包文档以避免截断，剩余空间用 padding 填充；仍是 next-token prediction。

**SFT**：
- token 量级大幅下降；强调通用有用性；
- 大量注入推理与代码数据；
- 提到"插入通向工具调用的推理"这一策略；
- **think token**：模型在其中"打草稿"，用户看不到，但会计入计费。

**RL**（GLM5 分为三部分）：
1. **Reasoning RL**：数学竞赛类数据，有可验证答案；
2. **Agentic RL**：把 LLM 放进 harness，用运行测试等方式验证（如 bug 修复：把失败测试修成通过）；
3. **General RL**：更开放，维度包括基础正确性、情商（专家标注者对"有用答案"的看法）、任务特定质量（如指令遵循）。

**On-policy cross-stage distillation**：RL 最后阶段针对**之前检查点的教师模型**（SFT 之后的检查点、第一个 RL 阶段之后的检查点）做蒸馏，以确保前面阶段学到的能力没有丢失。

**对技术报告的批判性阅读**：课程提醒，开放权重模型的技术报告不总是写明数据配方的全部细节；业界存在互相指控"蒸馏他人数据"的现象，这类内容不会写进报告。

**关于 harness 工程的趋势**：课程提到某极简 coding agent 的案例，说明模型自身推理能力增强后，harness 中需要的上下文工程可以减少。

---

## 四、关键公式与原则

**1. Next-token prediction 的 cross-entropy**
$$\mathcal{L}(\theta)=-\frac{1}{T}\sum_{t=1}^{T}\log p_\theta(x_t\mid x_{<t})$$
推导要点：最大化数据似然 → 链式分解 → 取 log 保数值稳定 → 取负转最小化 → 除以 $T$ 去除长度依赖。

**2. Bits per byte**
$$\text{BPB}=\mathcal{L}\cdot\frac{\#\text{tokens}}{\#\text{bytes}}\cdot\frac{1}{\log 2}$$
作用：消除 tokenizer 依赖，使 loss 跨模型可比。

**3. Bradley-Terry**
$$P(y_i\succ y_j)=\sigma(r_i-r_j)$$

**4. Reward model 的 pairwise loss**
$$\mathcal{L}=-\mathbb{E}\left[\log\sigma\left(r_\theta(x,y_W)-r_\theta(x,y_L)\right)\right]$$
与 cross-entropy 同构：建模事件 → 取概率 → log → 取负。

**5. LoRA**
$$W=W_0+BA,\quad B,A \text{ 低秩}$$

**6. RL 目标的两部分原则**：最大化 reward + 惩罚相对 reference model 的偏离。reference 通常为 SFT 模型。

**7. 贯穿全讲的原则**：
- **知识与行为分离**：预训练/中期训练给知识，SFT/偏好调优改行为。
- **训练与推理的分布匹配**：teacher forcing 造成 mismatch；on-policy 方法是对这一问题的系统性回应。
- **奖励信号的两个维度**：dense/sparse × on/off-policy，决定方法的性质与局限。
- **不要一次改变太多**：LoRA、RL 的 KL 惩罚、cross-stage distillation，本质都是"在已有能力附近做有约束的调整"。

---

## 五、课程作业关联

本讲内容与作业的对应关系（依据课程明确提到的方向整理，不虚构具体题目）：

1. **实现 next-token prediction 的 loss**：作业很可能要求从 logits 与 labels 计算 cross-entropy，并处理"只对回答部分计 loss"的 mask——这正是 SFT 与预训练目标的差别所在。理解"不惩罚预测输入"的原则可直接用于检查 mask 是否正确。
2. **LoRA 的实现与参数量对比**：低秩分解 $W_0+BA$、多任务共享 $W_0$ 只存 $\Delta$，是可动手验证的工程点。
3. **Reward model / pairwise loss**：把 Bradley-Terry 与 cross-entropy 的推导对应起来，有助于写出正确的 loss 与标签构造。
4. **偏好数据的构造与评估**：成对数据的组织、reference model 的选择（SFT 检查点）都会影响实现细节。
5. **推理任务的评测**：可验证奖励的构造（答案比对、测试用例）是 reasoning RL 的前置工程。
6. **长上下文相关**：RoPE 频率插值的直觉有助于理解位置编码实现与上下文扩展实验。

> 注：以上为基于本讲内容的关联方向梳理；具体作业要求以课程官方发布为准。

---

## 六、常见误区

1. **"预训练完模型就能回答问题。"** 错。预训练模型只会自动补全。教师用泰迪熊的例子明确演示了这一点。
2. **"cross-entropy 公式要背。"** 课程明确反对。应从"最大化数据似然 + 数值稳定 + 转最小化 + 归一化"四步推出。
3. **"loss 数值可以直接跨模型比较。"** 错。绝对值依赖 tokenizer，需用 BPB。
4. **"SFT 时应该对 prompt 也算 loss。"** 错。prompt 是给定的，预测它不是目标，会损害性能。
5. **"SFT 和 mid-training 是一回事。"** 不是。mid-training 是更高质量、更对齐的语料上继续 next-token prediction；SFT 是针对"给定输入模仿特定输出行为"的行为调整。
6. **"SFT 数据越多越好，应该和预训练同量级。"** 错。SFT 数据量少数个量级；模型已有知识，不需要那么多自由度，且普通研究者没有相应硬件。
7. **"LoRA 只该用在 attention 上。"** 这是早期建议；后续实验表明 FFN 内矩阵也应加上，那里参数与计算最集中。
8. **"RLHF 阶段 reward model 也会一起更新。"** 错。reward model 冻结，只更新 LLM 权重。
9. **"reward 高就一定好。"** 错。reward hacking：模型会朝 reward model 的偏好走，而 reward model 只是人类偏好的近似。
10. **"DPO 和 RLHF 只是实现方式不同，性质一样。"** 关键差异在 on/off-policy：DPO 基于固定输出，RLHF 用模型实际输出。
11. **"GRPO 需要 reward model。"** 不需要。它依赖可验证奖励（答案比对、测试用例）。
12. **"推理链是免费的。"** 错。think token 计入计费，只是用户看不到。
13. **"推理链公开无害。"** 课程指出两个风险：可能泄露用户/对话信息；可能被他人用于训练。这是 UI 上推理链逐渐不再直接展示的原因。
14. **"长上下文只要把 RoPE 拿来直接用就行。"** 不行。模型未见过长距离旋转，需要 long-context training 与频率插值。
15. **"数据过滤是次要工程。"** 课程用 model collapse 与"仅保留约 1%"说明 data curation 是核心工作。

---

## 七、复习清单

**概念自检**
- [ ] 能不看笔记画出训练流水线的阶段顺序，并说出每阶段"改什么、用什么 loss、数据从哪来"。
- [ ] 能从第一性原理推出 cross-entropy，并解释每一步的理由。
- [ ] 能解释 BPB 解决什么问题，公式中每一项的含义。
- [ ] 能说明 teacher forcing 的机制与它造成的 mismatch，以及哪些阶段在缓解它。
- [ ] 能写出 Bradley-Terry 公式与 reward model 的 pairwise loss，并指出它与 cross-entropy 的同构关系。
- [ ] 能说出 reward model 的两种架构。
- [ ] 能解释 RL 目标函数为何要加"相对 reference model 的偏离惩罚"，reference 通常是谁。
- [ ] 能用 dense/sparse × on/off-policy 的表格定位 SFT、RLHF、DPO、GRPO、on-policy distillation。
- [ ] 能解释 LoRA 的计算与存储双重优势，以及为何 FFN 矩阵也应纳入。
- [ ] 能说明 reasoning model 的奖励为何"可验证"，以及序列级稀疏奖励的局限。
- [ ] 能解释 YaRN 的直觉：频率插值让长位置差落入短上下文见过的范围。
- [ ] 能说出 model collapse 与 context rot 各指什么、在哪个阶段处理。

**工程细节自检（GLM5 案例）**
- [ ] 预训练为何把文档切块拼接、batch 不一定以 BOS 开头。
- [ ] best fit packing 与 padding 的作用。
- [ ] mid-training 的数据混合为何以长篇幅为主。
- [ ] SFT 的 loss 为何"更加局部化"。
- [ ] RL 的三个子阶段（reasoning / agentic / general）各自的数据与验证方式。
- [ ] cross-stage distillation 针对哪些检查点、解决什么问题。

**延伸思考**
- [ ] 如果让你为一个特定垂直任务设计训练流水线，你会跳过哪些阶段、为什么？
- [ ] 在 data-constrained 情况下，重复数据与引入低质新数据如何权衡？
- [ ] reward hacking 与 on-policy distillation 的教师偏差，是否是同一类问题的两种表现？

---

## 八、下讲预告（课程原意）

- **Lecture 4**：展开 RL 的数学细节，包括 GRPO 等算法的具体更新规则；本讲只给直觉。
- **Lecture 5**：训练基础设施（infrastructure），本讲明确表示不展开。
- **Lecture 8**：encoder-only 设置下无法逐 token 预测时的替代方案。
- 课程第二部分：agent 相关内容。

> 笔记边界说明：本讲未给出具体硬件规格、benchmark 单位、精确日期与外部链接；涉及数值处均为课程口头举例，用于说明量级。
