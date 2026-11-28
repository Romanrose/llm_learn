> **指定阅读导读（Reading-based）**：依据课程官网所列论文整理，不是课堂笔记复原或课堂逐字稿；未获得本讲录像或幻灯片。使用本次获取的论文版本，可能包含授课日期之后的修订，不能视为讲师在 Autumn 2025 课堂讲述的内容。PDF 文本提取可能遗漏图表或破坏公式/双栏顺序；来源与输入节选范围见 sources.yaml。

# CS329A 阅读笔记：Agentic Frameworks for Software Engineering（第 13 讲指定阅读）

> 说明：本笔记只依据三篇官方指定论文的提取文本撰写，属于**阅读导读**，不是课堂讲义复原。文中反复区分【论文主张/实验】与【解释】；所有数值均来自提取正文或表格，表格若在提取中损坏则不引用其数值。三篇论文 PDF 版本（arXiv v1/v2/v4）可能晚于课程讲授时间，本文**不声称**任何结果在 2025 年秋季课堂上讲过。未提供的附录、图表与超参数细节一律保留不确定性。

---

## 一、学习目标

读完这三篇论文，你应当能够：

1. **说出“测试时算力扩展（test-time compute scaling）”在软件工程任务中的两种基本形态**：串行（serial，多轮迭代、依据执行反馈修正）与并行（parallel，多次独立采样），并解释二者为何在“候选生成—候选选择”框架下互相耦合。这一点在 CodeMonkeys 中被明确建模为 Context / Generation / Selection 三个子任务【论文主张】。
2. **理解“覆盖率高 ≠ 最终分数高”**：并行采样提升 coverage（至少一个候选正确的比例），但最终得分取决于选择方法能否从候选中挑出正确解。CodeMonkeys 用 random / oracle 选择作为上下界来量化选择方法的差距【论文主张/实验】。
3. **理解领域专用接口（DSL / Agent-System Interface）如何降低 LLM 生成系统级代码的难度**：Wei et al. 主张用声明式 DSL 抽象底层 C++ mapper 代码，并配合 AutoGuide 把原始执行输出转成可操作反馈【论文主张】。
4. **理解“正确性 + 性能”双轴评估的设计**：KernelBench 提出 fast_p 指标，把功能正确与相对 PyTorch 基线的加速比阈值 p 合并为一个可调指标【论文主张】。
5. **批判性地看待三类证据**：单系统端到端分数（CodeMonkeys）、基准+消融（KernelBench、Wei et al.），以及各自的局限（成本、硬件依赖、选择瓶颈、训练数据低资源等）。

---

## 二、三篇论文的方法比较

### 2.1 任务与问题设定

| 维度 | CodeMonkeys（arXiv:2501.14723） | KernelBench（arXiv:2502.10517） | Wei et al.（arXiv:2410.15625） |
|---|---|---|---|
| 任务对象 | SWE-bench Verified 的真实 GitHub issue | 250 个 PyTorch ML 工作负载，要求生成高效 CUDA kernel | Legion 任务式并行程序的 mapper（任务/数据到处理器/内存的映射） |
| 输出 | 代码库编辑（aider 风格 diff）+ 测试脚本 | `ModelNew`（内联 CUDA 的自定义 kernel） | DSL 写成的 mapper 代码 |
| 反馈信号 | 测试脚本执行反馈、生成测试的通过/失败投票 | 编译错误、执行正确性、profiler 计时 | 原始执行输出，经 AutoGuide 解释与建议 |
| 评估核心 | SWE-bench Verified 解决率（%）与 USD 成本 | fast_p：正确且加速超过阈值 p 的比例 | 归一化吞吐（相对专家 mapper）、迭代次数 |

【解释】三者共同点是“LLM 生成 + 系统执行反馈 + 迭代优化”，但抽象层不同：CodeMonkeys 在**仓库级软件工程**上做多轮状态机；KernelBench 在**单 kernel 性能**上做一次性/重复采样/迭代精炼的对照实验；Wei et al. 在**系统代码生成**上引入 DSL 作为“搜索空间 + 可编译抽象”。

### 2.2 方法骨架对比

**CodeMonkeys**【论文主张】把解题拆成三步：(1) Context：用本地 Qwen2.5-Coder-32B-Instruct 扫描每个 Python 文件判断相关性，再用 Claude 3.5 Sonnet 做文件排序，平均得到约 74,570 tokens 上下文，相对“所有被评估文件”平均压缩 50.5 倍；128k 限制下 92.6% 实例的正确文件在上下文中。(2) Generation：测试状态机先迭代出能复现 issue 的测试脚本，编辑状态机再迭代出 diff，并允许“双边调试”（测试需 pre-edit 失败、post-edit 通过）；每个实例跑 10 对状态机、每个状态机最多 8 轮。(3) Selection：10 个候选先按“通过生成测试数”过滤到 top-3，再用选择状态机写新测试区分候选并做最终选择。

