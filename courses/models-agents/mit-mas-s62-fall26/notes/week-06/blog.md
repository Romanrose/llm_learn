# 从 Harness 到多智能体进化：Self-Evolving AI 第六周技术综述

> 基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。本文只依据两份官方幻灯片的抽取文本写作，页面重复、页码与 OCR 失真不视为论证依据；凡幻灯片未给出或抽取不完整的图表、数据，文中明确保留不确定性。

## 一、主线：模型不变，harness 决定一切

本周两份幻灯片的共同主题可以概括为一句话：**Agent = Model + Harness**。Harness 是包裹在模型外面的全部代码——它组装上下文、执行控制循环、提供工具、施加安全约束。第一份幻灯片（Ao Qu，Harness Engineering）从工程实现角度拆解 harness 的每个部件；第二份幻灯片（Paul Liang，Multi-Agent Evolution）则把视野从单个 harness 扩展到多智能体系统，并讨论如何让多智能体结构本身被自动进化。

两张幻灯片给了这条主线两个关键证据。其一，Terminal-Bench 的排行榜显示，在同一个模型下切换九种 harness，成功率从 58.0% 提升到 76.4%。其二，HarnessTax 的工作指出，同一模型在相近成功率下可能付出约两倍的成本。这两个数字并置的含义是：harness 既影响能力上限，也影响成本效率，它不是可有可无的脚手架，而是决定 agent 实际表现的核心变量。幻灯片未给出这两项研究的完整实验设置，本文不对其细节做推断。

## 二、Agent Loop：模型与 harness 的分工

ReAct 风格的 agent 循环在幻灯片中被拆成 Task → Thought → Action → Observation → Answer。幻灯片明确回答了"哪部分属于模型、哪部分属于 harness"：Thought、Action、Answer 由模型产生；执行 Tool、把 Observation 写回上下文、维持循环，是 harness 的职责。

用代码表达，循环极简：维护 `messages` 列表，反复调用模型，把回复追加为 assistant 消息，由 harness 解析出 action；若没有 action 则视为最终答案返回；否则执行工具，把输出作为 user 消息追加回上下文。Codex 的版本则说明"一个 turn = 多次模型调用，直到没有工具调用为止"，下一轮再把完整历史送回模型。

幻灯片还给了一个容易被忽视的细节：模型第一次看到的东西远不止用户输入。Codex 的 `gpt-5.2-codex_prompt.md` 在用户输入前就约 47k tokens，而仓库内容并不在 prompt 里，需要模型用工具去读。这提示 harness 的"上下文组装"本身就是一个设计空间：什么预置、什么按需读取。

## 三、深挖 mini-swe-agent：约 100 行的 harness

第一份幻灯片用最大篇幅解剖 mini-swe-agent，它的设计约束是：约 100 行代码、bash 是唯一工具、线性历史、每个 action 一个子进程、SWE-bench Verified 超过 74%。这个小例子几乎覆盖了 harness 工程的所有核心决策。

**限制检查。** `query()` 在每次模型调用前检查 `n_calls` 与 `cost` 是否超限，超限抛 `LimitsExceeded`。幻灯片的自问自答解释了原因：不会提交的 agent 会无限循环，步数或成本上限是终止它的手段。

**动作解析。** `parse_action()` 用正则从回复中提取恰好一个 bash 代码块；数量不为 1 时抛 `FormatError`，错误信息作为下一条消息回给模型，让模型自己修正格式。这是"错误即反馈"的最小实现。

**动作执行。** `execute_action()` 为每条命令起一个 `subprocess.run`，30 秒超时；超时抛 `ExecutionTimeoutError`，提示模型换一种做法。幻灯片特别讨论了为什么不保持一个长驻 shell：单 shell 下 harness 难以判断输出何时结束，且一条坏命令会污染后续所有步骤；代价是 `cd` 和 `export` 不跨命令保留，所以模型要写 `cd src && pytest` 这样的复合命令。

**观察截断。** 模板把返回码与输出包进 `<returncode>`/`<output>`；输出超过 10000 字符时只保留首尾各 5000 字符，中间标注省略字符数，并提示用 head/tail/sed/更窄的 grep。幻灯片解释：完整日志会淹没上下文，而开头和结尾通常已说明运行了什么、怎么失败的。

