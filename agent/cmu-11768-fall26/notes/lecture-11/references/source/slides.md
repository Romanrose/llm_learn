# Lecture 11 Slides：文本提取（待核）

- 官方来源：https://www.cmu-agents.com/slides/lecture-11-rl-advanced.pdf
- 提取日期：2026-10-03
- PDF SHA-256：e2f23de9092424cde3a72805e3b343d261a2e219518871843e719c4dbe5cc968
- 说明：按页提取；图示、公式和布局需对照官方 PDF，文本提取不能替代视觉核验。

## Slide 1

Advanced RL Algorithms
for Agents
Graham Neubig
Language Technologies Institute
I m p r o v i n g  h o w  a g e n t s  l e a r n  f r o m  e x p e r i e n c e
1


## Slide 2

RL lecture map
RL basics
Sample attempts →
score them → update
the policy →
Today
Useful feedback
Less waiting
Stable updates
Reliable rewards
Learning from a
teacher
→
Next lecture
Memory, parallelism,
and execution at scale
2

## Slide 3

An RL task: fixing a bug
We’ll train a coding agent to ﬁx bugs, using tests to judge each attempt.
Prompt
Fix the retry setting: zero should disable retries, but the code returns three. Preserve the other
cases.
Initial state: buggy code
def retry_count(config):
  return config.get("retries") or 3
Verifier: tests
Input → expected output
Missing → 3 None → 3
0 → 0 2 → 2
Bug-ﬁx example · Lecture 6: Coding Agents (slides) ↗ 3

## Slide 4

A successful trajectory
A trajectory τ is one attempt: the agent’s actions and the observations they produce.
Final reward: R(τ) = 1 if all four tests pass; 0 otherwise.
1 Inspect
Read the function
0 becomes 3
→2 Edit
Change default
handling
First patch
saved
→3 Test
Run the four tests
One test still
fails
→4 Revise
Change the code
again
Revised patch
saved
→5 Test again
Rerun the four
tests
All four tests
pass
4

## Slide 5

The RL training loop
Training repeats the loop to increase average reward over many attempts.
Sample
Run the agent on tasks
and collect trajectories τ. →
Score
The veriﬁer assigns each
trajectory its reward R(τ). →
Update
Use the rewards to
change the policy’s
parameters.
Collect new attempts with the updated policy
x is the task (initial state and prompt); θ is the policy’s parameters.
p (τ | x) is the probability of trajectory τ given task x.
Goal J(θ): maximize average reward on task x
θ
J(θ)=E  [R(τ)]τ∼p  (⋅∣x)θ
5

## Slide 6

Reward and the policy update
Plain REINFORCE uses the ﬁnal reward to weight every action in an attempt.
Successful attempt
All four tests pass: R(τ) = 1.
Increase the likelihood of its actions.
Failed attempt
At least one test fails: R(τ) = 0.
This attempt contributes no update.
At step t, action a follows history h: the task, earlier actions, and observations.
π (a | h) is the policy’s probability of that action given the history.
Loss to minimize for one sampled trajectory
How can a failed attempt still provide a learning signal?
t t
θ t t
L  =PG −R(τ)  logπ  (a  ∣
t
∑ θ t h  )t
6

## Slide 7

Credit assignment and
dense feedback
Which actions deserve credit?
7

## Slide 8

Comparing trajectories on the same task
Sample four attempts at the same bug-ﬁx task, then compare their rewards.
Attempt Final tests Reward R(τ) Update weight:
reward − baseline
1 All four pass 1 1 − 0.25 = +0.75
2 At least one fails 0 0 − 0.25 = −0.25
3 At least one fails 0 0 − 0.25 = −0.25
4 At least one fails 0 0 − 0.25 = −0.25
Use the group average as a baseline:
(1 + 0 + 0 + 0) / 4 = 0.25.
Even failed attempts now contribute: their actions get a negative weight.
8

## Slide 9

