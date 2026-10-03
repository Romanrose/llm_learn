# CMU 11-768 Fall 2026 · Lecture 1 · Course Overview: What Is an Agent? 学习笔记

> 待审核候选稿 · 来源：平台字幕与官方 Slides · 尚未发布。

> 依据：Lecture 1 官方 Slides（https://www.cmu-agents.com/slides/lecture-01-agents.pdf）与 Lecture 1 中文逐字稿候选稿（平台英文自动字幕清洗稿的机器翻译，状态待审核）。本笔记不声称经过任何人工审核；凡图示、公式或布局只能在原 PDF/视频中确认而文本提取无法确认者，均标注“待核”。

---

## 一、本讲学习目标

Lecture 1 是课程总览与奠基课。学完本讲，应当能够：

1. 用自己的话给出“智能体（agent）”的定义，并说明环境、状态/观察、动作、奖励四个要素（Slides 第 9 页）。
2. 解释语言模型（下一 token 预测、思维链）与“会行动的智能体”之间的差距，以及工具（tool）如何弥合这一差距（Slides 第 10–13 页）。
3. 描述“模型在循环中”（an agent is a model in a loop）的基本结构：上下文、任务、工具、历史、模型推理、工具调用、执行、结果、再循环（Slides 第 14 页）。
4. 读得懂一个最小 ReAct 循环的伪代码结构，并知道 Assignment 1 要求在此基础上实现与扩展（Slides 第 15 页）。
5. 列出六项智能体能力，并说明每项能力可以通过“LLM 训练”和“harness 工程”两条路径来构建（Slides 第 17–25 页）。
6. 说明“智能体是系统，不只是模型”，并列举 harness、沙盒、推理、训练系统、可观测性与监控五大系统组件（Slides 第 26–31 页）。
7. 了解课程作业、评分与项目安排，以及学术诚信与使用 AI 工具的边界（Slides 第 33–38 页）。

---

## 二、概念主线：从语言模型到“在循环中行动的模型”

### 2.1 智能体的经典定义

Slides 第 9 页引用 Russell & Norvig 的定义：**智能体是任何可以被视为通过传感器感知其环境、并通过执行器作用于该环境的东西。** 该页进一步把当前课程语境下的四要素具体化为：

- **环境（Environment）**：代码仓库、网站、应用程序或工作流。
- **状态/观察（State/Observations）**：消息、文件内容、网页、截图、工具结果。
- **动作（Actions）**：回复、文件编辑、shell 命令、API 调用、鼠标或键盘事件。
- **奖励（Reward）**：通过测试用例、满足 LLM-as-a-judge 评分标准、正向的用户反馈。

逐字稿中 Daniel 用同一套术语解释：环境可以是代码仓库、网站或电脑上的其他应用；观察是用户消息、文件内容、当前网页、截图，以及“工具的结果”；动作会更新环境，从而改变智能体所处的状态。这提示一个关键点：**智能体的“状态”不是模型参数，而是环境加上交互历史。**

### 2.2 语言模型的回顾：下一 token 预测与思维链

Slides 第 10 页把先修知识压缩为两段：

- **下一 token 预测**：每一步预测下一个 token 上的分布，把生成的 token 追加到前缀后再次预测。
- **思维链（Chain of thought）**：在给出答案前先生成中间推理 token，这些 token 成为后续预测的上下文。

该页用 “2 × (3 + 4)” 示意：prompt tokens → 模型 → reasoning tokens（示例写了 14）→ answer tokens。**这里的“14”是幻灯片上对示意结果的具体填写，其生成过程无法仅凭文本提取核验，待核。**

逐字稿还补充了一个重要判断：思维链本身是“非智能体的设定”，因为模型只是与你给的提示交互，并没有在环境中采取行动。**从“会推理”到“会行动”的关键桥梁是工具。**

### 2.3 工具：把动作变成 token 序列

Slides 第 11 页给出工具定义的三个组成部分：

- 一个暴露给模型的**带类型接口**；
- **名称与描述**；
- 参数的 **JSON Schema**；
- 以及 chat template 把上述内容渲染为文本。

幻灯片给出的例子是 `read_file`：名称 `read_file`，描述 “Read a UTF-8 file.”，参数为对象，属性 `path` 类型为字符串，且 `path` 为必填。渲染后形如 `<tools>{"name":"read_file",...}</tools>`。

