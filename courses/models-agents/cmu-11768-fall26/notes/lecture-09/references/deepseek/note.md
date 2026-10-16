# CMU 11-768 Fall 2026 · Lecture 9 · Training 2: Reinforcement Learning Basics 课程学习笔记

> 待审核候选稿 · 来源：平台字幕与官方 Slides · 尚未发布。

> 依据：Lecture 9 官方 Slides（`lecture-09-rl-basics.pdf`，页码引用均指该 PDF 页码）与课程视频自动字幕清洗稿的中文候选译稿。两者若有不一致，以 Slides 为准；图示与公式的视觉细节需对照官方 PDF 核验（待核）。本笔记不声称经过人工审核。

---

## 一、学习目标

学完本讲，你应当能够：

1. 用数字搜索（Number Search）这一贯穿例子，说明智能体与环境交互如何被形式化为轨迹、观测、动作与奖励（Slides 第 2、9、10、11 页）。
2. 说清 SFT 用于智能体/序列预测时的三类问题：任务不匹配、数据不匹配、暴露偏差（Slides 第 4、5、6 页）。
3. 写出期望奖励目标 $J(\theta)$，并独立推导 REINFORCE 的得分比率（score-ratio / log-derivative）技巧（Slides 第 13、18、19 页）。
4. 把策略梯度落到实现层面：掩码（masking）与按奖励重缩放（rescaling）SFT 损失（Slides 第 21、22 页）。
5. 说明基线（baseline）与优势（advantage）为何有用、为何不引入偏差，以及它降低方差的直觉（Slides 第 27–34 页）。
6. 描述组相对优势估计与 GRPO 更新，并说出 DrGRPO 的两处改动及其动机（Slides 第 37–40 页）。
7. 识别本讲方法的共同失效模式（组内奖励全同 → 无梯度）与常见补救方向（Slides 第 41 页）。

---

## 二、概念主线

本讲的叙事是一条“问题 → 目标 → 估计 → 改进 → 变体”的主线：

**上一讲回顾（SFT）→ SFT 的三个问题 → 让智能体自己生成轨迹并按奖励加权 → 期望奖励目标 $J(\theta)$ → 不可微，故用策略梯度 → REINFORCE → 奖励应当“相对化” → 基线与优势 → 组相对优势（GRPO/DrGRPO）→ 方法对比。**

主线的一句话版本：**本讲所有方法都只是在给“智能体自己采取的动作”配一个权重**，区别只在这个权重是什么（Slides 第 44 页）：

| 方法 | 权重 $w_t$ |
|---|---|
| ReST-EM | 成功轨迹上为 1，其余为 0（等价于对保留数据做 SFT） |
| REINFORCE | $R(\tau)$，该动作所属轨迹的奖励 |
| GRPO / DrGRPO | $\hat{A}$，相对同一任务实例其他 rollout 的奖励 |

统一形式（Slides 第 44 页）：

$$\nabla_\theta J = \sum_t w_t \nabla_\theta \log \pi_\theta(a_t \mid h_t)$$

---

## 三、贯穿例子：数字搜索（Number Search）

设定（Slides 第 2 页）：隐藏整数在 1 到 16 之间，智能体最多猜 4 次；每次猜错后环境返回“higher”或“lower”；只有猜中时奖励为 1，否则为 0。本讲的任务实例隐藏数字为 **11**。

四条样例轨迹（Slides 第 2 页）：

- $\tau_1$: 8 → higher → 12 → lower → 10 → higher → 11 → correct，$R = 1$
- $\tau_2$: 4 → higher → 8 → higher → 12 → lower → 11 → correct，$R = 1$
- $\tau_3$: 16 → lower → 8 → higher → 9 → higher → 10 → timeout，$R = 0$
- $\tau_4$: 1 → higher → 2 → higher → 3 → higher → 4 → timeout，$R = 0$

关键观察：$\tau_1$ 与 $\tau_2$ 动作不同但同样成功——这正是“任务不匹配”的直观来源。课堂中还类比了 Wordle：最优首次猜测类似二分（此处最优首猜为 8），但次优首猜（如 4）仍可能成功，而糟糕策略（如 16 或 1,2,3,4）会超时失败。演讲者还提到，若从 16 开始且第一次就返回 lower，则可能耗尽四次机会。

