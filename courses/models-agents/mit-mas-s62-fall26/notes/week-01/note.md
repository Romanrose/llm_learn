# MIT MAS.S62 · Self-Evolving AI（Fall 2026）Week 01 学习笔记

> **说明**：本笔记基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。以下内容严格依据提供的官方幻灯片抽取文本，不把页面重复、页码或 OCR 失真当作论证。幻灯片中的图表多数以图片形式存在，抽取文本未能还原图内信息，相关处已明确标注不确定性。英文术语保持原样。

---

## 一、课程基本信息

- 课程标题（幻灯片）：**How to AI an AI for Almost Anything**，Lecture 1 - Introduction。
- 主讲：**Paul Liang**，Assistant Professor，MIT Media Lab & MIT EECS。
- 教学团队（幻灯片标注为 Spring 2026）：Paul Liang（Course instructor）、Ao Qu（Teaching Assistant）。
- 课程网站：https://mit-mi.github.io/how2ai-course/fall2026/
- 提交平台：Canvas（https://canvas.mit.edu/courses/40521/）

> 注意：幻灯片第 6 页标题写的是 "Your Teaching Team, Spring 2026"，而课程本身标注为 Fall 2026。这可能是幻灯片沿用了旧学期模板，也可能是课程跨学期安排；幻灯片未作解释，此处保留不确定性，不作推断。

---

## 二、学习目标（Learning Objectives）

幻灯片列出的四条官方学习目标：

1. **Study recent technical achievements in AI research**——研究 AI 研究中的近期技术成果。
2. **Improve critical and creative thinking skills**——提升批判性与创造性思维。
3. **Understand future research challenges in AI**——理解 AI 未来的研究挑战。
4. **Explore and implement new research ideas in AI**——探索并实现新的 AI 研究想法。

**解释（非幻灯片原文）**：这四条目标呈现明显的"研究导向"而非"知识传授导向"：课程不是让学生复述技术，而是要求学生读论文、做批判、找问题、动手实现。第 4 条"implement"与后文 40% 的研究项目评分相呼应，说明课程的核心产出是研究能力而非考试成绩。

### 先修要求（Preferred Pre-requisites）

幻灯片用 "Preferred" 而非 "Required"，列出：

1. Knowledge of AI programming and experimentation（AI 编程与实验知识）；
2. Understanding of modern AI capabilities & limitations（理解现代 AI 的能力与局限）；
3. Bring external (non-AI) domain knowledge about your problem（自带非 AI 的领域知识）；
4. **Bonus**：worked on self-evolving AI, AI for discovery, etc.（有 self-evolving AI、AI for discovery 等经验者加分）。

**解释**：第 3 条值得注意——课程明确鼓励学生把外部领域知识带入问题，这与后文 "Self-Evolving AI for Science and Engineering"、"for Personalization"、"for Multimodal & Embodied World" 等应用方向一致，暗示课程期待学生做"AI × 领域"的研究，而非纯 AI 方法论研究。

---

## 三、课程形式与评分结构

### 授课形式（Course delivery format）

- 每周三 2 小时课，2–4pm。
- 课外 homework 与 reading assignments，周期约 2 周。
- 课外有**significant research project**，需要报告与展示。

### 评分概览（Grading Overview）

| 组成部分 | 权重 | 细节 |
|---|---|---|
| Homework assignments | 40% | 4 次，每次约 2 周 |
| Reading assignments | 20% | 4 次，覆盖 multimodal AI 的 state-of-the-art 研究，与 homework 同步发布，课上讨论/展示 |
| Research project | 40% | 其中 proposal with literature review 10%、midterm progress report 10%、final report and presentation 20% |

> **注意一处幻灯片内部不一致**：第 19 页 "Absences and Late Submissions" 写道 "Course participation and in-class discussions are a graded component (20%)"，而第 14 页评分概览中 20% 对应的是 reading assignments，并未单列 participation。两处表述是否指同一项、还是评分结构另有调整，幻灯片未说明。此处保留不确定性，不代为调和。

### 作业与阅读的具体安排

**Homework Assignments**（幻灯片标注 "Tentatively"，即暂定）：

