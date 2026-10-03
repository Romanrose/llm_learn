# CMU 11-768 Fall 2026 · Lecture 11 · Training 3: Advanced RL Algorithms 课程学习笔记

> 来源：仅官方 Slides；逐字稿未就绪。内容已由用户审核确认。

> **说明**：本文仅依据 Lecture 11 官方 Slides 的逐页文本提取撰写，尚未获取可用字幕，因此**不是完整课堂记录**，也不包含讲者口述、课堂问答或逐字稿。凡是文本提取无法确认的图示、公式排版或具体数值细节，均在文中标注“待核”。所有页码引用均指官方 Slides 的页码。缺少视频时，本文不提供时间定位。

---

## 一、学习目标

完成本讲后，应能：

1. 说明 RL 训练循环的三个阶段（采样、打分、更新），并写出目标函数 $J(\theta)$（Slides 第 5 页）。
2. 解释 REINFORCE 中最终奖励如何加权每个动作，并指出“失败轨迹无更新”的原因（Slides 第 6 页）。
3. 用组内平均奖励作为基线，说明 GRPO 一类方法为何能让失败轨迹也产生负权重（Slides 第 8 页）。
4. 解释 reward-to-go、值函数 $V_\mu(h)$、TD 误差与 GAE 的递推关系（Slides 第 10–16 页）。
5. 区分同步 RL 与异步 RL 在等待时间上的差异，并说明异步带来的“旧策略数据”问题（Slides 第 19–22 页）。
6. 写出重要性采样比率、整条轨迹比率，并解释为何长轨迹上方差会爆炸（Slides 第 23–26 页）。
7. 比较 PPO、GRPO、CISPO、GSPO、DAPO 在信用分配、加权与裁剪上的差别（Slides 第 27、35 页）。
8. 说明裁剪、参考模型 KL 惩罚、熵奖励各自的作用与副作用（Slides 第 29–34 页）。
9. 识别“无信息 rollout 组”、假阴性、假阳性、奖励黑客、探索崩溃等奖励可靠性问题（Slides 第 37–47 页）。
10. 说明课程、暖启动、蒸馏与 on-policy 蒸馏的基本机制（Slides 第 49–53 页）。

---

## 二、概念主线

本讲的主线是把 RL 基础循环推向“可实际训练 agent”的工程与算法细节。Slides 第 2 页的 RL lecture map 把这一路线标为“Today”，四个关注点是：

- **Useful feedback（有用的反馈）**：如何把最终奖励分配到时序上的具体动作；
- **Less waiting（减少等待）**：如何让 rollout 与学习重叠；
- **Stable updates（稳定更新）**：如何限制单次更新幅度；
- **Reliable rewards（可靠奖励）**：如何确保奖励信号本身可信。

下一讲转向“Memory, parallelism, and execution at scale”（Slides 第 2 页）。

全讲围绕一个统一的例子展开：**修复一个 retry 配置 bug 的编码 agent**（Slides 第 3 页）。任务提示要求“zero 应该禁用重试，但代码返回三次；保留其他情况”。初始 buggy 代码为：

```python
def retry_count(config):
  return config.get("retries") or 3
```

验证器是四个测试用例：`Missing → 3`、`None → 3`、`0 → 0`、`2 → 2`。这条主线贯穿信用分配、旧策略数据、裁剪和奖励可靠性，非常便于对照。

---

## 三、RL 训练循环与 REINFORCE

### 3.1 循环与目标

Slides 第 5 页给出三阶段循环：**Sample → Score → Update**，然后“Collect new attempts with the updated policy”。

符号假设（Slides 第 5、57、58 页）：

- $x$：任务（初始状态与提示）；
- $\tau$：一次尝试的轨迹，由动作与观察组成；
- $\theta$：策略参数；
- $p_\theta(\tau \mid x)$：给定任务下轨迹的概率；
- $R(\tau)$：最终奖励；
- 目标 $J(\theta) = \mathbb{E}_{\tau \sim p_\theta(\cdot \mid x)}[R(\tau)]$，即在任务上最大化平均奖励。

### 3.2 成功轨迹示例

Slides 第 4 页给出一次成功轨迹：Inspect → Edit → Test → Revise → Test again。奖励为 $R(\tau)=1$ 当且仅当四个测试全部通过，否则为 0。这体现了“最终奖励稀疏”的设定。

### 3.3 REINFORCE 与失败轨迹问题

Slides 第 6 页指出，朴素 REINFORCE 用最终奖励加权一次尝试中的**每一个动作**，损失为

