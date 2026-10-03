# Lecture 9 Slides：文本提取（待核）

- 官方来源：https://www.cmu-agents.com/slides/lecture-09-rl-basics.pdf
- 提取日期：2026-10-03
- PDF SHA-256：c8724ca6fbadb2afef38d627bbab2e09f8e8077fb1bb4dc0a4a078fb8669c1ca
- 说明：按页提取；图示、公式和布局需对照官方 PDF，文本提取不能替代视觉核验。

## Slide 1

RL Foundations for Agents
From SFT to policy gradients
Daniel Fried
11-768: AI Agents
1


## Slide 2

Running example: Number Search
Four sample trajectories:
τ1 8 higher 12 lower 10 higher 11 correct R = 1
τ2 4 higher 8 higher 12 lower 11 correct R = 1
τ3 16 lower 8 higher 9 higher 10 timeout R = 0
τ4 1 higher 2 higher 3 higher 4 timeout R = 0
τ ₁  and τ ₂ diﬀerent actions · same successful outcome
A hidden integer lies between 1 and 16. The agent has four guesses. After an incorrect guess, the
environment replies higher or lower. Reward is 1 only when it ﬁnds the number.
Hidden number for this task instance: 11
2

## Slide 3

SFT on demonstrations
SFT trains the agent to maximize the probability of all target actions in a demonstration
history h ₀
prompt →
target a ₀ *
guess 8 →
history h ₁
higher →
target a ₁ *
guess 12→
history h ₂
lower →
target a ₂ *
guess 10→
history h ₃
higher →
target a ₃ *
guess 11
Target actions may come from a person, a stronger model, or (today) a successful trajectory from this agent
L  =SFT −  logπ  (a  ∣
t
∑ θ t∗ h  )1:t
3

## Slide 4

Task mismatch
SFT maximizes the probability of demonstrated actions. We would like to maximize the
probability that the agent carries out the task. (these are not quite the same!)
DEMONSTRATION
τ1 8 higher 12 lower 10 higher 11 correct
ANOTHER SUCCESS
τ2 higher 8 higher 12 lower 11 correct
There are multiple ways to carry out a task.
Some actions are worse than others (e.g. should never guess "13" after "12 -> lower").
4
4

## Slide 5

Data mismatch
We'd like to be able to learn from sub-optimal data, too
DEMONSTRATION
τ1 8 higher 12 lower 10 higher 11 correct
OTHER ALTERNATIVES
τ2 4 higher 8 higher 12 lower 11 correct
τ3 16 lower 8 higher 9 higher 10 timeout
τ4 1 higher 2 higher 3 higher 4 timeout
5

## Slide 6

Exposure bias
The agent was not exposed to its own mistakes at training time, and might not be prepared to
handle mistakes when generating
TRAINING
DEMONSTRATION 8 higher 12 lower 10 higher 11 correct
GENERATION 8 higher ?
6
2

## Slide 7

Reinforcement learning
Generate actions/trajectories from the agent, evaluate their reward, and adjust the parameters
of the agent to maximize expected reward.
task instance
hidden
number 11
⇢agent
πθ
Generate
→
τ1 8 higher 12 lower 10 higher 11 correct R = 1
τ3 16 lower 8 higher 9 higher 10 timeout R = 0
Reward
Task mismatch We train the agent to maximize expected reward.
Data mismatch The agent can learn from all trajectories (seek high reward; avoid low reward)
Exposure bias The agent generates trajectories in training (on-policy), so it learns to recover from errors
Update
Adapted from Sean Welleck · RL Fundamentals ↗ 7

## Slide 8

Interactions as trajectories
8

## Slide 9

The agent‒environment loop
AGENT
Policy πθ
action a →
← observation o
← reward r
ENVIRONMENT
task instance x
Task instance x Observation o Action a Reward r
Text generation the prompt tokens so far next token score from a judge model
Web agent the task and
website rendered page click, type, scroll number of sub-tasks
completed
Number Search number (hidden) higher, lower, or
correct the next guess 1 on correct; otherwise 0
t
t+1
t+1
t+1 t t+1
9