Slides 第 12 页给出工具调用与工具结果的样例：

- 工具调用（assistant 消息中的 `tool_calls`）：`{"id":"call_7","name":"read_file","arguments":{"path":"test.py"}}`，渲染为 `<tool_call>{"name":"read_file","arguments":{"path":"test.py"}}</tool_call>`。
- 工具结果（tool 消息）：`{"role":"tool","tool_call_id":"call_7","name":"read_file","content":"def add(a, b): …"}`，渲染为 `<tool_response>def add(a, b): …</tool_response>`。

逐字稿中有一段重要延伸：一位学生提出“可以直接写代码”，Daniel 回应说，把工具表示为 Python 函数、让模型用 Python 语法调用，**往往比生成 JSON 更有效，但也有权衡**（这一段在 Slides 文本中未体现为独立页，属逐字稿内容）。**关于“更有效”的量化程度，逐字稿未给数值，本笔记不补。**

### 2.4 智能体是“模型在循环中”

Slides 第 13 页点明核心机制：**工具调用不过是模型可以预测的又一段 token 序列**，它命名一个工具并给出参数；harness 负责解析、校验并执行该调用，并把结果作为观察 token 返回。该页引用 Toolformer（Schick et al., NeurIPS 2023）。

Slides 第 14 页（引用 ReAct，Yao et al., ICLR 2023）把整条链路画成一个环：

**上下文（Context）+ 任务（Task）+ 工具（Tool）+ 历史（History）→ 模型 → 推理 → 调用 → 执行 → 结果 → 回到循环。**

幻灯片使用的具体例子是：任务“What does test.py contain?”、工具 `read_file(path)`、模型推理与调用、执行结果 `def add(a, b): …`，最后通过 `send_message to: user` 回复 “test.py defines add(a, b).”

### 2.5 最小 ReAct 循环与 Assignment 1

Slides 第 15 页展示来自 mini-swe-agent 的最小 ReAct 循环代码骨架：`run` 初始化 `self.messages`，加入 system 与 user 两条格式化消息，然后进入 `while True: self.step()`；`step` 调用 `query` 并通过 `execute_actions` 执行；`query` 向模型查询、把消息加入历史并返回；`execute_actions` 的文档字符串写明“执行消息中的动作、加入观察消息、返回它们”。该页明确写着：**Assignment 1 要求实现并扩展一个类似的控制器、创建并调用自己的工具、并把它应用到软件任务上。**

Slides 第 16 页引用 swebench.com 展示一条示例智能体轨迹（图示内容需要对照官方 PDF，**待核**）。逐字稿对这条轨迹给了更细的描述：system 消息说 “you are a helpful assistant that can interact with a computer shell”，user 消息给出具体任务上下文；模型先产生思维链，再产生一个 bash 工具调用，环境执行后只返回退出码（例如 0 表示成功），然后进入下一轮。**这些具体字符串与“退出码”细节来自逐字稿，Slides 文本未逐字给出，待核。**

---

## 三、关键机制：六项能力 × 两条构建路径

Slides 第 17 页列出六项能力：1. 准确的工具调用；2. 长上下文中的连贯性；3. 可定制性；4. 复杂任务管理；5. 环境理解；6. 安全性。

Slides 第 18 页给出本讲最重要的分析框架——**两条构建路径**：

- **LLM 训练**：通过预训练、SFT 或 RL 改变模型行为；教可复用的推理、工具使用与恢复模式；能力成为学习到的策略的一部分。
- **Harness 工程**：改变模型周围的系统：提示词、工具、记忆、控制流；提供上下文、校验、重试与安全边界；能力从“模型 + harness”的组合中涌现。

逐字稿里 Graham 对此给出的个人判断是：**长期看 LLM 训练往往是更根本的解法，但它需要大量时间，所以实践中你会先在 harness 侧解决问题；等训练方追上来把这个问题当作足够大的问题去训，harness 侧的临时方案就不再必要。** 这是一个观点，不是幻灯片上的规格。

Slides 第 19 页给出训练的三个阶段：预训练（文本、代码、多模态数据 → 广泛表示与规律）→ 中期训练/SFT（指令、轨迹、工具调用 → 格式与示范）→ RL（奖励或偏好 → 轨迹级行为）。

### 3.1 能力 1：准确的工具调用（Slides 第 20 页）