- **HW 1，due week 4：Context evolution**。暂定涉及 prompt optimization（TextGrad）与用 LLM 做优化（OpenEvolve）。
- **HW 2，due week 7：Harness evolution**。暂定涉及 skill evolution（SkillOpt）与 self-generating harness（Meta-Harness）。
- **HW 3，due week 10：Model evolution**。暂定涉及 test-time training 与 continual learning 方法。
- **HW 4，due week 12：Task evolution**。暂定涉及 self-generating tasks，并在 PostTrainBench 上"putting everything together"。

**Reading Assignments**：

- 4 次，通常 2 篇 required papers 加若干 suggested（optional）papers，配 5–6 个 discussion probes。
- 三部分任务：
  1. **Reading notes**：读指定论文并总结 main take-away points；可选地提出澄清问题。
  2. **Paper scouting**：围绕 question probes 搜寻额外论文、博客或其他资源。
  3. **Discussion points**：反思 question probes，准备讨论点，课上 live discussion 与 brainstorming。
- 目标：把每次讨论汇总，**jointly write a survey paper on self-evolving AI**，聚焦清晰的 taxonomy 与严谨的新方向。

**解释**：reading assignment 的最终产出是一篇合作 survey paper，这一点把"读论文"从个人作业变成了集体知识建构，与课程"研究导向"的定位一致。同时，survey 强调 "clear taxonomy"，呼应了课程用"Perspective 1/2/3"组织领域的方式（见后文）。

### 课程项目（Course Project）

- 目的：介绍研究过程，包括 reading literature、熟悉应用领域、尝试 state-of-the-art models、做 error analysis、开发与迭代新方法、评估与分析结果。
- 分组：2–4 人。
- 每组分配一位 mentor。
- 通过 regular updates、presentations、GitHub 追踪 equal contribution。

**项目时间线**：

| 时间 | 事项 |
|---|---|
| Week 2 | Project preferences：选定队友，对 dataset 与 task 有初步想法 |
| Week 4 | Proposal report + presentation：literature review 与研究想法 |
| Week 5 | 搭建 datasets 与 baselines |
| Week 7 | Midterm report + presentation：baselines 与新想法的结果 |
| Week 10 | 研究想法的更新结果、分析、ablations |
| Week 13 | Final presentations：描述探索过的研究想法、结果、分析、讨论 |
| Week 14 | Final report |

### 缺勤与迟交（Absences and Late Submissions）

- 期望学生到课；若计划缺课超过一次，应尽快告知。
- Homework 与 reading assignment 有 **wildcards（2 per student）**：24 小时延期，每次作业最多用 1 个。
- Project report 有 **wildcards（2 per team）**：可用于 proposal、midterm 或 final report，24 小时延期，可叠加使用。

### 选课说明（Assignments for This Coming Week）

- 本周通知选课状态；for-credit enrollment 上限 20–30 人。
- Listeners 欢迎参加 lectures、discussions 与 course projects（若投入），但空间与资源有限。
- Project preference form 本周发布：暂定队友名单、暂定方向与任务。

---

## 四、课程主题模块（Lecture Topics）

幻灯片声明主题 "subject to change, based on student interests and course discussions"。四个模块构成一条从"上下文"到"环境"的演化链条：

**Module 1: Context evolution**
- Week 2（9/16）：Prompt optimization, memory, tools, knowledge
- Week 3（9/23）：LLMs as optimizers for discovery
- Week 4（9/30）：Project proposal presentations

**Module 2: Harness evolution**
- Week 5（10/7）：Harness components, multi-agent systems
- Week 6（10/14）：Self-evolving harnesses
- Week 7（10/21）：Project midterm presentations

**Module 3: Model evolution**
- Week 8（10/28）：Continual learning, distillation, test-time training
- Week 9（11/4）：Self-play approaches

**Module 4: Environment evolution**
- Week 10（11/11）：Synthetic data and tasks, environment generation
- Week 11（11/18）：World models, evolving evaluation and rewards
- Week 12（11/25）：Future topics – AI for discovery, multimodal agents
- Week 13（12/2）：Project final presentations
- Week 14（12/9）：Future topics – Embodied harnesses, safe evolution（NeurIPS）

> **不确定性说明**：幻灯片中 Module 1 的 Week 3 页面旁有零散的 "𝑦" 符号，Module 2 页面旁有 "An armchair in the shape of an avocado" 文字，Module 3 页面旁亦有 "𝑦"。这些疑似是幻灯片配图或示例 prompt 的残留文本，抽取后失去上下文，无法判断其确切用途。此处如实保留，不强行解释为课程内容。