## Slide 10

Trajectories
The agent conditions only on past actions and observations (not hidden environment state).
a ₀ o ₁ a ₁ o ₂
history h ₂
what the policy conditions on
environment state s ₂
hidden number 11
not visible
prompt → guess 8 → higher → guess 12 → lower →
g ue s s  1 0 →
h ig h e r →
g ue s s  1 1 →
c o rr e c t
a ₂
o ₃
a ₃
o ₄
h  =t (o  ,a  ,o  ,…,o  ) π  (a ∣0 0 1 t θ t h  )t
10

## Slide 11

Trajectories
Trajectories can also include reward at each step.
a ₀ o ₁r ₁ =0 a ₁ o ₂r ₂ =0 a ₂ o ₃r ₃ =0 a ₃ o ₄r ₄ =1
trajectory τ ₁
reward R(τ ₁ ) = 1
In number search, 1 for "correct" and 0 otherwise.
prompt → guess 8 → higher → guess 12 → lower → guess 10 → higher → guess 11 → correct
τ =(o  ,a  ,r  ,o  ,…,a  ,r  ,o  ) R(τ)=0 0 1 1 T−1 T T
 r  ∑t=1
T t
11

## Slide 12

Trajectories
Trajectory probabilities depend on the policy and the environment.
a ₀ o ₁r ₁ =0 a ₁ o ₂r ₂ =0 a ₂ o ₃r ₃ =0 a ₃ o ₄r ₄ =1
p(o ₀ |x) πθ(8|h ₀ ) P(o ₁ ,r ₁ |…) πθ(12|h ₁ ) P(o ₂ ,r ₂ |…) πθ(10|h ₂ ) P(o ₃ ,r ₃ |…) πθ(11|h ₃ ) P(o ₄ ,r ₄ |…)
We don't know P, but we can sample from it by interacting with the environment.
prompt → guess 8 → higher → guess 12 → lower → guess 10 → higher → guess 11 → correct
p  (τ ∣θ x)=  π  (a  ∣
t
∏ θ t h  )(o  ,r  ∣t t+1 t+1 h  ,a  ,x)t t
12

## Slide 13

Objective: maximize expected reward
EXPECTED REWARD J OVER FOUR TRAJECTORIES
τ ₁ 0.30 × 1
τ ₂ 0.20 × 1
τ ₃ 0.25 × 0
τ ₄ 0.25 × 0
= 0.50
Training adjusts θ to maximize expected reward (i.e. the agent has a higher probability of high
reward trajectories)
low reward trajectories probability mass → high reward trajectories
J(θ)=E  [R(τ)]τ∼p  (⋅∣x)θ
13

## Slide 14

Expert iteration
14

## Slide 15

Reinforced self-training
ReST generates data from the policy, and then updates the policy using successful trajectories.
1 Grow
Sample trajectories from the current policy
and compute rewards.
2 Improve
Use rewards to ﬁlter the data; augment the
existing datasets; train the policy.
3 Repeat
Use the updated policy.
Gulcehre et al. · ReST, Fig. 1 ↗ Singh et al. · ReST-EM ↗ 15

## Slide 16

Reinforced self-training
The loss is the standard SFT loss, on trajectories with high reward
τ1 8 higher 12 lower 10 higher 11 correct R = 1
KEEP
τ2 4 higher 8 higher 12 lower 11 correct R = 1
KEEP
sample trajectories
↓
compute rewards
↓
keep τ ₁ , τ ₂
↓
SFT
τ 3 1 6 l o w e r 8 h i g h e r 9 h i g h e r 1 0 t i m e o u t
R  =  0
D R O P
τ 4 1 h i g h e r 2 h i g h e r 3 h i g h e r 4 t i m e o u t
R  =  0
D R O P
L  =ReST −   logπ  (a  ∣
τ:R(τ)=1
∑
t
∑ θ t h  )t
Gulcehre et al. · ReST ↗ Singh et al. · ReST-EM ↗ 16

