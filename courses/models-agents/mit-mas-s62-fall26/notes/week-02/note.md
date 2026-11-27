# MIT MAS.S62 · Self-Evolving AI · Fall 2026

## Week 02 学习笔记：Context Evolution 1（上下文演化 1）

> **说明**：本笔记基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。笔记内容仅依据所给两份官方幻灯片的可抽取文本与可辨认图示标注，页面重复、页码与 OCR 失真不作为论证依据。幻灯片中部分图表内容（如幻灯片 8、21、38–47 的图形细节、ACE 架构图 12–18 的具体连线）在抽取文本中缺失或仅部分可见，相关部分保留不确定性，不做虚构补全。文中区分"幻灯片内容"与"整理者解释"：凡属引申、类比或对缺失图示的合理概述，均以【解释】标注。不虚构课堂对话、实验数值、作业要求或参考文献；幻灯片中出现的引用仅按原文所列作者与题名转写。

---

## 一、学习目标

完成本周内容后，应能：

1. **界定上下文（context）与执行框架（harness）**：说清"模型在生成下一个 token 前读到的一切"这一上下文定义，以及 harness 作为"围绕模型、管理其上下文与执行流程的代码"这一定位（幻灯片 5–6）。
2. **列举上下文的类型**：文本与多模态上下文、prompts、memory 三类（幻灯片 3、47）。
3. **解释上下文如何改变行为**：从 next-token prediction 的注意力机制出发，理解 in-context learning、chain-of-thought、tree-of-thoughts 等上下文形态的作用（幻灯片 7–11、36–37）。
4. **理解 prompt optimization 的两大挑战与两条技术路线**：离散不可微 token 的优化问题（gradient-based vs search-based），以及高维搜索空间的降维问题（模块化、可组合的 prompt 与程序）（幻灯片 21–35）。
5. **比较应对长上下文的三种方式**：新架构、长上下文训练、上下文管理（含摘要、记忆系统、RAG），并说明各自代价（幻灯片 39–45）。
6. **理解 ACE（Agentic Context Engineering）的问题动机与核心设计**：brevity bias 与 context collapse 两个局限，增量式 delta update、结构化分工（Generator / Reflector / Curator）与确定性合并（客座讲者幻灯片 8–21）。
7. **形成批判性判断**：识别各方法的适用边界、评测困难与未解问题，能对照复习清单自测。

---

## 二、课程定位与今日路线图

幻灯片 2 的公告（announcements）仅为课程事务：通知 for-credit 或 listener 身份、加入 canvas、canvas 上的 project preferences 表单、当晚发布第一篇 reading assignment（主题为 context evolution）。这些属于行政信息，不构成本周技术内容。

幻灯片 3 / 47 给出今日讲纲：
- Types of context：text and multimodal, prompts, memory
- Prompt optimization
- Long-context models
- Context management and memory
- Guest speaker：agentic context engineering
- Demo of context evolution

【解释】从结构看，本周是一条"从上下文是什么 → 如何优化上下文（prompt 层面）→ 如何扩展上下文容量（长上下文模型）→ 如何管理上下文（记忆与 RAG）→ 如何让上下文自我演化（ACE）"的递进线索。幻灯片本身未明说这一叙事，此为整理者的结构化概括。

---

## 三、核心概念

### 3.1 Agent 的定义（幻灯片 4）

幻灯片给出的经典 agent 定义：**agent 通过 sensors 感知环境，通过 actuators 作用于环境**。课程把这一抽象落到 LLM 场景：

- **Environment**：code repo、website、application、real world。
- **States / observations**：messages、files、webpages、tool results。
- **Actions**：text、file edits、API calls、shell commands、physical movements。
- **Rewards**：test cases、task completions、LLM judges、user feedback。

【解释】这组映射的意义在于：LLM agent 的"感知"与"行动"大多以文本/多模态 token 形式出现，因此上下文天然就是 agent 的状态载体；后面的 context evolution 实际上是在讨论"如何演化这个状态"。

### 3.2 Context 与 Harness（幻灯片 5–6）

- **Context 定义**：Everything the model reads before generating the next token（模型在生成下一个 token 之前读到的一切）。
- **Harness 定义**：Code around the model that manages its context and execution flow to complete tasks（围绕模型、管理其上下文与执行流程以完成任务的代码）。

