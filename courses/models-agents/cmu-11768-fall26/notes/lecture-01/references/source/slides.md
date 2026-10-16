# Lecture 1 Slides：文本提取（待核）

- 官方来源：https://www.cmu-agents.com/slides/lecture-01-agents.pdf
- 提取日期：2026-10-03
- PDF SHA-256：16ad94b7cea06da50ff1736fba9ba3afcbb753fdea51c57b8df1ae3f9a7dd26c
- 说明：按页提取；图示、公式和布局需对照官方 PDF，文本提取不能替代视觉核验。

## Slide 1

What Are Agents?
And How Do They Work?
From language modeling to systems that act in the world
Daniel Fried · Graham Neubig
11-768: AI Agents
1


## Slide 2

01 · Intro
How capable are current agents?
Sixteen agents built a 100,000-line C compiler in two weeks—able to compile the Linux kernel.
Building a C compiler with a team of parallel Claudes · Carlini, Anthropic 2026 ↗ 2

## Slide 3

01 · Intro
How capable are current agents?
Summer Yue (@summeryue0) · X, February 2026 ↗ 3

## Slide 4

01 · Intro
How capable are current agents?
What should an agent be allowed to do autonomously? Autonomous Ask ﬁrst Never
Diagnose why the online store’s
checkout started failing
UNCLASSIFIED
Draft and send a product-launch
email to 50,000 customers
UNCLASSIFIED
Collect your tax forms, and prepare
and ﬁle your 2025 tax return
UNCLASSIFIED
Migrate a payments API from Python
to Rust without breaking mobile
checkout
UNCLASSIFIED
Buy concert tickets to my favorite
band if they set up a show in my area
UNCLASSIFIED
Adjust an insulin dose after a week of
glucose readings
UNCLASSIFIED
4

## Slide 5

Jing Yu Koh · multimodal GUI-agent demo · 2024 5


## Slide 6

OpenHands
O p e n H a n d s  V is u a l D e b u g g in g
O p e n H a n d s  V is u a l D e b u g g in g
Watch on
Graham Neubig · OpenHands visual debugging 6

## Slide 7

01 · Intro
Meet the teaching team
Instructors
Daniel Fried
 Graham Neubig
TAs
Aditya Soni
 Andy Liu
 Apurva Gandhi
 Demi Wang
Jiarui Liu
 Saujas Vaduguru
 Weiwei Sun
 Yueqi Song
Course contact: 11-768-fall-2026@lists.andrew.cmu.edu 7

## Slide 8

01 · Intro
Compute sponsors
T h a n ks  t o  t h e s e  s p o n s o r s  f o r  p r o v i d i n g  c o m p u t e  f o r  t h e  a s s i g n m e n t s  a n d  p r o j e c t !
8

## Slide 9

02 · Foundations
What is an agent?
An agent is anything that can be viewed
as perceiving its environment through
sensors and acting upon that
environment through actuators.
Russell & Norvig, Artiﬁcial Intelligence: A Modern
Approach
Environment: a repository, website, application, or workﬂow
State/Observations: messages, ﬁle contents, webpages, screenshots, and tool results
Actions: replies, ﬁle edits, shell commands, API calls, and mouse or keyboard events
Reward: passing test cases, satisfying LLM-as-a-judge rubrics, positive user feedback
9

## Slide 10

02 · Foundations
Recap: language models
Next-token prediction
At each step, predict a distribution over the
next token.
Append the generated token to the preﬁx
and predict again.
Chain of thought
Generate intermediate reasoning tokens
before the answer.
Those tokens become context for later
predictions.
2 × (3 + 4)
prompt tokens
Prompt
 Model
 Reasoning tokens
14
answer tokens
Answer
10

## Slide 11

02 · Foundations
Tool definition
A typed interface
exposed to the
model.
Name and description
JSON Schema for
arguments
The chat template
renders it as text
Example after apply_chat_template
{
  "name": "read_file",
  "description": "Read a UTF-8 file.",
  "parameters": {
    "type": "object",
    "properties": { "path": { "type": "string" } },
    "required": ["path"]
  }
}
<tools>
{"name":"read_file","description":"Read a UTF-8 file.",
 "parameters":{"type":"object","properties":{"path":{"type":"string"}},
 "required":["path"]}}
</tools>
11

## Slide 12

02 · Foundations
Tool calls and results
Tool call
After apply_chat_template
Tool result
After apply_chat_template
{"role":"assistant","tool_calls":[{
  "id":"call_7",
  "name":"read_file",
  "arguments":{"path":"test.py"}
}]}
<tool_call>
{"name":"read_file","arguments":{"path":"test.py"}}
</tool_call>
{"role":"tool",
 "tool_call_id":"call_7",
 "name":"read_file",
 "content":"def add(a, b): …"}
<tool_response>
def add(a, b): …
</tool_response>
12

## Slide 13

