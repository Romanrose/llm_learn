# Lecture 8 Slides：文本提取（待核）

- 官方来源：https://www.cmu-agents.com/slides/lecture-08-sft.pdf
- 提取日期：2026-10-03
- PDF SHA-256：1598a8bd9784ec044f89b8951af52bb2f80c0236b73aada0ca4cc3038049c4e3
- 说明：按页提取；图示、公式和布局需对照官方 PDF，文本提取不能替代视觉核验。

## Slide 1

11-768 · AI AGENTS | TRAINING 1
Supervised Fine-Tuning for Agents
Yueqi Song
Language Technologies Institute
T u r n i n g  r e c o r d e d  t r a j e c t o r i e s  i n t o  w e i g h t s
1


## Slide 2

Today
Weight updates as a capability
Trajectories as token sequences
Choosing the trajectories
One format for many datasets
Running the training
Knowing it worked
Handing oﬀ to RL
2

## Slide 3

A trajectory as recorded data
system
harness prompt
user
issue text
assistant
thought + bash
observation
test output
assistant
thought + edit
observation
diﬀ … assistant
submit
The agent received an issue and a couple of tools in a sandbox: bash and a ﬁle editor.
It produced thoughts, commands, and the observations those commands returned.
The repository's own tests decided whether the run succeeded.
Pan et al., 2024 · SWE-Gym, §4.2 ↗ 3

## Slide 4

Methods of updating the agent
LOCATION PROS CONS
Context window
SEP 1
high ﬁdelity to what happened costly, noisy, does not decide what
matters
External artifacts
SEP 3
inspectable, editable, retrievable,
portable
must be induced, selected, and
maintained
Model weights
THIS LECTURE
faster inference, broad behavior
change
slower updates, opaque, model-
speciﬁc
Change the weights once and every call after that gets the new behavior, with nothing extra in the
prompt.
The ﬁrst two rows update in seconds. This row costs a training run every time you change it.
And you cannot open the weights to see what changed, or move the change to a diﬀerent model.
4

## Slide 5

What the trajectories teach
How to write a tool call this harness can actually run.
How to keep going when the conversation gets long, because the trajectories it learned
from were long.
What a tool result looks like, so it waits for one instead of writing one itself.
And whatever else was in the data: extra commentary, repeated commands, one way of
solving a problem where several would work.
5

## Slide 6

The full training pipeline
Pre-training 20T tokens· Nemotron 3 Ultra
Mid-training 1.43T· K2 Horizon
SFT · today 332B· K2 Horizon
RL · Sep 22 → rollouts + rewards no ﬁxed corpus
D r a w n t o t ok e n s c a l e : e v e r y  s t e p  d o w n  i s  f e w e r  t ok e n s ,  e a c h  o n e  m or e  h e a v i l y  c u r a t e d .
Nemotron 3 Ultra ↗ K2 Horizon · Training Overview ↗ 6

## Slide 7

Cold start before reinforcement learning
Supervised ﬁne-tuning
initialize baseline
agent capabilities
Reinforcement learning
develop domain experts at
varying reasoning eﬀort
On-policy distillation
consolidate the experts
into one model
"The SFT stage establishes a high-quality cold-start policy for the subsequent RL stage."
" C ol d  s t a r t "  i s  t h e  c h e c kp oi nt  RL  b e g i n s  f r om .  T od a y ' s  s t a g e  i s  h o w  K 3  m a k e s  t h a t  c h e c k p oi n t  g ood .
In Kimi K3, the model learns to call tools and ﬁnish long tasks during SFT, before any RL.
Some might ask: why not just RL, without SFT? DeepSeek-R1-Zero ran RL directly on the
base model, with no SFT at all.
Their very next model put SFT back in: R1 starts from a few thousand curated examples,
because R1-Zero's answers mixed languages and were hard to read.
Kimi Team, 2026 · Kimi K3, §4.1 ↗ DeepSeek-R1 ↗ 7

## Slide 8

SFT and RL, side by side
SUPERVISED FINE-TUNING REINFORCEMENT LEARNING
learns from recorded trajectories, whoever produced them its own rollouts, scored by a reward
signal a target for every token one number per rollout
needs data and GPUs live environments, sandboxes, a checkable reward
good at learning tool calls, formats, long tasks sharpening what the model can already attempt
stuck when the demonstrations are wrong, narrow, or used up the start is too weak, or the reward cannot be checked
OpenThoughts-Agent, Table 11 ↗ Kimi K3 ↗ Kimi K2, §3.2 ↗ 8