幻灯片 6 引用 ReAct（Yao et al., ICLR 2023）作为 harness 的示例语境。【解释】二者的关系可概括为：context 是"模型看到的内容"，harness 是"决定模型看到什么、按什么流程行动的代码"；上下文演化既可由人设计，也可由 harness 自动完成——这正是 ACE 的切入点。

### 3.3 上下文如何改变行为（幻灯片 7–8）

幻灯片 7 的论断：**预测下一个 token 时，模型 attends to 前面的上下文（preceding context）**。幻灯片 8 标题相同但抽取文本缺失图像内容，无法确认其具体示例。【不确定性保留】此处只能确认课程强调"上下文通过注意力直接影响输出分布"，不推断幻灯片 8 的具体演示形式。

### 3.4 In-Context Learning 与推理结构（幻灯片 9–11）

- **In-Context Learning**：引 Brown et al., Language Models are Few-Shot Learners, NeurIPS 2020——即 few-shot 示例置于上下文即可引导模型行为。
- **Chain of Thought**：引 Wei et al., NeurIPS 2022——用中间推理步骤作为上下文引导推理。
- **Tree of Thoughts**：引 Yao et al., NeurIPS 2023——把推理组织为树状搜索结构。

【解释】三者递进体现了"上下文不仅是信息，还是推理的计算结构"：从示例（ICL）到线性推理轨迹（CoT）再到搜索树（ToT），上下文承载的认知负荷逐步增加，但都受上下文窗口与生成成本约束。

### 3.5 多模态上下文（幻灯片 12–17）

- **Prefix tuning / 冻结语言模型**（Tsimpoukelli et al., NeurIPS 2021）：通过 prefix 条件化建模 p(text | image)，图中出现 Adapter 与 "Adapted + pretrained" 标注。
- **MiniGPT-4**（Zhu et al., arXiv 2023）：两阶段——Stage 1 用 paired image-text data 做 alignment；Stage 2 用 image + text instructions 与示例补全做 instruction tuning。
- **Interleaved tokens**（Ong et al., OmniSapiens, ICML 2026）：language tokens、projected visual tokens、projected audio tokens 交错排列；幻灯片附 GitHub 链接（human_behavior_atlas）。
- **Socratic Models**（Zeng et al., ICLR 2023）：用于 image captioning、robot perception and planning、video reasoning 的零样本多模态推理组合。

【解释】多模态上下文的共同思路是"把非文本模态投影为 token 序列"，使其与文本共享同一注意力上下文；这为"上下文类型"增添了视觉与音频维度，也放大了长上下文管理的难度。

### 3.6 ReAct：推理与行动交织（幻灯片 18）

幻灯片 18 标题 "Reasoning and Acting in Context"，引 Yao et al., ReAct, ICLR 2023。抽取文本未含具体轨迹图，仅能确认课程将 ReAct 作为"上下文内推理与行动交替"的代表。【不确定性保留】不补述具体 prompt 模板或实验数字。

### 3.7 Prompt 敏感性与提示设计困难（幻灯片 19–20）

- **Prompt Sensitivity**（Sclar et al., ICLR 2024）：关键发现——LLMs are (were?) sensitive to spurious changes to prompts（对 prompt 设计中无关紧要的改动敏感）。括号中的 "(were?)" 是幻灯片原文措辞，暗示该结论可能随模型迭代而变化，值得注意。
- **Challenges in Prompting**（Zamfirescu-Pereira et al., CHI 2023, "Why Johnny Can't Prompt"）：非 AI 专家在设计 LLM prompts 时的困难包括：不知如何起步、难以选对指令、错误期待人类能力、常需寻求帮助。

【解释】这两页共同构成 prompt optimization 的动机：既然 prompt 表面形式影响巨大、人工设计又困难，就需要系统化的自动优化方法。

### 3.8 Prompt Optimization 的两种范式（幻灯片 21）

幻灯片 21 用流程图对比：

- **Standard prompting**：User → Prompt → LLM → Output → Eval。
- **LLM-assisted prompting**：同上，但在 Prompt 环节加入 LLM 辅助。
- **Prompt optimization**：Prompt → LLM → Output → Eval 构成回路（图中 Prompt 与后续环节形成迭代）。

【解释】三者差别在于"谁在改写 prompt"：人、人+LLM、还是自动优化器（以 Eval 为信号闭环）。幻灯片未给出回路的具体算法，仅示意结构。

