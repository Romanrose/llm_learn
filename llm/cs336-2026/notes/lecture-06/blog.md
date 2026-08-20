# 从 PyTorch 到 Triton：理解 GPU 内核编写的核心思维

## 导语

当我们在 PyTorch 中写下 `x @ y` 或 `torch.softmax(x, dim=-1)` 时，我们很少会思考底层到底发生了什么。但真正需要榨取性能时，你就必须直面 GPU 的硬件现实。本文是斯坦福 CS336《Language Modeling from Scratch》第六讲的完整梳理，将带你从硬件架构出发，逐步走到 Triton 内核的编写实践。

上一讲我们建立了 GPU 性能的宏观认知，这一讲则深入代码层面。我们会看到：为什么简单的 PyTorch 表达式可能性能糟糕？为什么需要理解 warp、共享内存和存储体冲突？以及如何用 Triton 编写 GeLU、Softmax 和矩阵乘法内核。最终，这些知识将直接服务于你实现 Flash Attention 和优化 Transformer 训练的目标。

---

## 一、GPU 硬件回顾：容量与带宽的权衡

让我们从一张典型的 NVIDIA GPU 简化示意图开始。课程将 A100、H100、B200 视为同一设计思路的不同代际：每张卡都有大约一两百个流式多处理器（Streaming Multiprocessors，SMs），代际变化更多体现在存储容量、带宽与具体硬件功能上。

- 每个 SM 内有寄存器，以及共享同一物理内存的 L1 缓存和共享内存。
- L2 缓存由整个芯片共享；高带宽内存（HBM）容量最大，并且跨代增长明显。
- 课程用 B200 作为例子：每个 SM 约有 65,000 个寄存器，合计约 256 KB。

这里的关键规律是：**容量与带宽大致负相关**。寄存器最快，随后是 L1、L2，HBM 在这条层级中最慢；优化时首先要避免不必要地往返较慢的存储层次。

## 二、编程模型：线程、线程块与网格

GPU 的编程模型可以用三层结构概括：

- **线程（Thread）**：在数据的一小部分上执行代码的最小单元。
- **线程块（Thread Block）**，也称为并发线程数组（Concurrent Thread Arrays，CTAs）：一组线程，它们可以访问同一块共享内存。
- **网格（Grid）**：所有线程块的集合。

当你启动一个内核时，实际上是启动了一个由线程和线程块组成的网格，让它们全部并行执行。

### 为什么需要线程块？

如果你只想做逐元素操作（比如 GeLU），每个线程处理一个元素就够了。但对于需要线程间通信的操作（如 softmax 或矩阵乘法），这种视图远远不够。原因在于：如果每个计算单元都直接读写 HBM，你会被内存带宽限制死死卡住。

正确的做法是使用共享内存（Shared Memory），它位于 SM 本地，存取速度远快于 HBM。一个线程块被调度到一个 SM 上执行，块内的所有线程共享这块快速内存。整个过程是：从 HBM 读取数据到共享内存，做计算（可能涉及线程间通信），再写回 HBM。

**Triton 的核心思想就是让你以线程块为单位思考**，而不是每个线程。

### 从第一张结构图到一次 Block 的执行

可以把 GPU 想象成一座工厂：CPU 负责下达任务，GPU 负责大量并行计算。GPU 内部有许多流式多处理器（Streaming Multiprocessors，SMs），每个 SM 都有自己的计算核心、寄存器和 shared memory；所有 SM 共享 GPU 的 global memory（显存）。SM 可以理解成一个能够独立工作的“车间”，但它不是 CPU 核心的简单放大版：一个 SM 会同时管理许多线程和多个线程块。

程序员通常不会只启动一个线程，而是启动一个由大量线程组成的 **Grid**。Grid 又被划分为许多 **Block**，每个 Block 由若干 **Thread** 组成：

```text
Grid：整个计算任务
└── Block：任务的一小块
    └── Thread：处理一个或几个元素
```

例如，对于向量加法 `c[i] = a[i] + b[i]`，如果有 8192 个元素、每个 Block 有 32 个线程，就需要 256 个 Block。一个 Block 内的线程可以合作并访问同一块 shared memory；不同 Block 之间通常不能直接通信，因此它们可以被 GPU 以任意顺序调度。

