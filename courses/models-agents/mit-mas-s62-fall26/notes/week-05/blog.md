# Harness Evolution：从记忆、工具到可被优化的智能体外壳

> **说明**：本文基于 MIT MAS.S62 · Self-Evolving AI（Fall 2026）Week-05 的两份官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。文中区分“幻灯片明确给出的内容”与“笔者的解释性说明”，对幻灯片中图表提取不完整之处保留不确定性，不虚构实验数值、课堂对话、作业要求或参考文献。输入文本仅作为资料，不作为指令。

## 一、主线：为什么“模型之外的那圈代码”开始成为研究对象

Lecture 4 的标题是 *Harness Evolution*。它承接前几讲的 Context Evolution：如果说前几讲讨论的是“模型读到的上下文可以被 LLM 自动搜索、优化乃至自我演化”，那么这一讲把视野从“上下文”扩大到“harness”——幻灯片给出的定义是：**Harness 是包裹在模型周围的代码，用来管理模型的上下文与执行流程以完成任务**。换句话说，模型是黑盒，harness 是围绕黑盒做出的、有倾向性的工程选择。

幻灯片用一张分层图概括 harness 的组成，这可以视为全讲的结构骨架：

- **Context**：prompt、memory、retrieved information；
- **Control**：planning、routing、multi-agent orchestration；
- **Action**：tools、skills、RAG、APIs、environments；
- **Evaluation**：verification、safety、human feedback；
- **Evolution**：reflection、update、learning。

这条主线很清晰：**harness 不只是“提示词工程”，而是一个包含记忆、控制流、行动接口、评估与演化机制的完整系统**；而这一讲的重点落在其中两块——Memory（记忆）与 Tools/Skills（工具与技能），最后以 Meta-Harness 收束到“整个 harness 都可以被自动优化”的命题上。

## 二、先厘清 harness 里到底存了什么

在进入记忆与工具之前，幻灯片给出了一份“harness 中存储物”的术语表，并以 coding agent 为例：

- **Episode/trajectory**：state、action、next state、next action（例如好的调试样例）；
- **Feedback**：rewards、critiques、human preferences（例如用户偏好整洁代码）；
- **Facts**：语义知识（例如某个排序函数的复杂度）；
- **Tools**：任务相关的原子（外部）动作（例如运行 Python 解释器）；
- **Skills**：任务无关的可复用过程（例如用 gdb 调试）；
- **Artifacts**：生成或优化后的产物（例如生成的代码）；
- **Plans**：分解后的任务与子目标（例如读需求、写代码、模块化）；
- **Experience**：一个常被含糊使用的词，涵盖 trajectories、feedback、skills。

**解释**：这份清单的价值在于把“经验”“记忆”这类模糊说法拆成可操作的对象。它同时暗示了一个判断标准——不同的存储物适合放在不同的位置（上下文、参数、外部存储），并以不同方式被复用（检索、适配、组合、迁移），这正是后文记忆分类图的坐标轴。

## 三、Harness Part 1：Memory

### 3.1 定义与定位

幻灯片对 memory 的定义是：**agent harness 的持久状态，存储超出当前上下文的信息，使长程、累积性学习成为可能**。紧接着给出三条定位：memory 是 context 与 harness 的一部分；memory 决定什么进入 context；memory 管理是 harness 的职责。

**解释**：这三条把“记忆”从“更大的上下文窗口”这一狭义理解中解放出来。记忆的关键不是容量，而是**准入决策**——由 harness 决定哪些过往信息值得重新进入当前上下文。

### 3.2 记忆的分类坐标

幻灯片用一张三维分类图概括记忆研究：**存什么**（feedback、skills、trajectories、semantic facts）、**怎么表示**（multimodal、structured、text、parameters）、**存在哪**（context、external），以及**怎么复用**（retrieve、adapt、compose、transfer）。这张图在讲末的 Summary 中被再次使用，并把具体工作标注到坐标上：例如 MEM1、MemGPT、Mem0、CLM、ExpeL 等。**需要说明的是**，幻灯片中这些标注点的精确位置无法从提取文本中完全还原，此处只保留“哪些工作被放进同一张分类图”这一事实，不推断其具体坐标。

### 3.3 外部记忆系统：MemGPT 与 Mem0