Rewards for individual turns
A successful trajectory can contain a mistake; a failed trajectory can contain a helpful
turn.
Two illustrative trajectories on the same task. Each action a , …, a  represents one agent turn.
Trajectory A
Success a a
Mistake a a a a R=1
Trajectory B
Failure a a a a
Helpful a a R=0
The group weight is the same for every turn in a trajectory.
Turn-level rewards could tell us which turns to reinforce within each trajectory.
0 5
0 1 2 3 4 5
0 1 2 3 4 5
9

## Slide 10

Reward-to-go from one trajectory
With only a ﬁnal reward, A receives zero at each step until the task succeeds.
History before
Action
Reward after
h
a
r  = 0
h
a
r  = 0
h
a
r  = 1
Starting just before a , how much reward remains on this trajectory?
Add the three remaining rewards, counting each equally
This sum is the reward-to-go R : the rewards received after h .
h
a
r  =  0
0
0
1
h
a
r  =  0
1
1
2
h
a
r  =  0
2
2
3
3
3
4
4
4
5
5
5
6
3
0+0+1=1
3 3
10

## Slide 11

Credit along two trajectories
B receives zero reward at every step. Compare its reward-to-go with A's.
Trajectory A
Success
a
R ₀ =1
a
R ₁ =1
a
R ₂ =1
a
R ₃ =1
a
R ₄ =1
a
R ₅ =1 R=1
Trajectory B
Failure
a
R ₀ =0
a
R ₁ =0
a
R ₂ =0
a
R ₃ =0
a
R ₄ =0
a
R ₅ =0 R=0
Add the remaining rewards: at every action, R = 1 on A and R = 0 on B.
How can we estimate which turns helped when we only observe the ﬁnal reward?
0 1 2 3 4 5
0 1 2 3 4 5
t t
11

## Slide 12

Expected reward-to-go from a history
Imagine continuing ten times from B's history h , using the same rollout policy μ.
Same h Ten possible continuations →
Reward-to-go from each continuation (illustrative)
0 1 0 0 1 0 0 0 1 0
Three continuations have R  = 1. The average is 3 ÷ 10 = 0.3.
Value: the average over all possible continuations under μ
The bar means “given h .” Ten samples give an estimate of this average.
3
3
3
V (h  )=μ 3 E  [R  ∣μ 3 h  ]3
3
12

## Slide 13

Learning the value function
Train a critic to predict reward-to-go from the history, using squared error.
Its prediction is V (h), with learned parameters φ. Reuse the ten outcomes at h : three 1s and seven 0s.
If Vφ(h ₃ ) = 0.6, its average squared error is
The best prediction for these samples is their mean, 0.3 (squared error 0.21).
Minimize over φ; E ₜ  averages histories from sampled rollouts
φ 3
 =10
3(0.6−1) +7(0.6−0)2 2
0.30
L (ϕ)=V E  V  (h  )−R  
t[( ϕ t t)2]
Squared-error baseline training · Ranzato et al., ICLR 2016 · §3.2.1 ↗ 13

## Slide 14

Modeling the value function
A critic can use its own network or read the policy's hidden representation.
Separate value network
History h
↓
Value network φ
Own body and output layer
↓
Prediction V (h)
Value loss trains the whole value network.
Example: InstructGPT.
Value head on policy body
History h
↓
Policy body (part of θ)
↓ stop-gradient
Linear value head φ
↓
Prediction V (h)
Value loss trains only the head.
Example: MIXER (Ranzato et al.).
Stop-gradient blocks the value loss from updating the policy body. The policy loss still trains it.
t
φ t
t
φ t
InstructGPT · Ouyang et al., 2022 · App. C.4 ↗ MIXER · Ranzato et al., 2016 · §3.2.1 ↗ 14

## Slide 15

