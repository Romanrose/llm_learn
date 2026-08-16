# CS336 Lecture 7：并行（Parallelism）中文讲义

## 学习目标

完成本讲学习后，你应该能够：

1. 理解分布式训练中的核心集合通信原语（collective operations），包括 all-reduce、reduce-scatter、all-gather 等
2. 解释 GPU 集群的硬件拓扑（NVLink、NVSwitch、InfiniBand）及其对通信带宽的影响
3. 掌握三种基本并行策略：数据并行（data parallelism）、张量并行（tensor parallelism）、流水线并行（pipeline parallelism）
4. 理解 DDP（Distributed Data Parallel）的实现原理：仅需在反向传播后插入一步梯度 all-reduce
5. 知道如何测量通信有效带宽，并能解释 all-reduce 与 reduce-scatter 的带宽关系

---

## 课程主线

本讲从单个 GPU 扩展到多个 GPU。上周我们关注单个 GPU 内部的优化（融合、分块等），本周则讨论如何协调多个 GPU 之间的数据流动。

核心观点：**计算单元与数据之间的距离是核心瓶颈**。单 GPU 场景下，数据在 HBM 中；多 GPU 场景下，数据可能在另一块 GPU 上。目标都是编排计算，避免数据传输成为瓶颈。

### 广义层次结构

| 层级 | 连接方式 | 相对速度 |
|------|---------|---------|
| 单节点单 GPU | L1 缓存 / 共享内存 | 最快 |
| 单节点单 GPU | HBM | 快（上周认为慢） |
| 单节点多 GPU | NVLink / NVSwitch | 中等 |
| 多节点多 GPU | InfiniBand / Ethernet | 慢 |

上周通过融合和分块减少内存访问；本周通过**复制（replicating）**和**分片（sharding）**减少 GPU 间通信。

### 为什么需要多 GPU？

1. **容量不足**：参数、激活值、梯度或优化器状态无法放入单 GPU HBM。例如 1 万亿参数模型远超单卡容量。
2. **加速训练**：即使单卡可容纳，仍希望通过拆分利用更多 GPU 的计算能力。

注意：分散到多 GPU 需要付出通信带宽代价，需要计算权衡。

---

## 第一部分：分布式通信与计算的构建模块

### 集合通信操作（Collective Operations）

这些原语源于 1980 年代的并行编程文献，并非为 LLM 训练发明，但至今仍是标准工具。

**基本术语**：
- **Rank**：特定设备（本课程中即 GPU）的编号
- **World size**：设备总数

**核心操作**：

#### 基础原语（热身）

| 操作 | 描述 | 训练中的直接用途 |
|------|------|-----------------|
| Broadcast | 从 rank 0 复制张量到所有 rank | 初始化时广播 checkpoint |
| Scatter | rank 0 上的大张量按 rank 分割分发 | 理解 reduce-scatter 的基石 |
| Gather | 从所有 rank 收集分片到 rank 0 | 理解 all-gather 的基石 |
| Reduce | 对所有 rank 的数据应用归约（sum/min/max）到 rank 0 | 理解 all-reduce 的基石 |

#### 训练中的核心操作

**All-gather**：对所有 rank 执行 gather，每个 rank 最终持有完整张量。

**Reduce-scatter**：对每个维度执行归约，然后将结果分发到不同 rank。

**All-reduce** = reduce-scatter + all-gather。输入相同，先在每个维度归约，再收集到所有 rank。

关键区别：
- All-reduce 在数据并行中用于梯度求和并复制完整参数
- 更高级方法（ZeRO、FSDP）需要将 all-reduce 拆分为 reduce-scatter + all-gather，以便更精细地管理存储

**All-to-all**：每个 rank 向其他每个 rank 发送指定张量。对 MoE 训练很重要——动态路由需要根据数据决定激活值送往哪个专家。当切分均衡时，all-to-all 本质上是矩阵转置。

#### 术语记忆技巧

- **Reduce**：执行结合律、交换律操作（sum、min、max）
- **Scatter** 是 **Gather** 的逆操作
- **All** 意味着目的地是所有设备

### 硬件：GPU 如何连接

#### 传统家庭式设置
- 同一节点 GPU 通过 PCIe 总线通信
- 不同节点通过以太网连接
- 这种方式不适合严肃的大规模训练

#### 数据中心设置
- 通常每节点 8 个 GPU，通过 NVLink 连接到 NVSwitch
- 参考：NVLink 5 提供约 1.8 TB/s 总带宽；B200 HBM 带宽约 8 TB/s（慢约 4 倍）
- 多个节点组成 pod，pod 间通过 InfiniBand 连接（需经过 PCIe）
- 更大规模经以太网连接（需经过 CPU，最慢）