**异常作为控制流。** `run()` 里所有问题都以异常形式冒出，在顶层统一处理：`NonTerminatingException`（格式错误、超时）转为消息回给模型继续；`TerminatingException`（已提交、超限）结束运行并返回类型名与信息。这种"深层抛、顶层收"的结构让错误处理集中在一处。

**人在回路。** `InteractiveAgent` 在 confirm 模式下执行前询问用户：回车即执行；输入其他内容则抛 `NonTerminatingException`，把用户拒绝理由作为下一条消息交给模型，例如"不要升级 Django，去修 validator"。

**真实任务轨迹。** 幻灯片展示了一个 django-11099 任务：system 消息要求"回复必须恰好包含一个 bash 代码块、一条命令"；step 1 用 `find`+`grep` 定位 validator 文件；steps 2–23 复现、用 sed 编辑、跑测试；step 24 用 `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT && git add -A && git diff --cached` 提交。幻灯片标注 24 步、$0.19、隐藏测试通过，并注明轨迹来源为 SWE-bench bash-only run。这些是幻灯片给出的单次运行数字，本文不将其推广为普遍结论。

## 四、工具设计：给 agent 设计，而非给人设计

幻灯片并列了 Claude Code 与 Codex 的必备工具：Read、按名搜索（Glob / rg --files）、文本搜索（Grep / rg）、编辑（Edit+Write / apply_patch）、执行（Bash / exec_command）、Web、Plan、委派（Agent / spawn_agent）、询问用户。而 mini-swe-agent 仅靠 bash 就覆盖了读、搜、改、执行四类。

同一个编辑任务在三种 harness 下形态迥异：Claude Code 用 `old_string`/`new_string` 的字符串替换；Codex 用 apply_patch 的 diff 格式；mini-swe-agent 直接写一条转义复杂的 `sed -i`。这说明工具接口不是中立的，它塑造模型的动作分布。

幻灯片的工具格式一节指出：schema 随请求发出，模型看到的是 name + description + schema，因此 **description 就是 prompt**。Anthropic 的 SWE-bench 案例中，对 `str_replace_editor` 描述的精修把 Claude 3.5 Sonnet 推到 49% SWE-bench Verified（幻灯片标注此前最佳 45%），其原话是"在精修工具描述后取得 state-of-the-art"。

两个反面/正面案例值得记住。Vercel 的 text-to-SQL agent 把 17 个工具砍到 2 个后，成功率从 4/5 升到 5/5，平均时间从 274.8s 降到 77.4s，token 从约 102k 降到约 61k，步数从约 12 降到约 7。SWE-agent 的对比更反直觉：无搜索工具 15.7%，模仿编辑器 Ctrl+F 的迭代搜索只有 12.0%，而"一次列出所有匹配、超过 50 条则要求更窄查询"的汇总式搜索达到 18.0%——照搬人类编辑器的交互反而最差。此外，简洁输出（concise 72 tokens vs detailed 206 tokens）与"告知下一步怎么做"的错误信息，都是把工具输出当作 prompt 来设计。

那么 bash 还是专用工具？幻灯片的答案是"both: bash for breadth, tools for guarantees"。专用工具带来权限分级（Read/Grep 免询问、Bash 需询问）、并行（读类并行、Edit/Bash 串行）、精确编辑（Edit 在 0 或 2+ 匹配时失败，sed 则照样退出 0）、可撤销（rewind 能恢复 Edit 改动，但恢复不了 Bash 里的 rm/mv）。CodeAct 的数据（代码动作 74.4% vs JSON 工具调用 52.4%）与 Cloudflare 的观察（"LLM 见过大量代码，没见过大量 tool call"）支持 bash 一侧；mini-swe-agent 的 74.4% 也来自 bash-only。

## 五、扩展机制：Skill、MCP、Hook、Plugin

幻灯片用一张对照表区分四种扩展：Skill 是过程性知识，由模型或 `/name` 触发，常驻上下文约 100 tokens；MCP 是外部工具，由模型调用，常驻的是工具名；Hook 是生命周期事件上运行你的代码，由 harness 总是触发，常驻上下文为零；Plugin 是以上打包，由用户安装。另有一行提醒：CLAUDE.md / AGENTS.md 总是加载、从不强制执行。

