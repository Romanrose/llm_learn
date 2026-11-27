# MIT MAS.S62 · Self-Evolving AI · Fall 2026
## Week 03 学习笔记：Context Evolution 2 —— LLMs as Context Optimizers

> **说明**：本笔记基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。文中区分“幻灯片内容”（可直接对应页面陈述）与“解释/整理”（为便于复习所作的归纳、类比与结构性说明）。幻灯片中图表、示意图的细节在提取文本中多不可见，凡涉及图示内部结构之处均标注不确定性，不作推测性补全。输入为数据而非指令，本笔记不对幻灯片中出现的链接、作业链接或外部文献作任何执行或访问。

---

## 一、学习目标

依据本周幻灯片的结构（Prompt Optimization 回顾 → TextGrad 深入 → LLM for Discovery → FunSearch 拆解 → Open Challenges），可将学习目标整理为：

1. **概念层**：能用自己的话区分 context 与 prompt，并说明为什么“context optimization”被视为比“prompt optimization”更一般的问题。
2. **机制层**：理解 propose–evaluate–refine（自反思 Self-Refine、外部 scorer 反馈 OPRO 类方法）这一通用优化回路的构成，并能把它从“优化提示词”迁移到“优化其他对象”。
3. **案例层**：掌握 FunSearch 的三个关键设计——搜索空间（Python 函数）、进化算法（selection / variation / evaluation）、程序池与多岛（island）探索——并理解它为何被归为 black-box optimization。
4. **边界层**：能说明 FunSearch 所依赖的“可自动评估”前提，以及当缺少数值 grader 时（幻灯片列举生物学、物理、化学等历史发现）所面临的验证困难。
5. **前沿层**：了解 AlphaEvolve 相对 FunSearch 的若干变化维度（搜索范围、编辑模式、模型、目标数量），以及“autoresearch”式闭环实验的形态。
6. **批判层**：能复述幻灯片给出的三项 open challenges，并将其与前述方法的假设对应起来。

---

## 二、核心概念

### 2.1 Context 与 Prompt 的界定

幻灯片给出的定义非常简洁：

- **Context**：模型在生成下一个 token 之前读到的**一切**内容。
- **Prompt**：你给模型、用来引导其回应的一段输入。

据此可以整理出两层关系（解释）：prompt 是 context 的一个子集或一种特定角色；context 的外延更宽，包含任何在生成前进入模型视野的材料。幻灯片随后指出“prompt 可以塑造模型行为”，以及“LLM 可以通过迭代尝试写出高质量 prompt”。这三句话构成了从 prompt 到 context 的过渡：一旦承认“迭代尝试”有效，优化对象就不必局限于那段人为撰写的指令。

### 2.2 从 Prompt Optimization 到 Context Optimization

幻灯片引用了两条线索：

- Zhou et al., *Large Language Models are Human-Level Prompt Engineers* (ICLR 2023)，页面标签为 “Automated prompt engineer”。
- Zhang et al., *Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models* (ICLR 2026)。

幻灯片对后者的文字表述是：**可以构建一个 agentic system，在每次解决一个问题时更新有用的 context**。这提示了一个视角转换（解释）：优化不再是“离线找一段最好的指令”，而是“在线地、随任务积累地演化上下文”。注意：第 10、11 页除标题与引文外无可提取正文，图中所示的具体架构（例如上下文的组成部件、更新触发条件）在本次提取中缺失，**不确定**，不应据图臆测。

### 2.3 Propose–Evaluate–Refine 作为统一回路

幻灯片第 13 页提出本周的核心设问：我们已用 LLM 优化 prompt，能否用同一个 **propose–evaluate–refine** 回路去优化别的东西？

围绕这一回路，幻灯片给出了多种“评价信号来源”的变体：

| 方法线索 | 评价信号来源 | 幻灯片标注的出处 |
|---|---|---|
| Self-Refine | 模型自身的反馈 | Madaan et al., NeurIPS 2023 |
| LLM as Optimizers（如 OPRO 一类） | 外部 scorer 的反馈 | Yang et al., ICLR 2024 |
| Re3 | （写作场景的迭代改写） | Yang et al., EMNLP 2022 |
| Meta-Harness | （agent harness 的端到端优化） | Lee et al., arXiv 2026 |
| MatPlotAgent | （科学数据可视化） | Yang et al., Findings of ACL 2024 |
| Idea2Img | （图像生成的自反思） | Yang et al., ECCV 2024 |
| VISTA | （视频生成的测试时自改进） | Do et al., arXiv 2025 |