奖励设置的一般化（Slides 第 9、11 页）：奖励是标量，可在轨迹末尾给出，也可逐步给出。字幕中提到 RLVR（带可验证奖励的强化学习）常使用 0/1 二元奖励，例如代码是否通过全部单元测试；本讲方法更通用，也适用于连续标量奖励。

---

## 四、符号与假设

先集中给出本讲用到的符号与它们背后的假设，后续公式都以此为基准。

- 任务实例 $x$（如隐藏数字 11）。
- 轨迹 $\tau = (o_0, a_0, r_1, o_1, \dots, a_{T-1}, r_T, o_T)$；奖励 $R(\tau) = \sum_{t=1}^{T} r_t$（Slides 第 11 页）。
- 历史 $h_t = (o_0, a_0, o_1, \dots, o_t)$，即策略真正条件化的东西（Slides 第 10 页）。
- 环境状态 $s_t$：决定环境的一切，可能含智能体看不到的隐藏状态（例如后端数据库内容、隐藏数字）。
- 策略 $\pi_\theta(a_t \mid h_t)$：$\theta$ 是驱动智能体的语言模型参数。
- 轨迹概率（Slides 第 12 页）：

$$p_\theta(\tau \mid x) = \prod_t \pi_\theta(a_t \mid h_t)\, P(o_{t+1}, r_{t+1} \mid h_t, a_t, x)$$

- 目标（Slides 第 13 页）：$J(\theta) = \mathbb{E}_{\tau \sim p_\theta(\cdot \mid x)}[R(\tau)]$。

**假设说明**：

1. **部分可观测（POMDP）**：字幕中明确回应提问——本讲处理的是 POMDP，智能体看不到底层状态，只能看到观测，因此 $o_{t+1}$ 的概率依赖于此前全部动作与观测历史，而非仅上一状态与动作。表述方式是为了便于处理，在此类情形下与其他等价写法一致。
2. **环境不可微**：动作是离散且采样的；环境（例如单元测试）不可微（Slides 第 18 页）。因此不能直接反向传播，需要策略梯度。
3. **环境概率未知但可采样**：我们不知道 $P$，但可以通过与环境交互来采样（Slides 第 12 页）。字幕中称之为“有点神奇”的地方在于：只靠交互采样就足以估计出依赖于该分布的参数梯度。
4. **奖励位置**：一般设置下可在每个动作/观测后给奖励；数字搜索只在轨迹末尾给 0/1 奖励（Slides 第 11 页）。两种奖励位置在公式上可互相等价处理。

---

## 五、SFT 的三个问题

Slides 第 3 页给出 SFT 损失：

$$L_{\text{SFT}} = -\sum_t \log \pi_\theta(a_t^* \mid h_{1:t})$$

目标动作可来自人类、更强的模型（蒸馏），或（本讲语境下）智能体自己的一条成功轨迹。

三个问题（Slides 第 4、5、6 页）：

1. **任务不匹配（task mismatch）**：SFT 最大化“被示范动作”的概率，我们真正想要的是最大化“完成任务”的概率。二者相似但不同：完成任务有多种方式（$\tau_1$ 与 $\tau_2$）；某些动作明显更差（例如在“12 → lower”之后不应猜 13），但 SFT 对所有未被示范的动作一视同仁，不会区分好坏。
2. **数据不匹配（data mismatch）**：我们希望也能从次优数据中学习。失败的轨迹（$\tau_3$、$\tau_4$）不应被 SFT 用来提高其动作概率，但我们仍希望有方法让模型“不要走这条路”。
3. **暴露偏差（exposure bias）**：训练时模型在固定历史下预测下一个动作，而生成/评估时历史由模型自己产生（自回归）。若模型生成了训练分布之外的动作（例如收到“higher”后却猜了更低的数），由于训练中从未见过这类情况，它的响应可能完全失准（Slides 第 6 页示意：训练示范是 8 → higher → 12，而生成为 8 → higher → ?）。

字幕中补充：RL 可视为一种让模型生成自己的训练数据、并学会从自己错误中恢复的方法；这一“让模型产生自己的训练数据”的性质称为**同策略（on-policy）**。它通常有利，因为监督信号与模型当前能力匹配，也有效率上的权衡（下一讲/后续讲座会讨论放宽这些假设、更偏 off-policy 的方法）。

---

## 六、专家迭代与 ReST