One-step change in value
Here, rewards are zero. Compare the critic’s value before and after each action.
Trajectory B · ﬁnal three actions
a
Before V (h ) = 0.3
Reward r  = 0
Next V (h ) = 0.6
0 + 0.6 − 0.3 = +0.3
a
Before V (h ) = 0.6
Reward r  = 0
Next V (h ) = 0.4
0 + 0.4 − 0.6 = −0.2
a
Before V (h ) = 0.4
Reward r  = 0
Next V (h ) = 0.0
0 + 0.0 − 0.4 = −0.4
B ends after a , so no future reward remains at h : V (h ) = 0.
Temporal-diﬀerence (TD) error, with no reward discounting
3
φ 3
4
φ 4
4
φ 4
5
φ 5
5
φ 5
6
φ 6
5 6 φ 6
δ  =t r  +t+1 V  (h  )−ϕ t+1 V  (h  )ϕ t
15

## Slide 16

Generalized advantage estimation
How should later errors aﬀect the credit given to B's a ?
Trajectory B · ﬁnal three actions
a
δ  = +0.3
Weight: 1
a
δ  = −0.2
Weight: 0.5
a
δ  = −0.4
Weight: 0.25
Choose λ = 0.5: each later error gets half the weight of the previous one.
Estimated advantage at a ₃ : combine the three errors
GAE repeats this backward: Â = δ + λÂ . At the end, no later errors remain.
3
3
3
4
4
5
5
 =A^3 0.3+0.5(−0.2)+0.25(−0.4)=0.1
t t t+1
GAE · Schulman et al., ICLR 2016 ↗ 16

## Slide 17

A surrogate: learning value from annotations
A process reward model (PRM) learns step correctness as a surrogate for value.
Here, 5x = 6x − 14 implies x = 14. The annotator marks “x = 7” as incorrect.
Let’s Verify Step by Step · Lightman et al., 2023 · Figure 1 ↗ 17

## Slide 18

Synchronous and asynchronous RL
18

## Slide 19

Waiting in synchronous RL
Every trajectory in a batch must ﬁnish before the policy update starts.
Generate trajectories Update policy Waiting
GPU 1
GPU 2
GPU 3
Generate
Generate
Generate
Wait Update
Update
Update
Generate
Generate
Generate
Time →
The next batch starts after the policy update.
AReaL · Fu et al., 2026 · §3.2 ↗ 19

## Slide 20

Overlapping rollouts and updates
Async RL lets rollout workers keep generating while the learner updates from completed
trajectories.
Generate trajectories Update policy
Rollout GPU 1
Rollout GPU 2
Learner GPU
Generate
Generate
Generate
Generate
Update 1
Generate
Generate
Update 2
Time →
Some completed trajectories now come from an earlier policy version.
AReaL · Fu et al., 2026 · §4.1 ↗ 20

## Slide 21

Stable policy updates
21

## Slide 22

Rollouts from an older policy
A rollout can ﬁnish after the learner has updated to a newer policy.
Rollout policy μ Learner policy πθ
Check None explicitly
Use get(..., 3)
Keep the original code
μ: sampled the recorded edit. πθ: is being updated now.
The rollout is stale: its actions came from μ, while the learner uses πθ.
0.40
0.70
0.40
0.20
0.20
0.10
22

## Slide 23

Importance sampling
At a ﬁxed history h, reweight a sampled action a by how likely it is under the current
policy.
At a ﬁxed history h
Correct edit
Behavior: 0.40
Current: 0.70
Weight: 0.70 / 0.40 = 1.75
Incomplete edit
Behavior: 0.40
Current: 0.20
Weight: 0.20 / 0.40 = 0.50
R(a) is the ﬁnal reward after taking action a in this example.
E  [R(a)] =a∼π  
θ E   R(a)a∼μ[μ(a∣ h)
π  (a∣ h)θ ]
23

## Slide 24

Long trajectories and stale data
The whole-trajectory ratio w multiplies local mismatches along an agent interaction.
Action a_t follows history h_t; environment dynamics are unchanged
1.05
One action ratio →
1.05¹ ⁰⁰  ≈ 132
Product along a
trajectory
→
High variance
A few samples can
dominate
w(τ ∣ x)=  =p  (τ ∣ x)μ
p  (τ ∣ x)θ
  
t
∏μ(a  ∣ h  )t t
π  (a  ∣ h  )θ t t
CTPO · Zhang et al., 2026 · §3.2 ↗ 24