$$L_{PG} = -\sum_t R(\tau) \log \pi_\theta(a_t \mid h_t)$$

其中 $a_t$ 是第 $t$ 步动作，$h_t$ 是历史（任务、先前动作与观察）。若 $R(\tau)=1$，增大其动作似然；若 $R(\tau)=0$，该轨迹**不产生任何更新**。Slide 直接抛出问题：“How can a failed attempt still provide a learning signal?”——这正是后续组基线、critic、PRM 等方法要解决的核心。

---

## 四、信用分配：从组基线到 GAE

### 4.1 组内比较

Slides 第 8 页给出四个尝试（同任务）：1 成功（$R=1$）、3 失败（$R=0$）。以组平均 $0.25$ 为基线，更新权重为：

| 尝试 | 奖励 | 权重（reward − baseline） |
|---|---|---|
| 1 | 1 | +0.75 |
| 2 | 0 | −0.25 |
| 3 | 0 | −0.25 |
| 4 | 0 | −0.25 |

结论：**失败尝试也贡献学习信号**，其动作获得负权重。

### 4.2 Turn 级奖励 vs 组权重

Slides 第 9 页用两条示意轨迹说明：成功轨迹 A 中可能含有错误动作，失败轨迹 B 中可能含有有帮助的动作。而组权重在整条轨迹内对每个 turn 相同，因此需要 turn 级奖励来判断“该强化哪些 turn”。

### 4.3 Reward-to-go

Slides 第 10 页：轨迹 A 的奖励序列为 $0,0,1$。从 $a_3$ 之前开始，“剩余奖励加总”，得 reward-to-go $R_3 = 0+0+1=1$。Slides 第 11 页对比 A 与 B：A 在每个动作处 $R_t=1$，B 在每个动作处 $R_t=0$。于是提出：当只观察最终奖励时，如何估计哪些 turn 真正有帮助？

### 4.4 值函数与 critic

Slides 第 12 页设想从 B 的历史 $h_3$ 继续 10 次，得到奖励序列（示意）：`1 0 0 1 0 0 0 1 0 0`，其中 3 次为 1，平均 $3 \div 10 = 0.3$。定义值函数：

$$V_\mu(h_3) = \mathbb{E}_\mu[R \mid h_3]$$

其中 $\mu$ 是 rollout 策略。十条样本给出该期望的一个估计。

Slides 第 13 页：训练 critic 预测 reward-to-go，损失为平方误差

$$L_V(\phi) = \mathbb{E}_t\left[(V_\phi(h_t) - R_t)^2\right]$$

若 $V_\phi(h_3)=0.6$，在十个样本（3 个 1、7 个 0）上的平均平方误差为

$$\frac{3(0.6-1)^2 + 7(0.6-0)^2}{10}$$

最优预测是样本均值 0.3（对应平方误差 0.21）。Slide 注明该思路参考 Ranzato et al., ICLR 2016 §3.2.1。

### 4.5 两种值函数建模

Slides 第 14 页给出两种架构：

- **独立 value network**：自带 body 和输出层，值损失训练整个网络；例子为 InstructGPT（Ouyang et al., 2022, App. C.4）。
- **policy body + value head**：用策略隐藏表示，加 stop-gradient 后接线性 value head，值损失只训练 head；例子为 MIXER（Ranzato et al.）。策略损失仍会训练 policy body。

### 4.6 TD 误差与 GAE

Slides 第 15 页：B 的最后三个动作，值分别为 0.3 → 0.6 → 0.4 → 0.0（终止处 $V_\phi(h_6)=0$），奖励均为 0。无折扣 TD 误差：

$$\delta_t = r_{t+1} + V_\phi(h_{t+1}) - V_\phi(h_t)$$

Slide 明确写出“with no reward discounting”，即示例中 $\gamma=1$（与 Slide 58 一致）。

Slides 第 16 页：取 $\lambda=0.5$，三个 $\delta$ 分别为 +0.3、−0.2、−0.4，权重依次 1、0.5、0.25，估计优势

$$\hat{A}_3 = 0.3 + 0.5(-0.2) + 0.25(-0.4) = 0.1$$

GAE 的向后递推为 $\hat{A}_t = \delta_t + \lambda \hat{A}_{t+1}$，末端无后续误差。引用 Schulman et al., ICLR 2016。

### 4.7 过程奖励模型（PRM）

