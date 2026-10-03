# CMU 11-768 Fall 2026 · Lecture 7 · Computer Use Agents 学习笔记

> 来源：平台字幕与官方 Slides。内容已由用户审核确认。

> 依据：Lecture 7 slides（官方 PDF 文本提取，标注为待核）与课堂逐字稿整理稿。本文标注的 Slide 页码依据 slides 提取文本；逐字稿仅用于补充讲解语境。图示、公式细节未与官方 PDF 视觉核验，均标注“待核”。本笔记内容已由用户审核确认。

## 一、学习目标

学完本讲，你应该能够：

1. 用自己的话定义 Computer Use Agent（CUA），并说清它与本课程此前讨论的文本型/软件工程型智能体的区别（Slides 第 2 页）。
2. 复述 CUA 的核心循环：观察 → 推理 → 行动 → 新观察，直到任务结束并计算奖励（Slides 第 3–8 页）。
3. 画出 CUA 建模的上下文结构：目标、截图、动作交错拼接成多模态序列，由 VLM 预测下一个动作（Slides 第 47–56 页）。
4. 区分四类评测范式：静态、端到端（网页）、端到端（桌面/移动）、长时程（Slides 第 18、24、34、38 页）。
5. 说明每类评测的验证方式：逐动作匹配、程序化状态检查、LLM/VLM 评委、人类评审、评分细则。
6. 概述三阶段训练流程：预训练 grounding/控制能力 → SFT 行为克隆 → RL 在模拟环境中按奖励更新策略（Slides 第 59、74 页）。
7. 认识 CUA 的残余挑战：速度与成本、个性化、基础设施与 UX、多智能体系统（Slides 第 77–80 页）。

## 二、概念主线

### 1. 什么是 CUA

CUA 是通过与人类相同的图形用户界面（GUI）操作计算机的智能体。它可以操作浏览器、桌面或移动设备（Slides 第 2 页）。关键点在于：它接收截图作为输入，产出与人类相同类型的动作——点击、滚动、打字、滑动、轻触。逐字稿中讲者强调，CUA 与文本型智能体的差别在于“在与人类完全相同的空间中操作”。

### 2. 观察—推理—行动循环

Slides 第 3 页给出循环骨架：用户任务 + 环境观察（通常为截图）进入 CUA 模型；模型产生推理轨迹与一个动作；基础设施校验并执行该动作；环境返回新截图作为下一轮观察。Slides 第 4–8 页用“买一个蓝色马克杯”贯穿演示：点击马克杯 → 向下滚动找配送信息 → 点击邮编框 → 输入“15213”，最后计算奖励 1.0。

逐字稿补充了循环终止条件：模型认为完成，或用尽预算。奖励通常是 0/1 二元，有时是部分奖励。

### 3. 一段简史

Slides 第 9–15 页与逐字稿给出时间线：

- 2017：MiniWoB，高度简化的玩具网页界面（Slides 第 9 页）。
- 2018：MiniWoB++。
- 2022：WebShop，用真实商品与语言目标做购物（Slides 第 10 页）。
- 2024：WebArena、VisualWebArena，走向真实网页界面（Slides 第 11 页）；OSWorld 转向完整桌面工作流（Slides 第 12 页）。
- 2026：MyPCBench 用个人历史数据（Slides 第 13 页）；CUA-World 用专业化桌面软件与真实数据（Slides 第 14 页）；GPT-6 ASTRA 演示显示能力飞跃但仍昂贵（Slides 第 15 页）。

逐字稿提到 2025–2026 年出现用编码智能体端到端生成环境与合成数据的趋势（如 MyPCBench 中的 Gmail 克隆），以及 CUA-World 覆盖天文学、生物学等长尾专业软件。

## 三、关键机制

### 1. 评测的三种“成功”定义

Slides 第 17 页区分：ACTION（是否点中目标）、OUTCOME（正确物品是否在购物车）、PROCESS（是否遵守约束，如不下单）。评测器应匹配你想要衡量的能力。

### 2. 静态评测

在固定观察上预测一个动作，不做环境 rollout（Slides 第 19 页）。任务示例：“把 20 美元以下的蓝色马克杯加入购物车，不要购买。”评分规则：预测的 (x, y) 落在目标框内得 1 分；对录制动作则匹配目标、操作与输入值。

