# TutorAgent

> 一个基于多智能体协作的智能编程导师系统，支持学习路径规划、RAG 出题、代码评审与学习记忆回顾。

---

## 📝 项目简介

**TutorAgent** 是一个基于 LLM 与多智能体（Agent-to-Agent, A2A）协作架构的智能编程导师系统，旨在模拟“真人导师”的教学流程，为用户提供**可持续、可回顾、可演进**的编程学习体验。
## 📌 项目来源说明

本项目基于@chen070808的毕业设计进行二次开发，

---

## ✨ 核心功能

- [x] **学习路径规划（PlannerAgent）**  
  根据用户目标与当前水平，自动生成结构化学习计划（Markdown），并支持阶段进度动态更新。

- [x] **智能出题（ExerciseAgent + RAG）**  
  基于 RAG 技术从题库中检索与当前学习阶段和难度匹配的编程题目。

- [x] **代码评审与反馈（CodeReview-Agent）**  
  对用户提交的代码进行自动化分析与执行测试，生成覆盖正确性、代码风格与复杂度的专业反馈。

- [x] **学习记忆与回顾（Memory + NoteTool）**  
  对学习行为、阶段进展与关键知识点进行持久化记录，支持跨会话的学习状态维护与自然语言回顾查询。

---

## 🛠️ 技术栈

- **框架**
  - HelloAgents（Agent 框架）

- **核心技术**
  - LLM（OpenAI / 本地模型）
  - RAG（检索增强生成）
  - 长短期 Memory 机制
  - 结构化 Markdown 笔记（NoteTool）

- **语言与依赖**
  - Python 3.10+
  - dotenv / pydantic / requests 等

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 已配置可用的 LLM API Key（或本地模型）

# 创建环境变量文件
cp .env.example .env

# 在 .env 中填写你的 LLM API Key
python main.py

用户输入：
我想学习 Python 的列表推导式

系统行为：
- PlannerAgent 生成学习计划并保存为学习笔记
- Memory 记录学习目标
- 后续可通过“我想回顾学习目标”进行回顾
用户输入：
我想要更新学习计划

系统行为：
- 自动更新学习计划进度
- 将对应阶段标记为已完成 [x]

## 🙏 致谢

感谢Datawhale社区和Hello-Agents项目！
感谢@chen070808