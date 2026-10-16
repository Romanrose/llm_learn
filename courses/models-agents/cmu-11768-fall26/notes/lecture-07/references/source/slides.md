# Lecture 7 Slides：文本提取（待核）

- 官方来源：https://www.cmu-agents.com/slides/lecture-07-computer-use-agents.pdf
- 提取日期：2026-10-03
- PDF SHA-256：444b4f2188fc62a50675ec3ef43896905437bbd95f3429879d2dfcc14929473c
- 说明：按页提取；图示、公式和布局需对照官方 PDF，文本提取不能替代视觉核验。

## Slide 1

JY Koh
11-768: AI Agents
15 Sep 2026
Computer Use Agents
1

## Slide 2

Computer Use Agents (CUAs)
01 / COMPUTER USE AGENTS
9
CUAs observe rendered GUIs, execute actions, and checks what changed.
BROWSER
Shop across pages
DESKTOP
Edit ﬁles across apps
MOBILE
Navigate screens and gestures

## Slide 3

Observe, Reason, Act
3
01 / COMPUTER USE AGENTS
USER TASK
CUA MODEL
Reasoning + Action
INFRASTRUCTURE
Validate Action → 
Execute
Observe State → 
Screenshot
input act
Actions change the state, a new screenshot observation is provided to the model.
input
ENVIRONMENT OBSERVATIONS

## Slide 4

4
01 / COMPUTER USE AGENTS
“BUY A BLUE MUG”
ENVIRONMENT OBSERVATIONS
input
input
CUA MODEL
“I see a blue mug on the 
center of the screen. I 
will click it.”
{"mouse": {"left_click": 
[33, 201]}}
INFRASTRUCTURE
Validate Action → 
Execute
act
Observe, Reason, Act

## Slide 5

5
01 / COMPUTER USE AGENTS
“BUY A BLUE MUG”
ENVIRONMENT OBSERVATIONS
input
input
CUA MODEL
“Delivery details are
below. I will scroll
down to ﬁnd them.”
{"scroll": {"dy": 520}}
INFRASTRUCTURE
Validate Action → 
Execute
act
studio.shop / blue-mug
Blue mug
$18 · Qty 1
Add to cart
Observe, Reason, Act

## Slide 6

6
01 / COMPUTER USE AGENTS
“BUY A BLUE MUG”
ENVIRONMENT OBSERVATIONS
input
input
CUA MODEL
“I see the ZIP ﬁeld.
I will click it
to start typing.”
{"mouse": {"left_click": 
[65, 53]}}
INFRASTRUCTURE
Validate Action → 
Execute
act
studio.shop / blue-mug
Delivery estimate
Postal code
Enter ZIP code
Observe, Reason, Act

## Slide 7

7
01 / COMPUTER USE AGENTS
“BUY A BLUE MUG”
ENVIRONMENT OBSERVATIONS
input
input
CUA MODEL
“I will type the ZIP
code to check
delivery options.”
{"type_text": "15213"}
INFRASTRUCTURE
Validate Action → 
Execute
act
studio.shop / blue-mug
Delivery estimate
Postal code
│
Observe, Reason, Act

## Slide 8

The loop continues until task completion, then a reward is computed.
8
01 / COMPUTER USE AGENTS
STEP 1 STEP 2 STEP 3
◀   ○    studio.shop / mugs
STUDIO / Everyday objects
Cream 
mug
$16
Blue mug
$18
Blue set
$28
◀   ○    studio.shop / blue-mug
STUDIO / Everyday objects
Blue mug
$18  ·  Quantity 1
Add to cart
◀   ○    studio.shop / blue-mug
Delivery estimate
Postal code
15213
click the blue mug scroll down type “15213”
…
REWARD
1.0
Task success
Observe, Reason, Act

## Slide 9

A Brief History of CUAs: Toy Environments
01 / COMPUTER USE AGENTS
Learning to use greatly 
simpliﬁed toy web 
interfaces
MiniWoB: Shi et al., ICML 2017  ·  MiniWoB++: Liu et al., ICLR 2018  ·  WebShop: Yao et al., NeurIPS 2022
2017–2022 2022–2024 2025–2026 Sep 2026

## Slide 10

A Brief History of CUAs: Toy Environments
01 / COMPUTER USE AGENTS
Shopping with
real products and
language goals
WebShop: Yao et al., NeurIPS 2022  ·  Oﬃcial environment demo
2017–2022 2022–2024 2025–2026 Sep 2026


## Slide 11

A Brief History of CUAs: Realistic Environments
01 / COMPUTER USE AGENTS
From toy tasks
to realistic
web interfaces
WebArena: Zhou et al., ICLR 2024  ·  VisualWebArena: Koh et al., ACL 2024
2017–2022 2022–2024 2025–2026 Sep 2026


## Slide 12

01 / COMPUTER USE AGENTS
OSWorld: Xie et al., NeurIPS 2024 · Oﬃcial overview video
Full (realistic)
desktop workﬂows
A Brief History of CUAs: Realistic Environments
2017–2022 2022–2024 2025–2026 Sep 2026


## Slide 13

A Brief History of CUAs: Realistic Envs and Data
01 / COMPUTER USE AGENTS
MYPCBENCH
Realistic apps with
personal history
Explore mail, calendar events, 
and project issues in one 
shared world.
Jang et al., 2026 · MyPCBench · Recorded environment walkthrough (33 s)
2017–2022 2022–2024 2025–2026 Sep 2026


## Slide 14