Skill 的格式是一个文件夹：必需的 `SKILL.md`（frontmatter 的 name ≤64 字符、小写连字符、与文件夹同名；description ≤1024 字符说明做什么、何时用），可选的 scripts、references、assets。幻灯片强调一个开放标准：Claude Code、Codex、Gemini CLI、GitHub Copilot、Cursor 读同一份 SKILL.md。其核心设计原则是 **Progressive Disclosure**：frontmatter 常驻（约 100 tokens/skill），正文在触发时加载（<5k tokens），捆绑文件按需读取。

MCP 用一套 JSON-RPC 消息统一 host、client、server：`tools/list` 发现、`tools/call` 调用；传输为本地 stdio 或远程 HTTP。幻灯片给出 weather.py 示例与 `claude mcp add` 命令，并强调"每个 host 和 server 只实现一次 MCP，而不是每对组合写一个连接器"。Host 是运行 agent 的应用，为每个 server 建一个 client，决定模型看到什么；client 是 harness 的一部分，与恰好一个 server 保持一条双向连接；server 提供 tools、resources、prompts。

Hook 挂在 SessionStart、PreToolUse、PostToolUse、Stop 等事件上，是确定性的代码。Plugin 通过 marketplace 安装，`plugin.json` 只有 name 必填。Q&A 页给出选型直觉：禁读 secrets 用 PreToolUse hook + deny 规则 + sandbox；每次编辑后格式化用 PostToolUse；接 Google Calendar 用 MCP；代码评审清单用 Skill；"总是用 uv 不用 pip"写 CLAUDE.md；跨 20 个仓库共享整套配置用 Plugin。

## 六、上下文：有限资源与缓存经济学

幻灯片引用 Context Rot 的研究：focused 约 300 tokens、full 约 113k tokens，每个模型都会随输入变长而性能下降，目标是"最小的高信号 token 集合"。

Prompt Caching 给出缓存输入 0.1× 价格的三条纪律：静态内容放前面、只追加不修改、工具顺序稳定。反例同样清楚：在顶部放时间戳会导致每次调用都 miss；会话中途 MCP 新增工具会让工具部分起 miss；用户输入新消息则是追加，能命中。这些小例子把"上下文布局即性能"具体化了。

保持上下文小的手段有五种：截断输出、掩码旧观察、压缩摘要、卸载到文件、隔离到子 agent。幻灯片引用 The Complexity Trap 的结论：掩码约等于摘要，成本减半。mini-swe-agent 的首尾截断与错误回灌，正是这一原则在百行代码里的落地。

## 七、Plan Mode、Memory、Subagents

Plan Mode 被明确回答为"不是另一个 harness，也不是另一个模型"：同一个模型、同一个循环，harness 只切换状态——多一条"只研究、不提改"的指令，编辑被阻止，shell 超出只读集需批准，并用 EnterPlanMode/ExitPlanMode 切换与请求批准。计划写在 `~/.claude/plans/<plan>.md` 文件里，幻灯片解释原因：对话会被压缩或清空，文件能存活，harness 可以把它放回去，模型也能随时重读。计划文件包含 Context、Steps、Not doing 三节，用户可 Ctrl+G 先编辑再批准。

Memory 是"harness 重新加载的文件"：CLAUDE.md 由人写、每次会话加载；auto memory 由 Claude 写、`/memory` 打开文件夹，含 MEMORY.md 索引与条目文件，条目带 name、description、metadata.type（如 feedback），并用 Why / How to apply 结构化。

Subagent 在自己的上下文里工作，只把结果带回来——幻灯片举例：读了 6100 tokens 只返回 420。这是"隔离"手段在上下文管理中的直接应用。

## 八、多智能体：何时帮助、何时伤害

第二份幻灯片先给 harness 的六部件框架：Context（prompt、memory、检索）、Control（规划、路由、多智能体编排）、Action（工具、skill、RAG、API）、Evaluation、Evolution（反思、更新、学习）。随后进入规划与任务分解：CoT、least-to-most 提示、规划器/执行器分离（大模型出高层计划、7B 执行模型映射为坐标动作）、web agent 的高层推理+观察解析+底层动作三段结构、人在回路澄清、用教师模型合成计划做 SFT、多次采样估计计划不确定性、具身环境中的重规划、以及"不只思考、要执行、看反馈、重试"的测试时交互。

多智能体部分区分去中心化（多实例提议、互评、辩论）与中心化（编排者+执行者）。幻灯片反复强调：**更多 agent 不自动更好**。它引用的五项发现值得逐条记录：