## Slide 9

The training lectures
TOPIC WHEN
Supervised ﬁne-tuning today
Reinforcement learning Sep 22 · Sep 29 · Oct 1
9

## Slide 10

Trajectories as token sequences
10

## Slide 11

The chat template applied to the trajectory
system
harness prompt
user
issue text
assistant
thought + bash
observation
test output
assistant
thought + edit
observation
diﬀ … assistant
submit
one token sequence · every boundary above is a template token
<|im_start|>tool ↵ 3·failed,·41·passed ↵ <|im_end|> ↵ <|im_start|>assistant
↵ The·test·compares·floats.·Fix·it. ↵ <tool_call> ↵ str_replace(...) ↵
</tool_call> ↵ <|im_end|>
“·” = space, “ ↵ ” = newline
Feed the trajectory through the template and you get one string of tokens.
The <|…|> markers are single special tokens. The rest is what the agent wrote and saw.
Transformers · chat templating ↗ Kimi K3 · XTML, §4.1.1 ↗ 11

## Slide 12

Which tokens carry the loss
system
harness prompt
user
issue text
assistant
thought + bash
observation
test output
assistant
thought + edit
observation
diﬀ … assistant
submit
loss computed context only
Cross-entropy over the assistant tokens only
L(θ) = −  logp  x  ∣ x  
t:m  =1t
∑ θ( t <t)
Mask: one bit per token, saying whether that token's prediction counts.
Minimizing it raises the probability of each recorded action, given everything before it.
Observations are conditioning context, not prediction targets.
12

## Slide 13

How the mask is built
Render
the template writes the conversation as
one string and notes where each assistant
span starts and ends
→
Tokenize
those character positions become token
positions
→
Mask
tokens inside an assistant span get a 1,
everything else a 0
The template does the bookkeeping as it writes: where assistant text starts, where it
stops.
By the time training starts, the roles are gone. The trainer sees the string and the bits,
nothing else.
Transformers · apply_chat_template ↗ 13

## Slide 14

Masking controls across frameworks
FRAMEWORK WHAT YOU SET HOW THE MASK IS PRODUCED
TRL assistant_only_loss=True the template marks the assistant spans as
it renders
Axolotl roles_to_train,
train_on_eos
ﬁnds each turn’s role header in the
rendered string
LLaMA-Factory train_on_prompt,
mask_history
tags whole turns as train-or-ignore while
encoding
Same decision in all three. Only TRL puts it in the template.
TRL · SFTTrainer ↗ Axolotl · conversation formats ↗ LLaMA-Factory · data args ↗ 14

## Slide 15

The end-of-turn token
<|im_start|>assistant ↵ I'll·run·the·failing·test. ↵ <tool_call> ↵
bash(cmd="pytest·-q") ↵ </tool_call> ↵ <|im_end|> ↵
“·” = space, “ ↵ ” = newline · red = loss computed, gray = context only
The role header is supplied at inference. It is never a
target.
The model produces the stop token, so it has to be inside the
mask.
"End of turn" is three events, not one: end this message, hand oﬀ to a tool, or ﬁnish the task. Kimi K3's template spells them apart
with separate tokens:
[open]message·role=assistant[sep] [open]think[sep] … [close]think[sep]
[open]response[sep] Use·math.isclose. [close]response[sep] [end_of_msg]
"the model may not learn to stop."
TRL · training chat templates ↗ TRL · SFTTrainer source ↗ Kimi K3 · XTML, §F ↗ 15

## Slide 16

Masking the reasoning block
<|im_start|>assistant ↵ <think> ↵ The·assert·compares·floats. ↵ </think> ↵
Use·math.isclose. ↵ <|im_end|>
“·” = space, “ ↵ ” = newline · red = loss computed, gray = context only
Two switches, set separately: does the reasoning stay in the context, and does it get
trained on.
In the context, the reasoning explains the action that follows. Trained on, it becomes
the style the model itself writes.
Nemotron keeps budget-truncated reasoning in the context, and masks the artiﬁcial
cut-oﬀ out of the loss.
NVIDIA, 2026 · Nemotron 3 Ultra, §3.1.1 ↗ 16