A Brief History of CUAs: Realistic Envs and Data
01 / COMPUTER USE AGENTS
Real software,
realistic tasks
CUA-WORLD
Aggarwal et al., 2026 · Gym-Anything / CUA-World
2017–2022 2022–2024 2025–2026 Sep 2026
Specialized desktop software 
with loaded data and realistic 
tasks.

## Slide 15

A Brief History of CUAs: Real World Use
01 / COMPUTER USE AGENTS
Koh, Sep 2026 · What’s the Point of Computer Use Agents? · OSWorld 2.0 SolveSpace demo (30×)
GPT-6 ASTRA
Very capable and fast, 
still (very) expensive.
2017–2022 2022–2024 2025–2026 Sep 2026


## Slide 16

Benchmarks & Evaluation

## Slide 17

What should count as success?
17
02 / BENCHMARKS
The same task can be evaluated in multiple diﬀerent ways.
ACTION
Did it click the 
target?
Fast grounding / imitation tests
OUTCOME
Is the right item in 
the cart?
State checks or evidence judging
PROCESS
Did it respect the 
constraints?
No checkout; no unwanted 
changes
Evaluators should match the capability you want to measure.

## Slide 18

Benchmarks
18
02 / BENCHMARKS
From predicting one action to completing extended workﬂows.
02A
Static evaluations
Predict an action on a ﬁxed observation.
02B
End-to-end evaluations (web)
Complete a task through browser interaction.
02C
End-to-end evaluations
(desktop, mobile)
Complete tasks across apps and system state.
Long horizon extends end-to-end evaluation across both web and desktop.
02D
Long horizon computer use
Sustain progress through extended workﬂows.

## Slide 19

TASK:
Static evals: Was this action correct?
02A / STATIC EVALUATIONS
27
Add a blue mug under $20 to the cart. Do not purchase.
SCREENSHOT REFERENCE RULE STEP SCORE
studio.shop / mugs
(x, y) ∈ target box
For recorded actions:
Match target, operation,
and input value.
1.0
correct point / step
No environment rollout
A correct step is not a completed task.
BENCHMARK EXAMPLES
ScreenSpot-Pro · Li et al., 2025 Mind2Web · Deng et al., 2023
AITW · Rawles et al., 2023 AndroidControl · Li et al., 2024

## Slide 20

ScreenSpot-Pro: Grounding in professional UIs
20
Point / region matching
1,581
screenshots
23
applications
3
operating systems
High-resolution professional UIs make grounding a benchmark of its own.
Source: Li et al., 2025, Fig. 1
02A / STATIC EVALUATIONS
EVALUATION CRITERION
BENCHMARK STATS

## Slide 21

TASK:
02A / STATIC EVALUATIONS
29
Construct a UV sphere mesh.
SCREENSHOT / BLENDER GROUND TRUTH
Box in original pixels
(417, 132)–(576, 152)
Point inside = 1
Original: 2560 × 1440
Li et al., 2025 · ScreenSpot-Pro, blender_windows_1
ScreenSpot-Pro: Grounding in professional UIs

## Slide 22

Mind2Web: Oﬄine generalization across the web
22
Oﬄine action matching
2,350
tasks
137
websites
31
domains
Next-action imitation is not the same thing as task completion.
Source: Deng et al., NeurIPS 2023, Fig. 1
02A / STATIC EVALUATIONS
EVALUATION CRITERION
BENCHMARK STATS

## Slide 23

TASK:
02A / STATIC EVALUATIONS
31
Rent a car in Brooklyn–Central, NY, for April 9–15.
RECORDED SCREENSHOT / UNITED GROUND-TRUTH ACTION
CLICK
Target: CAR tab
Value: none
Element: bookCarTab
Match the target element
and operation. No task
rollout is performed.
Deng et al., NeurIPS 2023 · Multimodal-Mind2Web, training example
Ground-truth target outlined in red
Mind2Web: Oﬄine generalization across the web

## Slide 24

Benchmarks
24
02 / BENCHMARKS
From predicting one action to completing extended workﬂows.
02A
Static evaluations
Predict an action on a ﬁxed observation.
02B
End-to-end evaluations (web)
Complete a task through browser interaction.
02C
End-to-end evaluations
(desktop, mobile)
Complete tasks across apps and system state.
Long horizon extends end-to-end evaluation across both web and desktop.
02D
Long horizon computer use
Sustain progress through extended workﬂows.

## Slide 25

TASK:
Programmatic state: Test the resulting world
02B / END-TO-END EVALUATIONS (WEB)
36
Add a blue mug under $20 to the cart. Do not purchase.
FINAL APP STATE EXECUTABLE CHECKS TASK REWARD
studio.shop / cart
Blue mug
$18 · Qty 1
In cart
cart.item == blue_mug
cart.price < 20
orders.count == 0
assert all(checks)
PASS
reward = 1.0
Database / ﬁle / app state
Repeatable and precise—but only for conditions the tests cover.
BENCHMARK EXAMPLES
WebArena · Zhou et al., 2024 OSWorld · Xie et al., 2024
AndroidWorld · Rawles et al., 2024 WorkArena · Drouin et al., 2024

## Slide 26

WebArena: Reproducible sites, executable goals
26
Programmatic end state
812
long-horizon tasks
4
self-hosted domains
functional
success checks
Evaluators check environment state, not whether the trace “looks right”.
Source: Zhou et al., ICLR 2024, Fig. 1
02B / END-TO-END EVALUATIONS (WEB)
EVALUATION CRITERION
BENCHMARK STATS

## Slide 27