**解释**：四个模块的命名——context → harness → model → environment——本身就是一个分析框架：self-evolving AI 可以演化的对象层次由外到内、再由内到外。Context 是最外层的输入组织，harness 是模型外的 agent 系统，model 是权重本身，environment 是任务与评估的来源。这一分层在后文 "Perspective 1: What is being evolved?" 中被再次使用，并与具体论文一一对应（FunSearch 演化 math programs、Meta-Harness 演化 harness、Absolute Zero 演化 model weights 与 tasks）。

---

## 五、从语言模型到自主 agent：六年进展（背景脉络）

幻灯片用一条时间线回顾 2020–2026 的进展，每一页均附有对应论文或产品作为出处。

- **2020 In-Context Learning**：GPT-3 在大规模无监督预训练后展现 zero-shot 与 few-shot 任务适应能力（Brown et al., OpenAI, 2020）。随后一页 "Few-Shot Prompting (GPT-3)" 重复强调同一结论。
- **2022 Instruction following**：instruction tuning 与 RLHF 使 LLM 更好地遵循用户指令（Ouyang et al., OpenAI, 2022）。对比页说明：同一 prompt 下，GPT-3 继续续写文本，而经过 supervised fine-tuning 与 RLHF 的 InstructGPT 会回答问题。
- **2022 Chain-of-thought reasoning**：CoT prompting 激发大模型的多步推理（Wei et al., Google Research, 2022）；零样本场景下简单 prompt 也可引出 CoT（Kojima et al., University of Tokyo & Google Research, 2022）。
- **2023 Reasoning and acting**：ReAct 让 LLM 交错进行推理、工具使用与环境交互（Yao et al., Princeton & Google Research, 2022）。幻灯片描述："Each thought guides the next search. Each observation motivates the next thought."
- **2024–2025 RL-trained reasoning**：强化学习提升复杂推理，并使模型能从额外的 test-time computation 中获益（DeepSeek-R1, DeepSeek-AI, 2025）。幻灯片特别指出：模型仅用 correctness reward 训练，"Re-checking its own steps appeared during RL training and was not written into the prompt"——即自我检查行为是 RL 训练中涌现的，而非 prompt 写死的。另有 GRPO 页：去掉 PPO 的 value network，通过同一 prompt 下的一组 rollouts 的奖励比较来估计 advantage（DeepSeekMath, Shao et al., 2024）。以及 OpenAI "Learning to Reason with LLMs"（2024 年 9 月）。
- **2025 Multi-turn Agentic Reasoning**：RL 从单轮响应推理扩展到复杂多轮交互（Search-R1, Jin et al., 2025；OpenAI Deep Research, 2025 年 2 月）。
- **2024–2026 Long-horizon model-harness agent systems**：harness 通过 context management、memory、tools、orchestration 让 agent 在长时程任务上持续取得进展（SWE-agent, Yang et al., Princeton, 2024；Claude Code demo, Anthropic, 2025 年 9 月）。幻灯片引用 Anthropic 材料称：Anthropic 每位贡献者写的代码量今年增长了八倍，Claude 撰写了 Anthropic 合并代码的约 80%（"When AI Builds Itself", Anthropic, 2026）。另有 METR 的 "Measuring AI Ability to Complete Long Software Tasks"（检索于 2026 年 9 月）。
- **2026 Automated Improvement Loops?**：连续三页引用 "When AI Builds Itself"（Anthropic, 2026）与 OpenAI "Research acceleration: The view inside OpenAI"（2026 年 9 月 6 日），标题带问号，呈现为"是否已出现自动化改进闭环"的开放问题。

> **不确定性说明**：上述时间线中多处引用 2026 年的文献与产品材料，且部分页面（如 METR、Anthropic 数据）以图片或引用形式呈现，抽取文本只保留了标题与少量文字。幻灯片未给出这些材料的完整上下文与数据细节，本笔记不补充、不推测具体数值含义。

**解释**：这条时间线的叙事逻辑是：能力从"预训练后的隐式适应"（in-context learning）→"对齐后的指令遵循"→"显式推理"→"推理与行动交错"→"RL 训练出的推理与自我检查"→"多轮 agentic 交互"→"model + harness 的长时程系统"→"自动化改进闭环？"。每一步都在为最后的问号做铺垫：当 agent 能长时程工作、能写大部分代码时，系统是否开始自己改进自己？这正是 self-evolving AI 的问题意识来源。