- ScreenSpot-Pro：1581 张截图、23 个应用、3 个操作系统，逐点/区域匹配（Slides 第 20–21 页）。Blender 示例中真值框为 (417, 132)–(576, 152)，原始分辨率 2560×1440。
- Mind2Web：2350 个任务、137 个网站、31 个领域，离线动作匹配（Slides 第 22–23 页）。示例任务为在 Brooklyn–Central 租车，真值动作为点击 CAR 标签。

逐字稿指出静态评测的主要缺陷是假阴性多：同一截图下可能有多个合理动作，但只有录制的那一个被判为正确。

### 3. 端到端评测（网页）

代理在环境中真正执行任务，最后用程序化检查验证状态（Slides 第 25 页）。示例检查：`cart.item == blue_mug`、`cart.price < 20`、`orders.count == 0`，全部通过才给 reward = 1.0。

- WebArena：812 个长时程任务、4 个自托管域、功能性成功检查（Slides 第 26–27 页）。示例任务：创建名为 awesome_llm_reading 的空仓库；验证器检查目标 URL 页面 HTML 中是否含该名字，但**不检查仓库是否为空**。
- VisualWebArena：910 个任务、3 个自托管站点、25.2% 图像输入任务（Slides 第 28 页）。

逐字稿补充：WebArena 的验证器由 CMU 研究生手写；程序化验证器也可能有假阴假阳；可能出现奖励黑客（例如为完成“加入评分最高商品”而把大量商品塞进购物车）。

### 4. LLM/VLM 评委

当无法为每个任务写验证器时，用另一个 LLM/VLM 依据评分细则判断轨迹证据（Slides 第 29 页）。

- WebVoyager：643 个任务、15 个真实网站、评委与人类一致率 85.3%（Slides 第 30–31 页）。示例任务：找到气候变化数据可视化相关 star 最多的 GitHub 项目。
- Online-Mind2Web：300 个任务、136 个真实网站、WebJudge 与人类一致率 85.7%（Slides 第 32 页）。

逐字稿提醒：真实网站会发生漂移，评委质量本身成为得分的一部分；大量智能体持续访问网站也让站点所有者不满。

### 5. 人类评审

Slides 第 33 页给出人类评审用于解决模糊结果：示例中 Reviewer A 判 PASS，Reviewer B 判 FAIL，最终因订单确认页显示发生了禁止的购买而判 FAIL。逐字稿称人类审查仍是黄金标准，但非常昂贵，通常只做一两次用于校准。

### 6. 端到端评测（桌面、移动）

- OSWorld：369 个任务、9 个应用、每个任务自带定制评测器（Slides 第 35–36 页）。示例任务：用文件夹中的收据更新记账表；检查 A1:E8 不变、C9:C13 费用标签、金额与滚动余额、D9 ≈ −186.93、E9 ≈ 603.07。
- WindowsAgentArena：154 个任务、11 个程序、20 分钟并行扫描（Slides 第 37 页）。
- 附录另有 WorkArena（33 个任务模板、19912 个实例、ServiceNow 环境）与 AndroidWorld（116 个任务族、20 个应用）。

### 7. 长时程评测

Slides 第 39 页给出混合检查示例：动作轨迹为 click(mug) → click(add_to_cart) → click(place_order)；状态检查通过（正确物品），过程检查失败（发生了购买），最终判 FAIL。要点：只看结果可能漏掉违规。

- Odysseys：200 个真实网页任务、平均 6.1 条评分细则、主评测上限 100 步（Slides 第 40–41 页）。示例任务：规划棕榈泉婚礼旅行，8 条细则中满足 7 条 = 0.875 平均分。
- OSWorld 2.0：108 个工作流、中位人类耗时 1.6 小时、平均代理调用 318 次（Slides 第 42–44 页）。示例任务：构建 FreeCAD 支撑支架并导出匹配图纸的 STEP 模型；另一个示例是在 SolveSpace 中按参考视频尺寸建模并保存。
- CUA-World-Long：200 个长任务、常需超过 500 步、8 条质量标准（Slides 第 45 页）。
- 附录另有 MyPCBench（184 个任务、17 个已登录应用、68% 跨应用）与 WeaveBench（114 个任务、中位 16 次切换、中位 76 次工具调用）。

### 8. 建模：VLM 从交错视觉历史预测动作