TASK:
38
Create an empty repository named awesome_llm_reading.
OFFICIAL DEMO / CREATED PROJECT PROGRAMMATIC VERIFIER
name = task.project_name
p = "/byteblaze/"
page.goto(GITLAB+p+name)
html = page.content()
reward = int(
  name in html.lower()
)
Task 476 (simpliﬁed).
Checks name at target URL.
Emptiness is not checked.
Zhou et al., ICLR 2024 · Oﬃcial demo + task 476 / program_html evaluator
WebArena: Reproducible sites, executable goals
02B / END-TO-END EVALUATIONS (WEB)

## Slide 28

VisualWebArena: Vision is part of the task
28
Multimodal + end state
910
tasks
3
self-hosted sites
25.2%
image-input tasks
Visual understanding changes which tasks are even expressible.
Source: Koh et al., ACL 2024, Fig. 1
02B / END-TO-END EVALUATIONS (WEB)
EVALUATION CRITERION
BENCHMARK STATS


## Slide 29

TASK:
LLM / VLM judging: Evaluate the evidence
02B / END-TO-END EVALUATIONS (WEB)
40
Add a blue mug under $20 to the cart. Do not purchase.
OBSERVED EVIDENCE LLM / VLM + RUBRIC JUDGMENT
studio.shop / cart
Blue mug
$18 · Qty 1
In cart
Screenshots + action history
✓  Blue mug present
✓  Price below $20
✓  No purchase shown
Rubric → evidence → verdict
PASS
“The visible cart meets
the requested criteria.”
Flexible evidence judging needs calibration against human labels.
BENCHMARK EXAMPLES
WebVoyager · He et al., 2024 Online-Mind2Web / WebJudge · Xue et al., 2025
CUA-World-Long · Aggarwal et al., 2026

## Slide 30

WebVoyager: Live web, open-ended outcomes
30
VLM-as-judge
643
tasks
15
live websites
85.3%
judge-human agreement
Realism rises; reproducibility falls.
Source: He et al., ACL 2024, Fig. 1
02B / END-TO-END EVALUATIONS (WEB)
EVALUATION CRITERION
BENCHMARK STATS

## Slide 31

TASK:
43
Find the most-starred GitHub project for climate-change data visualization.
PUBLISHED TRACE / GITHUB SEARCH VLM JUDGE INPUTS
Task + ﬁnal answer
+ last k screenshots
Recorded answer
resource-watch/
resource-watch: 63 stars
Judge checks the evidence
and returns SUCCESS or
NOT SUCCESS.
He et al., ACL 2024 · Released GitHub--0 trace and automatic evaluator
Historical trace, not current GitHub rankings
WebVoyager: Live web, open-ended outcomes
02B / END-TO-END EVALUATIONS (WEB)

## Slide 32

Online-Mind2Web: Live sites expose benchmark drift
32
Human + LLM judge
300
tasks
136
live websites
85.7%
WebJudge-human agreement
Live benchmarks drift—and judge quality becomes part of the score.
Source: Xue et al., COLM 2025, Fig. 1 (cropped)
02B / END-TO-END EVALUATIONS (WEB)
EVALUATION CRITERION
BENCHMARK STATS

## Slide 33

TASK:
Human review: Resolve ambiguous outcomes
02B / END-TO-END EVALUATIONS (WEB)
41
Add a blue mug under $20 to the cart. Do not purchase.
REVIEW EVIDENCE INDEPENDENT REVIEW ADJUDICATION
studio.shop / orders
Blue mug
$18 · Qty 1
ORDER PLACED
Reviewer A
PASS
Reviewer B
FAIL
FAIL
Order conﬁrmation shows
a forbidden purchase.
Resolve disagreement using evidence
Human review can score tasks or audit an automatic evaluator.
BENCHMARK EXAMPLES
WebVoyager · human scoring & judge audit · He et al., 2024
Online-Mind2Web · human labels & review · Xue et al., 2025

## Slide 34

Benchmarks
34
02 / BENCHMARKS
From predicting one action to completing extended workﬂows.
02A
Static evaluations
Predict an action on a ﬁxed observation.
02B
End-to-end evaluations (web)
Complete a task through browser interaction.
02C
End-to-end evaluations
(desktop, mobile)
Complete tasks across apps and system state.
Long horizon extends end-to-end evaluation across both web and desktop.
02D
Long horizon computer use
Sustain progress through extended workﬂows.

## Slide 35

OSWorld: Real desktops, custom end-state checks
35
Custom end-state checks
369
tasks
9
applications
custom
task evaluators
Every task ships with setup logic and application-speciﬁc state checks.
Source: Xie et al., NeurIPS 2024, Fig. 1
02C / END-TO-END EVALUATIONS (DESKTOP, MOBILE)
EVALUATION CRITERION
BENCHMARK STATS

## Slide 36

TASK:
48
Update the bookkeeping sheet using the receipts in the provided folder.
PAPER EXAMPLE / UPDATED WORKBOOK REFERENCE FILE + RULES
compare_table(
  saved_workbook,
  gold_workbook,
  rules
)
Reference checks
A1:E8 unchanged
C9:C13 expense labels
Amounts + running balances
D9 ≈ −186.93
E9 ≈ 603.07
Xie et al., NeurIPS 2024 · Fig. 1 + bookkeeping task 8e116af7
OSWorld: Real desktops, custom end-state checks
02C / END-TO-END EVALUATIONS (DESKTOP, MOBILE)

## Slide 37

WindowsAgentArena: Windows at cloud scale
37
Programmatic end state
154
tasks
11
programs
20 min
parallel sweep
Parallel VMs turn multi-day desktop evaluations into a cloud-scale sweep.
Source: Bonatti et al., 2024, Fig. 1
02C / END-TO-END EVALUATIONS (DESKTOP, MOBILE)
EVALUATION CRITERION
BENCHMARK STATS