---

## 六、Self-Evolving AI 的历史脉络

幻灯片用六个节点勾勒历史：

1. **1965 Intelligence Explosion**：Irving John Good，英国数学家，二战期间在 Bletchley Park 与 Alan Turing 共事，战后在 University of Manchester 继续与 Turing 合作计算机设计与 Bayesian statistics。1965 年发表 "Speculations Concerning the First Ultraintelligent Machine"，提出由机器递归改进自身设计而驱动的 intelligence explosion 设想。幻灯片拆解其逻辑链：
   1. 机器具备设计机器的智力能力；
   2. 它用该能力设计更强的后继者；
   3. 后继者更擅长机器设计；
   4. 因此可贡献下一轮改进。
2. **2003 Godel Machines**：Jürgen Schmidhuber（IDSIA），"Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements"。核心：自指系统在能**证明**某项修改有益时修改自身代码。
3. **2017 AlphaGo Zero – Self-Play At Scale**：David Silver 等，Nature。AlphaGo 先模仿专家棋谱再做 RL；AlphaGo Zero 不依赖人类棋谱，通过重复 self-play 循环自我提升。
4. **2023 LLM-guided discovery**：FunSearch 把 LLM 生成的代码与自动评估结合进演化循环，发现新的 cap set 构造与改进的 bin-packing 启发式（Romera-Paredes et al., Google DeepMind, 2023）。幻灯片列出两个应用：Cap Set Problem、Online Bin Packing。
5. **2025 Self-Modifying Agent**：Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents（Zhang et al., 2025）。
6. **2026 Automated AI research**：autoresearch（Andrej Karpathy, GitHub repository, 2026）。幻灯片描述：AI agent 按 program.md 提出想法、改代码、跑实验，在固定 compute budget 下改进 language model pretraining；每次实验 5 分钟，一晚约 100 次实验。

**解释**：这条历史线的关键对照是"证明"与"经验"。Gödel Machine 要求可证明的改进，因而极其保守；FunSearch、Darwin Gödel Machine、autoresearch 则用"跑实验—看结果"的经验反馈替代证明，把可自我改进的范围从"可形式验证的代码"扩展到"任何可评估的程序与训练流程"。幻灯片没有明说这一对比，但从 2003 到 2023/2025/2026 的跳跃可以读出这一转向。此外，1965 的 intelligence explosion 是思想实验，2017 的 self-play 是封闭游戏域，2023 之后才进入开放任务域——这三段的历史条件差异也值得注意。

---

## 七、当今 Self-Evolving AI 的图景：三个视角

幻灯片用三个 Perspective 组织领域。

### Perspective 1: What is being evolved?（演化对象）

- **FunSearch**：被演化的是 **math programs**（Romera-Paredes et al., Google DeepMind, 2023）。
- **Meta-Harness**：被演化的是 **agent harness**（Yoonho Lee et al., 2026）。
- **Absolute Zero**：被演化的是 **model weights**（Zhao et al., 2025）；同一工作里 **tasks 也被演化**。

> **不确定性说明**：Perspective 1 下有多页仅含标题或图片，抽取文本中只保留了上述带标注的图注。幻灯片是否还列出其他演化对象（如 prompts、memory、skills），从抽取文本无法确认，此处不补全。

**解释**：这四个例子恰好对应课程四个模块——programs 近似 task/context 层面的产物，harness 对应 Module 2，model weights 对应 Module 3，tasks 对应 Module 4 的 synthetic data and tasks。也就是说，"What is being evolved" 与课程模块划分是同一套分类法的两种表述。

### Perspective 2: How is it being evolved?（演化机制）

- **A Model View**：幻灯片仅有标题，无抽取到的正文内容。
- **An Agent View**：列出三个例子——
  - RLHF（Ouyang et al., OpenAI, 2022）：人类反馈训练模型遵循指令；
  - Voyager（Wang et al., 2023）：开放式具身 agent，用 LLM 驱动；
  - Darwin Gödel Machine（Zhang et al., 2025）：自改进 agent 的开放式演化。

> **不确定性说明**："A Model View" 页在抽取文本中只有标题，没有任何内容。该页原本应有图表或文字说明"从模型视角看演化机制"的分类，但无法从输入中恢复。这是本笔记最主要的信息缺口之一，复习时应以课堂幻灯片原件为准。

