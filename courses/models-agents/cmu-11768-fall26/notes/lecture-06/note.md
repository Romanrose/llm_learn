# CMU 11-768 Fall 2026 · Lecture 6 · Domains 1: Coding Agents 学习笔记

> 来源：平台字幕与官方 Slides。内容已由用户审核确认。

> 依据：Lecture 6 官方 Slides 逐页文本提取（待核）与中文逐字稿整理稿（机器翻译、待审核）。本笔记已由用户审核确认；图示、公式与数值若无法从文本确认，均在文中标注“待核”。关键论点标注 Slides 页码；仅有逐字稿支撑的内容标注为“逐字稿”。

---

## 一、学习目标

学完本讲后，应当能够：

1. 区分三类“会写代码”的能力层次：**单步补全**、**修改代码仓库**、**承担完整软件开发生命周期**（Slides 第 2 页）。
2. 说明构建编码智能体的三个基本要素——Prompt、Tools、LLM——并解释本讲为何重点放在 Tools 与 LLM 两部分（Slides 第 3 页；逐字稿说明提示与记忆已在前两讲覆盖）。
3. 描述编码模型训练的三个阶段：**预训练**、**中期训练（含 SFT）**、**RL 后训练**，以及每个阶段中编码特有的细节（Slides 第 6 页）。
4. 解释为什么“编辑（Editing）”与“推理（Reasoning）”是代码模型区别于通用语言模型的关键能力（Slides 第 5 页）。
5. 说明填充（infilling）目标如何把“挖空—预测”转化为自回归任务，并理解其收益与对普通补全的影响（Slides 第 14–17 页）。
6. 区分多种代码评估范式：与参考解比较、结构比较、嵌入比较、执行检查，并说明各自的优缺点（Slides 第 20–24 页）。
7. 描述编码智能体的“定位—编辑—验证”循环，以及工具集设计（尤其文件编辑格式）对性能的影响（Slides 第 33、41–43 页）。
8. 解释 SWE-bench 风格任务如何构造、fail-to-pass / pass-to-pass 的含义，以及通过变异注入 bug 生成训练数据的思路（Slides 第 47、51–52 页）。
9. 概述更广泛的软件工程任务（前端开发、库实现、测试生成、CI 修复、维护等）及其评估方式（Slides 第 56–72 页）。
10. 初步理解“代码行为预测 / 世界模型”的动机、风险与开放问题（Slides 第 74–79 页）。

---

## 二、概念主线

本讲的主线可以概括为：**从“会写一段代码”到“会改一个仓库”，再到“会做软件工程”，每一步都需要新的数据、新的工具与新的评估方式。**

### 2.1 三个层次（Slides 第 2 页）

- 单次补全（single completion）：给提示，产出一段代码。
- 修改仓库（modify multiple files）：在既有代码库中定位、修改多个文件。
- 完整开发（full software lifecycle）：需求、评审、部署、监控、维护等。

逐字稿中 Graham 明确说，本次讲的重点是 Tools 与 LLM，因为 Prompt/记忆已在前两讲讨论（逐字稿）。这提示我们：编码智能体的“难点”更多在于**模型能力**和**工具接口设计**。

### 2.2 单步代码模型的三种能力（Slides 第 5 页）

- **语言（Language）**：语法、API、惯用法。
- **编辑（Editing）**：需要同时看到缺口两侧（condition on both sides）。
- **推理（Reasoning）**：从规格到行为。

逐字稿中老师强调编辑“不是免费得到的，需要训练进模型里”，并举了 Python 空白字符有意义、不能随意归一化的例子（逐字稿；对应 Slide 第 7–9 页“preserve structure / preserve whitespace”）。

### 2.3 训练三阶段（Slides 第 6 页）

1. 预训练：大规模含代码语料。
2. 中期训练：代码混合比例、更长上下文。
3. RL 后训练：推理 + 执行奖励。

这条主线贯穿全讲：数据清洗、分词、填充、评估、RL、智能体循环、多脚手架训练，最后延伸到世界模型。

---

## 三、关键机制

### 3.1 预训练：从代码与文本中学习

Slides 第 7 页给出的损失写法为下一 token 预测（示意）：

$$
L_{LM} = -\mathbb{E}_{x\sim D_{mix}} \sum_t \log p_\theta(x_t \mid x_{<t})
$$