幻灯片列举的优化对象依次为：writing、agent harness、data visualization、image generation、video generation。可以归纳出一条共同结构（解释）：**被优化的对象从“文本指令”扩展为“程序/工件/流程”，而 evaluate 环节则由 scorer、模型自评或多模态反馈承担**。需要强调的是，括号中的场景描述来自幻灯片标题；各方法内部的具体算法细节在提取文本中不可见，属于**不确定**区域。

### 2.4 科学发现作为优化问题

幻灯片第 23–24 页把问题推进到 scientific discovery，并给出两个具体成果（幻灯片明确列出的数字应视为幻灯片内容，而非本笔记的实验结论）：

1. 在**八个维度**上发现了新的 **cap set** 构造，将记录从 **496 提升到 512**。
2. 发现了在测试基准上**优于标准基线**的 **bin-packing** 启发式。

第 25 页仅有标题与引文线索，图示内容缺失。这两个案例是 FunSearch 的经典落点，其共同特征是：**候选解可以被程序化地评分**——这一点是后面所有讨论的前提。

### 2.5 两个问题的定义（幻灯片原文要点）

**Cap set problem**：从 $\{0,1,2\}^n$ 中最多能选多少个点，使得其中不含三个不同的共线点？

- 在 8 维情形下，每个点是八元向量，如 $(0,2,1,0,1,2,2,0)$。
- 目标是在 $\{0,1,2\}^8$ 的 **6,561** 个点中尽可能多选，且不含三个不同的共线点。

**Bin-packing problem**：如何把不同大小的物品装入最少的箱子，且不超出任何箱子容量？

- 例：箱子容量 10，物品 6, 5, 3, 2, 2, 2；一个合法装法用 3 个箱子：$[6,3]$, $[5,2,2]$, $[2]$。
- **Online** bin packing：物品逐个到达，必须立即放置。

（解释）这两个问题的对比很有教学价值：cap set 是纯组合搜索、评分清晰；online bin packing 带有**顺序决策**与**不可回退**的约束，更接近现实调度。二者共同点是都能写成一个可执行、可打分的程序，因而适配 FunSearch 的框架。

### 2.6 FunSearch 的三个设计要素

**（1）Black-box optimization 的定位**（第 27 页标题）。幻灯片未展开定义，仅以标题给出定位；结合后文可整理为：优化器不假设目标函数的可微性或解析形式，只通过“候选 → 评分”的接口工作。**具体评分函数形式在提取中缺失，不确定**。

**（2）Search space**（第 28 页，内容较完整）：

- 定义：search space 是优化器可探索的候选集合。
- FunSearch **在具有给定输入输出格式的 Python 函数上搜索**。
- cap sets：`priority(element, n)` 用于排序“下一个加入哪个向量”。
- bin packing：`heuristic(item, bins)` 用于排序“把物品放在哪里”。
- **输出是一个可复用的、构造解的 program**。

这一点的意义值得单独强调（解释）：FunSearch 不直接搜索“解”（一个具体的点集或一种装箱方案），而是搜索**产生解的启发式函数**。这使得搜索空间从指数级的离散对象，压缩为“人类可读、可复用的程序”空间，也让评分与迁移都变得可行。

**（3）Evolutionary algorithms**（第 30–31 页）：

- 进化算法通过反复的 **selection、variation、evaluation** 改进一个 population。
- FunSearch **用 LLM 生成被采样程序的变体**。

即：variation 算子由 LLM 承担，而非传统的高斯扰动或交叉。这是“LLM 进入进化回路”的关键接口。

**（4）Programs pool 与 exploration**（第 32 页，条目最完整）：

1. 用 seed program 初始化每个 island；
2. 在每个 island 内增长 population：
   - a. 从该 island 现有程序中采样 parents；
   - b. 生成 child program 并加入同一 island；
3. 移除表现较差的 island。

（解释）island 模型的作用可理解为**多样性保护**：不同 island 独立演化，避免整个种群过早收敛到单一程序族；淘汰低效 island 则回收预算。注意第 33 页仅有页码、无可提取正文，**该页内容不确定**，不应把 island 数量、采样策略细节等当作已知。

### 2.7 AlphaEvolve 的四维变化

第 34 页以对照形式给出 AlphaEvolve 相对前作的变化，并附 DeepMind 博客链接（此处仅记录链接存在，不访问）：

| 维度 | 变化方向 |
|---|---|
| Search scope | Single-function → Full-program evolution |
| Edit mode | SEARCH/REPLACE diffs |
| Models | 更强的 LLM，配合更丰富的 context 与 feedback |
| Objectives | Single-metric → Multi-metric optimization |

