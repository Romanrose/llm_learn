# 自我进化的 AI：MIT MAS.S62 第一讲课程导览

> **说明**：本文基于 MIT MAS.S62 · Self-Evolving AI（Fall 2026）week-01 官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。文中区分"幻灯片陈述的内容"与"笔者对幻灯片结构的解读"，凡幻灯片图表信息在文本抽取中缺失者，均明确保留不确定性。不虚构课堂对话、实验数值、作业要求与参考文献，所有课程安排以幻灯片原文为准，实际执行可能调整。

---

## 一、这门课要回答什么问题

课程标题幻灯片给出的正式名称是 **"How to AI an AI for Almost Anything"**，主讲人为 MIT Media Lab 与 MIT EECS 的 Paul Liang 助理教授，助教为 Ao Qu。课程官网与 Canvas 提交入口在幻灯片中均有给出（见文末）。

从页面组织看，第一讲承担三重任务：课程行政信息（教学目标、先修要求、交付形式、评分、作业、项目时间线、缺勤与迟交政策）、技术背景（从语言模型到自主智能体的六年进展、自我进化 AI 的历史与当下爆发原因、当下图景的三种观察视角），以及研究议程（一系列开放研究问题与相关文献）。幻灯片末尾列出本周作业：选课状态通知（学分注册上限 20–30 人，旁听者在有热情的前提下欢迎参加讲座、讨论与课程项目，但空间与资源有限），以及本周发布的项目偏好表（初步队友名单、初步方向与任务）。

需要强调：以上均为幻灯片文本所述，本文不对其做任何补充或承诺性解读。

---

## 二、课程定位：从"用 AI"到"让 AI 进化 AI"

幻灯片第 2–4 页给出了课程的时代背景。第 2 页引用一句关于内部模型团队"用约 10,000 个协作 AI 智能体在 88 小时内得到 Navier–Stokes 解"的说法——这属于幻灯片引述的外部主张，本文仅转述其存在，不为其真实性背书。第 3 页标题为 "Computer Use Agents"（计算机使用智能体），第 4 页列出 AI 的新主题：

- **Test-time scaling**（测试时扩展）
- **AI agents + multi-agent**（智能体与多智能体）
- **User interaction and rich feedback**（用户交互与丰富反馈）
- **Continual learning**（持续学习）
- **Tool use and long-term memory**（工具使用与长期记忆）
- **Reinforcement learning and environment design**（强化学习与环境设计）

第 5 页标题即 "Self-Evolving AI"，并附有一篇博客链接。这六条主题实际上构成了后续四个课程模块的概念骨架：上下文、脚手架（harness）、模型、环境——分别对应"什么在进化"的不同层次。

### 教学目标与先修要求

幻灯片列出四条学习目标：

1. 研究 AI 领域近期技术成果；
2. 提升批判性与创造性思维；
3. 理解 AI 未来研究挑战；
4. 探索并实现新的 AI 研究想法。

先修要求为：AI 编程与实验知识；对现代 AI 能力与局限的理解；自带非 AI 领域知识（用于自己的问题）；加分项是做过自我进化 AI、AI for discovery 等工作。这四条先修要求透露了课程的设计取向：它不是纯理论课，也不是纯工程课，而是要求学生在"有领域问题 + 会做实验"的基础上，进入研究状态。

### 交付形式与评分

课程每周三 2–4pm 上课两小时；课外有作业与阅读任务，周期约两周；另有一个课外的重头研究项目，需要报告与展示。

评分结构（幻灯片原文）：

- **40% 作业**：4 次作业，每次约两周；
- **20% 阅读作业**：4 次，覆盖多模态 AI 前沿研究，与作业同步发布，约两周周期，含课堂讨论/展示；
- **40% 高质量研究项目**：其中 10% 提案与文献综述、10% 中期进展报告、20% 最终报告与展示。

