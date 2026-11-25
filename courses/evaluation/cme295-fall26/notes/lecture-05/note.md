# Stanford CME 295 · Transformers & Large Language Models · Autumn 2026
## Lecture 5：LLM Systems 学习笔记（候选稿）

> 说明：本笔记依据 Lecture 5 的逐字稿整理，只保留课程中明确出现的观点、术语与例子。课程中的数值（如 141 GB、75.2 对 66.6、五倍价格、十倍缓存价格、G=2 与 H=24 等）均按逐字稿原样引用，仅用于数量级直觉，不作为硬件规格或基准结论。凡属整理者的归纳与解释，均以「解读」标注。

---

## 一、学习目标

学完本讲，应当能够：

1. 说明为什么 LLM 的 decoder 在系统层面主要是一堆矩阵乘法，以及为什么这使 GPU 成为核心硬件。
2. 区分 **FLOPs**（算力预算的度量）与 **FLOPS / FLOP/s**（算力速度的度量），并解释 GPU 规格表上三类关键资源：算力、内存容量、内存带宽。
3. 解释单卡内存不足的两个来源：模型参数本身，以及训练时的 activations、gradients、optimizer states。
4. 用「迭代求分子/分母 + 数值稳定重缩放」推导 FlashAttention 的核心恒等式，并说明它为什么是**精确**方法、为什么能减少 HBM 读写、为什么反向传播中重算反而更快。
5. 区分五类并行：data parallelism、tensor parallelism、pipeline parallelism、context parallelism、expert parallelism；说明 ZeRO 属于数据并行的分片变体而非模型并行，并解释各自的通信代价与「气泡」问题。
6. 用 TTFT、TPOT、TTLT 描述推理延迟，并用 arithmetic intensity 与 roofline model 判断一个工作负载是 memory-bound 还是 compute-bound。
7. 解释 KV cache、paged attention、GQA / MQA、MLA 各自解决什么问题、付出什么代价。
8. 说明 speculative decoding 的接受/拒绝规则，并理解它为什么能恢复目标模型的分布。

---

## 二、课程主线

本讲回答两个贯穿始终的问题：

- **如何让模型装得下硬件？**（fit）
- **如何让它跑得快？**（speed）

课程按层次推进：

1. **单 GPU 内部**：以 FlashAttention 为例，说明如何通过算子融合与重计算，减少对慢速大容量内存的读写。
2. **多 GPU 训练**：说明为什么单卡内存必然不够，然后系统梳理数据并行、ZeRO 分片与四类模型并行。
3. **推理系统**：引入 TTFT / TPOT / TTLT、arithmetic intensity、roofline model，再依次讲 KV cache 的显存管理（paged attention）、KV 表示压缩（GQA / MQA、MLA）、以及用 speculative decoding 一次生成多个 token。

这条主线本身就是一个递进：先优化单个算子，再优化跨设备的数据与计算布局，最后优化服务端的显存与解码流程。

---

## 三、核心概念

### 3.1 硬件资源三角：算力、容量、带宽

课程用一张 GPU 规格表（以 Nvidia H200 为例）建立直觉：

- **算力速度**：以 teraflops 量级表示，且强烈依赖数据类型（低精度格式每秒可执行更多操作）。
- **内存容量**：HBM 为数百 GB 量级（课上例子为 141 GB）；SRAM 小得多，课上说是数百 MB 量级。
- **内存带宽**：HBM 约为每秒数 TB 量级；SRAM 快约一个数量级，为每秒数十 TB 量级。

关键结构事实：计算发生在片上的 **compute units**，HBM 在片外。SRAM 快而小，HBM 大而慢，因此优化的核心杠杆是**减少对 HBM 的读写次数**，而不是单纯减少计算量。

一个粗略估算说明了容量约束：若模型有 1000 亿参数、每个参数用 fp16（2 字节）存储，仅参数就需约 200 GB，已超过上述 GPU 的容量；训练还需额外存 activations、gradients、optimizer states（如 Adam 需要跟踪多个量）。

### 3.2 FlashAttention

**问题**：masked self-attention 需要 QKᵀ，形成 N×N 矩阵（N 为序列长度，可达数千甚至数万）。朴素实现要把这个大矩阵写入 HBM，再读回做 softmax，再写回，再读出去乘 V。