**KernelBench**【论文主张】提供 250 任务、三级难度（Level 1 单算子 100 个、Level 2 算子序列 100 个、Level 3 完整架构 50 个），输入是 PyTorch `Model` 与固定输入形状，输出是 `ModelNew`；正确性用 5 组随机输入比对，性能用 100 次计时取均值，指标 fast_p = 正确且 speedup>p 的任务比例。论文比较 one-shot、重复采样（fast_p@k）、迭代精炼（G / G+E / G+E+P 反馈）三种测试时策略。

**Wei et al.**【论文主张】提出 Agent-System Interface：DSL 用声明式语句表达 Task / Region / Layout / IndexTaskMap 等映射决策，编译到 C++ API；AutoGuide 通过关键词匹配把原始输出转成“解释 + 建议”。优化采用生成式优化（Trace / OPRO 框架），与仅用标量奖励的 OpenTuner（强化学习自动调优）对比。

---

## 三、核心机制

### 3.1 CodeMonkeys：状态机 + 投票 + 选择状态机

- **串行扩展的载体是状态机**：模型每轮拿到执行反馈，可改写或“批准”并终止【论文主张】。论文明确指出串行扩展是“间接的”——模型可提前批准，卡住的状态机无法靠加迭代上限挽救；而并行扩展总可以“加一条新轨迹”保证新起点【论文主张/解释】。
- **成本结构**【实验，Table 1】：全量 SWE-bench Verified 约 2291.90 USD，其中 relevance 334.02（14.6%，本地 8×L40S 估算）、ranking 19.92、gen tests 439.99、gen edits 1366.02（59.6%）、selection 131.95（5.8%）。【解释】这说明“并行摊销上下文成本”是该设计的核心经济动机：扫描一次、十次编辑共用。
- **选择方法的四级对比**【实验，Figure 6】：random 45.8%、majority voting with tests 53.0%、model selection 52.0%、model selection after top-3 55.6%、selection state machine after top-3 57.4%；oracle（=coverage）69.8%。【论文主张】选择状态机“收回”了 random 与 oracle 之间约一半差距。
- **Barrel of Monkeys**【实验】：把 CodeMonkeys 的编辑与 SWE-bench Verified 排行榜前四名提交（Blackbox AI Agent、CodeStory、Learn-by-interact、devlo，截至 2025-01-15）组成 5 样本集成，coverage 80.8%，选择后 66.2%，高于集成中最好的单体 62.8%；随机选该集成为 60.9%。论文提醒 coverage 的 pass@5 与 o3 的 pass@1 不可直接比较【论文主张/限定】。
- **DeepSeek-V3 附录**【实验】：在 100 实例子集上，Claude Sonnet 3.5 得 45.74%，比 DeepSeek-V3 最好分高 6.02%，但 DeepSeek API 便宜一个数量级以上；coverage 随算力继续上升。

### 3.2 KernelBench：双轴指标与三类测试时策略

- **fast_p 定义**【论文主张】：fast_p = (1/N)·Σ 1(correct_i ∧ speedup_i > p)，fast_0 即正确率。【解释】这解决了“少量极快正确解”与“大量慢但正确解”不可比的问题，也让基准可随模型进步调高 p。
- **One-shot 结果**【实验，Table 1，L40S，fast_1 对 PyTorch Eager】：GPT-4o 4%/5%/0%（L1/L2/L3）、OpenAI o1 10%/24%/12%、DeepSeek V3 6%/4%/8%、DeepSeek R1 12%/36%/2%、Claude 3.5 Sonnet 10%/7%/2%、Llama 3.1-70B 3%/0%/0%、Llama 3.1-405B 3%/0%/2%。【论文主张】前沿推理模型最好但整体仍弱，匹配 PyTorch 基线的案例不足 20%。
- **失败模式**【实验，Figure 2】：推理模型（o1、R1）执行失败更少（不正确解 <55% vs 其他 >70%），但功能正确性问题各家类似。【解释】即“能编译”与“算得对”是两道关。
- **重复采样 vs 迭代精炼**【实验，Table 2，预算 10 次调用】：迭代精炼在 6 个案例中 5 个更有效；DeepSeek-R1 Level 2 加 G+E+P 后 fast_1 从 36% 升到 72%；DeepSeek-V3 Level 2 重复采样 k=100 时 fast_1 达 37%（one-shot 4%）。论文也报告 DeepSeek-V3 对一组 34 个卷积变体即使 100 采样也从未正确【论文主张/限定】。
- **硬件知识实验**【实验】：few-shot 优化示例会让 o1 生成更长（平均 +25%）但执行失败更多，整体 fast_1 下降；o1 在 77% 的 GEMM 变体上使用 tiling 但仍慢于 PyTorch Eager；R1 对约 50% 的 Level 1 矩阵乘尝试 wmma 指令但多数编译失败。硬件规格信息对 Llama 3.1 70B / DeepSeek-V3 影响不显著。
- **个案加速**【实验，附录 D】：对角矩阵乘法 13×、GELU 融合 2.9×、Softsign 1.3×、matmul+div+sum+scale 融合 2.6×、cosine similarity 2.8×、triplet margin 2.0×（原文 1.9× 出现在摘要性表述处，按正文表格/小节为准）、ReLU-attention 融合 1.9×。【解释】这些是“存在性证明”，不是平均能力。