第 19 页补充：出勤与课堂讨论是评分组成部分（20%）——注意此处"20%"与阅读作业的 20% 在幻灯片中分别出现在不同页面，本文按原文分别记录，不代为调和两者关系。缺勤政策：若计划缺课超过一次应尽早告知。作业与阅读各有 2 次"通配"（wildcard），每次可延 24 小时，每项作业最多用 1 次；项目报告每队 2 次通配，可用于提案、中期或最终报告，可合并使用。

### 作业与阅读的具体安排

四次作业按模块推进（幻灯片标注"tentatively"，即暂定）：

- **HW1（第 4 周截止）· Context evolution**：暂定围绕 prompt optimization（TextGrad）与用 LLM 做优化（OpenEvolve）；
- **HW2（第 7 周）· Harness evolution**：暂定围绕 skill evolution（SkillOpt）与自生成 harness（Meta-Harness）；
- **HW3（第 10 周）· Model evolution**：暂定围绕 test-time training 与持续学习方法；
- **HW4（第 12 周）· Task evolution**：暂定围绕自生成任务，并在 PostTrainBench 上"把所有东西合起来"。

阅读作业每次通常 2 篇必读加若干建议（可选）论文，配 5–6 个讨论探针（discussion probes），分三部分：阅读笔记（总结要点，可选提出澄清问题）、论文侦察（围绕探针寻找额外论文、博客等资源）、讨论点（反思探针、准备课上讨论与头脑风暴）。幻灯片给出的总目标是：把各次讨论汇总，共同写出一篇关于自我进化 AI 的综述论文，重点是清晰的分类体系（taxonomy）与严谨的新方向。这是一个相当有雄心的课程设计——阅读作业不只是输入，而是产出的原料。

### 课程项目

项目旨在让学生经历完整研究流程：读文献、熟悉应用领域、尝试最先进模型、做错误分析、开发并迭代新方法、评估与分析结果。2–4 人一组，每组配一名导师，通过定期更新、展示与 GitHub 追踪等贡献。时间线：

- 第 2 周：确定队友、数据集与任务的想法；
- 第 4 周：提案报告 + 展示（文献综述与研究想法）；
- 第 5 周：搭建数据集与基线；
- 第 7 周：中期报告 + 展示（基线 + 新想法结果）；
- 第 10 周：研究想法的更新结果、分析、消融；
- 第 13 周：最终展示（研究想法、结果、分析、讨论）；
- 第 14 周：最终报告。

### 课程模块地图

四个模块的周次安排如下（幻灯片注明"subject to change, based on student interests and course discussions"，即以学生兴趣与课堂讨论为准，可能变动）：

| 模块 | 周次 | 主题 |
|---|---|---|
| Module 1: Context evolution | 第 2–4 周 | prompt optimization、memory、tools、knowledge；LLM 作为发现的优化器；项目提案展示 |
| Module 2: Harness evolution | 第 5–7 周 | harness 组件、多智能体系统；自进化 harness；项目中期展示 |
| Module 3: Model evolution | 第 8–9 周 | 持续学习、蒸馏、test-time training；self-play 方法 |
| Module 4: Environment evolution | 第 10–14 周 | 合成数据与任务、环境生成；世界模型、进化评估与奖励；未来主题（AI for discovery、多模态智能体）；项目最终展示；未来主题（具身 harness、安全进化，NeurIPS） |

第 9 页的课程交付格式与第 10–13 页的模块页中，部分页面带有装饰性插图（如"牛油果形状的扶手椅"、含 $y$ 的公式图、"online assistant icon"等），这些图形在文本抽取中仅有零散标注，**其完整图意无法从文本确认**，本文不据此做任何论证。

---

## 三、技术背景：从语言模型到自主智能体的六年

幻灯片用一组时间线页面勾勒 2020–2026 的进展，每页附有对应论文或产品出处。以下按年份归纳其**叙事线**（年份与出处均为幻灯片原文）：