Slides 第 47–56 页逐步展示：上下文从“目标 + 截图 0”开始，模型输出动作 0（如 click(x₀, y₀)）；动作被追加到轨迹；下一步上下文变为“目标 + 截图 0 + 动作 0 + 截图 1”，模型输出动作 1；到第 t 步，上下文是目标、截图与动作的交错序列，模型输出 click/type/tool/stop 之一。第 56 页强调：文本经 tokenizer + embedding，截图经视觉编码器 + projector，视觉 token 是连续 embedding 而非词表 ID；具体 token 划分与编码器因系统而异。

Slides 第 57 页列出前沿 CUA 的动作接口差异：GPT-6 Astra 用 Python/PyAutoGUI 或原生 computer tool；Fable/Opus 5 用原生 computer tool calls；Gemini 3.8 Flash 用归一化坐标的函数调用（0–999）；Qwen 3.8、Kimi K3 用函数调用；Muse Spark 用脚本 + 直接 GUI 动作。逐字稿强调输出格式差异让可复现性成为难题，并提到坐标通常归一化到 0–1000，因此跨分辨率迁移较好。

### 9. 训练三阶段

Slides 第 59、74 页给出总览：

- **预训练**：UI 元素与动作的 grounding/控制能力。用 Mind2Web、AITW 等数据学习“屏幕上有什么、如何寻址”，输出 click(x, y)、type(text)、swipe(…)（Slides 第 60 页）。示例：“CAR” ↔ 元素框/屏幕坐标，元素 bookCarTab。
- **后训练 SFT**：行为克隆人类演示与合成轨迹（Slides 第 61 页）。MolmoWebMix 为 36K 人类 + 105K 合成任务轨迹；AgentNet 发布 22625 条任务轨迹、3 个操作系统。合成数据常用特权信息（如 AxTree）让 teacher 展开得更好，再过滤保留有用轨迹。
- **后训练 RL**：在模拟环境中 rollout，按奖励更新策略（Slides 第 63–64 页）。示例任务：把 20 美元以下蓝色马克杯加入购物车、不要结账；动作序列为点击商品 → 加入购物车 → 验证/停止。

### 10. RL 为什么需要模拟环境

Slides 第 65 页给出三条理由：真实金钱（重复尝试会产生重复付费预订）、真实的人（预订会派单，探索影响他人）、无法干净重置（取消费用、时间不可恢复）。结论：在可重置的副本中探索，而非反复真实交互。

### 11. 环境与数据生成

- CUA-Gym：94 个模拟网页应用，计划→实现→测试；注入初始状态、检查最终状态、每次会话重置（Slides 第 66 页）。约 32K 验证元组、110 个环境、38% 跨应用任务（Slides 第 67–68 页）。3578 条 SFT 演示 → 在 10858 条验证元组上做 GSPO，OSWorld 从 62.2% 提升到 72.6%（Slides 第 69 页）。
- Gym-Anything：200 个软件应用、3 个操作系统、CUA-World 中 10K+ 任务（Slides 第 70 页）。创建代理构建、独立审计验证证据（Slides 第 70–71 页）。12103 个任务与环境、覆盖 22/22 个 SOC 职业组（Slides 第 72 页）。约 2000 条成功 SFT 轨迹，平均清单分从 12.7 升到 22.5，完美清单通过率从 1.6% 升到 4.4%（Slides 第 73 页）。

## 四、公式与符号的假设

本讲未给出以等号写成的数学公式，Slides 中的“公式”主要是伪代码与判分规则。以下为提取文本中可确认的形式及其假设，具体渲染与符号需对照 PDF 核验：

- 静态评测判分（Slides 第 19 页）：对录制动作匹配 target、operation、input value；对点选类，若 (x, y) ∈ target box 则记 1.0。“correct point / step”不等于“completed task”。
- 端到端状态断言（Slides 第 25 页）：`assert all(checks)` → PASS → reward = 1.0。假设环境可 API 访问数据库/文件/应用状态，且检查覆盖了任务的全部关键条件。
- WebArena 验证器（Slides 第 27 页）：`reward = int(name in html.lower())`。显式说明“不检查 emptiness”，因此该验证器只覆盖名字存在性。
- OSWorld 记账检查（Slides 第 36 页）：`compare_table(saved_workbook, gold_workbook, rules)`；规则包括 A1:E8 不变、C9:C13 标签、金额与滚动余额、D9 ≈ −186.93、E9 ≈ 603.07。≈ 表示数值比较带容差。
- Odysseys 评分（Slides 第 41 页）：7/8 satisfied = 0.875 average；图示另标 “Perfect completion = 0.0”，该处文本提取存在矛盾，待核。
- RL 目标（Slides 第 63–64 页）：滑出轨迹后按 reward 更新策略；正奖励提高该轨迹动作权重，零/负奖励降低。逐字稿表述为“最大化环境中的奖励”。
- 时间成本（Slides 第 77 页）：Task time ≈ turns × time / turn。这是估算式，用于说明减少轮数或每轮成本都能缩短任务时间。

