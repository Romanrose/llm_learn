# CS336 Lecture 6：Kernels、Triton 与 GPU 性能优化

## 学习目标

完成本讲后，你应该能够：

- 理解 GPU 的硬件层次结构（寄存器、共享内存、L2 缓存、HBM）及其对性能的影响
- 解释线程、线程块（thread block）、网格（grid）和 warp 之间的关系
- 识别影响 GPU 性能的关键因素：控制发散、占用率、存储体冲突、内存合并
- 进行正确的基准测试（benchmarking）和性能分析（profiling）
- 使用 Triton 编写三种类型的内核：逐元素操作（GeLU）、按行归约（softmax、row sum）、矩阵乘法（tiling）

---

## 课程主线

本讲有两个核心部分：

1. **回顾 GPU 硬件与编程模型**：建立对 GPU 性能瓶颈的直觉
2. **动手编写 Triton 内核**：从最简单的逐元素操作出发，逐步过渡到需要线程间通信的归约和矩阵乘法

贯穿始终的主线是：**编程模型负责正确性，硬件理解负责性能**。Triton 的价值在于它让你以"线程块"为思考单位，自动处理大部分底层细节，但你仍需理解硬件才能真正优化性能。

---

## 一、GPU 硬件回顾

### 1.1 内存层次结构

GPU 的存储层次从快到慢、从小到大依次为：

| 层次 | 本讲建立的性能直觉 |
|------|------|
| 寄存器（每 SM） | 线程私有、最快；讲义以 B200 约 65,000 个寄存器（约 256 KB）为例。 |
| L1 缓存与共享内存（每 SM） | 两者共享同一物理内存；共享内存可由程序员显式使用。 |
| L2 缓存 | 芯片级共享，比每个 SM 内的存储层次更大。 |
| HBM | 容量最大、跨代增长明显，但在这条层级中访问最慢。 |

课程强调的是容量与带宽大致负相关：越靠近计算单元的存储越快，容量通常越小。

**注意**：B200 还有张量内存（tensor memory, TMEM），位于寄存器和共享内存之间，供张量核心使用，但对程序员不可见。

### 1.2 编程模型

#### 三个层次

- **线程（thread）**：在数据的一小部分上执行代码
- **线程块（thread block）/ CTA**：一组线程，共享同一块共享内存
- **网格（grid）**：线程块的集合，一次内核启动对应一个网格

（H100/B200 还有线程块簇（thread block cluster），支持分布式共享内存，本讲不展开。）

#### 为什么需要线程块？

- 逐元素操作（如 GeLU）用线程直接处理每个元素就够了，线程之间不需要通信。
- 但 softmax、矩阵乘法这类操作需要线程间通信。如果全部通过 HBM 完成，代价极高。
- 线程块让一组线程共享 SM 上的共享内存，实现块内通信。

**核心思想**：线程块被调度到某个 SM 上执行，从 HBM 读取数据到共享内存，处理完后写回 HBM。

### 1.3 编程模型与硬件的交互

编程模型本身很简单：知道线程、线程块、网格即可写出正确的代码。但性能高度依赖硬件细节。

#### Warp：锁步执行的线程组

- 每个 warp = 32 个线程。64 线程的线程块 = 2 个 warp。
- warp 内所有线程必须以锁步（lockstep）方式执行同一条指令。
- **控制发散（control divergence）**：如果 warp 内不同线程走不同分支（if A else B），必须串行执行，严重降低效率。
- SM 同时运行多个 warp，一个 warp 等待 HBM 时，调度器零成本切换到另一个 warp——这是**延迟隐藏**的关键机制。

#### 占用率（Occupancy）

- 每个线程最多使用 255 个寄存器；SM 寄存器总量固定（如 65536 个）。
- 每个线程用寄存器越多，能同时调度的线程越少 → 占用率降低。
- 占用率低不一定是坏事：如果每个线程做更多工作（线程粗化，thread coarsening），可能反而更好。

**计算示例**：128 线程的线程块，每线程 160 个寄存器：
- 每块需 128 × 160 = 20,480 个寄存器
- SM 最多同时容纳 65,536 ÷ 20,480 ≈ 3 个块 = 384 线程 = 12 个 warp
- 若 SM 最多支持 64 个 warp，占用率 = 12/64 = 18%