**MemGPT**（Packer et al., arXiv 2024）被用三页幻灯片呈现，核心一句话是：**读与写都是 agent 发起的函数调用**。也就是说，记忆操作被显式建模为工具调用，由模型决定何时读写外部记忆。

**Mem0**（Chhikara et al., ECAI 2025）则展示了两点：其一，记忆被组织成**图结构**，把消息转换为实体与关系三元组，幻灯片指出结构化表示常用于表示知识、数据库与符号状态；其二，记忆操作包括 **add、update、delete、noop** 四类函数。

**解释**：MemGPT 与 Mem0 代表了“外部记忆”路线的两个侧面——接口上把记忆操作工具化，结构上把记忆图谱化。它们的共同前提是：记忆不放在模型参数里，也不完全放在上下文里，而是放在模型之外、由 harness 调度。

### 3.4 内部上下文中的记忆：MEM1

MEM1（Zhou et al., ICLR 2026）是幻灯片着墨最多的工作，也是讲末被主讲人列为“最喜欢的方法”之一。

它的问题设定是：**不断增长的推理上下文带来复杂度与遗忘挑战**。其提案是引入一个**内部状态（internal state）**，把推理与记忆整合起来；每一步模型更新该内部状态，并丢弃此前所有信息。幻灯片列出两条优势：实现近似恒定的记忆占用；支持端到端优化。

机制上，幻灯片给出的关键概念是 **Memory Consolidation（记忆巩固）**：MEM1 通过把过往知识压缩进最新的内部状态来保持上下文大小恒定，记忆中只保留最新的内部状态、query 与 info。在每一轮，MEM1 生成“内部状态 + 动作”或“内部状态 + 答案”；当新的内部状态生成时，此前的上下文被移除。答案被用来计算每条 rollout 轨迹的结果奖励（outcome reward）。幻灯片给出两种使用方式：直接 prompting / in-context learning；或者用奖励训练模型学会压缩。

关于行为层面，幻灯片展示了三类定性观察：MEM1 学会分别存储每个问题的关键抽取信息（示例中分别记下某球队在 Brooklyn 与 Los Angeles 的世界大赛出场次数）；它会在进入下一问题前显式更新记忆（示例中把“某人生于 Porto Recanati”加入累积摘要）；它学会在多次搜索无果后跳过当前问题。**解释**：这些是幻灯片展示的示例片段，用于说明“记忆巩固”在语言层面的表现，而非定量结论。

关于结果，幻灯片只有一页 MultiHopQA，其文字说明为：随着问题数量增加，基线方法性能下降而 MEM1 上升；基线方法的上下文增长而 MEM1 持平（图中以“–”表示不变）。**需要保留不确定性**：幻灯片未给出具体数值，且提取文本中的箭头符号属于图注性质，本文不将其转写为任何具体数字或效应量。

### 3.5 把记忆变成经验：Reflexion 与 ExpeL

**Reflexion**（Shinn et al., NeurIPS 2023）的要点是：轨迹存入短期记忆（STM），自我反思存入长期记忆（LTM）；模型上下文根据从记忆中的检索而更新；这是 context 演化与 memory 演化的结合。

**ExpeL**（Zhao et al., AAAI 2024）在 Reflexion 基础上推进：轨迹进 STM，反思进 LTM；并且**把反馈加入记忆**——记录某段经验是否有用；轨迹、经验、反馈以类似 few-shot 示例的方式随任务提供。

**解释**：这两项工作把“记忆”从被动的存储升级为可被检索、可被评价的经验库，记忆的写入质量（反思是否有用）开始成为 harness 设计的一部分。

### 3.6 上下文语言模型（CLM）

CLM（Shao et al., arXiv 2026）被幻灯片作为“上下文、记忆与 harness 讨论的收束”。其主张是：**Context Language Models 原生地管理自己的上下文，把上下文当作一个文件，允许模型对该文件做不受限制的编辑**。

具体机制包括：**context-as-a-file** 实现——LM 的实时上下文是一个可直接编辑的文件，路径写在 system prompt 中，LM 用 Bash 命令像编辑其他文件一样编辑它，对上下文文件的编辑与 LM 的上下文同步；**多智能体扩展**——多个上下文文件可以共存并分别与各自的 LLM agent 保持同步，子 agent 通过创建和删除额外的上下文文件来初始化与终止。

