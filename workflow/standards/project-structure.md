# llm_learn 统一项目结构

版本：1.0

本规范用于约束以后新增的课程、论文、Agent 教程和工程项目。当前重点是 `llm/cs336-2026/`，其他内容按需渐进式接入，不要求一次性补齐所有课程。

## 1. 设计原则

- 先有真实学习内容，再增加目录；不为“未来可能使用”创建空壳结构。
- 每个内容单元都有稳定 ID，目录、catalog-data、网站路由和生成记录使用同一个 ID。
- 原始资料、过程稿、正式稿和网站产物分层保存，避免互相覆盖。
- 自动化只生成候选稿和网站页面；来源、术语、公式、时间轴和发布状态由人确认。
- 生成页面不是源文件，不能直接编辑 `website/generated/`。
- 本地密钥、Cookie、音频、缓存和构建产物不进入 Git。

## 2. 顶层目录

```text
llm_learn/
├── llm/                     # LLM 课程学习内容
│   └── <course-id>/
├── agent/                   # Agent 教材和独立项目
│   └── <project-id>/
├── infra/                   # AI Infra 与开发环境资料
├── papers/                  # Paper 阅读、复现和教学实现
├── interest/                # 课外阅读与个人兴趣主题
├── website/                 # VitePress 网站、课程元数据和网站配置
│   ├── .vitepress/          # 主题、导航和构建配置
│   ├── catalog-data/        # 课程与资源元数据，不保存正文
│   │   ├── courses/         # <course-id>.yaml
│   │   └── reviews/         # 资源发现与审核清单
│   └── course.yaml          # 全站分类和网站设置
└── workflow/                # 自动化脚本、模板、规范和本地工具
    ├── scripts/             # 课程、网站和导出自动化
    ├── standards/           # 项目、逐字稿和质量规范
    ├── templates/           # 可复用的输出模板
    ├── .runtime/            # 本地可复现运行时（由 bootstrap 创建，不提交 Git）
    └── video/               # 旧的本地视频/字幕工具，不提交 Git
```

## 3. 课程模板

课程必须使用完整、稳定的课程 ID，例如 `cs336-2026`：

```text
llm/<course-id>/
├── README.md                # 课程入口、目录和运行说明
├── UPSTREAM.md              # 官方来源、许可证和同步说明
├── lectures/                # 官方讲义快照或可执行课程材料
├── notes/
│   └── <lecture-id>/        # 例如 lecture-04
│       ├── sources.yaml     # 来源与追溯
│       ├── generation.yaml  # 自动生成记录
│       ├── review.yaml       # 人工审核记录
│       ├── transcript.en.md
│       ├── transcript.zh-CN.md
│       ├── note.md
│       ├── blog.md
│       ├── references/      # 候选稿、补充材料、历史稿
│       └── assets/          # 图片和附件
├── references/              # 课程级作业、代码和扩展阅读
├── resources/               # 审核后的资源清单和可选下载文件
└── exports/                 # 本地生成的 PDF/XeLaTeX，不提交 Git
```

不是每一讲都必须拥有全部产物。`website/catalog-data/courses/<course-id>.yaml` 的 `outputs` 是网站展示的唯一来源。

## 4. Agent、论文和工程项目模板

独立项目不强行套用 Lecture 结构，但保留相同的 ID、来源和产物原则：

```text
agent/<project-id>/
├── README.md                # 项目目标、学习路径和运行命令
├── docs/                    # 教程或设计文档
├── examples/                # 可运行示例
├── src/                     # 项目源码（有需要时）
├── tests/                   # 测试（有需要时）
├── assets/                  # 图片和静态附件
├── package.json / pyproject.toml
└── .env.example             # 只写变量名和示例，不写密钥
```

论文复现使用 `papers/<paper-id>/`，至少包含 `README.md`、来源说明、实现或 Notebook、实验结果和环境文件。已有上游项目的内部目录与 README 保持上游语义，不为了统一外观改写第三方内容。

## 5. Catalog 与网站关系

```text
正文文件 ──┐
来源清单 ──┼─> website/catalog-data/*.yaml ──> workflow/scripts/generate-site.mjs ──> website/generated/
审核记录 ──┘                                                        └───────> VitePress / Pages
```

- `website/catalog-data/courses/` 描述课程、Lecture、来源和网站产物。
- `website/generated/` 和 `website/.vitepress/generated/` 是构建时生成的中间文件。
- `website/` 中的首页、专题页和 Vue 组件是手工维护的网站入口。
- 课程 PDF 由 `workflow/templates/latex/` 和 `note.md` 生成，输出放在 `exports/`，部署构建时临时复制到 `website/public/generated/`。

## 6. 渐进式接入流程

新增课程或项目时只做当前学习需要的最小闭环：

1. 分配稳定 ID，创建入口 README。
2. 在 `website/catalog-data/` 登记来源和内容单元。
3. 保存官方资料或代码，并记录 `UPSTREAM.md` 或来源清单。
4. 生成并人工审核必要的逐字稿、Note、Blog 或实验记录。
5. 将已确认的产物登记到 `outputs`，运行 `npm run build`。
6. 学到下一部分时再扩展目录，不提前复制整套空目录。

CS336 2026 是当前模板的完整示例；以后新增课程只需复制结构和流程，不需要复制它的全部内容。
