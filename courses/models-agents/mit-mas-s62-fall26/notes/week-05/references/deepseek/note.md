# MIT MAS.S62 · Self-Evolving AI（Fall 2026）Week-05 学习笔记：Harness Evolution

> **说明**：本笔记基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。文中对幻灯片内容的概括与对内容的解释已尽量区分；页面重复、页码与 OCR 失真不作为论证依据。幻灯片中图像/图表细节无法从抽取文本完整恢复，相关处保留不确定性。英文术语保留原文。

---

## 一、学习目标

完成本周材料后，应能：

1. **说清 harness 的定位**：把 agent 理解为“model + harness”，harness 是围绕模型、管理其 context 与执行流程的代码；能列举 harness 的五个功能面（Context、Control、Action、Evaluation、Evolution）。
2. **建立 harness 存储词汇表**：区分 episode/trajectory、feedback、facts、tools、skills、artifacts、plans、experience 等概念，并说明为何 “experience” 常被模糊使用。
3. **理解 memory 作为 harness 的第一组件**：掌握 memory 的定义（超出当前 context 的持久状态，支持长程与累积学习），以及“存什么 / 怎么表示 / 存在哪 / 怎么复用”四维分析框架。
4. **比较外部记忆与内部记忆两条路线**：MemGPT、Mem0 代表的外部记忆系统 vs. MEM1 代表的内部状态压缩路线；理解 MEM1 的 memory consolidation 思路与其被报告的行为模式。
5. **理解 tools 与 skills 的区别与演化**：task-specific atomic action vs. task-agnostic reusable procedure；工具调用经由代码（code as meta-tool）、单步工具学习（Toolformer）、多步工具推理（ToolLLM）、技能文本化/代码化、技能库（Voyager）、工作流记忆（AWM）等路线。
6. **理解 Meta-Harness 的“harness 即文件系统”思想**：把 prompts、RAG、skills、tools、memory、完整程序循环统一为可被 LLM 自主修改的文件系统对象。
7. **接触客座部分的 RLM 视角**：harness 是“在黑盒模型约束之上的有立场选择（opinionated choices）”；了解“harness 作为组合泛化器”“局部分布内（locally in-distribution）”等提法，以及 harness 的可刻画性、model–harness 协同设计等开放问题。
8. **形成批判性判断**：识别各方法的适用边界、评测上的不确定性，以及幻灯片中未给出的信息（如具体数值、实验设置细节）。

---

## 二、课程定位与前后衔接

**幻灯片内容**：本周属于“Harness Evolution”，接续此前的“Context Evolution”。Recap 指出：context 是模型在生成下一个 token 前读到的一切；LLM 可以通过对 prompts/text/modules 的搜索与优化来自动优化 context；LLM 也能演化自己的 context（即解空间）以求解开放式问题（如 NP-hard 优化、编程、科学发现）。

**解释**：这建立了本讲的叙事线索——优化对象从“context”逐级扩展到“memory”，再到整个“harness”。第 53 页把这条线索明确概括为 memory → context → harness 的逐级 generalization，并指出这些方法的共同点是：简单、无需手工工程、端到端，且在 zero-shot、in-context prompting、fine-tuning 下都有可扩展的结果。

**公告信息（仅记录，不视为作业要求推断）**：Homework 1 已发布，due Oct 13 11:59pm；Reading 2 本周晚些时候发布，submissions + presentation 在 Oct 14；项目下一 checkpoint 是 midterm report + presentation（Oct 28），要求包括 processed datasets、ran baselines、done error analysis、更好的 proposed idea；并提倡 bottom-up research 与来自 readings/literature review 的 top-down ideation 并行。

---

## 三、核心概念

### 3.1 Agent = Model + Harness

幻灯片把 harness 定义为“围绕模型的代码，管理其 context 与执行流程以完成任务”，并给出五个功能面：

| 功能面 | 幻灯片给出的内涵 |
|---|---|
| Context | Prompt、memory、retrieved information |
| Control | Planning、routing、multi-agent orchestration |
| Action | Tools、skills、RAG、APIs、environments |
| Evaluation | Verification、safety、human feedback |
| Evolution | Reflection、update、learning |

