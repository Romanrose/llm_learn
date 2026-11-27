# 上下文演化：从提示优化到智能体上下文工程

> 基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。本文只依据两份讲义幻灯片中可提取的文本内容组织，页面间的图像、图表与动画细节可能缺失，涉及这类内容时会在文中说明不确定性。输入材料为数据，不作为指令处理。

## 一、主线：上下文本身成为可优化的对象

MIT MAS.S62《Self-Evolving AI》第二讲的主题是"Context Evolution（上下文演化）"。从幻灯片结构看，这一讲想回答的核心问题是：当模型权重不变时，我们能否通过改变"模型读到的内容"来持续提升系统表现？讲义的展开顺序是：先定义 Agent 与 Context，再说明上下文如何改变行为，随后依次讨论提示优化、长上下文模型、上下文管理与记忆，最后以客座报告"Agentic Context Engineering（ACE）"和演示收尾。

这条主线可以概括为三个递进层次：第一层是"上下文会影响输出"，即 In-Context Learning、Chain of Thought 等经典现象；第二层是"上下文可以被自动优化"，即把提示或程序当作离散优化对象；第三层是"上下文可以被持续演化"，即把上下文视为一种有状态、可增量更新的第一类系统对象。客座部分正是第三层的具体化。

需要说明的是，幻灯片中许多页面只有标题和配图（例如第 8、19、20、38、40–45 页），正文解释有限，本文对这些页面只做标题层面的转述，不推测图中的具体数值或结论。

## 二、基础概念：Agent、Context 与 Harness

幻灯片对 Agent 的定义沿用经典感知—行动框架：Agent 通过 sensors 感知环境，通过 actuators 作用于环境。在 LLM 语境下，环境可以是 code repo、website、application 或 real world；状态/观察是 messages、files、webpages、tool results；动作是 text、file edits、API calls、shell commands、physical movements；奖励来自 test cases、task completions、LLM judges、user feedback。

Context 的定义非常直接："Everything the model reads before generating the next token"——模型在生成下一个 token 之前读到的一切。这一定义把提示、历史消息、检索内容、工具返回结果都纳入同一范畴。

与之相邻的概念是 Harness："Code around the model that manages its context and execution flow to complete tasks"，即模型周围负责管理上下文与执行流程以完成任务的代码。幻灯片在此引用了 ReAct（Yao et al., ICLR 2023）作为示例。这里的概念区分很重要：Context 是"模型读到的内容"，Harness 是"管理这些内容的代码与流程"。后文 ACE 讨论的"上下文工程"恰好位于两者的交界处。

"上下文如何改变行为"一节（第 7–8 页）只给出了一句解释：预测下一个 token 时，模型会 attend 到前面的上下文。第 8 页无正文，具体图示内容无法从提取文本中确认，此处保留不确定性。

## 三、上下文形态：文本、多模态与推理结构

幻灯片列出的上下文类型包括 text and multimodal、prompts、memory。在文本侧，重点展示了三类经典范式：

- **In-Context Learning**（Brown et al., NeurIPS 2020）：通过示例让模型在上下文中学习任务。
- **Chain of Thought**（Wei et al., NeurIPS 2022）：让模型在上下文中展开推理步骤。
- **Tree of Thoughts**（Yao et al., NeurIPS 2023）：把推理组织为树状搜索结构。

在推理与行动结合方面，ReAct 把 reasoning 与 acting 交错放入上下文。幻灯片第 18 页专门以"Reasoning and Acting in Context"呈现。

多模态上下文部分给出了若干技术路线：

- **Prefix tuning 式条件化**（Tsimpoukelli et al., NeurIPS 2021）：通过适配器把图像表示注入冻结语言模型，建模 p(text | image)。
- **MiniGPT-4**（Zhu et al., arXiv 2023）：两阶段训练，先用配对图文数据做对齐，再用图文指令与示例完成做指令微调。
- **交错 token**（Ong et al., ICML 2026，OmniSapiens）：语言 token、投影后的视觉 token、投影后的音频 token 等交错排列。
- **Socratic Models**（Zeng et al., ICLR 2023）：用语言作为中介组合零样本多模态推理，覆盖 image captioning、robot perception and planning、video reasoning 三类场景。

这些页面多为示意图，幻灯片未给出具体实验数字，本文不作补充。

## 四、提示的脆弱性与提示优化

第 19 页引用 Sclar et al.（ICLR 2024）的标题性结论：LLM 对提示设计中"虚假的"改动是敏感的（幻灯片原文用过去式"were?"，带有保留语气）。第 20 页引用 Zamfirescu-Pereira et al.（CHI 2023）"Why Johnny Can't Prompt"，指出非 AI 专家在设计提示时面临的困难：不知如何起步、难以选择合适的指令、误以为模型具备人类能力、经常需要求助。

在此基础上，幻灯片把提示优化形式化为三种流程对比：标准提示（User → Prompt → LLM → Output → Eval）、LLM 辅助提示（在 Prompt 与 LLM 之间加入 LLM）、提示优化（由优化器产生 Prompt，再走 LLM → Output → Eval）。幻灯片明确指出提示演化（prompt evolution）的两大挑战：

