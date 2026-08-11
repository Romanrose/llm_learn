# CS336 2026

本目录保存 Stanford CS336 2026 的官方课程材料、原始资源、逐讲内容和导出文件。课程唯一 ID 为 `cs336-2026`，内容归属由仓库根目录 `course.yaml` 的 `owner` 字段统一定义，不再按作者拆分目录。

CS336 2026 是当前仓库的完整课程样例。以后新增课程时，先复制本目录的组织原则和 catalog 配置，只接入正在学习的 Lecture，不要求一次性把整门课的所有资源和页面都补齐。

所有逐字稿遵循仓库级[课程逐字稿生成规范](../../standards/transcript-generation.md)。

## 数据目录

```text
llm/cs336-2026/
├── lectures/                 # 官方讲义仓库快照与可执行 Lecture
├── references/               # 课程级扩展阅读、补充笔记和参考实现
├── resources/                # discover/approve/ingest 后的资源清单与下载文件
├── notes/
│   └── lecture-NN/           # 每讲的文字内容，目录名与 catalog item ID 一致
│       ├── sources.yaml      # 视频、字幕、讲义等来源与追溯信息
│       ├── generation.yaml   # 自动生成任务、输入输出和审核状态
│       ├── review.yaml       # 人工审核记录（需要时创建）
│       ├── transcript.en.md  # 英文逐字稿
│       ├── transcript.zh-CN.md # 中文逐字稿
│       ├── note.md           # 课程讲义解读 / Lecture Note
│       ├── blog.md           # 面向网站发布的技术文章
│       ├── references/       # 仅属于本讲的补充材料和历史稿
│       └── assets/           # 本讲图片和附件
├── exports/                  # PDF、XeLaTeX 等生成产物，不提交 Git
└── UPSTREAM.md               # 官方讲义快照来源和同步方法
```

并非每讲都必须同时拥有全部文件。网站是否展示某个产物，以 `catalog/courses/cs336-2026.yaml` 中对应 Lecture 的 `outputs` 为准。

## 命名规则

- 课程目录使用完整 ID：`<category>/<course-id>/`，例如 `llm/cs336-2026/`。
- Lecture 目录直接使用 catalog ID：`lecture-01`、`lecture-12`。
- 稳定内容使用固定文件名，不在文件名中重复 Lecture 编号。
- 字幕文件使用 BCP 47 风格语言标签：`transcript.en.md`、`transcript.zh-CN.md`。
- 过程文件和历史材料放入本讲的 `references/`，图片与附件放入 `assets/`。

## 自动化入口

在仓库根目录运行：

```bash
npm run course -- sync cs336-2026
npm run course -- prepare cs336-2026 lecture-01
npm run course -- transcript cs336-2026 lecture-01 --engine krillinai --dry-run
npm run course -- generate cs336-2026 lecture-01 --provider deepseek --run
npm run course -- validate cs336-2026 lecture-01 --provider deepseek
npm run course -- validate cs336-2026 lecture-01 --published
npm run course -- export cs336-2026 lecture-04
npm run course -- generate cs336-2026 lecture-01 --run
npm run build
```

课程路径只在 `catalog/courses/cs336-2026.yaml` 的 `paths` 中配置；自动化脚本不再接收作者目录参数。

`transcript --engine krillinai` 是新的候选字幕入口。它使用本机 `workflow/video/krillinai/krillinai-cli`（或 `COURSE_KRILLINAI` 指定的二进制），优先取平台字幕、必要时按 KrillinAI 配置回退处理，并将中英 SRT、Markdown 候选稿和运行清单写入 `notes/lecture-NN/references/krillinai/`。该目录中的内容不会自动展示在网站，也不会覆盖同级正式的 `transcript.en.md` 与 `transcript.zh-CN.md`。先运行 `--dry-run`；实际生成前请完成 KrillinAI 的模型/密钥配置。`--caption-source any` 与 `whisper` 可能下载音频，命令要求额外传入 `--allow-audio-download`；只使用平台字幕时可指定 `manual` 或 `auto`。审核术语、完整性和时间轴后再手动采纳。

`generate --provider deepseek` 会读取根目录 `.env` 中的 DeepSeek 配置，基于英文逐字稿和本讲讲义代码生成中文逐字稿、Lecture Note 与 Blog 候选稿，统一写入 `notes/lecture-NN/references/deepseek/`。候选稿需要人工检查完整性、术语、幻觉和引用后，才能复制到正式文件名。

审核通过后使用默认的 `course validate` 检查 `references/<provider>/` 中的候选稿，再显式执行 `course promote ... --reviewed --overwrite`。`promote` 会把候选逐字稿、Note 和 Blog 提升到正式文件，并生成本讲 `review.yaml`；未传 `--reviewed` 时不会执行提升。已经发布的正式稿使用 `course validate ... --published` 复查，历史来源缺少原语言逐字稿时必须保留审核警告。

## 渐进式接入原则

一门新课程的最小闭环是：

1. 在 `catalog/courses/<course-id>.yaml` 登记课程和正在学习的 Lecture。
2. 在 `llm/<course-id>/` 保存官方材料和来源说明。
3. 只为当前 Lecture 创建 `notes/<lecture-id>/`，按需生成逐字稿、Note、Blog 或 PDF。
4. 人工审核后把正式产物登记到 `outputs`，再运行 `npm run build`。

没有实际内容的 Lecture 不创建空的产物目录；课程状态和网站展示以 catalog 为准。