#### 存储体冲突（Bank Conflicts）

- 共享内存分为 32 个存储体（bank），每个 4 字节宽。
- 每个时钟周期每个 bank 只能被一个线程访问。
- 多个线程访问同一 bank → 串行化 → 存储体冲突。
- 最坏情况：32 个线程同时访问矩阵第一列 → 32 路冲突。
- 矩阵乘法中不可避免（访问 A 的行和 B 的列），解决方案是 **swizzling**（重新排列共享内存布局）。

#### 内存合并（Memory Coalescing）

- warp 的 32 个线程访问 HBM 时，访问被合并为 128 字节的缓存行事务。
- 理想情况：所有线程访问同一缓存行 → 一次事务完成。
- 访问列时，大部分加载的数据未被使用 → 浪费带宽。

> **区分的要点**：存储体冲突是共享内存的问题；内存合并是 HBM 的问题。

#### 块占用率（Block Occupancy）

- 线程块以"波次"（wave）调度到 SM。
- 若线程块数不是 SM 数的整数倍，最后一波只有少量块 → 部分 SM 空闲。
- 例：B200 有 148 个 SM，启动 160 个块 → 第二波只有 12 个块。
- **解决思路**：让线程块数量整除 SM 数量。

---

## 二、基准测试与性能分析

### 2.1 方法论：成功配方

1. 对代码做基准测试和性能分析
2. 做出修改
3. 再次基准测试和性能分析

**关键原则**：在编写任何内核之前，先测量现有代码，找出瓶颈在哪里。

### 2.2 基准测试（Benchmarking）：测量端到端时间

基准测试只回答"花了多久"，不回答"时间花在哪里"。

#### 正确做法

```python
# 预热（warmup）：排除惰性编译等一次性开销
for _ in range(num_warmups):
    run()
torch.cuda.synchronize()  # 必须等待异步 CUDA 操作完成

# 多次计时，取平均
for trial in range(num_trials):
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)
    start_event.record()
    run()
    end_event.record()
    torch.cuda.synchronize()
    times.append(start_event.elapsed_time(end_event))
```

**注意事项**：
- **必须预热**：首次运行可能包含编译时间，而稳态性能才是你关心的。
- **使用 CUDA events 而非 CPU 计时**：避免测量到 CPU 启动内核的开销。
- **多次计时取平均**：消除方差。更严格的做法是看分布（如 P95）。

#### 基准测试的用途：观察扩展性

矩阵乘法的时间随维度增加应呈三次方增长。但注意：维度较小时（如 < 2000），时间几乎不变——GPU 是为大矩阵乘法设计的，小矩阵会很低效。

### 2.3 性能分析（Profiling）：定位瓶颈

性能分析告诉你时间花在哪里，还能揭示"引擎盖下实际发生了什么"。

#### PyTorch 内置 profiler

```python
with torch.profiler.profile(activities=[ProfilerActivity.CUDA]) as prof:
    run()
    torch.cuda.synchronize()
print(prof.key_averages().table(sort_by="cuda_time_total"))
```

#### 观察结果

- `a + b`：调用名为 `kernel at CUDA functor add` 的内核——一个张量加法内核。
- `a @ b`：调用 Cutlass 内核，名称形如 `cutlass3x_sm100_simt_sgemm_f32_f32_f32_f32_f32_64x64x16...`
  - `cutlass`：NVIDIA 的线性代数 CUDA 库
  - `sm100`：Blackwell 架构（B200）
  - `f32`：单精度浮点
  - `64x64x16`：分块（tile）形状

**重要发现**：改变张量维度会触发不同的内核（如从 64x64x16 变为 32x32x16）。PyTorch 在底层为你做了大量决策。

---

## 三、案例研究：GeLU 的三种实现

### 3.1 GeLU 函数

GeLU 激活函数（tanh 近似）：

```
gelu(x) = 0.5 * x * (1 + tanh(√(2/π) * (x + 0.044715 * x³)))
```

### 3.2 三种实现