**解释**：从仅有标题的两页结构看，幻灯片意图把"如何演化"分成 model view 与 agent view 两条线：前者关注权重/训练层面的更新机制，后者关注 agent 系统层面的行为与经验积累。Agent view 下的三个例子恰好是三种反馈来源——人类反馈（RLHF）、环境交互（Voyager）、自我修改（Darwin Gödel Machine）。这一解读基于标题与例子排列，属于解释而非幻灯片明文。

### Perspective 3: Relationships between big concepts（大概念之间的关系）

幻灯片列出三组关系，每组配一张图（图内文字部分可辨）：

- **AI for Discovery** —— 图注 "LILA Sciences / Discovery Loop"。
- **Continual Learning** —— 图注 "Oak Lab / Engram"。
- **AI for AI Research -> RSI** —— 图注 "Recursive Superintelligence / Mirendil"。

> **不确定性说明**：这三页的核心是关系图，抽取文本只保留了图注中的机构/项目名，图的节点与箭头关系无法还原。因此"AI for Discovery、Continual Learning、AI for AI Research (RSI) 三者如何相互关联"这一关键问题，本笔记无法依据输入回答。RSI 应为 recursive self-improvement 的缩写，但幻灯片未展开定义，此处仅标注缩写常见含义，不作论证。

---

## 八、研究想法与任务（Research Ideas and Tasks）

幻灯片按七个问题组织研究前沿，每个问题给出 Goal 与若干代表文献。以下逐一整理，文献标题与作者按幻灯片原文保留。

### 1. Can LLM learn taste and make genuine innovations?

**Goal**：从生成既有想法的合理变体，走向识别有价值的方向、产出真正新颖的发现。

- Si et al., 2024：Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers.
- Bo Jiang, 2026：HindSight: Evaluating Research Idea Generation via Future Impact.
- Tom Zahavy (Google DeepMind), 2026：LLMs Can't Jump.

**解释**：三篇文献分别对应三种评估路径——大规模人类研究、以未来影响回溯评估、以及（从标题看）对 LLM 能否跨越范式跳变的质疑。幻灯片只给标题，未给结论，不应推断哪篇支持哪种立场。

### 2. Can AI automate engineering optimization tasks? Can AI automate AI research itself?

**Goal**：让 agent 自主选择想法、运行实验、产出经过验证的研究发现。

- PaperBench: Evaluating AI's Ability to Replicate AI Research（Giulio Starace et al., OpenAI, 2025）。
- Learning to Discover at Test Time（Mert Yuksekgonul et al., Stanford & NVIDIA, 2026）。
- FrontierCS: Evolving Challenges for Evolving Intelligence（Qiuyang Mang et al., 2025）。
- CORAL: Towards Autonomous Multi-Agent Evolution for Open-Ended Discovery（Ao Qu, Han Zheng, Zijian Zhou et al., MIT & NUS, 2026）。
- EdgeBench: Unveiling Scaling Laws of Learning from Real-World Environments（Deyao Zhu et al., ByteDance Seed, 2026）。

**解释**：这组文献覆盖"评估基准"（PaperBench、FrontierCS、EdgeBench）与"方法"（Learning to Discover at Test Time、CORAL）两类。值得注意的是 CORAL 的作者含课程 TA Ao Qu，说明课程内容与教学团队自身研究直接相关——但这是从作者名单读出的事实，幻灯片未作此说明。

### 3. How to effectively turn experience into persistent knowledge?

**Goal**：把噪声大的交互轨迹转化为可复用、跨任务持久、且不累积错误或 catastrophic forgetting 的知识。

- ExpeL: LLM Agents Are Experiential Learners（Andrew Zhao et al., University of Maryland, 2024）。
- Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models（Qizheng Zhang et al., Stanford, 2025）。
- Self-Distillation Enables Continual Learning（Idan Shenfeld et al., MIT & Thinking Machines Lab, 2026）。
- Reinforcement Learning via Self-Distillation（Jonas Hübotter et al., ETH Zurich & Stanford, 2026）。
- Continual Learning Bench: Evaluating Frontier AI Systems in Real-World Stateful Environments（Asawa et al., 2026）。