**符号与假设（据 Slide 第 7 页文本）：**
- $D_{mix}$：混合数据分布（网页文本、技术文章、数学、源代码、文档）。
- $x_t$：第 $t$ 个 token；$x_{<t}$ 为其前缀。
- $p_\theta$：参数为 $\theta$ 的模型。
- 假设：标准自回归分解；损失对序列中各位置求期望。该公式的完整排版与是否含归一化常数**待核**（PDF 文本提取可能丢失上下标）。

Slides 第 7 页还列出三条原则：混合来源（Mix sources）、保留结构（Preserve structure：缩进、文件边界、API、文本—代码关系）、训练中评估（按领域留出损失 + 功能性编码任务）。

**数据选择与清洗（Slides 第 8 页）：**按语言与来源过滤、去重（fork、vendored 库、近乎相同的文件、复制的解法）、来源控制（许可证、日期、退出、敏感数据过滤）、防止泄漏（按仓库或问题族切分、去污染评测任务）。逐字稿中提到 StarCoder 论文与 trufflehog 之类的敏感数据工具（逐字稿）。

**分词（Slides 第 9 页）：**字节级 BPE；保留空白；压缩高频空白串。Slide 给出的示意为 `if·ready: ↵ ····return·value ↵` 的分词结果，**具体切分需对照 PDF 核验**。逐字稿讨论了两点：把空白与非空白分开分词是常见做法，理由是避免输出“半个单词”；但如果允许跨空白合并，可显著减少 token 数，代价是自动补全等场景可能出现超长 token（逐字稿）。

**规模（Slides 第 10 页）：**StarCoderBase 15.5B 参数、1T token、80+ 语言，来源包括源码、issue、commit、notebook；并称“多数语言随 token 增加而提升”。坐标轴含义见 Slide 文本（横轴训练 token，纵轴 pass@1）。

### 3.2 中期训练：加代码、加长上下文

Slides 第 11 页：继续语言模型训练，提高代码曝光同时保留文本与数学；经验性地选混合比例；Code Llama 在 Llama 2 基础上追加 500B token（7B/13B/34B）；随后扩展上下文，用相关文件与更长序列。

Slides 第 12 页给出混合比例对比表（Code/text/math 与 Common code、MATH、MMLU）：

- 100/0/0：49.8 / 10.3 / 23.8
- 70/20/10：48.3 / 33.2 / 62.9

逐字稿解释：纯代码配方在代码上略好，但在数学与问答上明显变差；加入文本与数学后代码仅有小降、其他能力保住（逐字稿；数值以 Slide 第 12 页为准）。

Slides 第 13 页：一致序列（相关文件、路径、跨文件依赖）；Qwen2.5-Coder 从 8K 训练到 32K，YaRN 支持 128K；用跨文件补全、填充、短上下文保持来验证。逐字稿补充：把所有文件直接拼接常常超过最长上下文，Google 单体仓库据称有数十亿行（逐字稿，**该数字需核**）。

### 3.3 填充（Infilling）

Slides 第 14 页给出经典例子：

```python
def is_positive(x: int) -> ____:
    return x > 0
```

只看左侧无法确定返回类型，而右侧函数体提供了 `bool` 的证据；正确补全为 `bool`。

Slides 第 15 页给出机制：训练序列为 `prefix [M0] suffix [M0] span [END]`；推理为 `prefix [M0] suffix [M0] → 生成 span`。多个洞用不同哨兵（M0、M1……）关联位置。可零样本执行：补全代码、推断类型、生成注释、重命名变量。

Slides 第 16 页给出通过率对比（HumanEval 派生填充任务）：

| 推理方法 | 单行 | 多行 |
|---|---|---|
| 从左到右，1 个候选 | 48.2% | 24.9% |
| 从左到右，10 个候选 + 重排 | 54.9% | 28.2% |
| 因果掩码填充 | 69.0% | 38.6% |

逐字稿强调“这完全不需要重排”，仅靠填充式推理就能接近大幅改进（逐字稿；数值以 Slide 第 16 页为准）。

Slides 第 17 页给出目标函数消融（相同 52B token 训练预算）：

