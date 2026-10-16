# Lecture 12 Slides：文本提取（待核）

- 官方来源：https://www.cmu-agents.com/slides/lecture-12-rl-systems.pdf
- 提取日期：2026-10-03
- PDF SHA-256：15a062df1513c0710e4e3bd8cfa247d4b131b966faadc32e5101561c322a8a13
- 说明：按页提取；图示、公式和布局需对照官方 PDF，文本提取不能替代视觉核验。

## Slide 1

Reinforcement 
Learning Systems
Apurva Gandhi
11-768: AI Agents


## Slide 2

RL Systems: Overview
2

## Slide 3

What operations must an LLM RL Framework support?
𝜃 += σ𝑡 R 𝜏 − 𝑏 ℎ𝑡 𝛻𝜃log 𝜋𝜃 𝑎𝑡|ℎ𝑡   
optim_step backward forward
env.verify env.state / env.step   + agent harness
Policy 
Gradient  
Update: 
3

## Slide 4

Why not just hand-roll custom implementation in 
vanilla PyTorch?
𝜃 += σ𝑡 R 𝜏 − 𝑏 ℎ𝑡 𝛻𝜃log 𝜋𝜃 𝑎𝑡|ℎ𝑡   
optim_step backward forward
Policy 
Gradient  
Update: 
optimizer.step() model.backward() model.forward()PyTorch 
API: 
4

## Slide 5

RL Frameworks are composed of two fundamentally 
different workloads!
𝜃 += σ𝑡 R 𝜏 − 𝑏 ℎ𝑡 𝛻𝜃log 𝜋𝜃 𝑎𝑡|ℎ𝑡   
optim_step “forward_backward”“sample”
Policy 
Gradient  
Update: 
Trainer Engine
e.g., Megatron, FSDP2
Prefill-style 
(Parallelizable)
Autograd
Inference Engine
e.g., VLLM, SGLang
Decode-heavy 
(Sequential)
No grad
 5

## Slide 6

RL Frameworks are composed of two fundamentally 
different workloads!
“forward_backward”“sample”
Trainer Engine
e.g., Megatron, FSDP2
Prefill-style 
(Parallelizable)
Inference Engine
e.g., VLLM, SGLang
Decode-heavy 
(Sequential)
KV Caching
Radix/Prefix Caching (across requests)
Continuous Batching 
Speculative Decoding/MTP
Model sharding (PP, CP, TP, EP, etc.)
Activation Checkpointing
Prefix sharing
Batch Sample Packing
Model sharding (PP, CP, EP, etc.)
6

## Slide 7

Interaction Between Train and Inference Engines 
“forward_backward”“sample”
Trainer Engine
e.g., Megatron, FSDP2Inference Engine
e.g., VLLM, SGLang
weight sync
Rollout/trajectory data
7

## Slide 8

Breaking down a training step
INFERENCE + ENV
1 · sample
Sample trajectories 
from the current policy 
while executing actions 
in the environment
ENVIRONMENT
2 · verify
Rewards from verifiers, 
tests or tool outcomes
TR AINER
3 · forward
Forward pass in the 
trainer to recompute 
logprobs with while 
tracking grad
TR AINER
4 · backward
Backward pass to 
compute gradient
SYNC
5 · optim_step  + sync
Update trainer policy 
weights, send to 
inference engine and 
reshard
Repeat with the updated weights
8

## Slide 9

Inference Optimizations: KV Caching 
KV CACHE · ONE ENTRY PER PAST TO KEN
K,V
t1
K,V
t2
K,V
t3
K,V
t4
K,V
t5
K,V
t6
new
t7
Step t7 computes q, k, v for the new token only, 
attends over every cached k, v, then appends its 
own.
KV Caching trades a lot of recomputation for a lot of memory.
HOW BIG IS IT? 
Llama-3-8B in bf16: 
• 128 KB per token
• 1 32k-token trace ≈ 4 GB;
• 64 of them ≈ 256 GB
9

## Slide 10

Inference Optimizations: Prefix Caching
System prompt + tools
Task Prompt A
Task Prompt B
rollout 1, step 1
rollout 2, step 1
rollout 3, step 1
rollout 1, step 1
reused freshly computed
rollout 1, step 2
Agentic RL especially benefits from prefix caching. 
• In Group Rollouts (e.g., GRPO), many rollouts share the same task prompts.
• KV from past steps/history of a rollout can be reused in future steps.
SGLang RadixAttention , vLLM Automatic Prefix Caching
10

## Slide 11