### 3.9 Prompt 演化的两大挑战（幻灯片 22、35）

幻灯片 22 与 35 内容一致，明确列出：

1. **如何对离散、不可微的 token 做优化**？需要离散优化技术。
   - 方向一：gradient-based 或 search-based；
   - 方向二：梯度直接更新 prompt，还是更新"生成 prompt 的 LLM"。
2. **搜索空间极高维**（所有长字符串构成的空间），如何通过模块化、可组合的 prompt 降低维度？
   - 方向：text vs code modules、软件工程最佳实践。

【解释】这两条挑战是本周"方法比较"的主轴：TextGrad 偏 gradient-based（文本梯度）、APE 偏 search-based（黑盒搜索）、DSPy 偏模块化编程；ACE 则把"优化对象"从 prompt 扩展到整个 playbook 上下文。

### 3.10 离散优化难题（幻灯片 23）

幻灯片 23 指出：若输入与各层都是文本，梯度难以计算；对 token embeddings 求梯度又无法映射回文本。这是"文本域优化"的根本困难。【解释】该页为后续 TextGrad 的"文本梯度"思路埋下伏笔：既然数值梯度不可用，就用自然语言反馈充当"梯度"。

### 3.11 Prompt Optimization via Text Generation（幻灯片 24）

引 Zhou et al., "Large Language Models are Human-Level Prompt Engineers", ICLR 2023——即 APE 一类方法：**LLM 通过黑盒优化/搜索来生成并评分 prompts**。【解释】其要点是把 prompt 视为搜索空间中的候选，由 LLM 提议、由评估打分选择；属于 search-based 路线。

### 3.12 TextGrad：文本自动微分（幻灯片 25–30）

引 Yuksekgonul et al., "TextGrad: Automatic Differentiation via Text", arXiv 2024。幻灯片给出的关键机制：

- LLMs optimize prompts through gradient descent / first-order optimization（用"文本梯度"做一阶优化）。
- 反馈形式为自然语言："This prediction can be improved by…" 用于更新 Prompt。
- 流程两步：1）给定 Evaluation，收集对 Prediction 的反馈；2）给定（对 Prediction 的反馈 + Evaluation），收集对 Prompt 的反馈。
- 幻灯片 27–30 为同一方法的连续图示，抽取文本未含新增文字，无法确认各页差异细节。【不确定性保留】

【解释】TextGrad 的类比是：把"损失对参数的梯度"替换为"评估对预测、预测对 prompt 的语言反馈链"，从而在不可微的文本域模拟反向传播；代价是每步都需多次 LLM 调用，成本与方差需关注（幻灯片本身未给数值）。

### 3.13 模块化程序：DSPy（幻灯片 31–34）

- **问题重述**（幻灯片 31）：优化空间极高维；通过抽象化，每个 LLM 步骤由一组 common modules（retrieve、read 等）构成。引 Khattab et al., "Demonstrate-Search-Predict", arXiv 2023。
- **DSPy 定位**（幻灯片 32）：远离自由形式字符串操作，走向编程——组合模块化算子构建 text transformation graphs；**compiler 自动生成优化后的 LM 调用策略与 prompts**。引 Khattab et al., "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines", arXiv 2023。
- **优化三方式**（幻灯片 34）：
  1. **Candidate Generation**：compiler 递归找出程序中所有唯一 Predict 模块（predictors），为其参数生成候选——instructions、field descriptions、demonstrations（input–output pairs）。
  2. **Parameter Optimization**：用超参调优算法（如 random search 或 Bayesian optimization）在候选中选择——回到离散优化问题。
  3. **Higher-Order Program Optimization**：修改程序控制流，例如 ensemble 多份副本并行运行并聚合（如 majority voting）。

【解释】DSPy 的贡献是把"优化 prompt 字符串"转化为"优化程序中的模块参数与结构"，用软件工程手段压缩搜索空间，与幻灯片 22 的挑战 2 直接对应。幻灯片 33 为模块实例化的代码示例，抽取文本仅标题，不转述代码细节。

### 3.14 长上下文模型（幻灯片 36–45）

**注意力回顾**（幻灯片 36–37）：引 Vaswani et al., NeurIPS 2017。抽取到的公式为：

h = softmax( XW_q W_k^T X^T / √d ) XW_v