## Slide 17

Weighting inside the assistant turn
Two components from one paper: SSB is a learned weight
that rebalances reasoning tokens against tool-call tokens in
the loss, and HDR resamples the hard examples.
Long reasoning dominates the loss, and the
short tool call is what you actually need
correct.
Rebalancing helps more on multi-turn than on
single-turn, on both base models.
Hao et al., 2025 · BalanceSFT, Table 5 ↗ 17

## Slide 18

Samples versus tokens
They chose the mixture by counting examples. The loss is computed per token.
The mixture was balanced by counting examples, but STEM and coding traces run far
longer, so they take nearly all the tokens.
Whatever you balance by counting trajectories, check what it turned into in tokens.
Microsoft AI, 2026 · MAI-Thinking-1, Table 10 ↗ 18

## Slide 19

Open problems in supervising a trajectory
We could not ﬁnd a published experiment that changes the mask for agent SFT and
measures what happens.
The careful masking experiments are single-turn instruction tuning, not agents.
The one case where unmasking the prompt helped had long prompts, short answers,
and little data. Agent trajectories are the opposite on all three.
At 8B scale this experiment is cheap, and it is sitting there unrun.
Chatterjee et al., 2025 · WIT ↗ Shi et al., 2024 · Instruction Modelling ↗ 19

## Slide 20

Choosing the trajectories
20

## Slide 21

Where the trajectories come from
WHO RAN THE TASK YOU KEEP EVERYTHING YOU KEEP THE RUNS THAT PASSED
a stronger model ran it plain distillation SWE-Gym · Nemotron · OT-Agent
the model ran it itself MAI, on its own reasoning runs expert iteration · Sep 22
Most agent SFT data sits in the top right box: a stronger model writes better trajectories
than the student could, and the task's own tests make keeping the good ones cheap.
In the bottom row the model makes its own training data. Repeat that loop and you get
expert iteration, which will be covered in future lectures.
21

## Slide 22

Distillation from a stronger model
SEP 10  GPT-4o and Claude ran the SWE-Gym tasks; 491 runs passed the repository tests.
A 32B Qwen model was ﬁne-tuned on those 491 runs alone.
Its scores on both SWE-Bench splits rose by more than ten points.
Pan et al., 2024 · SWE-Gym, §4.2 and Table 3 ↗ 22

## Slide 23

Trajectory count and saturation
Same task set throughout. Only the number of sampled
trajectories changes.
Accuracy was still rising when the sampling
budget ran out.
They had tasks to spare. What they ran out of
was compute to sample more runs.
Every point in this plot uses the same tasks.
What happens when you add new tasks comes
a few slides later.
Pan et al., 2024 · SWE-Gym, §5.2 and Figure 5 ↗ 23

## Slide 24