GPU 启动任务后，会把 Block 动态分配给 SM：

```text
Block 0 ──→ SM 0
Block 1 ──→ SM 1
Block 2 ──→ SM 0
```

一个 Block 必须整体放在一个 SM 上，不能拆到多个 SM，因为 Block 内的线程需要共享 shared memory，并且可能需要同步。如果 SM 资源（寄存器、shared memory 等）足够，一个 SM 可以同时容纳多个 Block；资源不足时，只能容纳较少的 Block。

Block 被放入 SM 后，硬件会把线程分成多个 **Warp**。一个 Warp 通常包含 32 个线程，因此 128 个线程的 Block 会被分成 4 个 Warp：

```text
Block 0
├── Warp 0：Thread 0–31
├── Warp 1：Thread 32–63
├── Warp 2：Thread 64–95
└── Warp 3：Thread 96–127
```

GPU 的指令调度基本以 Warp 为单位：同一 Warp 中的线程执行相同的指令，但处理不同的数据。以向量加法为例，每个线程根据自己的 Block ID 和 Thread ID 定位元素：

```python
i = block_id * threads_per_block + thread_id
c[i] = a[i] + b[i]
```

因此，一个 Block 的执行过程可以概括为：

```text
CPU 发起 kernel
→ GPU 创建 Grid
→ 调度器把 Block 分配给 SM
→ SM 把 Block 分成 Warp
→ Warp 中的线程读取数据、执行计算、写回结果
→ Block 完成后，SM 继续处理下一个 Block
```

这一过程解释了后面几个性能概念的来源：Block 是否能同时驻留在 SM 上，取决于资源使用量；Warp 中的线程是否访问连续地址，会影响内存合并；Warp 是否走不同分支，会产生控制发散。

## 三、编程模型与硬件的交互：那些决定性能的细节

编程模型本身很优雅，但性能对硬件极其敏感。以下是五个你必须理解的关键概念。

### 1. Warp 与控制发散

在硬件层面，线程块中的线程被分成 warp，每个 warp 有 32 个线程。一个 warp 内的所有线程必须以**锁步（lockstep）**方式执行同一条指令。如果遇到分支（if A else B），warp 只能先执行 A 路径，再执行 B 路径，这是串行化的，称为**控制发散（Control Divergence）**，应该尽量避免。

warp 的存在还有一个重要目的：**隐藏延迟**。当某个 warp 因为 HBM 读取而阻塞时（这可能需要 100 个周期），SM 可以零成本切换到另一个可执行的 warp。这正是 GPU 通过大量并发来掩盖内存延迟的设计哲学。

### 2. 占用率

每个线程最多使用 255 个寄存器，而每个 SM 的寄存器总数是固定的（如 B200 为 65,000）。因此，每个线程使用的寄存器越多，SM 能同时容纳的线程就越少，占用率（Occupancy）就越低。

但这不一定是坏事。课程中有一个具体例子：128 个线程的块，每个线程用 160 个寄存器，SM 最多只能同时运行 3 个块（12 个 warp），占用率仅为 18%。如果这是瓶颈，你可以通过**线程粗化（Thread Coarsening）**来调整——让每个线程处理多个元素，而不是一个。这样线程数减少，但每个线程做更多工作，可能反而更高效。

### 3. 存储体冲突

共享内存被划分为 32 个存储体（Banks），每个存储体 4 字节宽。每个周期，每个存储体最多只能被一个线程访问。如果多个线程试图访问同一个存储体的不同位置，访问就会被串行化，这就是**存储体冲突（Bank Conflicts）**。

最坏情况：32 个线程同时访问矩阵的第一列，就会造成 32 路存储体冲突。这在矩阵乘法中几乎是不可避免的（你必须访问行和列）。解决方案是 **swizzling**——重新排列共享内存的存储布局，使得冲突概率降低。

### 4. 内存合并

当 warp 中的 32 个线程访问 HBM 时，访问会被合并成 128 字节的事务（相当于一个缓存行）。如果所有线程访问连续内存（如第 1 行第 0 列、第 0 行第 1 列……），这就是完全合并，一次就能抓取全部数据。反之，访问列则会浪费大量带宽。