并标注了 (row) normalize to 0–1、normalize wrt dimension d、3×3 (weighted) outer product、3×d 与 d×3 等张量形状；幻灯片 37 以 "Fox jumps over the lazy" 为例，给出 y = a15 v1 + a25 v2 + a35 v3 + a45 v4 + a55 v5 的加权和形式。【解释】这说明每个 token 的新表示是对全部上下文 value 的加权聚合——上下文越长，注意力矩阵越大，这正是长上下文计算成本的来源；幻灯片中的 "lazy." 等零散文字为排版噪声，不作为论证。

**Needle-in-a-Haystack**（幻灯片 38）：仅给出 GitHub 链接（gkamradt/needle-in-a-haystack），无文字结论。【不确定性保留】不推断具体评测结果。

**应对长上下文的三种方式**（幻灯片 39）：

1. **New architectures**：sliding window、sparse、linear attention 等。
   - 优点：提升效率、降低计算；缺点：需重新设计与重新训练。
2. **Long-context training**：short-to-long training、synthetic data、扩展 position encodings。
   - 优点：扩大上下文窗口、使用简单；缺点：需要数据、可能昂贵。
3. **Context management**：context summarization、memory systems、RAG。
   - 优点：改善信息管道、可扩展；缺点：依赖 retrieval 与 memory 的质量。

**架构细节**（幻灯片 40–42，credit: CMU AI Agents course fall 2026）：

- Full attention vs Sliding window attention（幻灯片 40）；
- Sparse attention：Fixed global attention + sliding window local attention，以及 Context-dependent 变体（幻灯片 41）；
- 幻灯片 42 为 "Long Context Models Summary"，抽取文本仅有标题与 credit，总结要点缺失。【不确定性保留】

**长上下文训练数据**（幻灯片 43）三类：

1. 具有连贯自然结构的长文档，如 books、codebases、repositories、multiple documents；
2. Agent trajectories：observations + actions + rewards；
3. Synthetic tasks：在设定位置放置受控 evidence 与 distractors。

**位置编码**（幻灯片 44）：引 Chen et al., "Extending Context Window of Large Language Models via Position Interpolation", arXiv 2023。抽取文本仅有标题与引用，未含公式。

**长上下文评测**（幻灯片 46）：引 Yen et al., "Helmet: How to Evaluate Long-Context Language Models Effectively and Thoroughly", ICLR 2025。抽取文本未含具体指标或榜单。【不确定性保留】不虚构评测数值。

### 3.15 客座讲者：Agentic Context Engineering（ACE）

**背景与案例**（客座幻灯片 2–7）：

- 案例为 **AppWorld benchmark**：coding agent 与交互式环境；多轮、长上下文任务，许多 task queries 超过 10 轮、超过 32K tokens；环境提供定制的 tool 与 API 定义。
- 观察到的问题：agent 常在后续操作前**忘记先获取用户的 access token**；示例代码先调用 show_song_library 而报错 `Key "access_token" does not exist!`。
- 人工修补：在上下文中写入 "Principle 1: Always log in to retrieve access token from users as a first step."，并置于 system prompt 中。幻灯片 7 的结论句（抽取文本有断行）：agent 常错过 contextual/procedural knowledge，即"如何做"的知识，而非事实本身。

**三种适应范式对比**（客座幻灯片 8）：

- **Weight updates（fine-tuning / RL）**：优点——推理时强且紧凑；缺点——迭代慢、基础设施重、难以审计/回滚。
- **Retrieval（RAG）**：优点——注入事实、模块化；缺点——对 procedures、contexts、tool protocols、"how-to" 知识较弱。
- **Context evolution（本讲）**：优点——快速的 test-time learning、可解释、model-agnostic；缺点——长时程下需要稳定性与成本控制。

【解释】这一三分法是本周最重要的概念框架之一：它把"上下文演化"定位为介于权重更新与检索之间的第三种适应机制，强调"快速、可解释、模型无关"，但代价是长期稳定性与成本。

**现有上下文适应方法的两个局限**（客座幻灯片 9–10）：

- 代表方法：GEPA（prompt optimizers）、Dynamic Cheatsheet（agent memory）等。
- **Brevity bias**：偏好简短、精炼、通用的指令。
- **Context collapse**：把上下文重写为更短、信息更少的摘要；幻灯片以 Prompt_i → Rollouts_i → Reflector → Prompt_i+1 的循环示意"Context Collapse!"。
- 主张：上下文不应是精炼摘要，而应是**全面、演化的 playbook**——详尽、包容、富含领域洞见。