## Slide 25

Mismatch grows along a response
The cumulative ratio ρ  multiplies action ratios through token t.
Its spread grows at later positions in tool-using math rollouts.
tcum
CTPO · Zhang et al., 2026 · Fig. 1 ↗ 25

## Slide 26

Earlier actions change later histories
The current policy may rarely reach a history that the rollout policy visited.
Earlier edit
Add a None check
μ: 40%   πθ: 10%
→
Recorded history
The code now has thatcheck →
Next action
Run tests
μ: 50%   πθ: 50%
The next-action ratio is 1, but reaching this history is 0.10 / 0.40 = 0.25 as likely.
CTPO · Zhang et al., 2026 · §3.1 ↗ 26

## Slide 27

Which actions enter the weight?
For a response with T actions, ρ is the probability ratio for action t. Methods use
diﬀerent parts of the response.
Method Recorded actions → Weight uses
PPO / GRPO a a a a a Current action
CTPO a a a a a Actions through t
Full ratio a a a a a All actions
GSPO a a a a a All, length-normalized
DAPO and CISPO also use the current-action ratio; their clipping rules diﬀer.
t
0 1 t t+1 T−1
0 1 t t+1 T−1
0 1 t t+1 T−1
0 1 t t+1 T−1
CTPO · Zhang et al., 2026 · Table 1 ↗ DAPO · Yu et al., 2025 ↗ CISPO · MiniMax-M1, 2025 ↗ 27

## Slide 28

Clipping policy updates
28

## Slide 29

Why limit an update?
Stale rollouts can get large weights, letting a few samples dominate an update.
Image Credit: Aditya Soni ↗ 29

## Slide 30

Clipping a probability ratio
The clip function replaces a ratio outside the chosen bounds with the nearest bound.
Here each action is a generated token u; u  is its earlier context.
Ratio for one sampled token
Clipped value: ℓ is lower, u is upper
ℓ = 0.8 u = 1.2 ratio ρ ₜ
0.8
1.2
clipped value c ₜ
t <t
ρ  =t
 
μ(u  ∣ u  )t <t
π  (u  ∣ u  )θ t <t
c  =t clip(ρ  ,ℓ,u)t
PPO · Schulman et al., 2017 ↗ CISPO · MiniMax-M1, 2025 ↗ 30

## Slide 31

PPO and CISPO policy objectives
PPO puts c inside a minimum; CISPO uses it as a ﬁxed weight.
Shared clipped ratio
PPO policy objective to maximize
CISPO policy objective to maximize
E averages sampled tokens; Â estimates whether a token helped. sg holds c ﬁxed for gradients. A loss to
minimize is −J.
t
c  =t clip(ρ  ,ℓ,u)t
J  (θ)=PPO E  min ρ   ,c   
t[ ( tA^t tA^t)]
J  (θ)=CISPO E  sg(c  )  logπ  (u  ∣ u  )t[ t A^t θ t <t ]
t t t
PPO · Schulman et al., 2017 ↗ CISPO · MiniMax-M1, 2025 ↗ 31

## Slide 32

PPO’s clipped objective
PPO stops rewarding increases above the cap and decreases below the ﬂoor.
Positive advantage: A = +1
1.2 ratio
No extra gain above the cap
Negative advantage: A = −1
0.8 ratio
No extra gain below the ﬂoor
For a helpful action, stop rewarding a ratio above1 + ε. For an unhelpful action, stop rewarding a ratiobelow 1 − ε.
In this plot, ε = 0.2 is the clipping margin.
Adapted from PPO · Schulman et al., 2017 · Figure 1 ↗ 32

## Slide 33

Reference-model KL
A KL penalty discourages the policy from drifting far from a ﬁxed reference model.
Policy objective with a reference penalty
Rollout policy μ
Generates the training batch and
supplies the denominator in importance
ratios.
Reference model π
Stays ﬁxed as an anchor while the policy
learns.
J  is the policy objective; D  measures distribution diﬀerence; β sets the penalty strength.
 J  −θmax policy βD  (π  ∥π  )KL θ ref