- 从左到右语言建模：HumanEval 6.0%、MBPP 8.9%
- 因果掩码：HumanEval 8.0%、MBPP 10.9%

逐字稿评论：这说明加入填充训练**并非**要与标准补全做取舍（逐字稿；数值以 Slide 第 17 页为准）。

### 3.4 更多从代码中学习的方式（Slides 第 18 页）

- Commit diffs：before + message → after/diff（OctoPack）。
- Diagnostics：broken code + error → repair（DrRepair）。
- Tests：program + test outcomes → reward（CodeRL）。
- Execution traces：program → executed lines + states（CodeExecutor）。

逐字稿补充：CI 测试历史是“几乎免费”的丰富数据来源；测试与执行轨迹相关（逐字稿）。

### 3.5 评估生成代码

**与参考解比较（Slides 第 20 页）：**exact match、BLEU-4（token n-gram 重叠 + 简短惩罚）。Slide 用整数正负判断举例：`return x > 0` 与 `return x >= 0` 只差一个 token，但行为在 0 处不同；`return not (x <= 0)` 文本差异大但语义等价。

**结构比较（Slides 第 21 页）：**CodeBLEU，基于抽象语法树与数据流匹配。

**嵌入比较（Slides 第 22 页）：**CodeBERTScore，编码提示与每个代码片段，比较上下文 token 向量，最佳匹配得到精确率/召回率/F 值。

**执行检查（Slides 第 23 页）：**对候选代码在隔离运行时中运行测试用例，比较输出；Slide 给出 `is_positive` 在 −1、0、1 上的失败示例（0 处返回 T 而期望 F）。

**优缺点（Slides 第 24 页）：**可接受不同正确实现、能通过执行检测语义错误、与观测行为一致；但有限测试可能漏掉错误行为、需要可信测试与隔离依赖、需要时间与稳定环境。逐字稿进一步指出：好的单元测试极难写，某些基准的测试存在假阳性或假阴性，例如界面上“了解更多”按钮的测试可能连背景色一起检查（逐字稿）。

**基准（Slides 第 25 页）：**HumanEval（164 个 Python 函数，docstring → 补全，隐藏单元测试）；CodeContests（竞赛题，statement → 完整程序，编译 + 测试）。

**pass@k（Slides 第 26 页）：**k 次采样中至少一次通过所有测试的概率。

**非功能需求（Slides 第 27 页）：**NoFunEval 提出运行时效率（跑测试 + 计时，得分 speedup）、延迟/资源（对比参考编辑，DiffBLEU）、可维护性/安全（静态检查 + 编辑匹配，CodeQL × DiffBLEU）；共 397 个代码编辑任务。逐字稿补充说：对非智能体任务，效率基本没被纳入训练（逐字稿）。

**从测试结果学习（Slides 第 28 页）：**采样 → 推理 + 最终代码 → 运行测试 → 通过/失败作为奖励 → 更新模型，使被奖励的回答更可能。公式（据 Slide 第 49 页类似形式）：

$$
\max_\theta \; \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)]
$$

**符号与假设：**$\tau$ 为轨迹，$\pi_\theta$ 为策略，$R$ 为奖励。此处假设奖励可定义、可计算；探索与信用分配问题在 Slides 第 49 页被点出（“晚失败无法指出早先哪一步做错”）。公式完整形式与梯度估计**待核**。

**推理示例（Slides 第 29 页）：**计算 $1+\dots+n$，$0 \le n \le 10^{12}$。直接迭代太慢；配对推导出 $n(n+1)/2$ 并检查 0、1；错误记忆为 $n(n-1)/2$ 在 $n=1$ 即错。

**RL 后的代码准确率（Slides 第 30 页）：**16K → 32K 为 RL 期间回答 token 上限（K = 1,000 token），★/64K 表示评测时给更多 token 但不再 RL；橙色虚线为 o3-mini。具体曲线数值**待核**。

### 3.6 智能体编码

**单步与智能体对比（Slides 第 32 页）：**单步是自包含提示 → 推理 + 代码 → 评估答案；智能体是 issue + 既有文件 → 搜索 → 编辑 → 跑测试 ↺ → 补丁 + 证据。

**定位—编辑—验证循环（Slides 第 33 页）：**仓库含 cli.py、config.py、test_config.py；定位“零在哪里变成默认值？”；编辑“仅当值为 None 时用默认”；验证零 + 默认用例 + 调用方回归；失败则修正假设。

