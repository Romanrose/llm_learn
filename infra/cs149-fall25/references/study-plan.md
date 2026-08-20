# CS149 自学路径与作业替代项目

本计划以 Fall 2025 的公开 Slides 为准。官方页面说明共有五个编程作业和四个书面作业；具体题目通过课程系统发放，因此这里仅记录课程公开的任务主题，并给出可独立完成的等价练习。

## 四个学习模块

| 模块 | Lecture | 核心问题 | 最小可交付物 |
| --- | --- | --- | --- |
| 并行思维与 CPU | L01–L04 | 如何分解工作，并把 SIMD/线程抽象映射到处理器？ | ISPC 向量化小实验与 speedup 分析 |
| 性能工程 | L05–L08 | 怎样平衡负载、压缩通信，并用数据并行原语重写算法？ | work/span、cache/带宽与调度实验记录 |
| GPU 与 AI 系统 | L09–L13 | 怎样把 DNN/Transformer 映射到 GPU、加速器和数据中心？ | CUDA kernel 或 Triton kernel 的 profiling 报告 |
| 一致性与同步 | L14–L18 | 多线程如何保持正确性，并避免同步成为性能瓶颈？ | 锁与无锁数据结构对比、竞态复现与修复 |

## 五个编程作业的公开主题

| 官方作业 | 公开主题 | 自学替代实现 |
| --- | --- | --- |
| Assignment 1 | 用 ISPC 在多核 CPU 上编程 | 为 image blur、SAXPY 或 Mandelbrot 写串行、ISPC 与线程版；记录不同任务粒度下的 speedup。 |
| Assignment 2 | 调度 task graph | 实现有向无环图执行器，比较静态分配、共享队列与 work stealing 的 makespan。 |
| Assignment 3 | 用 CUDA 编写 renderer | 写一个 tile-based 2D renderer 或 Mandelbrot renderer；用 Nsight Compute 解释 occupancy、memory coalescing 和分支发散。 |
| Assignment 4 | 在 AI accelerator 上优化 DNN 计算 | 针对矩阵乘法、卷积或 attention 写融合 kernel，并用 roofline 分析确定瓶颈。 |
| Assignment 5 | 编写最快的 CUDA kernels | 选定固定形状的 reduction、softmax、GEMM 或 layer norm；建立正确性测试、基线与 benchmark 表。 |

## 每讲笔记模板

每完成一讲，在 `notes/lecture-NN/note.md` 记录以下内容：

1. 本讲的性能模型或正确性不变量。
2. 一个可以手算的例子，写出预测值与实测值。
3. 一个“失败尝试”：例如负载不均、非合并访问、false sharing 或数据竞争。
4. 与 LLM 系统的连接：训练、推理、通信或 kernel 优化中的对应场景。
5. 下一讲前需要复习的术语和一个未解决问题。

## 建议环境

- CPU：C++20、OpenMP 或 TBB；ISPC 用于 SIMD/SPMD 练习。
- GPU：CUDA Toolkit、Nsight Systems/Compute；没有 NVIDIA GPU 时先完成 CPU 与性能建模部分。
- 测量：固定输入规模、预热、重复运行、校验数值正确性；报告中同时记录硬件、编译器、参数与统计方式。

不要把一次 benchmark 当作结论。先提出瓶颈假设，再用 profiler 的证据验证或推翻它。