**解释**：这个五分法把“演化”本身列为 harness 的一等功能，意味着 harness 不只是静态脚手架，而是包含反思与更新机制的自适应系统。这也解释了本讲为何把 memory、tools、skills 都放在“可演化对象”的框架下讨论。

### 3.2 Harness 中存储内容的词汇表

以 coding agent harness 为例：

- **Episode/trajectory**：state、action、next state、next action（例：好的调试示例）。
- **Feedback**：rewards、critiques、human preferences（例：用户偏好整洁代码）。
- **Facts**：semantic knowledge（例：排序函数具有某种复杂度）。
- **Tools**：task-specific atomic (external) action（例：运行 python interpreter）。
- **Skills**：task-agnostic reusable procedure（例：用 gdb 调试）。
- **Artifacts**：生成或优化后的输出（例：生成的代码）。
- **Plans**：分解后的任务与子目标（例：读需求、编写、模块化）。
- **Experience**：常被模糊使用，涵盖 trajectories、feedback、skills。

**解释**：这张词汇表的价值在于为后续所有方法提供“坐标”——任何记忆/技能系统都可以被问：它存储的是哪一类对象？

### 3.3 Memory 的定义与四维框架

**定义（幻灯片原文意）**：memory 是 agent harness 的持久状态，存储超出当前 context 的信息，使长程与累积学习成为可能。三条要点：memory 是 context 与 harness 的一部分；memory 决定什么进入 context；memory management 是 harness 的职责。

概览图给出的四个分析维度（图中文字可辨，但布局细节不可完全恢复）：

- **What is stored**：feedback、skills、trajectories、semantic facts。
- **How it's represented**：multimodal、structured、text、parameters。
- **Where it's stored**：context、external。
- **How it's reused**：retrieve、adapt、compose、transfer。

**解释**：这一框架贯穿全讲，第 31 页与第 51 页的总结图都复用了它，并把具体方法（MemGPT、Mem0、MEM1、CLM、ExpeL 等）标注到相应位置。由于图像信息不完整，方法在图上的精确落点存在不确定性，笔记不据此断言细粒度分类。

---

## 四、Memory 的方法比较

### 4.1 外部记忆系统：MemGPT

**幻灯片内容**：外部记忆系统的读写是 agent 的函数调用（function calls）。引用 Packer et al., *MemGPT: Towards LLMs as Operating Systems*, arXiv 2024。连续三页展示同一系统（含图示，细节不可恢复）。

**解释**：把记忆操作显式化为函数调用，意味着“何时读写记忆”成为 agent 决策的一部分；这与 operating system 的隐喻一致——把有限的 context 当作“内存”，把外部存储当作“磁盘”。

### 4.2 外部记忆系统：Mem0

**幻灯片内容**：记忆被结构化为图（graph），把消息转换为 entity 与 relation triplets；结构化表示常用于表示知识、数据库、符号状态。记忆上定义 add、update、delete、noop 四类操作。引用 Chhikara et al., *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory*, ECAI 2025。

**解释**：与 MemGPT 的“函数调用式读写”相比，Mem0 强调的是**记忆的结构与编辑语义**——图结构 + 显式增删改。noop 的存在提示系统需要判断“这条信息不值得写入”。

### 4.3 内部记忆：MEM1

**幻灯片内容**：关键问题是“增长的推理 context 带来复杂度与遗忘挑战”。提案是引入一个整合推理与记忆的 internal state：每一步模型更新该内部状态并丢弃此前所有信息。优点：(1) 使记忆接近常数规模（near-constant memory）；(2) 支持端到端优化。