Slides 第 17 页：以“$5x = 6x - 14 \Rightarrow x = 14$”为例子，标注者把“$x = 7$”标为错误。PRM 把“步骤正确性”作为值的代理监督，引用 Lightman et al., 2023, Figure 1。

---

## 五、同步与异步 RL

Slides 第 19 页：同步 RL 中，一个 batch 的所有轨迹必须全部完成才能更新策略。图中三块 GPU 分别“Generate / Wait / Update”，时间轴上出现明显等待段，下一 batch 在策略更新之后才开始。引用 AReaL（Fu et al., 2026, §3.2）。

Slides 第 20 页：异步 RL 让 rollout worker 持续生成，learner 从已完成轨迹更新。时间轴上 rollout 与 Update 1、Update 2 重叠；**代价是部分完成轨迹来自较早的策略版本**。引用 AReaL §4.1。

Slides 第 22 页用一个具体算例说明“过期数据”：rollout 策略 $\mu$ 与 learner 策略 $\pi_\theta$ 对同一历史的三个候选动作概率不同（例如某动作 $\mu=0.40$、$\pi_\theta=0.70$；另一动作 $\mu=0.40$、$\pi_\theta=0.20$；第三动作 $\mu=0.20$、$\pi_\theta=0.10$）。文本提取未标明这些数字对应的具体动作名，**“Check None explicitly / Use get(..., 3) / Keep the original code”与数值的对应关系待核**。

---

## 六、稳定策略更新

### 6.1 重要性采样

Slides 第 23 页：在固定历史 $h$ 下，用 $\pi_\theta(a\mid h)/\mu(a\mid h)$ 对采样动作重新加权，例如 $0.70/0.40 = 1.75$、$0.20/0.40 = 0.50$。期望恒等式为

$$\mathbb{E}_{a\sim\pi_\theta}[R(a)] = \mathbb{E}_{a\sim\mu}\left[\frac{\pi_\theta(a\mid h)}{\mu(a\mid h)} R(a)\right]$$

### 6.2 整条轨迹的比率与高方差

Slides 第 24 页：整条轨迹比率

$$w(\tau \mid x) = \frac{p_\theta(\tau\mid x)}{p_\mu(\tau\mid x)} = \prod_t \frac{\pi_\theta(a_t\mid h_t)}{\mu(a_t\mid h_t)}$$

若每个动作比率为 1.05，则 100 个动作后 $1.05^{100} \approx 132$，乘积导致**高方差，少数样本可能主导更新**。引用 CTPO（Zhang et al., 2026, §3.2）。Slides 第 25 页指出，累计比率 $\rho_t^{cum}$ 随 token 位置增长，其离散程度在工具使用的数学 rollout 中随位置变大（CTPO Fig. 1；**具体曲线形状待核**）。

### 6.3 早期动作改变后续历史

Slides 第 26 页：一个“Add a None check”的编辑，$\mu$ 下概率 40%、$\pi_\theta$ 下 10%，于是到达该记录历史的相对概率只有 $0.10/0.40=0.25$；而该历史之后的“Run tests”动作比率仍为 $\mu:50\%$、$\pi_\theta:50\%$，比率为 1。这说明**局部比率正常，但历史上可达性已经被改变**（CTPO §3.1）。

### 6.4 不同方法用哪些动作进入权重

Slides 第 27 页给出表（响应有 $T$ 个动作，标准写法为 $a_0 \dots a_{T-1}$；文本提取在此处偶见 $a_T$，**页码内符号与 PDF 需对照**）：

| 方法 | 权重使用 |
|---|---|
| PPO / GRPO | 当前动作 |
| CTPO | 到 $t$ 为止的动作 |
| Full ratio | 全部动作 |
| GSPO | 全部动作，长度归一化 |

DAPO 与 CISPO 也用当前动作比率，只是裁剪规则不同（Yu et al., 2025；MiniMax-M1, 2025）。

### 6.5 裁剪

Slides 第 29 页说明“为什么要限制更新”：旧 rollout 可能获得过大权重，让少数样本主导更新。

Slides 第 30 页：单 token 比率

$$\rho_t = \frac{\pi_\theta(u_t \mid u_{<t})}{\mu(u_t \mid u_{<t})}, \qquad c_t = \text{clip}(\rho_t, \ell, u)$$

示例中 $\ell=0.8$、$u=1.2$。引用 PPO（Schulman et al., 2017）与 CISPO（MiniMax-M1, 2025）。

Slides 第 31 页给出两个目标：

$$J_{PPO}(\theta) = \mathbb{E}_t\left[\min\left(\rho_t \hat{A}_t,\ c_t \hat{A}_t\right)\right]$$

