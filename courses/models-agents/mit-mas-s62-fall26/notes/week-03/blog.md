# 把上下文当作可优化对象：MIT MAS.S62 第三讲《LLMs as Context Optimizers》梳理

> 基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。

## 一、主线：从"写提示词"到"优化上下文"

第三讲（Fall 2026 / week-03，Context evolution 2）的标题直接点明立场：**LLM 是上下文优化器（Context Optimizers）**。幻灯片用一条渐进路径展开这条主线：先回顾提示优化（Prompt Optimization），再深入 TextGrad 这类"把 LLM 反馈变成优化信号"的方法，然后转向 LLM for Discovery 与 FunSearch 的拆解，最后以开放挑战收束。

课程对两个基础概念的定义值得先固定下来。幻灯片原文区分：**Context 是模型在生成下一个 token 之前读到的全部内容；Prompt 是你给模型、用来引导其回应的一段输入**。这个区分是整讲的地基——提示只是上下文的一个特例，而"上下文优化"意味着把模型读到的所有东西都当作可迭代改进的对象，而不只是改一句指令。

幻灯片明确给出的演进判断是："LLMs can write high-quality prompts through iterative attempts"，并进一步提出："We can build an agentic system to update useful contexts everytime we solve a problem"。也就是说，优化的单位从"一次性提示"升级为"每次解题后都能被更新的有用上下文"。

**（解释）** 这条主线把"优化"重新定位了：不是人去猜更好的措辞，而是让模型在 propose–evaluate–refine 的循环中改进某个可被读写的外部对象——提示、程序、甚至整个 agent harness。幻灯片第 13 页用一个问句把这一转向说得很清楚：既然已经用 LLM 优化提示，能否用同一个 propose–evaluate–refine 循环去优化别的东西？后续内容基本都在回答这个问句。

## 二、回顾部分：自动提示工程与 agentic context

回顾段落引用了两篇工作作为锚点：Zhou 等人的 *Large Language Models are Human-Level Prompt Engineers*（ICLR 2023），幻灯片标注为 "Automated prompt engineer"；以及 Zhang 等人的 *Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models*（ICLR 2026），对应"Towards Context Optimization"的 agentic 系统设想。两页配图（第 8、10、11 页）在抽取文本中只剩标题与引文，**图示细节无法核验，此处不作推断**。

**（解释）** 这两条引用在叙事上分工不同：前者证明"LLM 自动写提示"在质量上可达人类水平，后者把范围从"写提示"扩展到"演化上下文"。幻灯片没有给出具体算法细节，因此这里只能确认其定位，不能补充方法内容。

## 三、TextGrad 深挖：把反馈变成梯度式的优化信号

TextGrad 部分（第 12–22 页）的展开方式是按"优化对象"逐个举例，每一页对应一类被优化的东西：

- **Self-Refine**（Madaan et al., NeurIPS 2023）：LLM 通过自我反馈做迭代精炼——幻灯片表述为 "LLMs can optimize through self-refine / self-refinement"。
- **LLM as Optimizers**（Yang et al., ICLR 2024）：LLM 利用来自 scorer 的反馈进行优化，两页分别展示该思路与反馈机制。
- **Optimize Writing**：Re3（Yang et al., EMNLP 2022），用递归重提示与修订生成长故事。
- **Optimize Agent Harness**：Meta-Harness（Lee et al., arXiv 2026），端到端优化模型 harness。
- **Optimize Data Visualization**：MatPlotAgent（Yang et al., Findings of ACL 2024）。
- **Optimize Image Generation**：Idea2Img（Yang et al., ECCV 2024），基于 GPT-4V 的迭代自精炼图像设计。
- **Optimize Video Generation**：VISTA（Do et al., arXiv 2025），测试时自改进的视频生成 agent。

**（解释）** 这一串例子的共同结构是"自然语言反馈充当优化方向"：无论是自我批评、外部 scorer、还是多模态评审，反馈都以文本形式回到生成端，驱动下一轮修改。幻灯片没有给出 TextGrad 的形式化定义或损失函数，因此不能把它说成某种具体的"文本梯度"算法——只能确认课程把它作为"用 LLM 反馈优化任意对象"的代表框架，并用应用清单展示其适用范围之广。这也解释了为什么这一节之后紧接着问"那科学发现呢"。

