# 上游来源与更新方式

- 课程：Carnegie Mellon University 11-768 AI Agents，Fall 2026。
- 课程主页与公开日程：<https://www.cmu-agents.com/>。
- 主讲教师：Graham Neubig、Daniel Fried；部分讲座由官网标注的客座讲者授课。
- 核对日期：2026 年 10 月 3 日。

## 录入方式

官网首页为客户端渲染应用，课程日程、阅读与作业信息来自首页引用的公开 JavaScript 中的静态数据。本次只提取课程数据，不执行下载脚本，不镜像应用代码。官网构建产物地址可能变化，更新时应从主页重新定位。

课程元数据保留官网标题、日期、模块、日程编号、讲者及资料链接。教学讲座映射为稳定 `lecture-id`，假期、项目答疑和展示保存在 `schedule.events` 中。中文副标题是本项目编写的导航说明，不是课程逐字稿或经过正文审核的 Lecture Note。

12 份 Slides 和前两次作业仓库已验证 HTTP 可访问；9 个录像链接及阅读链接已核对官网来源，未逐一播放录像或审阅阅读全文。具体核验范围见 [resources/manifest.yaml](resources/manifest.yaml)。

## 资料边界

- 官方 PDF、视频、论文、文章与代码仓库均保留外链，权利与许可证以对应来源为准。
- 为生成候选内容，临时获取了 12 份官方 PDF 并提取逐页文本；PDF 本体不保存到仓库。提取文本带有原始 URL、SHA-256 和图示/公式提取局限说明。
- 已获取 9 讲平台原始英文自动字幕。未下载音视频，不获取 Canvas、Piazza 等受限资料。
- 前 12 讲 Note、Blog 与前 9 讲中英文逐字稿已由用户确认，正式文件保存在讲次目录并显式登记到 outputs；候选与段落合并记录保留在 `references/`。具体范围与缺项见 [审核清单](../../workflow/review-queue.md)。

## 后续更新

先核对官网日程，再更新 `website/catalog-data/courses/cmu-11768-fall26.yaml` 与核验日期。官方新增资料应匹配已有 `scheduleCode` 和 `lecture-id`；若课程调整主题或日程，不对已有讲次批量重编号。

目前 `course sync` 仅支持特定 HTML 表格，不能用于该官网。更新后运行 `npm run build`，由现有生成器更新课程页面、参考资料页与独立侧栏。