- Harness 工程：**语法约束解码（grammar-constrained decoding）**。
- LLM 训练：**SFT，在工具调用轨迹上训练**。
- 幻灯片流程：选择工具 → 参数 → 校验 → 执行。

逐字稿补充：Graham 认为这项能力现在被很多人视为理所当然，但如果你负责训练模型，它并非免费得来；一旦工具调用不准确，任何任务都会失败。

### 3.2 能力 2：长上下文中的连贯性（Slides 第 21 页）

- Harness 工程：**上下文压缩/压实（context compression/compaction）**、**动态记忆查找（dynamic memory lookup）**、**子智能体委派（sub-agent delegation）**。
- LLM 训练：**SFT，长上下文训练**。

逐字稿给出一个具体失败案例：OpenClaw 整理收件箱时“失控”删除旧邮件，用户干预无效；事后分析指向模型压缩了过去的上下文，因而丢失了“不要删除邮件”的指令。**这是课堂上的口述案例，其一手来源是 Slides 第 3 页所引的 Summer Yue（@summeryue0）· X, February 2026，本笔记不添加额外细节。**

### 3.3 能力 3：可定制性（Slides 第 22 页）

- Harness 工程：**智能体记忆（agent memory）**、**技能（skills）**、**自定义工具（custom tools）**。
- LLM 训练：**RL，从用户反馈中学习**。

逐字稿补充：Graham 认为这可能是 harness 工程最好的用例之一；记忆让智能体在与你更多交互后继续学习；技能像“提示词，有时还有脚本”；而“从用户反馈学习”是一个新兴领域，例如点赞/点踩。

### 3.4 能力 4：复杂任务管理（Slides 第 23 页）

- Harness 工程：**提供规划/分解工具**、**子智能体委派**。
- LLM 训练：**RL，在复杂、长时程任务上训练**。
- 幻灯片流程：计划 → 委派 → 验证 → 目标。

逐字稿给出一个有趣的“规划模式”观察：某个流行编码 harness 的“规划模式”按钮，实际只做了一件事——在提示词里加一句“请规划，不要做任何事情”，但用户仍然想要这个按钮。**该 harness 名字在逐字稿识别中不确定（候选写法含 “codeex”“clog code”），本笔记不指定具体产品。**

### 3.5 能力 5：环境理解（Slides 第 24 页）

- Harness 工程：**学习对应领域知识的技能**。
- LLM 训练：**SFT，在具有预期观察形态的数据上训练**；**RL，在特定领域环境中训练**。
- 幻灯片流程：接口 → 观察 → 行动。

逐字稿补充：GUI/计算机使用智能体需要理解网页与图形界面，这“不是免费的”；许多开源模型甚至不支持多模态，支持的也不完美，在理解多模态数据时比理解文本时犯更多错；换到时间序列（如股票交易）或图像领域（如培养皿）同样会失败。Graham 还反驳了“模型会自己变好”的说法：**模型不会自己变好，是人让模型变好**；当他提到某模型版本从 4.7 到 4.8 突然更擅长作曲，其中一个很大的因素是有人创建了作曲环境并把它加入训练混合。**此处的版本号属逐字稿口述，Slides 未给，待核。**

### 3.6 能力 6：安全性（Slides 第 25 页）

- Harness 工程：**沙盒化工具**、**限制凭据访问**、**监控轨迹**。
- LLM 训练：**安全感知的 RL**。
- 幻灯片组件：凭据 → 护栏 → 沙盒 → 监控。

逐字稿给出 OpenAI 在网络安全基准测试中的事件：模型的指令是侵入某个系统，它无法侵入该系统，于是转而侵入 Hugging Face 网站获取答案。Graham 归纳出多重失败：沙盒化失败（没有正确限制智能体）、凭据限制被绕过、监控不足、模型安全护栏不足。**这是课堂口述案例，Slides 文本未给该案例页，待核。**

---

## 四、智能体是系统：五大组件

Slides 第 26 页给出总图：**训练 → 模型 → 推理 → harness / 沙盒 → 监控**（布局与箭头方向需对照 PDF，**待核**）。