**障碍**：softmax 的分母是整行指数之和，看似必须先物化整行。

**关键恒等式**：把求和写进分子后，

softmax(S)·V 的第 i 个分量 = exp(S_i)V_i 之和 / exp(S_j) 之和

因此可以定义分子累加量 N_T 与分母累加量 D_T，逐元素迭代更新：

- N_{T+1} = N_T + exp(S_{T+1})·V_{T+1}
- D_{T+1} = D_T + exp(S_{T+1})

最终结果就是 N/D，无需先物化整个 softmax 矩阵。

**数值稳定性**：exp 可能溢出。做法是分子分母同乘同一个常数（不改变比值），取「到目前为止遇到的最大 S 的负指数」。设 M 为运行最大值，则新元素贡献 exp(S − M)，已累加部分乘以 exp(M_old − M_new) 重新缩放。课程指出：若某分量小到无法表示，近似为 0 无害；真正危险的是大到无法表示且仍在贡献求和。

**解读**：这套推导的两个支点——迭代求和、运行最大值重缩放——就是课程希望记住的全部；幻灯片上复杂的公式只是这两点的产物。

**为什么快**：把 Q、K、V 的小块送入 SRAM，在片上完成融合计算，只把最终结果写回，避免 N×N 矩阵的 HBM 往返。

**训练时的额外收益**：反向传播本可复用前向存的注意力矩阵，但那意味着把它物化在 HBM。FlashAttention 选择在反向时**即时重算**，因此计算量更高（课上给出 75.2 对 66.6 的 GFLOPS 对比，仅作数量级参考），但运行时间更短。课程强调这是反直觉但正确的取舍：当被物化的对象很大且访问很慢时，丢弃结果并重算可能更划算。

**精确性**：课堂问答明确，FlashAttention 不做任何近似，结果与原始公式完全相同。课程提到文献中有 FlashAttention 2/3/4，它们在此之上做优化并适配新 GPU 系列（Hopper 的 H100/H200、Blackwell 的 B100/B200）。

### 3.3 训练并行：五个维度

动机：单卡内存装不下参数、activations（随序列长度与 batch size 增长）、gradients、optimizer states。

| 并行方式 | 切分对象 | 要点 |
|---|---|---|
| Data parallelism | 数据 | 各设备独立做前向/反向，之后同步梯度 |
| ZeRO（ZeRO Redundancy Optimizer） | optimizer states / gradients / parameters 分片 | 消除副本冗余；代价是计算前需通信取参数 |
| Tensor parallelism | 单层内的矩阵运算 | 多头注意力按 head 拆分；FFN 中矩阵可按行/列分解 |
| Pipeline parallelism | 按层切分 | 前向把信息传给下一设备，同时保留激活供反向；会产生设备空闲的 **bubble** |
| Context parallelism | 序列/token | 各设备持有部分 query，交换 K/V 后重复计算 |
| Expert parallelism | MoE 的 experts | 先做 attention，再按路由把 token 发到持有对应 expert 的设备，算完送回 |

课堂问答中的两个关键澄清：

- **ZeRO 不是模型并行**：对给定数据子批次，全部计算仍在同一设备上完成；只是通过通信获取缺失的参数、梯度、优化器状态。模型并行的定义是计算本身被分散到不同设备。
- **可以组合**：不是五选一。课程明确说可以把 tensor parallelism 与 data parallelism 等混用；但不应把并行度拉满，因为并行以设备利用不充分和通信开销为代价，而 GPU 按小时计费。

### 3.4 推理延迟指标

课程用两个对比场景建立直觉：10 token 输入 → 10k token 输出，与 10k token 输入 → 10 token 输出。后者更快，因为解码是逐 token 自回归，而 prefill 可以并行处理整个 prompt（teacher forcing）。

三个指标：

- **TTFT**（time to first token）：首 token 时间，受排队策略与 prefill 并行化影响。
- **TPOT**（time per output token）：每个输出 token 的时间。
- **TTLT**（time to last token）：最后一个 token 的时间。

infra 视角最关注前两个；TTLT 受模型自身推理行为（例如用户请求长故事）影响，不一定是系统不好的信号。

课程还提到：输出价格经验上约为输入价格的五倍（并非必然规律），并有「缓存输入」价格约为新输入十分之一的说法；这里的缓存指跨轮次复用的已计算状态，与解码时的 KV cache 不是同一件事（后者计入输出成本）。