ref
policy KL
DeepSeekMath · Shao et al., 2024 · GRPO objective ↗ 33

## Slide 34

Entropy for exploration
An entropy bonus rewards a broader next-token distribution.
Policy objective with an entropy bonus
H measures next-token uncertainty; α sets the bonus strength.
A broader distribution can help the agent try other actions.
It does not guarantee that those actions will be useful.
 J  +θmax policy αH(π  )θ
Proximal Policy Optimization · Schulman et al., 2017 · §5 ↗ 34

## Slide 35

A summary of popular algorithms
Compare how each method assigns credit, weights sampled tokens, and limits updates.
Algorithm Weight from reward Learned
critic? Importance ratio Clipping
REINFORCE Reward-to-go R No None: fresh rollouts None
PPO GAE from a critic Yes Current token ρ Minimum of raw and
clipped terms
GRPO Group comparison No Current token ρ Same as PPO
CISPO Group comparison No Current token ρ Clipped ratio as a ﬁxed
weight
GSPO Group comparison No Whole response,
length-normalized
PPO minimum, on the
response ratio
DAPO Group comparison No Current token ρ PPO minimum;
higher upper bound
Group comparison: subtract the group’s mean reward, then divide by its reward spread.
t
t
t
t
t
PPO ↗ GRPO ↗ CISPO ↗ GSPO ↗ DAPO ↗ 35

## Slide 36

Task selection and
reward reliability
36

## Slide 37

Uninformative rollout groups
Sample four trajectories per task. Each group below shows their ﬁnal rewards.
All attempts failed
0 0 0 0
Mean reward: 0
Subtract the mean:
0, 0, 0, 0
Mixed outcomes
0 1 0 1
Mean reward: 0.5
Subtract the mean:
−0.5, +0.5, −0.5, +0.5
All attempts passed
1 1 1 1
Mean reward: 1
Subtract the mean:
0, 0, 0, 0
Recall group advantages: subtract the group's mean reward. Equal rewards all become zero.
An all-zero group gives no outcome comparison. Why did every trajectory fail?
37

## Slide 38

Why did every trajectory fail?
Four failed trajectories give the same rewards: 0, 0, 0, 0. Inspect what happened before
choosing a remedy.
Verifier quality
A valid solution might be
rejected.
Check: the requirements and
failed tests.
Current capability
The model may not yet be
able to solve the task.
Check: whether stronger-
model demonstrations
succeed.
Lack of exploration
All attempts may repeat the
same approach.
Check: whether the
trajectories diﬀer.
38

## Slide 39

False negatives in the verifier
Return to the bug-ﬁx task. This candidate produces every required output.
Missing → 3 ✓ None → 3 ✓
0 → 0 ✓ 2 → 2 ✓
Candidate behavior
All four cases are correct.
Its implementation uses diﬀerent source
code.
Verifier rule
Require the exact phrase
value is None.
The candidate lacks it: reject.
This is a false negative: a valid solution is rejected. Check behavior instead of an incidental wordingchoice.
Related task/test review: SWE-bench Veriﬁed · 2024 ↗ 39

## Slide 40

Result of false negatives
Reward noise
Fitting to spurious changes in the output.
Equivalent solutions receive diﬀerent rewards because of wording or implementation details.
Benchmark saturation
Scores can ﬂatten below 100% when the evaluator rejects valid solutions.
Benchmark Plateau / limit Evidence from the audit
SWE-bench Veriﬁed ≈81% Progress slowed near 80.9%; many remaining
failures had ﬂawed tests.
τ-bench Airline ≈70% Inconsistent tasks limited achievable scores.
τ-bench Retail ≈92% Annotation errors limited achievable scores.
Historical versions, audited in 2025‒26. These are reported plateaus or limits; τ-bench has since corrected the tasks.
SWE-bench audit · OpenAI, Feb. 2026 ↗ SABER · Cuadron et al., 2025 · §5.1 ↗ τ-bench ﬁxes · Feb. 2026 ↗ 40