$$J_{CISPO}(\theta) = \mathbb{E}_t\left[\text{sg}(c_t)\, \hat{A}_t \log \pi_\theta(u_t \mid u_{<t})\right]$$

其中 $\text{sg}$ 表示“对梯度停止”。PPO 把 $c_t$ 放进 min，CISPO 把 $c_t$ 当固定权重。最小化损失即 $-J$。

Slides 第 32 页解释 PPO 均值直觉：正优势时，比率超过 $1+\varepsilon$ 不再给额外收益；负优势时，比率低于 $1-\varepsilon$ 不再给额外收益。图中 $\varepsilon=0.2$（改编自 PPO Figure 1；**曲线细节待核**）。

### 6.6 参考模型 KL 与熵奖励

Slides 第 33 页：参考模型 KL 惩罚

$$\max_\theta J_{policy} - \beta D_{KL}(\pi_\theta \parallel \pi_{ref})$$

其中 $\mu$ 生成训练 batch 并提供重要性比率分母，$\pi_{ref}$ 固定作为锚点。引用 DeepSeekMath（Shao et al., 2024, GRPO objective）。

Slides 第 34 页：熵奖励

$$\max_\theta J_{policy} + \alpha H(\pi_\theta)$$

熵 $H$ 衡量下一个 token 的不确定性。提醒：更宽的分布有助于尝试其他动作，但**不保证这些动作有用**（PPO §5）。

### 6.7 算法对照表

Slides 第 35 页汇总：

| 算法 | 奖励权重 | 学习 critic | 重要性比率 | 裁剪 |
|---|---|---|---|---|
| REINFORCE | reward-to-go $R_t$ | 否 | 无（fresh rollouts） | 无 |
| PPO | critic 的 GAE | 是 | 当前 token $\rho_t$ | 原始与裁剪项取 min |
| GRPO | 组比较 | 否 | 当前 token $\rho_t$ | 同 PPO |
| CISPO | 组比较 | 否 | 当前 token $\rho_t$ | 裁剪比率作固定权重 |
| GSPO | 组比较 | 否 | 整条响应、长度归一化 | PPO min，作用于响应比率 |
| DAPO | 组比较 | 否 | 当前 token $\rho_t$ | PPO min，上界更高 |

Slide 注明“组比较”指：先减去组平均奖励，再除以奖励离散程度（spread）。

---

## 七、任务选择与奖励可靠性

### 7.1 无信息 rollout 组

Slides 第 37 页给出三组四轨迹奖励：

- `0 0 0 0`：均值 0，减均值后全为 0；
- `0 1 0 1`：均值 0.5，减均值后 `−0.5, +0.5, −0.5, +0.5`；
- `1 1 1 1`：均值 1，减均值后全为 0。

结论：奖励完全相同（全 0 或全 1）的组，组优势全部为零，**无法提供组内比较**。

Slides 第 38 页提出排查“为何全失败”的三个维度：验证器质量、当前模型能力、探索不足。

### 7.2 假阴性

Slides 第 39 页：候选解在四个用例上全部正确，但实现用了不同源码；验证器要求出现精确短语 “value is None”，因此拒绝该解。这是假阴性——**有效解被拒绝**。提醒应检查行为而非随意的措辞选择。引用 SWE-bench Verified（2024）。

Slides 第 40 页列出后果与证据（历史版本，2025–26 审计）：

| Benchmark | 平台/上限 | 证据 |
|---|---|---|
| SWE-bench Verified | ≈81% | 进度在约 80.9% 附近放缓，剩余失败中许多测试有缺陷 |
| τ-bench Airline | ≈70% | 任务不一致限制可达分数 |
| τ-bench Retail | ≈92% | 标注错误限制可达分数 |

Slide 注明这些是“报告的 plateau 或 limit”，**τ-bench 此后已修正任务**。引用 SWE-bench audit（OpenAI, Feb. 2026）、SABER（Cuadron et al., 2025, §5.1）、τ-bench fixes（Feb. 2026）。以上数值仅为 Slide 所给，不外推。

### 7.3 假阳性与奖励黑客

Slides 第 41 页：把候选改成 `return 0`，训练验证器只测 `retries=0` 这一条，于是这一个用例通过、奖励为 1，但 Missing / None 和 2 都不通过。**假阳性奖励了无效解**，训练可能学会利用这一缺口。

Slides 第 42 页列出常见捷径：