- **2020 · In-Context Learning**：GPT-3 在大规模无监督预训练后展示零样本与少样本任务适应（Brown et al., OpenAI, 2020）；同页展示 few-shot prompting。
- **2022 · Instruction following**：指令微调与 RLHF 让 LLM 更好遵循用户指令（Ouyang et al., OpenAI, 2022）；同一提示下，GPT-3 续写文本，而经监督微调与 RLHF 的 InstructGPT 回答问题。
- **2022 · Chain-of-thought reasoning**：思维链提示引出多步推理（Wei et al., Google Research, 2022）；简单提示也可引出思维链（Kojima et al., University of Tokyo & Google Research, 2022）。
- **2023 · Reasoning and acting**：ReAct 让 LLM 交错进行推理、工具使用与环境交互（Yao et al., Princeton & Google Research, 2022/2023）；幻灯片概括为"每个想法引导下一步搜索，每个观察激发下一个想法"。
- **2024–2025 · RL-trained reasoning**：强化学习提升复杂推理，并使模型能从额外测试时计算中获益。DeepSeek-R1（DeepSeek-AI, 2025）页面注明"模型仅用正确性奖励训练，自我复查步骤在 RL 训练中出现，并非写入提示"；DeepSeekMath（Shao et al., DeepSeek, 2024）页面说明 GRPO 去掉 PPO 的价值网络，通过对同一提示的一组 rollout 比较奖励来估计优势；另有 OpenAI "Learning to Reason with LLMs"（2024 年 9 月）。
- **2025 · Multi-turn agentic reasoning**：RL 从单次回答推理扩展到复杂多轮交互（Search-R1, Jin et al., 2025；OpenAI Deep Research, 2025 年 2 月）。
- **2024–2026 · Long-horizon model-harness agent systems**：harness 通过上下文管理、记忆、工具与编排，使智能体在长时程任务上持续取得进展（SWE-agent, Yang et al., Princeton, 2024；Claude Code 演示, Anthropic, 2025 年 9 月）。此页还引用 Anthropic "When AI Builds Itself"（2026）中的说法："今年 Anthropic 每位贡献者的代码量增长了八倍，Claude 约写出 Anthropic 合并代码的 80%"；以及 METR 的 "Measuring AI Ability to Complete Long Software Tasks"（检索于 2026 年 9 月）。**这些均为幻灯片引述的外部主张，本文仅记录，不核实其数值。**
- **2026 · Automated Improvement Loops?**：再次引用 "When AI Builds Itself"（Anthropic, 2026）与 OpenAI "Research acceleration: The view inside OpenAI"（2026 年 9 月 6 日），标题带问号，显示这是开放问题而非既定结论。

**解读（非幻灯片原文）**：这条时间线的组织逻辑不是"模型越来越大"，而是"能力形态逐级变化"——从上下文学习（不改变权重）→ 指令跟随（对齐）→ 思维链（推理显式化）→ 行动（工具与环境）→ RL 训练推理（训练时与测试时计算结合）→ 多轮智能体 → 长时程 model-harness 系统 → 自动改进循环。每一步都在扩大"系统"的边界：从模型本身，扩展到提示、工具、环境，最后到 harness 与改进循环本身。这正是课程四个模块（context / harness / model / environment）的历史依据。

---

## 四、自我进化 AI 的历史与当下

幻灯片用一个独立章节追问："History of self-evolving AI, and why is it blowing up now?"（自我进化 AI 的历史，以及为何现在爆发？）