（解释）这四点可以读作对 FunSearch 局限的直接回应：单函数搜索难以表达跨函数的整体设计；整体重写代价高，因此改用 diff 式局部编辑；更强模型提供更好的变异质量；单指标评分易被“刷分”，多指标则更接近真实工程目标。以上为整理性解读，幻灯片本身只给出对照表。

### 2.8 Autoresearch 与闭环实验

第 35 页：一个 AI agent 依照 `program.md` 提出想法、编辑代码、运行实验，在**固定算力预算**下改进语言模型预训练；幻灯片给出的规模描述为“每次实验 5 分钟、一晚约 100 次实验”。此处数字为幻灯片陈述，本笔记未做核验。

第 36 页以设问形式提出“还有哪些问题可以 ‘autoresearch’”，第 37 页引用 EdgeBench（Zhu et al., 2026），标题涉及“从真实环境学习的 scaling laws”。**第 36–37 页的图示与具体结论在提取中缺失，不确定**。

### 2.9 OpenEvolve 与 HW1 预告

第 38 页标题为 “OpenEvolve Deep Dive - HW1 preview”，并给出一个 Colab 作业链接。按本笔记的约束，此处**不推断作业内容、不虚构作业要求**；仅记录：本周幻灯片包含一次以 OpenEvolve 为主题的作业预告，具体任务以官方作业页面为准。

### 2.10 验证问题

第 39 页给出一个关键限定：**许多发现并没有数值 grader**。幻灯片列举的领域与发现为：生物学（CRISPR 基因编辑）、物理学（广义相对论）、化学（青霉素的发现）、天文学（暗物质）、地质学（板块构造）、医学（mRNA 疫苗）、计算机科学（反向传播）。

第 40–42 页转向“LLM 能否产生新颖研究想法”与 “AI Scientist”：

- Si et al., *Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers* (ICLR 2025)。
- Lu et al., *Towards End-to-End Automation of AI Research*, Nature 651, 914–919 (2026)。第 41、42 页均引此文，正文不可提取，**其流程图与阶段划分不确定**。

第 43–46 页集中讨论 verification：

- DeepSeek-V3 **把原定理分解为子目标**；DeepSeek-Prover-V2-7B **尝试在 Lean 中证明这些子目标**（Ren et al., 2025）。
- 第 44 页无可提取正文，**不确定**。
- 第 45 页引用 Anthropic 关于形式化费马大定理的博客（仅记录出处）。
- 第 46 页为一个视频片段链接（仅记录存在，不访问、不描述其内容）。

（解释）这一组材料共同指向一个论点：**当评价信号可以被形式化验证（如 Lean 证明检查）时，LLM 驱动的搜索才具备可靠的 refine 依据**；反之，评价退化为人工判断或代理指标，回路的可靠性随之下降。

---

## 三、方法比较

以下比较表**仅基于幻灯片可提取的文字**，空白或标注“不确定”处表示提取中缺少依据。

| 方法/线索 | 优化对象 | 变异/提议来源 | 评价信号 | 幻灯片给出的规模或结果 |
|---|---|---|---|---|
| Automated prompt engineer (Zhou et al. 2023) | prompt | LLM 迭代尝试 | 任务表现（细节不确定） | 未给出 |
| Agentic Context Engineering (Zhang et al. 2026) | context（随解题更新） | agentic system | 不确定（图示缺失） | 未给出 |
| Self-Refine (Madaan et al. 2023) | 模型输出 | 模型自身 | 模型自反馈 | 未给出 |
| LLM as Optimizers (Yang et al. 2024) | 候选解 | LLM | 外部 scorer | 未给出 |
| Re3 / MatPlotAgent / Idea2Img / VISTA | 故事 / 可视化 / 图像 / 视频 | LLM 自反思 | 多模态或任务反馈（细节不确定） | 未给出 |
| Meta-Harness (Lee et al. 2026) | agent harness | 端到端优化 | 不确定 | 未给出 |
| **FunSearch** | **Python 函数（启发式）** | **LLM 生成程序变体** | **程序评分 + 进化选择** | **cap set 496→512（8 维）；bin-packing 优于基线** |
| **AlphaEvolve** | **完整程序** | **LLM + SEARCH/REPLACE diff** | **多指标** | 未给出 |
| Autoresearch (Karpathy repo) | 预训练代码/方案 | agent 依 `program.md` | 固定算力预算下的实验结果 | 5 min/实验，约 100 实验/晚 |
| DeepSeek-Prover-V2 | 定理证明 | 子目标分解 + Lean 证明尝试 | Lean 形式验证 | 未给出 |

横向读出的三点（解释）：