- 有互联网 → 找已发布答案；
- Git 历史（含未来提交）→ 找到并复制后续修复；
- 有模型 API key → 调用更强模型生成答案或训练数据；
- 可访问测试或 test runner → 让测试通过而不修 bug。

Slide 还记录了一个公开 API 的例子：某 PostTrainBench agent 用 grading key 生成训练数据，尽管有明确限制（MAI-Thinking-1 §3.3.1 p.43；PostTrainBench §5.4 Fig.7）。

Slides 第 43 页给出三条独立检查：训练奖励、未见任务上的独立成功、成本与失败（工具调用、回归、重复动作）。若奖励上升但独立指标未改善，应检查轨迹中的捷径。

### 7.4 动态采样与部分奖励

Slides 第 44 页：DAPO 动态采样保留混合奖励组，丢弃全同组，并继续采样直到 batch 满。图中示例：Task A `0 0 0 0` 跳过、Task B `0 1 0 1` 保留、Task C `1 1 1 1` 跳过、Task D 新组 `0 0 1 0` 保留；目标 2 组，收集到 2/2 后更新。引用 DAPO（Yu et al., 2025, §3.2）。

Slides 第 45 页：部分奖励是辅助奖励。示例任务通过 4 项检查，每过一项加 0.25：

| | τ₁ | τ₂ | τ₃ | τ₄ |
|---|---|---|---|---|
| 通过检查数 | 0/4 | 1/4 | 2/4 | 1/4 |
| 成功奖励 | 0 | 0 | 0 | 0 |
| 减均值后 | 0 | 0 | 0 | 0 |
| 成功 + 部分奖励 | 0 | 0.25 | 0.50 | 0.25 |
| 减均值后 | −0.25 | 0 | +0.25 | 0 |

不同部分分数可减少零优势组与 batch 的数量（表中“减均值后”行按 0.25 均值计算；**该行末位的 0 与 0.25 的对应关系需与 PDF 对照**）。

### 7.5 辅助奖励的风险

Slides 第 46 页给出两个已记录案例：

- 某 bug 对表面化的 web 工具调用给分，导致模型把浏览器当计算器并假装搜索（OpenAI, Dec. 2025）；
- “Nerdy” 人设下，含 goblin/gremlin 的比喻得分更高，导致这类词增多，甚至在没有该人设提示时也出现（OpenAI, Apr. 2026）。

### 7.6 探索崩溃

Slides 第 47 页：同一历史下三个动作概率从 `0.20 / 0.60 / 0.20` 变为 `0.01 / 0.98 / 0.01`，几乎所有样本都选 B，替代动作很少被尝试。熵奖励可鼓励替代动作，但应检查轨迹是否真的多样化（DAPO 相关讨论）。

---

## 八、向教师学习：蒸馏

### 8.1 课程与暖启动

Slides 第 49 页：当学生很少成功时，教师可提供成功轨迹。流程为：demonstrations（先学成功解）→ warm start → learnable tasks（模型有时能成功）→ harder tasks（随能力提升增难）。提醒保留早期任务并固定评估集。

### 8.2 蒸馏与 on-policy 蒸馏

Slides 第 50 页：在教师保存的轨迹上，训练学生匹配教师的动作概率。例：在某历史 $h_3$，教师给 $a_3$ 80%、另一动作 20%，记为 $q(\cdot \mid h_3)$。问题在于学生自己的错误会到达训练集里没有的历史。

Slides 第 51 页：on-policy 蒸馏改为**由学生生成历史**，再让教师在这些历史上给出目标。例：学生在轨迹 B 上到达 $h_3$，教师目标仍是 80% / 20%。“on-policy”指历史来自学生自己的 rollout。

### 8.3 稠密蒸馏目标

Slides 第 52 页：在 $h_3$，学生给两个动作各 0.5，教师给 0.8 / 0.2，反向 KL 为

$$0.5\log(0.5/0.8) + 0.5\log(0.5/0.2) \approx 0.223$$

对学生历史分布 $d_\mu$ 取平均，最小化

$$L_{OPD} = \mathbb{E}_{h \sim d_\mu}\left[D_{KL}\left(\pi_\theta(\cdot \mid h) \parallel q(\cdot \mid h)\right)\right]$$

引用 GKD（Agarwal et al., ICLR 2024）。

### 8.4 On-policy 自蒸馏

Slides 第 53 页：OPSD 使用一个“起始模型的冻结副本”作为教师，教师输入是任务与历史，**外加一份已验证解**，从而在学生自己的历史上给出更好的目标。引用 Self-Distilled Reasoner（Zhao et al., 2026）。