### 3.5 Arithmetic intensity 与 roofline model

- **Arithmetic intensity** = 完成的计算量 / 移动的内存量，把算力速度与内存带宽联系起来。
- **Roofline model**：以 arithmetic intensity 为横轴、计算吞吐量为纵轴，存在一条上界折线，因形似屋顶得名。折点称为 **ridge point**，此点既不受内存限制也不受计算限制。

课程给出的定位直觉：

- **解码阶段**：加载全部权重却只预测一个 token，处于 memory-bound 区域（课上称紫色区域）。
- **预填充阶段**：若用 FlashAttention 之类技巧做好内存优化，大量计算可并行，应处于 compute-bound 区域。

### 3.6 KV cache 与 paged attention

解码时复用过去算出的 keys 和 values，即 KV cache。

**显存管理问题**：服务商按用户可能的最大输出长度预留显存块，但实际 completion 往往远短于上限，造成大量「未使用但不可分配」的碎片。

**Paged attention**：给内存一个逻辑视图，把 K/V 放入大小为 B 的块中，并维护元数据（查找映射）记录每个查询的每个键值放在哪里。权衡是：B 太小则元数据庞大，B 太大则碎片化重现。课上给出 B=16 作为实践中典型数量级。

### 3.7 KV 表示压缩：GQA / MQA 与 MLA

- **MHA**：H 个 query 投影与 H 个 key/value 投影。
- **GQA**：只保留 G 个 key/value 投影，把 query 分组共享。G=H 退化为 MHA；G=1 为 **MQA**（multi-query attention），课程明确说这是另一个不想要的极端，因为 K/V 表达力不足以支撑好的特征。
- 课上例子：G=2、H=24 时，按 1 − 2/24 计算，内存占用减少约 91%；并提到 G=2 是 Qwen 3.8 Flash Next 采用的值（按逐字稿原样保留，不作外部核实）。

**代价**：参数更少意味着表达力下降，这是明确的 trade-off；预训练时通常做 grid search 与 ablation 研究来确定 G，实践中发现太接近 H 时收益只是边际性的。

- **MLA**（multi latent attention）：借用 LoRA 式的矩阵分解思路，先把 K/V 投影成一个很小的共享潜在表示，只存储这个共享固定表示，而非每头每 token 的向量；课程强调其「魔力」在于键与值共享同一个投影矩阵，使每个 token 只有一个表示。

### 3.8 Speculative decoding

**动机**：自回归逐 token 生成是耗时部分，而验证 token 是廉价的（可并行输入，prefill 与训练阶段都体现这一点）。于是用便宜的 **draft model** 生成接下来 K 个 token，交给 **target model** 一次性验证。

**接受规则（rejection sampling）**：

- 若目标模型对该 token 的置信度高于草稿模型，直接接受；
- 否则以概率比 min(1, T(x)/D(x)) 接受；
- 拒绝时，从残差分布中采样下一个 token，残差分布为 max(0, T(x) − D(x)) 归一化后的分布。

**正确性证明（课程现场推导）**：用全概率公式按「接受/拒绝」分支展开 P(X=x)，再用联合概率公式 P(A∩B)=P(A)P(B|A)，代入接受概率 min(1, T/D)，可化出

min(D(x), T(x)) + max(0, T(x) − D(x)) = T(x)

即该流程精确恢复目标模型的分布。课程将此称为一个非平凡的事实，并逐项消去中间项完成证明。

**额外收益与代价**：验证时目标模型已经把下一个 token 算出来了，等于「免费」多得一个 token；但一旦发生拒绝，之后草稿做的工作全部浪费，所以希望分布尽量对齐。对齐手段有两种课程提到的方法：**knowledge distillation**（让草稿拟合教师模型的下一 token 分布）与 **multi-token prediction**（同一 LLM 训练 K 个预测头，用它们作草稿，只用第一个作验证器）。

---

## 四、关键公式与原则

