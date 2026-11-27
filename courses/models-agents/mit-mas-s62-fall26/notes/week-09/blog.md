# 模型演化（二）：从自蒸馏到自我对弈——LLM 持续学习的训练环路与基础设施

> 基于官方幻灯片整理，并非课堂逐字稿；未核验课堂口头讲述。本文只依据两份官方幻灯片（week-09 的 lec6「RL & Self-Distillation in Practice」与 lec7「LLM Self-Play」）抽取的文本展开，不补充幻灯片之外的实验细节、参考文献或作业要求；凡幻灯片本身未给出、或因提取缺失而无法确认的内容，均明确标注为不确定。

## 一、主线：模型如何"自己教自己"

本周两次课表面上主题不同：lec6 讲强化学习（RL）与自蒸馏（self-distillation）在实践中的训练环路（training loop）与工程基础设施，lec7 讲 LLM 自我对弈（self-play）。但把两份材料并读，会发现它们围绕同一条主线：**在缺少（或不足以支撑）外部监督信号时，模型能否从自身产生的数据中获得可用的学习信号，以及这种"自给自足"的学习在什么条件下成立、在什么条件下失效。**

lec6 给出的答案是"可以，但要看清信号的形式"：RL 每个 episode 只给 O(1) 比特的信息，而 on-policy distillation 每 token 给 O(N) 比特。lec7 则把这个视角推到自我对弈：proposer 生成问题、solver 求解、verifier 验证，三者中越来越多环节由 AI 承担。最后一节"Generation Verification Gap"（生成—验证差距）为整条主线提供了理论边界：自我提升要成立，需要可改进的生成、验证优于求解的差距，以及高保真的模型更新。

下面按"训练信号的形式 → 训练环路与工程 → 自我对弈的三种范式 → 验证的角色"组织。

## 二、回顾：PPO/GRPO、OPD 与自蒸馏

幻灯片把 LLM 当作策略（policy）：每个 token 是一个动作，prompt 为 $x$，状态 $s_t=(x, y_{<t})$，奖励只在结尾给一次。以"What is 5 + (2 × 3)?"为例，错误答案 21（正确应为 11）得到 $r=0$。策略梯度损失为 $L(\theta)=-\sum_t A_t \log \pi_\theta(y_t|s_t)$；PPO/GRPO 在实践中加上重要性比率 $\rho_t=\pi_\theta/\pi_{old}$ 与 clip 项。两者差别在 advantage：PPO 用学习到的 value model 做 GAE，$A_t=Q(s_t,y_t)-V(s_t)$；GRPO 对同一 prompt 的 G 个答案做组内标准化 $\hat A_i=(r_i-\text{mean}(r))/\text{std}(r)$，不需要 $V$。

**On-policy distillation（OPD）** 换掉了 advantage 的来源。学生先自己采样 $y\sim\pi_\theta$，教师对每个 token 打分，学生朝教师移动。逐 token 的 reverse KL 为 $\mathrm{KL}(\pi_\theta\|\pi_T)=E_{y_t\sim\pi_\theta}[\log\pi_\theta(y_t|s_t)-\log\pi_T(y_t|s_t)]$，其梯度可写成策略梯度形式，$A_t=\log\pi_T(y_t|s_t)-\log\pi_\theta(y_t|s_t)$（利用 $E[\nabla\log\pi_\theta]=0$）。于是 OPD 的教师是另一个更大的模型（如 Qwen3-32B 教 Qwen3-8B）；**自蒸馏**的教师则是"模型自己 + 上下文 $c$"：教师读 $(c, x, y_{<t})$，给出 $\mathrm{sg}[\pi_\theta(y_t|c,x,y_{<t})]$，$A_t=\log\pi_\theta(y_t|c,s_t)-\log\pi_\theta(y_t|s_t)$。幻灯片列出 $c$ 的三种形态：demo（SDFT）、solution（OPSD）、feedback（SDPO）。这里的关键机制是 stop-gradient：教师是被冻结的打分者，学生是待更新的策略，否则"自己教自己"退化为恒等。

需要区分幻灯片内容与解释：以上公式与 $c$ 的分类均直接来自幻灯片；"stop-gradient 防止退化"是我对 $\mathrm{sg}[\cdot]$ 记号含义的解读，幻灯片本身只写了"$c$ only: without it, teacher = student → no signal"。

