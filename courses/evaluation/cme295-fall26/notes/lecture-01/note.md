# CME 295 Lecture 1：Transformers 课程笔记

## 学习目标

本讲是整个课程的概念地基，目标是让学习者建立一条从「原始文本」到「现代 LLM 输出」的完整心智链条，具体包括：

- 理解为什么需要 **tokenization**，并能在词级、字符级、子词级三种方案之间做出有依据的取舍。
- 理解 **BPE（byte pair encoding）** 作为当今最流行子词分词器的工作机制。
- 理解 **one-hot encoding** 的局限，以及 **word2vec** 如何通过代理任务学到有意义的词表示。
- 理解 **RNN** 解决了词序问题但引入长距离依赖与梯度消失问题。
- 理解 **attention** 与 **self-attention** 的核心直觉：用序列中其他 token 的函数来刻画当前 token 的表示。
- 理解 **query / key / value** 记号与自注意力的矩阵形式公式。
- 理解 **Transformer encoder-decoder** 的组件组合方式，以及 **residual connection**、**layer normalization**、**masked self-attention**、**multi-head attention**、**dropout**、**label smoothing** 各自的作用。

课程明确指出：第一讲是概念数量上最难的一讲之一，觉得信息量大是正常的。

---

## 课程主线

课程的叙事线索是一条「问题—瓶颈—新方案」的链条，而不是架构组件的罗列：

1. **2010 年代**：每个用例一个模型（情感分类、翻译、命名实体识别各一个），主导架构是 RNN。性能尚可，但缺乏可扩展性。
2. **2017 年**：《Attention Is All You Need》引入 Transformer，其范式具有可扩展性——给更多数据、更多算力、更多参数，性能提升远大于以往。
3. 此后从模型规模与训练 token 数量两个方向扩展，现代 LLM 由此诞生。
4. **2022 年**：ChatGPT 发布，从产品角度成为转折点，让大众习惯与聊天机器人交互。
5. **2026 年**：coding agent 被日常使用；课程第二部分将讨论从对话式助手到真正的 **agentic behavior** 的演进。

课程强调这个领域发展极快，今年讲座安排与去年差异很大，新增内容包括 post-training 中的 **policy distillation**、AI agent、以及一次预测一个 token 之外的 LLM 新范式（例如从 **diffusion** 角度出发的方法）。

---

## 核心概念

### 1. Tokenization

模型不理解文本，只理解数字。tokenization 是把文本切成不可再分的单元（**token**），再将每个 token 表示为向量。可用的 token 集合叫 **vocabulary**，切分后的 token 数量叫**序列长度**。词表大小与序列长度之间存在紧密关系，这直接影响分词器的选择。

三种方案及其权衡：

| 方案 | 优点 | 缺点 |
|---|---|---|
| 词级 | 简单（按空格切）、可解释 | 词形变化多导致词表巨大；同词根词（bear / bears）表示不保证相近；存在 **out of vocabulary** 风险 |
| 字符级 | 无 OOV、词表小、对拼写错误鲁棒 | 序列长度大幅变长，而模型复杂度是序列长度的函数，计算变慢；嵌入可解释性差 |
| 子词级 | 利用词根（bear / bears 共享 bear）；从数据中学到 | 需要额外训练工作；分词结果高度依赖分词器训练数据的分布 |

**子词级是当今远最流行的方案**。BPE 的机制：从初始 token 集合（例如字母表）出发，反复识别训练数据中最频繁的 pair，为其合并 token 加入词表，直到达到期望的词表大小。好处是共同出现的片段被识别出来，序列长度变短，效率由此而来。因此若做多语言工作，分词器必须训练在能代表所有目标语言的语料上——固定词表大小会被不同语言的 token 瓜分，只关注单一语言时可能得到更长的序列。

课程给出一个量级参考：当今 LLM 词表大小在数十万量级。

### 2. Special tokens

- **unknown token**：表示词表外的文本片段。
- **BOS / EOS**：主要用于生成任务。输入 BOS 表示「开始生成」，模型输出 EOS 表示生成结束。
- **padding token**：把序列补齐到统一长度，出于效率考虑——硬件偏好维度一致的张量。
- 课程强调这个列表**绝非详尽**，BOS/EOS/padding 的写法也**不是通用约定**；如今还有 user / assistant 等角色 token。

