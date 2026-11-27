# Saarland / UdS · Towards Self-Improving Agents · Winter 26/27 · Session-01 学习笔记

> **说明：基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。** 本笔记只从给定 PDF 的幻灯片抽取文本出发，区分“幻灯片明示内容”与“为便于学习而做的解释”。幻灯片中的图片/图表内容大多无法从文本层完整恢复，凡涉及图形、流程细节与实验数值之处，均标注不确定性，不虚构课堂对话、实验数值、作业要求或参考文献。

---

## 0. 课程定位与本次 session 的位置

幻灯片标题页给出课程名 **“Towards self-improving agents”**，授课者为 UdS（Universität des Saarlandes）的 **Yupei Du**，学期为 **winter 2026/27**。紧接着的一页提出贯穿课程的核心问题：

> **Can LLM agents learn from their own experience?**（LLM agent 能否从自身经验中学习？）

随后 “What is this seminar about?” 一页列出五个主题，构成本课程的整体框架：

1. **Reasoning and inference-time computation**（推理与推理时计算）
2. **Learning from agent experience**（从 agent 经验中学习）
3. **Task generation and curriculum learning**（任务生成与课程学习）
4. **Self-modifying agents**（自我修改的 agent）
5. **Evaluating self-improvement**（评估自我改进）

**解释（非幻灯片原文）**：这五个主题可以理解为一条链条——先讨论“在推理阶段多花算力能否提升表现”，再讨论“agent 能否把经验转化为学习”，然后讨论“训练任务本身能否被生成与编排”，进而讨论“agent 能否修改自身”，最后落到“如何评估自我改进是否真实有效”。这条链条也解释了为什么课程标题用 “Towards”（朝向）而非断言已实现通用的自我改进 agent。

---

## 1. 学习目标（基于幻灯片内容推导）

幻灯片没有单独列 “Learning objectives” 页，以下目标是从课程问题、主题清单、论文示例与考核格式中归纳的**学习层面目标**（属解释性整理）：

1. **理解核心问题**：能复述并界定 “self-improving agents” 的问题域，即 LLM agent 是否能从自身经验中学习，以及该问题的难点所在（幻灯片以问句形式提出，未展开定义）。
2. **掌握五大主题的定位**：能说明 reasoning / inference-time computation、learning from experience、task generation & curriculum learning、self-modifying agents、evaluation 五者各自关注什么，以及它们在一个“自我改进”框架中的相对位置。
3. **能读论文并做批判性报告**：幻灯片 “Presenting a paper” 明确要求：用例子解释问题与主要思想；讨论证据（evidence）、局限（limitations）与开放问题（open questions）；提前至少一周提出替代论文；事后提交 slides 与材料。这实际上给出了本课程对“理解论文”的操作性标准。
4. **能区分“推理时计算”与“学习”两类改进来源**：通过 Large Language Monkeys（重复采样扩展推理计算）与 RL + skill library（从经验中学习）两个示例，理解“多采样”和“参数/技能更新”是不同机制的改进路径。
5. **能讨论评估问题**：理解 “Evaluating self-improvement” 作为一个独立主题被列出，意味着自我改进的主张需要被评估，而不是默认成立（幻灯片未给出具体评估指标）。
6. **参与讨论与提问**：参与评分标准（0/1/2 三档）表明课程重视课堂质疑与 thoughtful contributions。

---

## 2. 核心概念

以下概念均来自幻灯片文本；每个概念后附“幻灯片依据”和必要的谨慎说明。

### 2.1 Self-improving agents（自我改进的 agent）

- **幻灯片依据**：课程标题 “Towards self-improving agents”；核心问句 “Can LLM agents learn from their own experience?”；“Self-modifying agents” 与 “Evaluating self-improvement” 两个主题。
- **解释**：幻灯片并未给出 “self-improving agent” 的形式化定义。从文本可以谨慎地说：课程把“自我改进”与“从自身经验学习”“自我修改”“可评估的改进”联系起来。任何更强的定义（例如“无需外部监督即可持续提升”）在幻灯片中没有明示，不应作为课程定义使用。

### 2.2 Reasoning and inference-time computation（推理与推理时计算）