## 三、RL vs OPD：信息密度是第一性差异

幻灯片用一张对照表把两者放在同一损失形式下：$L(\theta)=-\sum_t A_t\log\pi_\theta(y_t|s_t)$ 相同，差别全在 $A_t$。RL 的 $A_t=r-\text{baseline}$，是整个回答共用的一个数；OPD 的 $A_t=\log\pi_T-\log\pi_\theta$，是逐 token 的一个数。因此信息量：RL 每个 episode 约 O(1) 比特，OPD 约 O(N) 比特（N 为 token 数）。学习目标：RL 朝高奖励走（可能被 hack），OPD 朝教师走（以教师为天花板）。

这张表也解释了 lec6 嘉宾 Idan Shenfeld 的工作线索（幻灯片人物简介页）：其 RL's Razor 表明 on-policy RL 比监督微调遗忘更少，因为更贴近原模型；后续 Self-Distillation Enables Continual Learning 把这一观察变成不需要奖励的方法——prompt 里给一个示范，模型成为自己的教师。幻灯片还提到 Cursor 已用自蒸馏训练 Composer 2.5。这些是幻灯片陈述，本文不额外核验其数值。

**OpenClaw-RL** 展示了两种信号的组合：同一批回答上，① 一个 judge 读回复给好/坏，$r=-1$ 对答案每个 token 相同；② 同一 judge 把回复转成 hint $h$（"explain each step"），同一模型带 $h$ 作教师，$A_t=\log\pi_\theta(y_t|h)-\log\pi_\theta(y_t)$ 逐 token。损失 = ① + ②，一次更新完成。幻灯片的一句话总结很精炼：① 给每一轮一个分数，但只是一个数；② 指出该改哪些 token，但只在回复带有纠正时才有。

## 四、一次训练步：rollout 与 trainer 为何分居两地

幻灯片把一次训练步拆成五段：① rollout（vLLM/SGLang 推理引擎，每 prompt 采 n 条回答）→ ② reward（verifier、测试或 judge，每条一个分数）→ ③ advantage（逐 token，$A_t=r-\text{baseline}$，PPO 另需 critic $V$）→ ④ update（FSDP/Megatron 训练器）→ ⑤ weight sync 回推理引擎。参考模型（frozen start model）提供 KL penalty 的锚点。

"模型为什么住在两个地方"的答案：生成需要快速的 KV-cache 引擎，训练需要梯度和优化器状态，因此每次更新后都要复制权重。幻灯片给出量级对比（以 Qwen3-8B、8.2B 参数为例）：推理侧权重 bf16 每参数 2 字节 ≈ 16 GB，另加 KV cache（约 0.15 MB/token，占用剩余显存）；训练侧每参数需 weights 2 B + grads 2 B + fp32 权重副本 4 B + Adam 的 momentum 4 B + variance 4 B = 16 B，约 130 GB，再加 activations，超过单张 80 GB GPU。这些数字是幻灯片给出的估算，用于说明量级而非实测。

**batch 层级**也值得记住：$B=1024$ prompts、$n=5$ 回答/prompt → 一次 rollout 共 5120 条回答；mini-batch $M=256$ prompts，故 $B\div M=4$ 次优化器 step；8 卡数据并行下每卡 160 条；micro-batch $m=4$ 只是为放进显存，160÷4=40 次梯度累积。幻灯片提了一个判断题：mini-batch 1 与 2 哪个是 on-policy？答案只有 1——第一次更新后 $\pi_\theta\neq\pi_{old}$，后续 mini-batch 的数据已非当前策略所采。这是理解"on-policy"严格含义的好例子。

## 五、损失里的熵与 KL，以及该盯哪些曲线

幻灯片把损失拆成三项：policy gradient 项 $-\min(\rho_tA_t,\ \text{clip}(\rho_t,1-\epsilon,1+\epsilon)A_t)$（clip 限制单步幅度）；KL 到冻结模型 $+\beta\,\mathrm{KL}(\pi_\theta\|\pi_{ref})$（推理 RL 通常关闭，RLHF 开启）；熵项 $-\alpha H(\pi_\theta)$（通常关闭，但要一直看曲线，接近 0 意味着停止探索）。