### 3. 从 one-hot 到 word2vec

one-hot 向量两两点积为零（正交），不携带任何关于 token 之间关系的信息。目标是学到**有意义的表示**：teddy bear 应与 soft 相似，Paris 之于 France 如同 Berlin 之于 Germany。

word2vec 通过**代理任务**（proxy task，非最终目标，而是为达成其他目标而学的任务）学习表示：连续词袋版本预测上下文词之间的词，skip-gram 版本预测给定词周围的词。网络结构是 one-hot（大小 V）→ 矩阵乘法 → 隐藏表示（大小 D，通常远小于 V）→ 矩阵乘法 → 词表上的概率（大小 V），用交叉熵损失更新权重。训练完成后，中间学到的**潜在表示**具有有意义的相似度结构。

word2vec 的局限（课程通过提问方式引出）：

- 训练中未遇到的词没有表示。
- 词表变大时维度增大（但这属于所有方法共有的局限，非本方法特有）。
- **同一个词在不同句子中得到相同表示**，无法区分一词多义（bank 河岸 vs. 银行；cute 的真诚用法 vs. 讽刺用法）。
- **词序不重要**：「孩子抱泰迪熊」与「泰迪熊抱孩子」得到相同嵌入。

### 4. RNN 与它的瓶颈

RNN 额外维护一个**隐藏状态**，编码到目前为止所见序列的含义，并作为下一步预测的输入。这使模型能考虑词序，当年广泛用于分类、词性标注、生成等任务。

局限：把整个序列的含义压缩进单一向量，该向量不断被修改，因此难以记住很久以前出现的词，即**长距离依赖**问题（例：「my teddy bear is so cute. It is 3 feet tall.」中 it 指代久远的东西）。**LSTM** 引入 **cell state** 试图更长时间携带信息，但仍受同一问题困扰。更深层根源是**梯度消失**。此外，RNN 必须一个 token 一个 token 地前进才能做下一次预测，训练极其缓慢。

### 5. Attention 与 self-attention

attention 的直觉：不再只依赖隐藏状态封装过去，而是让模型与过去见过的 token 建立**直接连接**，学习哪些 token 重要，并让预测依赖这些重要 token。翻译场景中，预测下一个词时能直接访问源句中对应的词极有帮助，而 RNN 只能通过隐藏状态间接访问。

**self-attention** 是加强版：计算某 token 的表示时，把它表达为序列中**所有其他 token** 的函数。

**Q / K / V 记号**：

- **Query**：当前 token 发出的「我在找什么」的询问，试图确定哪些 token 有助于构建自己的表示。
- **Key**：每个 token 携带的、用于与 query 比对相似度的量。
- **Value**：每个 token 实际被加权聚合的向量。

权重由 query 与各 key 的相似度（如点积）决定，输出是 value 的加权平均。例：计算 teddy bear 的表示时，query 与 cute 的 key 点积可能很高，于是 cute 的 value 在结果中占比很大。

Q、K、V 本身由可学习的**投影矩阵**从输入 token 表示投影得到。

### 6. 自注意力的矩阵形式

课程明确提示：这可能是关于 Transformer 最重要的公式，期中考试有一道相关题目。

将 query 堆成矩阵 Q（n 行），key 堆成 K，value 堆成 V。则 `QKᵀ` 的第 (i, j) 项是第 i 个 query 与第 j 个 key 的点积，得到 n×n 的相似度矩阵；对它做 **softmax** 得到和为 1 的权重分布（负无穷经 softmax 变为零，这正是 masking 的实现原理）；再乘以 V，即得每个位置的加权求和。

完整形式为：

```
Attention(Q, K, V) = softmax(QKᵀ / √d_k) · V
```

除以 √d_k 的原因：d_k 会影响求和过程中的方差，需要归一化以使一切正确缩放。

### 7. Transformer 架构（encoder-decoder）

原论文背景是机器翻译。**Encoder** 为源文本计算有意义的表示；**Decoder** 利用 encoder 的表示与自身内部 embedding 生成译文。

