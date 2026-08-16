---
title: "CS336 2026 · Attention alternatives and mixture of experts · Lecture Note"
description: "从零构建语言模型，覆盖架构、GPU、并行训练、Scaling Laws、评估与数据。"
search: true
---



<CourseHeader eyebrow="CS336 2026 · Lecture 4" title="Attention alternatives and mixture of experts" description="" status="已发布" :details='[{"label":"日期","value":"Wed April 8"},{"label":"讲师","value":"Tatsu"},{"label":"官方资料","value":"1 项"},{"label":"内容产物","value":"3 项"}]' :links='[{"label":"课程主页","url":"https://cs336.stanford.edu/"},{"label":"官方视频","url":"https://www.youtube.com/playlist?list=PLoROMvodv4rMqXOcazWaTUHhq-yembLCV"},{"label":"官方讲义仓库","url":"https://github.com/stanford-cs336/lectures"}]' />

<CourseTabs active="lecture-note" :items='[{"id":"overview","label":"课程资料","route":"/generated/courses/cs336-2026/lecture-04/"},{"id":"lecture-note","label":"Lecture Note","route":"/generated/courses/cs336-2026/lecture-04/lecture-note"},{"id":"blog","label":"Blog 解读","route":"/generated/courses/cs336-2026/lecture-04/blog"},{"id":"transcript-zh","label":"中文逐字稿","route":"/generated/courses/cs336-2026/lecture-04/transcript-zh"}]' />

<div class="source-note">本页由 <code>llm/cs336-2026/notes/lecture-04/note.md</code> 自动生成；原始笔记位置保持不变。</div>

# CS336 Lecture 4：注意力替代方案与混合专家（MoE）