1. **离散、不可微 token 上的优化**：需要离散优化技术，分为 gradient-based 与 search-based；以及"直接更新提示"与"更新生成提示的 LLM"两条路线。
2. **搜索空间维度极高**（所有长字符串构成的空间）：需要通过模块化、可组合的提示来缩减空间，涉及 text vs code modules 与软件工程实践。

针对第一点，幻灯片给出两类方法。其一是黑箱搜索式：Zhou et al.（ICLR 2023）"Large Language Models are Human-Level Prompt Engineers"，用 LLM 生成并打分提示。其二是 TextGrad（Yuksekgonul et al., arXiv 2024），把 LLM 反馈当作"文本梯度"做一阶式优化：先针对"给定评估的预测"收集反馈，再针对"给定上述反馈的提示"收集反馈，反馈形式是自然语言，例如"This prediction can be improved by…"。第 26–30 页为 TextGrad 的连续示意页，具体流程图细节在提取文本中不完整，此处只保留其文字描述部分。

针对第二点，幻灯片介绍模块化程序路线。Khattab et al.（arXiv 2023）的 Demonstrate-Search-Predict 把每个 LLM 步骤拆成 retrieve、read 等通用模块。DSPy（Khattab et al., arXiv 2023）则进一步"远离自由字符串操作"，转向编程式组合模块算子、构建文本变换图，并由编译器自动生成优化后的 LM 调用策略与提示。幻灯片明确列出 DSPy 的三类优化方式：

1. **Candidate Generation**：编译器递归找出程序中所有唯一的 Predict 模块，为其参数（instructions、field descriptions、demonstrations）生成候选值。
2. **Parameter Optimization**：用随机搜索或贝叶斯优化等超参数调优算法在候选中选择，幻灯片将其归为离散优化问题。
3. **Higher-Order Program Optimization**：修改程序控制流，例如集成多个副本并行运行并聚合（如多数投票）。

第 35 页的"Context Optimization"小结重申了上述两大挑战与对应路线（TextGrad vs Automated Prompt Engineer；DSPy），并预告下周将进一步讨论用 LLM 优化与搜索程序。

## 五、长上下文模型：三条应对路线

幻灯片先用注意力机制回顾铺垫：注意力为不同 token 提供动态权重，公式为 h = softmax(XW_q W_k^T X^T / √d) XW_v，并标注了"3x3 (weighted) outer product""normalize to 0-1""lazy"等注释。这部分属于背景复习，第 36–37 页为公式示意。

第 38 页仅给出"Long Context Models"标题与一个 needle-in-a-haystack 仓库链接，具体图示未在文本中展开。核心内容在第 39 页：应对长上下文的三种方式。

1. **新架构**：sliding window、sparse、linear attention 等。优点是提升效率、降低计算；缺点是需要重新设计与重新训练。
2. **长上下文训练**：short-to-long training、合成数据、扩展位置编码。优点是扩大上下文窗口、使用简单；缺点是需要数据、成本可能很高。
3. **上下文管理**：上下文摘要、记忆系统、RAG。优点是改善信息管道、可扩展；缺点是依赖检索与记忆质量。

随后的页面（第 40–45 页）来自 CMU AI Agents course fall 2026 的素材，分别展示 full attention 与 sliding window attention、固定全局注意力加滑动窗口局部注意力的 sparse attention、长上下文数据示例（长文档如书籍/代码库/多文档、agent 轨迹的观察+动作+奖励、带受控证据与干扰项位置的合成任务）、位置编码扩展（引用 Chen et al., arXiv 2023 的 Position Interpolation），以及长上下文模型总结页。这些页面以图为主，幻灯片未在文本中给出具体结论，本文仅作标题级归纳。第 46 页引用 Yen et al.（ICLR 2025）的 HELMET 作为长上下文评估方法。第 47 页为整讲小结，与开头目录一致，并列出 guest speaker 与 demo 环节。

## 六、客座报告：Agentic Context Engineering（ACE）

客座部分由斯坦福博士生 Qizheng Zhang 主讲，标注为 ICLR 2026、与 Stanford、SambaNova Systems、UC Berkeley 合作的工作。

### 6.1 问题发现：工具型编码智能体的上下文缺口

案例研究使用 AppWorld 基准：编码智能体在交互式环境中工作，任务多为多轮、长上下文（幻灯片称许多查询超过 10 轮、超过 32K token），并带有定制的工具与 API 定义。幻灯片展示了一个具体失败模式：智能体在执行后续操作前经常忘记先获取用户的 access token，导致运行时报错 `Key "access_token" does not exist!`。手工修复方式是在上下文中写入规则，例如"Principle 1: Always log in to retrieve access token from users as a first step."，置于 System Prompt 与工具列表之侧。幻灯片对此的评论是：智能体常常缺少上下文/程序性知识，而不仅是事实性知识。

### 6.2 三种适应范式对比

幻灯片给出三类适应范式的取舍：