**解释**：这组文献与 Module 3（continual learning, distillation）和 Module 1（memory, context）交叉。"experience → persistent knowledge" 的难点在 Goal 里写得很清楚：noisy、跨任务、不累积错误、不 catastrophic forgetting——四个约束同时成立才叫"持久知识"。

### 4. When should we update model weights, and when should we update the harness?

**Goal**：判断新学到的经验应内化进 model weights，还是外化为 prompts、memory、skills、tools 与 orchestration。

- GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning（Lakshya Agrawal et al., UC Berkeley & Stanford, 2025）。
- Meta-Harness: End-to-End Optimization of Model Harnesses（Yoonho Lee et al., 2026）。
- WHALE: A Simple Recipe for Joint Harness-Weight Optimization（Kim et al., KRAFTON, KAIST & Stanford, 2026）。
- Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory（Chhikara et al., Mem0, 2025）。

**解释**：这是全课最核心的架构性问题之一，直接对应 Module 2 与 Module 3 的交界。GEPA 的标题暗示 prompt 层面的演化可胜过 RL，Meta-Harness 与 WHALE 则把 harness 与 weights 放在同一优化框架里比较或联合优化。幻灯片未给出这些方法的实验结论，不应推断孰优孰劣。

### 5. How can we oversee increasingly autonomous systems?

**Goal**：当 agent 在长时程上运行、能力可能超过监督者、且可能学会利用或规避评估者时，保持有意义的人类控制。

- AI Safety via Debate（Geoffrey Irving, Paul Christiano, Dario Amodei, OpenAI, 2018）。
- Weak-to-Strong Generalization: Eliciting Strong Capabilities with Weak Supervision（Collin Burns et al., OpenAI, 2023）。
- Agentic Misalignment: How LLMs Could Be Insider Threats（Anthropic, 2025）。
- CoT Red-Handed: Stress Testing Chain-of-Thought Monitoring（Benjamin Arnav et al., Google DeepMind, 2025）。

**解释**：这组文献的时间跨度从 2018 到 2025，说明 oversight 问题不是新问题，但 Goal 的表述（"exceed their supervisors"、"exploit or circumvent their evaluators"）把它放到了 self-evolving 的语境下：当系统自己改进自己时，监督者与被监督者的能力差会扩大，弱监督强的问题从假设变成现实约束。

### 6. Self-Evolving AI for Science and Engineering

**Goal**：从模拟、实验与真实世界反馈中持续学习，加速科学发现与工程优化。

- GeneBench-Pro: Evaluating Multistage Statistical Reasoning in Genomics, Quantitative Biology, and Translational Biomedicine（Jeremy Li and Andrew Ho, OpenAI, 2026）。
- Coscientist: Autonomous Chemical Research with Large Language Models（Boiko et al., 2023）。
- AnalogAgent: Self-Improving Analog Circuit Design Automation with LLM Agents（Zhixuan Bao et al., 2026）。
- Autonomous Agents Coordinating Distributed Discovery Through Emergent Artifact Exchange（Wang et al., 2026）。

### 7. Self-Evolving AI for Personalization

**Goal**：从个体交互与反馈中持续学习，适应用户不断演变的需求、偏好与目标。

- Learning Personalized Agents from Human Feedback（Kaiqu Liang et al., 2026）。
- OpenClaw-RL: Train Any Agent Simply by Talking（Yinjie Wang et al., 2026）。
- MIRIX: Multi-Agent Memory System for LLM-Based Agents（Yu Wang and Xi Chen, 2025）。
- StuLife: Building Self-Evolving Agents via Experience-Driven Lifelong Learning（ECNU-ICALK, 2026）。

### 8. Self-Evolving AI for Multimodal & Embodied World

**Goal**：从多模态感知与物理交互中持续学习，在动态真实环境中适应知识、技能与行为。

- Self-Evolving Embodied AI（Tongtong Feng, Xin Wang, Wenwu Zhu, 2026）。
- Voyager: An Open-Ended Embodied Agent with Large Language Models（Guanzhi Wang et al., NVIDIA & Caltech, 2023）。
- Seeing, Listening, Remembering, and Reasoning: A Multimodal Agent with Long-Term Memory（Long et al., 2025）。

**解释**：后三组（Science/Engineering、Personalization、Multimodal & Embodied）对应 Module 4 的 "Future topics" 与第 14 周的 "Embodied harnesses"。它们共享同一结构：**领域反馈 → 持续学习 → 适应**。差别在反馈来源——实验设备、用户对话、物理世界。这也呼应了先修要求第 3 条"bring external domain knowledge"：没有领域知识，就无法判断这些反馈意味着什么。

