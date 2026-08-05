# LLM 共学项目

一个面向大语言模型（LLM）理论、工程实现和智能体应用的学习共同体仓库。

这里不追求一个统一的“启动命令”，而是把课程、论文实现、Agent 教材和基础设施资料组织在一起，方便按学习阶段逐步深入，也方便成员通过笔记和代码互相复习、Review 和贡献。

## 学习路线

推荐按照“模型基础 → 核心机制 → Agent 应用 → 工程实践”的顺序学习：

1. **模型基础：** 使用 `cs336/` 学习如何从零构建语言模型。
2. **机制理解：** 使用 `papers/30-paper-zhCN/` 通过 Notebook 实现经典论文中的核心算法。
3. **Agent 应用：** 使用 `agent/hello-agents/` 学习 ReAct、RAG、MCP、多智能体和 Agentic RL。
4. **工程实践：** 参考 `infra/` 中的环境、远程开发和多服务器配置文档。

## 项目结构

```text
llm_learn/
├── agent/                  # Agent 学习资料与实践代码
│   ├── hello-agents/       # Datawhale《Hello Agents》教材及配套代码
│   ├── memory/             # 个人知识记忆
│   └── system/             # 系统配置
├── cs336/                  # Stanford CS336：从零构建语言模型
│   ├── lectures/           # 可执行讲义、课程代码和 Trace Viewer
│   ├── notes/              # 共学成员的个人笔记
│   └── references/         # 课程作业与参考实现
├── papers/                 # 论文阅读与教学实现
│   └── 30-paper-zhCN/      # Sutskever 推荐的 30 篇论文中文实现
└── infra/                  # 开发环境、远程连接和基础设施文档
```

## 快速开始

### CS336 课程

课程讲义和运行说明见 [`cs336/lectures/README.md`](llm/cs336/lectures/README.md)。例如：

```bash
cd cs336/lectures
pip install -r requirements.txt
python execute.py -m lecture_01
```

执行讲义后，可以使用 Trace Viewer 查看生成的运行轨迹；具体命令和远程 Slurm 运行方式请参考课程目录中的 README。

### 经典论文实现

`papers/30-paper-zhCN/` 包含 30 篇论文的教学 Notebook，覆盖 RNN/LSTM、CNN、Transformer、VAE、Scaling Law、RAG 等主题。该子项目使用独立的 `uv` 环境：

```bash
cd papers/30-paper-zhCN
uv sync
uv run jupyter notebook
```

### Agent 学习

`agent/hello-agents/` 是从基础理论到综合项目的完整教程，在线阅读入口和章节导航见其 [README](agent/hello-agents/README.md)。配套代码位于该目录的 `code/` 下，建议边读边运行、修改和调试。

## 如何参与

1. Fork 本仓库，或在本地创建自己的工作分支。
2. 在 `cs336/notes/<你的名字>/` 下维护个人学习笔记。
3. 在 `papers/` 中提交论文解读、实验记录或演示材料。
4. 为代码补充注释、测试和运行说明。
5. 提交 Pull Request，与其他成员进行 Review。

## 贡献规范

- 笔记命名建议使用 `lecture<数字>.md` 或 `lecture<数字>.py`。
- 论文分享建议使用 `YYYY-MM-DD-论文简称.md` 命名。
- 新增代码应说明依赖、运行方式和预期结果。
- 请不要提交 API Key、密码、私钥、真实服务器地址等敏感信息。
- `.obsidian/` 是本机 Obsidian 的工作区、插件和主题配置，已加入 `.gitignore`，不应提交到远程仓库。

## 相关说明

- CS336、Hello Agents 和论文实现目录保留各自上游项目的说明与许可证，请以对应目录中的文档为准。
- 基础设施实践记录见 [`infra/SSH-Codex-多服务器配置实战.md`](SSH-Codex-多服务器配置实战.md)。