Undesirable behaviors in successful rollouts
read, never edited edit‒test loop print( in the patch
system
harness prompt
user
issue text
assistant
thought + bash
observation
test output
assistant
thought + edit
observation
diﬀ … assistant
submit
"would teach undesirable behaviors if used directly as SFT data"
Every run on this slide passed its tests.
But look at how: one edited and re-ran tests in a loop for most of its turns, another left
print statements in the ﬁnal patch.
The loss copies every action, good or not. Train on these runs and the model learns the
mess together with the ﬁx.
NVIDIA, 2026 · Nemotron 3 Ultra, §3.1.1 ↗ 24

## Slide 25

Filtering rollouts by shape
The best ﬁlter here just counts turns and drops every run shorter than ﬁve.
Turn count says how much work a run took, not whether the work was any good.
A four-turn clean ﬁx gets dropped. A forty-turn mess gets kept. On average it still helped.
Raoof et al., 2026 · OpenThoughts-Agent, Table 7 ↗ 25

## Slide 26

Choosing the teacher
The paper reports GPT-5.3-Codex was the strongest of these ﬁve models on the
benchmarks themselves. Its runs produced the weakest student.
Leaderboard rank told them the wrong thing here. Trying two teachers and keeping the
better student is cheap by comparison.
Raoof et al., 2026 · OpenThoughts-Agent, Table 6 ↗ 26

## Slide 27

Task sources
The choice of task source changed results the most.
Diﬀerent sources help diﬀerent benchmarks, so spend your eﬀort here before tuning
anything else.
Mix the best four to eight sources. Going wider than that did not help them.
Raoof et al., 2026 · OpenThoughts-Agent, Table 2 ↗ 27

## Slide 28

Scaling the data
Both curves start from the same 10K dataset and diﬀer only in where the extra data
came from.
The pink curve adds more runs of the same tasks, and it ﬂattens out. The blue curve
adds new tasks, and it keeps climbing.
Raoof et al., 2026 · OpenThoughts-Agent, Figure 3 ↗ 28

## Slide 29

Discussion
A. A short run that solved the issue in four turns.
B. A long run that made a wrong edit, saw the test fail, and recovered.
C. A run that solved the issue after eleven attempts that changed nothing.
T h r e e  r u ns  o f  t h e  s a m e  t a s k j u s t  c a m e  b a c k .  Y ou  a r e  d e c i d i n g  w h a t  g oe s  i n t o t h e  t r a i n i n g  s e t .
Which of these do you keep?
For the ones you keep, which actions carry the loss?
Which of your answers would a minimum-turns ﬁlter get wrong?
29

## Slide 30

One format for many datasets
30

## Slide 31

Heterogeneity across agent datasets
Each dataset was built by a diﬀerent group, in its own format.
For a web page, some save the HTML and others save the accessibility tree.
To train on two of them together, you ﬁrst write two customized converters.
Song et al., 2026 · Agent Data Protocol, Table 1 ↗ 31

## Slide 32

One representation for a trajectory
You read each dataset once and rewrite it as typed actions and observations.
For the web page we just saw, keep the HTML and the accessibility tree, instead of
picking one.
Each dataset converts once, each harness once, not once per pair.
Song et al., 2026 · Agent Data Protocol, ICLR oral ↗ 32

## Slide 33

Harness-specific rendering
Once the data is in one format, you still have to write it back out for the harness you are
training for.
OpenHands, SWE-Agent and AgentLab take diﬀerent actions, so the same trajectory comes out
looking diﬀerent in each.
This is also where you set the system prompt and decide what to do when the context gets
long.
Then you check the result: do the tool calls parse, does each call come with a thought, does the
conversation end the way it should.
Song et al., 2026 · Agent Data Protocol, §3.3 ↗ 33

## Slide 34

Diversity versus task-specific data
Same harness, same model, same evaluation. Only the training mixture changes.
Train on the mixture and you beat the matching single-domain set, even on that domain's own
benchmark.
Song et al., 2026 · Agent Data Protocol, cross-task transfer ↗ 34

## Slide 35

Running the training
35

## Slide 36

Real SFT configurations
SEQUENCE BATCH LEARNING RATE
Nemotron 3 Ultra packed 294,912 then 515,000 64 1.5e-5 → 1e-6
MAI self-distillation packed 128k 2,048 1.7e-5 → 5.2e-6, 2% warmup
K2 Horizon 512K, three phases — decayed on a high-quality subset
Nemotron 3 Ultra, §3.1 ↗ MAI-Thinking-1, §3.1.4 and §3.5 ↗ K2 Horizon model card ↗ 36

## Slide 37

Expert routing during SFT
broad pre-training mix narrow agent SFT set
tokens per expert tokens per expert
The frontier models in this lecture are mixtures of experts. The models the public
papers ﬁne-tune are dense.
Fine-tune an MoE on narrow agent data and a few experts take most of the tokens, like
the right panel.
MAI's ﬁx: balance the routing hard during the supervised stage, a thousand times harder
than during RL, and raise dropout to 0.15.
Microsoft AI, 2026 · MAI-Thinking-1, §3.1.5 ↗ 37

## Slide 38

Packing whole conversations
pack 1 19k run 15k run 11k run 8k run unused
pack 2 29k run 17k run 7k run unused
T r a i ni ng  r u ns  on ﬁ x e d - l e ng t h  s e q u e n c e s .  P a c k i n g  ﬁ l l s  e a c h  on e  w i t h  s e v e r a l  c on v e r s a t i on s ,  i n s t e a d  o f  p a d d i n g  m o s t  o f  i t  a w a y .
Each conversation is assigned to the pack whose remaining capacity it most tightly ﬁts.
No conversation is split or truncated, which is a deliberate choice against hallucination.
Identical prompts are kept out of the same pack, and packs are shuﬄed afterwards.
NVIDIA, 2026 · Nemotron 3 Ultra, §3.1.2 ↗ 38

## Slide 39

Template drift
"The chat template should always match the format the model was trained with."
The template you train with has to be the template you serve with, down to the
whitespace.
Render the same trajectory twice, once with a tool message after it and once without,
and you can get two diﬀerent strings.
When a tool message is appended, a conditional thinking block changes the earlier
assistant turn, and the preﬁx no longer matches.
Transformers · writing chat templates ↗ TRL · training chat templates ↗ 39

## Slide 40

Released training artifacts
K2 Horizon's model card has a stage-by-stage training table: steps, tokens, sequence
length, and what each phase was for. That table is where the numbers on the
conﬁgurations slide came from.
It also links the Weights & Biases run, so you can look at the actual loss curves, and it
ships intermediate checkpoints for every stage.
Nemotron released the post-trained checkpoints together with the training data and the
recipe.
Reading one of these teaches a lot.
Nemotron 3 Ultra ↗ K2 Horizon ↗ 40

## Slide 41

Knowing it worked
41

## Slide 42

The mismatch between training and running
DEMONSTRATED
ITS OWN RUN
same preﬁx
issue + ﬁrst edit
edit A
the recorded one
tests pass
expected observation
submit
task complete
edit B
p l a u s i b l e ,  d i ﬀ e r e n t tests fail
u n e x p e c t e d  o b s e r v a t i o n now what
n o t  i n  t h e  d a t a
Training grades one action at a time, always continuing the recorded run.
Deployed, there is no recording. Every action the model takes changes what it sees next.
One diﬀerent edit and it is in a state no training run ever visited. Low loss promised
nothing about what happens there.
Ross et al., 2011 · DAgger ↗ 42

## Slide 43

Evaluation in the target harness
Before trusting any number, check that you can overﬁt twenty examples. If the loss will
not drop, the bug is upstream.
Then evaluate by running the model in a harness, on tasks with checkable outcomes.
Read published numbers carefully. Sometimes they are the best of several harnesses.
Match the split to the claim. Keep all runs of one task on the same side, and split by
repository if you want to say it generalizes to new ones.
OpenThoughts-Agent, Table 1 ↗ SWE-Gym, §5.2 ↗ 43

## Slide 44

Robustness across harnesses
Trajectories collected in one system teach that system's conventions along with the
task.
Collecting across several harnesses is how labs avoid training a model that only works
in one.
NVIDIA, 2026 · Nemotron 3 Ultra, §3.1.1 ↗ 44

## Slide 45

Regressions outside the target domain
Train on one capability and you move the others, whether or not you measure it.
Your mixture is the control here, and balancing it by examples is not the same as
balancing it by tokens.
So evaluate the things you were not trying to improve, too.
Microsoft AI, 2026 · MAI-Thinking-1, §3.5 ↗ 45

## Slide 46

Handing off to RL
46

## Slide 47

How much SFT before RL
"RL provides the most gains when the SFT model is selected with RL in mind."
RL applied to no SFT at all barely moves the base model.
SFT alone stops well short of what the pair reaches.
The winning recipe starts RL from a checkpoint that was deliberately not trained to its
own best score.
OpenThoughts-Agent, Table 11 ↗ MAI-Thinking-1, §3.1.4 ↗ 47

## Slide 48

Questions
N e x t  c l as s  ·  T r ai n i n g  2 :  R e i n f or c e m e n t  L e a r n i n g  B a s i c s
48

## Slide 49

Backup · Exact masking flags
FRAMEWORK FLAG BEHAVIOR
TRL assistant_only_loss=True needs {% generation %} markers; known
families get patched templates
TRL completion_only_loss prompt‒completion datasets; on by default
there
Axolotl roles_to_train:
["assistant"]
default; loss on the listed roles only
Axolotl train_on_eos: turn the EOS of each trained turn is in the loss
LLaMA-Factory train_on_prompt: false default; prompt tokens masked
LLaMA-Factory mask_history: true last turn only; truncation keeps the ﬁnal
turn
49