- **幻灯片依据**：主题清单第一条；示例论文 *Large Language Monkeys: Scaling Inference Compute with Repeated Sampling*。
- **解释**：从论文标题可提取的关键词是 **repeated sampling**（重复采样）与 **scaling inference compute**（扩展推理计算）。即：在不改变模型参数的前提下，通过在推理阶段增加采样/计算来提升表现。幻灯片未给出该方法的具体算法、采样数量、任务类型或实验数值，这些细节属于图表/正文内容，本次提取无法确认。

### 2.3 Learning from agent experience（从 agent 经验中学习）

- **幻灯片依据**：主题清单第二条；示例论文 *Reinforcement Learning for Self-Improving Agent with Skill Library*。
- **解释**：标题显示两个关键词：**Reinforcement Learning**（强化学习）与 **Skill Library**（技能库）。可以谨慎推断：该工作把 agent 的经验用于 RL 训练，并以技能库的形式组织/复用技能。但“技能如何表示”“经验如何收集”“RL 的具体算法”在幻灯片文本中均未出现，不能虚构。

### 2.4 Task generation and curriculum learning（任务生成与课程学习）

- **幻灯片依据**：主题清单第三条；示例论文 *Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability*；以及一页含流程元素的图：**Task generator → Training tasks → Learner**，并有 **learning progress** 与 **Evaluate progress** 两个标注。
- **解释**：该流程图（从提取文本可见的标签）暗示一个闭环：任务生成器产出训练任务，学习者在其上训练；同时存在对“学习进度”的评估，并似乎反馈回任务生成。**不确定性说明**：箭头方向、反馈回路的具体连接、各模块内部机制无法从文本层确认；上图仅为按提取标签的谨慎重构，不代表幻灯片图形的精确结构。
- **“Edge of Learnability”**：从论文标题可提取该短语，提示任务难度应位于“可学习性的边缘”——即过难或过易都不利于学习。这是标题层面的提示，幻灯片未给出该概念的量化定义。

### 2.5 Self-modifying agents（自我修改的 agent）

- **幻灯片依据**：主题清单第四条；示例论文 *Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents*。
- **解释**：标题关键词包括 **Darwin**（暗示演化/选择）、**Gödel Machine**（自我修改机器的经典概念）、**Open-Ended Evolution**（开放式演化）。可以谨慎地说：该工作把自我改进 agent 放在开放式演化的框架下讨论。幻灯片未说明其具体实现、修改对象（代码/提示/架构）或评估方式，这些不可从提取文本确认。

### 2.6 Evaluating self-improvement（评估自我改进）

- **幻灯片依据**：主题清单第五条，独立成条。
- **解释**：将“评估”单列为主题，意味着课程把“自我改进是否发生、是否可测”视为独立问题。幻灯片未列出具体指标、基准或统计方法，笔记中不应补造。

### 2.7 课程运作相关概念（Logistics）

- **Instructor**: Yupei Du，邮箱 yudo@lst.uni-saarland.de
- **时间地点**：Tuesdays, 16:15–17:45，Gebäude C7 3 – Seminarraum 1.14
- **Paper sessions**: 10 Nov 2026–2 Feb 2027
- **No class**: 3 Nov, 22 Dec, 29 Dec
- **Format**：每周一篇主论文，由一或两名学生报告；报告 45–60 分钟；讨论 30–45 分钟；要求读论文并积极参与。
- **Presenting a paper**：用例子解释问题与主要思想；讨论证据、局限与开放问题；至少提前一周提出替代论文；事后发送 slides 与材料。
- **Participation and assessment**：每次课参与评分 0（not engaged）/1（questions/comments）/2（thoughtful contributions）。4 credits：Presentation 60% + participation 40%。7 credits：Presentation 30% + participation 20% + term paper 50%。
- **Term paper**（仅 7-credit 版本）：focused survey 或小型独立项目；最多 10 页（不含 references 与 appendices）；NeurIPS format；邮件提交 PDF；**Deadline: 31 March 2027**。
- **LLM policy**：允许使用 AI 工具；须记录使用情况；你对内容负责；需核查 claims、citations、experiments、code。
- **Questionnaire**：幻灯片给出链接 `https://forms.gle/6RSfE7YJchVNQjzC8`（属课程事务信息，非学术参考文献）。