在完整策略梯度之前，本讲先给一个朴素但有效的基线：**专家迭代**中的一类——**强化自训练（Reinforced Self-Training, ReST）**（Slides 第 14–16 页）。

流程（Slides 第 15 页）：

1. **Grow**：从当前策略采样轨迹并计算奖励。
2. **Improve**：用奖励过滤数据（二元奖励时保留 $R = 1$），扩充已有数据集，训练策略。
3. **Repeat**：用更新后的策略继续。

损失仍是标准 SFT 损失，只作用在高奖励轨迹上（Slides 第 16 页）：

$$L_{\text{ReST}} = -\sum_{\tau: R(\tau)=1} \sum_t \log \pi_\theta(a_t \mid h_t)$$

课堂澄清点（来自字幕）：它与“自蒸馏”的区别在于用奖励做过滤；若模型完全无法产生正奖励轨迹，RL/ReST 可能并不适用，可考虑先用好示范做冷启动（字幕提到推理模型常有冷启动阶段）、课程学习（先选有足够多可解样本的问题），或给予中间奖励。

---

## 七、策略梯度与 REINFORCE

### 7.1 目标与推导（Slides 第 18、19 页）

不能直接反向传播的两个原因：动作是离散且采样的（改变 $\theta$ 只改变概率，样本相对于参数的导数几乎处处为零）；环境不可微。

起点是把期望写成求和：

$$J(\theta) = \sum_\tau p_\theta(\tau \mid x) R(\tau)$$

取梯度：奖励 $R(\tau)$ 只依赖轨迹，不依赖 $\theta$，所以

$$\nabla_\theta J = \sum_\tau \nabla_\theta p_\theta(\tau \mid x) R(\tau)$$

**得分比率技巧**：乘除 $p_\theta(\tau \mid x)$，并用 $\nabla p / p = \nabla \log p$：

$$\nabla_\theta J = \sum_\tau p_\theta(\tau \mid x) R(\tau) \nabla_\theta \log p_\theta(\tau \mid x) = \mathbb{E}_{\tau \sim p_\theta(\cdot \mid x)}\left[ R(\tau) \nabla_\theta \log p_\theta(\tau \mid x) \right]$$

这是可采样估计的期望。REINFORCE（Williams, 1992，Slides 第 19 页标注）。

### 7.2 三个组成部分（Slides 第 20 页）

$$\nabla_\theta J = \mathbb{E}_{\tau \sim p_\theta(\cdot \mid x)}\left[ R(\tau) \sum_t \nabla_\theta \log \pi_\theta(a_t \mid h_t) \right]$$

- $\tau \sim p_\theta(\cdot \mid x)$：通过与环境交互采样得到；
- $R(\tau)$：来自环境的任务级评估；
- $\nabla_\theta \log \pi_\theta(a_t \mid h_t)$：机制与 SFT 中相同，但动作是策略采样出来的，而不是示范动作。

### 7.3 轨迹对数概率的分解（Slides 第 21 页）

$$\log p_\theta(\tau \mid x) = \sum_t \log P(o_{t+1}, r_{t+1} \mid h_t, a_t, x) + \sum_t \log \pi_\theta(a_t \mid h_t)$$

环境项不含 $\theta$，求导后为常数而消失：

$$\nabla_\theta \log p_\theta(\tau \mid x) = \sum_t \nabla_\theta \log \pi_\theta(a_t \mid h_t)$$

一个动作可能对应**多个 token**。若 $a_t = (u_{t,1}, \dots, u_{t,m_t})$，则

$$\nabla_\theta \log \pi_\theta(a_t \mid h_t) = \sum_{k=1}^{m_t} \nabla_\theta \log \pi_\theta(u_{t,k} \mid h_t, u_{t,<k})$$

### 7.4 实现：掩码 + 奖励缩放（Slides 第 22 页）

实际计算“基本上就是对标准 SFT 损失做掩码与重缩放”：

$$L_{\text{PG}} = -R(\tau) \sum_{t:\, m_t = 1} \sum_t \log \pi_\theta(u_t \mid u_{<t})$$

其中 $m_t = 1$ 标记策略自己生成的 token（含 turn 结束 token），$m_t = 0$ 标记提示词与观测 token；$R(\tau)$ 是一个被整条轨迹所有生成 token 共享的标量。字幕中演讲者提到第一次看到 REINFORCE 在复杂任务上的实现（涉及对话模型优化的论文）时，惊讶于其简单：做一次 SFT 梯度计算，再把梯度/损失乘以奖励。