**定位（Slides 第 34 页）：**示例命令 `rg 'retries' buggy_config.py` 得到 `return config.get("retries") or 3`；用环境变量运行单测复现 `AssertionError: 3 != 0`。

**编辑（Slides 第 35 页）：**

- 之前：`return config.get("retries") or 3`（所有假值都选默认）
- 之后：`value = config.get("retries")` 且 `return 3 if value is None else value`（显式 0 得以保留）

**验证（Slides 第 36 页）：**`python3 -m unittest -v test_config` 输出 missing → 3、None → 3、zero → 0、positive → 2，`Ran 4 tests: OK`。

**固定工作流替代方案（Slides 第 37 页）：**Agentless（Xia 等），不做迭代式工具调用，而是先定位文件、再定位类与函数、再选行，最后用单步模型生成补丁。逐字稿说明：该方案曾在短期内“令人沮丧地有效”，因为当时模型对单步代码求解训练充分、对智能体工具调用训练不足（逐字稿）。

**仅 shell 工具集（Slides 第 39 页）：**模型选命令，一个 shell 接口；读/搜用 rg、cat、find；编辑用 sed、Python、patch；执行检查用 pytest、构建命令；bash 返回输出 + 退出码 + 超时。mini-SWE-agent 即此类。

**用 shell 编辑（Slides 第 40 页）：**`sed 's/^RETRIES = 3$/RETRIES = 5/' settings.py > settings.new` 然后 `mv`。

**整文件与文本替换（Slides 第 41 页）：**整文件写简单但重复未变代码；搜索/替换紧凑但需无歧义匹配。Slide 给出 OpenHands/Pi/OpenCode 的编辑工具与 Aider 的 SEARCH/REPLACE 格式示例。

**diff 与 patch（Slides 第 42 页）：**统一 diff 标准但含行号与上下文；Aider 省略 hunk 行号；Codex 用文件操作 + 上下文，无行数。

**diff 格式影响（Slides 第 43 页）：**Aider 重构基准（89 个 Python 任务），GPT-4 Turbo（gpt-4-1106-preview）成功率：SEARCH/REPLACE 20%，简化统一 diff 61%。逐字稿补充：GPT-4 Turbo 在统一 diff 上更好是因为训练数据中见过更多；Gemini 曾因自有编辑格式在测试框架上表现较差（逐字稿；数值以 Slide 第 43 页为准）。

**找相关代码（Slides 第 44 页）：**从症状出发（flag、loader、retry loop 都可能匹配），沿值追踪（配置输入 → 默认逻辑），例如 `rg 'retries' .`。

**依赖图导航（Slides 第 45 页）：**LocAgent 给智能体特殊工具沿依赖路径追踪（config.py → cli.py → client.py → test_config.py），检索相关邻域后用执行验证。逐字稿提醒：让此类方法优于更简单方法在实践中很难（逐字稿）。

### 3.7 评测与训练

**SWE-bench（Slides 第 47 页）：**从 GitHub issue 构造；取 issue 被解决时的仓库状态（PR 之前）；找到与 issue 相关的测试；智能体生成补丁；应用补丁与测试；全部相关测试通过得 1 分，否则 0 分。两种测试：fail-to-pass（PR 前失败、PR 后通过）与 pass-to-pass（PR 前后都通过，防回归）。

**构建可运行训练任务（Slides 第 48 页）：**起始状态（文件 + 依赖 + 测试命令）、issue（请求行为 + 复现）、检查（bug 修复前失败、修复后恢复）。收集轨迹前先验证环境。

**多步修复的 RL（Slides 第 49 页）：**助手动作（搜索、编辑、测试/结束）为训练目标；文件查找结果、补丁应用、测试输出只作为上下文；终端奖励为“是否修好”。问题：晚失败无法指出早先哪一步决策错误。公式：$\max_\theta \mathbb{E}_{\tau\sim\pi_\theta}[R(\tau)]$。

**训练数据与推理算力（Slides 第 50 页）：**SWE-Gym，32B 模型；学习式验证器选择用于推理扩展。具体曲线**待核**。

