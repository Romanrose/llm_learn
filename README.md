# llm_learn

[学习网站](https://romanrose.github.io/llm_learn/) · [资料检索](https://romanrose.github.io/llm_learn/generated/resources/) · [课程源码目录](courses/README.md) · [维护指南](workflow/README.md)

以课程为主线的个人学习资料库，覆盖编程与系统、大模型与智能体、软件与产品、机器人与 AI 硬件。仓库保存课程来源、资料索引、学习笔记和审核记录；网站提供课程导航、资料检索以及官方 Lab 与作业入口。

目前有 **18 个课程入口、19 套课程版本资料**，其中 CMU 15-213 同时保留 2026 与 2015 历史版本；UVA 产品管理入口包含五门子课程。课程单元可能是讲座、阅读、教程或作业，不把单元数统一当作讲次数。

## 从哪里开始

- **阅读与学习**：从[网站课程目录](https://romanrose.github.io/llm_learn/)选课，或在[资料库](https://romanrose.github.io/llm_learn/generated/resources/)按课程、关键词和类型检索。Lab 与作业使用课程官方公布的仓库、题目页或 Notebook。
- **查看课程文件**：进入 `courses/<方向>/<course-id>/`，从该课 README 查看来源和内容边界。
- **维护网站**：编辑 `website/`；课程与讲次的权威元数据位于 `website/catalog-data/courses/`。
- **整理学习内容**：按 [workflow/README.md](workflow/README.md) 准备资料、生成候选稿、审核并发布。

## 课程目录

以下链接分别进入仓库中的课程文件和已生成的网站课程页。年份对应所接入的课程版本；未标学期的当前在线资料单独说明。

### 编程与计算机系统

程序设计、计算机系统与并行计算。

| 课程与本地资料 | 学习重点 | 网站 |
| --- | --- | --- |
| [CS61A Fall 2026](courses/foundations/cs61a-fall26/) | Python、递归、数据抽象与程序设计 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs61a-fall26/) |
| [CMU 15-213 Fall 2026](courses/foundations/cmu-15213-fall26/) | C、机器代码、内存、进程、网络与并发 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cmu-15213-fall26/) |
| [15-213 Fall 2015](courses/foundations/cmu-15213-fall15/) | 2015 历史录像与配套资料；与 2026 分开使用 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cmu-15213-fall15/) |
| [CS149 Fall 2025](courses/foundations/cs149-fall25/) | 多核、CUDA、并行性能与同步 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs149-fall25/) |

### 大模型与智能体

语言模型、强化学习、生成模型与 Agent 工程。

| 课程与本地资料 | 学习重点 | 网站 |
| --- | --- | --- |
| [CS224N Winter 2026](courses/models-agents/cs224n-winter26/) | NLP、Transformer、预训练、对齐与评测 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs224n-winter26/) |
| [CS336 2026](courses/models-agents/cs336-2026/) | 从零训练语言模型，覆盖系统、数据、规模与后训练 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs336-2026/) |
| [CMU 11-768 Fall 2026](courses/models-agents/cmu-11768-fall26/) | 工具、上下文、记忆、Agent 训练与评估 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cmu-11768-fall26/) |
| [CS329Z Fall 2026](courses/models-agents/cs329z-fall26/) | RAG、编排、多智能体、评测与安全 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs329z-fall26/) |
| [Harvard CS2680 Fall 2026](courses/models-agents/harvard-cs2680-fall26/) | Coding Agent、Agent 系统与高效推理服务 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/harvard-cs2680-fall26/) |
| [CS224R Spring 2026](courses/models-agents/cs224r-sp26/) | 模仿学习、Actor-Critic、离线 RL 与 LLM / 机器人应用 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs224r-sp26/) |
| [MIT 6.S184 2026](courses/models-agents/mit-6s184-2026/) | Flow Matching、扩散模型、ODE / SDE 与生成实践 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/mit-6s184-2026/) |

### 软件与产品开发

软件质量、需求发现、交互设计与 AI 产品。

| 课程与本地资料 | 学习重点 | 网站 |
| --- | --- | --- |
| [MIT 6.102 Spring 2026](courses/software-product/mit-6102-sp26/) | TypeScript、规格、测试、抽象与并发 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/mit-6102-sp26/) |
| [UVA Digital Product Management · 当前在线版](courses/software-product/uva-digital-product-management/) | 五门子课程：定位、敏捷、假设验证、分析与团队 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/uva-digital-product-management/) |
| [Stanford CS147 Autumn 2026](courses/software-product/cs147-fall26/) | 需求访谈、原型、可用性测试与设计项目 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs147-fall26/) |
| [CS329X Fall 2026](courses/software-product/cs329x-fall26/) | 人类偏好、人机协作与 LLM 交互评估 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cs329x-fall26/) |
| [Berkeley UX for AI Spring 2026](courses/software-product/berkeley-ux-ai-sp26/) | AI 产品用户体验；目前仅公开课程介绍 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/berkeley-ux-ai-sp26/) |

### 机器人与 AI 硬件

桌面机械臂、嵌入式系统与端侧部署。