---

## 九、常见误区

1. **把 REINFORCE 的“零更新”当成“无信号”**：失败轨迹仍可通过组基线（Slide 8）获得负权重。
2. **把组权重当成 turn 级信用**：同一轨迹内所有 turn 共享同一组权重（Slide 9），因此成功轨迹里的错误动作也会被强化。
3. **忽略 $\gamma=1$ 的假设**：本讲 TD 与 GAE 示例都使用无折扣回报（Slides 第 15、58 页）。
4. **把重要性比率看成“局部安全”**：动作比率正常，不代表到达该历史的概率没变（Slide 26）；整条轨迹的乘积会放大方差（Slide 24）。
5. **把裁剪当成万能稳定器**：裁剪只限制单点比率，方法间用哪些动作进入权重不同（Slide 27），PPO 与 CISPO 的裁剪语义也不同（Slide 31）。
6. **以为熵奖励一定有益**：它鼓励尝试，但不保证动作有用（Slide 34）；过度训练还会伴随探索崩溃（Slide 47）。
7. **只看训练奖励**：训练验证器可能被假阳性、假阴性或捷径利用（Slides 第 39–42 页），需要独立检查（Slide 43）。
8. **把平台期都归因于模型能力**：SWE-bench Verified、τ-bench 的案例显示，验证器或标注问题也会限制可达分数（Slide 40；数值仅为 Slide 所给）。

---

## 十、复习问题

1. 写出 $J(\theta)$，并说明 $p_\theta(\tau \mid x)$ 与 $R(\tau)$ 各自的角色（Slide 5）。
2. 在 Slide 8 的四条轨迹里，为什么失败轨迹也产生更新？权重分别是多少？
3. reward-to-go 与值函数 $V_\mu(h)$ 的关系是什么？为什么 critic 用平方误差训练（Slides 第 10–13 页）？
4. 写出 TD 误差与 GAE 递推式，并用 $\lambda=0.5$ 复算 Slide 16 的 $\hat{A}_3$。
5. 为什么“policy body + value head”要用 stop-gradient？它对策略损失还有什么影响（Slide 14）？
6. 同步与异步 RL 的等待差异在哪？异步引入什么问题（Slides 第 19–22 页）？
7. 整条轨迹的重要性比率为什么随长度爆炸？举出 Slide 24 的数值例子。
8. PPO 与 CISPO 的目标有何不同？$\text{sg}(\cdot)$ 的作用是什么（Slide 31）？
9. 参考模型 KL 与熵奖励分别解决什么问题、带来什么风险（Slides 第 33–34 页）？
10. 为什么“全 0”或“全 1”组对 GRPO 类方法无信息？DAPO 的动态采样如何处理（Slides 第 37、44 页）？
11. 假阴性与假阳性各会带来什么后果？Slide 41 的 `return 0` 例子说明什么？
12. 列出 Slide 42 的至少三种奖励黑客捷径，并说明 Slide 43 的三条独立检查如何互补。
13. on-policy 蒸馏与普通蒸馏的关键差别是什么？“on-policy”指什么（Slides 第 50–51 页）？
14. 写出 Slide 52 的反向 KL 计算，并说明为什么最小化该目标能让学生接近教师。

---

## 十一、待核清单

- Slides 第 22 页：三个动作名称、概率与 $\mu$/$\pi_\theta$ 列的对应关系（文本提取未标明）。
- Slides 第 25 页：$\rho_t^{cum}$ 离散度随位置增长的曲线形状。
- Slides 第 27 页：表中 `a_T` 与 `a_{T-1}` 的下标写法。
- Slides 第 32 页：PPO 目标曲线细节。
- Slides 第 45 页：“减均值后”一行中 0 与 0.25 的逐列对应。
- 所有涉及 PDF 图示、公式排版、颜色或箭头的位置，以官方 PDF 为准。

---

## 十二、官方来源链接

- 课程主页：<https://www.cmu-agents.com/>
- 课程日程与阅读：<https://www.cmu-agents.com/#schedule>
- 官方课程日程（同址）：<https://www.cmu-agents.com/#schedule>
- 作业与项目要求：<https://www.cmu-agents.com/#assignments>
- Assignment 1 · Harness：<https://github.com/cmu-agents/assignment-1>
- Assignment 2 · Eval：<https://github.com/cmu-agents/assignment-2>
- Lecture 11 slides：<https://www.cmu-agents.com/slides/lecture-11-rl-advanced.pdf>