---

## 3. 方法比较

幻灯片以“每个主题配一篇示例论文”的方式呈现，因此比较只能在**标题与主题标签层面**进行；以下比较表中的“机制”一栏均标注为基于标题的谨慎解读，凡幻灯片未给出的细节一律留空并注明不确定。

| 维度 | Inference-time computation（Large Language Monkeys） | Learning from experience（RL + Skill Library） | Task generation & curriculum（Teaching Models to Teach Themselves） | Self-modifying agents（Darwin Gödel Machine） |
|---|---|---|---|---|
| 幻灯片给出的定位 | 主题一：推理与推理时计算 | 主题二：从 agent 经验中学习 | 主题三：任务生成与课程学习 | 主题四：自我修改的 agent |
| 改进发生在何处（据标题推断） | 推理阶段：repeated sampling 扩展 inference compute | 学习阶段：RL 训练 + skill library | 训练任务层面：生成任务并按学习进度调整 | agent 自身：开放式演化式自我修改 |
| 是否改变模型参数 | 标题未提及参数更新，重点在 inference compute（不确定） | 标题含 Reinforcement Learning，通常涉及参数更新（推断，幻灯片未明示） | 标题未说明学习者是否更新参数；流程含 Learner 与 Evaluate progress（不确定） | 标题含 self-improving agents 与 evolution，修改对象不确定 |
| 关键机制词 | repeated sampling, scaling inference compute | reinforcement learning, skill library | task generator, training tasks, learner, learning progress, edge of learnability | Darwin, Gödel Machine, open-ended evolution |
| 评估方式 | 幻灯片未给出 | 幻灯片未给出 | 图中有 “Evaluate progress” 标签，具体指标未给出 | 幻灯片未给出 |
| 主要不确定性 | 采样规模、任务、收益曲线均不可从提取文本确认 | 技能表示、经验来源、算法细节不可确认 | 流程图精确结构与反馈方向不可确认 | 修改对象与演化机制不可确认 |

**解释（非幻灯片原文）**：从比较可以看出课程的设计意图——四个技术主题分别对应“改进可能发生的四个位置”：推理时、经验学习时、任务分布上、agent 自身结构上；第五个主题（评估）横切所有位置。这一“位置分类”是笔记作者的组织方式，不是幻灯片明示的分类法。

---

## 4. 局限与不确定性

### 4.1 幻灯片本身呈现的局限（文本可支持）

1. **课程是 “Towards” 而非 “How to”**：标题用 “Towards self-improving agents”，核心问题以问句形式出现（“Can LLM agents learn from their own experience?”），说明课程把该问题视为开放问题而非既定结论。
2. **示例论文仅给标题**：五个主题各配一篇论文标题，幻灯片文本层没有给出方法细节、实验设置或数值结果，因此无法在笔记中比较性能。
3. **评估被列为待讨论主题**：把 “Evaluating self-improvement” 单独列出，本身暗示“自我改进”的度量是未决问题（此为解释，非幻灯片原话）。

### 4.2 本次提取带来的不确定性（必须保留）

- **图表缺失**：主题三的流程图只提取到标签（Task generator、Training tasks、Learner、learning progress、Evaluate progress），其图形结构、箭头方向、是否有反馈回路均无法确认；笔记中的“闭环”描述属谨慎重构。
- **无数值**：幻灯片文本中没有出现任何实验数值、数据集名称或基准分数；本笔记不填写任何数值。
- **无参考文献列表**：幻灯片只出现论文标题（Large Language Monkeys、Reinforcement Learning for Self-Improving Agent with Skill Library、Teaching Models to Teach Themselves、Darwin Gödel Machine），未给出作者、年份、 venue；笔记不补造引用信息。
- **OCR/版式失真风险**：标题页的人名、邮箱、日期等已按可读文本记录；若个别字符存在识别偏差，以官方 PDF 为准。
- **未核验课堂口头讲述**：教师可能在课堂上补充了定义、例子与要求，本笔记不包含这些内容。

### 4.3 概念层面的谨慎边界