02 · Foundations
From LLMs to agents: actions as tokens
Language model
A tool call is another token sequence the
model can predict.
The sequence names a tool and supplies its
arguments.
Harness
Parses, validates, and executes the call.
Returns the result as observation tokens.
Model
 Reasoning
read_file
path: "test.py"
Tool call
 Execute
def add(a, b): …
Observation
Toolformer · Schick et al., NeurIPS 2023 ↗ 13

## Slide 14

02 · Foundations
An agent is a model in a loop
Context
Task
What does test.py contain?
Tool
read_file(path)
History
Model
 Reasoning
r e a d _ f i l e ( " t e s t . p y " )
C a l l
E x e c u t e
d e f  a d d ( a ,  b ) :  …
R e s u l t
send_message
to: user
“test.py defines add(a, b).”
Call
ReAct · Yao et al., ICLR 2023 ↗ 14

## Slide 15

A minimal ReAct loop
mini-swe-agent Browse the full source: Loop → Templates →
Assignment 1: implement and extend a similar controller; create and call your own tools; apply it to software tasks.
def run(self, task: str = "", **kwargs) -> dict:
    self.messages = []
    self.add_messages(
        self.model.format_message(role="system", content=self._render_template(self.config.system_template)),
        self.model.format_message(role="user", content=self._render_template(self.config.instance_template)),
    )
    while True:
        self.step()
def step(self) -> list[dict]:
    return self.execute_actions(self.query())
def query(self) -> dict:
    message = self.model.query(self.messages)
    self.add_messages(message)
    return message
def execute_actions(self, message: dict) -> list[dict]:
    """Execute actions in message, add observation messages, return them."""
15

## Slide 16

02 · Foundations
Example agent trajectory
s w e b e n c h . c o m  ↗
16

## Slide 17

03 · AGENT CAPABILITIES
Agent capabilities
1. Accurate tool calling 2. Coherence over long context
3. Customizability 4. Complex task management
5. Environment understanding 6. Safety
17

## Slide 18

03 · AGENT CAPABILITIES
Two ways to build these capabilities
LLM training
Change the model’s behavior through
pretraining, SFT, or RL.
Teach reusable patterns for reasoning, tool
use, and recovery.
Capabilities become part of the learned
policy.
Harness engineering
Change the system around the model:
prompts, tools, memory, and control ﬂow.
Provide context, validation, retries, and
safety boundaries.
Capabilities emerge from the model‒
harness combination.
→
 +
Training Model Harness
18

## Slide 19

03 · TRAINING · PRETRAINING → SFT → RL
How agent behavior is trained
01
Pretraining
Text, code, multimodal data
Broad representations and
regularities
02
Mid-training / SFT
Instructions, traces, tool calls
Formats and demonstrations
03
RL
Rewards or preferences
Trajectory-level behavior
19

## Slide 20

03 · CAPABILITY 1 / 6
Accurate tool calling
Harness engineering
Grammar-constrained decoding.
LLM training
SFT: train on tool-calling traces.
read_file
path: "test.py"
Select tool Arguments Validate Execute
20

## Slide 21

03 · CAPABILITY 2 / 6
Coherence over long context
Harness engineering
Context compression/compaction.
Dynamic memory lookup.
Sub-agent delegation.
LLM training
SFT: long-context training.
History Summary Memory Retrieval
21

## Slide 22

03 · CAPABILITY 3 / 6
Customizability
Harness engineering
Agent memory.
Skills.
Custom tools.
LLM training
RL: learning from user feedback.
Memory Skills Tools
22

## Slide 23

03 · CAPABILITY 4 / 6
Complex task management
Harness engineering
Provide planning/decomposition tools.
Sub-agent delegation.
LLM training
RL: train on complex, long-horizon tasks.
Plan Delegate Verify Goal
23

## Slide 24

03 · CAPABILITY 5 / 6
Environment understanding
Harness engineering
Learn skills corresponding to domain
knowledge.
LLM training
SFT: train on data w/ expected observation
shape.
RL: train in domain-speciﬁc environments.
Interface Observe Act
24

## Slide 25

03 · CAPABILITY 6 / 6
Safety
Harness engineering
Sandboxing tools.
Limit access to credentials.
Monitor trajectories.
LLM training
RL: safety-aware RL.
Credential Guardrail Sandbox Monitor
25

## Slide 26

04 · AGENT ENGINEERING
Agents are systems, not just models
Sandbox
Harness Inference
Model
Monitoring
 Training
26

## Slide 27

04 · AGENT ENGINEERING
Harness engineering
Shared functionality
Manage state, tools, memory, and control
ﬂow
Validate actions and handle errors
Enforce permissions and safety boundaries
Example software:
Coding agents: CC, Codex, OpenHands,
OpenCode, Pi
Orchestrators: LangChain, CrewAI
Harness
Permissions Memory Tools Control ﬂow
27

## Slide 28