## Slide 17

From rewards to gradients
Policy gradients
17

## Slide 18

How to maximize expected reward?
We can't use backpropagation directly: sampling and the environment are non-diﬀerentiable
PARAMETERS
θ →
POLICY
πθ(a|h) ✕
SAMPLE
action a ✕
ENVIRONMENT
obs o, reward r
Sampled action
Changing θ changes the action probabilities, but
actions are discrete and sampled.
Task environment
The world is not (usually!) diﬀerentiable. How do you
take the derivative of a unit test w.r.t. code?
pθ(τ|x) changes with θ R(τ) is observed after the rollout
General solution: policy gradient (REINFORCE, Williams 1992).
J(θ)=  p  (τ ∣
τ
∑ θ x) R(τ)
18

## Slide 19

Policy gradient
Maximize expected reward
under the policy.
Take the gradient: only the
probability depends on θ.
Multiply and divide by trajectory
probability.
Use ∇p / p = ∇ log p.
This is an expectation we can
estimate from samples.
J(θ)=E  [R(τ)]=τ∼p  (⋅∣x)θ
 p  (τ ∣
τ
∑ θ x)R(τ)
∇  J =θ
 ∇  p  (τ ∣
τ
∑ θ θ x)R(τ)
∇  J =θ
 p  (τ ∣
τ
∑ θ x)R(τ)  
p  (τ ∣ x)θ
∇  p  (τ ∣ x)θ θ
∇  J =θ
 p  (τ ∣
τ
∑ θ x)R(τ)∇  logp  (τ ∣θ θ x)
∇  J =θ E  [R(τ)∇  logp  (τ ∣τ∼p  (⋅∣x)θ θ θ x)]
REINFORCE (Williams, 1992) ↗ 19

## Slide 20

Policy gradient
Replace the expectation by trajectories we sample.
τ ~  pθ(·|x)
Current-policy trajectories and
histories
obtain by sampling: policy and
environment
R(τ)
Task-level evaluation
obtain from the environment
∇θ log πθ(a ₜ |h ₜ )
Changes probabilities of sampled
actions
same mechanics as in SFT
∇  J =θ E  [R(τ)∇  logp  (τ ∣τ∼p  (⋅∣x)θ θ θ x)]
τ ∼p  (⋅ ∣θ x),  =∇  Jθ R(τ)∇  logp  (τ ∣θ θ x)=R(τ)  ∇  logπ  (a  ∣
t
∑ θ θ t h  )t
Williams · REINFORCE, 1992 ↗ 20

## Slide 21

Trajectory log probability
p(o ₀ |x) · πθ(a ₀ |h ₀ ) · P(o ₁ ,r ₁ |h ₀ ,a ₀ ,x) · πθ(a ₁ |h ₁ ) · P(o ₂ ,r ₂ |h ₁ ,a ₁ ,x)
Same computation as SFT: sum token log probabilities. Here the tokens were sampled by the policy.
t indexes actions; k indexes tokens within action a.
We can just multiply by R(τ) to get ∇ˆ θJ.
logp  (τ ∣θ x)=  logP(o  ,r  ∣
t
∑ t t h  ,a  ,x)+t t
 logπ  (a  ∣
t
∑ θ t h  )t
=const+  logπ  (a  ∣
t
∑ θ t h  )t
∇  logp  (τ ∣θ θ x)=  ∇  logπ  (a  ∣
t
∑ θ θ t h  )t
a  =t (u  ,…,u  ), ∇  logπ  (a  ∣t,1 t,m  
t θ θ t h  )=t
 ∇  logπ  (u  ∣
k=1
∑
m  
t
θ θ t,k h  ,u  )t t,<k
t
21