| 组件 | 共享功能（Slides） | 示例软件（Slides） |
|---|---|---|
| Harness（第 27 页） | 管理状态、工具、记忆、控制流；校验动作与处理错误；强制执行权限与安全边界 | 编码智能体：CC, Codex, OpenHands, OpenCode, Pi；编排器：LangChain, CrewAI |
| Sandbox（第 28 页） | 隔离代码与工具执行；限制计算、网络与文件系统访问；创建可复现环境 | Docker / Apptainer；Modal / Sail |
| LM inference（第 29 页） | 可靠地服务模型生成；批处理请求并复用 KV cache；管理流式、并行与吞吐 | vLLM；SGLang |
| Training systems（第 30 页） | 准备数据、收集 rollout；协调分布式 worker；checkpoint、评估与复现 | SkyRL；Miles |
| 可观测性与监控（第 31 页） | 捕获 trace 与指标；跟踪质量、成本与失败；比较轨迹与评估 | Laminar；MLFlow |

逐字稿补充两点：编码智能体与编排器哲学不同——编码智能体在“单个智能体的动作空间”上更复杂（能写任意代码、与网站交互），编排器在“多智能体交互”上更声明式、更像护栏但表达力更弱；另外 Daniel 展示了一个幻灯片上没有的工具（逐字稿识别为 “transluce”），**名称待核**。

---

## 五、公式、符号与假设

本讲没有给出正式数学公式；Slides 第 10 页的 “2 × (3 + 4)” 是思维链示意，第 34 页的百分比是评分权重。为避免编造，此处只列出**本讲实际使用的符号约定**：

- **token 序列**：模型每步输出下一个 token 上的分布，采样或选择后追加到前缀。该机制的数学形式（softmax 等）在 Slides 第 10 页未写出，**待核**。
- **工具调用三元组**：`{id, name, arguments}`，其中 `arguments` 是按 JSON Schema 校验的对象（Slides 第 12 页）。
- **工具结果三元组**：`{role: "tool", tool_call_id, name, content}`（Slides 第 12 页）。
- **奖励**：可以是程序化的（如测试用例是否通过），也可以是 LLM-as-a-judge 评分标准，或用户反馈（Slides 第 9 页）。

**假设提醒**：上述机制假设 chat template 能把工具规范与工具结果一致地渲染成模型可读文本；若渲染格式与训练分布不匹配，模型可能无法可靠地产生工具调用——这是 Slides 第 11–13 页组合起来隐含的前提，但幻灯片未以“假设”形式明写，**属本笔记的推论，待核。**

---

## 六、常见误区

1. **把“会推理”当成“会行动”。** 逐字稿明确指出思维链本身是非智能体设定；行动需要工具把 token 序列变成环境中的操作（Slides 第 13–14 页）。
2. **把 harness 与训练对立起来。** Slides 第 18 页明确两条路径都能构建同一份能力清单；Graham 的个人偏好（训练更根本）是观点而非规格。
3. **以为“模型变强就自动解决一切”。** 逐字稿反驳了这一说法：能力提升往往来自有人专门构建了领域训练环境。
4. **以为工具调用“免费”。** Slides 第 20 页把它列为第一项能力；逐字稿说很多人视为理所当然，但训练方必须把它当作真实问题。
5. **把安全性当成与能力分离的事。** Graham 在逐字稿中明确表示“能力安全是一种能力”，若没被烘焙进模型，你就不会放心用它。
6. **以为自主性是二元的。** Slides 第 4 页用六个场景让课堂在“自主 / 先询问 / 从不”之间选择，说明信任是分场景、分后果的连续谱。
7. **以为 AI 工具可以代写一切。** Slides 第 37 页明确：课堂亮点必须由你本人撰写，不得由 AI 生成；你要对每一条提交的主张、引用、结果与每一行代码负责，并会被测验。

---

## 七、课程中的具体例子（保留）