#### RDMA（Remote Direct Memory Access）

标准以太网通信需经过 CPU：GPU → CPU 内核 socket 缓冲区 → 网络数据包 → 网络接口。这会引入大量延迟。

**RDMA 允许 GPU 直接读写另一 GPU 内存，无需 CPU 介入**。NVLink/NVSwitch 环境天然支持 RDMA，InfiniBand 也支持。标准以太网不支持，但 RoCE（RDMA over Converged Ethernet）实现了类似能力。

#### 值得注意的进展

- **NVIDIA NVL72**：8 GPU/托盘 × 9 托盘 = 72 GPU 组成单一 NVLink 域，实现高速互联
- **RoCE**：以太网绕过 CPU，作为 InfiniBand 的更低成本替代方案

### PyTorch 分布式实现

**NCCL**（NVIDIA Collective Communication Library）：将集合操作翻译为 GPU 间实际发送的底层数据包。NCCL 检测硬件拓扑、优化路径、启动通信内核。

**`torch.distributed`** 提供简洁接口：
- 后端选择：GPU 用 `nccl`，CPU 用 `gloo`
- 支持更高级算法如 FSDP（本课程不使用）

**关键示例**：

```python
# All-reduce：就地修改张量
dist.all_reduce(tensor=data, op=dist.ReduceOp.SUM)

# Reduce-scatter：输出到单独张量
dist.reduce_scatter_tensor(output=output, input=input, op=dist.ReduceOp.SUM)

# All-gather：输出到张量列表
dist.all_gather_into_tensor(output_tensor=output, input_tensor=input)
```

**同步注意**：
- CUDA 操作默认异步，需要 `torch.cuda.synchronize()` 确保内核完成
- `dist.barrier()` 等待所有进程到达同一点
- 异步操作允许计算与通信重叠

### 通信基准测试与有效带宽

**All-reduce 带宽计算**：
```
sent_bytes = size_bytes × 2 × (world_size - 1)
total_duration = world_size × duration
bandwidth = sent_bytes / total_duration
```

- 因子 2：发送和接收
- (world_size - 1)：归约步数
- 随 world_size 增大，(world_size-1)/world_size ≈ 1，带宽 ≈ 2 × size_bytes / duration

**关键性质**：
- 有效带宽与 world_size **无关**（好事）
- 与拓扑无关（NCCL 决定环或树形拓扑）
- Reduce-scatter 无 2 倍因子，因为只需发送一次

由于 all-reduce = reduce-scatter + all-gather，all-reduce 移动 2 倍数据，耗时约 2 倍，但带宽相同。

---

## 第二部分：分布式训练

本部分通过极简 MLP 实现讲解三种并行策略。注意：MLP 是 Transformer 中的计算瓶颈，因此具有代表性。

### 数据并行（Data Parallelism）

**策略**：按批次维度切分数据，每个 GPU 持有完整模型参数和优化器状态。

**流程**：
1. 每个 rank 持有 `batch_size / world_size` 条数据
2. 独立前向传播、计算损失
3. 独立反向传播得到**不同的**梯度
4. **关键步骤**：对所有参数梯度执行 all-reduce（取平均）
5. 更新参数

**核心洞察**：DDP 与标准训练的唯一区别就是**在反向传播后插入一步梯度同步**。

```python
# 唯一区别
for param in params:
    dist.all_reduce(tensor=param.grad, op=dist.ReduceOp.AVG)
```

**性质**：
- 各 rank 损失不同（基于本地数据）
- 梯度 initially 不同，经 all-reduce 后相同
- 参数始终保持一致

**约束**：批次大小需 ≥ world size，最好是 world size 的倍数。

**简洁性**：DDP 非常模块化——不关心前向传播的具体形式，适用于任意模型。

**局限**：需要在内存中保存所有模型参数。当模型放不进单卡内存时，需要更聪明的方案（下一讲：FSDP/ZeRO，使用 all-gather + reduce-scatter 而非完整 all-reduce）。

### 张量并行（Tensor Parallelism）

**策略**：按宽度维度（特征维度）切分每层参数，每个 rank 持有部分参数。

**列并行（Column Parallel）**：
- 参数矩阵形状为 `num_dim × local_num_dim`（按列切分）
- 每个 rank 计算部分激活值
- 通过 **all-gather** 收集所有激活值，拼接为完整维度