## Slide 38

Benchmarks
38
02 / BENCHMARKS
From predicting one action to completing extended workﬂows.
02A
Static evaluations
Predict an action on a ﬁxed observation.
02B
End-to-end evaluations (web)
Complete a task through browser interaction.
02C
End-to-end evaluations
(desktop, mobile)
Complete tasks across apps and system state.
Long horizon extends end-to-end evaluation across both web and desktop.
02D
Long horizon computer use
Sustain progress through extended workﬂows.

## Slide 39

TASK:
Hybrid / trajectory: Check outcome and process
02D / LONG HORIZON COMPUTER USE
55
Add a blue mug under $20 to the cart. Do not purchase.
ACTION TRACE TWO KINDS OF CHECK FINAL VERDICT
1   click(mug)
2   click(add_to_cart)
3   click(place_order)
STATE CHECK
✓  Correct item
PROCESS CHECK
✕  Purchase was made
FAIL
Outcome-only grading
could miss the violation.
A plausible deliverable is not enough if the process violated the task.
BENCHMARK EXAMPLES
WeaveBench · trajectory-aware judge · Li et al., 2026
OSWorld 2.0 · completion + separate safety audit, 2026

## Slide 40

Odysseys: Long-horizon tasks on the live web
40
Rubric-based LLM judge
200
live-web tasks
6.1
rubric items per task (avg.)
100
steps · main evaluation cap
Grade progress across the workﬂow—not just a single ﬁnal screenshot.
Odysseys: Benchmarking Web Agents on Realistic Long Horizon Tasks.  Jang*, Koh*, Fried & Salakhutdinov, 2026.
02D / LONG HORIZON COMPUTER USE
EVALUATION CRITERION
BENCHMARK STATS

## Slide 41

TASK:
Odysseys: Score progress across the whole trip
02D / LONG HORIZON COMPUTER USE
57
Plan a Palm Springs wedding trip, compare airports, and build an itinerary.
Jang et al., 2026 · Published trip-planning illustration; rubric text condensed
Flights Drive window Hotel if needed Car rental CryptPad itinerary
R1 Compare PIT–LAX ﬂights ✓
R2 Compare PIT–PSP ﬂights ✓
R3 Check the 9am–4pm drive window ✓
R4 Recommend LAX or PSP ✓
R5 Open a priced car-rental option ✓
R6 Evaluate both restaurant detours ×
R7 Create an editable daily itinerary ✓
R8 Summarize the complete trip plan ✓
RUBRIC CHECKPOINTS / PUBLISHED ILLUSTRATION
7 / 8 satisﬁed = 0.875 average     Perfect completion = 0.0


## Slide 42

OSWorld 2.0: Hours-long workﬂows
42
Partial + binary checks
108
workﬂows
1.6 h
median human time
318
average agent calls
The frontier shifts from clicks to hidden state, changing requirements, and veriﬁcation.
Source: Yuan, Zhou, Xiong et al., 2026, Fig. 1
02D / LONG HORIZON COMPUTER USE
EVALUATION CRITERION
BENCHMARK STATS

## Slide 43

TASK:
OSWorld 2.0: A ﬁle can exist and still be wrong
02D / LONG HORIZON COMPUTER USE
59
Build a FreeCAD support bracket and export a STEP model matching the drawing.
REFERENCE DRAWING / STEP 27 EXPORTED MODEL / STEP 251
Yuan, Zhou, Xiong et al., 2026 · Oﬃcial Task103 failure case (cropped)


## Slide 44

TASK:
OSWorld 2.0: Modeling a part in SolveSpace
02D / LONG HORIZON COMPUTER USE
44
Recreate a mechanical part from the reference video’s dimensions and steps, then save it as a SolveSpace ﬁle.
Koh, Sep 2026 · What’s the Point of Computer Use Agents? · GPT-6 Astra demo (30×)


## Slide 45

CUA-World-Long: One hard task per software
45
Checklist VLM veriﬁer
200
long tasks
>500
steps often needed
8
quality criteria
One long task per application exposes failures across real professional software.
Source: Aggarwal et al., 2026, Fig. 1 (cropped)
02D / LONG HORIZON COMPUTER USE
EVALUATION CRITERION
BENCHMARK STATS

## Slide 46

Modeling

## Slide 47

A VLM predicts actions from visual history
03 / MODELING
64
CONTEXT AT STEP 0
GOAL
“Buy a blue 
mug < $20”
SCREENSHOT 0

## Slide 48

A VLM predicts actions from visual history
03 / MODELING
65
CONTEXT AT STEP 0
GOAL
“Buy a blue 
mug < $20”
SCREENSHOT 0
click(x₀, y₀)ACTION 0


## Slide 49

A VLM predicts actions from visual history
03 / MODELING
66
APPEND ACTION 0 TO THE TRAJECTORY
GOAL
“Buy a blue 
mug < $20”
SCREENSHOT 0
click(x₀, y₀)ACTION 0
ACTION 0
click(x₀, y₀)

## Slide 50

A VLM predicts actions from visual history
03 / MODELING
67
CONTEXT AT STEP 1
GOAL
“Buy a blue 
mug < $20”
SCREENSHOT 0 ACTION 0
click(x₀, y₀)
SCREENSHOT 1
studio.shop / blue-mug
Blue mug
$18 · Qty 1
Add to cart


## Slide 51