Inference Optimizations: Continuous Batching
11
Schedule at the granularity of one decode step: finished sequences leave the batch at 
once, and queued requests take their slots.
Usually accompanied with chunked prefill to avoid long prompts from causing decode 
latency spikes. Alternatively, can disaggregate prefill and decode.
STATIC BATCHING
A idle
B
C idle
D idle
Every slot waits for the longest request (B).
CONTINUOUS BATCHING
A E H
B
C F
D G I
Freed slots are refilled at the next step.
Yu et al., 2022 (Orca, iteration-level scheduling)

## Slide 12

Inference Optimizations: Speculative Decoding
12
A cheap drafter guesses k tokens; the policy checks all k in one parallel pass. Rejection 
sampling keeps the policy's exact distribution.
Drafter
e.g., MTP head or a small 
model
proposes k = 4
t1 t2 t3 t4
Policy
scores all 4 in one pass
t1 t2 t3′
RL-SPECIFIC CATCH
The policy changes every training step, so a frozen drafter's acceptance rate decays. Train it 
online with an auxiliary objective (e.g., SFT, distillation).
Leviathan et al., 2023

## Slide 13

Trainer Optimizations: Activation Checkpointing
13
Keep only each layer's input in the forward pass; recompute the layer's internals when the 
backward pass reaches it.
STANDARD
CHECKPOINTED
L1
all activations
L1
input only
L2
all activations
L2
input only
L3
all activations
L3
input only
L4
all activations
L4
recomputing
L5
all activations
L5
input only
L6
all activations
L6
input only
backward pass: recompute one layer at a time, use it, free it
MEMORY
From every layer's activations to one input per layer , plus a 
single layer's activations at a time.
COST
Full recompute adds ~one forward pass: ≈ +33% 
compute. Selective recompute (only attention) costs 
far less.
Chen et al., 2016 (gradient checkpointing); Korthikanti et al., 2022 (selective activation recomputation).


## Slide 14

Trainer Optimizations: Prefix Sharing
14
RL batches repeat prefixes: the prompt across a GRPO group, the history across turns. Compute each 
once, forward and backward. (Counter-part to prefix caching in inference)
DENS E · PRO MPT REPEATED
prompt P r1
prompt P r2
prompt P r3
prompt P r4
SHARED · PROMPT ONCE
prompt P
r1
r2
r3
r4
Tree attention mask (no attention across branches) · position IDs as in each standalone sequence · gradients from every branch accumulate into P
SHARED P ROM PTS · SNOWFLAKE ZoRRo
In long-prompt GRPO batches, 80–95% of tokens are 
duplicate prompt tokens. Deduplicating them gives up to 
6× faster actor updates.
PREFIX TREES · AReaL -DTA
Multi-turn τ²-bench rollouts compress 9.43× as a prefix 
tree. A DFS walks one root-to-leaf path at a time: up to 
8.31× vs dense training.
Snowflake AI Research, 2026 (ZoRRo, Arctic RL); Zhang et al., 2026 (AReaL-DTA: Dynamic Tree Attention, ICML).


## Slide 15

Optimizations: Parallelism
15
GPU 0
keeps its Q
GPU 1
keeps its Q
GPU 2
keeps its Q
GPU 3
keeps its Q
KV blocks rotate
Context Parallelism
Parallelisms — NVIDIA NeMo Framework User Guide


## Slide 16

Train-Inference Interactions: Weight Sync
Full Weight Sync:
• Full broadcast to every inference rank.
• 1T parameter model → ~2TB sync
• Delta Weight Sync: 
• ~99% of parameters unchanged between RL weight updates bf16 change.
• Sync only the delta.
Note: Parameters need to be re-sharded for inference engine parallelism layout.
16
Mihai & Belilovsky (PULSE), 2026

## Slide 17

Train–Inference Interactions:
Rollout Routing Replay (R3)
Ma et al., 2025, R3, Fig. 1
Problem
Tiny numerical differences can select 
different MoE experts.
R3 Solution
Record rollout expert choices and 
replay the selections in training.
Inference engine must provide routing 
decisions to training engine.

## Slide 18

Agentic RL: The Sharp Bits 
18

## Slide 19