机制细节（多页展示，文字可辨部分）：
- 每一轮，MEM1 生成“internal state + action”或“internal state + answer”。
- **Memory consolidation**：通过把过去知识压缩进最新的 internal state 来保持 context 规模恒定；记忆中只保留最新 internal state、query 与 info。
- 生成下一个 internal state 时移除此前 contexts。
- 用 answer 计算每条 rollout trajectory 的 outcome reward；两种使用方式：(1) direct prompting/in-context learning；(2) 用 reward 训练模型做压缩。
- 引用 Zhou et al., *Learning to Synergize Memory and Reasoning for Efficient Long-Horizon Agents*, ICLR 2026；附 https://github.com/MIT-MI/MEM1。

**结果与行为（幻灯片声称，非本笔记核验）**：在 MultiHopQA 上，“问题数增加时，baseline 方法性能下降、MEM1 上升；context 方面 baseline 上升、MEM1 持平”。行为观察包括：分别存储每个问题的关键抽取信息；在进入下一问题前显式更新记忆；在多次搜索无果后学会跳过该问题。

**不确定性说明**：结果页为图表，抽取文本只保留了趋势描述，没有具体数值、误差或评测配置；本笔记不虚构这些数字。对“MEM1 持平/上升”的解读应视为幻灯片作者的主张。

### 4.4 把记忆变成经验：Reflexion 与 ExpeL

**Reflexion（Shinn et al., NeurIPS 2023）**：trajectories 存入 short-term memory，自我反思的经验存入 long-term memory；模型 context 基于从 memory 的 retrieval 更新；是 context evolution 与 memory evolution 的结合。

**ExpeL（Zhao et al., AAAI 2024）**：在 Reflexion 基础上，trajectories 进 STM、reflections 进 LTM；**把 feedback 加入记忆**——记录经验是否有用；trajectories、experience、feedback 以类似 few-shot 示例的方式随任务给出。

**解释**：这两项工作把“记忆”从被动存储推进到“可复用的经验”；ExpeL 的关键增量是对经验做效用标注，从而支持筛选。

### 4.5 Context Language Models（CLM）

**幻灯片内容**：作为 context、memory、harness 讨论的收束，CLM 原生管理自己的 context——把 context 当作文件（context-as-a-file），允许模型对该文件做不受限编辑。实现：LM 的 live context 是一个可直接编辑的文件，路径写在 system prompt 中；LM 用 Bash 命令像编辑其他文件一样编辑它；对 context 文件的编辑与 LM 的 context 同步。多 agent 扩展：多个 context 文件可共存并与各自的 LLM agent 保持同步；通过创建/删除额外 context 文件来初始化与终止 subagents。实验包括 zero-shot 使用，以及通过 in-context learning、context evolution、reinforcement learning 做 fine-tuning（RL 的 reward 是 task outcome 与 cache efficiency 的混合）。引用 Shao et al., *Context Language Models*, arXiv 2026。

**解释**：CLM 把“记忆管理”还原为“文件编辑”这一模型已熟悉的操作，减少了对专门记忆 API 的依赖。第 53 页将其与 MEM1、Meta-Harness 并列为作者最偏好的方法，共同点是简单、端到端、无需手工工程。

### 4.6 Memory 方法横向比较（基于幻灯片可辨内容）

| 方法 | 存储位置 | 表示 | 复用方式 | 演化信号 |
|---|---|---|---|---|
| MemGPT | external | （图示，细节不可恢复） | 函数调用读写 | 未在抽取文本中说明 |
| Mem0 | external | graph / entity-relation triplets | add/update/delete/noop | 未在抽取文本中说明 |
| MEM1 | context（internal state） | 压缩后的内部状态 | 每步更新并丢弃旧信息 | outcome reward（可用 RL 训练压缩） |
| Reflexion | STM + LTM | 文本轨迹与反思 | retrieval 更新 context | 自我反思 |
| ExpeL | STM + LTM | 轨迹、反思、feedback | few-shot 式复用 | 经验效用反馈 |
| CLM | context-as-file | 可编辑文件 | Bash 编辑、多文件同步 | in-context / context evolution / RL |

**解释**：从 MemGPT 到 CLM，可以看到“谁来管理记忆”的重心从外部系统设计逐步转向模型自身的原生管理；MEM1 则走了相反方向的压缩路线——不是扩大可寻址存储，而是让状态规模恒定。

