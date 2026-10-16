# 从补全到软件工程：CMU 11-768 Lecture 6 如何拆解 Coding Agents

> 待审核候选稿 · 来源：平台字幕与官方 Slides · 尚未发布。

## 一、这节课到底在回答什么问题

如果只看标题“Domains 1: Coding Agents”，很容易以为这是一节工具巡礼：把当下流行的编码智能体列一遍，讲讲它们怎么调用终端、怎么改文件。但 Lecture 6 的组织方式不是这样。它更像是在追问一串递进的问题：

1. 一个“会写代码的语言模型”，和普通语言模型差在哪？
2. 把这样的模型放进智能体循环后，仓库级编码要多出哪些环节？
3. 这些环节里，工具接口的设计为什么能显著改变成功率？
4. 当任务从“修一个 bug”扩展到前端、库实现、CI 修复时，训练和评估要怎么变？

Slides 第 2 页把整个领域切成三层：写代码（单次 completion）、修改仓库（多文件修改）、执行完整开发流程（full software lifecycle）。这三层不是并列的，而是难度与自由度的递进。课堂的讲述顺序也基本沿着这条线：先讲单步代码模型（第 4–30 页），再讲智能体式编码（第 31–45 页），然后是评估与训练（第 46–54 页），最后扩展到前端与更广的开发任务（第 55–72 页），并以代码行为预测收尾（第 73–79 页）。

> **学习者解释**：我理解这节课的核心张力在于——单步模型和智能体的“能力来源”不同。单步模型靠预训练和推理能力一次性给出答案；智能体靠工具、循环和验证把不确定性摊开。课程用大量篇幅处理后者，说明在仓库级任务上，工程接口往往比模型规模更早成为瓶颈。

## 二、单步代码模型：三件事缺一不可

Slides 第 5 页给出写代码的三个要素：**Language（语法、API、惯用法）、Editing（同时依赖两侧上下文）、Reasoning（从规格到行为）**。这三件事看起来朴素，但每一项都对应一种训练决策。

### 2.1 预训练：代码不是普通文本

Slides 第 7 页强调预训练要混合网页文本、技术文章、数学、源码和文档，并保留结构——缩进、文件边界、API、文本与代码的关系。第 8 页讲数据清洗：按语言和来源过滤、去重（fork、vendored 库、近似文件）、记录许可证与来源日期、做敏感数据过滤、防止评测泄漏。

一个课程里反复出现的细节是 **空白字符**。Slides 第 9 页给出 StarCoder2 的分词示例：`if·ready: ↵ ····return·value ↵` 被切成 `if | ·ready | : | ↵ ··· | ·return | ·value | ↵`。也就是说，连续空白被压缩成 token，而不是每个空格一个 token。讲者在课堂上提到，早期曾有把所有空白规范化的做法，这对 Python 是灾难性的，因为空白本身有语法含义。第 9 页还提示，标识符可能跨 token，因此需要对代码友好的子词切分。

> **学习者解释**：分词看似底层，但它决定了模型“看见”代码的粒度。如果缩进被压成一个 token，模型就更容易学到块结构；如果每个空格都是独立 token，序列会变长且结构信号被稀释。这也解释了为什么讨论代码模型时总绕不开 tokenizer。

### 2.2 中期训练与长上下文

Slides 第 11 页引 Code Llama：在 Llama 2 基础上追加 500B token，并扩展上下文，训练相关文件和更长序列。第 12 页给出 Qwen2.5-Coder 的混合比例对比：100/0/0（code/text/math）时 Common code 49.8、MATH 10.3、MMLU 23.8；70/20/10 时为 48.3、33.2、62.9。课程用它说明——纯代码会牺牲通用能力，而混合能在代码几乎不掉的情况下保住数学与问答。

第 13 页讲长输入：把相关文件、路径、跨文件依赖拼成连贯序列；Qwen2.5-Coder 从 8K 训练到 32K，再用 YaRN 扩到 128K；并用跨文件补全、infilling 和短上下文保持来验证。

### 2.3 Infilling：让模型看右侧

Slides 第 14 页的例子非常直观：

```
def is_positive(x: int) -> ____:
    return x > 0
```

只看左侧函数体，返回类型难以确定；但右侧 `return x > 0` 强烈暗示是 `bool`。第 15 页给出机制：训练时把序列写成 `prefix [M0] suffix [M0] span [END]`，推理时放 `prefix [M0] suffix [M0]` 让模型生成 span；多个洞用不同 sentinel。第 16 页的实验数字（HumanEval 派生的 infilling 任务）显示：从左到右单候选 48.2%/24.9%，从左到右 10 候选重排 54.9%/28.2%，因果掩码 infilling 69.0%/38.6%。第 17 页进一步说明，因果掩码训练在标准补全上并不吃亏（HumanEval 8.0% vs 6.0%，MBPP 10.9% vs 8.9%）。

