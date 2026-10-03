# CMU 11-768 · AI Agents（Fall 2026）

这是 Carnegie Mellon University 11-768 AI Agents 的自学入口，主讲教师为 Graham Neubig 与 Daniel Fried。课程围绕 LLM Agent 的构建、评测与训练展开，可在 CS336 的语言模型基础之后继续学习。

[官方课程](https://www.cmu-agents.com/) · [网站课程工作台](https://romanrose.github.io/llm_learn/generated/courses/cmu-11768-fall26/) · [课程元数据](../../website/catalog-data/courses/cmu-11768-fall26.yaml)

## 当前接入范围

截至 2026 年 10 月 3 日，官网日程有 30 个日程项，其中 23 次教学讲座进入逐讲导航，7 个假期、项目答疑或期末展示项单独保存在元数据的 `schedule.events` 中。

- 前 12 讲的官方 PDF Slides 保留外链，已临时获取用于逐页文本提取；仓库保存提取文本和来源哈希。
- 前 9 讲的官方录像链接及平台原始英文自动字幕，已清洗并生成翻译候选；未下载音视频。
- 265 个逐讲阅读条目，去重后为 252 个链接；保留官网的课程阅读与补充参考分组。
- [Assignment 1 · Harness](https://github.com/cmu-agents/assignment-1)：构建编码 Agent 的运行框架。
- [Assignment 2 · Eval](https://github.com/cmu-agents/assignment-2)：构建 Agent 正确性与功能评测。
- Assignment 3 · Training：官网已列出目标及截止日期，尚未提供作业链接。

尚未发布资料的教学讲座保留计划状态；不创建空笔记目录。当前 `publishOutputs: true`，只显式开放用户审核通过的产物：前 12 讲 Note、Blog 与前 9 讲中英文逐字稿。

## 已审核发布内容

前 1–9 讲按字幕与 Slides 整理的 Note、Blog、中英文逐字稿已由用户确认，正式文件位于各讲目录；候选及合并记录保留在 `references/deepseek/`。原 Slides 版 Note、Blog 保存在 `references/deepseek-slides/` 供对照。前 10–12 讲已发布基于 Slides 的 Note、Blog，逐字稿等待官方录像或字幕。第 13–23 讲尚缺正文来源。

来源、段落合并与用户确认记录见 [本次发布记录](../../workflow/review-queue.md)。运行 `npm run build` 构建 catalog 中显式开放的正式产物；`npm run review:dev` 用独立快照审阅后续候选。结构检查不代替人工审核，自动字幕专名、公式与翻译需重点核对。

## 学习主线

```text
运行框架、工具、上下文、Skills / Memory、规划
  → 编码、计算机使用、深度研究
  → SFT、强化学习与训练系统
  → 沙箱、框架、监控
  → 多 Agent、人机交互与搜索
```

按课程日程交替学习应用与训练部分，优先结合 Slides、录像及官方阅读，再完成 Harness 与 Eval 的练习。课程中的作业要求和政策以官网及作业仓库为准。

## 维护约定

- 稳定课程 ID 为 `cmu-11768-fall26`；目录、元数据、网站路由使用同一 ID。
- 讲次使用 `lecture-01` 至 `lecture-23`，同时保存官网 `scheduleCode`（如 `1a`）；后续更新不按日期重新编号。
- 网站资料由 `website/catalog-data/courses/cmu-11768-fall26.yaml` 管理；来源核验记录见 [manifest](resources/manifest.yaml)。
- CMU 官网通过客户端脚本渲染日程，现有 `course sync` 的 HTML 表格解析器不适用。本次依据官网数据人工核对录入；后续先核对官网，再定向更新 YAML，运行 `npm run build`。
- 正式内容按 `workflow/standards/project-structure.md` 和 `workflow/standards/transcript-generation.md` 建立来源及审核记录；仅在实际开始某讲时创建相关目录。

上游来源和资料边界见 [UPSTREAM.md](UPSTREAM.md)。