**注入 bug 造修复任务（Slides 第 51 页）：**准备可执行基线 → 变异代码（不改测试）→ 保留新的测试失败。SWE-smith。

**注入与检查（Slides 第 52 页）：**基线四个测试全过；把 `return 3 if value is None else value` 变异为 `return 3 if not value else value`，零的测试失败；基线 4 过、变异 3 过 1 败、恢复 4 过。

**跨语言（Slides 第 53 页）：**Python（pyproject.toml、pytest）、TypeScript（package.json、npm test）、Rust（Cargo.toml、cargo test）；先读项目配置再决定构建与测试命令。Multi-SWE-bench、SWE-bench Multilingual。

**多脚手架训练（Slides 第 54 页）：**脚手架 = 提示 + 工具 + 智能体循环 + 上下文管理；同一模型权重；示例脚手架 OpenHands、OpenCode、Codex；任务检查（补丁 → 测试奖励）；轨迹 + 奖励更新模型。Nemotron 3 Ultra：每个任务分布 ≥2 个脚手架；Polar：原生脚手架调用共享模型 API 代理。逐字稿补充 Nvidia Neotron 报告在 5 个或更多脚手架上训练（逐字稿；具体数量以 Slide 第 54 页“≥2”为准，逐字稿数字待核）。

### 3.8 前端开发

**智能体驱动的前端（Slides 第 56 页）：**定位组件与事件处理器 → 编辑逻辑与样式 → 浏览器验证（类型 → 点击 → 检查保存状态；截图 → 视觉理解）→ 失败则修正。SWE-bench Multimodal 提供浏览器与截图工具。

**浏览器智能体 vs Playwright（Slides 第 57 页）：**浏览器智能体由模型选下一步动作（观察 → 选动作 → 输入/点击，适应式探索）；Playwright 脚本由模型写可重复检查（fill、click、expect、screenshot）。截图 → 视觉检查或批准基线比较。

**验证前端修复（Slides 第 58 页）：**编辑 `value.length → value.trim().length`；行为：0 条记录、有效名仍可保存；外观：错误提示在 Name 旁可见可读。

**评测视觉问题解决（Slides 第 59 页）：**issue + 图片；起点仓库；候选补丁；执行检查（空白 → 错误、无新记录）；回归检查（有效名 → 保存、既有测试通过）。要点：issue 里有图片并不代表用图像相似度作为评分规则。

### 3.9 更广泛的软件开发

**从需求到维护（Slides 第 61 页）：**需求 → 实现循环（编辑、测试）→ 评审（diff + 证据、发布决策）→ 部署/监控（生产信号、回滚路径）→ 维护（新需求、观测到的失败）。要点：测试通过只是其中一步，不是发布决策。

**开发者时间分布（Slides 第 62 页）：**编码 15%、会议 + 邮件 25%、调试 14%、跑测试 8%、代码评审 5%、需求 + 文档 6%、帮助 + 同步 + 社交 11%、学习 + 行政 + 杂项 8%、休息 8%。来源：Meyer 等 2019，5,928 份微软自我报告工作日。

**任务对比（Slides 第 63 页）：**

| 任务 | 产物 | 环境/验证器 | 时间视野 |
|---|---|---|---|
| 修复 | 补丁 | 仓库 / 回归测试 | 一个问题 |
| 库创建 | 实现 | 脚手架 / 包测试 | 多个函数 |
| 测试生成 | 新测试 | 有 bug + 已修复版本 / 判别 | 一个行为 |
| CI 修复 | 代码或配置 | 工作流 / 所需检查 | 一次构建运行 |
| 演化 | 累积变更 | 持久应用 / 里程碑 + 回归 | 依赖任务 |

**定位任务（Slides 第 64 页）：**CodeScout；搜索策略：issue + 仓库 → 检查/搜索 → 预测文件（如 django/…/datetime.py，模块 TruncDate，函数 as_sql）；奖励为三个层级上的 F1；与 gold patch 中位置比较，补丁不作为策略输入。

**应用创建与修改（Slides 第 65 页）：**ViBench；需求（产品/功能描述）；Zero-to-One 建新应用 15 个；Vibe-on-Ref 扩展参考 MVP 45 个；Vibe-on-Vibe 扩展智能体早先 MVP 45 个；每个结果用人工编写的浏览器测试计划检查。