- **1965 · Intelligence Explosion**：英国数学家、Bletchley Park 密码学家（与 Turing 共事）Irving John Good 发表 "Speculations Concerning the First Ultraintelligent Machine"，提出机器递归改进自身设计的思想。幻灯片用四步概括其逻辑：机器有能力设计机器 → 用它设计更强的后继 → 后继更擅长机器设计 → 因此可进入下一轮改进。
- **2003 · Gödel Machines**：Jürgen Schmidhuber（IDSIA）的 "Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements"。幻灯片概括：自指系统在能证明修改有益时修改自身代码。
- **2017 · AlphaGo Zero — Self-Play At Scale**：AlphaGo 先模仿专家棋局再强化学习；AlphaGo Zero（Silver et al., Nature, 2017）则在没有人类棋局数据的自对弈循环中改进。
- **2023 · LLM-guided discovery**：FunSearch（Romera-Paredes et al., Google DeepMind, 2023）把 LLM 生成的代码与自动评估结合进进化循环，发现新的 cap set 构造与改进的装箱启发式；幻灯片列出 Cap Set Problem 与 Online Bin Packing 两个任务。
- **2025 · Self-Modifying Agent**：Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents（Zhang et al., 2025）。
- **2026 · Automated AI research**：幻灯片引用 Andrej Karpathy 的 GitHub 仓库 "autoresearch"（2026），描述一个 AI 智能体按 program.md 提出想法、编辑代码、运行实验，在固定算力预算下改进语言模型预训练（"每次实验 5 分钟，一晚约 100 次实验"）。**该数值为幻灯片引述的仓库描述，本文不代为验证。**

**解读（非幻灯片原文）**：这条历史线的选取很有意思——它把 1965 年的思辨、2003 年的可证明自我改进、2017 年的规模化自对弈、2023 年的 LLM+进化搜索、2025 年的自我修改智能体、2026 年的自动研究串成一条"自我改进的自动化程度递增"的线索。幻灯片并未明说"为什么是现在"，但从前一章的六年进展可以读出其结构：只有当模型具备推理、工具使用、长时程执行与可自动评估的奖励信号时，递归改进循环才具备工程可行性。这是笔者的串联，不是幻灯片原文。

---

## 五、当下图景：三个观察视角

幻灯片用三个"Perspective"组织当下工作，这是全讲最核心的概念框架。

### Perspective 1：What is being evolved?（什么在被进化）

同一问题下并列四个例子，各自指向不同对象：

- **FunSearch**：被进化的是数学程序（math programs）；
- **Meta-Harness**（Yoonho Lee et al., 2026）：被进化的是智能体 harness；
- **Absolute Zero**（Zhao et al., 2025）：被进化的是模型权重（model weights）；
- **Absolute Zero（同一工作）**：任务（tasks）也被进化。

**解读（非幻灯片原文）**：这一视角的价值在于它把"自我进化"从一个笼统口号拆成可操作的对象层级：程序/技能、harness、权重、任务/环境。四者可以独立进化，也可以组合——这与课程四个模块一一对应。幻灯片在此处有多页仅有标题或图形而缺少文本说明，**哪些具体图表支撑哪一对象，文本抽取无法确认**。

### Perspective 2：How is it being evolved?（如何被进化）

幻灯片给出"Model View"（模型视角）与"Agent View"（智能体视角）两个子视角。Agent View 下列出三个例子：

- **RLHF**（Ouyang et al., OpenAI, 2022）——人类反馈训练；
- **Voyager**（Wang et al., 2023）——开放式具身智能体；
- **Darwin Gödel Machine**（Zhang et al., 2025）——开放式自我改进智能体的进化。

**解读（非幻灯片原文）**：Model View 与 Agent View 的区分，大致对应"通过训练改变参数"与"通过交互改变行为/结构"两条路径。幻灯片的 Model View 页面在文本抽取中几乎为空，仅有标题，**其具体内容无法确认**，本文不猜测。Agent View 的三个例子则呈现了从"人类反馈"到"环境反馈+自生成课程"到"自我修改代码"的谱系。

### Perspective 3：Relationships between big concepts（大概念之间的关系）

幻灯片用三组对照页呈现相邻概念的分野：

- **AI for Discovery**：配图标注 "LILA Sciences / Discovery Loop"；
- **Continual Learning**：配图标注 "Oak Lab / Engram"；
- **AI for AI Research → RSI**：配图标注 "Recursive Superintelligence / Mirendil"。