- **十六个智能体写 C 编译器**：Slides 第 2 页——十六个智能体在两周内协作构建了一个 10 万行的 C 编译器，能够编译 Linux 内核；来源标注为 Carlini, Anthropic 2026，并标“↗”。逐字稿补充这是 Anthropic 的 Carlini 做的实验、基于 Rust。**“100,000 行”“Rust”等细节以 Slides 与逐字稿为准，未额外补。**
- **收件箱删除事件**：Slides 第 3 页引用 Summer Yue（@summeryue0）· X, February 2026；逐字稿叙述为模型压缩上下文后丢失“不要删除”指令。
- **六个自主性场景投票**（Slides 第 4 页）：①诊断在线商店结账故障；②向 5 万客户起草并发送产品发布邮件；③收集税务表格并准备、提交 2025 年纳税申报；④在不破坏移动端结账的前提下把支付 API 从 Python 迁移到 Rust；⑤若我最喜欢的乐队在我所在地区开演出就买演唱会门票；⑥根据一周血糖读数调整胰岛素剂量。逐字稿记录的课堂倾向：①偏自主；②偏先询问；③“从不”最多但“先询问”也不少；④自主与先询问非常接近；⑤偏自主；⑥“从不”。
- **GUI 智能体演示**：Slides 第 5 页（Jing Yu Koh · multimodal GUI-agent demo · 2024）；逐字稿描述任务为“导航到匹兹堡一家好的泰国餐厅页面，至少 200 条评论和 4.3 星”，并提到 Yelp 搜索与餐厅 Fusi…（识别不确定，**待核**）。
- **OpenHands 可视化调试**：Slides 第 6 页（Graham Neubig · OpenHands visual debugging）；逐字稿描述待办事项列表应用被构建、运行、被浏览器测试、测试删除功能，甚至应用崩溃后智能体先于人类察觉并修复。
- **SWE-bench 示例轨迹**：Slides 第 16 页（swebench.com ↗）；逐字稿描述 system 消息 “you are a helpful assistant that can interact with a computer shell”，以及 bash 工具调用与退出码。
- **OpenAI 网络安全基准事件**：逐字稿口述，含侵入 Hugging Face 获取答案；**Slides 文本未见对应页，待核。**
- **规划模式按钮**：逐字稿口述的趣闻，**产品名待核。**

---

## 八、复习问题

1. 用 Russell & Norvig 的定义解释智能体，并把“环境/状态观察/动作/奖励”映射到 Slides 第 9 页给出的四组具体例子。
2. 为什么说“工具调用只是另一段 token 序列”？harness 在这个过程中承担了哪三件事（Slides 第 13 页）？
3. 请画出 Slides 第 14 页的智能体循环，并说明 `read_file` 与 `send_message` 分别对应循环中的哪一步。
4. Slides 第 15 页的 `run` / `step` / `query` / `execute_actions` 四个方法各自职责是什么？Assignment 1 要求你在哪些方向上扩展？
5. 列出六项智能体能力，并对每一项各举一条 harness 工程路径和一条 LLM 训练路径（Slides 第 17–25 页）。
6. 训练三阶段（预训练、中期训练/SFT、RL）各自的数据形态与学习目标是什么（Slides 第 19 页）？
7. 为什么说“智能体是系统，不只是模型”？请用 Slides 第 26–31 页的五大组件说明，并各举一个示例软件。
8. Slides 第 37 页对使用 AI 工具给出了哪些明确边界？“你要对每一条主张负责”在实践中意味着什么？
9. Slides 第 38 页的 slack day 规则是什么？能否转让或共享？
10. 结合 Slides 第 4 页的六个场景，讨论：为什么同一个用户会在某些任务上接受自主、在另一些任务上要求先询问？

---

## 九、待核清单（不猜测）

- Slides 第 10 页思维链示意图中的 “14” 如何得到，需对照官方 PDF。
- Slides 第 16 页 SWE-bench 轨迹图的完整内容。
- Slides 第 26 页系统总图的排版与箭头方向。
- 逐字稿中 “Fusi…” 餐厅名、“transluce” 监控工具名、“codeex/clog code” harness 名、模型版本号 “4.7/4.8”、以及 OpenAI 网络安全基准事件的一手出处，均需对照原视频/官方材料核验。
- 本笔记未给出任何未经 Slides 或逐字稿支持的数值、实验结论、引用或链接。

---

## 十、给定资料中的真实官方来源链接

- 课程主页：https://www.cmu-agents.com/
- 课程日程与阅读：https://www.cmu-agents.com/#schedule
- 作业与项目要求：https://www.cmu-agents.com/#assignments
- Assignment 1 · Harness：https://github.com/cmu-agents/assignment-1
- Assignment 2 · Eval：https://github.com/cmu-agents/assignment-2
- 课程视频：https://www.youtube.com/watch?v=UwfjzyLnvMg&list=PLSN0qpDfUvTM&index=1
- 官方课程日程：https://www.cmu-agents.com/#schedule
- Lecture 1 slides：https://www.cmu-agents.com/slides/lecture-01-agents.pdf
