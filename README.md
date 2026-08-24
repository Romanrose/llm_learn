# llm_learn

[学习网站](https://romanrose.github.io/llm_learn/) · 课程笔记、讲义解读、逐字稿与学习资料库

`llm_learn` 是一个以课程为主线的个人学习知识库。它从官方课程页面、视频和讲义出发，逐步整理为可浏览的课程资料、逐讲笔记、Blog 解读、中英文逐字稿、延伸阅读与 PDF；项目、论文和访谈则作为学习路径中的补充入口，不复制或替代其上游仓库。

网站与内容均遵循“先有真实学习内容，再逐步接入”的原则：自动化只产出候选稿，正式公开内容需要经过人工审核。

供 Codex、Claude Code 等编程 Agent 使用的仓库约定见 [AGENTS.md](AGENTS.md)。

## 当前收录

| 类型 | 内容 | 当前状态 | 网站入口 |
| --- | --- | --- | --- |
| 课程 | Stanford CS336 2026 · Language Modeling from Scratch | 19 讲；已整理 17 讲的课程笔记、Blog 与中英文逐字稿 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs336-2026/) |
| 课程 | Stanford CS149 Fall 2025 · Parallel Computing | 已接入课程主页、18 讲 Slides、公开视频与参考资料；笔记暂不公开 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs149-fall25/) |
| 项目资料 | Hello Agents、Agent Memory、TencentDB Agent Memory | 保留项目源码、教程与学习入口 | [智能体专题](https://romanrose.github.io/llm_learn/topics/agent/) |
| 工程资料 | Network、SSH、多服务器开发、GPU Systems | 保留工程笔记与课程关联资料 | [AI Infra 专题](https://romanrose.github.io/llm_learn/topics/infra/) |
| 论文与延伸阅读 | 30 Papers、技术文章、访谈与演讲 | 按专题持续归档 | [课程与专题](https://romanrose.github.io/llm_learn/#course-map) |

## 仓库结构

```text
llm_learn/
├── llm/                         # 大模型课程的原始资料与逐讲内容
│   └── cs336-2026/
│       ├── lectures/             # 官方讲义快照与可执行材料
│       ├── notes/lecture-NN/     # 正式逐字稿、Note、Blog、来源和审核记录
│       ├── references/           # 课程级扩展阅读、作业与参考实现
│       ├── resources/            # 审核后的资源清单
│       └── exports/              # 本地生成的 PDF / XeLaTeX（不提交）
├── infra/
│   ├── cs149-fall25/             # 并行计算课程资料与学习计划
│   └── network/                  # 网络、SSH、远程开发笔记
├── agent/                        # Agent 教材与独立项目
├── papers/                       # 论文阅读、复现与教学实现
├── interest/                     # 课外阅读与个人兴趣主题
├── website/                      # 当前生效的 VitePress 网站
│   ├── catalog-data/             # 课程、讲次、来源与网站产物的元数据
│   ├── .vitepress/               # 主题、导航和构建配置
│   ├── topics/                   # 项目与专题入口页
│   └── course.yaml               # 全站分类和站点设置
└── workflow/                     # 课程、网站、转写与 LaTeX 自动化
    ├── scripts/
    ├── standards/
    └── templates/
```

当前网站构建入口是 `website/` 与 `workflow/`。课程元数据、站点分类、自动化脚本和规范均以这两个目录为唯一编辑入口。

## 本地预览与构建

```bash
npm install
npm run workflow:bootstrap
npm run workflow:doctor
npm run dev
```

本地站点默认运行在 `http://127.0.0.1:5173/llm_learn/`。正式构建：

```bash
npm run build
```

构建会先生成课程页面和可发布的 PDF，再执行 VitePress 构建。推送到 `master` 后，GitHub Actions 会自动发布到 [GitHub Pages](https://romanrose.github.io/llm_learn/)。

课程工作流的可复现安装、诊断和协作交接说明见 [workflow/README.md](workflow/README.md)。运行时、下载缓存和 `.env` 均只保留在本机，不进入 Git。

## 课程内容如何生成

课程的正文、资源清单和审核记录在本地保存；`website/catalog-data/courses/<course-id>.yaml` 决定哪些内容会在网站展示。

```text
官方课程资源
  → 发现与人工审核
  → 字幕 / 讲义 / 候选稿
  → 人工校对与发布确认
  → Catalog 登记
  → 网站页面与 PDF
```

常用命令：

```bash
# 同步课程表、发现公开资源
npm run course -- sync cs336-2026
npm run course -- discover cs336-2026

# 准备字幕与生成候选稿
npm run course -- prepare cs336-2026 lecture-01
npm run course -- transcript cs336-2026 lecture-01 --engine krillinai --dry-run
npm run course -- generate cs336-2026 lecture-01 --provider deepseek --run

# 审核候选稿并显式发布
npm run course -- validate cs336-2026 lecture-01 --provider deepseek
npm run course -- promote cs336-2026 lecture-01 --provider deepseek --reviewed --overwrite

# 导出单讲 PDF 或构建全站
npm run course -- export cs336-2026 lecture-04
npm run build
```

`generate`、`transcript` 生成的是候选内容，不会自动覆盖正式笔记。只有通过校对后执行带 `--reviewed` 的 `promote`，相关产物才会成为可发布内容。完整约定见：[项目结构规范](workflow/standards/project-structure.md)、[逐字稿规范](workflow/standards/transcript-generation.md) 和 [提示词手册](workflow/standards/prompt-handbook.md)。

## 新增一门课程

不需要先创建完整的空目录。只为正在学习的部分建立最小闭环：

1. 分配稳定课程 ID，并创建课程入口与来源说明。
2. 在 `website/catalog-data/courses/<course-id>.yaml` 登记课程、讲次和官方资料。
3. 在 `llm/<course-id>/` 或对应分类目录保存真实资料、笔记与实验。
4. 生成候选逐字稿、Note 或 Blog，完成审核后再登记到 `outputs`。
5. 运行 `npm run build`，检查课程页后发布。

CS336 是完整课程工作台的参考实现；CS149 展示了“先接入官方资料、后逐讲补充笔记”的轻量接入方式。

## 本地环境与资料边界

将本机模型服务地址、密钥和路径写入 `.env`；可从 [.env.example](.env.example) 复制。不要提交 API Key、Cookie、真实服务器地址、未授权下载的音视频或本地缓存。

课程讲义、视频、论文和项目代码仍归原作者及课程方所有。本仓库默认以外链、来源清单和自行完成的学习笔记为主；使用、下载和再分发请遵循各上游项目的许可证与课程规则。