---

## 五、Tools 与 Skills 的方法比较

### 5.1 定义

- **Tools**：agent 可执行的 task-specific atomic action。例：从数据库检索某篇论文到 context。
- **Skills**：agent 在完成任务过程中学到的 task-agnostic reusable procedure，常结合推理与多次工具调用。例：如何做全面检索、聚类主题、撰写摘要。

### 5.2 工具使用与“代码作为元工具”

**幻灯片内容**：引用 Wang et al., *What are Tools Anyway? A Survey from the Language Model Perspective*, arXiv 2024。要点：code 是 meta-tool——代码把控制流、库、函数与多个操作组合进一个 action。

**Tool Calls via Code**：引用 Wang et al., *Executable Code Actions Elicit Better LLM Agents*, ICML 2024。幻灯片声称：通过代码调用工具在最少交互轮数下取得最佳成功率。

**解释**：“代码作为元工具”把工具调用从“单次 API 选择”提升为“可组合的程序合成”，这是后续 skills 代码化的基础。具体成功率数字未在抽取文本中给出，不予复述。

### 5.3 工具学习路线

- **单步工具调用（Toolformer）**：Schick et al., NeurIPS 2023。训练单步工具调用的 policy；主要贡献是大型 API 工具使用数据集，模型尝试并过滤不同工具用法，只在成功的用法上训练。
- **多步推理 + 工具（ToolLLM）**：Qin et al., ICLR 2024。把单步扩展到多步推理与工具使用，显著扩大支持的工具数量；使用 RapidAPI 的工具层级数据集（幻灯片称 16000+ real-world APIs）。

**解释**：Toolformer 的“尝试—过滤—训练”是一种自监督式的工具学习；ToolLLM 则把问题规模推向真实 API 生态，难度从“选对工具”变成“在层级化的工具空间中规划”。

### 5.4 Skills 的表示与学习

- **Skills as Text vs Skills as Code**：Wang et al., *Inducing Programmatic Skills for Agentic Tasks*, COLM 2025。幻灯片以对比页呈现两种表示（对比结论的图像细节不可恢复）。
- **Skills as Abstract Classes in Code**：Yu et al., *PolySkill: Learning Generalizable Skills Through Polymorphic Abstraction for Continual Learning*, ICLR 2026。用多态抽象把技能表示为代码中的抽象类，以支持持续学习中的泛化。
- **Skill Learning from Memory Trajectories**：Wang et al., *Agent Workflow Memory*, ICML 2025。常见工作流（即技能序列）可从过去成功与失败的 trajectories 中学到并存入 memory。
- **Skill Library（Voyager）**：Wang et al., *Voyager: An Open-Ended Embodied Agent with Large Language Models*, TMLR 2024。组合了自动课程生成、环境交互与反馈、工具使用、技能归纳，并存入 library（memory）。

**解释**：技能演化的关键问题是**抽象层级**——文本技能易读但难组合，代码技能可执行可组合但需要正确性保障，抽象类则试图兼顾泛化与复用。AWM 把“技能”落到“工作流序列”这一可统计的单元，Voyager 则给出开放式环境中技能库持续增长的完整回路。

### 5.5 Meta-Harness：把整个 harness 当作优化对象

**幻灯片内容**：LLM 优化 text/code 时通常只用短摘要、标量分数与少量历史候选；但 harness 更复杂。Meta-Harness 的 proposer 使用一个文件系统，内含完整源代码、分数与先前的执行轨迹；Claude Code proposer 通过 grep 与 cat 读取（幻灯片称 10M tokens 的反馈，对比先前方法的 26K）；proposer 能把失败追溯回具体的 harness 决策。框架上，harness 被统一表示为文件系统并通过代码完整优化，优化对象包括 prompts、RAG 系统、skills、tools、memory、完整程序循环。三个用例：文本分类 harness 演化；面向科学研究、context 用于数学推理的 RAG harness 演化；长程自主执行 + 验证循环的 agentic coding。引用 Lee et al., *Meta-Harness: End-to-End Optimization of Model Harnesses*, COLM 2026。