## Slide 22

Computing the policy gradient
Eﬀectively, we just do masking and rescaling of the standard SFT loss computation.
<|im_start|>user ↵ Find·the·number·in·1–16. ↵ <|im_end|> ↵ <|im_start|>assistant ↵
guess(8) ↵ <|im_end|> ↵ <|im_start|>tool ↵ higher ↵ <|im_end|> ↵
<|im_start|>assistant ↵ guess(12) ↵ <|im_end|> ↵ … ↵ <|im_start|>assistant ↵
guess(11) ↵ <|im_end|>
“·” = space, “ ↵ ” = newline · colored = sampled by the policy, gray = context only
m = 1
tokens the policy sampled, including the
end-of-turn token
m = 0
prompt and observation tokens, which the
policy did not choose
R(τ)
one scalar, shared by every generated
token in the trajectory
L  =PG −R(τ)  logπ  (u  ∣
t:m  =1t
∑ θ t u  )<t
t t
22

## Slide 23

Policy-gradient training loop
After an update, the new policy collects the next batch.
1 Collect
Sample task
instances; sample
from the agent on
them.
→
2 Evaluate
Compute rewards
for each trajectory.
→
3 Form loss
Weight action log
probabilities by
reward.
→
4 Update
Backpropagate,
change θ, collect
again.
↺
L  =PG −  R(τ  )  logπ  (a  ∣
i
∑ i
t
∑ θ i,t h  )i,t
23

## Slide 24

With binary rewards, this looks a lot like ReST
REINFORCE
=
SFT loss on the successful trajectories
(there are some diﬀerences, e.g. ReST does batched updates and aggregates datasets)
−  R(τ  )  logπ  (a  ∣
i
∑ i
t
∑ θ i,t h  )i,t −   logπ  (a  ∣
i:R(τ  )=1i
∑
t
∑ θ i,t h  )i,t
Williams · REINFORCE ↗ Singh et al. · ReST-EM ↗ 24

## Slide 25

Better than expected
Baselines and advantages
25

## Slide 26

Rewards should be relative
τ ₁
All actions get upweighted.
τ ₃
In basic REINFORCE, as in ReST, this produces no gradient at all!
The update should depend on how well the policy usually does on this example.
guess 8
← R=1
higher guess 12
← R=1
lower guess 10
← R=1
higher guess 11
← R=1
correct
guess 16
← R=0
lower guess 8
← R=0
higher guess 9
← R=0
higher guess 10
← R=0
timeout
26

## Slide 27

Advantages
Advantage: how much better is this action, than the policy's average?
History h: guess 8 / higher · guess 12 / lower — the number is 9, 10 or 11, with two guesses left.
Neither Qπ nor Vπ is known, so we estimate advantage from the sampled reward.
A (h,a)=π
 −
expected reward after a
 Q (h,a)π
 
expected reward from h
 V (h)π
guess 11
if wrong, two candidates and one
guess left
Aπ(h,11) < 0
Vπ(h)
guess 10
if wrong, one candidate and one
guess left
Aπ(h,10) > 0
 =A^t −
trajectory reward
 R(τ)  
an estimate of V (h  )π t
 b(h  )t
27

## Slide 28

Policy gradients with advantage estimates
Incorporate advantages by recentering the reward.
REINFORCE: one trajectory
reward weights every action.
Subtract a baseline — the weight
is now Â ₜ .
Both lines are diﬀerent ways to estimate the same ∇θJ.
Â ₜ  = R(τ) − b(h ₜ ). Diﬀerent choices for b produce diﬀerent algorithms
a constant
upcoming bandit example
a running mean of
rewards
adapts as the policy improves
Vφ(h ₜ )
a trained value model: actor‒critic,
PPO
the group mean
no extra model: GRPO (next
section)
 =∇  Jθ R(τ)  ∇  logπ  (a  ∣
t
∑ θ θ t h  )t
 =∇  Jθ
  ∇  logπ  (a  ∣
t
∑
 A^t
 (R(τ)−b(h  ))t θ θ t h  )t