**增量式上下文更新**（客座幻灯片 11）：

- 先前做法：monolithic rewrite → collapse；
- ACE 做法：delta updates → stable growth；
- "Recipe #1: Incremental update for graceful scaling of model context"。

**ACE 架构**（客座幻灯片 12–19）：幻灯片 12–18 为同一架构的连续图示，抽取文本仅标题，具体组件文字缺失。【不确定性保留】仅能依据幻灯片 19 的总结句确认："Recipe #2: Structured division of labor (Generator, Reflector, Curator)"。即三类角色分别负责执行、洞察提取与整合。【解释】结合幻灯片 21 的形式化描述可补全理解：Generator 产生轨迹，Reflector 提炼经验，Curator 以 delta 形式并入 playbook——但各角色的输入输出细节在抽取文本中不可见，不做进一步断言。

**"这不就是 prompt engineering 吗？"**（客座幻灯片 20）：标题为反问，抽取文本无正文。【不确定性保留】无法确认讲者的具体回应；不虚构论点。

**形式化：把上下文演化视为系统问题**（客座幻灯片 21）：

- **State**：把演化中的上下文作为 first-class citizen 的更好表示——sections；itemized bullets + metadata → 支持 localization、fine-grained retrieval、incremental adaptation、periodic de-duplication and clean-up。
- **Update operator**：delta updates + deterministic merge——紧凑的 delta 上下文而非全量重写 → 保留旧知识、避免 collapse、支持 batching/parallel learning。
- **Architecture**：autonomous loop + structured division of labor——分离 execution、insight extraction、integration，并允许迭代精炼。

【解释】这三要素对应"状态—算子—架构"的系统观，是 ACE 与"prompt 优化器"的关键区别：后者优化一个静态 prompt，前者维护一个可增量生长、可去重清理的结构化 playbook。

**AppWorld 案例结果**（客座幻灯片 22–28）：

- 幻灯片 22：ACE 生成的上下文包含详细、领域特定的洞见，连同可直接使用的工具与代码，构成 comprehensive playbook；展示 "Pre-defined general section names" 与 "Generated bullet-points of insights"。抽取文本仅部分可见，不转述具体条目。
- 幻灯片 23–25：图示页，抽取文本无结论文字。【不确定性保留】
- 幻灯片 26：ACE achieves better performance than RAG-based ICL and prompt optimizers。
- 幻灯片 27：ACE can evolve context even without supervised labels, using environment feedback。
- 幻灯片 28：ACE could evolve context both offline（system prompt）and online（agent memory）。

**成本与效率**（客座幻灯片 29–30）：

- 幻灯片 29：对 ACE 与 GEPA 做 component-wise cost analysis；结论——ACE significantly reduces tokens usage and adaptation latency as compared to GEPA。
- 幻灯片 30：标题 "KV Cache Reuse: Longer Context ≠ Higher Serving Cost"；抽取到的具体数字：ACE 使用更多 raw input tokens，但其中 **91.8%** 可由 KV-cached prompts 服务，减少 **82.6%** 的 billed input token 成本。【解释】这是幻灯片明确给出的数值，属客座讲者陈述，本笔记不额外核验、不推广为普遍结论。

**结果总结**（客座幻灯片 31）：Accuracy: **+10.6%** on agents and **+8.6%** on finance；Efficiency: significantly reducing adaptation latency and rollout cost。同为幻灯片陈述数值，不虚构其置信区间或实验设置细节（抽取文本未给）。

**生产案例**（客座幻灯片 32–34）：

- **SCX.ai**（澳大利亚 AI 产品与研究公司）：客服 workflow chatbot。Without ACE：chatbot 总是直接退款（"funny yet dangerous"）；With ACE：总是先询问并核验 order ID + order details。
- **AnyShift**（法国 platform engineering 初创）：幻灯片仅给公司描述与博客链接（anyshift.io/blog/ace-retrieval-layer），无结论文字。【不确定性保留】

**未来方向**（客座幻灯片 35）：

