# Code Agent（HelloAgents CLI）

这是一个基于 **HelloAgents** 组件（`HelloAgentsLLM` / `ContextBuilder` / `ReActAgent` / `TerminalTool` / `NoteTool` / `MemoryTool`）搭建的简易 Code Agent CLI，目标体验类似 Claude Code/Codex：支持多轮对话、按需探索代码库、生成补丁并在确认后落盘。

## 快速开始

1) 准备依赖与环境变量（建议用 `.env`，不要提交）：

- 依赖：安装根目录的 `requirements-mvp.txt`
- 在仓库根目录创建 `.env`（参考 `.env.example`），至少包含：
  - `DEEPSEEK_API_KEY=...`（或其他 OpenAI 兼容 provider 的 key）
  - 可选：`LLM_MODEL_ID=deepseek-chat`、`LLM_BASE_URL=https://api.deepseek.com`

2) 启动 CLI（工作区默认 `.`）：

```bash
python3 -m code_agent.hello_code_cli --repo .
```

命令：
- `:quit` 退出
- `:plan <目标>` 强制生成计划（平时由模型按需调用 `plan[...]` 工具）

## 已实现功能（当前版本）

- 多轮对话：基于 `SimpleAgent`，保留近期对话历史。
- 智能体范式：核心使用 `ReActAgent`（推理 + 工具调用），规划能力作为可选工具 `plan[...]`。
- 上下文工程：使用 `ContextBuilder`（GSSC）融合系统指令、对话历史、笔记检索结果、情景记忆（episodic）等，控制上下文预算。
- 按需探索（更像 Claude Code）：
  - 默认不做全仓扫描；模型只有在需要证据时才会调用 `TerminalTool`（优先 `ls/rg/sed/cat` 小范围命令）。
- 工具能力：
  - `TerminalTool`：用于查看/检索（`rg/grep/find/cat/head/tail/sed` 等），并强化了安全限制：
    - 默认允许 shell 语义（管道等，体验更像 Claude Code）
    - 重定向/子命令替换/危险命令会要求用户确认（`allow_dangerous=true` + 交互确认）
    - `git` 默认仅允许 `status/diff`；`git reset --hard` 需要显式放行
    - `rm/chmod` 等高风险命令默认拒绝（需显式确认后放行）
  - `NoteTool`：在 `<repo>/.helloagents/notes/` 下写入结构化笔记（用于记录决策/阻塞/行动）。
- `MemoryTool`：仅启用 `episodic`（SQLite 持久化），默认存储在 `<repo>/.helloagents/memory/`。
- 补丁落盘（B 路线）：
  - 模型可在回复中输出 `*** Begin Patch ... *** End Patch` 格式补丁。
  - CLI 检测到补丁后会执行应用流程；对于高风险补丁（如 `*** Delete File:` 或大规模变更）会二次询问 `y/n`。
  - 落盘通过 `code_agent/executors/apply_patch_executor.py`：原子写、备份、冲突检测、规模限制。

## 约束与已知限制

- 目前“敏感操作确认”优先覆盖：`Delete File`、`git reset --hard`、`rm/chmod`、大规模变更；更细粒度策略后续可扩展。
- `TerminalTool` 仍是“字符串命令”入口，但执行为 argv-only，并在工具内拦截 shell 语义；更严格的参数级白名单可继续收紧。
- 存储布局默认使用 `<repo>/.helloagents/`（notes/memory/sessions/logs），可用环境变量覆盖：
  - `HELLOAGENTS_DIR=.helloagents`
  - `CODE_AGENT_MAX_STEPS=8`

## 相关文件

- CLI 入口：`code_agent/hello_code_cli.py`
- 主逻辑/上下文工程：`code_agent/agentic/code_agent.py`
- 补丁执行器：`code_agent/executors/apply_patch_executor.py`
- 上下文工程文档：`docs/第九章 上下文工程.md`