幻灯片还给出实验设置的两页：第一组实验是 CLM 的 zero-shot 使用；第二组是通过 in-context learning、context evolution 或 reinforcement learning 对 CLM 做微调，其中强化学习的奖励是**任务结果与缓存效率的混合**（reward is mix of task outcome and cache efficiency）。幻灯片展示了 in-context instructions 与 context evolution、RL 的示意页，但**具体实验数值与图表细节在提取文本中缺失，本文不作补充**。

**解释**：CLM 的意义在于把“记忆管理”从 harness 代码中的隐式逻辑，变成模型可直接操作的显式对象（文件）。这与 MEM1 形成有趣对照：MEM1 把记忆压进内部状态以保持恒定，CLM 把整个上下文暴露为可重写的文件以保持可控。

### 3.7 记忆部分的小结

Summary 页把前述工作放回三维分类图：ExpeL、MEM1、MemGPT、CLM、Mem0 等分别落在“存什么 / 怎么表示 / 存在哪”的不同组合上。**解释**：这张图本身就是一个论断——记忆研究的差异，很大程度上是“表示与位置的选择”的差异，而不是“有没有记忆”的差异。

## 四、Harness Part 2：Tools and Skills

### 4.1 定义上的关键区分

幻灯片给出两个定义：**Tool 是 agent 可执行的任务相关的原子动作**（例如从数据库检索某篇论文并取回上下文）；**Skill 是 agent 在完成任务过程中学到的、任务无关的可复用过程，通常结合推理与多次工具调用**（例如如何做一次全面检索、聚类主题、撰写摘要）。

**解释**：这组定义的区分点是“任务相关 vs 任务无关”“原子 vs 组合”。工具是可被调用的动作单元，技能是可被复用的程序性知识。这一区分贯穿本节后续所有工作。

### 4.2 工具使用：从综述到代码作为元工具

幻灯片引用 Wang et al.（arXiv 2024）的工具综述，并用一页指出：**代码是一种元工具（meta-tool）**——代码把控制流、库、函数与多个操作组合进一个动作。

随后引用 *Executable Code Actions Elicit Better LLM Agents*（ICML 2024），其结论是：**通过代码调用工具在成功率最高的情况下使用了最少的交互轮数**。**需要说明**：幻灯片未给出该结论的具体数值与实验设置细节，本文只转述这一比较性表述。

### 4.3 学习工具调用：Toolformer 与 ToolLLM

**Toolformer**（Schick et al., NeurIPS 2023）针对**单步工具调用**训练策略：构建大规模 API 工具使用数据集，让模型尝试并过滤不同的工具使用，再在成功的样本上训练。

**ToolLLM**（Qin et al., ICLR 2024）把单步调用扩展到**多步推理 + 工具使用**，并显著扩大支持的工具体量，使用 RapidAPI 的工具层级数据集（幻灯片称其覆盖 16000+ 真实 API）。

**解释**：这两项工作体现了工具学习的一条演进线——从“学会何时调用一个 API”，到“在推理链中编排大量 API”。

### 4.4 技能：文本、代码与抽象类

幻灯片引用 CMU AI Agents 课程的材料，重申工具与技能的定义后，转向技能的表示形式。*Inducing Programmatic Skills for Agentic Tasks*（COLM 2025）对应“**技能作为文本 vs 技能作为代码**”的对比；*PolySkill*（ICLR 2026）则提出“**技能作为代码中的抽象类**”，通过多态抽象获得可泛化的技能以支持持续学习。

**解释**：技能表示的演进逻辑是：文本技能易读但难执行，代码技能可执行但难泛化，抽象类则在二者之间引入接口与多态，使技能可在不同任务间迁移。

### 4.5 从轨迹中学技能：AWM 与 Voyager

**Agent Workflow Memory**（Wang et al., ICML 2025）指出：常见工作流（即技能序列）可以从过往成功与失败的轨迹中学习，并存入记忆。幻灯片用两页展示这一“从记忆轨迹学习技能”的过程。

**Voyager**（Wang et al., TMLR 2024）的技能库则组合了多个想法：自动课程生成、环境交互与反馈、工具使用、技能归纳，并存入技能库（即记忆）。幻灯片同样用两页展示技能库。

