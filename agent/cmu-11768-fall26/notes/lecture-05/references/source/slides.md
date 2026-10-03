# Lecture 5 Slides：文本提取（待核）

- 官方来源：https://www.cmu-agents.com/slides/lecture-05-planning.pdf
- 提取日期：2026-10-03
- PDF SHA-256：32271dff69a87f555fe82a192d5cd20ac058b3266bc965e8a5411897781f8adf
- 说明：按页提取；图示、公式和布局需对照官方 PDF，文本提取不能替代视觉核验。

## Slide 1

Planning and Task Decomposition
Daniel Fried
11-768: AI Agents
H o w  a g e n t s  d e c i d e  w h a t  t o  d o .  P l u s ,  a  b i t  o f  m u l t i - a g e n t .
1


## Slide 2

A reactive agent on a long task
TASK
Buy the lab's new GPU workstation: compare conﬁgurations and prices across vendor sites, check compatibility
against the cluster requirements on the internal wiki, and ﬁle the purchase requisition.
1 ACTION goto vendor-a.com → Workstations → spec sheet → GPU
comparison ...
15 ACTION configure: 2× RTX 6000, 128 GB RAM, 850 W PSU
31 OBSERVE wiki: “racks accept 4U chassis; each slot with 1600 W”
context compacted · 128k → 14k tokens.
four vendors searched: only D fits, but has 20-week lead time
201ACTION pick D? look for a fifth vendor? relax a requirement?
202ACTION goto procurement portal → New requisition → Submit
1 Four independent searches run
as one thread in one context.
2 The four sites it chose all come
back and none is great.
3 It picks one anyway and ﬁles the
requisition.
2

## Slide 3

Structure in a long task
Vendor A
Vendor B
Vendor C
Vendor D
Vendor E
Compatibility
check (wiki) Requisition
arrives later
irreversible
replan
The task has parallel searches, dependencies, information that arrives later in the task, and a step that cannot be undone.
The graph itself also changes: when none of the four vendors ﬁts, a ﬁfth search has to be added.
TODAY'S QUESTIONS
Value
When is planning useful?
When can it hurt?
Representation
How is a plan
represented?
Commitment
When is a plan made, and
what may change it?
Oversight
How/when should a
person weigh in?
3

## Slide 4

Plan Mode in coding agents
read-only
investigation → clarifying
questions → written
plan → human
review → execution
Cursor, Claude Code, and Codex all introduced a
Plan Mode: write a persistent plan, have a
human verify it, carry it out (possibly with sub-
agents, in parallel).
Possibly helpful: more compute, better context,
an external artifact, decomposition, or the
human approval.
Cursor · “Introducing Plan Mode,” 2025 ↗ Claude Code permission modes ↗ OpenAI model guidance ↗ 4

## Slide 5

What is a plan (for LLM agents)?
WORKING DEFINITION
A plan is an explicit representation of intended future behavior: the actions or
subgoals an agent will attempt, with any ordering or dependencies among them.
A plan is for this task. (versus a skill, which provides reusable guidance across tasks). Plans can
be more speciﬁc than skills.
A plan organizes future work. It may specify actions or subgoals, along with their ordering and
dependencies.
A plan is a proposal, not a guarantee. It can be inspected and revised: by the user, another
model, or interactions with the environment.
“Everybody has a plan until they get punched in the mouth.” — Mike Tyson 5

## Slide 6

Planning across the course
Topic Lecture
Prompted plans and harness structure: decomposition,
replanning, plan artifacts This lecture
A ﬁxed workﬂow for coding (Agentless) Coding agents
Multi-agent roles and communication Interaction 1
Clariﬁcation and human approval Interaction 2
Search over plans and predicted futures; MACU and RAO
revisited Search 1‒2
6

## Slide 7

Decomposition before acting
“ W e e k s  o f  p r o g r a m m i n g  c a n  s a v e  y o u  h o u r s  o f  p l a n n i n g . ”  —  p r o g r a m m e r  p r o v e r b
7

## Slide 8

Chain-of-thought is a plan
KOJIMA ET AL. 2022 WANG ET AL. 2023
Provides extra compute and a scratchpad for the model to refer back to
Plan and solution arrive in one model generation. Nothing explicitly inspects the plan.
The CoT can be trained to increase the probability of a correct answer (STaR, Zelikman et al.; DeepSeek
R1).
Q: [problem]
A: Let's think step by step.
Q: [problem]
A: Let's first understand the problem and
devise a plan to solve the problem. Then,
let's carry out the plan and solve the
problem step by step.
Kojima et al. · NeurIPS 2022 ↗ Wang et al. · ACL 2023 ↗ Zelikman et al. (STaR) · NeurIPS 2022 ↗ DeepSeek-AI (DeepSeek-R1), 2025 ↗ 8

