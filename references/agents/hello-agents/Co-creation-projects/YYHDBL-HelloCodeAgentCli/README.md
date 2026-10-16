# HelloAgents Code Agent CLI

<div align="center">

**面向本地代码仓库的智能 Code Agent 命令行工具**

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[特性](#-核心特性) • [架构](#-系统架构) • [快速开始](#-快速开始) • [使用指南](#-使用指南) • [开发](#-开发指南)

</div>

---

## 📝 项目简介

**HelloAgents Code Agent CLI** 是一个基于 HelloAgents 框架开发的智能代码助手，提供类似 Claude Code/Codex 的交互体验，专注于本地代码仓库的安全智能操作。

### 核心价值

- **🎯 精准检索**：按需探索代码库，先证据后结论，避免全库扫描
- **🛡️ 安全可控**：补丁式修改 + 原子写入 + 自动备份，危险修改需人工确认
- **🧠 智能推理**：基于 ReAct 范式，支持多步推理与行动
- **📊 任务管理**：内置 Todo 系统，可视化追踪多步骤任务进度
- **🔧 工具丰富**：集成终端、上下文获取、Note管理

### 适用场景

- ✅ 代码库探索与分析
- ✅ 智能代码修改与重构
- ✅ 局部功能修复与优化
- ✅ 项目结构理解
- ✅ 代码审查辅助
- ✅ 技术演示与教学

---

## ✨ 核心特性

### 1. 智能推理引擎

- **ReAct Agent**：结合推理（Reasoning）与行动（Acting），支持多步骤复杂任务
- **多步跟踪**：Todo Board 实时展示任务进度（pending → in_progress → completed）

### 2. 安全补丁系统

```
*** Begin Patch
Update File: src/example.py
```python
# 修改后的代码
```
*** End Patch
```

- ✅ 标准化补丁格式
- ✅ 原子化文件操作
- ✅ 自动备份（.backup 后缀）
- ✅ 白名单文件类型控制
- ✅ 人工确认机制

### 3. 多源上下文构建

**GSSC 流水线**（Gather-Select-Structure-Compress）：

```
用户查询 → 收集信息 → 相关性筛选 → 结构化组织 → Token 压缩 → 生成回复
```


### 4. 工具生态

| 工具类型 | 功能描述 | 主要用途 |
|---------|---------|---------|
| **Terminal Tool** | 安全终端执行（白名单命令） | 文件浏览、搜索、文本处理 |
| **Context Fetch Tool** | 按需代码检索 | 读取特定文件/目录内容 |
| **Note Tool** | 笔记增删改查 | 记录重要信息、决策点 |
| **Todo Tool** | 任务管理 | 多步任务跟踪、进度可视化 |
| **Plan Tool** | 规划生成 | 复杂任务分解与执行计划 |
| **Memory Tool** | 记忆管理 | 长期知识存储与检索 |



## 🏗️ 系统架构

### 整体架构图
┌─────────────────────────────────────────────────────────────┐
│                     用户交互层 (CLI)                          │
│                   hello_code_cli.py                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   智能体层 (Agents)                           │
│  ┌─────────────┐  ┌─────────────┐                           │
│  │ ReActAgent  │  │ PlanAgent   │                           │
│  └─────────────┘  └─────────────┘                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    核心层 (Core)                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   LLM    │  │ Message  │  │  Config  │  │ Exception│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   能力层 (Capabilities)                       │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  Context Builder │  │  Memory Manager │                  │
│  │   (GSSC流水线)   │  │   (多层记忆)    │                  │
│  └─────────────────┘  └─────────────────┘                  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    工具层 (Tools)                             │
│  Terminal │ ContextFetch │ Note │ Todo │ Plan │ Memory │... │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   执行器层 (Executors)                        │
│  ApplyPatchExecutor - 安全补丁应用与文件操作                  │
└─────────────────────────────────────────────────────────────┘
```


```

### 核心模块说明

#### 1. Agents 层
- **ReActAgent**：主引擎，循环执行"思考→行动→观察"
- **PlanSolveAgent**：规划式任务分解
- **ReflectionAgent**：自我反思与优化
- **SimpleAgent**：基础对话型 Agent

#### 2. Core 层
- **HelloAgentsLLM**：统一 LLM 接口，支持 OpenAI/DeepSeek/Qwen 等
- **Message**：消息抽象与序列化
- **Config**：配置管理
- **Exceptions**：异常体系

#### 3. Context 层
- **ContextBuilder**：GSSC 流水线实现
- **ContextConfig**：上下文构建配置
- **ContextPacket**：信息包抽象

#### 4. Memory 层
- **MemoryManager**：统一记忆管理接口
- **Types**：WorkingMemory, EpisodicMemory, SemanticMemory, PerceptualMemory


#### 5. Tools 层
- **ToolRegistry**：工具注册与管理
- **Builtin Tools**：内置工具集
- **Base**：工具基类与参数定义

#### 6. Executors 层
- **ApplyPatchExecutor**：补丁解析与安全应用

---

## 🚀 快速开始

### 环境要求

- **Python**：3.10 或更高版本
- **操作系统**：macOS / Linux / Windows


### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd YYHDBL-HelloCodeAgentCli
```

#### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

创建 `.env` 文件：

```bash
# LLM 配置（必需）
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
```

#### 5. 运行 CLI

```bash
# 在当前目录启动
python -m code_agent.hello_code_cli --repo .

# 指定其他代码库
python -m code_agent.hello_code_cli --repo /path/to/your/project
```

---

## 📖 使用指南

### 基础用法

启动后进入交互式命令行：

```
🚀 HelloAgents Code Agent CLI
📂 Repo: /path/to/project
💡 输入 'help' 查看帮助，'exit' 退出

👤 > 帮我分析 src/main.py 的入口函数

🤖 Thought: 需要先获取文件内容
   Action: context_fetch[path=src/main.py]
   Observation: [文件内容]
   
   Thought: 已获取内容，开始分析
   Action: Finish[分析结果...]
```

### 项目演示

视频演示：https://www.bilibili.com/video/BV1UzBpBBE75/?vd_source=b0893117eda5f3e931a05d426f9789ed

图片演示：

![image-20251222163957228](/Users/yyhdbl/Library/Application Support/typora-user-images/image-20251222163957228.png)



### 命令行参数

```bash
python -m code_agent.hello_code_cli [OPTIONS]

选项：
  --repo PATH              代码库路径（默认：当前目录）
  --model TEXT             LLM 模型名称
  --api-key TEXT           API 密钥
  --base-url TEXT          API 基础 URL
  --max-steps INTEGER      最大推理步数（默认：15）
  --enable-memory          启用记忆系统
  --enable-rag             启用 RAG 检索
  --debug                  调试模式
  --help                   显示帮助信息
```

---

## 📂 项目结构

```
YYHDBL-HelloCodeAgentCli/
├── agents/                      # 智能体实现
│   ├── react_agent.py          # ReAct 范式
│   ├── plan_solve_agent.py     # 规划式 Agent
│   ├── reflection_agent.py     # 反思式 Agent
│   └── simple_agent.py         # 简单对话 Agent
│
├── code_agent/                  # 主应用
│   ├── hello_code_cli.py       # CLI 入口
│   ├── agentic/                # Code Agent 实现
│   │   └── code_agent.py
│   ├── executors/              # 执行器
│   │   └── apply_patch_executor.py
│   └── prompts/                # 提示词模板
│       ├── system.md
│       ├── react.md
│       ├── plan.md
│       └── tools.md
│
├── core/                        # 核心模块
│   ├── agent.py                # Agent 基类
│   ├── llm.py                  # LLM 接口
│   ├── message.py              # 消息抽象
│   ├── config.py               # 配置管理
│   └── exceptions.py           # 异常定义
│
├── context/                     # 上下文构建
│   └── builder.py              # GSSC 流水线
│
├── memory/                      # 记忆系统
│   ├── manager.py              # 记忆管理器
│   ├── base.py                 # 基础定义
│   ├── embedding.py            # 嵌入模型
│   ├── types/                  # 记忆类型
│   │   ├── working.py
│   │   ├── episodic.py
│   │   ├── semantic.py
│   │   └── perceptual.py
│   ├── storage/                # 存储后端
│   │   ├── document_store.py
│   │   ├── qdrant_store.py
│   │   └── neo4j_store.py
│   └── rag/                    # RAG 系统
│       ├── document.py
│       └── pipeline.py
│
├── tools/                       # 工具系统
│   ├── base.py                 # 工具基类
│   ├── registry.py             # 工具注册表
│   ├── chain.py                # 工具链
│   ├── async_executor.py      # 异步执行
│   └── builtin/                # 内置工具
│       ├── terminal_tool.py
│       ├── context_fetch_tool.py
│       ├── note_tool.py
│       ├── todo_tool.py
│       ├── plan_tool.py
│       ├── memory_tool.py
│       └── ...
│
├── utils/                       # 工具函数
│   ├── cli_ui.py               # CLI 界面
│   ├── helpers.py              # 辅助函数
│   ├── logging.py              # 日志配置
│   └── serialization.py        # 序列化工具
---

```

## 🔮 未来规划

### 近期计划

- [ ] **会话恢复**：支持断点续传，自动恢复摘要
- [ ] **细分终端命令工具**：将Terminal Tool拆分为原子性的命令工具
- [ ] **改写Note Tool**：
- [ ] **改写记忆系统**：


## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 👥 作者与致谢

### 核心贡献者

- **YYHDBL** - *项目维护者*

### 特别鸣谢

- **Datawhale 社区**：提供学习资源与支持
- **Hello-Agents 项目**：提供框架基础
- **OpenAI & DeepSeek**：LLM 技术支持

---



<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by HelloAgents Community

</div>