## Slide 41

False positives and reward hacking
Keep the same task requirements, but suppose training tests only the input retries=0.
def retry_count(config):
    return 0
Candidate: always return zero.
Training verifier
The one tested case passes.
Reward: 1
Input Required output Candidate output
0 0 0 ✓
Missing / None 3 0 ✗
2 2 0 ✗
A false positive rewards an invalid solution. Training can learn to exploit this gap.
41

## Slide 42

Reward hacking in coding agents
A passing score can come from a shortcut that the benchmark was meant to exclude.
Available in the environment Shortcut
Internet access → Find the published solution online.
Git history, including future
commits → Find and copy the later bug ﬁx.
A model API key → Call a diﬀerent, stronger model for answers or
training data.
Access to tests or the test
runner → Make the tests pass without ﬁxing the bug.
Documented API example: a PostTrainBench agent used a grading key to generate training data, despite an
explicit restriction.
Web, Git, and test exploits · MAI-Thinking-1 · §3.3.1, p.43 ↗ API misuse · PostTrainBench · §5.4, Fig.7 ↗ 42

## Slide 43

Independent checks of progress
The constant-zero patch earned training reward 1, but passed only one of the four
required cases.
Training reward
Measures success on the
training veriﬁer
Independent success
Check unseen tasks and
behavior the training
veriﬁer missed
Costs and failures
Inspect tool calls,
regressions, and repeated
actions
If reward rises without independent improvement, inspect trajectories for shortcuts.
43

## Slide 44

DAPO: dynamic sampling
Identical rewards give zero group advantages. DAPO keeps mixed groups and samples
until the batch is full.
Sample four trajectories per task
Each circle is a reward: 0 = failure, 1 = success.
Task A 0 0 0 0 Skip group
Identical rewards
Task B 0 1 0 1 Keep group
Mixed rewards
Task C 1 1 1 1 Skip group
Identical rewards
Task D
New group 0 0 1 0 Keep group
Mixed rewards
→
Training batch
Example target: 2 groups
2 / 2 groups collected
Task B 0 1 0 1
Task D 0 0 1 0
Batch full → update the policy
Keep every trajectory in a mixed group, including its failures.
DAPO · Yu et al., 2025 · §3.2 Dynamic Sampling ↗ 44

## Slide 45

Partial and auxiliary rewards
Partial credit is an auxiliary reward: extra feedback for progress before full success.
Illustrative task: pass all 4 checks. Add 0.25 reward per check passed.
Four trajectories on the same task τ ₁ τ ₂ τ ₃ τ ₄
Checks passed 0 / 4 1 / 4 2 / 4 1 / 4
Success reward 0 0 0 0
Subtract the mean: 0 0 0 0 0
Success + partial reward 0 0.25 0.50 0.25
Subtract the mean: 0.25 −0.25 0 +0.25 0
Diﬀerent partial scores can reduce zero-advantage groups and batches.
45

## Slide 46

Risks of auxiliary rewards
The model may learn to increase the added reward without improving the task.
Intended behavior What the reward favored Observed behavior
Useful tool use A bug gave credit for
superﬁcial web-tool calls.
GPT-5.1 used the browser as a
calculator and acted as though it
had searched.
A playful “Nerdy”
persona
Metaphors with “goblin”
or “gremlin” received
higher scores.
Creature metaphors became
more common, including without
the persona prompt.
Calculator hacking · OpenAI, Dec. 2025 ↗ Where the goblins came from · OpenAI, Apr. 2026 ↗ 46

## Slide 47

Exploration collapse
At one history, training changes the probabilities of three possible actions.
Earlier policy Later policy
Action A
Action B
Action C
Almost every sample now chooses B, so alternatives are rarely tried.
An entropy bonus encourages alternatives; check whether trajectories diﬀer.
0.20
0.01
0.60
0.98
0.20
0.01
DAPO · Yu et al., 2025 · exploration and entropy collapse ↗ 47

## Slide 48

Learning from a teacher
Distillation: match a teacher's action probabilities
48

