---
title: "CS336 2026 · GPUs, TPUs · Lecture Note"
description: "从零构建语言模型，覆盖架构、GPU、并行训练、Scaling Laws、评估与数据。"
search: true
---



<CourseHeader eyebrow="CS336 2026 · Lecture 5" title="GPUs, TPUs" description="" status="字幕已准备" :details='[{"label":"日期","value":"Mon April 13"},{"label":"讲师","value":"Tatsu"},{"label":"官方资料","value":"1 项"},{"label":"内容产物","value":"3 项"}]' :links='[{"label":"课程主页","url":"https://cs336.stanford.edu/"},{"label":"官方视频","url":"https://www.youtube.com/playlist?list=PLoROMvodv4rMqXOcazWaTUHhq-yembLCV"},{"label":"官方讲义仓库","url":"https://github.com/stanford-cs336/lectures"},{"label":"课程视频","url":"https://www.youtube.com/watch?v=izZba4UA7iY"}]' />

<CourseTabs active="lecture-note" :items='[{"id":"overview","label":"课程资料","route":"/generated/courses/cs336-2026/lecture-05/"},{"id":"blog","label":"Blog 解读","route":"/generated/courses/cs336-2026/lecture-05/blog"},{"id":"transcript-zh","label":"中文逐字稿","route":"/generated/courses/cs336-2026/lecture-05/transcript-zh"},{"id":"lecture-note","label":"Lecture Note","route":"/generated/courses/cs336-2026/lecture-05/lecture-note"}]' />

<div class="source-note">本页由 <code>llm/cs336-2026/notes/lecture-05/note.md</code> 自动生成；原始笔记位置保持不变。</div>

# CS336 Lecture 5 · GPUs, TPUs — 中文 Lecture Note

> 本笔记基于 Stanford CS336 (2026) Lecture 5 编写，主题为 GPU 与 TPU 硬件模型、GPU 性能优化技巧及 FlashAttention 原理。目标读者为有编程基础、希望深入理解语言模型训练/推理底层硬件的学习者。

---

## 学习目标

完成本讲后，你应该能够：

1. 描述 GPU 的核心硬件结构（SM、内存层次、warp），并将其与 CPU 的设计哲学进行对比。
2. 解释 GPU 的 SIMT 执行模型及其对控制流（如 if 语句）的语义影响。
3. 列出六种提升 GPU 利用率的核心技巧，并说明各自解决的问题。
4. 理解 roofline 模型，并能解释"内存受限"与"计算受限"的划分。
5. 说明 FlashAttention 如何通过对注意力计算进行分块（tiling）、重计算（recomputation）与算子融合，实现高效的内存利用。
6. 理解低精度计算（如 FP8、MXFP8）在现代 GPU 中的实现方式与权衡。

---

## 课程主线

本讲分为三个部分：

- **第一部分：GPU 硬件与编程模型** — 建立 GPU 的思维模型（CPU 对比、SM、内存层次、SIMT、TPU 映射）。
- **第二部分：六个 GPU 加速技巧** — 从控制流发散到低精度、算子融合、重计算、合并内存访问和分块。
- **第三部分：FlashAttention 复盘** — 将前述技巧综合应用于注意力机制，实现内存高效的注意力计算。

最终目标：理解课程开篇展示的矩阵乘法吞吐量曲线图——为何在特定矩阵维度下性能出现周期性暴跌，以及如何通过调整参数（如 padding）规避这些问题。

---

## 核心概念

### 1. GPU 硬件模型

- **CPU vs GPU**：CPU 面向低延迟、复杂控制流，拥有少数 ALU 与大型控制单元；GPU 面向高吞吐量，拥有大量轻量级计算核心（SM），单个任务延迟高，但总吞吐量极大。
- **SM（Streaming Multiprocessor）**：GPU 的基本计算单元，类似于"核心"。A100 有 128 个 SM。每个 SM 包含流处理器（SP），可并行执行线程。
- **内存层次**：
  - 寄存器（最快、最本地化）
  - 共享内存（SM 内，可编程，近 L1 缓存）
  - L1/L2 缓存（硬件管理）
  - 全局内存 / HBM（DRAM，容量大，速度慢）
  - 常量内存、主机内存（CPU 侧，可卸载）

关键点：**全局内存访问比 L1/共享内存慢约 10 倍**（A100 实测）。因此，所有优化策略的核心都是：尽可能把数据留在靠近计算单元的内存层级。

### 2. GPU 编程模型

- **线程（Thread）**：轻量级执行单元，遵循 **SIMT（单指令多线程）** 模型——同一 warp 中所有线程执行相同指令，但输入数据不同。
- **Block**：一组线程，保证被调度到同一个 SM 上，可访问共享内存。
- **Warp**：GPU 的调度单元，32 个连续编号线程构成一个 warp。调度器以 warp 为单位分发指令。