**解释**：这是本讲“演化层级”的最高点——不仅记忆与技能可演化，承载它们的整个程序都可被搜索。其代价是 proposer 需要处理海量、非结构化的反馈，因此“文件系统 + 检索命令”成为必要的基础设施，而非实现细节。10M vs 26K 的数字为幻灯片陈述，本笔记未核验。

---

## 六、客座部分：Rethinking the Role of Harnesses in LMs（Alex Zhang）

> 说明：客座幻灯片抽取文本较稀疏，多处页面仅有标题或图，以下只归纳文字可辨内容，不补全缺失论证。

### 6.1 出发点

- 过往工作方式的两种表述：“LM capabilities are a function of training data, whose size & quality is a function of what we care about solving / benchmarking.” 与 “LM systems and kernel design are iterative with clear objectives, but data constrained. How do we accelerate such tasks?”
- Typical LM workflow：Input prompt → LM → “Reasoning” + answer；以及加入 transform 的变体（Input prompt → LM → transform → answer）。
- “What does the 'standard' agent look like?” 一页仅有标题与图，内容不可恢复。

### 6.2 时间线与 RLM

- “Start of 2026: Context management in language models”：Jan 1，Prime Intellect 透露在做 RLMs；过去数月人们把 Claude Code 用于非 coding 任务；Jan 6，Cursor 发布 dynamic context。
- **Recursive Language Models**（Zhang, Kraska, Khattab, NeurIPS 2026）提出三个问题：语言模型是否应完全神经化？harness 是否重要、设计 harness 时哪些抽象重要？long-context 是不是一个“愚蠢的问题”？
- 核心引述：“LMs are constrained around their architecture. Harnesses are opinionated choices on top of a blackbox model, to get around that model's constraints.”
- 另有引用 From Raymond Weitekamp (2026)，以及“Are 'LM agents' analogous to an RLM reasoning chain?”——设想要求 LM 产出蛋白质折叠算法或其它大任务；并提到 mini-swe-agent 约 100 行代码。

### 6.3 The Mismanaged Geniuses Hypothesis

引述（Zhang, Li, Khattab, 2026）：“Language models are sufficiently capable of composing themselves to solve harder tasks. This a property of tasks themselves.” 与 “Harnesses can enable wider task transfer, by implicitly shaping what the model sees.”

**解释**：这一假设把能力问题的部分责任从模型转移到任务结构与 harness 设计上——若任务本身可组合，模型可能已具备自组合能力；harness 的作用是塑造模型所见，从而影响迁移。

### 6.4 Harness 作为组合泛化器

- *Language Model Harnesses are Compositional Generalizers*（Zhang, Khattab, 2026）：设计目标是 “Locally In-Distributionness”；实验设置为“只在短任务上训练，只在更长变体上评估”，即把泛化压力从 LM 移除；并尝试把泛化表现关联到训练轨迹（图中提到 max(re-executing top-25 closest train trajectories on eval contexts)，细节不可完全恢复）。

### 6.5 开放问题

- **微观视角（harness 设计选择）**：Base LM → Compaction → Compaction + RLM + “model shape” → Compaction + RLM → RLM 的谱系（图中带问号，具体含义不确定）。
- **宏观视角（相对 harness 的 scaling）**：harness 如何影响 data / envs 上的 scaling；harness 的 scaling laws（token spend）。
- **可刻画性**：若要为 harness 建立可预测的（如 inference scaling）规律，如何参数化我们关心的 harness 类？模型变强后 harness 的角色是什么？在有 verification 的情况下是否退化为 “LLM monkeys”？相对模型而言 harness 中最终重要的是什么（提及 HarnessTax, Pan et al., 2026）？
- **模糊 model–harness 协同设计**：不同输入/输出类型是否有更适合 harness 的权衡？某些 harness 改动是否会变成架构改动？LM 是否应始终是稠密的 string → string（提及 Jev, TypeSafe AI, 2026；以及把输出空间约束为 string → Dict[Literal, ...] 的例子）？model shape：LM 能否对“自己看到什么”与“不同粒度”有更多控制（引 https://alexzhang13.github.io/blog/2026/shape/）。