## Slide 9

Decomposing before solving
Separate out planning fom
solving:
Stage 1 writes subquestions.
Stage 2 answers them in order
and passes answers forward.
Models struggled at
answering complex questions
but were better at answering
sub-questions.
Answering sub-questions
requires less context.
Improvements grow with
problem length.
Least-to-Most · Zhou et al., ICLR 2023 · Figure 1 ↗ Recursive Language Models · Zhang et al., 2025 ↗ 9

## Slide 10

Decomposition allows modularity
A decomposer generates sub-tasks and routes each sub-task to a dedicated handler.
What awards have movies produced by people born in 1910 won? ->
Who were born in the year 1910? simple QA + For which moves was #1 the producer? position QA + ...
Modularity allows improving handler models independently: via in-context demonstrations or
training.
Programmatic/structured control: we'll see this later on with RAO, RLM, and MACU.
Decomposed Prompting · Khot et al., ICLR 2023 · Figure 1 ↗ 10

## Slide 11

Plans that act on the world
" W e ' l l  b u r n  t h a t  b r i d g e  w h e n  w e  c o m e  t o  i t . "
11

## Slide 12

Reasoning versus acting
A CoT reasoning step
changes only text
can be undone by writing more
every intermediate is visible
plans are useful if the model can
condition on them better
An action in the world
changes the state the agent meets next
can reveal information
can fail
can be irreversible: submit, send
Acting means plans must handle feasibility, consequences, information, and recovery.
12

## Slide 13

Classical planning
A state is a set of predicates;
actions have preconditions
and eﬀects.
A valid sequence of actions
satisﬁes every action's
preconditions.
Planning is a search problem:
ﬁnd a sequence of valid
actions that reach the goal.
states
on-table(x) · on(x, y)
clear(x) · holding(x)
hand-empty
actions
pick-up(x) · unstack(x, y)
put-down(x) · stack(x, y)
preconditions + eﬀects
pick-up(x): on-table(x) ∧ clear(x) ∧ hand-empty
→ holding(x) ∧ ¬on-table(x) ∧ ¬hand-empty
initial state + goal
on(blue, orange) · clear(red, blue, yellow)
goal: on(orange, blue)
plan
unstack(blue, orange)
put-down(blue)
pick-up(orange)
stack(orange, blue)
PlanBench · Valmeekam et al., NeurIPS 2023 Datasets & Benchmarks · p. 6 ↗ STRIPS · Fikes and Nilsson, Artificial Intelligence 1971 ↗ 13

## Slide 14

What is hard has changed
With LLMs everything is implicit!
For an LLM agent, writing a plausible plan is easier, and knowing whether its
model of the world is correct is harder.
So agent design uses less deep search, and more checking the world: observation,
veriﬁcation, and recovery from errors.
But search, and action applicability, are still useful concepts
14

## Slide 15

Plan representations
Formal plans are checkable; language plans are
general. Programs are in-between.
Line of work in ~2023: use a code LLM to write
code that calls perception and control APIs
The program runs and can be inspected, but is
limited by what its APIs and programmatic
structure allow.
... but, APIs could call an LLM or another neural
model
Code as Policies · Liang et al., ICRA 2023 ↗ ProgPrompt · Singh et al., ICRA 2023 ↗ Binder · Cheng et al., ICLR 2023 ↗ 15

## Slide 16

Why replan while acting?
DECISIONS MADE BEFORE EXECUTION DECISIONS MADE DURING EXECUTION
Developer-deﬁned workﬂow
The developer speciﬁes the procedure:
check a ﬁxed vendor list.
Agentless (next lecture)
→
Plan-then-execute agent
The model plans which vendors to check,
then commits before execution.
plan-then-execute
→
Adaptive agent
After four vendors fail, execution feedback
leads the model to search for another.
RAO · MACU
DEVELOPER-DEFINED PROCEDURE Committing to a plan up front is faster,
cheaper, and more predictable.
Replanning lets the model adapt when
execution reveals new information.
Use replanning when that feedback is
worth the extra cost and complexity.
for v in VENDORS:               # fixed list
    specs[v] = read_specs(v)    # model call
ok = [v for v in specs if fits(v)]
requisition(cheapest(ok))
Anthropic · “Building effective agents,” 2024 ↗ 16

## Slide 17

Reasons to add planning
structure
mod u l a r i t y  ·  f e e d b a c k  ·  l o n g  h o r i z o n s  ·  c o n t r o l
“Plan to throw one away; you will, anyhow.” — Fred Brooks, The Mythical Man-Month
17

