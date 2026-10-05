> 当前状态更新：2026-10-03 用户批准已有 Note / Blog，已登记正式 outputs。下方候选阶段记录保留来源与缺口；新ASR逐字稿另行待校对。

# CS147 Autumn 2026：资料覆盖与版本核查

核查日期：2026-10-03。当前是公开资料阶段的补充，不代表课程全部讲座已发布或候选稿已审核。

## 已补充

- 十个稳定作业单元各有原创中文学习 Note 与独立 Blog 候选，共 20 篇；见课程 [README](../README.md)。
- 已阅读 [2026 作业总览](https://hci.stanford.edu/courses/cs147/2026/au/assignments.pdf)、[时间线](https://hci.stanford.edu/courses/cs147/2026/au/timeline.pdf)、[课程日程](https://hci.stanford.edu/courses/cs147/2026/au/calendar.html)，并补充 A1/A2 真正的 2026 独立说明链接。
- 三份公开讲义各有 Note/Blog 候选，共 6 篇；记录实际内容版本，保留作业导航的身份。
- 日程中 61 个去重可见链接保存于 [official-links.yaml](official-links.yaml)，包括公开阅读、外部补充视频、讲义/媒体链接与受限阅读标记。链接索引不等于逐项已阅读、可访问或获准转载。

## 真正的讲义候选

| 单元 | PDF 内容版本 | 候选 Note | 候选 Blog |
| --- | --- | --- | --- |
| Lecture 01 · Introduction | 2026，72 页 | [Note](../references/lectures/lecture-01/codex/note.md) | [Blog](../references/lectures/lecture-01/codex/blog.md) |
| Lecture 02 · Design Discovery | **2025，86 页；由 2026 日程链接复用** | [Note](../references/lectures/lecture-02/codex/note.md) | [Blog](../references/lectures/lecture-02/codex/blog.md) |
| Lecture 03 · Define | 2026，81 页 | [Note](../references/lectures/lecture-03/codex/note.md) | [Blog](../references/lectures/lecture-03/codex/blog.md) |

讲义候选整理可核实的主题，并给原创练习；不是逐页翻译，也没有补写图片案例中的课堂口述。Lecture 03 标注 CC BY-NC-SA 3.0；其他材料未核实可再分发许可，仅保留官方外链。

## 字幕与尚未公开的内容

- 十个 assignment 单元是作业，不是十讲录像。不能给它们拼装逐字稿。
- 日程的 Design Discovery 指向 `lectures/02-design-discovery.mp4`，但没有可见字幕文件/轨道入口；讲义实际是 2025，录制年份未确认。字幕发现阶段未下载媒体；随后用户明确授权临时音频获取，已完成本地ASR和对齐中文翻译候选，录制年份仍未确认。
- Introduction/Define 有 PDF/PPT，无可见课堂录像或字幕入口；未找到可生成对应完整英中逐字稿的来源。
- 未来 Ideate、Concept Videos、Exploration、Early Stage Prototyping、Visual Information Design、Human Abilities、Conceptual Models、Heuristic Evaluation、HCI Visions、Usability Testing、Design Patterns、Guest Lecture、Career Panel、What is HAI 等当前只有日程主题或阅读链接，未据此生成课堂 Note/逐字稿。
- Klemmer 视觉设计、Typography、Grids 等 YouTube 视频是日程指定的外部补充资源，不等于 2026 课堂录像；字幕及转载许可未逐项审核，先保留准确外链。
- `readings/restricted/` 材料仅记录链接和限制，未读取、复制或绕过访问。
- `videos.html`、`webresources.html` 由导航链接，但公开请求返回 404；没有将其标为可用资源。

## 版本冲突

1. `02-design-discovery.pdf` URL 含 2026，但封面与页脚是 Autumn 2025 / September 24, 2025；保留为复用资料，不能声称最新版内容。
2. `logistics.html` 页面标题仍写 2025，正文部分安排指向 2026；教学政策只作为需复核的课程规则，不机械导入本地规则。
3. A2 独立 2026 PDF 写 Oct 9–10；calendar/timeline 写 Oct 8–9。正式截止时间需课程最新通知核验，本地不替课程确认。
4. calendar 出现 A11 Final Report，总览是十个单元。将 final report 视为官方日程已列出的额外课程级交付，不改动现有 assignment-01..10；未找到独立公开 A11 说明，因此只保留日程入口。

## 发布与下一步

候选阶段曾保持 `candidate-ready` / `review.state: pending`；2026-10-03 用户已批准现有26篇 Note / Blog，相关 `run.yaml` 的 review 已更新为 approved，正式 outputs 已登记。新增ASR由独立 `transcript-run.yaml` 管理，仍待校对。结构检查不证明内容审核通过。未来官方资料更新时，先核查真实版本、日期与许可，再补充来源；确有字幕时才生成完整原语言及中文逐字稿。

## 第二轮字幕发现

五个YouTube补充视频均执行无登录、无Cookie、只字幕的实际提取且全部成功，不能将它们报成无字幕。前四为2022/2013旧材料的英文自动字幕，Inclusive Design为2014材料且有英文人工字幕。平台没有返回开放许可，现保存成功提取证据与官方字幕入口，未将完整版权文本复制或翻译进仓库。详见 [caption-discovery.yaml](caption-discovery.yaml)。

- [CS 147 2022: Experience Prototyping](../references/supplements/experience-prototyping-2022/README.md)。
- [Lecture 3.1 Visual Design](../references/supplements/visual-design-2013/README.md)。
- [Lecture 3.2 Typography](../references/supplements/typography-2013/README.md)。
- [Lecture 3.3 Grids and Alignment](../references/supplements/grids-alignment-2013/README.md)。
- [Meet The Normals - Adventures in Universal Design](../references/supplements/inclusive-design-2014/README.md)。

真正课堂候选 `02-design-discovery.mp4` HEAD确认200；同名VTT/SRT与英文变体404，公开HTML无track。字幕发现阶段曾标 `needs-audio-authorization`；用户本轮已明确授权，现完成临时音频提取、本地ASR与全文翻译候选，sources更新为 `asr-draft-ready`，录制年份仍待核实。

## 授权音频ASR结果

公开视频时长6829.61秒，临时音频6829.545938秒。采用Apple GPU / mlx-whisper / whisper-small.en-mlx，不调用远程ASR；中文只依据英文ASR逐段翻译。新稿仍待审核，不继承此前26篇Note/Blog批准。

- [英文ASR候选](../references/lectures/lecture-02/codex/transcript.en.md)、[中文对照候选](../references/lectures/lecture-02/codex/transcript.zh-CN.md)。
- [独立转写记录](../references/lectures/lecture-02/codex/transcript-run.yaml)、[结构检查与低置信度定位](../references/lectures/lecture-02/codex/transcript-checks.yaml)、[术语修正与重识别日志](../references/lectures/lecture-02/codex/transcript-edit-log.json)。
- 讲者明确五分钟休息的时间空白已解释；01:45:47–01:49:32录音近乎数字静默，无法恢复此段缺失话语。正文保留对应时间戳说明，不从讲义补写。初次ASR在静默期间出现循环Thank you机器幻觉，已依据音频与定点重识别去除并留痕。
- 定点重识别恢复静默后的伦理讲解；低置信度段落与未核专名在正文显式标记。结构对齐不证明识别/翻译准确，尚需回听确认。原始ASR JSON不含本地路径或请求头，临时音频不进入Git。
