# LLM 学习仓库

这是一个围绕大语言模型（LLM）的个人共学仓库：把课程讲义、逐字稿与笔记、论文复现、Agent 教材和开发环境资料放在同一个可持续维护的知识库中。

学习主线是：**模型基础 → 从零实现 → 论文机制 → Agent 应用 → 工程实践**。仓库不是单一程序，因此不提供统一的启动命令；请进入对应目录，按照该目录的说明运行。

## 从这里开始

1. 先阅读根目录的[学习与转写提示词手册](提示词.md)，了解课程笔记、视频逐字稿和转写流程的约定。
2. 学习 [CS336：Language Modeling from Scratch](llm/cs336/)，用课程讲义和作业建立训练语言模型的系统认识。
3. 在 [`llm/cs336/notes/`](llm/cs336/notes/) 中记录自己的课程笔记与逐字稿；当前已有 `ljy` 的笔记示例。
4. 结合 [`papers/30-paper-zhCN/`](papers/30-paper-zhCN/) 复现经典论文，随后进入 [`agent/hello-agents/`](agent/hello-agents/) 的 Agent 学习与实践。

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
│   └── cs336/                         # Stanford CS336 学习主目录
│       ├── lectures/                  # 课程讲义、可执行代码与 Trace Viewer
│       ├── notes/                     # 个人课程笔记与逐字稿
│       ├── references/                # 作业、参考实现与扩展材料
│       └── UPSTREAM-LECTURES.md       # 讲义来源与同步说明
├── papers/
│   └── 30-paper-zhCN/                 # 经典论文的中文教学实现
├── agent/
│   ├── hello-agents/                  # 《Hello Agents》教材与配套代码
│   ├── memory/                        # 学习过程中的记忆/知识资料
│   └── system/                        # Agent 系统配置资料
├── infra/                             # GPU、网络、远程开发与工具配置
├── xingqu/                            # 延伸阅读与兴趣主题
└── 提示词.md                           # 笔记、逐字稿、转写流程手册
```

## CS336 快速开始

课程入口和具体运行说明见 [`llm/cs336/lectures/README.md`](llm/cs336/lectures/README.md)。一个典型的本地运行方式如下：

```bash
cd llm/cs336/lectures
pip install -r requirements.txt
python execute.py -m lecture_01
```

讲义运行后可使用 Trace Viewer 查看执行轨迹。远程 Slurm、依赖和具体参数请以课程目录中的 README 为准。

课程笔记建议写入 `llm/cs336/notes/<你的名字>/`：

```text
llm/cs336/notes/<你的名字>/
├── lecture4.md             # 整理后的课程笔记
└── lecture4_transcript.md  # 阅读友好的完整逐字稿
```

视频转写采用“**优先使用字幕；没有字幕时，在得到账号/音频下载授权后使用本地 ASR**”的流程。转写规范、模型选择和 Markdown 公式写法请见[提示词手册](提示词.md)。本机的转写工具放在 `workflow/`，仅供本地使用，不提交到 GitHub。

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
- 个人 CS336 笔记放在 `llm/cs336/notes/<你的名字>/`，建议命名为 `lecture<数字>.md`；完整逐字稿追加 `_transcript.md`。
- 新增代码请说明依赖、运行命令和预期结果；论文笔记建议以 `YYYY-MM-DD-论文简称.md` 命名。
- 不提交 API Key、密码、私钥、真实服务器地址或未授权下载的内容。
- `.obsidian/`、`workflow/`、课程运行缓存和本地虚拟环境均为本地文件，不进入远程仓库。

## 资料来源

- CS336 的上游讲义、许可证与同步说明见 [`llm/cs336/UPSTREAM-LECTURES.md`](llm/cs336/UPSTREAM-LECTURES.md)。
- 各教材与论文实现保留其上游说明与许可证；使用和再分发时请遵循对应目录中的规则。