> **学习者解释**：Infilling 的价值不只是“填空”。它把“编辑”这件事变成可训练目标：模型学会同时利用改动点的左右两侧。这正好对应真实开发中“在已有代码中间插入逻辑”的常见动作。

第 18 页列出更多学习信号：commit diff（before + message → after/diff）、诊断（broken code + error → repair）、测试（program + test outcomes → reward）、执行轨迹（program → executed lines + states）。

## 三、评估生成代码：从文本相似到执行

Slides 第 20 页讲参考解比较：精确匹配、BLEU-4。课堂举的例子很能说明问题——`return x > 0` 与 `return x >= 0` 只差一个 token，但在 x=0 时行为不同；而 `return not (x <= 0)` 文本差异大，对整数却等价。第 21、22 页给出 CodeBLEU（比较 AST 与数据流）和 CodeBERTScore（嵌入后做 token 级匹配）作为结构/表示层面的替代。

第 23 页转向执行检查：候选代码在隔离运行时中跑测试用例，比较输出。第 24 页列优缺点：能接受不同正确实现，但有限测试可能漏掉错误行为；能检测语义错误，但需要可信测试、依赖和隔离环境；匹配观测行为，但需要时间和稳定环境。课堂特别强调单元测试的假阳性/假阴性问题：测试不够严格会放过错误实现；而像“右上角好看的按钮”这类需求，测试可能去检查背景色，造成假阴性。讲者说这是当前训练编码智能体的最大问题之一。

第 25 页给出 HumanEval（164 个 Python 函数，docstring → 补全，隐藏单测）与 CodeContests（竞赛题，statement → 完整程序，编译+测试）。第 26 页定义 pass@k。第 27 页补充非功能需求：运行时效率、延迟/资源、可维护性/安全，并提到 NoFunEval 的 397 个代码编辑任务。

第 28 页讲用测试结果做 RL：采样 → 运行测试 → 奖励 → 更新模型。第 29 页用 `1 + … + n` 说明推理如何从“逐个加”走到公式 `n * (n + 1) // 2`，并指出 `n * (n - 1) // 2` 在 n=1 就错。第 30 页展示 DeepCoder 的 RL 后编码准确率曲线，说明 16K→32K 的响应 token 限制与 64K 评估的设置。

## 四、智能体式编码：localize–edit–verify

Slides 第 32 页对比单步与智能体：单步是自包含 prompt → 推理+代码 → 评估答案；智能体是 issue + 现有文件 → 搜索 → 编辑 → 跑测试 ↺ → patch + 证据。第 33 页给出核心循环：**Localize（零在哪里变成默认值？）→ Edit（只在 None 时给默认）→ Verify（零、默认、调用方回归）**，失败则修正假设。

第 34–36 页是贯穿例子。问题代码是 `return config.get("retries") or 3`，因为 0 是 falsy，所以显式零被覆盖。定位用 `rg 'retries'`，复现用单测；编辑改为：

```
value = config.get("retries")
return 3 if value is None else value
```

验证跑四个用例：missing→3、None→3、zero→0、positive→2，全部通过。

第 37 页提到一个替代方案 Agentless：把流程固定为定位文件、类/函数、行，再用单步模型生成补丁。讲者说它曾在一段时间内比智能体更有效，因为模型被大量训练做单步解题，而不是工具调用与验证循环。

### 4.1 工具集：shell-only 够不够？

Slides 第 39 页给出 mini-SWE-agent：只给一个 shell 工具，读写用 rg/cat/find，编辑用 sed/Python/patch，执行用 pytest/build。第 40 页展示用 sed 替换文本的例子。但第 41 页指出问题：整文件写入简单但重复未改代码；search/replace 紧凑但需要无歧义匹配。第 42 页给出 unified diff 和 Codex 的文件操作 patch 语法。第 43 页引用 Aider 的重构基准（89 个 Python 任务，GPT-4 Turbo）：SEARCH/REPLACE 20%，简化 unified diff 61%。

课堂讨论中，讲者提到有些模型在自己的编辑格式上训练，换到别的 harness 就明显变差，这说明 **harness 的格式也是模型能力的一部分**。

> **学习者解释**：这解释了一个常见困惑——同一个模型在不同编码工具里表现差异很大。不一定是模型“变笨”，而是它的训练分布与工具的输出格式不匹配。第 54 页的 multi-harness training 正是对此的回应。

### 4.2 找到相关代码

第 44 页讲从症状出发、沿值追踪；第 45 页给出 LocAgent：沿依赖图检索相关邻域，再用执行验证。

## 五、智能体的评估与训练