### 7.5 训练循环（Slides 第 23 页）

1. **Collect**：采样任务实例，在其上从智能体采样；
2. **Evaluate**：为每条轨迹计算奖励；
3. **Form loss**：用奖励给动作对数概率加权；
4. **Update**：反向传播，改变 $\theta$，再采集。

损失：$L_{\text{PG}} = -\sum_i R(\tau_i) \sum_t \log \pi_\theta(a_{i,t} \mid h_{i,t})$。标准 REINFORCE 每个实例只用一条轨迹；批大小即任务实例数（后续 GRPO 会为每个实例生成多条轨迹）。

### 7.6 与 ReST 的关系（Slides 第 24 页）

二元奖励下，REINFORCE 与 ReST 形式相近：

$$-\sum_i R(\tau_i) \sum_t \log \pi_\theta(a_{i,t} \mid h_{i,t}) \quad\text{vs.}\quad -\sum_{i: R(\tau_i)=1} \sum_t \log \pi_\theta(a_{i,t} \mid h_{i,t})$$

差异在于 ReST 做批量更新并聚合数据集，而 REINFORCE 完全在线：采样后直接更新。

---

## 八、基线与优势

### 8.1 动机：奖励应当是相对的（Slides 第 26 页）

- 对成功轨迹 $\tau_1$，所有动作都被 $R=1$ 上调；
- 对失败轨迹 $\tau_3$，基础 REINFORCE（以及 ReST）**完全不产生梯度**，因为被奖励 0 缩放。

但我们其实希望“学会不去做” $\tau_3$ 这类事。另一个直觉是：更新应取决于策略在这个实例上通常表现多好。设想模型约 95% 的时间在该实例上得 1，若 5% 的时间出现一个愚蠢错误而得到 0，应对这类罕见但代价高的错误做很强的反向更新。

### 8.2 优势的定义（Slides 第 27 页）

$$A_\pi(h, a) = Q_\pi(h, a) - V_\pi(h)$$

即“采取该动作后的期望奖励”减去“从该历史出发的期望奖励”。课堂具体例子：历史为 8 → higher、12 → lower，数字只能是 9、10 或 11，还剩两次猜测。若策略足够好，$V_\pi(h)$ 可以接近 1；若在有效范围内更随机，可能更像 2/3。

- 猜 11：若错则剩两个候选、只剩一次猜测，故 $A_\pi(h, 11) < 0$；
- 猜 10：即使错也还剩一次猜测，可以往高或往低猜，故 $A_\pi(h, 10) > 0$。

由于 $Q_\pi$ 与 $V_\pi$ 都未知，实践中用采样奖励来估计：

$$\hat{A}_t = R(\tau) - b(h_t)$$

### 8.3 带优势估计的策略梯度（Slides 第 28 页）

$$\nabla_\theta J = \mathbb{E}\left[\sum_t (R(\tau) - b(h_t)) \nabla_\theta \log \pi_\theta(a_t \mid h_t)\right]$$

baseline $b$ 的不同选择产生不同算法：

| baseline 选择 | 对应方法 |
|---|---|
| 常数 | 本讲的 bandit 例子 |
| 已见奖励的运行平均 | 随策略改进而自适应 |
| 训练出的价值模型 $V_\phi(h_t)$ | actor–critic、PPO |
| 组内均值 | GRPO（无需额外模型） |

Slides 第 28 页强调：这些行是估计同一个 $\nabla_\theta J$ 的不同有效方式。

### 8.4 基线不引入偏差（Slides 第 29 页）

对只依赖历史的基线：

$$\mathbb{E}_{a \sim \pi_\theta(\cdot \mid h)}\left[b(h) \nabla_\theta \log \pi_\theta(a \mid h)\right] = b(h) \sum_a \pi_\theta(a \mid h) \nabla_\theta \log \pi_\theta(a \mid h)$$

利用 $\nabla \log \pi = \nabla \pi / \pi$，得 $b(h) \nabla_\theta \sum_a \pi_\theta(a \mid h) = b(h) \nabla_\theta 1 = 0$。因此减去这样的基线是无偏的。

### 8.5 两臂老虎机例子（Slides 第 30–33 页）

