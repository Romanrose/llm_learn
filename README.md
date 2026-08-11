# LLM 学习仓库

这是一个围绕大语言模型（LLM）的个人共学仓库：把课程讲义、逐字稿与笔记、论文复现、Agent 教材和开发环境资料放在同一个可持续维护的知识库中，并通过 VitePress 生成统一的学习网站。项目采用“统一模板、渐进接入”的方式维护：当前以 CS336 2026 为完整样例，其他课程和项目在真正开始学习时再逐步加入。

学习主线是：**模型基础 → 从零实现 → 论文机制 → Agent 应用 → 工程实践**。仓库提供统一的网站和 Course CLI；课程内部的 Python、Node.js 和 Notebook 项目仍按各自 README 运行。

## 从这里开始

1. 先阅读[统一项目结构](workflow/standards/project-structure.md)、[学习与转写提示词手册](workflow/standards/prompt-handbook.md)和[课程逐字稿生成规范](workflow/standards/transcript-generation.md)。
2. 学习 [CS336 2026：Language Modeling from Scratch](llm/cs336-2026/)，用课程讲义和作业建立训练语言模型的系统认识。
3. 在 [`llm/cs336-2026/notes/`](llm/cs336-2026/notes/) 中按 Lecture 保存课程笔记、逐字稿与 Blog。
4. 结合 [`papers/30-paper-zhCN/`](papers/30-paper-zhCN/) 复现经典论文，随后进入 [`agent/hello-agents/`](agent/hello-agents/) 的 Agent 学习与实践。

## 学习网站

`website/` 集中保存 VitePress 网站、全站配置和课程元数据。课程与专题内容保留在 `llm/`、`agent/`、`infra/`、`papers/` 和 `interest/` 五个并列方向中；`website/course.yaml` 保存全局设置，`website/catalog-data/` 负责描述课程、Lecture 与逐字稿、Blog、讲义和 PDF 之间的关系，构建前会自动生成网站页面和导航。

```bash
npm install
npm run dev
```

正式构建使用 `npm run build`。GitHub Pages 的项目路径已经配置为 `/llm_learn/`；生产部署由合并到 `master` 的 GitHub Actions 负责。

### 本地环境配置

所有本机路径、模型服务地址和密钥统一放在根目录 `.env` 中；仓库提供 [.env.example](.env.example) 作为模板。复制后填写：

```bash
cp .env.example .env
```

`.env` 已被 Git 忽略，不能提交 API Key、Cookie 或其他凭据。课程脚本启动时会自动读取它，当前 Shell 中已经存在的环境变量优先级更高。

### Course 自动化

课程资源进入内容生成流程前，先同步官方课程表，再经过发现、审核和摄取三个阶段：

```bash
npm run course -- sync cs336-2026
npm run course -- prepare cs336-2026 lecture-01
npm run course -- transcript cs336-2026 lecture-01 --engine krillinai --dry-run
npm run course -- generate cs336-2026 lecture-01 --provider deepseek --run
npm run course -- validate cs336-2026 lecture-01 --provider deepseek
# 人工审核确认后再执行
npm run course -- promote cs336-2026 lecture-01 --provider deepseek --reviewed --overwrite
npm run course -- discover cs336-2026
npm run course -- approve cs336-2026 <resource-id>
npm run course -- ingest cs336-2026
npm run build
```

`sync` 从官方课程表更新 Lecture、日期、讲师、讲义和作业节点，同时保留已有逐字稿与 Blog 配置；`prepare` 匹配官方视频并优先提取已有字幕，生成正式英文逐字稿与 `sources.yaml`；`transcript --engine krillinai` 使用本地 KrillinAI 生成中英候选稿到每讲的 `references/krillinai/`，默认不覆盖正式稿，先用 `--dry-run` 校验接口；`generate --provider deepseek` 使用 `.env` 中的 DeepSeek 配置生成中文逐字稿、Lecture Note 和 Blog 候选稿到 `references/deepseek/`，也不会自动覆盖正式稿；当 `any` 或 `whisper` 可能回退到音频下载/ASR 时，必须显式增加 `--allow-audio-download`；`discover` 只生成候选清单；`approve` 由人确认允许进入知识库的资源；`ingest` 生成可追溯的本地资源清单。二进制讲义只有显式增加 `--download` 时才会下载。
`validate` 默认检查候选稿；对已经发布的正式稿使用 `course validate <course-id> <lecture-id> --published`。它会检查时间戳对应关系、重复段落、中文长度、文件头以及 Note/Blog 的时间轴边界。历史来源如果没有原语言逐字稿，会明确给出警告而不是伪装成完整对照稿。`promote` 只在传入 `--reviewed` 后将候选稿复制为正式稿，并写入 `review.yaml` 和 catalog 状态。正式文件已存在时还需要显式传入 `--overwrite`。

`course status` 同时显示“资源审核状态”和“Lecture 内容状态”；资源仍有待审核，不代表已经生成的 Lecture 内容不可阅读。

## 学习地图

| 阶段 | 内容 | 建议产出 |
| --- | --- | --- |
| 1. 模型基础 | CS336 讲义、作业与参考实现 | 每讲笔记、关键公式和最小复现实验 |
| 2. 论文机制 | Transformer、RAG、Scaling Law 等论文 Notebook | 一页论文卡片、可运行实验记录 |
| 3. Agent 应用 | ReAct、RAG、MCP、多智能体、Agentic RL | 小型 Agent 项目或章节练习 |
| 4. 工程实践 | 远程开发、GPU、网络和工具配置 | 可复现环境说明与踩坑记录 |