1. **Naïve PyTorch 实现**：直接写出公式，每一步是独立内核
2. **PyTorch 内置实现**：`torch.nn.functional.gelu(x, approximate="tanh")`
3. **编译实现**：`torch.compile(naive_gelu)`

基准测试中，Naïve 版本明显慢于内置实现与编译实现；重点不在某个单点数值，而在于三者的数学结果相同、底层 kernel 数量和内存流量却不同。

### 3.3 为什么性能差异这么大？

用 profiler 查看：
- **Naïve 实现**：调用多个内核（加法、tanh、乘法等）。每次内核调用都从 HBM 读取数据、写回结果，然后下一个内核再读取……**没有内核融合**。
- **内置实现**：只有一个 GeLU CUDA 内核。
- **编译实现**：`torch.compile` 生成单个 Triton 内核，将所有操作融合。

**核心概念——内核融合（kernel fusion）**：将多个逐元素操作合并为一个内核，每个元素只从 HBM 读一次、写一次，而非多次往返。

---

## 四、Triton 入门

### 4.1 CUDA vs Triton

**CUDA**（NVIDIA 开发）：
- 思维模型：每个线程做什么
- 优点：细粒度控制，接近底层
- 缺点：线程间通信需要手动管理同步（synchronize）、共享内存分配

**Triton**（OpenAI 开发）：
- 思维模型：每个线程块做什么
- 优点：不需要显式处理线程同步、共享内存分配；编译器自动生成 PTX
- 适合从零开始的课程和大多数训练/推理场景

### 4.2 Triton 的概念框架

- 思考"块做什么"：一个块将数据加载到共享内存 → 操作 → 写回全局内存
- 是"巨型矩阵操作"（PyTorch 风格）和"单线程操作"（CUDA 风格）之间的中间点
- 实际上你写的是 Python 代码，使用 `@triton.jit` 装饰器

---

## 五、Triton 内核示例

### 5.1 GeLU：逐元素操作

```python
@triton.jit
def triton_gelu_kernel(x_ptr, y_ptr, num_elements, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(axis=0)  # 标识当前块
    start = pid * BLOCK_SIZE
    offsets = start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < num_elements  # 处理边界情况

    x = tl.load(x_ptr + offsets, mask=mask)
    # 计算 GeLU...
    tl.store(y_ptr + offsets, y, mask=mask)
```

启动方式：
```python
num_blocks = triton.cdiv(num_elements, BLOCK_SIZE)
kernel[(num_blocks,)](x, y, num_elements, BLOCK_SIZE=BLOCK_SIZE)
```

**关键点**：
- 内核函数没有返回值，需要提前分配输出张量 `y`
- 方括号中的 `(num_blocks,)` 定义网格形状
- `tl.program_id` 告诉块"我是谁"
- `tl.arange(0, BLOCK_SIZE)` 生成 0 到 BLOCK_SIZE-1 的索引
- `mask` 处理张量大小不能整除块大小的情况
- 指针就是整数，用偏移量访问
- 计算部分看起来几乎像普通 PyTorch——这是 Triton 的设计目标

### 5.2 底层发生了什么：PTX

Triton 编译器将内核编译为 PTX（Parallel Thread Execution）——GPU 的中间汇编语言。

观察 PTX 代码可以学到：
- `ld.global.*` / `st.global.*`：从 HBM 读写
- `%ctaid.x`：块索引；`%tid.x`：线程索引
- `%f*`：浮点寄存器；`%r*`：整数寄存器
- 每个线程实际处理 8 个元素——编译器自动做了**线程粗化**（thread coarsening）

**注意**：PTX 代码只编译一次，所有线程执行同一份代码，通过线程 ID 区分自己。

### 5.3 Softmax：按行归约

**朴素 PyTorch 版本**需要约 5 次 MN 读取、3 次 MN 写入（max、subtract、exp、sum、divide），而理论只需要一次读、一次写。

**Triton 版本**：让每个块负责一行。