单参数策略：$p = \pi_\theta(\text{guess A}) = \sigma(\theta)$。当前 $\theta = -1.1$，$p = 0.25$ 奖励 1，$1-p = 0.75$ 奖励 0——这是一个糟糕的策略，因为高概率给了无奖励动作。我们希望 $\theta$ 变得更正。

**无基线**：

- 采样 A（奖励 1）：梯度 $= 1 \times (1-p) = +0.75$；
- 采样 B（奖励 0）：梯度 $= 0 \times (-p) = 0$。

**加基线 $b = 0.5$**（Slides 第 31 页）：

- 采样 A：$\hat{A} = 1 - 0.5 = +0.5$，梯度 $= +0.5 \times 0.75 = +0.375$（无基线时 +0.75）；
- 采样 B：$\hat{A} = 0 - 0.5 = -0.5$，梯度 $= -0.5 \times (-0.25) = +0.125$（无基线时 0）。

两者都让 $\theta$ 增大、提高猜 A 的概率，但基线**从失败中也产生了学习信号**，同时保持期望梯度不变。

**方差对比**（Slides 第 32 页）：精确期望 $\mathbb{E}[\hat g] = 0.1875$。无基线时采样估计为 0.375（概率 0.25）与 0（概率 0.75）；基线 0.5 时样本更接近真值。Slides 第 32 页给出基线 0.5 时 $\hat g$ 的 SD = 0.108。

**长期行为**（Slides 第 33 页）：反复采样的滑动平均都收敛到 0.1875，但无基线时 SD 0.325，基线 $b=0.5$ 时 SD 0.108。字幕中演讲者说这类可视化是为了“说服自己”基线如何起作用，并强调该直觉可迁移到更复杂的序列决策设置。

### 8.6 基线的局限（Slides 第 34 页）

**有好处**：标记轨迹比预期更好还是更差；好的基线降低梯度方差。

**未解决**：同一轨迹内所有动作共享同一个优势 $\hat{A}$（**信用分配**问题未解决）；估计 $V_\pi(h)$ 可能需要单独的模型。

---

## 九、中间奖励与 reward-to-go

若环境在最终步之前也给奖励，可用 **reward-to-go** 降低方差（Slides 第 35 页）：

$$R_t = \sum_{t'=t+1}^{T} r_{t'}$$

一个动作只被它之后的奖励加权；更早的奖励不依赖 $a_t$，因此去掉它们可降方差而不增偏差。数字搜索只在末尾结算，故对每个动作都有 $R_t = R(\tau)$。Slides 第 35 页还给出一个示意：某个工具奖励 +0.2 在动作 $a_t$ 之前，因此被“忽略”。

---

## 十、组相对优势与 GRPO / DrGRPO

### 10.1 组相对优势（Slides 第 37 页）

思路：对同一实例多次采样策略，用组内奖励的均值作为 baseline，无需额外模型。

$$\bar{R} = \frac{1}{G}\sum_{j=1}^{G} R(\tau_j), \qquad \hat{A}_j = \frac{R(\tau_j) - \bar{R}}{\sigma_R}, \qquad b(h_t) = \bar{R}$$

Slides 第 37 页的表格（沿用 $\tau_1$–$\tau_4$）：奖励 [1, 1, 0, 0]，$\bar{R} = 0.5$，$\sigma_R = 0.5$，先中心化再除以标准差，得到优势 [+1, +1, −1, −1]。

字幕中所属动机：GRPO 出自 DeepSeekMath 论文，目的是效率——过去把 RL 用于语言模型常需要单独模型来预测 baseline，这很耗算力；组相对方法去掉了这个模型，很优雅。组大小常见取 8（字幕提到后续讲座会有关于组大小选择的指导）。

### 10.2 GRPO 更新（Slides 第 38 页）

批中包含多个任务实例，每个实例有自己的组：

| 任务实例 | 组内奖励 | $\bar{R}_i$ | 优势估计 |
|---|---|---|---|
| $x_1$（隐藏 11） | 1 1 0 0 | 0.50 | +1 +1 −1 −1 |
| $x_2$（隐藏 3） | 1 0 0 0 | 0.25 | +1.73 −0.58 −0.58 −0.58 |
| $x_3$（隐藏 7） | 1 1 1 0 | 0.75 | +0.58 +0.58 +0.58 −1.73 |