- 把上下文视为快速的 test-time 持续学习媒介，稳定后选择性 distill 进权重；
- Parallel context learning at scale：Combee, COLM 2026；
- Meta-evolution for memory systems and harnesses：Meta-Harness, COLM 2026；
- 更新的安全性与正确性（ML + systems）；
- Consolidation（learning）：in-context 或 weight-update self-distillation。

**结论**（客座幻灯片 36）：context evolution 作为 AI 适应的新范式；brevity bias 与 context collapse；ACE 使能 self-improving agents 与 domain AI。附论文、代码、博客与联系方式（按幻灯片原样列于文末来源之外不重复）。

---

## 四、方法比较

| 维度 | Prompt 优化（APE / TextGrad） | 模块化编程（DSPy） | 长上下文模型 | 上下文管理（RAG/记忆） | ACE（上下文演化） |
|---|---|---|---|---|---|
| 优化对象 | prompt 字符串 | 程序内模块参数与控制流 | 模型架构/训练/窗口 | 检索与记忆管道 | 结构化 playbook（state） |
| 优化信号 | 评估反馈（文本梯度或搜索打分） | compiler + 超参搜索 | 训练数据与位置编码 | 检索质量 | 环境反馈（可无监督标签） |
| 离散优化难题 | 直接面对（挑战 1） | 以模块化降维（挑战 2） | 不适用 | 部分规避 | 以 delta + merge 规避全量重写 |
| 主要代价 | 多次 LLM 调用、方差 | 编译与搜索开销 | 重训练/数据成本 | 依赖 retrieval 质量 | 长时程稳定性与成本控制 |
| 可解释性 | 中（反馈可读） | 中（程序结构可读） | 低 | 中 | 高（幻灯片主张 interpretable） |
| 模型无关性 | 高 | 高 | 低（需重训） | 高 | 高（model-agnostic） |

【解释】上表为整理者依据两份幻灯片文字归纳，非幻灯片原生表格；其中"可解释性""模型无关性"评级依据客座幻灯片 8 的 pros/cons 措辞，其余为对照归纳。表格不引入幻灯片之外的实验结论。

**两条优化路线的对照**（依据幻灯片 22、35）：gradient-based（TextGrad：用自然语言反馈模拟梯度，直接更新 prompt）vs search-based（APE：LLM 生成候选并评分）；以及"更新 prompt 本身"vs"更新生成 prompt 的 LLM"。DSPy 则把战场从"字符串"移到"程序结构"，用 candidate generation、parameter optimization、higher-order optimization 三步压缩搜索空间。

**长上下文三路线的对照**（依据幻灯片 39）：新架构（效率优先但需重训）、长上下文训练（简单但贵）、上下文管理（可扩展但依赖检索与记忆质量）。三者并非互斥，幻灯片未讨论组合策略，此处不引申。

**ACE 与 prompt optimizer 的对照**（依据客座幻灯片 9–11、26、29–30）：既有方法因 brevity bias 与 context collapse 而丢失信息；ACE 以 delta update 与 deterministic merge 保持"stable growth"，并以 KV cache 复用（91.8% 命中、82.6% 成本下降，幻灯片陈述值）缓解"长上下文=高服务成本"的直觉。

---

## 五、局限与不确定性

1. **幻灯片自身的局限陈述**：
   - Prompt 敏感性结论被写成 "LLMs are (were?) sensitive"，括号暗示结论可能随模型版本变化（幻灯片 19）。
   - 长上下文三路线各有明确代价（幻灯片 39）：重训、数据成本、检索/记忆质量依赖。
   - 上下文演化范式需"stability + cost control at long horizons"（客座幻灯片 8）。
   - 既有上下文适应方法存在 brevity bias 与 context collapse（客座幻灯片 9–10）。
2. **抽取文本导致的不确定性**（明确保留，不补全）：
   - 幻灯片 8 的图像内容缺失，无法确认其演示的具体上下文变化示例。
   - 幻灯片 12–17 的多模态图示细节（如 prefix tuning 的具体张量流向）仅有零散标注。
   - 幻灯片 27–30 的 TextGrad 连续图示、幻灯片 33 的 DSPy 代码、幻灯片 42/45 的 "Long Context Models Summary" 正文、幻灯片 44 的位置编码公式、幻灯片 46 的 Helmet 评测细节，抽取文本均缺失或仅有标题。
   - 客座幻灯片 12–18 的 ACE 架构图文字缺失，仅能依据幻灯片 19 与 21 的总结句概述三组件分工。
   - 客座幻灯片 20 "Isn't this just prompt engineering?" 仅有标题，讲者回应不可知。
   - 客座幻灯片 23–25、34 为图示或链接页，无结论文字。
