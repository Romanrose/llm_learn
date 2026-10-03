# 课程内容审核与发布记录

范围：CMU 11-768 Fall 2026；CS336 2026 第 18、19 讲。资料核对日期：2026 年 10 月 3 日。

本批 46 份产物已由用户确认内容，并在参照 CS336 2026 合并逐字稿段落后提升为正式稿。原先 10 讲共 1758 个碎段合并为 678 个自然阅读段；中英文同边界、同时间戳，合并前后正文逐字比对一致。英文稿来自平台字幕清洗，中文稿逐段翻译；CMU 自动字幕中的错词与专名仍需回听核对。结构检查通过只证明文件、段落和时间戳符合约定，不证明内容语义、公式或引用正确。

## 本地审核入口

运行 `npm run review:dev`，在终端给出的本地地址打开课程页面。CMU 路由为 `/llm_learn/generated/courses/cmu-11768-fall26/`；CS336 第 19 讲为 `/llm_learn/generated/courses/cs336-2026/lecture-19/`。讲次页面上方可切换课程笔记、Blog、中文与英文逐字稿。仅有 Slides 的讲次不显示可用逐字稿标签。

审核预览使用启动时生成的临时快照，普通网站构建不会覆盖它。修改候选稿后重启 `npm run review:dev` 即可更新；临时快照不是第二套源文件或发布管线。

`npm run build` 和 `npm run dev` 使用正式模式，只读取 catalog 显式开放的 outputs；不会因候选文件存在而发布。

## 正式文件