**控制发散（Divergence）**：在 SIMT 下，if/else 的两个分支都会被所有线程执行，不满足条件的线程被屏蔽（空转）。因此，GPU 代码中应尽量避免分支，改用掩码/乘法实现条件逻辑（如 ReLU）。

> 注：一个 block 中的 warp 数量因硬件而异，没有固定值。

### 3. TPU 与 GPU 的趋同演化

- TPU 在高层结构上与 GPU 高度相似：均有矩阵乘法单元（GPU：Tensor Core；TPU：MXU）、并行向量单元和内存层次（HBM + 共享内存 SMEM）。
- 主要差异在规模与灵活性：
  - GPU：大量（约 528）小矩阵乘法单元，灵活性高
  - TPU：少量（约 2~8）大矩阵乘法单元，锁死在大矩阵乘法上
- 命名陷阱：TPU 的"张量核心"指处理器单元；GPU 的"Tensor Core"指矩阵乘法电路。

### 4. Roofline 模型与操作强度

- **Roofline 模型**：横轴为操作强度（每字节内存移动对应的 FLOPs），纵轴为可达吞吐量。
- 曲线分为上升段（**内存受限**）和平坦段（**计算受限**）。训练/推理时应处于平坦段——即计算单元已饱和。
- **操作强度（Arithmetic Intensity）** = FLOPs / Bytes moved。提高操作强度是优化的核心方向（例：ReLU 在 FP32 下为 1 FLOP / 8 bytes，操作强度极低）。

---

## 六个 GPU 加速技巧

### 技巧 1：控制流最小化（避免发散）

- 原因：if/else 分支在 SIMT 下两个分支都执行，空转等待。
- 实践：用掩码乘法替代分支（如 ReLU 使用 `x * (x > 0)`）。

### 技巧 2：低精度计算（Low Precision）

- 动机：降低每个操作的数据字节数，缓解内存带宽压力；同时张量核心在低位宽下吞吐量大幅提升。
- 原理：矩阵乘法中，输入以低精度（如 BF16）送入，乘积以全精度（FP32）累加，输出转回 FP32。
- 挑战：不同算子对精度敏感度不同（如 softmax、exp 常需 FP32）；低位宽易上溢/下溢，需要缩放因子。
- **MXFP8**：分块量化，每 32 个元素共享一个 E8M0 缩放因子。代价是转置/量化操作复杂——实践中需为每个量化矩阵保留原始与转置两份拷贝。
- **FP4（MXFP4）**：仅 16 个值（-6 到 6），每 16 个元素一个 E4M3 缩放因子。已有训练尝试，但尚未成为主流。
- 结论：低精度可节省 20–30% 训练时间，但非免费——量化/反量化开销需权衡。第一层和最后一层通常最难量化（易导致训练不稳定）。

### 技巧 3：算子融合（Operator Fusion）

- 思想：将多个算子合并为一个 kernel，减少中间结果在全局内存中的读写次数。
- 例子：`sin²x + cos²x` 在 PyTorch 中产生 5 个中间操作。融合后只读一次全局内存、写一次结果。
- 工具：Torch Compiler / JAX Compiler 可自动完成简单融合；复杂融合（如 FlashAttention）需手动设计。

### 技巧 4：重计算（Recomputation）

- 思路：丢弃反向传播所需的中间激活值，在反向时重新计算。
- 收益：内存访问次数减少（8 次 → 5 次），计算量不变（或略增）。
- 适用场景：计算充裕但内存带宽紧张时（例如注意力得分矩阵的中间值）。

### 技巧 5：合并内存访问（Coalesced Access）

- 原理：DRAM 以突发（burst）模式工作——访问一个地址会一次性返回一个连续段的数据（约 128 字节），只要访问落在同一段内就是"免费"的。
- 要求：warp 中所有线程的读地址应落在同一个（或相邻）突发段内。
- 反例：行主序矩阵按列访问时，每个线程落在不同突发窗口，导致严重低效。
- 实践：尽量按行（连续地址）访问矩阵；无法满足时对矩阵进行 **padding**，使行对齐到突发边界。
- 案例：nanoGPT 将词表 50,257 → 50,304（对齐到 64 的倍数），获得约 25% 加速。

### 技巧 6：分块（Tiling）

- 思想：将数据切分为块（tile），加载到共享内存后反复使用，大幅减少全局内存访问次数。
- 效果：矩阵乘法中，无分块时每个输入元素从全局内存读取 N 次；分块大小 T 时减少到 N/T 次。
- 约束：分块大小须与矩阵维度、突发段边界、共享内存容量对齐；不整除时会出现"瘦长块"或波次量化问题。
- 自动化：PyTorch 的 `max-autotune` 编译器会尝试不同分块大小以找到最优。

#### 波次量化（Wave Quantization）

- 现象：举例 A100（108 SMs）上使用 256×128 分块，矩阵从 1792 增加到 1793 时，块数从 98 跳到 120，超过 SM 数，需两轮调度。第二轮只有 12 个块，大部分 SM 空闲，性能骤降。
- 启示：矩阵维度应尽量为 SM 数量的倍数（或其约数）。

