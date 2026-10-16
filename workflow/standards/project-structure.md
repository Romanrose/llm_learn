# llm_learn 统一项目结构

版本：2.0 · 2026-10-16

本规范按用户明确要求迁移实际课程目录。旧路径对照与本地克隆说明见[目录迁移表](directory-migration-2026-10.md)。

## 顶层职责

| 目录 | 职责 |
| --- | --- |
| `courses/foundations/` | 编程与计算机系统课程 |
| `courses/models-agents/` | 大模型、强化学习、生成模型与智能体课程 |
| `courses/software-product/` | 软件工程、产品管理与交互设计课程 |
| `courses/robotics-hardware/` | 小型机器人、嵌入式系统与端侧 AI 课程 |
| `references/` | 非课程的上游项目、论文、工程资料和其他阅读 |
| `website/` | 网站内容、主题、导航与唯一一套 catalog 元数据 |
| `workflow/` | 脚本、模板、内容规范与本地工具 |

不另建平行的 `site/`、根级 `catalog/`、`scripts/` 或第二套 `course.yaml`。课程源目录按首页方向组织；catalog 的技术 `category` 可保留 `llm`、`agent`、`infra` 等标签，不用标签推断文件夹。

## 课程源目录

```text
courses/<group>/<course-id>/
├── README.md                    # 课程入口、内容边界和学习说明
├── UPSTREAM.md                  # 官方来源、版本及更新说明（按需）
├── resources/                   # 官方外链清单与资源审核记录
├── lectures/                    # 已有授权的代码 / 讲义快照（按需）
├── notes/<lecture-id>/
│   ├── sources.yaml             # 字幕、讲义与追溯信息
│   ├── generation.yaml          # 生成记录
│   ├── review.yaml              # 审核记录
│   ├── note.md                  # 课程笔记
│   ├── blog.md                  # 独立解读
│   ├── transcript.en.md         # 英文逐字稿
│   ├── transcript.zh-CN.md      # 中文逐字稿
│   ├── references/<provider>/   # 候选稿和过程材料
│   └── assets/                  # 本讲附件
├── references/                  # 课程级补充阅读
└── exports/                     # 生成的 PDF / XeLaTeX，不提交
```

只创建已经需要的文件与目录。仅接入官方资料的课程可以只有 README 与 metadata；不预建空讲次。课程 ID 与讲次 ID 跨目录、catalog、审核记录和网站路由保持一致。每个年份分别使用稳定 ID。

## 元数据与发布

- `website/course.yaml`：站点设置、四个首页方向、课程入口和历史版本关系。
- `website/catalog-data/courses/<course-id>.yaml`：课程身份、来源、讲次、`paths`、`practice`、`outputs`。
- `paths.root` 指向 `courses/<group>/<course-id>`；其他源路径、`outputs.source` 和导出来源也需同步更新。
- `outputs` 是正文公开的唯一依据；`publishOutputs: false` 保持仅资源导航，不因迁移而开放候选稿。
- `website/generated/` 与 `website/.vitepress/generated/` 是生成文件，不手改、不提交。
- PDF 构建时写入课程 `exports/`，部署所需文件临时复制到 `website/public/generated/`。

## 补充资料

`references/agents/`、`references/engineering/`、`references/papers/`、`references/interests/` 保存原有补充材料。第三方项目保持内部语义、许可证和来源，不强行改成 Lecture 结构。

## 新增或迁移课程

1. 分配稳定 ID，创建课程 README，注明来源和可公开内容。
2. 配置 catalog 的 `paths`、官方资源与当前讲次，再登记首页方向。
3. 课程资料默认保留官方外链；音视频下载和 ASR 仍需用户明确授权。
4. 准备证据、生成候选稿并审核后，才把正式内容登记到 `outputs`。
5. 运行 `npm run validate:structure` 和 `npm run build`，核对公开路由、资料关联和来源文件。

本地密钥、Cookie、运行时、音视频与缓存不进入 Git。结构迁移不改变网站视觉、课程 URL、内容类型边界或审核状态。