## 仓库结构

```text
llm_learn/
├── llm/
│   └── cs336-2026/                    # Stanford CS336 2026 学习主目录
│       ├── lectures/                  # 课程讲义、可执行代码与 Trace Viewer
│       ├── notes/lecture-NN/          # 逐讲笔记、逐字稿、Blog 与生成清单
│       ├── references/                # 作业、参考实现与课程级扩展材料
│       ├── resources/                 # 审核后摄取的官方资源
│       ├── exports/                   # PDF/XeLaTeX 等本地生成产物
│       └── UPSTREAM.md                # 讲义来源与同步说明
├── papers/
│   └── 30-paper-zhCN/                 # 经典论文的中文教学实现
├── agent/
│   ├── hello-agents/                  # 《Hello Agents》教材与配套代码
│   ├── memory/                        # 学习过程中的记忆/知识资料
│   └── tencentdb-agent-memory-tutorial/ # Agent Memory 渐进式教程
├── infra/                             # GPU、网络、远程开发与工具配置
├── interest/                          # 课外阅读与个人兴趣主题
├── website/                            # VitePress 网站、配置和课程元数据
│   ├── .vitepress/                     # 导航、主题和构建配置
│   ├── catalog-data/                   # 课程与资源 YAML
│   ├── course.yaml                     # 全站设置和分类
│   └── ...                             # 首页、专题页和生成页面
└── workflow/                           # 脚本、模板、规范和本地工具
    ├── scripts/                        # Course CLI、网站和导出脚本
    ├── standards/                      # 项目、逐字稿和质量规范
    ├── templates/                      # LaTeX 等可复用输出模板
    └── video/                          # 本地视频/字幕工具，不提交 Git
```

## CS336 快速开始

课程数据规范见 [`llm/cs336-2026/README.md`](llm/cs336-2026/README.md)，讲义运行说明见 [`llm/cs336-2026/lectures/README.md`](llm/cs336-2026/lectures/README.md)。一个典型的本地运行方式如下：

```bash
cd llm/cs336-2026/lectures
pip install -r requirements.txt
python execute.py -m lecture_01
```

讲义运行后可使用 Trace Viewer 查看执行轨迹。远程 Slurm、依赖和具体参数请以课程目录中的 README 为准。

课程内容按 Lecture ID 统一写入 `llm/cs336-2026/notes/lecture-NN/`，不再增加作者目录：

```text
llm/cs336-2026/notes/lecture-04/
├── sources.yaml            # 来源与追溯信息
├── generation.yaml         # 自动生成与审核状态
├── transcript.en.md        # 英文逐字稿
├── transcript.zh-CN.md     # 中文逐字稿
├── note.md                 # 课程讲义解读
├── blog.md                 # 网站文章
├── references/             # 本讲补充资料与历史稿
└── assets/                 # 图片与附件
```

以后新增课程或项目只复制这套结构和约定，不需要预先创建完整课程树。具体规则见[统一项目结构](workflow/standards/project-structure.md)。

视频转写采用“**优先使用字幕；没有字幕时，在得到账号/音频下载授权后使用本地 ASR**”的流程。转写规范、模型选择和 Markdown 公式写法请见[提示词手册](workflow/standards/prompt-handbook.md)。本机的转写工具放在 `workflow/video/`，仅供本地使用，不提交到 GitHub。

## 论文与 Agent 学习

### 经典论文实现

[`papers/30-paper-zhCN/`](papers/30-paper-zhCN/) 包含 30 篇经典论文的教学 Notebook，覆盖 RNN/LSTM、CNN、Transformer、VAE、Scaling Law、RAG 等主题。该目录使用独立的 `uv` 环境：

```bash
cd papers/30-paper-zhCN
uv sync
uv run jupyter notebook
```

### Agent 学习

[`agent/hello-agents/`](agent/hello-agents/) 覆盖 Agent 基础、ReAct、RAG、MCP、多智能体与 Agentic RL。建议边读教材、边运行 `code/` 目录里的示例，并将实验记录留在自己的笔记目录中。

## 贡献与同步约定

- 在分支上修改，通过 Pull Request 合并；不要直接覆盖他人的笔记。
- 课程内容放在 `llm/<完整课程 ID>/notes/<Lecture ID>/`；稳定产物使用 `note.md`、`blog.md`、`transcript.<语言>.md` 等固定文件名。
- 新增代码请说明依赖、运行命令和预期结果；论文笔记建议以 `YYYY-MM-DD-论文简称.md` 命名。
- 不提交 API Key、密码、私钥、真实服务器地址或未授权下载的内容。
- `.obsidian/`、`workflow/video/`、课程运行缓存和本地虚拟环境均为本地文件，不进入远程仓库；`workflow/scripts/`、`workflow/standards/` 和 `workflow/templates/` 是仓库正式内容。

## 资料来源

- CS336 的上游讲义、许可证与同步说明见 [`llm/cs336-2026/UPSTREAM.md`](llm/cs336-2026/UPSTREAM.md)。
- 各教材与论文实现保留其上游说明与许可证；使用和再分发时请遵循对应目录中的规则。