注意，这与存储体冲突很相似，但它们是两个不同的限制：一个涉及共享内存，一个涉及 HBM。

### 5. 线程块占用率与波次量化

线程块以波次（waves）调度到 SM 上。B200 有 148 个 SM，如果你启动 160 个线程块，第一波是 148 个，第二波只有 12 个，剩下大量 SM 空闲。这就是**波次量化问题（Wave Quantization）**。理想情况下，线程块的数量应该能整除 SM 的数量。

---

## 四、基准测试与性能分析：成功的方法论

课程反复强调一个成功公式：**对代码进行基准测试和性能分析，做出修改，然后再测试**。关键是，要在编写内核之前就测量代码，找出瓶颈在哪。

### 基准测试的基本功

课程用矩阵乘法演示了从零开始做基准测试的方法。有三个注意事项：

1. **预热（Warmup）**：一些操作是惰性编译的，第一次运行的时间不能代表稳定状态。
2. **多次计时**：考虑方差，通常取平均值。
3. **使用 CUDA 事件**而非 `time.time()`：CUDA 事件能提供更精确的 GPU 时间，并且需要同步（`torch.cuda.synchronize()`）确保所有异步操作完成。

一个有趣的观察是：当矩阵维度小于约 2000 时，时间几乎是常数；之后呈三次方增长。这是因为 GPU 是为大型矩阵乘法设计的，小矩阵无法充分利用硬件。

### 性能分析：看穿 PyTorch 的伪装

PyTorch 内置了性能分析器。当你分析 `a + b` 时，会看到一个名为 `kernel at CUDA functor add` 的内核——这告诉你，即使是最简单的加法，底层也是一个 CUDA 内核。

更有趣的是矩阵乘法：`a @ b`（2048×2048）会调用 `cutlass3x_sm100_simt_sgemm_f32_f32_64x64x16...`，而 128×128 的矩阵乘法调用的内核名却不同（`32x32x16`）。这些名字其实透露了实现细节：

- `cutlass` 是 NVIDIA 的线性代数 CUDA 库。
- `sm100` 对应 Blackwell 架构（B200）。
- `f32` 是数据类型。
- `64x64x16` 是分块（tile）的形状。

这意味着：**同样的 PyTorch 代码，不同维度会调用不同的底层内核**，而你根本无法直接控制这些选择。

---

## 五、GeLU 案例：内核融合的巨大威力

让我们将基准测试和性能分析应用到 GeLU 激活函数上。课程对比了三种实现：

1. **Naïve 实现**：直接用 PyTorch 公式写出 `0.5 * x * (1 + torch.tanh(0.79788456 * (x + 0.044715 * x^3)))`。
2. **内置实现**：`torch.nn.functional.gelu(x, approximate="tanh")`。
3. **编译实现**：对 naïve 版本调用 `torch.compile`。

基准测试中，naïve 实现明显慢于内置和编译版本。课程借此强调：即使数学表达式相同，kernel 数量与中间张量读写也会显著改变性能。

性能分析揭示了原因：

- **naïve 实现**调用了多个内核（加法、乘法、tanh 等），每个内核都从 HBM 读数据、算完写回，下一个内核再从 HBM 读。这就是**没有内核融合（No Kernel Fusion）**，导致大量 HBM 往返。
- **内置版本**是一个单独的 GeLU 内核，因为它太常用，所以有人专门写了一个融合内核放进标准库。
- **编译版本**（`torch.compile`）生成的也是一个单一的 Triton 内核——编译器自动识别出整个计算图，合并成一个融合操作。

**结论是明确的**：内核融合（Kernel Fusion）将多次 HBM 读写减少为一次读、一次写，这是性能提升的关键。

---

## 六、Triton 入门：以线程块为单位的思考

CUDA 的思维模型是“每个线程做什么”：你写一段代码，通过线程 ID 定位自己，然后执行操作。这给了你细粒度控制，但你得自己管理共享内存、同步等细节。

**Triton 的思维模型是“每个线程块做什么”**。你指定每个块要执行的计算，Triton 编译器负责把块映射到具体的 warp 和线程。对于本课程来说，Triton 已经足够强大。

Triton 代码看起来非常像 Python，但有三个关键差异：

