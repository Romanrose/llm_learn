---
title: 智能体与 Agent
description: Agent 课程、架构、记忆、工具使用与工程实践
---

# 智能体与 Agent

本区收录 Agent 课程、教材、专题笔记和可运行教程。

## CMU 11-768 · AI Agents（Fall 2026）

[进入课程工作台](/generated/courses/cmu-11768-fall26/) · [课程参考资料](/generated/courses/cmu-11768-fall26/references/) · [官方课程](https://www.cmu-agents.com/)

Graham Neubig 与 Daniel Fried 开设的研究生课程，从 Agent 运行框架、工具使用、上下文、Skills 与记忆出发，延伸到编码、计算机使用、深度研究、SFT / RL 训练、安全和交互。

截至 2026 年 10 月 3 日，已登记 23 次教学讲座、12 份官方 Slides、9 个录像链接、前两次作业仓库，以及逐讲阅读资料。假期、项目答疑和期末展示不计入讲次数；尚未发布资料的讲次保留计划状态。前 12 讲 Note、Blog 与前 9 讲中英文逐字稿已由用户审核并开放；逐字稿参照 CS336 2026 按完整语义段合并。

## Hello Agents

位于 `agent/hello-agents/`，覆盖 Agent 基础、ReAct、RAG、MCP、多智能体、Context Engineering 与 Agentic RL。

建议先建立基本范式，再进入 Memory 和长时程任务。

## Agent Memory

位于 `agent/memory/`，重点讨论记忆分层、事实提取、混合召回、上下文预算和生产系统中的降级策略。

## TencentDB Agent Memory

位于 `agent/tencentdb-agent-memory-tutorial/`，包含四个渐进式 Demo 和 Tiny Memory 教学实现。后续会并入统一 Course 页面，保留教程内部的章节顺序。

## 推荐顺序

1. Hello Agents 基础章节
2. ReAct、工具使用与 RAG
3. Agent Memory 四层模型
4. Tiny Memory 渐进式实现
5. Agentic Evaluation 与生产化