注意：每个任务实例**单独**标准化（各自的 $\bar{R}_i$ 与 $\sigma_i$）。损失形式（Slides 第 38 页）：

$$-\sum_i \frac{1}{G}\sum_{j=1}^{G} \sum_t \hat{A}_{ij} \log \pi_\theta(a_{ij,t} \mid h_{ij,t})$$

Slides 第 38 页明确注明：这是针对当前策略轨迹写出的形式，**省略了原论文的 ratio、clipping 与 KL 项**。字幕也确认今天只讨论 GRPO 内部的优势函数，ratio/clipping/参考模型正则在后续讲座讨论。字幕中有提问确认该优势是无偏的（因为它只依赖提示与模型采样），回答为是。

### 10.3 DrGRPO 的两处改动（Slides 第 39 页）

1. **不除以组标准差**，只减去组内均值。理由：除以 $\sigma_R$ 会让优势失去“问题难度”的意识——实例的难度尺度被标准化掉了，从而“几乎总是通过”或“几乎总是失败”的实例权重被放大（Slides 第 39 页“Advantage estimate”行）。字幕补充：很多自称 GRPO 的实现实际上已经去掉除以标准差的步骤。
2. **不按生成长度归一化**，改为除以全局常数 $C$（论文使用生成预算）。理由：按长度归一化时，长而错误的回答每个 token 被惩罚得更少，于是策略会**漂移向更长的错误答案**（Slides 第 39 页“Response aggregation”行）。

Slides 第 39 页底注：奖励本身不变，改变的是任务实例与回答之间的相对权重。

### 10.4 DrGRPO 的 token 系数（Slides 第 40 页）

对单个任务实例，轨迹 $j$ 的每个生成 token 共享该轨迹的优势估计（$\hat{A}_j = R(\tau_j) - \bar{R}$，不除以 $\sigma_R$）：

$$L_{\text{DrGRPO}} = -\frac{1}{G}\sum_{j=1}^{G} \frac{1}{C}\sum_{t: m_{j,t}=1} \hat{A}_j \log \pi_\theta(u_{j,t} \mid u_{j,<t})$$

Slides 第 40 页给出 $\tau_1$（$\hat{A}_1 = +0.5$）与 $\tau_3$（$\hat{A}_3 = -0.5$）的逐 token 示意：每个生成 token 的系数为 $\hat{A}_j / C$。页面注明这是简化形式，原论文目标还含 ratio 与 clipping。

### 10.5 退化情形（Slides 第 41 页）

组内奖励完全相同时，优势全为 0，该组不贡献任何梯度：

- 全部失败 $[0,0,0,0] \to [0,0,0,0]$：可能对当前策略太难；
- 全部成功 $[1,1,1,1] \to [0,0,0,0]$：可能对当前策略太容易。

若采样的轨迹全部失败，可考虑（Slides 第 41 页）：换任务实例、扩大探索、加入示范、提供更有信息量的奖励。字幕中进一步列出：冷启动/示范微调、课程学习、中间奖励与奖励塑形（例如给“找到正确文件”的中间奖励）。

---

## 十一、常见误区

1. **“策略梯度需要知道环境模型”**。不需要。未知 $P$ 可通过交互采样绕过（Slides 第 12 页）。代价是算法偏慢、算力需求大。
2. **“奖励为 0 的轨迹没有信息”**。在基础 REINFORCE 里确实没有梯度（Slides 第 26 页），但加 baseline 后，失败也会提供学习信号（Slides 第 31 页）。
3. **“减 baseline 会改变优化目标”**。不会；对只依赖历史的 baseline，期望梯度不变（Slides 第 29 页），变化的是方差（Slides 第 32、33 页）。
4. **“baseline 能解决信用分配”**。不能。同一轨迹所有动作共享同一个 $\hat{A}$（Slides 第 34 页）。reward-to-go 是另一条独立思路（Slides 第 35 页）。
5. **“GRPO 就是论文完整损失”**。本讲只讲优势函数，省略了 ratio、clipping、KL 项（Slides 第 38、40、42 页）。
6. **“GRPO 的除以标准差是必要的”**。字幕指出很多实现已去掉它；DrGRPO 正是把它作为两处改动之一，并给出“失去难度意识”的动机（Slides 第 39 页）。
7. **“ReST 与 REINFORCE 是两种完全不同的东西”**。二元奖励下二者损失形式高度相似，差别在于批量更新/数据集聚合 vs 完全在线（Slides 第 24 页）。
8. **“组内奖励全对/全错只是数据问题”**。它是算法层面的退化：优势恒为 0，该组无梯度（Slides 第 41 页）。