A VLM predicts actions from visual history
03 / MODELING
68
CONTEXT AT STEP 1
GOAL
“Buy a blue 
mug < $20”
SCREENSHOT 0 ACTION 0
click(x₀, y₀)
click(x₁, y₁)ACTION 1
SCREENSHOT 1
studio.shop / blue-mug
Blue mug
$18 · Qty 1
Add to cart


## Slide 52

A VLM predicts actions from visual history
03 / MODELING
69
APPEND ACTION 1 TO THE TRAJECTORY
GOAL
“Buy a blue 
mug < $20”
SCREENSHOT 0 ACTION 0
click(x₀, y₀)
click(x₁, y₁)ACTION 1
SCREENSHOT 1
studio.shop / blue-mug
Blue mug
$18 · Qty 1
Add to cart
ACTION 1
click(x₁, y₁)

## Slide 53

A VLM predicts actions from visual history
03 / MODELING
70
CONTEXT AT STEP t
GOAL
“Buy a blue 
mug < $20”
SCREENSHOT 0 ACTION 0
click(x₀, y₀)
SCREENSHOT 1 ACTION 1
click(x₁, y₁)
SCREENSHOT t
studio.shop / cart
Blue mug
$18 · Qty 1
Checkout
studio.shop / blue-mug
Blue mug
$18 · Qty 1
Add to cart

## Slide 54

A VLM predicts actions from visual history
03 / MODELING
71
CONTEXT AT STEP t
GOAL
“Buy a blue 
mug < $20”
SCREENSHOT 0 ACTION 0
click(x₀, y₀)
SCREENSHOT 1 ACTION 1
click(x₁, y₁)
SCREENSHOT t
click / type / tool / stop
studio.shop / cart
Blue mug
$18 · Qty 1
Checkout
ACTION t
studio.shop / blue-mug
Blue mug
$18 · Qty 1
Add to cart

## Slide 55

A VLM predicts actions from visual history
03 / MODELING
71
CONTEXT AT STEP t
GOAL
“Buy a blue 
mug < $20”
SCREENSHOT 0 ACTION 0
click(x₀, y₀)
SCREENSHOT 1 ACTION 1
click(x₁, y₁)
SCREENSHOT t
click / type / tool / stop
Interleaved visual and action history lets the policy condition on past progress.
Generic VLM policy · o denotes observations, a actions · tokenization and history compression vary by system
studio.shop / cart
Blue mug
$18 · Qty 1
Checkout
ACTION t
studio.shop / blue-mug
Blue mug
$18 · Qty 1
Add to cart

## Slide 56

