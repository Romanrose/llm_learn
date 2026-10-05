# 产品管理、软件工程与设计课程：本地审核清单

日期：2026-10-03。由三个课程子智能体并行核对公开来源，已有74篇 Note / Blog 获用户明确批准，已登记正式 outputs；此前候选稿和来源记录仍保留。CS147新增ASR中英逐字稿保持独立待校对状态，审核预览可查看，不继承现有正文批准。

## 当前覆盖

当前共 37 组 Note / Blog、74 篇已批准正文：UVA 5 组、MIT 19 组、CS147 10 组作业及 3 组讲义。另有 CS147 Design Discovery 一组中英 ASR 全文候选，约1小时54分钟，待回听校对；其余课程的资料缺口仍明确保留。

| 课程 | 目录与候选正文 | 仍缺少的资料 |
| --- | --- | --- |
| [UVA Digital Product Management](product/uva-digital-product-management/README.md) | 五门子课程、二十个模块的公开导航；每门子课程一组原创 Note / Blog；教师公开补充资料及跨课程练习 | 完整视频内容、视频级笔记、评分作业正文，以及可核验的中英逐字稿；不能把子课程级解释称作完整课程覆盖 |
| [MIT 6.102 Spring 2026](software-engineering/mit-6102-sp26/README.md) | 十九篇核心阅读各一组 Note / Blog；作业、项目、考试和工具的官方入口 | 官方 FAQ 明确本课以交互阅读教授概念，主动学习课堂不录像，课堂逐字稿不适用；校内服务仍需课程身份 |
| [Stanford CS147 Autumn 2026](design/cs147-fall26/README.md) | 十个作业单元各一组 Note / Blog；前三讲公开讲义的已批准解释；官方日程及版本冲突记录 | 第二讲已生成中英ASR全文候选；其他课堂录像或字幕、后续讲义仍待课程发布；第二讲由2026官网链接复用2025讲义，不能整体称为2026新材料 |

上述 Note / Blog 是自写教学解释，用户已批准这批正文接入，保留原有来源范围和事实限制。英文阅读与作业原文仅保留官方链接；未把第三方书籍或付费材料复制进仓库。

## 逐项检查入口

- [UVA：资源覆盖与访问限制](product/uva-digital-product-management/resources/coverage.md)
- [MIT：十九篇阅读与工程资源覆盖](software-engineering/mit-6102-sp26/resources/coverage.md)
- [CS147：作业、讲义与版本缺口](design/cs147-fall26/resources/coverage.md)

每个单元的 `sources.yaml` 说明实际读取的来源；`references/codex/run.yaml` 与 `checks.yaml` 区分生成完成、结构检查与人工审核。结构检查通过并不代表正文已审核。

## 本地审核与构建

```bash
node workflow/scripts/validate-resource-drafts.mjs \
  uva-digital-product-management mit-6102-sp26 cs147-fall26
npm run review:dev
```

审核模式可在课程单元页切换候选笔记与 Blog。CS147 三个讲义单元已接入独立课程页面，原候选稿通过课程 README 仍可追溯。普通 `npm run build` 展示已批准的74篇Note / Blog；审核预览可另外显示新ASR候选稿。

## 后续补齐条件

- UVA：必须先有合法访问课程内容的方式，并核对保存与再分发权限；不能用公开目录推测讲课全文。
- MIT：获得官方公开的课堂视频或带时间戳字幕入口，才能新增课堂逐字稿。
- CS147：优先等待官方字幕与后续讲义；媒体没有字幕时，只能在明确获准下载音频后考虑 ASR。

不将这些实际缺口标记为“全部完成”，也不通过生成空文件或猜测时间戳补齐。

## 逐字资料入口复核

本地课程页已支持 `transcriptReferences`：没有本地全文时，相关语言标签显示“逐字资料”，点击查看官方字幕或逐字文本外链。这些入口不计入完整逐字稿数量，也不改变候选正文的发布状态。

- UVA：教师公开 Josh Andrews 访谈英文全文入口，关联四个相关子课程；是独立补充，无段落时间轴，不是 Coursera 原课。
- CS147：五条官方日程补充视频已核实有英文字幕（四条自动、一条人工），关联 A2/A4/A6/A8。实际视频年份为2013、2014、2022，均保留外链和轨道追溯，不标成2026课堂录像。
- MIT：根据官方 FAQ，十九个交互阅读单元的课堂逐字稿明确不适用，已更新状态说明。
- CS147 Design Discovery：公开媒体可访问，但未找到字幕。用户已明确批准临时音频下载和转写；中英全文候选与来源检查分别见 [英文稿](design/cs147-fall26/references/lectures/lecture-02/codex/transcript.en.md)、[中文稿](design/cs147-fall26/references/lectures/lecture-02/codex/transcript.zh-CN.md)、[检查记录](design/cs147-fall26/references/lectures/lecture-02/codex/transcript-checks.yaml)。录像年份仍未确认，全文待回听校对。

资料审计记录见各课 resources 下的 transcript/caption audit 或 subtitle coverage 文件。没有保存未经许可的补充视频全文与完整翻译。