### 3.3 Wei et al.：DSL + AutoGuide + 生成式优化

- **DSL 的作用**【论文主张】：声明式表达映射决策（processor selection、memory placement、layout、index mapping），编译到 C++；平均减少 14× 代码行；DSL 在 LLM 训练语料中低资源，但生成成功率更高。
- **代码生成成功率**【实验，Table 2，10 个映射策略】：C++ 单次 0%、DSL 单次 80%；C++ 迭代精炼 0%、DSL 迭代精炼 100%。【解释】这支持“语义鸿沟 + 代码量”两个解释机制，但样本仅是 10 个策略，外推需谨慎。
- **优化效果**【实验】：9 个基准（Circuit、Stencil、Pennant + Cannon's、SUMMA、PUMMA、Johnson's、Solomonik's、COSMA），10 轮迭代下最佳 mapper 全部匹配或超过专家 mapper，最高 1.34×（Circuit，源于把两个数据集合放入 GPU FrameBuffer 而非 ZeroCopy）；COSMA 上 1.31×（更优 index mapping 降低跨 GPU 通信）。Trace 10 轮比 OpenTuner 1000 轮快 3.8×；同为 10 轮时快 11×。每应用优化约 10 分钟，把“数天”降到“数分钟”【论文主张】。
- **AutoGuide 消融**【实验，Figure 6】：0-shot / 5-shot 最差；Execution < Execution+Explain < Execution+Explain+Suggest，全反馈最好。【解释】性能提升来自迭代工作流设计，而不只是提示词。
- **统计细节**【实验，Table A1】：Trace 在 SUMMA/PUMMA/Solomonik 上方差大（均值 0.86×/0.57×/0.52×，最好 1.09×），说明“报告最好一次”的合理性依赖于离线多次运行；论文明确说明 mapper 可复用、搜索是一次性成本。

---

## 四、评估与局限

### 4.1 评估设计上的共性

- 三篇都依赖**可自动执行的验证信号**（仓库测试、随机输入比对+计时、运行时吞吐），因此评估可复现性强；但也因此**只覆盖“可被程序化验证”的正确性与性能**，对可维护性、可读性、安全性无评估【解释】。
- 三篇都区分**“能生成”与“能选中/能变快”**：CodeMonkeys 用 coverage vs score；KernelBench 用 fast_0 vs fast_p；Wei et al. 用生成成功率 vs 归一化吞吐。

### 4.2 各自的局限【论文自述 + 解释】

**CodeMonkeys**
- 上下文阶段仍有 7.4% 实例漏掉相关文件；文件级 recall 以官方补丁编辑的文件为准，不覆盖替代解【论文主张/限定】。
- 选择只收回约一半差距；Barrel of Monkeys 上收回比例更小；未利用仓库既有测试套件（论文点名 Agentless 与 Gemini 团队用了）【论文主张】。
- 生成多样性仅靠正温度采样，状态机之间互不知晓，可能冗余；串行扩展受“模型提前批准”限制【论文主张】。
- 成本约 2300 USD/全量 Verified，且依赖 Claude API 价格与本地 GPU 估算（附录 C 用 RunPod 8×L40S $8.24/小时、20% 利用率等假设）【实验/假设】。【解释】跨时间、跨供应商的可比性有限。

**KernelBench**
- 正确性用 5 组随机输入，程序等价性本质不可判定（论文引 Halting Problem 讨论），未来可探索形式化验证【论文主张】。
- 评测限于 NVIDIA GPU（主用 L40S），跨硬件泛化有限：DeepSeek R1 Level 2 在 L40S 上 fast_1 36%、A10G 上 47%【实验】。
- torch.compile 基线在小 kernel 上有可复现的运行时开销，因此主分析用 PyTorch Eager；不同 compile 配置结果差异大（Table 4）【论文主张/限定】。
- CUDA 在 The Stack v1.2 中仅 0.073%，属低资源语言，这是失败的重要假设性原因【论文主张/解释】。
- 迭代精炼实验用 temperature=0，作者自述这是“聚焦反馈效果、牺牲多样性”的局限【论文主张】。