```python
@triton.jit
def triton_softmax_kernel(x_ptr, y_ptr, x_row_stride, y_row_stride,
                          num_cols, BLOCK_SIZE: tl.constexpr):
    row_idx = tl.program_id(0)
    col_offsets = tl.arange(0, BLOCK_SIZE)

    x_ptrs = x_ptr + row_idx * x_row_stride + col_offsets
    x_row = tl.load(x_ptrs, mask=col_offsets < num_cols, other=float("-inf"))

    x_row = x_row - tl.max(x_row, axis=0)  # 数值稳定性
    numerator = tl.exp(x_row)
    denominator = tl.sum(numerator, axis=0)
    y_row = numerator / denominator

    tl.store(y_ptr + row_idx * y_row_stride + col_offsets, y_row,
             mask=col_offsets < num_cols)
```

**关键点**：
- 假设每行能放进一个块（`BLOCK_SIZE >= num_cols`）
- `stride` 告诉如何将二维索引映射到线性内存
- `tl.max(x_row, axis=0)` 沿列做归约——Triton 处理了内部的通信和同步
- 块之间没有共享内存，天然独立

### 5.4 Row Sum：一行装不下的归约

当行长度超过块大小时（如 4096 列，块大小 1024），需要在单个线程块内部循环分片。

```python
@triton.jit
def row_sum_kernel(x_ptr, out_ptr, N, BLOCK_SIZE: tl.constexpr):
    row = tl.program_id(0)
    acc = tl.zeros([BLOCK_SIZE], dtype=tl.float32)  # 每个线程的累加器

    for start in range(0, N, BLOCK_SIZE):  # 遍历所有分片
        cols = start + tl.arange(0, BLOCK_SIZE)
        mask = cols < N
        x = tl.load(x_ptr + row * N + cols, mask=mask, other=0.0)
        acc += x

    result = tl.sum(acc, axis=0)  # 最终的线程间归约
    tl.store(out_ptr + row, result)
```

**概念区别**：这里循环遍历的是同一行的不同分片（tile），不是独立的块。块对应整行，每个块处理整行的所有分片。

### 5.5 矩阵乘法：Tiling 的艺术

#### 朴素方法的问题

固定输出元素 C[m,n]，对每个 k 从 HBM 读取 A[m,k] 和 B[k,n]：
- 读取次数 ~ M×K×N，算术强度 O(1)
- 大量冗余读取：C4 和 C5 都用到 A4、A5、A6

#### 理想化方法

把整个 A 和 B 加载到共享内存：
- 读取次数降至 M×K + K×N，算术强度 O(N)（理想情况）
- 问题：A 和 B 通常太大，放不进共享内存

#### Tiling 方法（分块）

**核心思想**：在全局层面是朴素的，在局部层面是理想化的。

1. 将输出矩阵 C 划分为输出分块（tile），每个分块对应一个线程块
2. 对每个输出分块，扫描 A 的行分块和 B 的列分块：
   - 将对应的 A 分块、B 分块从 HBM 加载到共享内存
   - 做矩阵乘法，累加到部分和
3. 完成后将输出分块写回 HBM

**算术强度提升到 O(tile_size)**，通常不够理想 O(N)，但已足够好。

**额外收益——内核融合**：既然在写内核，可以顺便应用逐元素激活函数（如 ReLU），在写回 HBM 之前完成，无需额外往返。

```python
@triton.jit
def matmul_relu_kernel(a_ptr, b_ptr, c_ptr, M, N, K,
                       stride_am, stride_ak, stride_bk, stride_bn,
                       stride_cm, stride_cn,
                       BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr,
                       BLOCK_K: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)

    indices_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    indices_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    indices_k = tl.arange(0, BLOCK_K)

    a_ptrs = a_ptr + indices_m[:, None] * stride_am + indices_k[None, :] * stride_ak
    b_ptrs = b_ptr + indices_k[:, None] * stride_bk + indices_n[None, :] * stride_bn

    acc = tl.zeros([BLOCK_M, BLOCK_N], dtype=tl.float32)

    for k in range(0, K, BLOCK_K):
        a = tl.load(a_ptrs, mask=(indices_m[:, None] < M) & (indices_k[None, :] + k < K), other=0.0)
        b = tl.load(b_ptrs, mask=(indices_k[:, None] + k < K) & (indices_n[None, :] < N), other=0.0)
        acc += tl.dot(a, b)
        a_ptrs += BLOCK_K * stride_ak
        b_ptrs += BLOCK_K * stride_bk

    acc = tl.maximum(acc, 0.0)  # ReLU，融合激活

    c_ptrs = c_ptr + indices_m[:, None] * stride_cm + indices_n[None, :] * stride_cn
    tl.store(c_ptrs, acc, mask=(indices_m[:, None] < M) & (indices_n[None, :] < N))
```