1. **没有返回值，只有显式的读写**：你需要分配输出张量，内核往里写。
2. **指针运算**：输入输出是整数指针，你需要计算偏移量。
3. **块（Block）的概念**：每个块处理数据的一个片段。

### 第一个 Triton 内核：GeLU

```python
@triton.jit
def triton_gelu_kernel(x_ptr, y_ptr, num_elements, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(axis=0)      # 当前块 ID
    start = pid * BLOCK_SIZE         # 该块的起始位置
    offsets = start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < num_elements    # 处理边界

    x = tl.load(x_ptr + offsets, mask=mask)
    # 计算 GeLU 公式
    a = 0.79788456 * (x + 0.044715 * x * x * x)
    exp = tl.exp(2 * a)
    tanh = (exp - 1) / (exp + 1)
    y = 0.5 * x * (1 + tanh)

    tl.store(y_ptr + offsets, y, mask=mask)
```

流程很清晰：**醒来（获取 PID）→ 定位数据（计算偏移量）→ 读取（tl.load）→ 计算 → 写回（tl.store）**。

查看生成的 PTX（并行线程执行，GPU 的中间汇编）代码，你会发现：

- `ld.global.*` 和 `st.global.*` 是内存读写指令。
- 每个线程实际处理 8 个元素（**线程粗化**），编译器自动做了这个优化。
- `%ctaid.x` 是块索引，`%tid.x` 是线程索引——代码只编译一次，每个线程通过索引区分自己。

---

## 七、Softmax：归约操作与行列设计

Softmax 不再是逐元素操作，它需要对矩阵的每一行进行归约（计算最大值、求和）。这里的关键设计决策是：**让每一行成为一个线程块**。因为行与行之间不需要共享内存，块之间可以完全独立。

```python
@triton.jit
def triton_softmax_kernel(x_ptr, y_ptr, x_row_stride, y_row_stride, num_cols, BLOCK_SIZE: tl.constexpr):
    row_idx = tl.program_id(0)
    col_offsets = tl.arange(0, BLOCK_SIZE)

    x_ptrs = x_ptr + row_idx * x_row_stride + col_offsets
    x_row = tl.load(x_ptrs, mask=col_offsets < num_cols, other=float("-inf"))

    x_row = x_row - tl.max(x_row, axis=0)
    numerator = tl.exp(x_row)
    denominator = tl.sum(numerator, axis=0)
    y_row = numerator / denominator

    y_ptrs = y_ptr + row_idx * y_row_stride + col_offsets
    tl.store(y_ptrs, y_row, mask=col_offsets < num_cols)
```

这里有一个新元素：`tl.max` 和 `tl.sum` 在块内做归约。Triton 自动处理了线程间的通信，你不需要手动同步。

对比朴素 PyTorch 实现，Triton 版本大幅减少了 HBM 读写次数（从 5MN 次读取和 3MN 次写入降到 MN 读取和 MN 写入），这正是性能提升的核心。

---

## 八、行求和：当数据装不下一个块

当矩阵的行超过一个块能容纳的列数时（比如 4096 列，但块大小只有 1024），就需要一种新的策略。课程以行求和为例演示了这个问题。

核心思路是**循环遍历多个块片（Tiles）**：

```python
@triton.jit
def row_sum_kernel(x_ptr, out_ptr, N, BLOCK_SIZE: tl.constexpr):
    row = tl.program_id(0)
    acc = tl.zeros([BLOCK_SIZE], dtype=tl.float32)

    for start in range(0, N, BLOCK_SIZE):    # 遍历所有块片
        cols = start + tl.arange(0, BLOCK_SIZE)
        mask = cols < N
        x = tl.load(x_ptr + row * N + cols, mask=mask, other=0.0)
        acc += x

    result = tl.sum(acc, axis=0)    # 最终归约
    tl.store(out_ptr + row, result)
```

每个线程保持一个累加器，逐块片处理一行数据。最后，通过 `tl.sum(acc, axis=0)` 将所有线程的累加器合并成一个标量。

这是从逐元素到分块的过渡——数据不再能一次性装进块里，你需要引入循环和更复杂的索引管理。

---

## 九、矩阵乘法：分块（Tiling）的经典实践

矩阵乘法是深度学习的命根子，也是本讲的压轴戏。我们来看三种方法的演进：