**解释**：客座部分没有给出结论性框架，而是把 harness 研究定位为一个尚缺“参数化与定律”的领域。这与主讲部分“memory → context → harness”的层级扩展形成呼应：可优化对象在变大，但刻画与预测工具尚未跟上。

---

## 七、局限与不确定性

1. **证据层级**：本笔记的唯一依据是幻灯片抽取文本。所有“效果更好/成功率最佳/性能上升”等表述均为幻灯片作者的陈述，未经独立核验；具体数值、置信区间、评测配置多不可得。
2. **图表信息缺失**：MemGPT、Mem0、CLM、Meta-Harness 用例、MEM1 结果与行为、客座部分的多数示意图，均以图像承载关键信息；抽取文本只保留了标题、图注与少量标签。涉及图内布局与细粒度分类的判断（如第 31、51 页总结图中各方法的精确落点）应保留不确定性。
3. **术语模糊性**：幻灯片自己指出 “experience” 常被模糊使用；skills 与 workflows、tools 与 code 之间的边界在不同工作中并不一致，跨论文比较需谨慎。
4. **方法覆盖不均**：MEM1、CLM、Meta-Harness 得到的篇幅与细节最多，其它工作（MemGPT、Mem0、Toolformer、ToolLLM、Voyager 等）多为一页概览，其机制细节与本笔记的概括之间存在信息落差。
5. **未包含的内容**：幻灯片未给出作业要求、实验数值、参考文献完整列表之外的细节；本笔记不对此做任何补全或推断。
6. **客座部分的可读性**：该组幻灯片抽取文本稀疏，多处仅有引述句或标题，无法还原完整论证链；本笔记对其只做要点记录，不视为完整讲授内容。

---

## 八、复习清单

**概念层**
- [ ] 用一句话定义 harness，并说出它的五个功能面及各一例。
- [ ] 区分 episode/trajectory、feedback、facts、tools、skills、artifacts、plans、experience。
- [ ] 复述 memory 的定义与三条要点（属于 context 与 harness、决定进入 context 的内容、管理是 harness 的职责）。
- [ ] 画出 memory 的四维框架（存什么/怎么表示/存在哪/怎么复用），并各举两例。
- [ ] 区分 tools（task-specific atomic）与 skills（task-agnostic reusable procedure）。

**方法层**
- [ ] MemGPT 与 Mem0 的记忆操作方式有何不同（函数调用 vs 图结构 + add/update/delete/noop）？
- [ ] MEM1 的 memory consolidation 如何保持 context 恒定？两种使用方式是什么？outcome reward 从哪来？
- [ ] Reflexion 与 ExpeL 的差异（后者加入 feedback/效用标注）是什么？
- [ ] CLM 的 context-as-a-file 如何实现？多 agent 扩展如何工作？三种 fine-tuning 途径是什么？
- [ ] Toolformer 与 ToolLLM 分别解决单步与多步的什么问题？
- [ ] 技能表示的三条路线（text / code / abstract class）各有什么取舍？
- [ ] AWM 与 Voyager 分别如何从轨迹中学习技能/工作流？
- [ ] Meta-Harness 的 proposer 为何需要文件系统与 grep/cat？它优化哪些对象？三个用例是什么？

**综合层**
- [ ] 解释“memory → context → harness”的层级扩展，以及三种偏好方法的共同点。
- [ ] 用自己的话解释 RLM 的核心引述（harness 是黑盒模型之上的有立场选择）。
- [ ] 说明“harness 作为组合泛化器”与“locally in-distribution”的实验设置含义。
- [ ] 列出客座部分提出的至少四个开放问题（可刻画性、scaling laws、model–harness 协同设计、model shape）。
- [ ] 指出本周材料中至少三处因图表缺失而无法确认的信息。

---

## 九、官方幻灯片 URL

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec4%20-%20harness.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/harness_guest.pdf
