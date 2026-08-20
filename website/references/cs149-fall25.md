---
title: CS149 Fall 2025 自学工作台
description: 并行计算课程的先修要求、学习路径、作业替代项目与资料边界。
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

## 编程作业的自学替代

官方公开说明列出五项主题：ISPC、多任务图调度、CUDA renderer、AI 加速器上的 DNN 优化、以及最快 CUDA kernels。具体题目属于课程系统，因此本仓库不复制；可用以下替代项目保持学习闭环：

- ISPC 图像滤波/曼德勃罗集：比较串行、ISPC、线程版。
- Task graph executor：比较静态调度、共享队列与 work stealing。
- CUDA 2D renderer：用 profiler 分析 occupancy、coalescing 与 divergence。
- Matmul/attention 融合 kernel：建立 roofline 分析与正确性测试。
- 固定形状的 reduction、softmax 或 layer norm：以可复现实验表追逐性能上限。

完整的可编辑学习计划与实验记录模板保存在仓库的 `infra/cs149-fall25/references/study-plan.md`；本课程的逐讲公开资料可从[课程目录](/generated/courses/cs149-fall25/)进入。

## 资料边界

本课程页只索引公开的 Fall 2025 Slides 与 2023 公开视频。Canvas、Ed Discussion、课堂测验以及需要 Stanford 身份的作业材料不下载、不镜像；后续笔记会严格链接回每讲的官方来源。