---

## 十二、复习问题

1. 写出 $J(\theta)$ 的定义，并完整推导 REINFORCE 的表达式，指出每一步用到了什么假设（Slides 第 13、18、19 页）。
2. 为什么 $\nabla_\theta \log p_\theta(\tau \mid x)$ 中环境概率项会消失？这一性质对算法有什么实际意义（Slides 第 21 页）？
3. 用 Slides 第 2 页的四条轨迹解释“任务不匹配”：为什么 $\tau_1$ 与 $\tau_2$ 的存在说明 SFT 目标与“完成任务”的目标不同？
4. 在数字搜索给出历史“8 → higher、12 → lower”时，为什么 $A_\pi(h, 10) > 0$ 而 $A_\pi(h, 11) < 0$？这对策略意味着什么（Slides 第 27 页）？
5. 在两臂老虎机例子中，基线 $b = 0.5$ 如何把“采样 B 得到 0 梯度”变成“+0.125 的梯度”？为什么这不改变期望梯度（Slides 第 30、31 页）？
6. 已知无基线时 SD 0.325、基线 0.5 时 SD 0.108，而两者滑动平均都收敛到 0.1875。这说明基线的收益体现在哪里（Slides 第 32、33 页）？
7. 为什么 DrGRPO 去掉除以 $\sigma_R$？为什么去掉按长度归一化？分别对应 Slides 第 39 页表格中的哪一行？
8. 如果某个任务实例的四条 rollout 奖励全是 0，GRPO 会怎样？可以采取哪些补救措施（Slides 第 41 页）？
9. 用 Slides 第 44 页的权重视角统一比较 ReST-EM、REINFORCE、GRPO/DrGRPO。
10. 本讲的三类 SFT 问题，分别被本讲的哪一部分机制所解决（Slides 第 7、45 页）？

---

## 十三、待核事项

以下内容仅靠文本提取无法确认，需对照官方 PDF 与视频核验，本笔记不做猜测：

- 所有公式的精确排版、上下标位置与希腊字母（Slides 第 12、13、19、20、21、22、28、29、37、38、40、44 页）。
- 图示与曲线：Slides 第 7 页 RL 流程图、第 15 页 ReST 三阶段图、第 18 页不可微示意、第 30–33 页的 sigmoid 曲线与梯度采样可视化、第 34 页信用分配示意、第 35 页 reward-to-go 时间轴、第 42 页 PPO/GRPO 对比图。
- Slides 第 1 页的 SWE-bench 标注（演示中含有小字“SWE-bench verified”一类字样）——文本提取不可靠，待核。
- 逐字稿中的若干专名与术语被自动字幕误写（例如 “Swedbench”、“gpo”、“DRGP”、“Dr. gpo”、“Aorva”、“Graham”、“PO”、“deal or no deal” 论文名），语义应以官方 Slides 术语（PPO、GRPO、DrGRPO、ReST-EM 等）为准。
- Slides 第 32 页标注基线 $b = 0.5$ 时 SD 0.108 与无基线 0.325 的数值来源与计算细节。
- 逐字稿中提到的具体论文（Williams 1992、ReST/ReST-EM、DeepSeekMath、DrGRPO）在 Slides 中以脚注链接形式给出，具体链接与引用格式待核。

---

## 十四、官方来源链接（给定资料）

- 课程主页：https://www.cmu-agents.com/
- 课程日程与阅读：https://www.cmu-agents.com/#schedule
- 作业与项目要求：https://www.cmu-agents.com/#assignments
- Assignment 1 · Harness：https://github.com/cmu-agents/assignment-1
- Assignment 2 · Eval：https://github.com/cmu-agents/assignment-2
- 课程视频（Lecture 9）：https://www.youtube.com/watch?v=paAcPaaYZGM&list=PLSN0qpDfUvTM&index=9
- 官方课程日程：https://www.cmu-agents.com/#schedule
- Lecture 9 slides：https://www.cmu-agents.com/slides/lecture-09-rl-basics.pdf