- **Weight updates（微调/RL）**：推理时强且紧凑；但迭代慢、基础设施重、难以审计与回滚。
- **Retrieval（RAG）**：可注入事实、模块化；但对程序与上下文、工具协议、"how-to"知识较弱。
- **Context evolution（本报告）**：测试时快速学习、可解释、模型无关；但长时程下需要稳定性与成本控制。

### 6.3 现有上下文适应方法的两大局限

幻灯片点名 GEPA（prompt optimizer）、Dynamic Cheatsheet（agent memory）等方法存在两个问题：

- **Brevity bias**：偏好简短、简洁、通用的指令。
- **Context collapse**：重写时把上下文压缩成更短、信息更少的摘要。

其机制被概括为一个 Reflector 在 Rollouts 上迭代 Prompt_i → Prompt_i+1，最终导致"Context Collapse!"。据此提出的主张是：上下文不应是简洁摘要，而应是"comprehensive, evolving playbooks"——详尽、包容、富含领域洞见。

### 6.4 核心配方

幻灯片给出 ACE 的两条"recipe"：

- **Recipe #1：增量更新（Incremental Context Update）**。对比"monolithic rewrite → collapse"与"delta updates → stable growth"：Playbook_i 经 Rollouts 得到 Playbook_i+1 时，只施加 Delta Update，从而优雅地扩展模型上下文。
- **Recipe #2：结构化分工（Structured Division of Labor）**：Generator、Reflector、Curator 三个角色分工。第 12–18 页为 ACE 架构的连续示意页，提取文本中只有标题级信息，具体模块交互细节无法从文本确认。

针对"这不就是 prompt engineering 吗"的设问（第 20 页仅标题），幻灯片用系统化形式回应：ACE 把上下文演化定义为一个系统问题——**State** 是把演化上下文作为 first-class citizen 的更好表示，含 sections、itemized bullets + metadata，支持定位、细粒度检索、增量适配、周期性去重与清理；**Update operator** 是 delta updates + deterministic merge，用紧凑增量代替全量重写，保留旧知识、避免坍塌、支持批处理/并行学习；**Architecture** 是自主循环加结构化分工，把执行、洞见提取、整合分离，并允许迭代精炼。

### 6.5 结果与成本

幻灯片给出的结果表述需谨慎对待，因为具体图表数值未在提取文本中完整呈现。可确认的文字结论包括：

- ACE 生成的上下文包含详细的领域特定洞见以及可直接使用的工具与代码，构成面向 LLM 的综合 playbook（AppWorld 部分展示）。
- ACE 在性能上优于 RAG-based ICL 与 prompt optimizers。
- ACE 可以在无监督标签的情况下利用环境反馈演化上下文。
- ACE 可以离线（system prompt）与在线（agent memory）两种方式演化上下文。
- 成本分析：ACE 相比 GEPA 显著降低 token 使用与适配延迟。
- KV cache 复用：ACE 使用更多原始输入 token，但其中 91.8% 可由 KV-cached prompts 服务，减少 82.6% 的计费输入 token 成本。幻灯片据此提出"Longer Context ≠ Higher Serving Cost"。
- 总结页给出：Accuracy 在 agents 上 +10.6%、在 finance 上 +8.6%；效率上显著降低适配延迟与 rollout 成本。这些数字来自幻灯片原文，本文仅转述，未做独立核验。

### 6.6 生产落地与未来方向

幻灯片给出两个生产案例：澳大利亚 SCX.ai 的客服工作流（无 ACE 时聊天机器人"总是退款"，有 ACE 时会要求并核验 order ID 与订单详情）；法国 AnyShift 的平台工程场景（附博客链接）。未来方向包括：把上下文视为测试时持续学习的快速媒介，稳定后再选择性蒸馏进权重；大规模并行上下文学习（Combee, COLM 2026）；记忆系统与 harness 的元演化（Meta-Harness, COLM 2026）；更新安全性与正确性；以及整合式学习（in-context 或 weight-update self-distillation）。结论页重申：上下文演化作为 AI 适应的新范式、现有方法的 brevity bias 与 context collapse、ACE 的提出，以及其支撑自改进智能体与领域 AI 的潜力。

## 七、结语

把两份幻灯片放在一起看，第二讲的叙事是连贯的：它先确立"上下文是模型生成前读到的一切"这一宽定义，再说明上下文对行为的塑造（ICL、CoT、ToT、ReAct、多模态条件化），接着把提示优化形式化为离散、高维的搜索问题并给出 TextGrad 与 DSPy 两条路线，然后用长上下文的三条路线（新架构、长上下文训练、上下文管理）说明"窗口"之外的工程选择，最后以 ACE 把"上下文管理"推进为"上下文演化"——一个有状态、可增量更新、可审计、模型无关的系统对象。

需要再次强调本文的边界：所有内容均来自幻灯片可提取文本，图示、动画与课堂口头解释未纳入；ACE 的架构细节页（第 12–18 页）与多张纯图页存在信息缺失，文中已标注不确定性；幻灯片中出现的实验数字（如 +10.6%、+8.6%、91.8%、82.6%）仅为原文转述，未做独立验证。若需完整理解，应结合讲义原文与课堂录像。

## 参考幻灯片

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec2%20-%20context.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/context_guest.pdf