- “Self-improving” 在幻灯片中没有形式化定义；不能把“重复采样提升表现”直接等同于“自我改进”，二者在课程中分属不同主题（主题一 vs 主题二至四），这一区分是笔记的解释。
- “Edge of Learnability” 仅为论文标题短语，不能据此断言课程给出了难度控制的具体算法。

---

## 5. 复习清单

**A. 事实性记忆（幻灯片明示）**

- [ ] 课程名、授课教师、学期：Towards self-improving agents；Yupei Du；winter 2026/27。
- [ ] 核心问句：Can LLM agents learn from their own experience?
- [ ] 五个主题：reasoning and inference-time computation；learning from agent experience；task generation and curriculum learning；self-modifying agents；evaluating self-improvement。
- [ ] 四篇示例论文标题（按主题对应）：
  - Large Language Monkeys: Scaling Inference Compute with Repeated Sampling
  - Reinforcement Learning for Self-Improving Agent with Skill Library
  - Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability
  - Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents
- [ ] 课程事务：周二 16:15–17:45，C7 3 – Seminarraum 1.14；paper sessions 10 Nov 2026–2 Feb 2027；停课 3 Nov、22 Dec、29 Dec。
- [ ] 报告格式：45–60 分钟报告 + 30–45 分钟讨论；一或两名学生；需用例子讲问题与思想、讨论证据/局限/开放问题、提前一周提替代论文、事后交材料。
- [ ] 评分：参与 0/1/2 三档；4 credits = 60% presentation + 40% participation；7 credits = 30% presentation + 20% participation + 50% term paper。
- [ ] Term paper（7 credits）：survey 或小项目；≤10 页（不含 references/appendices）；NeurIPS format；PDF 邮件提交；截止 31 March 2027。
- [ ] LLM policy 四要点：可用 AI 工具；记录使用；自负内容责任；核查 claims/citations/experiments/code。

**B. 理解性复述（合上笔记自测）**

- [ ] 用自己的话说明“推理时计算”与“从经验学习”两条改进路径的区别，并各举幻灯片中的论文标题为例。
- [ ] 说明主题三流程图中出现的四个标签，并指出哪些结构信息是幻灯片文本无法确认的。
- [ ] 解释为什么课程把 “Evaluating self-improvement” 单列为一个主题（基于幻灯片结构的合理推断，并标注这是推断）。
- [ ] 说明 “Edge of Learnability” 在幻灯片中只以论文标题形式出现，不能过度解读。

**C. 批判性思考（对应报告要求）**

- [ ] 对每篇示例论文，尝试提出至少一个“证据是否充分”的问题（课堂讨论用；笔记不预设答案）。
- [ ] 思考：若一个 agent 在重复采样下表现提升，这能否作为“从自身经验学习”的证据？两者在课程框架中分属哪两个主题？
- [ ] 思考：自我修改 agent 的“改进”应如何被评估？幻灯片未给答案，列出你认为需要澄清的问题。

**D. 事务性检查**

- [ ] 确认自己选 4 credits 还是 7 credits，并对应准备 presentation / term paper。
- [ ] 确认报告周次与替代论文的提前一周截止。
- [ ] 填写问卷链接（幻灯片给出）：`https://forms.gle/6RSfE7YJchVNQjzC8`。
- [ ] 使用 AI 工具时保留使用记录，并核查所有 claims 与 citations。

---

## 6. 一页速记（可选）

- **一个问题**：LLM agents 能否从自身经验中学习？
- **五个主题**：推理时计算 → 经验学习 → 任务生成/课程 → 自我修改 → 评估。
- **四篇示例**：Monkeys（重复采样）、RL+Skill Library、Teach Themselves（Edge of Learnability）、Darwin Gödel Machine（开放式演化）。
- **一条主线（解释）**：改进可以发生在推理、学习、任务分布、agent 结构四个位置，评估横切全部。
- **一个态度**：标题是 “Towards”，问题是问句——把自我改进当作待检验的主张，而非既定事实。

---

**官方幻灯片 URL（仅输入中给出者）**：https://docs.google.com/presentation/d/1NbojB0-V0Ef_5V2rAyjQIw5ZsWOLd6Shs9XudmM4Uis/export/pdf