**Encoder 流程**：

1. **Input embedding**：把 token 映射为可学习的 embedding，非上下文感知。
2. **Position embedding**：与 token embedding **相加**，以告知 token 在序列中的位置。两种获得方式：学习式（缺点是遇到比训练时更长的输入就无能为力），或不同频率的正弦/余弦函数（类比手表时针、分针、秒针以不同频率转动，合起来能精确读出时间）。其良好性质是：相近位置表示相似，远离位置表示不相似。
3. **Self-attention layer**：学习投影矩阵把 token 投影到 Q/K/V 空间，按上式交互，从而把 token 表示为其他 token 的函数。
4. **Feed-forward neural network**：把表示投影到更高维空间并配激活函数，以学习非线性。
5. 重复 N 次（原论文 N = 6）。末端每个 token 得到一个上下文感知的、有意义的表示。

**Decoder 流程**（自回归）：

1. 输入 **BOS** token，加位置编码。
2. **Masked self-attention**：每个 token 只看自己和之前的 token，因为不能与尚未解码的 token 交互。
3. **Cross attention**：query 来自已解码内容，key 和 value 来自 encoder 的输出。含义是「我如何把这个 token 表示为输入文本中所有 token 的函数」。
4. Feed-forward network。
5. **Linear + softmax** 投影到词表空间，得到下一个 token 的概率分布。
6. 选取下一个 token（启发式方法在后续课程讨论；本例取最大值），把它作为输入送回 decoder，重复整个流程，直到输出 EOS。

### 8. 关键技巧

- **Residual connection**：层的输出是「x 的某个函数 + x」，而非完全替换 x。可理解为对 x 做修改而非整体改写；在很深架构中有助于反向传播，让模型学得更好。
- **Layer normalization**：对激活值归一化，有助于收敛。
- **Multi-head attention**：用不同投影矩阵并行做多组 Q/K/V（本例 8 组），类比 CNN 中多个 filter 以不同方式卷积输入。各组结果拼接后用 W_O 投影回模型空间。Transformer 的一个良好性质是许多操作保持 embedding 原始维度 D_model 不变。
- **Dropout**：训练时以一定概率有意丢弃单元，避免模型过度依赖某些特征，提升泛化。
- **Label smoothing**：不要求模型 100% 预测目标词，而是例如 90% 给目标词、10% 分给词表其他词。理由是语言中同一句话可以有多种合理续写（"what a nice day / class / ..."）。作者发现这在机器翻译上也能提升指标（课程提到 BLEU 是这类指标之一）。

**维度记号**：序列长度 n；模型维度 D_model；投影矩阵 W_Q、W_K、W_V 形状分别为 (D_model, D_Q)、(D_model, D_K)、(D_model, D_V)；由矩阵乘法约束，D_Q 必须等于 D_K。Q、K、V 均为 n 行。FFN 把 D_model 投影到 D_FF（通常比模型维度更大，以允许学习复杂表示）。多头情形下，最后用 W_O 把 H×D_V 空间的嵌入变回模型空间。

### 9. 究竟是什么让它奏效

课程给出的提炼是：论文标题本身就道出了秘诀——**attention 是核心**。其次是 **feed-forward network**，模型的大部分参数与容量在此，学习主要发生在这里。其余组件是帮助更好学习的技巧。课程还补充：数据质量是另一层面的复杂性。（解释：这一判断与后续课程中「许多组件可被去掉、只反复使用组件子集」的观察相呼应。）

**关于 softmax 的两种用途**：注意力层中的 softmax 是把 query 跨 token 投影到 key 空间上；最后一层的 softmax 是为预测下一个 token。同一个函数，目的不同。

---

## 课程作业与考核关联