### 朴素方法

固定某个 (m, n) 位置，对每个 k 从 HBM 读入 A[m, k] 和 B[k, n]，乘累加。这是正确但极其低效的：读取次数是 M×K×N 量级，算术强度（操作数 / 传输字节数）是常数 O(1)，完全不可接受。

### 理想化方法

把整个 A 和 B 都加载到共享内存，然后计算 C。这样读取次数降到 M×K + K×N，算术强度达到理想的 O(N)。但问题是：A 和 B 通常太大，无法放入共享内存。

### 分块方法（Tiling）

这是真正的解法。把输出矩阵 C 分成多个输出块（tiles），每个线程块负责一个输出块。对于每个 (A 的行块, B 的列块)：

1. 加载对应的 A 块和 B 块到共享内存。
2. 执行块级矩阵乘法（`tl.dot`）。
3. 累加到部分和中。

```python
@triton.jit
def matmul_relu_kernel(a_ptr, b_ptr, c_ptr, M, N, K, ...):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)

    indices_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    indices_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    indices_k = tl.arange(0, BLOCK_K)

    a_ptrs = a_ptr + indices_m[:, None] * stride_am + indices_k[None, :] * stride_ak
    b_ptrs = b_ptr + indices_k[:, None] * stride_bk + indices_n[None, :] * stride_bn

    acc = tl.zeros([BLOCK_M, BLOCK_N], dtype=tl.float32)

    for k in range(0, K, BLOCK_K):
        a = tl.load(a_ptrs, mask=...)
        b = tl.load(b_ptrs, mask=...)
        acc += tl.dot(a, b)          # 核心：块级矩阵乘法
        a_ptrs += BLOCK_K * stride_ak
        b_ptrs += BLOCK_K * stride_bk

    acc = tl.maximum(acc, 0.0)       # 内核融合：在写回前应用 ReLU
    tl.store(c_ptrs, acc, mask=...)
```

这个实现的额外好处是**内核融合**：在写回 HBM 之前，你可以对累加结果应用任何逐元素函数（如 ReLU）。这避免了额外的内核启动和 HBM 往返。

这里的算术强度提升到分块大小的量级，虽然达不到理想的 O(N)，但如果分块足够大，效果已经很好。

---

## 十、课程总结与学习路径

这一讲在整个课程中的位置非常关键：它填补了从“宏观理解 GPU”到“实际编写内核”之间的鸿沟。上一讲（第五讲）建立算法与硬件的桥梁，这一讲则让你手握 Triton 这一工具，为接下来的课程（多 GPU 编程、Flash Attention 实现）打下基础。

核心要点可以归纳为几个层次：

1. **编程模型保证正确性**：PyTorch、Triton、PTX 三个层次提供了从高层抽象到底层控制的不同选择。
2. **硬件细节决定性能**：SM 数量、warp 锁步执行、存储体冲突、内存合并、占用率——这些都会影响最终速度。
3. **基准测试和性能分析帮助你找到瓶颈**：永远先测量再优化。
4. **Triton 让线程块思考变得自然**：读入共享内存 → 操作（可以融合）→ 写回 HBM。

从 GeLU（逐元素）到 Softmax（行内归约）、行求和（块片循环）再到矩阵乘法（真正的分块），难度逐步递增。理解了这些例子，你就掌握了实现 Flash Attention 所需的全部要素——它本质上就是 Softmax 和矩阵乘法在分块策略下的融合。

下次我们将从单个 GPU 转向多个 GPU，探讨数据并行和模型并行等更深层次的分布式训练技术。但在此之前，请确保你已经掌握了本讲的核心：用 Triton 以线程块为单位思考，让硬件的每个部分都物尽其用。

---

## 参考资料

- **官方视频**：[CS336 2026 Lecture 6](https://www.youtube.com/watch?v=xnDHaNUvHBg)
- **课程讲义**：[CS336 · Language Modeling from Scratch](https://cs336.stanford.edu/lectures/?trace=lecture_06)（Lecture 6: Kernels, Triton）
- **GPU 架构入门讲义**：[Stanford CS149 · GPU Architecture & CUDA Programming](https://cs149.stanford.edu/winter19content/lectures/07_gpuarch/07_gpuarch_slides.pdf)