**解读（非幻灯片原文）**：这三组对照暗示了课程要区分的三个邻近领域：用 AI 做科学发现、让模型持续学习、以及让 AI 做 AI 研究从而走向递归自我改进（RSI, Recursive Self-Improvement）。三者共享"循环改进"的结构，但改进的对象、反馈来源与风险剖面不同。幻灯片未给出文字定义，**上述区分是笔者基于标题与配图标注的推断，图内完整内容不可见**。

---

## 六、研究问题与任务清单

幻灯片最后一部分列出六组研究问题，每组附 3–5 篇文献。以下按原文问题陈述归纳，文献仅列幻灯片给出的条目（作者与年份照录，不补充摘要）。

**1. LLM 能否学会品味并做出真正的创新？**
目标：超越对已有想法生成"看似合理的变体"，转向识别有价值的方向、产出真正新颖的发现。文献：Si et al., 2024（100+ NLP 研究者的大规模人类研究）；Bo Jiang, 2026（HindSight：用未来影响评估研究想法生成）；Tom Zahavy (Google DeepMind), 2026（"LLMs Can't Jump"）。

**2. AI 能否自动化工程优化任务？能否自动化 AI 研究本身？**
目标：让智能体自主选择想法、运行实验、产出经证实的研究发现。文献：PaperBench（Giulio Starace et al., OpenAI, 2025）；Learning to Discover at Test Time（Mert Yuksekgonul et al., Stanford & NVIDIA, 2026）；FrontierCS（Qiuyang Mang et al., 2025）；CORAL（Ao Qu, Han Zheng, Zijian Zhou et al., MIT & NUS, 2026）；EdgeBench（Deyao Zhu et al., ByteDance Seed, 2026）。

**3. 如何有效地把经验转化为持久知识？**
目标：把嘈杂的交互轨迹转化为可复用、跨任务持久、不累积错误、不发生灾难性遗忘的知识。文献：ExpeL（Andrew Zhao et al., University of Maryland, 2024）；Agentic Context Engineering（Qizheng Zhang et al., Stanford, 2025）；Self-Distillation Enables Continual Learning（Idan Shenfeld et al., MIT & Thinking Machines Lab, 2026）；Reinforcement Learning via Self-Distillation（Jonas Hübotter et al., ETH Zurich & Stanford, 2026）；Continual Learning Bench（Asawa et al., 2026）。

**4. 何时应更新模型权重，何时应更新 harness？**
目标：判断新经验应内化进权重，还是外化到提示、记忆、技能、工具与编排中。文献：GEPA（Lakshya Agrawal et al., UC Berkeley & Stanford, 2025）；Meta-Harness（Yoonho Lee et al., 2026）；WHALE（Kim et al., KRAFTON, KAIST & Stanford, 2026）；Mem0（Chhikara et al., Mem0, 2025）。

**5. 如何监督越来越自主的系统？**
目标：当智能体在长时程运行、能力超过监督者、且可能学会利用或规避评估者时，保持有意义的人类控制。文献：AI Safety via Debate（Irving, Christiano, Amodei, OpenAI, 2018）；Weak-to-Strong Generalization（Collin Burns et al., OpenAI, 2023）；Agentic Misalignment（Anthropic, 2025）；CoT Red-Handed（Benjamin Arnav et al., Google DeepMind, 2025）。

