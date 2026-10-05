---
title: CS149 Fall 2025 自学工作台
description: 并行计算课程的先修要求、学习路径、官方编程作业与资料边界。
outline: [2, 3]
---

# CS149 Fall 2025 自学工作台

[课程主页](https://gfxcourses.stanford.edu/cs149/fall25/courseinfo) · [18 讲 Slides](https://gfxcourses.stanford.edu/cs149/fall25/lecture/) · [2023 公开视频](https://www.youtube.com/playlist?list=PLoROMvodv4rMp7MTFr4hQsDEcX7Bx6Odp)

CS149 的价值在于它把“并行代码能跑”提升为“理解为什么会快、为什么还不够快，以及怎样保持正确”。课程覆盖 CPU/GPU、数据并行、AI 加速器与并发控制，是理解 LLM 训练/推理系统底层性能的扎实起点。

## 开始前

官方建议具备操作系统背景，并熟悉：机器指令与寄存器/内存状态、内存层级、C/C++ 调试、线程创建，以及快速学习 CUDA/ISPC 这类 C 风格语言的能力。若这些基础薄弱，先补齐 C++ 调试和线程基础，再进入 L01。

## 学习路线

| 阶段 | Lecture | 要解决的问题 |
| --- | --- | --- |
| 并行思维与 CPU | L01–L04 | 如何划分工作、理解 SIMD/多线程，并将串行代码改写为并行代码？ |
| 性能工程 | L05–L08 | 如何安排工作、降低通信和访存代价，并使用 map/reduce/scan 等数据并行原语？ |
| GPU 与 AI 系统 | L09–L13 | 如何将 DNN/Transformer 放到 GPU、专用加速器和数据中心？ |
| 并发正确性 | L14–L18 | 缓存一致性、内存模型、锁、无锁算法和事务内存怎样影响正确性与性能？ |

每讲按“Slides → 一个最小实现 → 性能预测 → 测量/解释 → 复盘”的顺序完成。课程目录中的每个 Lecture 已有公开 PDF 的稳定入口；笔记生成后会出现在同一个位置。

## 官方编程作业

[Fall 2025 课程主页](https://gfxcourses.stanford.edu/cs149/fall25/)公布了以下五个作业仓库。题目、起始代码和环境要求以各仓库说明为准。

| 作业 | 官方 GitHub |
| --- | --- |
| 1 · 多核 CPU 性能分析 | [stanford-cs149/asst1](https://github.com/stanford-cs149/asst1) |
| 2 · 多核任务图调度 | [stanford-cs149/asst2](https://github.com/stanford-cs149/asst2) |
| 3 · CUDA Circle Renderer | [stanford-cs149/asst3](https://github.com/stanford-cs149/asst3) |
| 4 · Trainium2 Conv + MaxPool | [stanford-cs149/asst4-trainium2](https://github.com/stanford-cs149/asst4-trainium2) |
| 5 · CUDA Kernels 优化 | [stanford-cs149/asst5-kernels](https://github.com/stanford-cs149/asst5-kernels) |

完整的可编辑学习计划与实验记录模板保存在仓库的 `infra/cs149-fall25/references/study-plan.md`；本课程的逐讲公开资料可从[课程目录](/generated/courses/cs149-fall25/)进入。

## 资料边界

本课程页索引公开的 Fall 2025 Slides、官方作业仓库与 2023 公开视频。Canvas、Ed Discussion、课堂测验及需要 Stanford 身份的材料保留原站入口；后续笔记链接回对应的官方来源。
