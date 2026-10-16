# Stanford CS149 · Parallel Computing  
## Lecture 7：GPU Architecture and CUDA Programming

## 学习目标

完成本讲后，应能够：

1. 解释 GPU 如何从固定的图形流水线演化为通用并行处理器。
2. 使用 SPMD（Single Program, Multiple Data）模型理解 CUDA kernel。
3. 区分 CUDA thread、thread block、warp 与 Streaming Multiprocessor（SM）。
4. 根据 `threadIdx`、`blockIdx` 和 `blockDim` 计算线程负责的数据位置。
5. 理解 host/device 分离的地址空间，以及显式数据传输的成本。
6. 使用 shared memory 和 block-level barrier 组织线程协作。
7. 从多线程、SIMD、任务调度和资源约束的角度解释 GPU 如何执行大量 CUDA 线程。
8. 判断哪些跨线程块通信方式是安全的，哪些会依赖未定义的调度顺序并可能死锁。

---

## 一、课程主线

本讲的核心观点是：现代 GPU 并没有引入一套完全陌生的并行计算思想。它主要把课程前面讨论过的多核、硬件多线程、SIMD、SPMD 和任务调度，以更大的规模重新组合起来。

课程沿着三条线索展开：

1. **历史线索**：GPU 最初为图形渲染设计，随后通过 shader、通用 GPU 计算的早期“绕行方案”、Brook 等数据并行语言，最终发展出 CUDA。
2. **编程模型**：程序员编写一个 kernel，并批量启动大量 CUDA threads；线程被组织成 thread blocks。
3. **硬件实现**：GPU 将 blocks 动态调度到多个 SM，在 SM 内以 warp 为单位利用 implicit SIMD 执行，并通过保留大量执行上下文隐藏延迟。

---

## 二、从图形渲染到通用计算

### 2.1 图形工作负载天然具有数据并行性

传统图形处理首先接收三角形网格（triangle mesh），将三维顶点投影到屏幕，再为三角形覆盖的像素计算颜色。材质种类极多，因此颜色计算逐渐不再由固定功能硬件完成，而是由一个小程序完成；这个程序会针对大量像素分别运行。

从并行计算角度看，这正是典型的数据并行工作负载：

- 图像包含数百万个像素；
- 同一个着色程序作用于不同像素；
- 各像素的计算在很大程度上可以独立进行；
- 实时渲染要求每秒重复执行几十次甚至更多。

因此，GPU 很早就开始增加更多核心和 ALU，而不是依赖更强的单线程性能。CPU 遇到时钟频率、功耗和指令级并行性（ILP）增长受限的问题时，GPU 已经在利用不断增加的晶体管扩展并行执行资源。

### 2.2 早期 GPGPU 是对图形接口的“借用”

早期研究者发现，像素着色程序也可以执行物理模拟、流体模拟或蛋白质相关计算。为了触发大量程序实例，他们会绘制覆盖整个屏幕的三角形，然后把像素输出通道当作普通数值使用，例如把 RGBA 解释为粒子的空间坐标。

这种方法能利用 GPU 的算力，但实现上仍然受制于图形流水线。Brook 等系统进一步提供了流式编程模型（stream programming model）或数据并行编程模型：程序看起来是在对集合中的每个元素应用函数，编译器再把它转换为底层图形操作。

2007 年，NVIDIA 提供了更直接的 compute mode 和 CUDA：程序员不再伪装成“绘制三角形”，而是提交一个 kernel，并要求 GPU 运行它的许多副本。

---

## 三、CUDA 的核心抽象：SPMD 与批量启动

CUDA 采用 SPMD 编程模型：

> 编写一个程序，由大量具有不同线程 ID 的程序实例执行；每个实例根据自己的 ID 决定处理哪些数据。

这里的“线程”是 **CUDA thread**，即编程模型中的逻辑程序实例。它不能直接等同于 CPU 线程，也不能直接等同于一个独占的硬件执行上下文。

CUDA 与 ISPC 的对应关系可以近似理解为：

| ISPC | CUDA |
|---|---|
| program instance | CUDA thread |
| gang | thread block 内的一组线程 |
| task | thread block |
| `programIndex` | `threadIdx` 与 `blockIdx` 组合得到的位置 |
| 编译器生成 SIMD 指令 | GPU 硬件识别可共同执行的线程 |

这一对应关系用于建立直觉，并不表示两套系统在所有细节上完全相同。

### 3.1 Grid、block 与 thread

一次 kernel launch 会创建一个 grid。Grid 由多个 thread blocks 构成，每个 block 又包含多个 CUDA threads。CUDA 允许这些维度是一维、二维或多维的，这对于图像和张量寻址很方便。

一维情况下，线程的全局索引通常为：