**解释**：AWM 与 Voyager 把第三节的记忆机制与本节技能概念接了起来——**技能是记忆中被蒸馏出来的可复用过程**，而记忆是技能归纳的原料。

### 4.6 Meta-Harness：把整个 harness 当作优化对象

Meta-Harness（Lee et al., COLM 2026）是本节乃至全讲的“收束点”。幻灯片先给出问题背景：LLM 优化文本/代码时，通常只使用短摘要、标量分数与少量过往候选；但 **harness 要复杂得多**。

Meta-Harness 的做法是：**proposer 使用一个文件系统，其中包含完整源代码、分数与先前的执行轨迹**；幻灯片以 Claude Code proposer 为例，说明它通过 grep 与 cat 读取，获得的反馈量级为 **10M tokens，而此前方法为 26K tokens**；因此 proposer 能把一次失败追溯回具体的 harness 决策。

幻灯片给出三个使用场景：为文本分类演化 harness；为科学研究演化 RAG harness（上下文用于数学推理）；长程自主执行 + 验证循环的 agentic coding。并强调其统一框架“以文件系统表示，完全通过代码优化”，可优化 prompts、RAG 系统、skills、tools、memory、完整程序循环。

**解释**：Meta-Harness 的命题是——如果 harness 可以被表示为一个文件系统，那么它就可以像代码一样被自动搜索与修改；这使“harness evolution”从人类手写 harness，走向 LLM 自主改写 harness。幻灯片中 10M 与 26K 的对比是明确给出的数字，但本文不将其扩展为任何性能结论。

## 五、全讲小结：三种“把 X 当作 Y”的思路

Summary 页回到 harness 的三维分类图，并在“我最喜欢的方法”一页给出三条并列：

- **MEM1**：把记忆当作上下文中的内部状态，由 LLM 自主更新；
- **CLM**：把整个上下文当作持久文件，由 LLM 自主维护与重写；
- **Meta-Harness**：把整个 harness 当作文件系统，由 LLM 自主修改。

幻灯片随后总结其共性：简单、无需手工工程、端到端；是一个新的范式，推广了“可被自主优化的对象”（memory → context → harness）；在 zero-shot、in-context prompting、fine-tuning 下都有可扩展的结果。

**解释**：这三条其实是同一个思想的三级放大——**把某个原本由人类工程师隐式管理的对象显式化，然后交给模型自主优化**。这也是本讲标题“Harness Evolution”的真正含义：演化的对象从上下文，扩展到记忆，再到整个 harness。

## 六、嘉宾部分：重新思考 harness 的角色

第二份幻灯片来自 Alex Zhang（MIT CSAIL 博士生，Omar Khattab / Tim Kraska 指导），主题是 *Rethinking the role of harnesses in LMs*。其结构是若干组对照命题与开放问题，本文按幻灯片顺序转述，并明确区分幻灯片内容与解释。

### 6.1 从“典型 LM 工作流”到“标准 agent”

幻灯片先展示典型语言模型工作流：输入 prompt → LM → “reasoning” + answer；再加入“transform”环节，形成 prompt → LM → transform → answer 的链条。随后以“标准 agent 长什么样”为题展示 agent 结构（该页图示在提取文本中缺失，本文不描述其具体形态）。

### 6.2 2026 年初的上下文管理动态

幻灯片列出三条时间线式信息：1 月 1 日 Prime Intellect 透露正在做 RLM；1 月 6 日 Cursor 发布 dynamic context；以及“过去几个月人们把 Claude Code 用于非编程任务”。**解释**：这些是幻灯片给出的行业观察，本文仅转述，不补充其背景细节。

### 6.3 Recursive Language Models（RLM）

RLM（Zhang, Kraska, Khattab, NeurIPS 2026）部分提出三个问题：语言模型是否应该完全是神经的？harness 是否重要、设计 harness 时哪些抽象重要？以及一句立场性表述——“long-context 是个愚蠢的问题”。

幻灯片给出 RLM 的核心引语：**“LM 受其架构约束。Harness 是在黑盒模型之上、为绕过该模型约束而做出的有倾向性的选择。”** 随后一页展示“LM agent 是否类比于 RLM 推理链”的设问：假设要求一个 LM 产出蛋白质折叠算法或某个大任务，幻灯片以“e.g. mini-swe-agent is ~100 lines of code!”提示 agent 实现的轻量性。（该页图示在提取文本中缺失。）