28

## Slide 29

Baselines do not bias the gradient estimator
So E[ ∇ˆ θJ] = ∇θJ for any baseline that conditions only on the history
=∇  Jθ
 (R(τ)−∑t b(h  ))∇  logπ  (a  ∣t θ θ t h  )t
so this is an unbiased estimate of J's gradient if the expectation is 0
E[  ]=∇  Jθ ∇  J−θ E[  b(h  )∇  logπ  ]∑t t θ θ
E  [b(h)∇  logπ  (a∣a∼π  (⋅∣h)θ θ θ h)]
=b(h)  π  (a∣∑a θ h)∇  logπ  (a∣θ θ h)
=b(h)  ∇  π  (a∣∑a θ θ h) π∇logπ = ∇π
=b(h)∇   π  (a∣θ∑a θ h)=b(h)∇  1=θ 0
29

## Slide 30

Simple example: two-armed bandit
With one policy parameter and two actions, we can compute gradients exactly.
0.0
0.5
1.0 p = πθ(guess A)
−4 0 2 4
θ
p = 0.25
θ = −1.1
an update moves θ
The sigmoid σ turns the single real number θ into a probability.
guess A p = σ(θ) = 0.25 reward 1
guess B 1 − p = 0.75 reward 0
Raising θ raises p(guess A) and lowers p(guess B)
sampled guess A · reward 1
reward R(τ)
R = 1 ×
slope ∂/∂θ log π (a)
1 − p = +0.75 =
gradient on θ
+0.75
if we sample A, A becomes more likely
sampled guess B · reward 0
reward R(τ)
R = 0 ×
slope ∂/∂θ log π (a)
−p = −0.25 =
gradient on θ
0
if we sample B, nothing happens
This gradient is correct, but a baseline/advantage can make it more useful.
θ θ
30

## Slide 31

Simple example: Adding a baseline
Subtracting a baseline says whether a reward was better or worse than expected.
guess A p = σ(θ) = 0.25 reward 1 guess B 1 − p = 0.75 reward 0
sampled guess A · reward 1
advantage Â = R − b
1 − 0.5 = +0.5 ×
slope ∂/∂θ log π (a)
1 − p = +0.75 =
gradient on θ
+0.375
without a baseline: +0.75
increases p(guess A)
sampled guess B · reward 0
advantage Â = R − b
0 − 0.5 = −0.5 ×
slope ∂/∂θ log π (a)
−p = −0.25 =
gradient on θ
+0.125
without a baseline: 0
increases p(guess A), so decreases p(guess B)
The baseline adds a learning signal from failure while preserving the expected gradient.
reward 0 baseline b(h ₀ ) = 0.5 reward 1
worse than expected · Â < 0 Â > 0 · better than expected
θ θ
31

## Slide 32

Simple example: varying the baseline
Changing the baseline changes the variance of the gradient estimate, while keeping the
expectation the same
b = 0 b = 0
prob 0.75
ĝ  = 0.125
prob 0.25
ĝ  = 0.375
0 0.25 0.5 0.75
E[ ĝ ] = 0.1875
one sampled gradient estimate ĝ  = (R − b)·∇θ log πθ(a)
baseline b 0.50 SD of ĝ 0.108
32

## Slide 33

Simple example: noise in the gradient estimate
Computed a running estimate of the gradient by repeated sampling, with no baseline and with
baseline 0.5.
latest sample guess B gives ĝ  = no baseline 0.000 with baseline 0.125
gradient estimate ĝ
0
0.125
0.375
0.75
5 10 15 20
samples drawn
true gradient 0.1875
no baseline spread SD 0.325 running average 0.188 baseline b = 0.5 spread SD 0.108 running average 0.188
Draw a sample Draw 5 Clear 20 of 20 samples
Both averages converge to the same value, but the baseline has lower variance.
33