| 课程与本地资料 | 学习重点 | 网站 |
| --- | --- | --- |
| [JHU Hands-on Robot Learning Fall 2026](courses/robotics-hardware/jhu-robot-learning-fall26/) | SO-101 机械臂、数据采集、模仿学习与 VLA | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/jhu-robot-learning-fall26/) |
| [MIT 6.5940 Fall 2026](courses/robotics-hardware/mit-65940-fall26/) | 剪枝、量化、MCUNet、TinyEngine 与端侧推理 | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/mit-65940-fall26/) |
| [Cornell ECE4760 / 5730 · 当前公开版](courses/robotics-hardware/cornell-ece4760-current/) | Pico 2 / RP2350、通信、信号处理与 PID | [进入课程](https://romanrose.github.io/llm_learn/generated/courses/cornell-ece4760-current/) |

## 仓库结构

```text
llm_learn/
├── courses/                       # 课程源文件，方向与网站首页对应
│   ├── foundations/               # 编程与计算机系统（含历史版本）
│   ├── models-agents/             # 大模型与智能体
│   ├── software-product/          # 软件与产品开发
│   └── robotics-hardware/         # 机器人与 AI 硬件
├── references/                    # 配套学习材料与上游项目
│   ├── agents/                    # Hello Agents、记忆教程及项目
│   ├── engineering/               # 网络、SSH 与工程笔记
│   ├── papers/                    # 论文阅读与教学实现
│   └── interests/                 # 其他阅读笔记
├── website/                       # VitePress 网站及权威元数据
│   ├── catalog-data/courses/      # 课程、讲次、来源、paths 和 outputs
│   ├── .vitepress/                # 主题、导航与构建配置
│   ├── references/                # 网站中的版本与访问说明页
│   └── course.yaml                # 首页分类与站点设置
├── workflow/                      # 同步、审核、生成与 PDF 工具
│   ├── scripts/
│   ├── standards/
│   └── templates/
├── AGENTS.md                      # 编程 Agent 的协作约定
└── package.json                   # 网站与课程工作流命令
```

`courses/` 保存课程内容，`references/` 保存配套材料，`website/` 决定如何公开展示，`workflow/` 提供维护工具。补充材料的分类入口见 [references/README.md](references/README.md)。

每门课按需要建立 `README.md`、`UPSTREAM.md`、`resources/`、`notes/<lecture-id>/` 和 `references/`；只保存官方外链的课程不预建空笔记。单讲内容分别使用 `note.md`、`blog.md`、`transcript.en.md`、`transcript.zh-CN.md`，PDF 输出在被 Git 忽略的 `exports/`。

## 资料与发布状态

课程间的完整度不同。CS336 和 CMU 11-768 已有较多正式学习内容；其他课程可能提供阅读笔记，也可能只接入官方讲义、作业或日程。Berkeley UX for AI 目前仅有官方课程介绍；秋季课程尚未公开的后续资料保留预告状态。

- 官方讲义、视频、论文、仓库和作业优先保留原站链接；访问权限以课程方为准。
- 历史录像与当前课程分别标注，课程演示代码与作业起始代码分别登记。
- AI 生成内容先作为候选稿，经校对后再登记 `outputs`。目录中存在文件不代表已在网站发布。
- `publishOutputs: false` 的课程仅发布资源导航；候选内容不会因目录迁移而自动公开。

## 本地预览与构建

使用 Node.js 24 与 npm。完整构建还需要系统可用的 XeLaTeX 和中文字体；GitHub Actions 已配置安装所需 TeX 组件。字幕与模型服务是可选的内容维护依赖，浏览和编辑网站不需要配置模型 API。

在仓库根目录运行：

```bash
npm ci
npm run validate:structure
npm run dev
```

开发地址以终端输出为准，通常是 `http://localhost:5173/llm_learn/`。生成发布文件：

```bash
npm run build
npm run preview
```

构建会生成课程页面、已配置的 PDF 和 VitePress 站点。`website/generated/`、`website/.vitepress/generated/`、`website/.vitepress/dist/` 与本地运行时不提交 Git。推送到 **master 主分支**后，GitHub Actions 构建并部署到 GitHub Pages；部署结果可在仓库 Actions 中查看。

## 新增与维护课程

1. 分配稳定的课程 ID，在 `courses/` 对应方向创建课程 README 与来源说明。
2. 在 `website/catalog-data/courses/<course-id>.yaml` 设置 `paths`、官方资料、讲次及作业入口；只接入资源时设置 `publishOutputs: false`。
3. 在 `website/course.yaml` 对应方向登记首页入口。历史版本使用独立 ID，并挂在主课程的版本入口下。
4. 需要生成笔记时按工作流准备证据、生成候选稿并审核，再显式登记 `outputs`。
5. 运行 `npm run validate:structure` 和 `npm run build`，检查课程页、资料检索与官方作业链接。

完整命令与安装说明见 [维护指南](workflow/README.md)，路径和内容约定见[项目结构规范](workflow/standards/project-structure.md)、[逐字稿规范](workflow/standards/transcript-generation.md)与 [AGENTS.md](AGENTS.md)。

## 目录迁移说明

2026 年 10 月按课程方向整理了实际源目录。旧的 `llm/`、`agent/`、`infra/`、`interest/`、`papers/` 已归并到 `courses/` 和 `references/`；网站的课程 ID、讲次 ID 和 URL 保持不变。旧路径到新路径的对照见[目录迁移表](workflow/standards/directory-migration-2026-10.md)。已有本地克隆请先保存自己的修改，再更新主分支；本地未跟踪的草稿、缓存和音视频需按迁移表自行归位。

## 来源与使用边界

课程资料和第三方项目的版权与许可证归各自作者。移动文件夹不改变其许可证；引用、运行和再分发仍遵循上游要求。本仓库主要提供官方资料链接和自行整理的学习内容。

模型服务配置放在本机 `.env`，示例见 [.env.example](.env.example)。密钥、Cookie、个人配置、下载的音视频和运行缓存不进入 Git。