- 课程为两学分，可选字母成绩或通过/不通过。
- **无作业**，但有两场考试：期中覆盖前四讲，期末覆盖最后五讲（共九讲），期末占总成绩 50%（即两场考试各占一半）。
- 考试形式为多选题加自由回答题；2025 年度的期中、期末样题已发布在课程网站的 2025 标签页，可用于了解出题预期。练习题存在，但今年题目会不同。
- 考试范围原则：课上讲过的内容都可能考；教材中有但课上未覆盖的主题不会考。
- 复习建议：定期复习效果最好，课上认真听讲最重要。官方**速查表（cheat sheet）** 由两位讲师近期更新，目标是简洁覆盖全部内容，适合考前复习。
- 每张幻灯片底部通常附有来源，供深入查阅。
- 无官方 office hour，但两位讲师每次课后会留下答疑，也可通过 ED 平台提问。
- 幻灯片提前一天发布，便于课上做注释。

**明确的考试提示**：自注意力的矩阵形式公式「可能很重要」，期中考试有一道相关题目。

---

## 常见误区

1. **把 BPE 与 engram 混为一谈**。课程中被问及时明确回答：engram 是另一回事；BPE 是通过迭代合并最频繁 pair 来从语料学习 token，直到达到目标词表大小。
2. **认为 BOS/EOS/padding 的写法是通用标准**。课程反复强调这些只是惯例，不同模型有不同变体（如 user/assistant token），遇到不同写法不必惊讶。
3. **认为 one-hot 是合理的 token 表示**。它使所有 token 两两正交，完全不携带相似度信息。
4. **认为 softmax 在模型中是同一件事**。注意力层的 softmax 与输出层的 softmax 功能完全不同。
5. **混淆「消除词序」与「表示词序」**。朴素地让每个 token 与所有 token 交互确实丢失了词序信息，这正是需要位置编码的原因；课程明确说这是后面才处理的部分。
6. **把分词器视为与任务无关的预处理**。分词结果高度依赖分词器训练数据的分布，必须与最终目标一致；多语言场景尤其如此。
7. **认为 LSTM 解决了长距离依赖**。它只是缓解，课程指出这类变体仍有相同局限。
8. **把 encoder 与 decoder 的注意力混同**。decoder 有两种：masked self-attention（query/key/value 都来自已解码内容）与 cross attention（query 来自解码侧，key/value 来自 encoder）。
9. **以为词表越大越好或越小越好**。词表大小与序列长度是 trade-off，直接影响计算效率与表示质量。
10. **把 Transformer 的成功归于单一组件堆叠**。课程的判断是：注意力机制 + 前馈网络（容量所在）是核心，其余是学习技巧。

---

## 复习清单

- [ ] 能说出词级、字符级、子词级分词的各自优缺点，并解释为什么子词级成为主流。
- [ ] 能描述 BPE 的迭代合并过程，并解释它为何缩短序列长度。
- [ ] 能说明 unknown / BOS / EOS / padding token 各自的用途，并知道这些约定不通用。
- [ ] 能解释 one-hot 为何无法表达相似度，以及 word2vec 的代理任务逻辑与网络各层维度（V → D → V）。
- [ ] 能列出 word2vec 的四类局限（OOV、维度随词表增长、一词多义、词序无关）。
- [ ] 能说明 RNN 的隐藏状态作用、长距离依赖问题、梯度消失根源，以及 LSTM cell state 的意图。
- [ ] 能用自己的话解释 attention 的直觉：与过去 token 建立直接连接，学习哪些 token 重要。
- [ ] 能解释 Q、K、V 各自扮演的角色，以及它们由可学习投影矩阵得到。
- [ ] 能默写 `softmax(QKᵀ/√d_k)·V`，并解释 softmax 的作用、√d_k 缩放的原因，以及负无穷经 softmax 变零与 masking 的关系。
- [ ] 能画出/复述 encoder 的流程：input embedding + position embedding → self-attention → FFN，重复 N 次。
- [ ] 能复述 decoder 的自回归流程，并区分 masked self-attention 与 cross attention 的 Q/K/V 来源。
- [ ] 能说明 residual connection、layer normalization、multi-head attention、dropout、label smoothing 各自解决什么问题。
- [ ] 能说清各维度记号：n、D_model、D_Q = D_K、D_V、D_FF、H，以及 W_O 的作用。
- [ ] 能回答「究竟是什么让 Transformer 奏效」，并知道课程对此的判断及其理由。
- [ ] 能说出考试结构、范围原则与复习资源位置。