**Wei et al.**
- 评测用 gpt-4o-2024-08-06、单节点 2×Intel 10 核 E5-2640 v4 + 4×P100，基准仅 9 个；DSL 表达力“目前未遇到无法表达的最优 mapper”，但这是作者经验陈述，非形式化保证【论文主张/限定】。
- AutoGuide 用关键词匹配实现，鲁棒性依赖输出模式【论文主张】。
- 报告“最好一次”结果，同时给出均值/方差（Table A1），读者需自行判断部署场景【解释】。

### 4.3 横向比较的注意事项【解释】

- 三篇的“迭代”含义不同：CodeMonkeys 是带终止条件的多轮状态机；KernelBench 的迭代精炼是固定轮数、温度 0；Wei et al. 是生成式优化框架内的 10 轮。不能把“轮数”直接换算成算力或效果。
- 三篇的“选择”难度不同：CodeMonkeys 有 10 个同分布候选需选择；KernelBench 的 fast_p@k 是 oracle 式“有任一正确即可”，回避了选择问题（论文也明确 fast_p@k 是覆盖式指标）；Wei et al. 把“选最好 mapper”交给离线多次运行。
- 数值不可跨论文拼接：SWE-bench 解决率、fast_1、归一化吞吐是三种不同量纲。

---

## 五、复习清单

**概念核对**
1. 用一句话定义 serial vs parallel test-time compute，并各举 CodeMonkeys 中的一个实现载体。
2. 解释 coverage、oracle selection、random selection 三者关系；CodeMonkeys 的 69.8% / 57.4% / 45.8% 分别对应什么。
3. 为什么 CodeMonkeys 要先做“生成测试投票”再做“模型选择”？论文中哪个对比支持这一顺序（52.0% vs 55.6%）？
4. 写出 fast_p 公式，说明 fast_0 的含义，以及为什么需要可调 p。
5. KernelBench 三级任务各是什么？各 100/100/50 的依据是什么（原语操作数量）？
6. Wei et al. 的 DSL 四个核心语句（Task / Region / Layout / IndexTaskMap）各控制什么决策？
7. AutoGuide 的 Explain 与 Suggest 分别解决什么问题？消融中哪一档最好？

**证据核对（只引用论文给出的数）**
8. CodeMonkeys 总成本约多少 USD？占比最大的阶段是哪个？relevance 阶段为何能摊销？
9. KernelBench one-shot 中 o1 与 R1 在 Level 1/2/3 的 fast_1 各是多少？哪一级最难？
10. KernelBench 迭代精炼 10 轮、预算与重复采样相同的前提下，6 个对比里几个更优？
11. Wei et al. 中 DSL vs C++ 的单次与迭代精炼成功率各是多少？最高加速比出现在哪个基准、多少倍？
12. Wei et al. 的 Trace 10 轮 vs OpenTuner 1000 轮的相对加速是多少？

**批判性思考**
13. 如果 CodeMonkeys 把 10 条轨迹增加到 20 条，coverage 与最终分数可能如何变化？论文对“串行/并行可互换性”的限定是什么？
14. KernelBench 的 5 组随机输入是否足以判定正确性？论文自己如何讨论这一限制？
15. Wei et al. 报告“最好一次”是否合理？Table A1 的方差如何影响这一主张的说服力？
16. 三篇论文各自没有评估什么（可维护性、安全性、跨硬件、跨模型供应商）？这对“agentic framework for software engineering”的整体图景意味着什么？

**不确定性与边界（写作时须保留）**
17. 提取文本未包含 CodeMonkeys 全部附录（如 B.1 完整提示词、Figure 2 的具体子任务数值图）、KernelBench 部分附录（D.4 之后的迭代精炼示例、部分图表）、Wei et al. 附录 A.5–A.8 的细节；引用这些内容时应标注“未在提取范围内”。
18. 三篇论文的 arXiv 版本日期（CodeMonkeys v2 2025-02、KernelBench v1 2025-02、Wei et al. v4 2025-05）不构成“2025 秋课堂讲授内容”的证据；本笔记不主张任何课堂细节。

---

## 六、官方指定链接

1. https://arxiv.org/abs/2501.14723 —— CodeMonkeys: Scaling Test-Time Compute for Software Engineering
2. https://arxiv.org/pdf/2502.10517 —— KernelBench: Can LLMs Write Efficient GPU Kernels?
3. https://arxiv.org/abs/2410.15625 —— Improving Parallel Program Performance with LLM Optimizers via Agent-System Interfaces