---

## FlashAttention 解析：所有技巧的综合

注意力计算的核心操作：

1. `S = Q @ K^T`
2. `P = softmax(S)`
3. `O = P @ V`

朴素实现中，S（N×N）和 P（N×N）都要写入全局内存，内存复杂度为 O(N²)。

**FlashAttention 的两大关键手段**：

### ① 在线 Softmax（Online Softmax）

- 经典 softmax 需要先找最大值（求指数），再计算归一化，需要两遍扫描。
- 在线 softmax：边扫描边追踪 running max 和 running sum。
  - 遇到新最大值 m'，将已累加的 sum 按 `sum *= exp(m_old - m_new)` 修正，再累加 `exp(x - m_new)`。
- 效果：每个块（tile）可独立计算 softmax，无需等待全局最大值，从而实现**分块式注意力计算**。

### ② 分块 + 重计算

- 将 Q、K、V 切成块（例如 Q 块、K 块、V 块），逐块加载到共享内存。
- 计算每个 Q 块对所有 K 块的部分注意力，在线更新 running max/sum，并将结果以加权方式累加到输出块。
- 反向传播时**不保存**注意力得分矩阵（N×N），而是逐块重新计算——这就是重计算技巧的直接应用。
- 最终，全局内存访问量从 O(N²) 降到 O(N² / T)（T 为分块大小），实现内存高效。

### ③ 结果

- FlashAttention 实现了一个融合的、内存高效的注意力 kernel，显著提升训练/推理吞吐量，是大模型推理（长上下文）的关键优化之一。

---

## 关键公式

- 操作强度（Arithmetic Intensity）：
  \[
  \text{AI} = \frac{\text{FLOPs}}{\text{Bytes moved}}
  \]
- 无分块矩阵乘法全局内存读取次数（每个元素）：\( N \) 次
- 分块后（分块大小为 T）：\( N/T \) 次全局读取 + T 次共享内存读取
- 在线 softmax 修正：
  \[
  \ell_{\text{new}} = \ell_{\text{old}} \cdot e^{m_{\text{old}} - m_{\text{new}}} + \sum e^{x_i - m_{\text{new}}}
  \]
  （其中 \( \ell \) 为归一化累加和，\( m \) 为 running max）

---

## 课程作业关联

- 作业 1/2 中会涉及与 CUDA Mode / GPU 书中练习相似的矩阵乘法分块优化。
- FlashAttention 的分块与在线 softmax 部分将是作业中的核心编程任务。
- 建议先独立完成一个朴素矩阵乘法 kernel，再逐步加入分块、合并访问与 padding，观察吞吐量变化。

---

## 常见误区

1. **认为 GPU 只是"更多核心的 CPU"** — GPU 的调度单位是 warp，分支会导致隐式空转。
2. **忽略内存层次** — 全局内存访问的代价远高于 L1/共享内存，性能瓶颈常在内存而非计算。
3. **以为低精度是"免费的"** — 量化/反量化有额外开销，且第一/最后一层难以量化。
4. **分块大小越大越好** — 需要对齐突发段与 SM 数量；过大可能导致波次量化。
5. **FlashAttention 只是矩阵乘法的优化** — 其核心难点在于 softmax 的在线计算，这是注意力分块的前提。
6. **混淆 TPU 与 GPU 的"Tensor Core"** — 前者指处理器，后者指矩阵乘法单元。

---

## 复习清单

- [ ] 能画出 GPU 内存层次结构并列出各级延迟相对大小
- [ ] 解释 SIMT 模型：warp 内所有线程执行相同指令
- [ ] 描述共享内存（可编程）与 L1 缓存（自动）的区别
- [ ] 计算 ReLU 在 FP32 下的操作强度（1 FLOP / 8 bytes）
- [ ] 解释 MXFP8 的缩放因子机制及转置问题
- [ ] 给出一个算子融合的实例（如 sin²x + cos²x 的融合 kernel）
- [ ] 描述重计算如何减少内存访问次数（8 → 5 例子）
- [ ] 定义合并内存访问（Coalesced Access），并说明 DRAM 突发（burst）原理
- [ ] 解释分块的收益公式（N/T 次全局读取）及波次量化现象
- [ ] 推导在线 softmax 的更新公式
- [ ] 总结 FlashAttention 的完整流程：分块 → 在线 softmax → 重计算

---

## 总结

本讲的核心信息：**系统性能的关键不在计算而在数据移动**。现代 GPU 算力增长远超内存带宽增长，因此所有优化策略都围绕"减少全局内存访问、提高数据复用"展开。六个技巧（控制流最小化、低精度、算子融合、重计算、合并访问、分块）是这一原则的具体体现。最后，FlashAttention 正是这一原则的集大成者——通过分块、在线 softmax 与重计算，将注意力从 O(N²) 内存访问降低到接近 O(N)，成为大模型训练与推理不可或缺的基石。
