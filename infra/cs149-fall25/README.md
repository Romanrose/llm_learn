# Stanford CS149 · Parallel Computing（Fall 2025）

这是 Stanford CS149 Fall 2025 的自学入口。课程从多核 CPU、SIMD 和 GPU 的编程模型出发，延伸到调度、数据并行、AI 加速器、缓存一致性与无锁同步；适合作为理解 GPU 性能和并行训练系统的底层课程。

课程主页与逐讲 Slides 已在 [`website/catalog-data/courses/cs149-fall25.yaml`](../../website/catalog-data/courses/cs149-fall25.yaml) 统一登记；构建网站后可从课程页逐讲访问。学习安排、作业范围和产出规范见 [`references/study-plan.md`](references/study-plan.md)。

## 学习目标

- 能以 work、span、speedup、efficiency、arithmetic intensity 等指标分析并行程序，而不只看总耗时。
- 能解释 SIMD、线程、warp、block、内存层级、调度与同步如何共同决定实际性能。
- 能用 ISPC/C++ 线程/CUDA 逐步把串行问题转换为正确、可扩展的并行实现。
- 能把 CS149 的分析框架迁移到 Transformer 推理、GPU kernel 优化和 AI 加速器问题。

## 资料边界

- 已接入：Fall 2025 课程主页、18 讲公开 Slides，以及课程方公开提供的 2023 YouTube 视频播放列表。
- 未镜像：Canvas、Ed Discussion、测验及其他需要 Stanford 身份的受限资料。
- 本仓库只保存资料索引、学习笔记和自行完成的实现；官方 PDF 默认仅外链，避免不必要的镜像与许可证歧义。

## 推荐节奏

以 9 周、每周 2 讲的节奏完成。每讲顺序固定为：读 Slides → 手推或运行最小实验 → 写下性能预测 → 测量并解释偏差。完成每个模块后，再做对应的自学项目，而不是只累计阅读量。

```text
基础模型（L01–L04） → 性能工程（L05–L08） → AI 系统（L09–L13） → 并发正确性（L14–L18）
```

## 本地约定

- 正式笔记写入 `notes/lecture-NN/`；未开始的 Lecture 不创建空目录。
- 课程级实验、作业替代实现和扩展阅读放在 `references/`。
- 运行 `npm run course -- discover cs149-fall25` 可重新核对公开入口；已登记的 Slides 可在审核后用 `ingest` 写入清单，但不传 `--download` 时不会下载二进制文件。

上游来源、快照策略与更新方式见 [`UPSTREAM.md`](UPSTREAM.md)。