**6. 面向科学与工程、个性化、多模态与具身世界的自我进化 AI**
- **科学与工程**：从模拟、实验与真实反馈中持续学习以加速发现与工程优化。文献：GeneBench-Pro（Jeremy Li & Andrew Ho, OpenAI, 2026）；Coscientist（Boiko et al., 2023）；AnalogAgent（Zhixuan Bao et al., 2026）；Autonomous Agents Coordinating Distributed Discovery…（Wang et al., 2026）。
- **个性化**：从个体交互与反馈中持续学习，适应用户演变的需求、偏好与目标。文献：Learning Personalized Agents from Human Feedback（Kaiqu Liang et al., 2026）；OpenClaw-RL（Yinjie Wang et al., 2026）；MIRIX（Yu Wang & Xi Chen, 2025）；StuLife（ECNU-ICALK, 2026）。
- **多模态与具身**：从多模态感知与物理交互中持续学习，在动态真实环境中适应知识、技能与行为。文献：Self-Evolving Embodied AI（Tongtong Feng, Xin Wang, Wenwu Zhu, 2026）；Voyager（Guanzhi Wang et al., NVIDIA & Caltech, 2023）；Seeing, Listening, Remembering, and Reasoning（Long et al., 2025）。

**解读（非幻灯片原文）**：这六组问题不是并列的，而是一条递进链：**品味/创新**（能否有好想法）→ **自动化研究**（能否自己跑实验）→ **经验固化**（能否记住）→ **权重 vs harness**（记在哪里）→ **监督**（如何不被绕过）→ **领域落地**（科学、个性化、具身）。其中第 4 组问题直接对应课程 Module 3 与 Module 4 的分界，第 5 组则对应第 14 周"安全进化"的未来主题。幻灯片对每组问题只给"目标"陈述，未给结论；所有文献均为指引性阅读，本文不代为总结其内容。

---

## 七、结语

把这 24 页幻灯片连起来读，第一讲给出的不是一套答案，而是一张地图。这张地图有三层：

**第一层是行政层**——课程以"作业（40%）+ 阅读（20%）+ 项目（40%）"驱动，四次作业沿着 context → harness → model → task 四个进化对象推进，阅读作业最终汇聚为一篇共同撰写的综述，项目则要求完整的"读文献—搭基线—迭代方法—评估分析"闭环。这一层的信息密集程度说明：这门课把"做研究"本身当作教学内容，而不是把研究留作课外延伸。

**第二层是历史层**——从 2020 年的 in-context learning 到 2026 年的自动改进循环，六年进展的主线不是参数规模，而是"系统边界"的扩张：提示、工具、环境、harness、改进循环本身逐步被纳入可优化对象。这条主线同时解释了 1965 年 Good 的思辨为何在 2026 年重新获得工程意义：递归改进需要可自动评估的反馈信号与可执行的长时程智能体，而这两者在最近两年才同时具备。幻灯片对"是否已在爆发"保持谨慎——2026 年的标题页带着问号。

**第三层是问题层**——三个视角（进化什么、如何进化、与邻近概念的关系）与六组研究问题共同构成课程的研究议程。值得注意的是，这些问题里有相当一部分是"元问题"：不是"如何让模型更强"，而是"新经验该记在哪里"、"如何监督超过监督者的系统"、"如何判断一个想法是否真有价值"。这些问题没有标准答案，幻灯片本身也只给目标与文献，不给结论。

对读者而言，这篇导览最值得带走的一点或许是：**自我进化 AI 的核心困难不在"让系统改自己"，而在"如何可靠地判断改动是好的"**。从 Gödel Machine 的"可证明有益"到 FunSearch 的自动评估、到 RL 的正确性奖励、到课程反复强调的评估与奖励进化（第 11 周），所有工作都在回答同一个问题——反馈信号从哪来、可不可信、会不会被利用。这既是技术问题，也是监督问题，也是这门课把"安全进化"放在最后一周的原因。

---

## 附：本文引用到的官方幻灯片中出现的链接

- 课程网站：https://mit-mi.github.io/how2ai-course/fall2026/
- Canvas 提交入口：https://canvas.mit.edu/courses/40521/
- 幻灯片中出现的博客链接（Self-Evolving AI 页）：https://quao627.github.io/blog/self-evolving-agents/
- 主讲人主页：https://pliang279.github.io

（以上链接均为幻灯片文本中直接给出的 URL；幻灯片中引用的论文与产品出处已在正文按原文标注，本文不额外补充链接。）