## 四、LLM for Discovery：两个具体成果与问题背景

幻灯片第 23–26 页从"优化对象"切换到"优化能带来什么发现"。第 24 页列出 LLM 驱动搜索在两个任务上的成果：一是在八个维度上发现新的 cap set 构造，把记录从 **496 提升到 512**；二是发现能在所测基准上超过标准基线的 bin-packing 启发式。这是幻灯片中少数给出具体数字的地方，应原样保留。

第 26 页给出两个问题的背景定义：

1. **Cap set 问题**：从 {0,1,2}^n 中最多能选多少点，使得不包含三个共线的不同点？在 8 维情形下，每个点是八元向量（如 (0,2,1,0,1,2,2,0)），需从 {0,1,2}^8 的 **6,561** 个点中尽可能多选，且无三点共线。
2. **Bin-packing 问题**：如何用最少的箱子装入不同大小的物品且不超容量？示例：容量 10，物品 6,5,3,2,2,2，一个合法装法用 3 箱：[6,3]、[5,2,2]、[2]。**在线（online）** 情形下物品逐个到达，必须立即放置。

**（解释）** 这两个问题的共同点是：解空间巨大、难以直接穷举，但"候选解好不好"相对容易评估——这正好适配"LLM 提议 + 评估器打分"的搜索范式。幻灯片选择它们，大概率是为了给 FunSearch 的拆解提供具体载体；但课程并未在此处说明为何偏偏是这两个任务，此处不作推测。

## 五、FunSearch 拆解：在黑箱优化中搜索程序

FunSearch 部分（第 27–33 页）按组件拆解：

- **黑箱优化（Black Box Optimization）**：第 27 页给出这一框架定位。
- **搜索空间（Search Space）**：候选集合。FunSearch 搜索的是**具有给定输入输出格式的 Python 函数**。对 cap set，是 `priority(element, n)`，为下一个要加入的向量排序；对 bin packing，是 `heuristic(item, bins)`，为物品的放置位置排序。**输出是一个可复用的、能构造解的程序**，而非单个解。
- **进化算法（Evolutionary algorithms）**：通过反复的选择、变异与评估改进种群；FunSearch 用 LLM 生成被采样程序的变体。
- **Programs Pool 与探索**：三步——(1) 每个 island 用一个 seed program 初始化；(2) 在 island 内扩大种群：从该 island 已有程序中采样父代，生成子程序并加入同一 island；(3) 移除表现较差的 island。

**（解释）** 这套设计的要点在于"程序即候选"：搜索发生在函数空间，评估发生在由该函数构造出的解上，因此一个高分函数可以被复用、迁移到不同输入规模。island 模型则提供了多样性维护机制——不同 island 独立演化，差的整体淘汰。幻灯片第 33 页在抽取文本中为空页，**该页内容缺失，无法判断是否有补充图示或说明**。

## 六、从 FunSearch 到 AlphaEvolve、Autoresearch 与更广的"自动研究"

第 34 页用对照方式概括 AlphaEvolve 相对前者的扩展，共五组转变：搜索范围从**单函数到全程序演化**；编辑模式采用 **SEARCH/REPLACE diff**；模型使用**更强 LLM 并配更丰富的上下文与反馈**；目标从**单指标到多指标优化**。页面附有 DeepMind 博客链接。

第 35 页介绍 Autoresearch：一个 AI agent 按 `program.md` 提出想法、编辑代码、运行实验，在**固定算力预算**下改进语言模型预训练——幻灯片给出的量级是**每次实验 5 分钟、一晚约 100 次实验**。第 36 页把问题抛给听众："还有哪些问题可以 autoresearch？"第 37 页引用 Zhu 等人的 *EdgeBench: Unveiling Scaling Laws of Learning from Real-World Environments*（2026），但抽取文本仅剩引文，**页面主体内容缺失**。第 38 页为 OpenEvolve 深挖兼 HW1 预览，附 Colab 链接；**作业具体要求未在幻灯片文本中给出，此处不虚构**。