Sequence Extension
Harness A
Append to the existing history
Harness B
Compact every two observations
Turn 1 T A₁ O₁ Turn 1 T A₁ O₁
Turn 2 T A₁ O₁ A₂ O₂ Turn 2 T A₁ O₁ A₂ O₂
Turn 3 T A₁ O₁ A₂ O₂ A₃ O₃ Turn 3 T S A₃ O₃
Turn 4 T A₁ O₁ A₂ O₂ A₃ O₃ A₄ O₄ Turn 4 T S A₃ O₃ A₄ O₄
After O₂: keep T; summarize A₁ O₁ A₂ O₂ → S
T = task     Aᵢ = action     Oᵢ = observation     S = compacted interaction history
Which harness is better for training efficiency?
23404: Sequence Extension - Tinker Documentation

## Slide 20

Sequence Extension: Training Batch
One trajectory advantage Â, broadcast to every action token
Harness A: one concatenated datapoint
Token span Task A₁ O₁ A₂ O₂ A₃ O₃ A₄ O₄
Loss mask 0 1 0 1 0 1 0 1 0
Advantage 0 Â 0 Â 0 Â 0 Â 0
Harness B: two datapoints, both containing Task
Token span
Loss mask
Advantage
Task A₁ O₁ A₂ O₂
0 1 0 1 0
0 Â 0 Â 0
Task S A₃ O₃ A₄ O₄
0 0 1 0 1 0
0 0 Â 0 Â 0
Repeated task tokens have zero direct loss, but still require context computation.
Preserve exact prefixes and concatenate for as long as practical. 24

## Slide 21

Chat Template Quirks
Popular chat templates may not satisfy the sequence extension 
property. 
E.g., Qwen 3 / Qwen 3.5’s default chat template removes reasoning 
from past history. 
No Token Left Behind: Demystifying Token -In-Token-Out in Miles
21

## Slide 22

Chat Template Quirks
E.g., Qwen 3 / Qwen 3.5’s default chat template removes reasoning 
from past history. 
Agent RL training frameworks often ship with their own custom chat 
template or “renderers” that preserve sequence extension 
(e.g., Tinker , PrimeRL). 22

## Slide 23

Token-In, Token-out (TITO)
In what format should we store and transport rollout/trajectory 
data from the inference engines to the trainer engines? 
1. String
2. Tokens
23

## Slide 24

Token-In, Token-out (TITO)
In what format should we store and transport rollout/trajectory 
data from the inference engines to the trainer engines? 
1. String
2. Tokens
• Small, inconsistent transformations in string space can lead to 
inconsistent tokenizations between train and inference (e.g., chat 
template adding some whitespace) 
• Tokenization is one-to-one, but de-tokenization is many-to-one.
24
No Token Left Behind: Demystifying Token -In-Token-Out in Miles

## Slide 25

Async RL
Pipeline RL, AReaL
Overlap inference and weight updates. Reduces GPU idle due to very long rollouts.
Requires staleness/off-policy corrections. 
Sync RL
• Co-locate Train & Inference Engines 
(same GPUs shared by both)
Async RL
• Split GPUs between Train & 
Inference 
• Agentic RL is often rollout-bound 
(long trajectories), so can dedicate 
more GPUs to inference (e.g., 3:1 
ratio)
• Requires continuous batching and 
in-flight weight-update support. 25

## Slide 26

In-flight Weight 
Updates
Inference frameworks have 
evolved to accommodate RL 
systems needs. 
Example from SGLang Docs.
26

## Slide 27

Complex Harnesses (Sub-agents, Context compaction, etc.) 
27
Recursive Agent Optimization (RAO), 2026 ; Recursive Language Models (RLM), 2025

## Slide 28

System Design Choices
28

## Slide 29

Harness Agnostic Design
• Many popular agent harnesses: Codex, Claude Code, OpenHands, Pi, 
Hermes, Prime Agent, etc.
• How to support all?
• Anti-pattern: Custom rollout/environment code for each harness.
• Harness-agnostic pattern: Middleman/Proxy service that emulates inference APIs (chat-
completions, responses, anthropic, etc.) → 0 code changes when using new harness
OpenHands
Pi
Trainer
Chat Completions 
API 
Agent Lightning
Middleman
Inference 
Engine 
Rollout Store
(logprobs, r3, etc.)  
Inference Service
29

## Slide 30

Single Program Multiple Data (SPMD)
One Python program runs on every GPU rank  (simplified example pseudocode below)
rank = dist.get_rank()
train = dist.new_group([0, 1, 2, 3])
infer = dist.new_group([4, 5, 6, 7])
if rank < 4:
while True:
batch = next_batch_shard(train)
forward_backward(batch, train)
optimizer.step()
publish_weights_async(train)
else:
while True:
refresh_weights_if_ready(infer)
prompt = next_prompt(infer)
trace = rollout(prompt, infer)
enqueue_trajectory(trace, infer)
All ranks
Create both groups
in the same order.
Ranks 0–3: training
FSDP collectives
and optimizer updates
Ranks 4–7: inference
Tensor/Context-parallel decoding
and weight refresh
Coordination lives in the program running on every rank. 
Straightforward with direct control of everything in a single program, but less flexible.
AReaL versions < 1.0
30