3. **数值的边界**：+10.6% / +8.6%、91.8%、82.6% 均为客座幻灯片陈述，抽取文本未给实验设置、基线细节与置信区间；本笔记按"幻灯片如此陈述"处理，不推广、不二次解读。
4. **本笔记未覆盖**：课堂口头补充、demo 环节的具体内容（幻灯片 3/47 列有 "Demo of context evolution"，但无对应文字材料）、作业与阅读材料的具体要求（仅知 reading assignment 主题）。
5. **【解释】层面的局限**：第三节与第四节的类比、表格与叙事线索为整理者归纳，可能与讲者原意有偏差；凡涉及机制因果的表述均以幻灯片原文为准。

---

## 六、复习清单

**概念自测**

- [ ] 用一句话给出 context 与 harness 的定义，并各举一例（幻灯片 5–6）。
- [ ] 列出 agent 定义中的 environment / states / actions / rewards 四要素在 LLM 场景下的对应物（幻灯片 4）。
- [ ] 说明 next-token prediction 中注意力如何使上下文影响输出；写出幻灯片 36–37 的注意力公式并解释各张量形状。
- [ ] 区分 in-context learning、chain-of-thought、tree-of-thoughts 三种上下文结构及其引用（幻灯片 9–11）。
- [ ] 列举多模态上下文的至少三种做法（prefix tuning、MiniGPT-4 两阶段、interleaved tokens、Socratic Models）（幻灯片 12–17）。
- [ ] 复述 prompt sensitivity 的关键发现与 "Why Johnny Can't Prompt" 的四类困难（幻灯片 19–20）。
- [ ] 说出 prompt 演化的两大挑战，并各举一条应对路线（幻灯片 22、35）。
- [ ] 解释 TextGrad 的"文本梯度"两步反馈流程（幻灯片 25–26）。
- [ ] 复述 DSPy 的三种优化方式及其与"高维搜索空间"挑战的对应（幻灯片 34）。
- [ ] 列出应对长上下文的三种方式及各自优缺点（幻灯片 39）。
- [ ] 说出长上下文训练数据的三类来源（幻灯片 43）。
- [ ] 复述 ACE 针对的两个局限（brevity bias、context collapse）与"playbook 而非摘要"的主张（客座幻灯片 9–10）。
- [ ] 用 state / update operator / architecture 三要素描述 ACE 的系统形式化（客座幻灯片 21）。
- [ ] 说出 ACE 的三类角色分工（Generator、Reflector、Curator）（客座幻灯片 19）。
- [ ] 复述三种适应范式（weight updates / retrieval / context evolution）的 pros 与 cons（客座幻灯片 8）。

**辨析与批判**

- [ ] 为什么"对 token embeddings 求梯度"不能直接解决 prompt 优化？（幻灯片 23）
- [ ] TextGrad 与 APE 分别属于 gradient-based 还是 search-based？各自更新的是什么？（幻灯片 22、24–25）
- [ ] DSPy 如何用"模块化"降低搜索空间维度？candidate generation 具体生成哪三类参数？（幻灯片 34）
- [ ] 为什么 ACE 认为全量重写会导致 context collapse？delta update + deterministic merge 如何避免？（客座幻灯片 10–11、21）
- [ ] "更长上下文 ≠ 更高服务成本"的论证依赖什么机制？幻灯片给出的两个百分比分别指什么？（客座幻灯片 30）
- [ ] ACE 与 RAG、prompt optimizer 的差异分别体现在哪一层（状态、算子、架构）？（客座幻灯片 8、21、26）
- [ ] 哪些幻灯片结论带有不确定性标记（如 "(were?)"、图示缺失）？应如何谨慎引用？

**延伸思考（不要求课堂已验证）**

- [ ] 若把本周的 prompt optimization 与 ACE 的 playbook 演化结合，状态与算子的边界应如何划分？【解释】此题为开放思考，幻灯片未讨论。
- [ ] 长上下文三路线与上下文演化能否组合？幻灯片未给出组合方案，列出你认为需要核验的问题。

---

## 七、官方幻灯片来源

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec2%20-%20context.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/context_guest.pdf