第 39 页是一个重要的提醒：**许多发现并没有数值评分器**。幻灯片列举：生物学（CRISPR 基因编辑）、物理学（广义相对论）、化学（青霉素的发现）、天文学（暗物质）、地质学（板块构造）、医学（mRNA 疫苗）、计算机科学（反向传播）。随后两页转向"LLM 能否产生新颖研究想法"：Si 等人 *Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers*（ICLR 2025），以及 Lu 等人 *Towards End-to-End Automation of AI Research*（Nature 651, 914–919, 2026）的 AI Scientist（两页）。

**（解释）** 第 39 页在论证链上起转折作用：前面所有方法都依赖"可评估"，而科学史上标志性发现恰恰缺少即时评分器。这为下一节的"验证"主题和最后的开放挑战埋下伏笔。幻灯片没有说明这些历史案例与 LLM 方法之间的具体对应关系，不能替它补论证。

## 七、验证为什么重要

验证部分（第 43–46 页）以形式化数学为例：**DeepSeek-V3 把原定理分解为子目标，DeepSeek-Prover-V2-7B 尝试在 Lean 中证明这些子目标**（Ren et al., 2025）。第 44 页标题重复"Verification is important for discovery"，正文缺失。第 45 页引用 Anthropic 关于形式化费马大定理的博客；第 46 页给出一个视频链接。

**（解释）** 这一节的逻辑是：当正确性可以被机器检查（如 Lean 证明器），"发现"就有了可靠信号，优化循环才闭合。反过来，缺少验证器的领域正是难点——这与第 39 页形成呼应。至于视频与博客的具体内容，抽取文本未提供，**不作描述**。

## 八、开放挑战与结语

第 47 页列出三项开放挑战，原文表述清晰，可直接作为收束：

1. **超长上下文带来的分布偏移（Distribution shift from ultra-long contexts）**：随着上下文长度增长，模型行为如何变化？优化与发现方法在这种诱发的分布偏移下有多稳健？
2. **可验证领域之外的真实发现（Genuine discovery beyond verifiable domains）**：当正确性或进展无法被自动评估器轻易验证时，LLM 能否产生真正新颖的发现？
3. **更快的适应（Faster Adaptation）**：模型能否从更少的实验中学习有用的设计原则，从而在更小的实验预算下做出更好的决策与设计？

第 48 页预告下一讲主题："From Memory to Harness"。第 49 页为本周事务通知（选课状态、人数上限 20–30、项目偏好表等），此处仅作事实性提及，不展开。

**结语。** 把整讲串起来看，第三讲的核心主张可以概括为一句话：**优化的对象正在从"提示"扩展为"上下文"，再扩展为"程序与整个研究流程"**。TextGrad 一类工作证明自然语言反馈足以驱动跨模态、跨任务的迭代改进；FunSearch 把候选提升到"可复用程序"的层级，并用进化式种群维护多样性；AlphaEvolve 与 Autoresearch 则把这一范式推向全程序与端到端实验循环。而第 39 页与第 43 页共同划出了边界：没有可靠验证器的地方，"发现"就缺少闭合信号——这正是开放挑战第二条的要害。幻灯片没有声称这条路径已经解决科学发现，它给出的是一张能力地图和三个明确的未解问题；读者若要把这套方法用于自己的问题，第一步应当是问：我的任务有没有一个足够可靠、足够便宜的评估器？

**（解释）** 需要说明的是，本讲多处配图（第 8、10–11、24–25、28–29、33、37、40–42、44–46 页等）在抽取文本中仅剩标题、引文或空页，图示与页面正文的具体内容无法核验；上文凡涉及这些页面的描述，均只基于可读的标题与引文，不对缺失内容作补充。幻灯片中的具体数字（496→512、6,561、容量 10 示例、5 分钟/约 100 次实验、20–30 人上限）均按原文保留。

## 参考来源（官方幻灯片）

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec3%20-%20llm%20optimizers.pdf