## Slide 31

Everything-as-a-service w/ Single Controller
Orchestrator / 
Controller
Inference Service
Agent Service
 Trainer Service
Weight Sync Service
Env / Reward Service
Open Reward Standard (ORS)
SGLang / vLLM API
Illustrative service boundaries and API examples.
Tinker training  API
31

## Slide 32

Everything-as-a-service w/ Single Controller
Orchestrator / 
Controller
Inference Service
Agent Service
 Trainer Service
Weight Sync Service
Env / Reward Service
Open Reward Standard (ORS)
Tinker training  API
SGLang / vLLM API
Illustrative service boundaries and API examples.
Separation of concerns (decoupling):
• Each of these components is fairly 
complex and specialized. 
• Instead all living in the same codebase: 
• Lightweight orchestrator (CPU 
training loop) → researchers can 
easily prototype different 
algorithms without complex 
dependencies.
• Project maintenance, updates 
and releases don’t need to be 
synchronized.
32

## Slide 33

Everything-as-a-service w/ Single Controller
Orchestrator / 
Controller
Inference Service
Agent Service
 Trainer Service
Weight Sync Service
Env / Reward Service
Open Reward Standard (ORS)
Tinker training  API
SGLang / vLLM API
Illustrative service boundaries and API examples.
Modularity
• Easy to swap a service implementation 
for another one as long as the same 
protocols are used for inter-service 
communication.
Hosted Service (e.g., OpenReward)
or
Self-hosted
33

## Slide 34

Elastic Scale Up
Orchestrator / 
Controller
Inference Service
34

## Slide 35

Elastic Scale Up
Orchestrator / 
Controller
Inference 
Service 
Controller
…
35

## Slide 36

Multi-cluster / Heterogeneous Compute
Orchestrator / 
Controller
Inference 
Service 
Controller
…
8xH100
 4xMi350
36

## Slide 37

Example: AstraFlow (Haizhong Zheng et. al, 2026)
37

## Slide 38

Multi-policy Training
Microservice architecture makes it easy to train multiple different 
models simulataneously (e.g., for multi-agent rollouts with heterogenous policies)
38

## Slide 39

Online RL (Training after Deployment)
AReaL 2.0, 2026
Online RL in production at Cursor: 
• Cursor Tab
• Composer (new model checkpoint from real user interaction every 5 hours) 39

## Slide 40

Multi-Tenant, Multi-LoRA Training
• 8 concurrent runs beat 8 serial 
runs in throughput (but with 
e2e time per run).
• Each concurrent LoRA run can 
be a different user of your 
training service. 
• Requires special kernels 
Grouped-GEMM/SGMV 
kernels. 
SkyRL + Trajectory Labs: Multi-LoRA Training for Continual Learning, 2026 ;   Punica: Multi-tenant LoRA Serving, 2023
40

## Slide 41

Tinker
• Pioneered multi-tenant, multi-LoRA RL training and the decoupled training 
service design.
• Clean API design:
• Training client per training run.
• Sampling client per LoRA weight checkpoint.
41

## Slide 42

Thank you, Questions?
Next Class: Sandboxing and Credential Management
42


## Slide 43

Some Useful Metrics to Track/Debug
Metric What it tells you Warning sign
Reward / pass@1 Is the policy improving on the training tasks? Flat for many steps, or rising while held-out evals fall (reward 
hacking)
pass@k Coverage: can any of k samples solve it? Falls while pass@1 rises: diversity is collapsing
Entropy How much the policy still explores Sudden collapse toward 0, or a jump (degenerate text)
importance_weight_max Worst token ratio, e.g. π_train / π_rollout Spikes: mismatch or stale data; a few tokens dominate the 
update
Grad norm Size of each update before clipping Spikes ahead of divergence; steady upward drift
Average staleness How many weight versions old the data is Creeping up: rollouts can't keep pace with training
Trainer MFU How well the trainer GPUs are used Drops from padding, imbalance or small microbatches
Timing: rollout, update, stall, 
total Where the wall-clock time of a step goes Stall > 0: the trainer is waiting on rollouts
43