\[
i = \text{blockIdx.x}\times \text{blockDim.x}+\text{threadIdx.x}
\]

二维情况下：

\[
i = \text{blockIdx.x}\times \text{blockDim.x}+\text{threadIdx.x}
\]

\[
j = \text{blockIdx.y}\times \text{blockDim.y}+\text{threadIdx.y}
\]

多维 ID 并不是计算模型的本质要求；它主要能减少从一维索引还原图像或张量坐标时的地址计算。

### 3.2 向上取整与边界检查

若数据规模不能被 block 大小整除，grid 通常需要覆盖到数据边界之外。需要的 block 数为：

\[
\text{numBlocks}
=
\left\lceil
\frac{N}{\text{threadsPerBlock}}
\right\rceil
\]

使用整数运算时可写成对应的向上取整形式。这样会产生一些没有有效数据可处理的线程，因此 kernel 内必须检查：

\[
i < N
\]

二维矩阵则需要同时检查行、列边界。

**讲义原意**：CUDA 的抽象不是“对数组中的每个元素自动创建一个线程”，而是“创建指定数量的 blocks 和 threads”；每个线程再通过程序判断自己应该做什么。遗漏边界判断可能导致越界访问甚至程序崩溃。

---

## 四、Host、Device 与 CUDA 内存模型

简化的 CUDA 系统包含两个执行世界：

- **Host**：普通 C/C++ 代码运行在 CPU 上。
- **Device**：CUDA kernel 运行在 GPU 上。

对于独立 GPU，可以把 CPU 与 GPU 理解为拥有各自的地址空间和 DRAM。普通 `malloc` 返回 host 地址，而 `cudaMalloc` 返回 device 地址。Host 不能直接把 device pointer 当作本地指针解引用；kernel 也不能直接使用普通 host allocation。

典型的数据流是：

1. 在 host 上准备输入数据；
2. 在 device 上分配空间；
3. 将数据从 host 复制到 device；
4. 启动 kernel；
5. 等待计算完成；
6. 将结果从 device 复制回 host。

对于独立显卡，复制通常意味着数据经过 PCIe，在两套 DRAM 之间移动，因此可能很慢。异步复制可以用来隐藏一部分延迟。课程将这种复制类比为在两个地址空间之间进行消息传递。

现代系统可能允许 kernel 直接使用某些 CPU 指针，但讲义强调：这并不意味着访问免费；实际访问仍可能经过 PCIe。理解分离地址空间仍然是分析 CUDA 数据移动成本的基础。

### 4.1 三类重要存储范围

本讲给出的简化 CUDA 内存层次包括：

- **Thread-local storage**：每个线程私有，其他线程不可访问。
- **Shared memory**：每个 block 一份，只有该 block 内的线程能够访问。
- **Device global memory**：设备上的所有 CUDA threads 都可通过 load/store 访问。

Thread block 因而不仅是编号方式，也是线程协作、同步和数据局部性的基本范围。

---

## 五、Shared Memory：显式组织数据复用

课程以一维卷积为例。若每个输出值需要读取相邻三个输入值，最直接的实现会让相邻线程从 global memory 重复加载重叠数据。即使缓存可能缓解这一问题，程序仍可利用 shared memory 显式组织复用。

假设一个 block 有 128 个线程并计算 128 个输出。若每个输出需要三个相邻输入，则整个 block 需要 130 个输入元素：

\[
128 + 2 = 130
\]

协作加载过程为：

1. 128 个线程各加载一个输入到 block 的 shared array；
2. 其中两个线程额外加载末尾的两个元素；
3. 所有线程到达 block-level barrier；
4. 屏障之后，各线程从 shared memory 读取所需的三个值并计算输出。

这样，每份重叠输入只需从 global memory 搬入一次，之后由相邻线程在快速的 block-local storage 中复用。

### 5.1 为什么必须有 barrier

线程采用 SPMD 方式执行，但硬件不保证 block 内所有线程以完全相同的速度推进。如果没有 `syncthreads` 一类的 barrier，某个线程可能在其他线程尚未完成加载时就开始读取 shared memory。

Barrier 的语义是：

> 只有当 block 内所有线程都到达屏障后，任何线程才可以继续。

因此，越过屏障后，程序才能依赖共享数组已经被完整初始化。Shared memory 与 barrier 共同表达了“这组线程需要被放在一起协作”的意图。

---

## 六、从 CUDA 程序到 GPU 执行

### 6.1 Blocks 是可调度的工作单位

一次 launch 可以创建约一百万个 CUDA threads，组成数千个 blocks。GPU 不需要同时拥有一百万个硬件执行上下文。更合适的理解是：

- Grid 声明了一大批工作；
- GPU 的硬件调度器维护尚未执行的 blocks；
- 各 SM 从中取得 blocks；
- 当一个 block 完成并释放资源后，SM 再接收新的 block。