| 讲次 | 学习内容 | 逐字稿 | 状态 |
|---|---|---|---|
| CMU L01 · Course Overview: What Is an Agent? | [Note](../agent/cmu-11768-fall26/notes/lecture-01/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-01/blog.md) | [中文](../agent/cmu-11768-fall26/notes/lecture-01/transcript.zh-CN.md) · [EN](../agent/cmu-11768-fall26/notes/lecture-01/transcript.en.md) | [结构检查](../agent/cmu-11768-fall26/notes/lecture-01/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L02 · Agent Capabilities 1: Tool Use | [Note](../agent/cmu-11768-fall26/notes/lecture-02/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-02/blog.md) | [中文](../agent/cmu-11768-fall26/notes/lecture-02/transcript.zh-CN.md) · [EN](../agent/cmu-11768-fall26/notes/lecture-02/transcript.en.md) | [结构检查](../agent/cmu-11768-fall26/notes/lecture-02/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L03 · Agent Capabilities 2: Context Management for Long-Context Agents | [Note](../agent/cmu-11768-fall26/notes/lecture-03/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-03/blog.md) | [中文](../agent/cmu-11768-fall26/notes/lecture-03/transcript.zh-CN.md) · [EN](../agent/cmu-11768-fall26/notes/lecture-03/transcript.en.md) | [结构检查](../agent/cmu-11768-fall26/notes/lecture-03/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L04 · Agent Capabilities 3: Skills and Memory | [Note](../agent/cmu-11768-fall26/notes/lecture-04/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-04/blog.md) | [中文](../agent/cmu-11768-fall26/notes/lecture-04/transcript.zh-CN.md) · [EN](../agent/cmu-11768-fall26/notes/lecture-04/transcript.en.md) | [结构检查](../agent/cmu-11768-fall26/notes/lecture-04/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L05 · Agent Capabilities 4: Planning, Task Decomposition, and Multi-Agent Coordination | [Note](../agent/cmu-11768-fall26/notes/lecture-05/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-05/blog.md) | [中文](../agent/cmu-11768-fall26/notes/lecture-05/transcript.zh-CN.md) · [EN](../agent/cmu-11768-fall26/notes/lecture-05/transcript.en.md) | [结构检查](../agent/cmu-11768-fall26/notes/lecture-05/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L06 · Domains 1: Coding Agents | [Note](../agent/cmu-11768-fall26/notes/lecture-06/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-06/blog.md) | [中文](../agent/cmu-11768-fall26/notes/lecture-06/transcript.zh-CN.md) · [EN](../agent/cmu-11768-fall26/notes/lecture-06/transcript.en.md) | [结构检查](../agent/cmu-11768-fall26/notes/lecture-06/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L07 · Computer Use Agents | [Note](../agent/cmu-11768-fall26/notes/lecture-07/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-07/blog.md) | [中文](../agent/cmu-11768-fall26/notes/lecture-07/transcript.zh-CN.md) · [EN](../agent/cmu-11768-fall26/notes/lecture-07/transcript.en.md) | [结构检查](../agent/cmu-11768-fall26/notes/lecture-07/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L08 · Training 1: Supervised Fine-Tuning (SFT) | [Note](../agent/cmu-11768-fall26/notes/lecture-08/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-08/blog.md) | [中文](../agent/cmu-11768-fall26/notes/lecture-08/transcript.zh-CN.md) · [EN](../agent/cmu-11768-fall26/notes/lecture-08/transcript.en.md) | [结构检查](../agent/cmu-11768-fall26/notes/lecture-08/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L09 · Training 2: Reinforcement Learning Basics | [Note](../agent/cmu-11768-fall26/notes/lecture-09/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-09/blog.md) | [中文](../agent/cmu-11768-fall26/notes/lecture-09/transcript.zh-CN.md) · [EN](../agent/cmu-11768-fall26/notes/lecture-09/transcript.en.md) | [结构检查](../agent/cmu-11768-fall26/notes/lecture-09/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L10 · Domains 3: Deep Research Agents | [Note](../agent/cmu-11768-fall26/notes/lecture-10/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-10/blog.md) | 等待公开录像/字幕 | [结构检查](../agent/cmu-11768-fall26/notes/lecture-10/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L11 · Training 3: Advanced RL Algorithms | [Note](../agent/cmu-11768-fall26/notes/lecture-11/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-11/blog.md) | 等待公开录像/字幕 | [结构检查](../agent/cmu-11768-fall26/notes/lecture-11/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CMU L12 · Training 4: RL Systems | [Note](../agent/cmu-11768-fall26/notes/lecture-12/note.md) · [Blog](../agent/cmu-11768-fall26/notes/lecture-12/blog.md) | 等待公开录像/字幕 | [结构检查](../agent/cmu-11768-fall26/notes/lecture-12/references/deepseek/checks.yaml) · 已由用户审核发布 |
| CS336 L19 · Guest lecture: Dan Fu | [Note](../llm/cs336-2026/notes/lecture-19/note.md) · [Blog](../llm/cs336-2026/notes/lecture-19/blog.md) | [中文](../llm/cs336-2026/notes/lecture-19/transcript.zh-CN.md) · [EN](../llm/cs336-2026/notes/lecture-19/transcript.en.md) | [结构检查](../llm/cs336-2026/notes/lecture-19/references/deepseek/checks.yaml) · 已由用户审核发布 |

## 缺项与来源边界

- CMU L01–L09：字幕与 Slides；原 Slides 版 Note、Blog 保留在本地供对照。使用平台原始英文自动字幕，未下载音视频。
- CMU L10–L12：只有官方 Slides 的提取文本，生成 Note、Blog；逐字稿等待公开录像或字幕。PDF 本体只临时用于文本提取，来源 URL、页码和哈希保留在 `references/source/slides.md`。
- CMU L13–L23：官网尚未提供这些讲次的正文资料，等待更新。
- CS336 L19：平台人工英文字幕；没有独立 Slides 输入，因此 Note、Blog 用逐字稿时间定位，不推测 Slides 页码。
- CS336 L18：未找到 Daniel Selsam 嘉宾课的官方公开视频、Slides 或逐字稿，未生成正文。[来源核验记录](../llm/cs336-2026/notes/lecture-18/sources.yaml)。

## 审核依据

用户确认本批内容没有问题，要求参照 CS336 2026 合并中英文逐字稿后发布。逐讲 `review.yaml` 记录用户确认，`references/deepseek/paragraph-merge.yaml` 保存原分段、合并边界与正文一致性检查。

结构检查涵盖时间戳逐项对齐、原文字序完整保留及字幕覆盖。它不代表代理重新回听了全部视频；公式、图示和自动字幕的来源局限继续保留在正式文件中。

生成脚本：`node workflow/scripts/generate-review-drafts.mjs <course-id> <lecture-id...>`；结构检查：`node workflow/scripts/validate-review-drafts.mjs <course-id> <lecture-id...>`。翻译分块保存在候选目录，失败或旧来源版本不进入审核预览；正式版本审核前保留候选目录。