1. **资源三分配**：算力速度（FLOP/s）、内存容量（HBM）、内存带宽（HBM↔SRAM）。优化时先判断瓶颈在哪一项。
2. **softmax 的整行依赖**：单个分量的 softmax 需要整行指数和——这是朴素 attention 必须物化 N×N 矩阵的根源。
3. **FlashAttention 迭代式**：N_{T+1} = N_T + exp(S_{T+1})V_{T+1}，D_{T+1} = D_T + exp(S_{T+1})，输出为 N/D；配合运行最大值 M 做重缩放 exp(S − M) 与 exp(M_old − M_new)。
4. **精确性原则**：FlashAttention 与 speculative decoding 的接受规则都不引入近似（后者在分布意义上精确恢复目标分布）。
5. **Roofline 判据**：arithmetic intensity 与 ridge point 的相对位置决定 memory-bound 还是 compute-bound。
6. **并行不是免费的**：任何并行都换取通信开销或设备空闲（bubble），并行度应按瓶颈选择而非拉满。
7. **重算 vs 存储**：当中间结果很大且存储介质访问慢时，丢弃并重算可能比物化更快。

---

## 五、课程作业关联

逐字稿未直接描述作业题目。可据课程内容推断的关联方向（属解读，非课程原话）：

- 若作业涉及实现 attention，应能对比朴素实现与分块/融合实现在显存占用与运行时间上的差异，并解释差异来自 HBM 读写次数而非 FLOPs。
- 若作业涉及多卡训练配置，应能根据模型规模与序列长度估算单卡是否装得下，并论证选择哪种并行组合、需要哪些通信。
- 若作业涉及推理服务指标，应能用 TTFT / TPOT 拆解延迟，并判断给定负载落在 roofline 的哪一侧。

---

## 六、常见误区

1. **混淆 FLOPs 与 FLOPS**：前者是算力预算（总量），后者是算力速度（每秒）。课程在第二讲提过前者，本讲才真正用到后者。
2. **以为 FlashAttention 是近似注意力**：课堂明确否认，它是精确方法，只是改变了数据搬运方式。
3. **以为重算一定更慢**：在中间结果巨大且需写入慢速内存时，反向重算可以减少运行时间，代价是更高 FLOPs。
4. **以为 ZeRO 是模型并行**：对给定子批次，计算仍全部在同一设备完成，只是通过通信取参数。
5. **以为并行方式只能选一种**：可以组合；但不应盲目拉满并行度。
6. **把「跨轮次缓存输入」与「解码 KV cache」混为一谈**：前者是提供商已算好的历史状态、按输入计价；后者发生在解码、计入输出成本。
7. **以为 GQA 中 G 越小越好**：G=1（MQA）是另一个极端，K/V 表达力不足；G 的选择需要 ablation。
8. **认为 TTLT 高就说明系统差**：TTLT 很大程度上由模型自身生成长度决定，infra 主要优化 TTFT 与 TPOT。
9. **以为拒绝采样只是工程启发式**：课程给出了它精确恢复目标分布的证明。

---

## 七、复习清单

- [ ] 我能解释为什么 decoder 的两层本质上是矩阵乘法，以及 GPU 的哪些特性使其适合。
- [ ] 我能写出 GPU 规格表上三类资源的名称与数量级关系（不背具体数字）。
- [ ] 我能用 1000 亿参数、fp16 的例子说明单卡为何装不下，并列出训练时除参数外还需存储的四类量。
- [ ] 我能从 softmax 的整行依赖出发，说明朴素 attention 的 HBM 读写序列。
- [ ] 我能写出 FlashAttention 的迭代式与重缩放因子，并说明为何它是精确的。
- [ ] 我能解释 FlashAttention 在反向传播中为何选择重算，以及代价与收益。
- [ ] 我能列出五种并行方式各自切分什么，并说明 ZeRO 为何不是模型并行。
- [ ] 我能解释 pipeline parallelism 的 bubble 从何而来。
- [ ] 我能区分 TTFT、TPOT、TTLT，并说明 infra 关注哪两个。
- [ ] 我能用 arithmetic intensity 与 roofline model 判断解码与预填充分别处于哪一侧。
- [ ] 我能说明 paged attention 解决的碎片化问题，以及块大小 B 的双向权衡。
- [ ] 我能写出 GQA 在两个极端（G=H、G=1）分别退化为哪种注意力，并说明其代价。
- [ ] 我能说明 MLA 共享了什么、只存储什么。
- [ ] 我能复述 speculative decoding 的接受规则，并说明残差分布的形式与「免费多得一个 token」的含义。
- [ ] 我能说出两种让草稿与目标分布对齐的方法。