这与任务系统或线程池很相似：程序声明大量相对独立的工作，由调度器把它们分配给有限数量的 worker。课程特别指出，作业中由软件实现的部分任务调度思想，在 GPU 中被实现进了硬件。

Block 被调度时，硬件需要一次性为它分配所需资源，包括：

- block 中所有线程的执行上下文；
- 该 block 要求的 shared memory；
- kernel 运行所需的其他资源。

多个 blocks 可以同时驻留在同一个 SM 上，前提是总资源需求不超过 SM 的容量。

### 6.2 资源需求决定驻留数量

若每个 block 需要 128 个线程执行上下文和约 512 字节 shared memory，则 SM 能同时容纳多少 blocks，取决于两类资源中更先耗尽的一类。可能仍有空闲线程上下文，但 shared memory 已不足以容纳下一个 block，此时新 block 仍不能被调度。

这种机制的关键优点是：同一 kernel 的 blocks 通常具有相同的资源需求。一个 block 完成后，恰好释放出启动同类 block 所需的一组资源，调度过程因而相对简单。

---

## 七、Warp、Implicit SIMD 与 SM

### 7.1 Warp 是硬件概念

CUDA thread 和 thread block 属于编程模型，而 **warp** 是硬件执行概念。课程以 NVIDIA GPU 为例，将 32 个 CUDA threads 的执行上下文组织为一个 warp。

每个 CUDA thread 在概念上有：

- 自己的标量寄存器；
- 自己的程序计数器（Program Counter，PC）；
- 自己的执行状态。

当一个 warp 中的线程位于同一条指令时，硬件可以让它们通过 SIMD 执行单元共同执行。这称为 **implicit SIMD**：

- CPU SIMD 通常由编译器生成显式向量指令；
- GPU 接收的是大量标量风格的 CUDA threads；
- 硬件比较线程的 PC，并识别哪些线程能够共同执行。

从大多数程序的性能直觉来看，可以把一个 warp 近似看作“执行向量指令的传统线程”，但这只是理解方式：实际上每个 CUDA thread 仍有自己的 PC。

### 7.2 分支分歧

若 warp 内的线程走向不同控制流，它们的 PC 不再一致。硬件会运行处于某一 PC 的线程，同时屏蔽其他线程，再处理另一条路径。这与带掩码的 SIMD 执行相似。

因此：

> SPMD 允许各线程执行不同控制流，但 warp 内控制流越一致，SIMD 执行资源通常利用得越充分。

课程强调不要混淆 SPMD 与 SIMD：

- **SPMD** 描述程序员看到的编程模型；
- **SIMD** 描述硬件如何同时执行多个数据通道；
- CUDA 是 SPMD 模型，GPU 可以使用 SIMD 实现它。

### 7.3 Streaming Multiprocessor

SM 可以包含：

- 多组 warp 执行上下文；
- 多个取指和译码单元；
- 浮点、整数、load/store 和特殊数学运算等执行资源；
- 供驻留 blocks 使用的 shared memory。

以课程讨论的 V100 为例，一个 SM 可以保留大量 warps，并在每个周期从可运行 warps 中选择少数几个推进。大量驻留线程并不代表它们全部同时执行，而是让硬件在某些 warps 等待内存或其他资源时，迅速选择其他可运行 warps，从而隐藏延迟。

课程给出的总体理解是：

\[
\text{GPU execution}
=
\text{multicore}
+
\text{heavy multithreading}
+
\text{SIMD}
+
\text{limited superscalar scheduling}
\]

---

## 八、线程块的同步语义与调度限制

### 8.1 一个 block 必须能够整体驻留

若某个 block 声明需要 256 个线程，但一个 SM 只能提供 128 个线程执行上下文，GPU 不能简单地先运行前 128 个线程，再运行后 128 个线程。

原因在于 block 内可能存在 barrier：

1. 前 128 个线程运行到 barrier；
2. 它们等待同一 block 的其余线程；
3. 但它们仍占用全部执行上下文；
4. 后 128 个线程无法开始；
5. 程序死锁。

除非系统使用代价很高的抢占与状态换出机制，否则无法保证这种执行正确且高效。因此，标准 CUDA 模型要求一个 block 的所有线程能够同时处于活跃状态并驻留在同一个 SM 上。

### 8.2 Block 内与 block 间保证不同

同一个 block 内：

- 线程被放在同一 SM 上；
- 可以共享 shared memory；
- 可以使用 block-level barrier；
- 可以通过原子操作等方式协作。

不同 blocks 之间：

- 可以访问同一 global memory；
- 可以执行 global atomic operations；
- 不能假设 blocks 的执行顺序；
- 不能假设两个 blocks 会同时驻留。