以"数学推理 RL"为例的示例运行（幻灯片注明是 verl 公开基线：Qwen2.5-Math-7B、GRPO 变体、AIME 2024，并给出公开 W&B 链接），幻灯片用三组"正常 vs 红旗"描述曲线：奖励应慢起后稳步上升，若从一开始就平坦说明无信号；验证指标应随奖励上升，若奖励升而验证降则是过拟合/奖励 hack；熵应保持在 0 以上，若趋近 0 是坍缩；回答长度随推理变化，若卡在最大长度说明被截断；KL 小而稳（此处约 1e-4），若尖峰说明单步走太远；梯度范数先高后稳，若尖峰或 NaN 则不稳定。**注意**：这些是幻灯片对曲线的定性描述与一个公开 run 的示例，不是本文复现的实验结论。

## 六、从 verl 到 reef：数据集训练 vs 在线学习

verl 侧，你写的东西很少：① 任务转 parquet（每行一个 prompt，含 reward_model 的 ground_truth）；② 一个 reward 函数（如抽取答案后与 ground truth 比较返回 0/1）；③ 一条启动命令，用 override 覆盖配置（GRPO、batch 1024、Qwen3-8B、vLLM、n=5、mini-batch 256、8 卡等，与上一节数字一致）；④ 看曲线；⑤ 导出：`verl.model_merger merge` 把 FSDP 分片合成 Hugging Face 格式，再用 vLLM 服务。幻灯片还给出 `PPOTrainer.step()` 的简化伪代码，与五段式一一对应，并注明"简化"。

**verl vs reef** 的对比是本周向"自演化 agent"过渡的关键：verl 是"先训练、后部署"——固定 prompt 集与标签，trainer 做 rollout→reward→update 若干步，产出 checkpoint 再单独导出部署；reef 是"边服务边学习"——面对活流量（用户与 agent 的请求、回复、反馈），同一系统内 Serve / Train / Evaluate 三职能并存，新版本无需重启。幻灯片的一句话定义：verl 是你准备好数据集上的训练器，reef 是从自身流量中学习的推理服务器。lec6 末尾只给出 reef 的 GitHub 与博客链接，未展开内部机制；本文据此不臆测其实现细节。

## 七、自我对弈：从 AlphaZero 到 LLM

lec7 开篇给出自我对弈的一般定义（引 Zhang+ 2025）：agent 通过与自身的历史版本或并发版本交互，迭代地改进策略。随后用一张"Propose / Solve / Verify"三列表格定位范式：SFT 三者皆人；RL 是人出题、AI 解、人验证；self-play 则是 AI 出题、AI 解、人/AI 验证。这实际上是把 lec6 的"信号从哪来"问题推进了一层：不仅 advantage 可以来自模型自己，**训练数据本身**也可以由模型生成。

**AlphaZero 部分**是幻灯片用约 20 页逐步演示的搜索过程：从状态 S 开始，策略网络 $\pi$ 提议走法 A、B、C 并给出先验；value 网络给出 $V(A)=0.60$、$V(B)=0.78$、$V(C)=0.10$；回传估计值；选择 B 分支展开，F、G 为终局，实际奖励 0.20 与 0.00，故 B 的均值修正为 0.10；再依次展开 A（D 预测 0.85、E 终局 0.40，A 暂估 0.625）、C（H、I 终局 −0.20、−0.40，C 为 −0.30）、D（J、K 终局 1.00、0.80，D 为 0.90，A 修正为 0.73，S 为 0.26）。最后"训练"一步：策略学习 $\pi(S)\to A$、$\pi(A)\to D$、$\pi(D)\to J$；价值学习 $V(S)\to0.26$、$V(A)\to0.73$、$V(D)\to0.90$。这里我按幻灯片页面顺序重述了数值链；幻灯片本身是分页动画式的，各页数值应作为一个整体理解，不宜拆开单独引用。

## 八、竞争式与协作式 LLM 自我对弈

**竞争式（PSV）**：solver 因解出问题得奖励，proposer 因"让 solver 觉得难"得奖励。幻灯片用 Verus（形式化验证代码）与传统 Python 单元测试对比，说明验证的强弱：单元测试只覆盖若干断言，而 Verus 的 spec 用 `ensures` 量化所有下标对，并附 proof。PSV 的流程是 proposer 出题、solver 解、verifier 判，按难度分层（如 ✅✅✅❌ 为 Easy）。结果页给出 Dafny2Verus、MBPP、HumanEval 三个基准上 k=1/5/10 的柱状图，并标注"test-time pass@1 相对 RFT 的提升：+31.17 pp / +32.95 pp / +13.51 pp"。**不确定性说明**：柱状图的具体高度无法从提取文本可靠还原，本文只引用幻灯片明写的提升数字，不推断各方法绝对值。