## Slide 34

Baselines and credit assignment
What are the advantages of baselines (so far)?
Helps
Marks a trajectory as better or worse than
expected.
A good baseline reduces gradient variance.
Does not solve
All actions have the same advantage Â.
Estimating Vπ(h) may require a separate value
model.
Â = +0.5 guess 8 guess 12 guess 10 guess 11
34

## Slide 35

What if we have intermediate rewards?
If the environment gives rewards before the ﬁnal step, use reward-to-go to reduce variance.
→ → action a ₜ → action → terminal reward +1
included in R ₜ
An action is weighted only by the
rewards that come after it.
Earlier rewards do not depend on
a ₜ , so dropping them cuts variance
without adding bias.
Number Search pays out once, at
the end: R ₜ  = R(τ) for every action.
R  =t
 r  
t=t+1′
∑
T
t′
a c t i o n
t o o l  r e w a r d  + 0 . 2
i g n o r e d
35

## Slide 36

Comparing trajectories
Group-relative advantage estimates
36

## Slide 37

Group-relative advantage estimates
Advantages: how much better is this trajectory than expected? We can compute this by
sampling the policy multiple times. No separate model needed!
reward
R ⱼ
centered
R ⱼ −R̄
divide by
σR
advantage
Â ⱼ
τ1 8 higher 12 lower 10 higher 11 correct 1 +0.5 ÷0.5 +1
τ2 4 higher 8 higher 12 lower 11 correct 1 +0.5 ÷0.5 +1
τ3 16 lower 8 higher 9 higher 10 timeout 0 −0.5 ÷0.5 −1
τ4 1 higher 2 higher 3 higher 4 timeout 0 −0.5 ÷0.5 −1
from the group R̄ = 0.5 σR = 0.5
b(h  )=t =Rˉ
  R(τ  ) for every h   in the groupG1 ∑j=1
G j t
 =A^j
 , =σ  
R
R(τ  )−j Rˉ Rˉ b(h  ), σ  =t R std{R(τ  ),…,R(τ  )}1 G
37

## Slide 38

The GRPO update
Batches contain multiple task instances, each with its own group.
task instance rewards of the G rollouts group mean advantage estimates Â ᵢ ⱼ
x ₁  · hidden 11 1 1 0 0 R̄ ₁  = 0.50 +1 +1 −1 −1
x ₂  · hidden 3 1 0 0 0 R̄ ₂  = 0.25 +1.73 −0.58 −0.58 −0.58
x ₃  · hidden 7 1 1 1 0 R̄ ₃  = 0.75 +0.58 +0.58 +0.58 −1.73
policy-gradient loss · i indexes the batch
→
GRPO loss · i batch, j group
Each task instance has its
own R̄ ᵢ  and σ ᵢ .
Each task instance is normalized
individually.
GRPO supplies group-relative weights to the same
policy-gradient term.
−  R(τ  )  logπ  (a  ∣
i
∑ i
t
∑ θ i,t h  )i,t −      logπ  (a  ∣
i
∑G
1
j=1
∑
G
A^ij
t
∑ θ ij,t h  )ij,t
Written for current-policy trajectories, without the paper's ratio, clipping, or KL terms.Shao et al. · DeepSeekMath, §4.1.2 ↗ 38

## Slide 39

DrGRPO’s two changes
DrGRPO removes the group-standard-deviation and response-length divisions.
GRPO DrGRPO Why it changes
Advantage
estimate
 is measured inside each group, so it diﬀers from one task
instance to the next. Instances the policy almost always passes
or almost always fails have a small , so they count for more.
Response
aggregation
 diﬀers from one response to the next. A long incorrect
response is penalized less per token than a short one, so the
policy drifts toward longer wrong answers.
C is a global constant, the same for every response; the paper uses the generation budget.
Rewards stay ﬁxed; the relative weights of task instances and responses change.
 