**回顾 stride 的作用**：张量在内存中是线性化的。`stride` 告诉你多维索引 (row, col) 如何映射到线性索引：`index = row * stride_row + col * stride_col`。

---

## 六、与课程作业的关联

本讲内容直接服务于作业中的内核实现任务。你需要：

1. 用 profiler（Nsight）分析 PyTorch 代码，理解底层内核调度
2. 为注意力机制编写 Triton 内核（Flash Attention）
3. 利用 `tl.load` / `tl.store` / `tl.dot` / `tl.reduce` 等 Triton 原语

本讲覆盖的 GeLU、softmax、矩阵乘法是 Flash Attention 的三个构成要素：
- 逐元素操作（GeLU）→ 理解如何加载、计算、存储
- 按行归约（softmax）→ 理解块内归约
- 矩阵乘法 tiling → 理解如何将大操作分解到多个线程块

---

## 七、常见误区

1. **把 HBM 读写当免费**：每次内核启动都伴随 HBM 往返。减少内核数量（融合）是优化第一要务。

2. **认为占用率越高越好**：低占用率不一定是坏事。有时让每个线程做更多工作（线程粗化）反而更好。

3. **混淆存储体冲突和内存合并**：前者是共享内存问题，后者是 HBM 问题。解决方案完全不同。

4. **忘记预热或不同步**：基准测试必须预热、多次计时、显式 `torch.cuda.synchronize()`，否则数据不可信。

5. **认为 Triton 自动处理所有事情**：Triton 处理线程块内部的同步和共享内存，但你要思考如何划分块、如何管理掩码、如何避免边界错误。

6. **块大小越大越好**：块太大可能放不进共享内存，或导致存储体冲突；块太小无法有效利用硬件。需要实验。

7. **忽略尾波效应**：线程块数量应尽量整除 SM 数量，否则最后一波会有 SM 空闲。

---

## 八、复习清单

**硬件与模型**
- [ ] 能否画出 GPU 内存层次图，并说出每层的容量、带宽量级？
- [ ] 能否解释 thread、thread block、grid、warp 的关系？
- [ ] 为什么需要线程块，而不是只用一个线程网格？

**性能因素**
- [ ] 什么是控制发散？为什么应该尽量避免？
- [ ] 什么是占用率？如何计算？为什么高占用率不等于高性能？
- [ ] 什么是存储体冲突？最坏情况是什么？swizzling 是什么？
- [ ] 什么是内存合并？什么访问模式是最佳的？
- [ ] 什么是波次量化（wave quantization）问题？

**基准测试与分析**
- [ ] 基准测试前为什么必须预热？
- [ ] 为什么用 CUDA events 而不是 CPU 计时？
- [ ] 为什么 `torch.cuda.synchronize()` 是必需的？
- [ ] profiler 能告诉你什么？如何从内核名称推断实现细节？

**Triton 编程**
- [ ] Triton 的思维模型与 CUDA 有何不同？
- [ ] `tl.program_id`、`tl.arange`、`tl.load`、`tl.store` 各自做什么？
- [ ] 为什么要用 mask？什么时候需要？
- [ ] Triton 生成的 PTX 代码中，`%ctaid.x` 和 `%tid.x` 分别代表什么？

**算法模式**
- [ ] 逐元素操作（GeLU）的 Triton 内核结构是怎样的？
- [ ] 按行归约（softmax）为什么适合用"一行一块"策略？
- [ ] 一行太大时怎么办？（分片循环 + 累加器）
- [ ] 矩阵乘法的 naive、idealized、tiling 三种方法有何区别？
- [ ] Tiling 如何影响算术强度？
- [ ] 什么情况下可以在写回 HBM 前融合激活函数？