A VLM predicts actions from interleaved tokens
03 / MODELING
72
TOKENIZED CONTEXT AT STEP t
GOAL TOKENS VISUAL TOKENS 0 ACTION TOKENS 0 VISUAL TOKENS 1 ACTION TOKENS 1 VISUAL TOKENS t
click
Text → tokenizer + embeddings; screenshots → vision encoder + projector.
Illustrative token splits; visual tokens are continuous embeddings, not vocabulary IDs. Token counts / encoders vary.
ACTION t
Buy a … v0,1 … v0,N click ( … v1,1 … v1,N click ( … vt,1 … vt,N
CAUSAL TRANSFORMER
INSTRUCTION TURN 0 TURN 1 TURN t
( xt , yt )

## Slide 57

Frontier CUAs: Similar observations, diﬀerent actions
Output format and schema diﬀers between models (reproducibility is a nightmare).
Sources: OpenAI · Anthropic · Google · Qwen¹ · Meta² · Moonshot  |  ¹27B template; ²1.1 report  |  Sep 2026
03 / MODELING
73
MODEL ACTION INTERFACE OUTPUT FORMAT / SCHEMATIC EXAMPLE
GPT-6 Astra Python / PyAutoGUIor native computer tool pyautogui.click(x, y)computer_call: actions=[…]
Fable / Opus 5 Native computer tool calls(one or more per response) tool_use: left_clickinput: {coordinate: [x, y]}
Gemini 3.8 Flash Computer-use function calls(normalized coordinates) functionCall: clickargs: {x, y}  ∈ 0–999
Qwen 3.8 Function calls(app-deﬁned GUI schema) <tool_call><function=…>…XML-style tool serialization¹
Muse Spark Scripts + direct GUI actionsincluding action batches Tool / script output²Exact GUI schema is app-speciﬁc
Kimi K3 Function calls(app-deﬁned GUI schema) tool_calls[].functionname + JSON arguments

## Slide 58

Training

## Slide 59

Training Stages
UI ELEMENTS ACTIONS
Visuals: Mind2Web (Deng et al., 2023) · AITW (Rawles et al., 2023) · Editable teaching schematics
04 / TRAINING
75
boxes · labels · OCR
→ grounding
click · type · swipe
→ control
HUMAN DEMOS
goal + human trace
→ behavior cloning
SYNTHETIC DATA
agent-generated 
traces
→ behavior cloning
RL ROLLOUTS
task + veriﬁer
→ task reward
Pre-training Post-training (SFT) Post-training (RL)
click(x, y)
type(text)
swipe(…)
Teacher
o0 a0
o1 a1
o → a → …
reward
+1

## Slide 60

Pre-training: UI elements and actions
UI ELEMENTS / GROUNDING ACTION PREDICTION
Deng et al., 2023 · Mind2Web training example; Wu et al., 2025 · OS-Atlas
04 / TRAINING
76
“CAR” ↔ element box / screen coordinates
CLICK
element: bookCarTab
value: none
Other labels: type(text), swipe(start, end)
Learn what is on the screen, and how to address it.

## Slide 61

Post-training (SFT): Imitate useful trajectories
HUMAN DATA SYNTHETIC DATA
Gupta et al., 2026 · MolmoWeb Fig. 2 excerpt; Table 2; Wang et al., 2025 · OpenCUA Table 2; §2.3
04 / TRAINING
77
MolmoWebMix (example above)
36K human + 105K synthetic task trajectories
AxTree
teacher Roll out Filter
Record format (Fig. 2) · 105K synthetic tasks
Retain a useful trajectory → SFT
Same next-action loss; demonstrations can come from humans or agents.
AgentNet
22,625 released task trajectories · 3 OS

## Slide 62

Demonstration data: More scale, richer trajectories
Human and synthetic traces now cover longer, more diverse workﬂows.
2023
Mind2Web
2,350 tasks
137 websites
WEB
2023
AITW
715K episodes
30K 
instructions
MOBILE
2024
WebLINX
100K 
interactions
2.3K demos
WEB
2024
Android 
Control
15,283 demos
833 apps
MOBILE
2024
GUI 
Odyssey
7,735 
episodes
cross-app
MOBILE
2025
AgentNet
22,625 tasks
18.6 steps
per trajectory
DESKTOP
Scale has increased over time; data type also shifts towards focusing on longer, cross-app, 
multi-turn supervision.
Mind2Web · AITW · WebLINX · AndroidControl · GUI Odyssey · AgentNet · MolmoWeb
04 / TRAINING
79
2026
MolmoWeb
Mix
36K human
105K synth.
task 
trajectories
WEB

## Slide 63

Generate experience → score the outcome → improve the policy.
78
04 / TRAINING
POLICY ACTION 0 POLICY ACTION 1 POLICY ACTION 2
◀   ○    studio.shop / mugs
STUDIO / Everyday objects
Cream 
mug
$16
Blue mug
$18
Blue set
$28
◀   ○    studio.shop / blue-mug
STUDIO / Everyday objects
Blue mug
$18  ·  Quantity 1
Add to cart
◀   ○    studio.shop / blue-mug
Delivery estimate
Postal code
15213
click the blue mug scroll down type “15213”
…
REWARD
1.0
Task success
Post-training (RL): Learn from scored rollouts
Goal: Find a blue mug, check delivery, and add it to the cart.
Update the policy using trajectory rewards
Illustrative rollout · CUA-Gym / Gym-Anything: Interactive tasks and veriﬁers

## Slide 64

RL Training
04 / TRAINING
80
Add one blue mug under $20 to the cart; do not check out.
◀   ○    studio.shop / mugs
STUDIO / Everyday objects
Cream mug
$16
Blue mug
$18
Blue set
$28
◀   ○    studio.shop / blue-mug
STUDIO / Everyday objects
Blue mug
$18  ·  Quantity 1
Add to cart
◀   ○    studio.shop / cart
Your cart
Blue mug
Qty 1
$18
Subtotal  $18
Checkout
history + screen history + screen history + screen
SFT learns next action prediction; RL evaluates trajectories based on outcomes.
Teaching example · screenshots, actions, and optional rationale labels are interleaved
TASK:
click productACTION 0 add to cartACTION 1 verify / stopACTION 2

## Slide 65

We need simulated environments for RL
81
REAL MONEY
Repeated attempts can create
duplicate paid bookings.
REAL PEOPLE
A booking can dispatch a driver;
exploration aﬀects other people.
NO CLEAN RESET
Cancellation may incur a fee;
spent time cannot be restored.
Explore in resettable replicas, not repeated real world interactions.
MyPCBench · Jang et al., 2026 · Task bounded_action-f041 · Published trajectory, step 53
04 / TRAINING
TASK: Book an airport ride for my upcoming Jamaica ﬂight.


## Slide 66

CUA-Gym: Build reusable, resettable mock applications
94 MOCK WEB APPS / PLAN → IMPLEMENT → TEST
Wang et al., 2026 · CUA-Gym Fig. 2; §2.2
04 / TRAINING
83
One mock app supports many tasks through controlled, isolated state.
Inject initial state Inspect ﬁnal state Reset each session

## Slide 67

CUA-Gym: Co-generate tasks, states, and rewards
~32K VERIFIED TUPLES / 110 ENVIRONMENTS
Generate the world and its reward independently—then test that they agree.
Wang et al., 2026 · CUA-Gym Fig. 1; §2.1
04 / TRAINING
82


## Slide 68

CUA-Gym: How much training data?
110
environments
32,112
veriﬁed RLVR tuples
38%
cross-application tasks
A broad environment pool supports many independently veriﬁed tasks.
Wang et al., 2026 · CUA-Gym Fig. 8(a); §2.3
04 / TRAINING
84
94 MOCK WEB APPS + 16 DESKTOP APPS


## Slide 69

CUA-Gym: Veriﬁed rollouts improve the policy
3,578 SFT DEMOS → GSPO ON 10,858 VERIFIED TUPLES
OSWorld Performance: 62.2 → 72.6%
Wang et al., 2026 · Fig. 9 data-scale ablation; §3 main results
OSWorld-Veriﬁed · GUI calls · 100 model steps · programmatic checks
04 / TRAINING
85


## Slide 70

Gym-Anything: Create and audit real software setups
200
software applications
3
operating systems
10K+
tasks in CUA-World
The creation agent builds, an independent audit veriﬁes the evidence.
Aggarwal et al., 2026 · Gym-Anything Fig. 2, phases 1–2; §3
04 / TRAINING
86
SELECT SOFTWARE / CREATE ↔ AUDIT


## Slide 71

Gym-Anything: Scale tasks, then verify trajectories
PROPOSE + AMPLIFY CHECKLIST-BASED VERIFICATION
Aggarwal et al., 2026 · Gym-Anything Fig. 2, phases 3–4; §4.1
04 / TRAINING
87
Execute seed tasks
Amplify with an LLM → ﬁlter
Privileged evidence + weighted checklist
Partial credit + integrity checks


## Slide 72

Gym-Anything: Environments across real software
200
software applications
12,103
tasks and environments
22 / 22
SOC occupation groups covered
The generator creates task-ready setups across professional software.
Aggarwal et al., 2026 · Gym-Anything Fig. 1; §5
04 / TRAINING
88
REAL INSTALLED SOFTWARE / LINUX · WINDOWS · ANDROID


## Slide 73

Gym-Anything: Distill successful trajectories
~2,000
successful SFT trajectories
12.7 → 22.5
average checklist score / 100
1.6 → 4.4%
perfect-checklist pass rate
More software and more tasks both help supervised post-training.
Aggarwal et al., 2026 · Fig. 6(a); Table 3; §6.1–7.1
CUA-World-Test · GUI actions · 200 steps · Gemini 3 Flash checklist judge
04 / TRAINING
89
KIMI-K2.5 TEACHER → QWEN3-VL-2B-THINKING STUDENT


## Slide 74

Training Stages
UI ELEMENTS ACTIONS
Visuals: Mind2Web (Deng et al., 2023) · AITW (Rawles et al., 2023) · Editable teaching schematics
04 / TRAINING
90
boxes · labels · OCR
→ grounding
click · type · swipe
→ control
HUMAN DEMOS
goal + human trace
→ behavior cloning
SYNTHETIC DATA
agent-generated 
traces
→ behavior cloning
RL ROLLOUTS
task + veriﬁer
→ task reward
click(x, y)
type(text)
swipe(…)
Teacher
o0 a0
o1 a1
o → a → …
reward
+1
Strong CUA
Pre-training Post-training (SFT) Post-training (RL)

## Slide 75

Summary
1 CUAs operate directly on the GUI
They observe and act within the same interface as humans.
2 Evaluations should target the right metrics and level of behavior
Static actions, end-to-end tasks, and long horizon workﬂows are measured diﬀerently.
3 Models predict actions from interleaved visual history
CUAs are vision-language models that emit GUI actions, some also use code and tools.
4
Pretraining → SFT → RL
Models are trained through large scale pretraining, SFT on human annotated and synthetic 
trajectories, and RL within simulated environments.
11-768 · GUI Agents
05 / SUMMARY
91

## Slide 76

What’s remaining?

## Slide 77

Speed + Cost
FASTER CUAS REQUIRE BOTH SYSTEMS AND MODEL IMPROVEMENTS
Game-TARS · ByteDance Seed, 2025, §3.3 / §4.3.2   ·   FDM-1 · Standard Intelligence, 2026
05 / WHAT’S REMAINING
93
Long contexts are expensive
Screenshots and reasoning add preﬁll 
and generation cost.
Game-TARS: Sparse Thinking
Reason at key decisions; act directly on 
routine steps.
Fewer / cheaper turns
Improve planning and batching; 
explore direct action models (FDM-1).
Task time ≈ turns × time / turn
Reasoning at every step
Game-TARS: Sparse reasoning
Think Act Think Act Think Act
Think Act Act Act Think Act
FDM-1: Direct action prediction
Act Act Act Act Act Act

## Slide 78

Personalization: Adapt to the user
GUM: INFER THE USER’S CONTEXT
GUM · Shaikh et al., 2025, Fig. 1   ·   MyPCBench · Jang et al., 2026, project overview 94
Personal context changes
Use the user’s ﬁles, history and 
preferences—not generic 
defaults.
Memory must be revisable
GUM retrieves and updates 
conﬁdence-weighted user facts.
User control is essential
MyPCBench tests personal 
context. Consent and forgetting 
are essential.
MYPCBENCH: A PERSONAL DIGITAL LIFE
05 / WHAT’S REMAINING

## Slide 79

Infrastructure + UX
CODEX: BACKGROUND COMPUTER USE
Proactivity needs consent, visibility, and an easy oﬀ switch.
OpenAI, 2026 · Codex for (almost) everything · demo excerpt 95
Don’t block the user
Run in isolated background sessions 
while their work continues.
Collaborate in real time
Show progress; accept corrections, 
approval and interruption.
Novel UI / UX for CUAs
Much to be explored still!
05 / WHAT’S REMAINING

## Slide 80

Multi-Agent Systems
MACU: PLAN → PARALLELIZE → REPLAN
Parallelism helps only when coordination preserves correctness.
MACU · Koh, Salakhutdinov & Fried, 2026, Fig. 1 / §3 (adapted) 96
Divide work by dependencies
MACU dispatches ready subtasks to 
CUAs in isolated environments.
Share evidence, then replan
Hand oﬀ ﬁles and results; verify work 
and recover from failures.
Beyond homogeneous CUAs
Combine CUA, code and tool agents; 
control conﬂicts and overhead.
05 / WHAT’S REMAINING

## Slide 81

Thanks!

## Slide 82

Appendix: Benchmarks
WEB + STATIC EVALUATION
MiniWoB / MiniWoB++
WebShop
ScreenSpot-Pro
Mind2Web
Android in the Wild
AndroidControl
WebArena
VisualWebArena
WebVoyager
Online-Mind2Web
WorkArena / WorkArena++
DESKTOP, MOBILE + LONG HORIZON
OSWorld / Veriﬁed
WindowsAgentArena
AndroidWorld
MobileWorld
Odysseys
OSWorld 2.0
MyPCBench
WeaveBench
AgentNetBench and CUA-World-Long share their papers with training datasets/environments (p. 99).
APPENDIX / REFERENCE
98

## Slide 83

Appendix: Modeling / Training
MODELS + GROUNDING
OS-Atlas
UI-TARS
Qwen-UI-Agent
Qwen3.6-27B (model card)
Game-TARS
DATA + TRAINING ENVIRONMENTS
OpenCUA / AgentNet / AgentNetBench
MolmoWeb / MolmoWebMix
CUA-Gym
Gym-Anything / CUA-World
Grounding and demonstration datasets that also serve as static benchmarks are listed on p. 98.
APPENDIX / REFERENCE
99

## Slide 84

Appendix: Systems
AGENT LOOPS + ORCHESTRATION
ReAct
Interleaved reasoning and actions
MACU: Multi-Agent Computer Use
Orchestrating multiple computer-use agents
GUM: General User Models
User modeling from computer activity
FRAMEWORKS + EFFICIENCY
BrowserGym ecosystem
Shared environments and experiment tooling
Cua (open-source framework)
Computer-use environments and infrastructure
FDM-1 (technical blog)
High-frequency computer action modeling
Papers and technical resources for agent orchestration, personalization, infrastructure, and eﬃciency.
APPENDIX / REFERENCE
100

## Slide 85

Appendix: Products
OPENAI + ANTHROPIC
Codex Computer Use (OpenAI blog)
Operator (OpenAI launch)
OpenAI computer-use API guide
Claude computer use (launch blog)
Developing computer use (Claude blog)
Claude computer-use tool docs
OTHER PRODUCTS + RELEASES
Grok Bot (xAI launch)
Gemini computer-use API guide
Muse Spark 1.1 (Meta release)
Navigator n2 (Yutori release)
Oﬃcial product announcements, technical blogs, and API documentation. Operator is a historical launch.
APPENDIX / REFERENCE
101

## Slide 86

Android in the Wild: Scale without end-state checks
86
Oﬄine action matching
715K
episodes
5.69M
examples
30,378
unique prompts
Scale buys coverage; the evaluator still matches recorded actions.
Source: Rawles et al., 2023, Fig. 1
02A / STATIC EVALUATIONS
EVALUATION CRITERION
BENCHMARK STATS

## Slide 87

AndroidControl: Diverse apps, paired instructions
87
Oﬄine action matching
15,283
demonstrations
14,548
unique tasks
833
Android apps
Paired high- and low-level instructions separate planning from motor control.
Source: Li et al., NeurIPS 2024, Fig. 1
02A / STATIC EVALUATIONS
EVALUATION CRITERION
BENCHMARK STATS

## Slide 88

AgentNetBench: An oﬄine desktop proxy
88
Oﬄine step matching
100
tasks
17.63
average steps
2,143
total actions
AgentNetBench turns human desktop trajectories into a fast oﬄine proxy.
Source: Wang et al., NeurIPS 2025, Fig. 2 (cropped)
02A / STATIC EVALUATIONS
EVALUATION CRITERION
BENCHMARK STATS

## Slide 89

WorkArena: Enterprise tasks with validators
89
Programmatic checks
33
task templates
19,912
instances
ServiceNow
environment
Parameterized tasks make enterprise state validation reproducible.
Source: Drouin et al., ICML 2024, Fig. 1
02C / END-TO-END EVALUATIONS (DESKTOP, MOBILE)
EVALUATION CRITERION
BENCHMARK STATS

## Slide 90

WorkArena++: Compositional enterprise workﬂows
90
Compositional end state
682
composite tasks
5
skill families
10
company themes
Composition converts atomic UI skills into knowledge-work workﬂows.
Source: Boisvert et al., NeurIPS 2024, Fig. 1
02C / END-TO-END EVALUATIONS (DESKTOP, MOBILE)
EVALUATION CRITERION
BENCHMARK STATS

## Slide 91

AndroidWorld: Parameterized mobile state
91
System-state reward
116
task families
20
applications
∞
parameterized instances
Task generators and system-state rewards create repeatable mobile episodes.
Source: Rawles et al., ICLR 2025, Fig. 1
02C / END-TO-END EVALUATIONS (DESKTOP, MOBILE)
EVALUATION CRITERION
BENCHMARK STATS

## Slide 92

MobileWorld: Cross-app, user, and MCP tasks
92
Programmatic + hybrid
201
tasks
27.8
average steps
62.2%
cross-app tasks
Modern mobile use mixes GUI control, clariﬁcation, and structured tools.
Source: Kong et al., ACL 2026, Fig. 2 (cropped)
02C / END-TO-END EVALUATIONS (DESKTOP, MOBILE)
EVALUATION CRITERION
BENCHMARK STATS

## Slide 93

MyPCBench: One person's cross-app digital life
93
Per-rubric LLM judge
184
tasks
17
logged-in apps
68%
multi-app tasks
One seeded identity turns separate apps into one reproducible digital life.
Source: Jang et al., arXiv 2026, Fig. 1 (cropped)
02D / LONG HORIZON COMPUTER USE
EVALUATION CRITERION
BENCHMARK STATS

## Slide 94

WeaveBench: Hybrid GUI + CLI trajectories
94
Trajectory-aware judge
114
tasks
16
median switches
76
median tool calls
Outcome-only grading can overcredit agents that take invalid shortcuts.
Source: Li et al., EMNLP 2026, Fig. 3
02D / LONG HORIZON COMPUTER USE
EVALUATION CRITERION
BENCHMARK STATS