幻灯片还列了六项相关工作（Language Self-Play、Absolute Zero Reasoner、R-Zero、STP、Self-Challenging Agents、Skill Self-Play），每项给出奖励设计与若干提升数字（如 Absolute Zero 7B-Coder 50.4 vs 44.3；R-Zero Qwen3-4B 49.93 vs 45.01，并注明"无标准 RL-only 对照"）。这些数字是各论文自报，幻灯片原样列出；本文照录但不将其视为可比基准。幻灯片也坦率指出竞争式的问题：proposer 被激励去出"难"题，它确实会——但**不是所有难题都对 solver 的训练有用**。

**协作式（SOAR、Goedel-Code-Prover）**：核心是把 proposer 的奖励改为"学生学得怎么样"。SOAR 的做法：teacher 生成 (q, a)，student 做 10 步 RL，评估学生；teacher 用 RLOO 更新，奖励 = 学生训练后的准确率减去训练前。幻灯片给出 Llama-3.2-3B-Instruct 在 MATH、HARP 上的 test pass@32（如 MATH：Hard-only RL 9.6±2.6 vs SOAR-PQ 18.9±5.3）。幻灯片还用"I CL 直觉"一页连接两个层面：上下文学习在功能上类似梯度下降（引 von Oswald+ 2022 等），因此可问"能否用 ICL 替代内层训练循环"——这正是 Goedel-Code-Prover 一类方法的动机。其结果页给出 Verina(189)、Clever(161)、AlgoVeri(77) 上 8B 模型与三个强基线（BFS-Prover-V2-32B、Goedel-Prover-V2-32B、DeepSeek-Prover-V2-671B）的对比柱状图；同样地，**柱高无法从提取文本核实**，本文只指出幻灯片标注了 68.8%、62.3%、54.0% 等数值与基准名，不重建图表。

## 九、验证的角色：Generation Verification Gap

lec7 最后一节回答"自我对弈何时可预期地有效"。幻灯片先给三个条件：① 可改进的生成（输出有方差）；② GV-Gap（验证强于求解）；③ 高保真的模型更新（能可靠地把模型拟合到被选中的样本）。发现部分：相对 GV-Gap 随预训练 flops 单调增长（生成器与验证器为同一模型时）；当验证器与生成器容量差距增大时，gap 也增大。幻灯片还给出两个机制性提示：工具可以提升验证容量；递归训练会跨代放大错误，不可靠的过滤会让模型强化自身错误，而足够可靠的自验证即使在全合成数据上也能防止坍缩。最后是"锐化机制"（sharpening）：用模型自身的评分信号挑选回答，再训练它更可靠地生成这些回答——把昂贵的推理时选择摊销进权重；但"更好的自评分意味着更好的答案"只在评分信号本身有用时成立。

## 结语

把两周内容接起来看，lec6 回答"信号从哪来、怎么工程化"：RL 的 O(1) 比特与蒸馏的 O(N) 比特之分、自蒸馏用上下文 $c$ 造出教师、rollout 与 trainer 的双居所与权重同步、batch 层级的 on-policy 边界，以及 verl 的"数据集训练"到 reef 的"边服务边学"。lec7 回答"数据从哪来、何时可信"：从 AlphaZero 的搜索—回传—训练闭环，到 PSV 的竞争式出题、SOAR 的"按学生进步给 proposer 发奖励"、Goedel-Code-Prover 的协作式验证，最后落到 GV-Gap 这一判据。两讲共同的告诫是：自演化系统的瓶颈往往不在更新算法，而在**信号的质量与验证的可靠性**——这正是把"模型演化"从口号变成工程时最需要盯着的地方。本文所有数值与结论均以幻灯片文本为限；图表细节与课堂口头补充未纳入。

## 参考（仅输入中给出的官方幻灯片 URL）

- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec6%20-%20rl%20in%20practice.pdf
- https://mit-mi.github.io/how2ai-course/fall2026/schedule/lec7%20-%20self%20play.pdf