04 · AGENT ENGINEERING
Sandbox
Shared functionality
Isolate code and tool execution
Limit compute, network, and ﬁlesystem
access
Create reproducible environments
Example software:
Docker / Apptainer
Modal / Sail
Execution Isolation Resources Access
28

## Slide 29

04 · AGENT ENGINEERING
LM inference
Shared functionality
Serve model generations reliably
Batch requests and reuse the KV cache
Manage streaming, parallelism, and
throughput
Example software:
vLLM
SGLang
the next …
Requests Route Compute KV cache Tokens
29

## Slide 30

04 · AGENT ENGINEERING
Training systems
Shared functionality
Prepare data and collect rollouts
Coordinate distributed workers
Checkpoint, evaluate, and reproduce runs
Example software:
SkyRL
Miles
Rollouts Workers Rewards Update
30

## Slide 31

04 · AGENT ENGINEERING
Observability and monitoring
Shared functionality
Capture traces and metrics
Track quality, cost, and failures
Compare trajectories and evaluations
Example software:
Laminar
MLFlow
Traces Inspect Quality Latency Cost
31

## Slide 32

05 · LEARNING OBJECTIVES
What you should be able to do
1. Implement an agent from scratch on
top of an open-source LLM.
2. Design evaluations for multi-step
tasks.
3. Train agents to improve their
capabilities.
4. Reason about safety and reliability
tradeoﬀs.
5. Pursue an open research question in
agents.
Build
 Evaluate
 Train
 Safety
 Research
32

## Slide 33

06 · ASSIGNMENTS
Learn by building and measuring
A1 · Harness
TENTATIVE DUE: THU, SEP 10
Build the basic infrastructure and establish a reproducible baseline.
A2 · Evaluation
TENTATIVE DUE: THU, SEP 24
Measure behavior, report failure cases, and distinguish demos from
evidence.
A3 · Training
TENTATIVE DUE: THU, OCT 22
Train or adapt a component; analyze behavior, cost, and robustness.
Project
Integrate the ideas around a scoped task, environment, and
evaluation.
33

## Slide 34

06 · SEMESTER SCHEDULE
Semester schedule
Aug 25 ‒ Sep 8
Agent capabilities
what is an agent · tools · context · memory · planning
Sep 10 ‒ Sep 15
Domains
coding · GUI
Sep 17 ‒ Oct 1
Training + domains
SFT · RL basics · deep research · advanced RL
Oct 6 ‒ Oct 22
Frameworks + safety
sandboxes · OpenHands · LangGraph
Fall break: Oct 12‒16
Oct 27 ‒ Nov 5
Interaction + projects
people · multi-agent · project hours
Nov 10 ‒ Dec 3
Advanced topics + presentations
future of work · search · posters
Thanksgiving: Nov 25‒27
34

## Slide 35

07 · COURSE PREREQUISITES
Before we begin: prerequisites
This course requires prior serious
experience training a language model.
We’ll share a link to a Google form on
Piazza. Submit the form by Thursday,
Aug 27 so that we can ﬁnalize
enrollment.
In the form, tell us about a university
course with an LM-training
assignment: the course, assignment
link, term, and grade.
If you lack the formal prerequisite,
explain comparable experience—such
as pre/post-training work or
published research training 4‒7B+
language models.
We will enforce the prerequisite
strictly; students who cannot meet it
will be asked to drop the course.
35

## Slide 36

07 · ASSIGNMENT POLICIES · COURSE WORK
How course work adds up
Assignments 1‒3: 40% total,
completed individually.
Lecture highlights: 10% total,
completed individually; due within 24
hours after each lecture, starting
Thursday.
Research project: 50% total, in teams
of 2‒3.
Proposal 5% · check-in 5% ·
presentation 10% · ﬁnal report 30%.
Assignment descriptions and Canvas
provide the authoritative
requirements and deadlines.
Build
 Evaluate
 Train
 Safety
 Research
36

## Slide 37

07 · ASSIGNMENT POLICIES · USING AGENTS
Using Agents in This Class?
We acknowledge that you use agents day-to-day, but we also want you to learn how to
build, evaluate, and reason about them yourself.
AI tools are generally permitted unless a speciﬁc assignment or project writeup says
otherwise.
Lecture highlights must be written by you, not generated by AI.
You are responsible for every submitted claim, citation, result, and line of code—and will
be quizzed on it.
37

## Slide 38

07 · ASSIGNMENT POLICIES · DEADLINES
Deadlines, submission, and slack
Assignments 1‒3 each include two 24-
hour slack days.
Slack days are attached to each
assignment: they cannot be
transferred or shared.
After slack days are used, the penalty
is 5% of the assignment score per
additional day or part-day.
Project proposal and report each have
two slack days; the presentation has
none.
× 2
Due date 2 slack days −5% / day
38

## Slide 39

Thank you, Questions?
N e x t  C l a s s :  A g e n t  C a p a b i l i t i e s  1  —  T o o l  U s e
39