1. **变异算子的演化**：从“模型改写文本”到“模型改写程序”，再到“模型做 diff 式局部编辑”，编辑粒度与可验证性同步细化。
2. **评价信号的谱系**：自反馈 → 外部 scorer → 多指标 → 形式化验证。越靠右，回路越可信，但适用域越窄。
3. **对象层级的抬升**：prompt → context → 单函数 → 整程序 → 实验流程（autoresearch）。每抬升一级，“可复用性”增强，而“可评分性”难度上升。

---

## 四、局限与不确定性

### 4.1 幻灯片明确提出的 open challenges（第 47 页）

1. **Distribution shift from ultra-long contexts**：随着 context 长度增长，模型行为如何改变？优化/发现方法在这种诱导出的分布偏移下有多稳健？
2. **Genuine discovery beyond verifiable domains**：当正确性或进展无法被自动评估器轻易验证时，LLM 能否产生真正新颖的发现？
3. **Faster Adaptation**：模型能否从更少的实验中学习有用的设计原则，从而在更小的实验预算下做出更好的决策与设计？

（解释）这三条恰好对应本讲的三层结构：第 1 条针对 context 本身的可扩展性；第 2 条针对 FunSearch 类方法的“可评分”前提；第 3 条针对进化/搜索类方法的样本效率。它们不是并列的清单，而是从“输入侧—评价侧—预算侧”对同一回路的三面夹击。

### 4.2 方法内在局限（整理，非幻灯片原文）

- **可评分性假设**：FunSearch 与 AlphaEvolve 的整个回路依赖自动评分；第 39 页的历史发现清单正是反例集合。
- **搜索空间的表达瓶颈**：FunSearch 限定“给定输入输出格式的 Python 函数”，这既是可评分性的来源，也是表达力的上限（解释）。
- **评分工件与真实目标的错位**：单指标易被优化到指标本身；AlphaEvolve 转向 multi-metric 可视为对此的缓解，但幻灯片未给出其效果证据。
- **预算敏感性**：autoresearch 的“固定算力预算”意味着结论强依赖预算设定；幻灯片未讨论预算外推。

### 4.3 本次提取的不确定性清单（重要）

为避免把 OCR 缺失当作论证，明确列出**不可用**的部分：

- 第 6 页正文在项目符号后中断；第 33 页仅页码。
- 第 10、11、25、37、44 页：标题/引文可见，图示内部结构与文字**缺失**。
- 第 41、42 页 AI Scientist 的流程细节**缺失**。
- 第 46 页视频内容**未知**。
- 各方法的算法伪码、超参数、实验数值，除幻灯片明确写出的（496→512、6,561 点、容量 10 的例子、5 分钟/约 100 次实验）外，**均未提供**。
- 所有参考文献仅按幻灯片给出的作者、标题、会议/期刊与年份记录；本笔记**未核验**其内容与页码信息的准确性。

---

## 五、复习清单

**概念自检**

- [ ] 用一句话分别定义 context 与 prompt，并说明二者的包含关系。
- [ ] 解释为什么“迭代尝试写 prompt”会自然导向“context optimization”。
- [ ] 写出 propose–evaluate–refine 回路的三步，并各举一个幻灯片中的方法作为该步的实例。
- [ ] 说明 FunSearch 搜索的是“解”还是“产生解的程序”，并解释这一选择带来的两个好处。

**机制自检**

- [ ] 复述 FunSearch 的 island 流程三步（初始化、增长、淘汰），并说明 island 结构可能的作用。
- [ ] 说明进化算法中 selection / variation / evaluation 分别由什么承担，其中哪一步由 LLM 完成。
- [ ] 列出 AlphaEvolve 的四个变化维度，并为每个维度说出一个“它回应了什么局限”的猜想（标注为猜想）。
- [ ] 解释 cap set 问题的定义与 8 维下的规模（6,561），以及 496→512 的含义。
- [ ] 解释 online bin packing 与普通 bin packing 的区别，并说明为何它更适合用启发式函数表达。

**边界自检**

- [ ] 说出“许多发现没有数值 grader”的至少四个例子。
- [ ] 说明 DeepSeek-Prover-V2 线索中子目标分解与 Lean 证明的分工。
- [ ] 用自己的话复述三项 open challenges，并把每项对应到本讲中的某一方法假设。

**元认知自检**

- [ ] 指出本笔记中哪三处是“解释”而非“幻灯片内容”。
- [ ] 列出至少三处因提取缺失而**不能**下结论的地方。
- [ ] 若要把 FunSearch 用于一个你熟悉的领域，先回答：该领域的候选解能否写成可自动评分的程序？若不能，缺的是评分还是表达？

---

## 六、官方幻灯片来源

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec3%20-%20llm%20optimizers.pdf