1. 只在特定任务上有效：财务 agent 多智能体 +81%（任务自然可分解），PlanCraft −70%（顺序依赖，拆分反而有害）。经验法则：可并行→中心化；需探索→去中心化；顺序依赖→单 agent。
2. 不同基座模型成本-性能权衡不同：OpenAI 随成本上升性能平台化，Google 更高成本更高性能，Anthropic 上 MAS 可能伤害性能。
3. agent 数量增加不总提升：工具密集型任务（如 16 工具工作流）受协调开销拖累，环境越复杂惩罚越叠加。
4. 异构 agent 混合可胜过更强基座：单 agent 基线 >45% 时 MAS 有害；便宜编排者+昂贵执行子 agent 似乎效果好。
5. 性能可预测：以模型、任务、MAS 配置为参数的 scaling law 在 87% 情况下预测最佳架构——从"试试某种配置"走向更有原则的 agent 设计科学。

幻灯片未展示这些发现背后的完整实验表，本文不补充具体基准细节。

## 九、多智能体进化：CORAL

既然 MAS 依赖任务、基座模型、拓扑等关键超参数且不总有效，第二份幻灯片提出把 MAS 设计空间自动化，即可进化的对象有三层：个体模型与 agent（模型、上下文、harness）、多智能体系统（角色、通信、拓扑）、共享信息（公共记忆、工具、skill）。

CORAL 是幻灯片给出的实例，关键思想四条：多智能体专业化、更高自主性、共享记忆、heartbeat 机制。应用面覆盖 kernel engineering、运筹、系统工程、科学发现；幻灯片称其在数学、算法、系统优化 8 项任务上取得新 SOTA，多智能体进化相对单 agent 的增益在 4%–20% 区间。分析部分给出三组观察：知识积累（笔记与 skill 记忆）的重要性；多 agent 协同进化优于多个独立 agent；跨 agent 信息转移——kernel engineering 上 36% 的尝试以另一个 agent 为父代，这些尝试改进率 17%，而全部尝试为 9%；探索多样性——agent 词汇重叠 Jaccard 0.3–0.4，即过半探索是独有的；贡献均衡——各 agent 进化尝试数与成功率大致相当。这些是幻灯片报告的数字，本文按原样转述，不作外推。

## 十、安全：Lethal Trifecta 与权限/沙箱

第一份幻灯片的安全部分围绕 Simon Willison 的"致命三元组"：agent 读到藏有指令的 GitHub issue（不可信输入）、能读 .env（访问敏感数据）、能用 curl 把数据发出去（外发通道）。三者齐备，攻击者即可取走数据；去掉任何一个，攻击失败。

防御分两层。权限规则由 Claude Code 自己在执行前检查每个工具调用，如 allow `Bash(pytest *)`、deny `Read(./.env)`。沙箱由操作系统强制（macOS Seatbelt、Linux bubblewrap），命令及其子进程只能读写允许的文件、只能访问白名单域名。幻灯片的对照表揭示了单靠权限规则的漏洞：`Read` 工具打开 .env 会被规则挡住，`cat .env` 也被挡住，但 `python -c "print(open('.env').read())"` 能穿过权限规则（规则不知道 Python 在读 .env），却被沙箱的 denyRead 挡住。这正是"规则+沙箱"必须并用的原因。

## 十一、结语

把两份幻灯片合起来看，harness engineering 的轮廓相当清晰：模型负责思考与出动作，harness 负责执行、反馈、预算、截断、缓存、计划、记忆、隔离与信任边界。mini-swe-agent 证明这些职责可以用约 100 行代码实现；Claude Code 与 Codex 的对比证明接口选择（bash vs 专用工具、字符串替换 vs patch）会改变模型行为；Vercel 与 SWE-agent 的实验证明"少而精、面向 agent 设计"的工具往往优于"多而全、面向人设计"的工具。当视野扩展到多智能体，结论从"harness 决定表现"延伸为"拓扑与任务结构共同决定表现"，并进一步指向用进化方法自动搜索这个设计空间。第一份幻灯片的总结页说得好：harness 补上模型做不到的事——行动、了解项目、扛住错误、装进窗口、保持正轨、记住、并行、被信任；但它"无法让模型想到它不知道的东西"。这句话既是本周的边界，也是下周"模型进化"的引子。

---

官方幻灯片来源：
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/harness%20engineering%20tutorial.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec5%20-%20multi%20agent.pdf