## Slide 18

Planning pressures in the workstation task
GPU WORKSTATION PROCUREMENT
Search vendor A
Search vendor B
Search vendor C
Search vendor D
Check conﬁgurations
against the wiki
Submit purchase
requisition
MODULARITY
Searches carried out separately.
Search another vendor
FEEDBACK
None ﬁts, so revise the plan.
LONG HORIZON Requirements and progress persist across the whole task.
CONTROL
A person approves
before the agent submits.
18

## Slide 19

Separating planner from executor
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
Separate modules can use diﬀerent models and training data.
Planner model (GPT-4o) is visually grounded but
bad at producing pixel-level actions: describe the
next action in language.
A separately trained 7B executor model maps that
description to screen coordinates.
UGround · Gou et al., ICLR 2025 · Figure 2 ↗ Agent S · Agashe et al., ICLR 2025 ↗ 19

## Slide 20

Training the planner
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
Have a teacher
model segment and
label successful
trajectories to
produce a plan.
Fine-tune a planner
model and an
executor model on
these annotated
trajectories.
Plan-and-Act · Erdogan et al., ICML 2025 · Figure 3 ↗ 20

## Slide 21

Beware of fixed roles and multi-agent systems
Role decompositions for coding have had limited success.
Roles are ﬁxed before the task arrives: the
veriﬁer cannot localize a fault to check its own
answer.
Handoﬀs are summary reports, which can drop
context the next agent needs.
Don’t Sleep on Single-agent Systems · Neubig, 2024 ↗ CodeR · Chen et al., 2024 · Figure 1 ↗ 21
Graham
Neubig

## Slide 22

Modeling affordances
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
Recall classic planning:
actions have pre-conditions.
Learn a value function for
each robotic skill, which
predicts probability of
completing it.
Multiply this value with the
probability from the LLM
producing the plan.
SayCan rescores sub-tasks in the plan using a model of skill aﬀordances.
SayCan · Ahn et al., CoRL 2022 · Figure 3 ↗ Zero-Shot Planners · Huang et al., ICML 2022 ↗ 22

## Slide 23

Replanning on environmental feedback
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
LLM-Planner · Song et al., ICCV 2023 · Figure 1 ↗ Inner Monologue · Huang et al., CoRL 2022 ↗ SwiftSage · Lin et al., NeurIPS 2023 23

## Slide 24

Thinking vs acting
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
Match compute across three
diﬀerent inference methods.
Produce longer CoTs, sample
multiple candidates, or interact
more with the environment.
"You just signaled task
completion. Let's pause and
think again."
Scaling interaction allows
obtaining more information
from the environment, like
Reﬂexion.
Test-Time Interaction · Shen et al., NeurIPS 2025 · Figure 3 ↗ 24

## Slide 25

Overthinking
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
Patterns: analysis paralysis, rogue action
chains, premature disengagement.
More overthinking predicts less issue resolution
across model types.
Cuadron et al., 2025 · Figures 1 and 4 ↗ 25

## Slide 26

Thinking vs looking
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
WHAT THE AGENT DOES NOT KNOW
Every ﬁle has a hidden format with
three parts:
delimiter , ; \t
quote character " '
header rows to skip 0 1
Twelve combinations, and the ﬁle only parses if
all three are right. The ﬁlename is the only clue:
sales_fr.tsv points to a tab.
Calibrate-then-Act · Ding, Tomlin, Durrett, 2026 · Figure 1 ↗ PPP-Agent · Sun et al., COLM 2026 ↗ 26

## Slide 27

Calibrating confidence before acting
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
WHAT CTA ADDS TO THE PROMPT
Additional context:
 • Estimated format likelihoods
   are provided below.
 
Format likelihoods:
{prior}
What the model then reads out of it:
The delimiter is most likely to be ';' with a
probability of ~0.85 … But I'm not 100% sure,
so maybe I should run some unit tests to
conﬁrm.
Calibrate-then-Act · Ding, Tomlin, Durrett, 2026 · Figure 2 ↗ 27

## Slide 28

Long-horizon failures
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
Vending-Bench: run a simple business for a long time.
Task: price, order, and restock a vending machine.
Horizon: up to 2,000 messages—about 25M tokens and
up to 222 simulated days.
Later actions condition on the agent’s earlier mistake.
Was this just a bad plan?
One temporary error aﬀects every later
decision.
PREMATURE RESTOCK
Due today ≠ already delivered
The environment correctly reports: items unavailable.
↓
WRONG INFERENCE
“Unavailable now” → “business failed”
The agent never waits for the fulﬁllment email or
checks again.
↓
ERROR PERSISTS
Daily fee becomes “fraud”
Subject: EMERGENCY: Unauthorized Fees After
Business Termination
Vending-Bench · Backlund and Petersson, 2025 · Tables 3‒4 ↗ 28