**库实现（Slides 第 66 页）：**Commit0 与 ProgramBench；库脚手架中 `parse(…)`、`evaluate(…)` 缺函数体，配文档与测试，一起实现并跑集成包测试；ProgramBench 给参考可执行文件，探测输入观察输出，新实现匹配可观测行为，内部设计可不同。

**维护（Slides 第 67 页）：**SWE-Milestone。

**测试生成（Slides 第 68 页）：**SWT-Bench（Mündler 等 2024）。

**CI 修复（Slides 第 69 页）：**观测到构建失败（Node 16 而包要求 Node >=18，`npm ci: EBADENGINE`）；因果相关改动是把 setup-node 配成 `node-version: '20'`；重跑安装、构建、测试。数据集 LCA CI Builds Repair。

**学习新任务的技能（Slides 第 70 页）：**找相关代码（搜索/依赖）、实现函数（规格 → 代码）、写 bug 测试（issue → 可执行检查）、训练策略（SFT 或 RL）；留出任务：新仓库上修 issue、建库、检测新 bug；等推理预算。

**生成练习项目（Slides 第 71 页）：**SWE-Playground（Zhu、Gandhi & Neubig）。

**迁移到新开发任务（Slides 第 72 页）：**32B 模型，Base 与 Hybrid-Gym 对比：SWE-bench Verified 修复 7 → 32.4；SWT-Bench Verified 测试生成 9.01 → 16.86；Commit0 Lite 建库 8.34 → 13.45。柱状图数值**以 Slide 第 72 页为准**，图形细节待核。

### 3.10 代码行为预测与世界模型

**选择动作并预测效果（Slides 第 74 页）：**历史 h（已检查代码、工具结果）；策略 $\pi(a\mid h)$ 选择“跑测试”；真实环境执行，观测到断言失败；世界模型 $p(o\mid h,a)$ 预测测试结果；预测可能错；历史也条件化预测。

**预测执行：共享引用（Slides 第 75 页）：**

```python
items = [1]
alias = items
alias.append(2)
result = len(items)
```

真实执行：`items = [1, 2]`、`alias = [1, 2]`、`result = 2`；错误预测是把别名当作副本。

**预测何时帮助智能体（Slides 第 76 页）：**两个修复 A（对）与 B（错）；模型预测 A 失败、B 通过 → 错误决策选 B 丢弃 A；因此要跑两个候选来检查模型判断；比较任务成功率与总延迟/token/工具调用。

**从程序执行学习（Slides 第 77 页）：**FAIR CodeGen Team 等 2025，CWM。

**构建与使用模拟器（Slides 第 78 页）：**Dainese 等 2024，Code World Models / GIF-MCTS。

**开放问题（Slides 第 79 页）：**更好的决策（在同一批问题上度量预测误差与任务成功率）、更低的成本（含延迟、token、真实环境调用）、新设定（留出程序、依赖、环境）、何时执行（变化回退阈值，同时度量失败与节省）。

---

## 四、公式的假设与符号汇总

1. **预训练损失**（Slide 第 7 页）：$L_{LM} = -\mathbb{E}_{x\sim D_{mix}} \sum_t \log p_\theta(x_t \mid x_{<t})$。假设标准自回归分解、混合分布采样；记号排版**待核**。
2. **RL 目标**（Slide 第 49 页，另见第 28 页思想）：$\max_\theta \mathbb{E}_{\tau\sim\pi_\theta}[R(\tau)]$。假设轨迹可采样、奖励可计算；信用分配难点见 Slide 第 49 页。
3. **pass@k**（Slide 第 26 页）：k 次采样至少一次通过全部测试的概率；具体无偏估计式未在文本提取中给出，**待核**。
4. **BLEU-4 / CodeBLEU / CodeBERTScore / DiffBLEU**（Slides 第 20–22、27 页）：文本 n-gram 重叠、AST + 数据流、上下文嵌入匹配、与参考编辑的相似度。具体公式**待核**。

---

## 五、常见误区