---

## 九、方法比较：本讲给出的对照框架

幻灯片本身没有一张显式的"方法比较表"，但通过模块划分与三个 Perspective，实际提供了多组可比较的维度。以下比较是对幻灯片内容的**结构化整理与解释**，不是幻灯片原文表格。

### 维度一：演化对象（What is being evolved）

| 对象 | 代表工作 | 对应模块 |
|---|---|---|
| Math programs | FunSearch | Module 1/4 之间（程序即任务产物） |
| Agent harness | Meta-Harness | Module 2 |
| Model weights | Absolute Zero | Module 3 |
| Tasks | Absolute Zero | Module 4 |

**比较要点**：越靠"外"（programs、harness），反馈信号越容易获得、迭代成本越低；越靠"内"（weights），改变越持久但成本越高、越难回滚。幻灯片未明说这一权衡，但模块顺序（context → harness → model → environment）与第 4 个研究问题（weights vs harness）都指向同一张力。

### 维度二：演化机制（How is it being evolved）

| 机制 | 代表工作 | 反馈来源 |
|---|---|---|
| 人类反馈 + RL | RLHF | 人类偏好 |
| 环境交互 + 技能积累 | Voyager | 环境 |
| 自我修改 + 开放式演化 | Darwin Gödel Machine | 自身代码与评估 |

> 该表依据 Perspective 2 "An Agent View" 页的三条文献整理；"A Model View" 页内容缺失，故机制维度不完整。

### 维度三：改进的保证方式

| 方式 | 代表 | 特点 |
|---|---|---|
| 可证明的改进 | Gödel Machines (2003) | 修改前需证明有益，范围受限于可形式化验证的对象 |
| 经验验证的改进 | FunSearch (2023)、Darwin Gödel Machine (2025)、autoresearch (2026) | 靠自动评估/实验反馈筛选，范围广但无保证 |

**解释**：这一对照是本讲历史部分最重要的分析线索，但幻灯片未以表格形式呈现，属于从相邻页面推断的结构。复习时应注意区分"幻灯片明说的"（各工作的定义与年份）与"本笔记推断的"（两者构成保证方式的两极）。

### 维度四：经验内化的位置

| 位置 | 代表 | 持久性/成本 |
|---|---|---|
| Prompts / context | GEPA、Agentic Context Engineering | 易改、易失 |
| Memory / skills / tools（harness） | Meta-Harness、Mem0、ExpeL | 中等 |
| Model weights | Self-Distillation、continual learning 方法 | 持久、成本高 |

**解释**：此表综合了研究问题 3 与 4 的文献，是"何时更新 weights、何时更新 harness"这一问题的方法学展开。幻灯片只给文献标题与 Goal，未给性能对比，故表中"持久性/成本"一列是概念性描述，不是实验结果。

---

## 十、局限与不确定性

依据输入，明确列出以下局限：

1. **图表信息缺失**。幻灯片大量内容以图片呈现（时间线配图、Perspective 关系图、各工作的示意图、AlphaGo Zero 与 autoresearch 的流程图等），抽取文本只保留了标题、图注与少量文字。凡涉及图内结构、箭头关系、数据曲线的判断，本笔记均未作出。
2. **"Perspective 2: A Model View" 页无内容**。这是结构性缺口，导致"如何演化"的模型视角无法整理。
3. **"Perspective 3" 三页仅为图注**。AI for Discovery、Continual Learning、AI for AI Research (RSI) 三者的关系图无法还原，本笔记只能列出图注中的机构/项目名。
4. **零散符号无法解释**。Module 1 与 Module 3 页面旁的 "𝑦"、Module 2 页面旁的 "An armchair in the shape of an avocado"，疑似配图或示例 prompt 残留，抽取后失去上下文，本笔记未强行赋予含义。
5. **评分结构存在内部不一致**。第 14 页 grading overview 与第 19 页 participation 20% 的表述不一致，幻灯片未说明，本笔记未代为调和。
6. **学期标注不一致**。第 6 页写 "Spring 2026"，课程为 Fall 2026，原因未知。
7. **2026 年文献与材料无法核验**。时间线与研究前沿中大量引用 2026 年的论文、产品与博客（如 "When AI Builds Itself"、"Research acceleration: The view inside OpenAI"、autoresearch、Meta-Harness、WHALE 等），幻灯片只给标题与出处，本笔记不补充其内容、结论或数值。
8. **所有作业均为 "Tentatively"**。HW 1–4 的具体内容幻灯片明确标注暂定，可能随课程讨论调整。
9. **文献结论未给出**。研究想法部分每篇文献只有标题与作者，幻灯片未陈述其发现，本笔记不做推断。
10. **本笔记非课堂记录**。课堂口头讲述、板书、现场讨论、Q&A 均未纳入；幻灯片声明主题 "subject to change, based on student interests and course discussions"，实际授课内容可能与本笔记所列不同。