## Slide 29

Execution horizon
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
Better step accuracy extends the horizon, while self-conditioning can make later steps less accurate.
Sinha et al., 2025 · Figure 1 ↗ 29

## Slide 30

Model size and execution horizon
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
Larger models execute longer tasks but self-condition more. Can reinforcement learning ﬁx this?
Sinha et al., 2025 · Figure 1 ↗ 30

## Slide 31

Decomposing adaptively and recursively
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
Delegation is an action, so it can be
trained.
The agent calls
launch_subagent(goal) to run a
copy of itself on a subtask, and that
copy can do the same.
Each node is scored on its own task
plus how often its children
succeeded.
Trained on medium tasks only, it
delegates deeper on hard ones.
RAO · Gandhi et al., 2026 · Figures 1 and 7 ↗ Recursive Language Models · Zhang et al., 2025 ↗ ADaPT · Prasad et al., NAACL Findings 2024 31
Apurva Gandhi


## Slide 32

Plans as security boundaries
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
ReAct lets every page inﬂuence the next action,
creating an injection path.
A program can accept values from pages
without accepting new actions.
Piet et al., 2026 · Figure 1 ↗ 32

## Slide 33

Control: human editing and approval
Cursor
In tro d u c in g  P la n  M o d e
In tro d u c in g  P la n  M o d e
Watch on
Cursor · Introducing Plan Mode ↗ 33

## Slide 34

Global constraints
Some constraints span every subtask.
Flights, hotels, food, and attractions
decompose cleanly.
Budget, transport, and diet remain global—and
are often violated across pieces.
TravelPlanner · Xie et al., ICML 2024 · Figure 1 ↗ 34

## Slide 35

Multi-agent computer use
P u t t i n g  i t  a l l  t o g e t h e r
35

## Slide 36

Example task: finding ACL surgeons
Odysseys · Jang, Koh, Fried, Salakhutdinov, 2026 ↗ 36
Lawrence Jang
 Jing Yu Koh

## Slide 37

Example task: finding ACL surgeons
Odysseys · Jang, Koh, Fried, Salakhutdinov, 2026 ↗ 37
Lawrence Jang
 Jing Yu Koh

## Slide 38

Long-horizon computer use
Modularity
decompose and specialize
Feedback
replan when needed
Long horizon
limit context
Control
separate authority
MACU · Koh, Salakhutdinov, Fried, 2026 ↗ 38
Jing Yu Koh

## Slide 39

0:00/ 0:23
39

## Slide 40

Where multiple agents help
MACU · Koh, Salakhutdinov, Fried, 2026 · Table 1 ↗ 40

## Slide 41

Stronger managers improve coordination
O S W O R L D  A B L A T I O N  ·  3 6  T A S K S  ·  Q W E N 3 . 5 - 4 B  W O R K E R
MACU · Koh, Salakhutdinov, Fried, 2026 ↗ 41

## Slide 42

Weaker workers are lifted more
O S W O R L D  A B L A T I O N  ·  3 6  T A S K S  ·  O P U S  4 . 6  M A N A G E R
MACU · Koh, Salakhutdinov, Fried, 2026 ↗ 42

## Slide 43

Worker parallelism on Odysseys
O D Y S S E Y S  E A S Y  S U B S E T  ·  4 5  T A S K S
MACU · Koh, Salakhutdinov, Fried, 2026 ↗ 43

## Slide 44

Revising the graph
MACU · Koh, Salakhutdinov, Fried, 2026 · Table 2 ↗ 44

## Slide 45

Closing
45

## Slide 46

A design checklist
1 Are the subtasks separable? Would planner and executor beneﬁt from diﬀerent models or training?
2 Which failures or observations should change the plan?
3 How will the system stop errors and context from accumulating?
4 What information or authority stays separate—and who approves irreversible actions?
B e f o r e  a d d i n g  p l a n n i n g  s t r u c t u r e ,  a s k :
46

## Slide 47

Open problems
Checking
Language plans and subgoal graphs have no general
validator.
Calibration
Agents misjudge when to think, look, ask, or revise.
Global state
Cross-subtask constraints resist both decomposition and
longer context.
Scaﬀolding
Whether trained reasoning absorbs these structures
remains open.
47

## Slide 48

Questions?
N e x t  C l a s s :  D o m a i n s  1  · C o d i n g  A g e n t s
48

