# 智能编程导师 (Intelligent Programming Tutor)

一个基于 HelloAgents 框架的智能编程学习助手系统，提供个性化的编程学习体验。

## 功能特点

### 🎯 核心功能

- **学习路径规划**：根据学习目标和当前水平，制定个性化的学习计划
- **智能出题**：根据学习内容自动生成编程练习题
- **代码评审**：对提交的代码进行专业评审，提供改进建议和最佳实践指导

### 🤖 多智能体架构

本项目采用多智能体协同工作模式，包含以下智能体：

- **TutorAgent（导师）**：主协调智能体，负责理解用户需求并调用相应的子智能体
- **PlannerAgent（规划师）**：制定个性化学习计划和路径
- **ExerciseAgent（出题人）**：根据学习内容生成编程练习题
- **ReviewerAgent（评审员）**：评审代码并提供专业反馈，支持代码执行测试

## 项目结构

```
chen070808-ProgrammingTutor/
├── src/
│   ├── agents/          # 智能体定义
│   │   ├── tutor.py     # 主导师智能体
│   │   ├── planner.py   # 学习规划智能体
│   │   ├── exercise.py  # 出题智能体
│   │   └── reviewer.py  # 代码评审智能体
│   └── tools/           # 工具定义
│       ├── agent_tool.py    # A2A智能体工具包装
│       └── code_runner.py   # 代码执行工具
├── main.ipynb           # 示例演示 Notebook
├── requirements.txt     # 项目依赖
└── .env                 # 环境配置（需自行创建）
```

## 安装与配置

### 1. 环境要求

- Python 3.8+
- HelloAgents 框架

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件并配置以下参数：

```bash
# LLM 模型配置
LLM_MODEL_ID=Qwen/Qwen2.5-72B-Instruct
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api-inference.modelscope.cn/v1
LLM_TIMEOUT=60
```

参考 `.env.example` 文件了解完整配置选项。

## 使用方法

### 方式一：Jupyter Notebook

打开 `main.ipynb` 并按顺序运行各个单元格，体验完整的学习流程：

1. 学习路径规划
2. 获取编程练习题
3. 代码评审与反馈

### 方式二：Python 代码

```python
from hello_agents import HelloAgentsLLM
from src.agents.tutor import TutorAgent

# 初始化 LLM
llm = HelloAgentsLLM.from_env()

# 创建导师智能体
tutor = TutorAgent(llm)

# 示例 1：请求学习计划
response = tutor.run("我想学习 Python 中的列表推导式")
print(response)

# 示例 2：请求练习题
response = tutor.run("请给我出一道关于列表推导式的练习题")
print(response)

# 示例 3：代码评审
code = """
numbers = [1, 2, 3, 4, 5]
squares = []
for n in numbers:
    squares.append(n * n)
"""
response = tutor.run(f"请评审以下代码：{code}")
print(response)
```

## 技术架构

### 智能体协同机制

- 采用 **Agent-to-Agent (A2A)** 工具调用模式
- `TutorAgent` 通过工具接口调用子智能体：
  - `call_planner(query)` - 调用学习规划师
  - `call_exercise(query)` - 调用出题人
  - `call_reviewer(query)` - 调用代码评审员

### 代码执行能力

`ReviewerAgent` 集成了 `CodeRunner` 工具，可以：
- 安全执行用户提交的 Python 代码
- 捕获运行时错误和异常
- 基于执行结果提供更精准的反馈

## 示例场景

### 场景 1：学习路径规划

**用户输入**：
```
我想学习 Python 中的装饰器，但我只了解基础的函数定义
```

**系统响应**：
导师会调用 PlannerAgent，生成包含以下内容的学习计划：
- 前置知识检查
- 分阶段学习目标
- 推荐学习资源
- 实践项目建议

### 场景 2：获取练习题

**用户输入**：
```
请给我出一道关于装饰器的练习题
```

**系统响应**：
ExerciseAgent 会生成一道练习题，包含：
- 题目描述和要求
- 输入输出示例
- 难度级别
- 考察知识点

### 场景 3：代码评审

**用户输入**：
```python
@decorator
def greet(name):
    print(f"Hello, {name}")
```

**系统响应**：
ReviewerAgent 会：
1. 执行代码检查语法和运行时错误
2. 分析代码质量和最佳实践
3. 提供改进建议
4. 指出潜在问题

## 开发与扩展

### 添加新的智能体

1. 在 `src/agents/` 目录下创建新的智能体类
2. 继承 `SimpleAgent` 基类
3. 在 `TutorAgent` 中注册新智能体工具

### 自定义工具

1. 在 `src/tools/` 目录下创建新工具类
2. 继承 `Tool` 基类并实现 `run()` 方法
3. 将工具注入到相应的智能体中

## 注意事项

- 确保 `.env` 文件配置正确，特别是 API 密钥
- 代码执行功能默认启用沙箱模式，建议不要执行不可信代码
- LLM 调用需要网络连接，请确保网络畅通

## 贡献者

- chen070808

## 许可证

本项目遵循 MIT 许可证。

## 致谢

本项目基于 [HelloAgents](https://github.com/datawhalechina/hello-agents) 框架开发。