第 47 页讲 SWE-bench 的评估流程：用 GitHub issue 和解决时的仓库状态、相关测试，生成补丁后应用并跑测试；fail→pass 表示修复，pass→pass 表示未破坏行为。第 48 页给出可运行训练任务的构成：起始状态（文件+依赖+测试命令）、issue（请求行为+复现）、检查。第 49 页讲多步修复的 RL：搜索、编辑、测试/结束是训练目标；文件、补丁、测试输出是上下文；终局奖励的问题是“晚期失败无法指出早期哪一步错了”。第 50 页提到 SWE-Gym 的 32B 模型与推理期 learned-verifier 选择。第 51–52 页讲 SWE-smith：变异代码而不变异测试，保留新出现的失败，从而程序化生成修复任务。第 53 页讲多语言（Python/TypeScript/Rust）要先读项目配置再决定构建与测试命令。第 54 页讲 multi-harness training：同一权重在 OpenHands、OpenCode、Codex 等多个 harness 上训练，Nemotron 3 Ultra 的说明是每个任务分布至少两个 harness。

## 六、前端与更广的开发任务

第 56 页讲前端智能体：定位组件与事件处理器、改逻辑与样式、在浏览器中验证（type→click→检查状态，截图→视觉理解）。第 57 页对比浏览器智能体与 Playwright 脚本。第 58 页给出修复例子：把 `value.length` 改为 `value.trim().length`，行为检查（0 记录、有效名仍保存）与外观检查（错误可见）。第 59 页特别强调：issue 里带图片，并不意味着用图像相似度评分。

第 61 页给出从需求到维护的完整视图：需求、兼容性、审查、发布决策、部署/监控、维护。第 62 页引用 2019 年微软调查：编码只占 15%，会议+邮件 25%，调试 14%，跑测试 8%，等等。第 63 页用表格比较修复、库创建、测试生成、CI 修复、演化的 artifact、环境/验证器与视野长度。第 64–69 页分别讲定位（CodeScout，F1 三层）、应用创建（ViBench）、库实现（Commit0、ProgramBench）、维护（SWE-Milestone）、测试生成（SWT-Bench）、CI 修复（Node 16 vs >=18 的 EBADENGINE 例子）。第 70–72 页讲跨任务迁移：Base 32B 与 Hybrid-Gym 32B 在 SWE-bench Verified（7→32.4）、SWT-Bench Verified（9.01→16.86）、Commit0 Lite（8.34→13.45）上的对比。

## 七、代码行为预测

第 74 页提出 policy 与 world model 的区分：策略选动作，世界模型预测结果。第 75 页给出别名例子：`items = [1]; alias = items; alias.append(2); result = len(items)`，真实执行 items=[1,2]、result=2，而错误预测会把 alias 当拷贝。第 76 页说明预测何时有用：两个补丁中模型误判 A 失败 B 通过，选错；要用真实执行校验，并同时比较任务成功率与总延迟/token/工具调用。第 77–78 页提到 CWM 与 Code World Models/GIF-MCTS。第 79 页列出开放问题：更好的决策？更低的成本？新的设置？何时执行？

## 八、把课程收束成一张图

第 81 页的结论把六条线并列：代码模型（预训练、中期训练、执行奖励 RL）；智能体编码（localize/edit/verify 与工具）；智能体训练（可运行任务、修复奖励、多样 harness）；前端（浏览器交互与视觉验证）；更广开发（定位、应用、库、维护、测试、CI）；代码行为预测。这六条线共同回答开头那个问题：从“会写代码”到“能交付软件”，中间隔着的不是单一能力，而是一整套接口、验证与训练数据的工程。

> **学习者解释**：如果让我用一句话概括这节课的立场，我会说——编码智能体的进步不是一个纯模型问题。工具格式、测试质量、环境稳定性、harness 多样性，都会直接改变可测量的成功率。这也解释了为什么课程把大量篇幅给了评估与数据构造，而不是只讲模型架构。

## 九、待核事项

- Slides 第 12、16、17、30、43、62、72 页的图示、公式与完整表格需对照官方 PDF 视觉核验；本文引用的数值来自提供的文本提取，标注为“待核”。
- 逐字稿为英文自动字幕清洗稿的机器翻译，存在错词与时间戳；本文凡“课堂提到/讲者说”均以逐字稿为依据，未冒充讲者原话，也不声称经过人工审核。
- 涉及论文年份、作者与具体页码的引用，均以 Slides 提取文本中的标注为准；未能从给定资料确认的细节未作补充。

## 十、官方来源链接

- 课程主页：https://www.cmu-agents.com/
- 课程日程与阅读：https://www.cmu-agents.com/#schedule
- 作业与项目要求：https://www.cmu-agents.com/#assignments
- Assignment 1 · Harness：https://github.com/cmu-agents/assignment-1
- Assignment 2 · Eval：https://github.com/cmu-agents/assignment-2
- 课程视频：https://www.youtube.com/watch?v=1BWeH1oOM7k&list=PLSN0qpDfUvTM&index=6
- Lecture 6 slides：https://www.cmu-agents.com/slides/lecture-06-coding-agents.pdf