**与数据并行的区别**：
- 数据并行无需改动模型本身
- 张量并行必须修改模型结构（利用矩阵乘法可分解性）

**前向传播**：每层计算后 all-gather 激活值。

**反向传播**：对偶操作为 **reduce-scatter** 梯度。

**硬件要求**：
- 每层都需传输激活值（数据量大）
- 通常只在**节点内部**（NVLink/NVSwitch）使用
- 不会跨 NVLink 域使用张量并行

### 流水线并行（Pipeline Parallelism）

**策略**：按深度（层）切分网络，每个 rank 获得部分层。

**流程**：
1. 数据批次拆分为**微批次（micro-batches）**
2. rank 0 处理自己的层后，通过点对点 `send` 发送到 rank 1
3. rank 1 接收后继续处理，再发送到 rank 2

**关键原语**：
- `dist.recv(tensor=x, src=rank-1)`：从上一个 rank 接收
- `dist.send(tensor=x, dst=rank+1)`：发送到下一个 rank
- 异步版本（`isend`/`irecv`）支持通信与计算重叠

**微批次动机**：
- 减少**流水线气泡（pipeline bubble）**——等待其他张量处理时的空闲时间
- 更小批次快速处理并传递，减少空闲

**缺失内容**：
- 通信与计算重叠（异步操作）
- 反向传播的具体实现（作业内容）

**硬件要求**：
- 容忍较慢互联
- 适合跨节点甚至跨地域场景（去中心化训练）

### 并行策略选择考量

| 策略 | 通信量 | 硬件要求 | 主要挑战 |
|------|--------|---------|---------|
| 数据并行 | 梯度同步 | 中等 | 批大小上限（临界批大小） |
| 张量并行 | 每层激活值 | 高（NVLink） | 需修改模型 |
| 流水线并行 | 层间激活值 | 低 | 流水线气泡 |

**常见组合**：节点内张量并行 + 节点间数据/流水线并行。

**临界批大小**：数据并行中，批大小增长超过某阈值后不再提升效率，应考虑其他并行方式。

---

## 课程作业关联

作业二涉及：
- 实现集合通信操作
- 研究通信与计算重叠（特别是反向传播中梯度计算后立即开始通信）
- 实现三种并行策略

---

## 常见误区

1. **认为 rank 就是 GPU**：本课程中 rank 等价于 GPU，但概念上 rank 是逻辑设备编号
2. **忽视 CUDA 异步性**：CUDA 内核默认异步，必须 `synchronize()` 确保完成，且注意与 `barrier()` 的顺序
3. **认为 all-gather 与 gather 相同**：all-gather 输出到所有 rank，gather 仅输出到指定 rank
4. **混淆 reduce-scatter 与 scatter**：scatter 仅分发不归约，reduce-scatter 先归约再分发
5. **认为带宽与 world_size 相关**：有效带宽公式中 (world_size-1)/world_size 收敛于 1，实际与规模无关
6. **张量并行用于所有互联**：张量并行通信频繁，只应在 NVLink 等高速互联上使用
7. **忽视同步屏障的代价**：过多 barrier 导致不必要等待
8. **DDP 计算量重复**：每个 rank 都做完整前向/反向，是冗余计算，但避免传输优化器状态

---

## 关键公式与原则

**有效带宽**：
```
all-reduce: bandwidth ≈ 2 × size_bytes / duration
reduce-scatter: bandwidth ≈ size_bytes / duration
```

**集合操作组合**：
```
all-reduce = reduce-scatter + all-gather
gather = scatter 的逆操作
all = 目的地为所有设备
```

**并行策略对比**：
```
数据并行：按 batch 切分，同步梯度
张量并行：按 width 切分，同步激活值
流水线并行：按 depth 切分，传递激活值
```

---

## 复习清单

- [ ] 能画出广播、散射、收集、归约、全收集、归约散射、全归约、全对全的输入输出图
- [ ] 解释为什么 all-reduce = reduce-scatter + all-gather
- [ ] 描述 GPU 集群的典型拓扑及各级带宽相对关系
- [ ] 解释 RDMA 解决的问题（绕过 CPU）
- [ ] 编写 DDP：只需在反向传播后插入梯度 all-reduce
- [ ] 解释张量并行为何需要高速互联，反向传播对应哪个操作
- [ ] 解释微批次如何减少流水线气泡
- [ ] 推导 all-reduce 有效带宽公式，解释 2 倍因子来源
- [ ] 理解异步操作（async_op=True）如何实现通信与计算重叠