- 视频：[Bilibili P4](https://www.bilibili.com/video/BV1msTD6CE6j?p=4)
- 主题：**Attention alternatives** 与 **Mixture of Experts**
- 形式：根据英文音频机器转写整理、翻译为中文讲义；术语和公式保留英文缩写，非逐字翻译。

## 一页总览

现代 LLM 的两项主要架构压力来自：

1. **上下文变长**：标准注意力需要每个位置与所有位置交互，序列长度为 \(n\) 时成本随 \(n^2\) 增长；长上下文下它会超过 FFN，成为主要瓶颈。
2. **希望更多参数、但不希望同等增加 FLOPs**：MoE 将原本稠密的 FFN 替换为多个专家，并只激活少数专家，使总参数量大于每个 token 的激活参数量。

本讲的中心观点是：架构并非只看大 O；**常数、内存访问、跨卡通信和负载均衡**都会实质决定模型是否可训练、可部署。

---

## Part I：为什么需要注意力替代方案？

标准自注意力为：

$$
\operatorname{Attn}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

其中 \(QK^\top\) 会形成 \(n\times n\) 的注意力矩阵，因此计算与显存均受 \(n^2\) 影响。随着 context window 增大，FFN 的线性成本增长慢于注意力的二次增长。

### 1. 先做系统优化：FlashAttention

FlashAttention 不改变注意力的数学结果或二次复杂度；它通过分块计算、避免物化完整 attention matrix，减少 HBM 与 SRAM 之间的内存搬运。

- 这是典型的“常数因子”优化，却能带来显著吞吐提升。
- 它还让部分原本放不进显存的序列长度变得可运行。
- 但当上下文到百万 token 量级时，仅靠常数优化仍不够，必须改变连接模式或状态表示。

### 2. 线性注意力：利用矩阵乘法结合律

暂时忽略 softmax 后：

$$
(QK^\top)V = Q(K^\top V)
$$

左式先计算 \(QK^\top\)，会产生 \(n^2\) 项；右式先计算 \(K^\top V\)，成本转为约 \(O(nd_kd_v)\)。隐藏维度通常远小于极长的上下文长度，所以对长序列更有利。

这也给出一个 RNN 视角。令状态为：

$$
S_t=S_{t-1}+k_t v_t^\top, \qquad y_t=q_tS_t
$$

含义：

- **训练**时可用关联/扫描（scan）形式并行计算；
- **推理**时只携带固定大小的 \(S_t\)，而非整段 KV cache；
- 代价是去掉或近似 softmax 后，表达能力通常不及全注意力。

因此实践中更常见的是**混合架构**：多数层使用线性或局部机制，间隔若干层插入一次全局 softmax attention。讲座中以 7 个线性层配 1 个全注意力层为例；关键不是某个固定比例，而是保留必要的全局信息交互。

### 3. Mamba-2：为状态加入遗忘门

线性注意力的朴素状态会无差别累积历史信息。Mamba-2 可以理解为在此基础上加入输入依赖的门 \(\gamma_t\)：

$$
S_t = \gamma_t \odot S_{t-1} + k_tv_t^\top
$$

直觉与 LSTM 的 forget gate 相似：模型可决定保留多少旧状态。重要限制是门应仅依赖当前输入、而不依赖先前状态；这样才仍能同时拥有并行训练形式与递归推理形式。

### 4. Gated DeltaNet：控制“写入”与“遗忘”

Gated DeltaNet 在遗忘门之外增加写入门 \(\beta_t\)：

- \(\gamma_t\)：控制旧状态保留多少；
- \(\beta_t\)：控制当前 token 的新信息是否写入；
- delta 方向试图在写入当前 key 的同时，减少与现有状态中相同方向的冗余信息。

它们共同目标是：保留状态模型的长序列/推理优势，同时提升简单线性递归的表达能力。课程强调，目前大规模最可靠的方案依然多为**带 softmax attention 的混合模型**，而不是完全线性的替代品。

### 5. 选择注意力机制时的判断框架

| 方案 | 优点 | 主要代价/风险 |
|---|---|---|
| 全 softmax attention | 全局检索能力强、成熟 | 长序列二次成本与 KV cache 大 |
| FlashAttention | 不改语义却显著提速 | 不改变二次渐近复杂度 |
| 线性/状态空间层 | 近线性扩展、固定状态推理 | 信息压缩与表达能力受限 |
| 混合层 | 兼顾效率和全局建模 | 架构与训练调参更复杂 |

---

## Part II：MoE 是什么？

MoE 的本质是把 Transformer block 中的稠密 FFN 改成条件计算：

$$
y = \sum_{i\in \operatorname{TopK}(g(x))} g_i(x)\,E_i(x)
$$

- \(E_i\)：第 \(i\) 个 expert，通常本身就是一个 FFN；
- \(g(x)\)：router/gate，为当前 token 给专家打分；
- 每个 token 仅执行 top-\(K\) 个专家。

若把一个 FFN 换成 \(N\) 个同尺寸专家，总参数量可以接近增加 \(N\) 倍；但一次前向/反向只付出约 \(K\) 个专家的计算。故 MoE 可以理解为**更高参数密度的 FFN**，而非一种与 Transformer 完全不同的模型。

### 1. Top-K 路由

最常用的路由器很简单：为每个 expert 学一个向量，与 token 表示做内积得到 score；对 expert 维度归一化后，取分数最高的 \(K\) 个，并按 gate 权重合并其输出。

为什么看似简单的 router 能工作？课程给出的经验是：专家未必自然对应“医学专家”“法律专家”等人类可命名的领域；它们往往只是在 token 模式、语言、标点、频率或隐空间方向上形成分工。因此，不应把 expert specialization 过度拟人化。

### 2. 共享专家与细粒度专家

DeepSeek MoE 的重要设计是：

- **shared experts**：对所有 token 始终激活，负责普遍、共享的计算；
- **routed experts**：由 router 条件激活，负责可分化的计算；
- **fine-grained experts**：把大专家拆得更细，让路由有更细的组合粒度。

共享专家把每个 token 都需要的通用变换从竞争性路由中移出，使 routed experts 更容易专门化。课程引用的消融结果表明：细粒度划分和共享专家通常都有收益。

### 3. 负载均衡：MoE 训练的必要条件

只优化主训练损失时，router 很容易把大量 token 送往极少数专家：热门专家不断得到更多梯度，形成正反馈；其余专家几乎不训练，参数被浪费。

因此需加入负载均衡辅助损失（load-balancing auxiliary loss），使 token 分配更均匀。它不是锦上添花：课程中的消融显示，移除后训练损失变差，且绝大多数 token 会塌缩到少数 expert。

需要理解的张力：

- 主损失希望 token 去“最有用”的 expert；
- 均衡损失希望 expert 使用更均匀；
- 好的训练配置是在二者之间找到可用的平衡。

DeepSeek V3 等工作尝试用 per-expert bias 的在线调整等方法弱化或替代显式辅助损失，但极端失衡仍须被控制。

### 4. 系统问题：expert parallelism

专家常分布在不同 GPU 上。token 经 router 选择专家后，需要 all-to-all 通信把 token 发到对应设备，再把结果聚合回来。

这意味着 MoE 的真实瓶颈不只是专家 FLOPs：

- 单个 expert/token 负载不均会造成 straggler；
- 跨设备路由与通信成本会抵消部分稀疏计算收益；
- 因而还可能需要 device-level routing / communication balancing 等系统层面的目标。

**结论：训练大模型既是深度学习问题，也是系统问题。**

### 5. 数值稳定性

路由中包含 `top-k + softmax`。softmax 在低精度训练中是风险点；MoE 又额外引入了一次 softmax，因此 router 的数值稳定、容量控制与实现细节不能被当作普通 glue code 忽略。

### 6. DeepSeek MoE 的演进（课程案例）

| 版本 | 课程强调的设计点 |
|---|---|
| DeepSeekMoE V1 | 细粒度专家 + 共享专家 + top-k 路由 + 辅助均衡损失 |
| DeepSeek V2 | 扩大专家规模；加入设备路由与通信均衡，直接把系统效率纳入设计 |
| DeepSeek V3 | 延续共享/细粒度思路；探索弱化辅助损失的均衡方式，以及 sigmoid + softmax 等路由变体 |

讲座还介绍了 V3 的两个相关思想：

- **MLA（Multi-head Latent Attention）**：先把隐藏状态投影为较低维 latent，再由 latent 生成 Q/K/V；推理时缓存 latent \(C\) 而非完整 K/V，从而节省 KV cache。RoPE 与这种压缩的兼容需要额外处理。
- **MTP（Multi-Token Prediction）**：一次预测多个未来 token。除可能增强训练信号外，也可为推理中的 speculative decoding 提供结构上的支持。

---

## 本讲应能回答的问题

1. 为什么长上下文下 attention 会从次要成本变为主要成本？
2. FlashAttention 为什么不改变 \(O(n^2)\)，却依然重要？
3. 如何从 \(QK^\top V\) 的结合律得到线性注意力与 RNN 状态视角？
4. Mamba-2 / Gated DeltaNet 中，遗忘门和写入门分别解决什么问题？
5. MoE 为什么能增加总参数量却不按比例增加每 token FLOPs？
6. top-k routing 为什么必须配合 load balancing？
7. 为什么 expert parallelism 使 MoE 成为通信与调度问题？

## 建议的复习与动手任务

1. 手算形状：令 \(Q,K\in\mathbb{R}^{n\times d_k}\)、\(V\in\mathbb{R}^{n\times d_v}\)，分别写出 \((QK^\top)V\) 与 \(Q(K^\top V)\) 的中间张量形状和复杂度。
2. 在小型 PyTorch 实验中，比较标准 causal attention 与一个不带 softmax 的线性状态实现；观察二者的输出差异与内存规模。
3. 实现 toy MoE：4 个小 FFN、top-2 router，并记录每个 expert 的 token count；分别在有/无均衡损失时观察是否发生 collapse。
4. 阅读时优先关注：Mamba-2、Gated DeltaNet、DeepSeekMoE、DeepSeek V2/V3 的架构与系统部分。

## 术语表

- **context window**：模型一次可读取的 token 序列长度。
- **KV cache**：自回归推理中缓存历史 key/value，避免每步重新计算。
- **state-space model (SSM)**：以固定大小状态递归地表示序列历史的一类模型。
- **expert**：MoE 中可被条件激活的子网络，通常为 FFN。
- **router / gate**：决定 token 应激活哪些专家的轻量网络。
- **load balancing loss**：避免路由塌缩、促进专家利用均衡的辅助损失。
- **expert parallelism**：将不同专家放到不同设备上执行的并行方式。