σ  
R
R  −j Rˉ R  −j Rˉ σ  
R
σ  
R
  (⋅)∣y  ∣j
1
t
∑   (⋅)C
1
t
∑ ∣y  ∣j
Liu et al. · DrGRPO, Fig. 1 and §3.2 ↗ 39

## Slide 40

Token coefficients in DrGRPO
For one task instance, every generated token in trajectory j shares that trajectory's advantage
estimate.
τ ₁
Â ₁  = +0.5
<|im_start|>assistant↵ guess(8)↵ <|im_end|>↵ <|im_start|>tool↵
higher↵ <|im_end|>↵ …↵ <|im_start|>assistant↵ guess(11)↵
<|im_end|>
PER TOKEN
+0.5 / C
τ ₃
Â ₃  = −0.5
<|im_start|>assistant↵ guess(16)↵ <|im_end|>↵ <|im_start|>tool↵
lower↵ <|im_end|>↵ …↵ <|im_start|>assistant↵ guess(10)↵
<|im_end|>
PER TOKEN
−0.5 / C
Â ⱼ  = R(τ ⱼ ) − R̄, with no division by σR. Simpliﬁed: the paper's objective also has a ratio and clipping.
L  =DrGRPO −      logπ  (u  ∣G
1
j=1
∑
G
C
1
t:m  =1j,t
∑ A^j θ j,t u  )j,<t
Liu et al. · DrGRPO, §3.2 ↗ Shao et al. · DeepSeekMath, Eq. 3 ↗ 40

## Slide 41

Equal rewards and zero advantage estimates
When every reward in a group matches, the group is degenerate and contributes no gradient.
ALL TRAJECTORIES FAIL
[0, 0, 0, 0] → [0, 0, 0, 0]
possibly too hard for the current policy
ALL TRAJECTORIES SUCCEED
[1, 1, 1, 1] → [0, 0, 0, 0]
possibly too easy for the current policy
What could we change if every sampled trajectory fails?
Choose diﬀerent task instances, broaden exploration, add demonstrations, or supply a more
informative reward.
41

## Slide 42

GRPO vs PPO
GRPO was proposed as a more eﬃcient alternative to PPO, which uses a separate model to
estimate the advantage baseline.
PPO trains a value model
GRPO computes group-relative advantages
The advanced RL lecture covers ratios, clipping, and reference-model terms.Shao et al. · DeepSeekMath, Fig. 4 and §4.1.2 ↗ 42

## Slide 43

Summary
43

## Slide 44

Comparing the methods we’ve seen so far
Every method today weights the actions the agent took. They (mainly) diﬀer in the weight.
ReST-EM w ₜ  = 1 on a successful trajectory, 0 on the rest (the SFT loss on what was kept)
REINFORCE w ₜ  = R(τ), the reward of the trajectory the action came from
GRPO/DrGRPO w ₜ  = Â, the reward relative to the other rollouts on the same task instance
τ1 8 higher 12 lower 10 higher 11 correct R = 1
τ2 4 higher 8 higher 12 lower 11 correct R = 1
τ3 16 lower 8 higher 9 higher 10 timeout R = 0
τ4 1 higher 2 higher 3 higher 4 timeout R = 0
 =∇  Jθ
 w  ∇  logπ  (a  ∣∑t t θ θ t h  )t
j
44

## Slide 45

Takeaways
Sampling trajectories from the policy and weighting them by reward addresses the three
problems we started with.
Task mismatch
The objective is expected reward, so any trajectory that succeeds is reinforced.
Data mismatch
The agent can also learn from sub-optimal trajectories, based on their reward.
Exposure bias
The trajectories come from the current policy, so the agent is trained to recover from its own mistakes.
45

## Slide 46

Questions?
Upcoming: async RL / oﬀ-policy data, importance weighting
46