例如，所有 blocks 都对全局直方图执行 `atomicAdd` 是有效的：无论 blocks 以何种顺序运行，原子更新仍然成立。

但若 block 1 忙等，直到 block 0 写入某个标志，就可能死锁。假设 GPU 一次只能运行一个 block，而调度器先运行 block 1，block 1 会持续等待；block 0 因没有资源而永远无法启动。

关键原则是：

> Blocks 可以通过 global memory 发生交互，但 kernel 内不能依赖 blocks 的执行先后顺序。

---

## 九、课程作业关联

### Assignment 2

本讲多次将 GPU block 调度与任务系统联系起来：

- 大量 blocks 类似一批待处理任务；
- SM 类似 worker；
- GPU 硬件维护“下一个 block”并进行动态分配；
- 一个 block 完成后释放资源，随后调度新 block。

因此，Assignment 2 中的软件任务调度、worker 分配以及 SIMD mask 等经验，是理解 GPU 硬件调度和 warp divergence 的直接基础。

### Assignment 3

课程明确指出，Assignment 3 将涉及 CUDA，包括：

- host 与 device 之间的数据管理；
- kernel launch；
- thread/block 索引；
- block 内同步；
- 原子操作；
- host 等待 device 完成；
- 线程组织和内存访问方式对性能的影响。

编写作业代码时，不能只验证计算结果，还应检查 block 大小、数组边界、shared memory 用量、同步位置和连续内存访问。

---

## 十、常见误区

1. **把 CUDA thread 当作 CPU thread。**  
   CUDA thread 是逻辑程序实例；大量 CUDA threads 会复用有限的硬件执行资源。

2. **把 SPMD 和 SIMD 当作同义词。**  
   前者是编程模型，后者是执行机制。CUDA 的 SPMD threads 可以由 GPU 以 implicit SIMD 方式执行。

3. **认为二维 thread ID 是 CUDA 的本质。**  
   一维同样可以完成计算；多维组织主要为了方便图像和张量寻址。

4. **认为 launch 的线程数必须恰好等于数据元素数。**  
   Threads 按 blocks 创建，通常需要向上取整，并在 kernel 中检查边界。

5. **认为 device pointer 能被 host 直接访问。**  
   在简化的分离地址空间模型中，这种解引用无效；现代统一寻址能力也不代表访问没有传输成本。

6. **认为 shared memory 会自动获得复用收益。**  
   程序必须显式安排协作加载、同步和读取；缺少 barrier 可能读到尚未初始化的数据。

7. **认为一个 block 可以分批运行。**  
   Block 内 barrier 要求所有线程能够同时处于活跃状态，因此 block 不能超过单个 SM 可支持的规模。

8. **认为 blocks 会按编号执行。**  
   CUDA 不保证 block 的启动和完成顺序。跨 block 的生产者—消费者忙等可能死锁。

9. **认为线程越多、block 越大就一定越快。**  
   Block 大小和 shared memory 用量会影响一个 SM 能同时驻留多少 blocks；程序员指定这些参数时，也是在对硬件资源作出要求。

10. **把 warp 与 thread block 混为一谈。**  
    Block 是程序员可见的协作和调度单位；warp 是 GPU 用于组织和执行一组线程的硬件细节。

---

## 十一、复习清单

- [ ] 能说明像素着色为何构成数据并行工作负载。
- [ ] 能概述从图形流水线、早期 GPGPU hack、Brook 到 CUDA 的演化。
- [ ] 能解释 CUDA 为什么采用批量 SPMD kernel launch。
- [ ] 能区分 grid、thread block、CUDA thread、warp 和 SM。
- [ ] 能根据 `blockIdx`、`blockDim`、`threadIdx` 计算全局数据索引。
- [ ] 能正确处理数据规模不能整除 block 大小时的边界条件。
- [ ] 能说明 host memory、device global memory、shared memory 和 thread-local storage 的访问范围。
- [ ] 能解释 CPU–GPU 数据复制为什么可能成为性能成本。
- [ ] 能用一维卷积示例说明 shared memory 如何支持跨线程数据复用。
- [ ] 能说明 `syncthreads` 所保证的条件，以及省略它可能产生的错误。
- [ ] 能解释 GPU 如何把大量 blocks 动态分配到有限数量的 SM。
- [ ] 能说明线程上下文和 shared memory 如何共同限制 block 驻留数量。
- [ ] 能区分 SPMD 与 implicit SIMD。
- [ ] 能解释 warp divergence 与 SIMD mask 的关系。
- [ ] 能说明大量驻留 warps 如何用于隐藏延迟。
- [ ] 能解释为什么一个 block 必须整体适配单个 SM。
- [ ] 能判断跨 block 的原子更新为何有效，而依赖 block 顺序的忙等为何可能死锁。