## Slide 49

Curricula and warm starts
When the student rarely succeeds, a teacher can provide successful trajectories to learn
from.
Demonstrations
First learn from
successful solutions
A warm start
→
Learnable tasks
Practice tasks where
the model sometimes
succeeds
→
Harder tasks
Increase diﬃculty as
the model improves
A curriculum
Keep earlier tasks in the mix, and use a ﬁxed evaluation set to measure improvement.
49

## Slide 50

Distillation
Train a student to match a teacher’s action probabilities on a ﬁxed set of trajectories.
Saved trajectory from the teacher
h a  → h a  → h a  → h
next action here
At this saved history, the teacher assigns 80% to a  and 20% to the other action. Call
this distribution q(· | h ).
When the student acts, its own mistakes can lead to histories missing from this training set.
0 0 1 1 2 2 3
3
3
Knowledge distillation · Hinton et al., 2015 · §2 ↗ Distillation for language models · Agarwal et al., 2024 · §3 ↗ 50

## Slide 51

On-policy distillation
Let the student generate the training histories, then ask the teacher for targets at those
histories.
Student rollout on trajectory B
h a  → h a  → h a  → h
next action here
Example teacher targets at this student history: 80% for a  and 20% for the other
action.
Train the student to match these probabilities. “On-policy” means the histories came from the student'sown rollouts.
0 0 1 1 2 2 3
3
On-Policy Distillation of Language Models · Agarwal et al., ICLR 2024 ↗ 51

## Slide 52

A dense distillation objective
At the same h , suppose the student assigns equal probability to the two actions.
Next-action probabilities a Other action
Student π 0.5 0.5
Teacher q 0.8 0.2
Reverse KL measures probability mismatch (natural logarithms)
Average this KL mismatch over student histories (distribution d ), then minimize:
3
3
θ
0.5log(0.5/0.8)+0.5log(0.5/0.2)≈0.223
μ
L  =OPD E  D  π  (⋅ ∣ h)∥q(⋅ ∣ h)h∼d  
μ[ KL( θ )]
GKD · Agarwal et al., ICLR 2024 · choice of divergence ↗ 52

## Slide 53

On-policy self-distillation
A veriﬁed solution can help a teacher give better targets at the student's own history.
Student rollout on trajectory B
h a  → h a  → h a  → h
next action here
Student input
The task and history h .
Teacher input
The same task and history,
plus a veriﬁed solution.
OPSD uses a frozen copy of the starting model as teacher. Its next-action probabilities train the studentas before.
0 0 1 1 2 2 3
3
Self-Distilled Reasoner · Zhao et al., 2026 · OPSD ↗ 53

## Slide 54

Conclusion
54

## Slide 55

RL takeaways
Useful feedback
Use group comparisons, a
critic, or process rewards
to assign credit.
Stable updates
Know the behavior policy;
control how strongly
samples change the
model.
Reliable rewards
Match task diﬃculty and
verify the behavior you
actually want.
55

## Slide 56

Questions?
Next Class: RL Systems
56

## Slide 57

Notation: the rollout
Symbol Meaning
x, τ, T Task; sampled trajectory; number of actions
h, a History before step t; action at that step
u, u Generated token at position t; earlier context
π , μ Current policy; policy that generated the rollout
p (τ | x), p (τ | x) Probability of the whole trajectory under each policy
R(τ), r , R Final reward; reward after a; reward-to-go from h
t t
t <t
θ
θ μ
t+1 t t t
57

## Slide 58

Notation: learning signals
Symbol Meaning
Â Estimated advantage: how an action compares with expectation
ρ, c One-token policy ratio; its clipped value
ρ , w(τ | x) Ratio through token t; ratio for the whole trajectory
V (h), V (h) Expected reward-to-go under μ; the critic's estimate
δ Reward plus next value, minus current value
γ, λ Reward discount (examples use γ = 1); weight on later errors in
GAE
q, d Teacher's target; histories collected by the student
t
t t
tcum
μ φ
t
μ
58