---

## 十一、复习清单

### A. 事实性记忆（幻灯片明示）

- [ ] 课程全名、主讲人、TA、课程网站与 Canvas 链接。
- [ ] 四条 Learning Objectives 的原文表述。
- [ ] 四条 Preferred Pre-requisites，特别是第 3 条与 Bonus 条。
- [ ] 评分结构：40% homework（4 次）、20% reading（4 次）、40% project（10/10/20）。
- [ ] 四个模块的名称与对应周次：Context / Harness / Model / Environment evolution。
- [ ] HW 1–4 各自对应的模块与暂定主题（Context / Harness / Model / Task evolution）。
- [ ] Reading assignment 的三部分：reading notes、paper scouting、discussion points；最终目标是 jointly write a survey paper。
- [ ] Project 时间线的七个节点（Week 2/4/5/7/10/13/14）。
- [ ] Wildcards 规则：学生 2 个（每次作业最多 1 个，24 小时）；团队 2 个（可叠加）。
- [ ] 选课上限 20–30 人；listeners 的政策。
- [ ] 时间线八个节点：2020 in-context learning、2022 instruction following、2022 CoT、2023 ReAct、2024–2025 RL-trained reasoning、2025 multi-turn agentic reasoning、2024–2026 long-horizon model-harness systems、2026 automated improvement loops?
- [ ] 历史六个节点：1965 intelligence explosion（I. J. Good）、2003 Gödel Machines（Schmidhuber）、2017 AlphaGo Zero（Silver）、2023 FunSearch（DeepMind）、2025 Darwin Gödel Machine、2026 autoresearch（Karpathy）。
- [ ] Perspective 1 的四个演化对象及其代表工作：math programs / FunSearch；harness / Meta-Harness；model weights / Absolute Zero；tasks / Absolute Zero。
- [ ] Perspective 2 Agent View 的三个例子：RLHF、Voyager、Darwin Gödel Machine。
- [ ] 七个研究问题各自的 Goal 表述与至少两篇代表文献。

### B. 概念理解（需能用自己的话解释）

- [ ] 为什么课程用 context → harness → model → environment 的顺序组织模块？这一顺序与"演化对象"分类是什么关系？
- [ ] "What is being evolved" 与 "How is it being evolved" 两个视角分别回答什么问题？为什么需要两个视角而不是一个？
- [ ] Gödel Machine 的"可证明改进"与 FunSearch/autoresearch 的"经验验证改进"在保证性与适用范围上有何差别？
- [ ] DeepSeek-R1 页面所说"自我检查行为在 RL 训练中出现、并非写入 prompt"意味着什么？它对"self-evolving"的定义有何启示？
- [ ] "When should we update model weights, and when should we update the harness?" 这一问题的两端各自的风险是什么（从幻灯片给出的 Goal 与文献标题出发）？
- [ ] "Turn experience into persistent knowledge" 的四个约束（noisy、跨任务、不累积错误、不 catastrophic forgetting）分别对应哪些方法类别？
- [ ] 为什么 oversight 问题在 self-evolving 语境下比在普通 LLM 语境下更尖锐？Goal 中的三个条件分别指什么？
- [ ] Reading assignment 最终要合写 survey paper，这对"taxonomy"提出了什么要求？与课程的 Perspective 分类有何呼应？

### C. 辨析与批判（幻灯片未给答案，需自行判断）

- [ ] 幻灯片中 "2026 Automated Improvement Loops?" 标题带问号——这个问号是修辞还是真实的不确定性？依据是什么？
- [ ] 时间线从 1965 到 2026 的叙事是否构成"进步史"