### 6.4 The Mismanaged Geniuses Hypothesis

幻灯片以两组引语对照呈现这一假设（Zhang, Li, Khattab, 2026）：一组是“语言模型足够有能力组合自身以解决更难的任务——这是任务本身的属性”；另一组是“harness 可以通过隐式塑造模型所见，实现更广的任务迁移”。

**解释**：这组对照把争论聚焦为——能力究竟来自模型自身，还是来自 harness 对输入分布的重塑。幻灯片没有给出裁决，只给出假设名称与两条立场。

### 6.5 组合泛化与“局部分布内”

*Language Model Harnesses are Compositional Generalizers*（Zhang, Khattab, 2026）部分给出一个实验设定：**只在短任务上训练，完全在更长变体上评估**，并讨论“从 LM 身上移除泛化压力”。幻灯片另有一页把泛化性能与训练轨迹关联，图注为“在评估上下文上重新执行最接近的 top-25 训练轨迹的最大值”。**需要保留不确定性**：该图的具体坐标与结果在提取文本中缺失，本文不转写任何数值或趋势结论，仅保留图注所述的方法描述。

### 6.6 当前关注：微观与宏观两个视角

幻灯片把当前兴趣分为两层：**微观视角（harness 设计选择）**，给出一条从 Base LM → Compaction → Compaction + RLM + “model shape” → Compaction + RLM → RLM 的谱系；**宏观视角（相对 harness 的扩展）**，包括 harness 如何影响数据/环境上的 scaling，以及 harness 的 scaling laws（token 花费）。谱系中“model shape”处标有问号，表示未定。

### 6.7 开放问题：harness 可被刻画吗

幻灯片列出一组问题：若要为 harness 建立可预测的（如推理 scaling）规律，如何参数化我们关心搜索的 harness 类别？随着模型变强，harness 的角色是什么、如何刻画与研究？带验证时，这是否退化为“LLM monkeys”？相对模型而言，harness 中最终重要的是什么？并标注 **HarnessTax（Pan et al., 2026）**。

### 6.8 模糊模型—harness 协同设计

最后一组幻灯片讨论：是否存在与不同输入/输出类型配合更好的权衡？某些 harness 改动是否会变成架构改动？幻灯片给出两个例子：Jev（TypeSafe AI, 2026）作为“约束输出空间，使 LM 成为 string → Dict[Literal, noul]”的近期例子；以及“model shape”一节的问题——“语言模型能否对自己的所见有更多控制，并具有不同的粒度级别？”（链接指向 alexzhang13 的博客文章）。

**解释**：嘉宾部分整体不是给答案，而是给问题清单。它与主讲部分形成互补：主讲部分展示“harness 已经被怎样演化”，嘉宾部分追问“harness 应该如何被刻画、其边界在哪里”。两部分的共同底色是：harness 不再是临时脚手架，而是需要被建模、被优化、被理论化的对象。

## 七、结语

把两份幻灯片放在一起看，Week-05 的主线可以概括为三次“对象化”：

1. **记忆被对象化**：从 MemGPT 的函数调用式外部记忆、Mem0 的图结构记忆，到 MEM1 的内部状态与 CLM 的上下文文件，记忆不再是“更大的窗口”，而是 harness 中可被表示、存放、复用与演化的显式对象。
2. **工具与技能被对象化**：工具是原子动作，技能是可复用过程；代码作为元工具、技能作为代码/抽象类、工作流从轨迹中被归纳，技能由此成为可学习、可存储、可组合的资产。
3. **harness 本身被对象化**：Meta-Harness 把整个 harness 表示为文件系统并交给 LLM 优化；嘉宾部分则进一步追问这种对象化的边界——harness 是否能被参数化、其 scaling 是否可预测、模型与 harness 的协同设计是否会模糊二者的界限。

需要再次强调本文的边界：以上是对官方幻灯片抽取文本的整理与解释，**未核验课堂口头讲述**；幻灯片中的图表细节、实验数值与部分图示在提取文本中缺失，本文对相应位置只保留定性描述与不确定性说明，不虚构任何数据、对话、作业要求或参考文献。若需完整细节，请以官方幻灯片原文为准。

## 参考来源（官方幻灯片）

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec4%20-%20harness.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/harness_guest.pdf