1. **“会写代码 = 会做软件工程”**。Slides 第 2、61、62 页反复提示：编码只占开发者时间约 15%，评审、部署、监控、维护同样重要。
2. **“编辑是免费的”**。逐字稿明确说编辑需要训练；Slides 第 5 页把 Editing 与 Language、Reasoning 并列为三项能力。
3. **“填充会牺牲普通补全”**。Slides 第 17 页消融说明因果掩码反而更好；逐字稿强调不是取舍。
4. **“测试通过就等于正确”**。Slides 第 24 页列出有限测试可能漏掉错误行为；逐字稿举了按钮背景色假阴性的例子。
5. **“diff 格式无所谓”**。Slides 第 43 页显示 SEARCH/REPLACE 20% 对简化统一 diff 61%（同一模型）。
6. **“一个 shell 工具就够了”**。Slides 第 39–41 页与逐字稿指出：文件编辑接口需要专门设计，搜索/替换需无歧义匹配。
7. **“世界模型预测可以直接信”**。Slides 第 75、76 页给出别名误判与错误决策的例子；Slides 第 79 页把“何时执行”列为开放问题。
8. **“基准测试是干净的”**。逐字稿说每个著名基准都有论文抱怨单元测试质量；Slides 第 24、48 页强调环境与测试可信度。

---

## 六、复习问题

1. Slides 第 2 页的三层能力分别是什么？各需要一个什么样的数据或工具支持？
2. 为什么预训练时要保留缩进、文件边界与文本—代码关系（Slides 第 7 页）？Python 空白字符的例子说明了什么（逐字稿）？
3. Slides 第 9 页的分词示例中，空白串被合并成 token 的好处与风险各是什么？
4. Slides 第 12 页的混合比例表说明了什么权衡？如果你是产品团队，会如何选择？
5. 填充任务如何把“挖空预测”变成自回归（Slides 第 15 页）？多个洞如何处理？
6. Slides 第 16 页三种推理方法的差异是什么？为什么“因果掩码填充”优于“多候选 + 重排”？
7. 比较“与参考解比较”“结构比较”“嵌入比较”“执行检查”四种评估范式（Slides 第 20–24 页），各自最容易被什么错误欺骗？
8. SWE-bench 的 fail-to-pass 与 pass-to-pass 分别防止什么错误（Slides 第 47 页）？
9. 定位—编辑—验证循环中，Slides 第 35 页的“之前/之后”代码差异为什么重要？它修复的根因是什么？
10. 为什么文件编辑格式会显著影响智能体性能（Slides 第 41–43 页）？搜索/替换格式的主要缺点与缓解方式是什么？
11. 变异注入 bug（Slides 第 51–52 页）相比从 PR 构造任务，优势与劣势各是什么？
12. 多脚手架训练（Slides 第 54 页）试图解决什么问题？为什么模型在不同脚手架上表现会不同？
13. 前端任务为什么需要视觉验证（Slides 第 56–59 页）？Slides 第 59 页说“issue 里有图片并不代表用图像相似度评分”，这提醒我们什么？
14. Slides 第 63 页的五种任务在“环境/验证器”和“时间视野”上如何不同？这如何影响训练数据需求？
15. 世界模型 $p(o\mid h,a)$（Slides 第 74 页）在什么情况下可能误导智能体？Slides 第 76、79 页建议如何评估它的价值？
16. 逐字稿提到模型对 Python 有强偏好（逐字稿），Slides 第 53 页展示多语言配置。这两者之间可能有什么张力？

---

## 七、给定资料中的官方来源链接

- 课程主页：https://www.cmu-agents.com/
- 课程日程与阅读：https://www.cmu-agents.com/#schedule
- 作业与项目要求：https://www.cmu-agents.com/#assignments
- Assignment 1 · Harness：https://github.com/cmu-agents/assignment-1
- Assignment 2 · Eval：https://github.com/cmu-agents/assignment-2
- 课程视频：https://www.youtube.com/watch?v=1BWeH1oOM7k&list=PLSN0qpDfUvTM&index=6
- 官方课程日程：https://www.cmu-agents.com/#schedule
- Lecture 6 slides：https://www.cmu-agents.com/slides/lecture-06-coding-agents.pdf
- Assignment 1 · Harness：https://github.com/cmu-agents/assignment-1

> 说明：以上链接为给定资料中列出的官方来源；本笔记未另行检索或添加资料之外的链接。所有数值、图表与公式细节请以官方 PDF 与视频为准；标注“待核”处表示仅凭文本提取无法确认。