符号说明：o 表示观察，a 表示动作，t 表示步数；x, y 为屏幕坐标；reward 为任务奖励。

## 五、常见误区

1. **把“动作正确”当作“任务完成”**。Slides 第 19 页明说：A correct step is not a completed task。静态评测只衡量 grounding/模仿，不衡量端到端成功。
2. **以为程序化验证器一定可靠**。Slides 第 25 页提示“只覆盖测试覆盖到的条件”；第 27 页的 WebArena 例子明确不检查仓库为空。逐字稿也承认存在假阴假阳。
3. **以为 LLM 评委等价于人类判断**。WebVoyager 一致率 85.3%、Online-Mind2Web 85.7%（Slides 第 30、32 页），仍有差距，且逐字稿提醒评委容易被欺骗。
4. **只看最终交付物**。Slides 第 39 页显示，最终物品对了但过程中发生了禁止的购买，应判 FAIL。
5. **以为可以在评测集上训练**。逐字稿明确说不应在基准上训练；工业界常见做法是生成相似任务在分布内训练，部分基准提供单独的 train/val/test 划分。
6. **以为截图表示不如 HTML/无障碍树**。逐字稿称基于截图的方法简单得多，且效果出奇地好；桌面场景也不易获得 HTML。但 GPT-6 等模型在可用时仍会使用无障碍表示。
7. **忽略坐标归一化**。逐字稿称坐标通常归一化到 0–1000，因此绝对分辨率不同也能较好迁移；但这是经验性说法，未见 slides 正式规格。
8. **把 RL 当成唯一关键阶段**。逐字稿强调预训练与 SFT 为 RL 提供强大基础；RL 是“点睛之笔”。

## 六、复习问题

1. 用“买蓝色马克杯”的例子，完整描述 CUA 的一轮 observe–reason–act，并指出奖励在何时计算。（参考 Slides 第 3–8 页）
2. 静态评测与端到端评测各衡量什么能力？为什么前者会产生较多假阴性？（参考 Slides 第 19、25 页）
3. WebArena 的仓库创建任务中，验证器检查什么、不检查什么？这说明了程序化验证器的什么局限？（参考 Slides 第 27 页）
4. 在什么情况下你会选择 LLM/VLM 评委而不是程序化验证器？它带来什么新风险？（参考 Slides 第 29–32 页）
5. Odysseys 为什么使用评分细则而不是单一二元奖励？7/8 满足意味着什么？（参考 Slides 第 40–41 页）
6. 长时程评测中“状态检查”和“过程检查”分别捕捉什么？举出 Slides 第 39 页的例子说明二者冲突时如何裁决。
7. 描述 CUA 在第 t 步的上下文组成。文本和截图分别如何进入模型？（参考 Slides 第 53–56 页）
8. 训练三阶段各解决什么问题？为什么 RL 阶段需要模拟环境？（参考 Slides 第 59、65、74 页）
9. CUA-Gym 与 Gym-Anything 在“生成环境与奖励”上分别采取什么策略？它们报告了哪些数据规模？（参考 Slides 第 66–73 页）
10. Slides 第 77–80 页列出哪些未解决问题？各自的核心难点是什么？

## 七、给定资料中的官方来源链接

- 课程主页：https://www.cmu-agents.com/
- 课程日程与阅读：https://www.cmu-agents.com/#schedule
- 作业与项目要求：https://www.cmu-agents.com/#assignments
- Assignment 1 · Harness：https://github.com/cmu-agents/assignment-1
- Assignment 2 · Eval：https://github.com/cmu-agents/assignment-2
- 课程视频：https://www.youtube.com/watch?v=jwGluLrrqjQ&list=PLSN0qpDfUvTM&index=7
- 官方课程日程：https://www.cmu-agents.com/#schedule
- Lecture 7 slides：https://www.cmu-agents.com/slides/lecture-07-computer-use-agents.pdf

（完）
