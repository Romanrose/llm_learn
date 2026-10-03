# Lecture 6 Slides：文本提取（待核）

- 官方来源：https://www.cmu-agents.com/slides/lecture-06-coding-agents.pdf
- 提取日期：2026-10-03
- PDF SHA-256：9f764df75b573499d090ed71d19a7b8bbfa01ad7059a440ca1af00111b480b51
- 说明：按页提取；图示、公式和布局需对照官方 PDF，文本提取不能替代视觉核验。

## Slide 1

Agents for Coding and
Software Development
Graham Neubig
Language Technologies Institute
F r o m  c o d e  c o m p l e t i o n  t o  s o f t w a r e  e n g i n e e r i n g
1


## Slide 2

Coding agents
Writes code
single completion
1
Modiﬁes
repositories
modify multiple ﬁles
2
Performs
development
full software lifecycle
3
2

## Slide 3

Three ingredients
Prompt Tools LLM
3

## Slide 4

Models that write code
4

## Slide 5

Writing code from a prompt
Language
syntax · APIs · idioms
Editing
condition on both sides
Reasoning
speciﬁcation → behavior
5

## Slide 6

Training a coding model
Pre-training
large corpora including code
Mid-training
code mixtures · longer contexts
RL post-training
reasoning · execution rewards
6

## Slide 7

Pre-training: learning from code and text
Mix sources: web text, technical prose, mathematics, source code, and documentation.
Preserve structure: indentation, ﬁle boundaries, APIs, and text‒code relationships.
Evaluate during training: held-out loss by domain + functional coding tasks.
L  =LM −E   logp  (x  ∣x∼D  
mix ∑t θ t x  )<t
Groeneveld et al., 2024 · OLMo, §2 ↗ 7

## Slide 8

Pre-training: choosing and cleaning data
Filter by language and source: remove generated dumps, broken encodings, and low-
value repetition.
Deduplicate: forks, vendored libraries, near-identical ﬁles, and copied solutions.
Control provenance: record licenses, source dates, opt-outs, and sensitive-data
ﬁltering.
Prevent leakage: split by repository or problem family; decontaminate evaluation tasks.
StarCoder · data selection, filtering, and decontamination ↗ 8

## Slide 9

Pre-training: splitting code into tokens
Learn code-aware subwords: byte-level BPE on code + prose; identiﬁers can span tokens.
Preserve whitespace: spaces, tabs, and newlines carry syntax and literal content.
Compress frequent runs: merge whitespace into tokens instead of spending one token per
space.
Source if·ready: ↵ ····return·value ↵
Tokens if | ·ready | : | ↵ ··· | ·return | ·value | ↵
Actual StarCoder2 split · “·” = space, “ ↵ ” = newline, “|” = token boundary
StarCoder §5.3 ↗ Chen et al., 2021 · whitespace-run tokens ↗ StarCoder2 tokenizer ↗ 9

## Slide 10

Pre-training on a large code corpus
StarCoderBase
15.5B parameters
1T tokens · 80+ languages
Source, issues, commits,
notebooks
Most languages improve with
more tokens.
Horizontal: training tokens (billions) · Vertical: pass@1 · Each curve: one language
Li et al., 2023 · StarCoder ↗ 10

## Slide 11

Mid-training: adding more code
Continue language-model training: increase code exposure while retaining text and
math.
Choose the mixture empirically: compare code gains with general-capability retention.
Code Llama: Llama 2 → 500B additional tokens for 7B / 13B / 34B models.
Then extend context: train on related ﬁles and longer sequences with suitable
positions.
Rozière et al., 2023 · Code Llama, §2 ↗ 11

## Slide 12

Mixing code, text, and math
Code / text / math Common code MATH MMLU
100 / 0 / 0 49.8 10.3 23.8
70 / 20 / 10 48.3 33.2 62.9
Hui et al., 2024 · Qwen2.5-Coder, Table 3 (selected columns) ↗ 12

## Slide 13

Mid-training: handling longer inputs
types.py
Result.value can be None → worker.py
propagates Result → caller.py
complete the null check
Coherent sequences: related ﬁles, paths, and cross-ﬁle dependencies.
Positions + length: Qwen2.5-Coder trains at 8K → 32K; YaRN enables 128K.
Validate: cross-ﬁle completion, inﬁlling, and short-context retention.
Qwen2.5-Coder · §3.2.2; see also Lecture 3 ↗ 13

## Slide 14

Infilling: using code before and after a gap
Fill the return-type annotation
The body is to the right of the hole.
Use both sides to propose the span
The suﬃx supplies evidence for bool.
def is_positive(x: int) -> ____:
    return x > 0
def is_positive(x: int) -> bool:
    return x > 0
Fried et al. · InCoder, §2 and §4 · illustrative example ↗ 14

## Slide 15

Infilling: marking and predicting gaps
Original prefix span suffix
Training prefix [M0] suffix [M0] span [END]
Inference prefix [M0] suffix [M0] →  generate span
One or more holes: distinct sentinels associate each span with its location.
Zero-shot edits: complete code, infer types, generate comments, rename variables.
Fried et al. · InCoder (2022 preprint; ICLR 2023), §2 and §4 ↗ 15

## Slide 16

Infilling: the value of right context
Completed functions passing tests (%)
Inference method Suﬃx used for Single-line Multi-line
Left-to-right · 1 candidate Not used 48.2% 24.9%
Left-to-right · 10 candidates Reranking only 54.9% 28.2%
Causal-masked inﬁlling Generation 69.0% 38.6%
Fried et al. · InCoder, §4.1 · HumanEval-derived infilling tasks ↗ 16

## Slide 17

Infilling: preserving code completion
Pass@1 · matched 52B-token training budget
Training objective HumanEval MBPP
Left-to-right language modeling 6.0% 8.9%
Causal masking 8.0% 10.9%
Fried et al. · InCoder, §5 · objective ablation ↗ Related scaling study: Bavarian et al., 2022 ↗ 17

## Slide 18

Beyond infilling: more ways to learn from code
Commit diﬀs
before + message → after / diﬀ
Muennighoﬀ et al., 2023 · OctoPack ↗
Diagnostics
broken code + error → repair
Yasunaga & Liang, 2020 · DrRepair ↗
Tests
program + test outcomes → reward
Le et al., 2022 · CodeRL ↗
Execution traces
program → executed lines + states
Liu et al., 2023 · CodeExecutor ↗
18

## Slide 19

Evaluating Generated Code
19

## Slide 20

Comparing with a reference solution
Exact match: does generated code reproduce the reference?
BLEU-4: measure token n-gram overlap, with a brevity penalty.
Integer x: is it positive? Code Behavior
Reference return x > 0 Speciﬁcation
Small textual change return x >= 0 Wrong at x = 0
Diﬀerent expression return not (x <= 0) Equivalent for integers
Yin & Neubig, ACL 2017 · §5.1 ↗ Ren et al., 2020 · CodeBLEU ↗ 20

## Slide 21

Comparing code structure
Ren et al., 2020 · CodeBLEU · original overview figure ↗ 21

## Slide 22

Comparing learned code representations
CodeBERTScore
Encode prompt + each code
snippet
Compare contextual token
vectors
Best matches → precision /
recall → F-score
Zhou et al., EMNLP 2023 · CodeBERTScore · original similarity heatmap ↗ 22

## Slide 23

Checking behavior by running code
Candidate
is_positive(x):
 return x >= 0
Test cases
Inputs: −1, 0, 1
Expected: F, F, T
Run code
Isolated runtime
Time + memory limits
Compare outputs
Input Actual Expected
−1 F F
0 T F
1 T T
Fail: zero is not positive
Chen et al., 2021 · functional evaluation · classroom example ↗ 23

## Slide 24

Benefits and limits of execution checks
Beneﬁt Disadvantage / limit
Accepts diﬀerent correct
implementations Finite tests can miss incorrect behavior
Detects semantic errors through
execution
Needs trusted tests, dependencies, and isolated
execution
Matches observed behavior Requires time and a stable execution environment
Chen et al., 2021 · functional evaluation ↗ Liu et al., 2023 · EvalPlus / test adequacy ↗ 24

## Slide 25

Evaluating functions and full programs
HumanEval
164 Python functions
docstring → completion
hidden unit tests
CodeContests
competitive problems · includes Codeforces
statement → full program
compile + test
HumanEval ↗ CodeContests / AlphaCode ↗ 25

## Slide 26

Success across multiple attempts
pass@k: probability that at least one of k sampled programs passes all tests
Chen et al., 2021 · HumanEval ↗ 26

## Slide 27

Non-functional requirements
Existing program
“Make this code faster”
Code LM
Edit the code
Revised program
Same outputs; less time
How is the requested improvement checked?
Runtime efficiency
Run tests + time execution
Score: speedup
Latency / resource use
Compare reference edits
Score: DiffBLEU
Maintainability / security
Static checks + edit match
CodeQL × DiffBLEU
Singhal et al., 2024 · NoFunEval · 397 code-editing tasks ↗ 27

## Slide 28

Learning from test results
Sample responses
Problem → reasoning
+ final code
Run tests
Execute final code
Pass / fail → reward
Update model
Make rewarded
responses more likely
Sample again with the updated model
Luo et al., 2025 · DeepCoder · execution-reward RL ↗ 28

## Slide 29

Reasoning toward a solution
Compute 1 + … + n, for 0 ≤ n ≤ 10¹²
Iterate
Add every integer
sum(range(n + 1))
Too slow at large n
Pair endpoints
Derive formula; check 0, 1
n * (n + 1) // 2
Correct and efficient
Recall a formula
Mistranscribe the expression
n * (n - 1) // 2
Wrong already at n = 1
29

## Slide 30

Coding accuracy after reinforcement learning
16K → 32K: response-token limit during RL (K = 1,000 tokens).
★ / 64K: more tokens at evaluation, no further RL. Orange dashed line: o3-mini.
Luo et al., 2025 · DeepCoder · LiveCodeBench coding tasks ↗ 30

## Slide 31

Agentic coding
31

## Slide 32

From single-step to agentic coding
Single-step coding Self-contained
prompt → Reasoning
+ code → Evaluate
the answer
Agentic coding Issue +
existing ﬁles → Search → edit
→ run tests ↺ → Patch +
evidence
32

## Slide 33

The localize‒edit‒verify loop
Repository
cli.py
conﬁg.py
test_conﬁg.py
Localize
Where does zero
become the default?
Edit
Default only when
the value is None.
Verify
Zero + default cases
+ caller regressions
Failure → revise the hypothesis
Interaction-loop concepts: SWE-agent · original teaching diagram ↗ 33

## Slide 34

Localize: find the cause
Localize the implementation
Zero is falsy: inspect the defaulting rule.
Reproduce the behavior
Now repair the condition, not the test.
$ rg 'retries' buggy_config.py
return config.get("retries") or 3
$ RETRY_MODULE=buggy_config python3 \
  -m unittest test_config.RetryTests.test_zero
AssertionError: 3 != 0
FAILED (failures=1)
34

## Slide 35

Edit: change the defaulting rule
Before
All falsy values select the default.
After
An explicit zero now survives.
return config.get("retries") or 3 value = config.get("retries")
return 3 if value is None else value
35

## Slide 36

Verify: check the fix and regressions
Run the existing tests Use failures to guide the next step
Zero still becomes three?
Localize where the value changes.
A default case breaks?
Edit the rule, then verify again.
$ python3 -m unittest -v test_config
missing   →  3   PASS
None      →  3   PASS
zero      →  0   PASS
positive  →  2   PASS
Ran 4 tests: OK
36

## Slide 37

An alternative: a fixed workflow
Xia et al. · Agentless, original overview figure ↗ 37

## Slide 38

Coding toolsets
38

## Slide 39

Coding with a shell-only toolset
Model
Choose a command
One shell interface
Read / search rg, cat, find
Edit files sed, Python, patch
Execute checks pytest, build commands
bash
Output + exit status + timeout
mini-SWE-agent · shell-only interface and execution model ↗ 39

## Slide 40

Editing with shell commands
Replace text with sed
Match the line, write the result, replace theﬁle.
One shell, many editing methods
sed / awk
Text patterns and line-based changes
Python scripts
Compute replacements across ﬁles
sed 's/^RETRIES = 3$/RETRIES = 5/' \
  settings.py > settings.new
mv settings.new settings.py
40

## Slide 41

Whole files and text replacements
Whole ﬁle · settings.py
Simple to apply; repeats unchanged code.
Pi write · OpenCode write · OpenHands create
Search / replace · send old and new
Compact; needs an unambiguous match.
OpenHands · Pi · OpenCode edit
RETRIES = 5
TIMEOUT = 30
settings.py
<<<<<<< SEARCH
RETRIES = 3
=======
RETRIES = 5
>>>>>>> REPLACE
Aider · formats ↗ OpenHands ↗ Pi ↗ OpenCode ↗ 41

## Slide 42

Diffs and patch commands
Uniﬁed diﬀ
Standard: line positions + context.Aider: omit hunk line numbers.
File-operation patch · Codex syntax
File operations + context; no line counts.
Codex · OpenCode / OpenHands (preset-dependent)
--- a/settings.py
+++ b/settings.py
@@ -1,2 +1,2 @@
-RETRIES = 3
+RETRIES = 5
 TIMEOUT = 30
*** Begin Patch
*** Update File: settings.py
@@
-RETRIES = 3
+RETRIES = 5
 TIMEOUT = 30
*** End Patch
Aider · uniﬁed diﬀs ↗ Codex · parser ↗ OpenCode · selection ↗ OpenHands · GPT-5 preset ↗ 42

## Slide 43

Diff format can make a big difference
Method inside
a large class → Move to a
top-level function → Check syntax
and code preservation
Aider refactoring benchmark: 89 Python tasks
GPT-4 Turbo (gpt-4-1106-preview) · benchmark success rate
SEARCH / REPLACE 20%
Simpliﬁed uniﬁed diﬀ 61%
Aider · unified-diff experiment and refactoring benchmark ↗ 43

## Slide 44

Finding relevant code
Start with the symptom
A ﬂag, a loader, and a retry loop may allmatch.
Follow the value
Conﬁguration input
Where is zero ﬁrst read?
Defaulting logic
Where does zero become three?
rg 'retries' .
44

## Slide 45

Navigating code with dependency graphs
Issue
Zero becomes three
config.py
retry_count(config)
cli.py
configure_client
calls
test_config.py
Zero / None / missing
tests
client.py
Retry loop
uses result
Retrieve the relevant neighborhood,
then check it with execution.
Chen et al., 2025 · LocAgent ↗ 45

## Slide 46

Coding agent evaluation and
training
46

## Slide 47

Evaluating issue resolution
Fail → pass  requested repair Pass → pass  preserved behavior
Jimenez et al. · SWE-bench evaluation pipeline, original source figure ↗ 47

## Slide 48

Building runnable training tasks
Runnable task
Starting state Files + dependencies + test command
Issue Requested behavior + reproduction
Checks Bug fails before; repair restores behavior
Validate the environment before collecting training trajectories.
SWE-Gym · executable training environments ↗ 48

## Slide 49

RL for multi-step code repairs
Assistant actions: training targets
Search
Find config.py
Edit
Preserve zero
Test / finish
Check regressions
Files found Patch applied Test output
Context only
Terminal reward: repaired or not
A late failure does not identify which earlier decision was wrong.
max  E  [R(τ)]θ τ∼π  
θ
Jain et al., 2025 · R2E-Gym ↗ 49

## Slide 50

Training data and inference compute
Training scale
 Inference scale: learned-veriﬁer selection
Pan et al., 2024 · SWE-Gym · 32B model ↗ 50

## Slide 51

Creating repair tasks by injecting bugs
Prepare  executable baseline Mutate  code, not tests Keep  new test failures
Yang et al., 2025 · SWE-smith, original pipeline figure ↗ 51

## Slide 52

Injecting and checking a bug
Working baseline
All four existing tests pass.
Mutate the condition
Zero now becomes three; its test fails.
Before  4 pass Mutated  3 pass · 1 fail Restored  4 pass
value = config.get("retries")
return 3 if value is None else value
value = config.get("retries")
return 3 if not value else value
SWE-smith · procedural mutation and execution validation ↗ 52

## Slide 53

Working across programming languages
Python
pyproject.toml
src/
tests/
pytest
TypeScript
package.json
src/
tests/
npm test
Rust
Cargo.toml
src/
tests/
cargo test
Read the project configuration before choosing build and test commands.
Multi-SWE-bench ↗ SWE-bench Multilingual ↗ 53

## Slide 54

Multi-harness training
Harness = prompts + tools + agent loop + context management
Shared model
Same weights
Example harnesses
OpenHands
OpenCode
Codex
Task checks
Patch → test reward
Trajectories + rewards → update the model
Nemotron 3 Ultra: ≥2 harnesses per task distribution
Polar: native harnesses call a shared model API proxy
Nemotron 3 Super ↗ Nemotron 3 Ultra ↗ Polar ↗ Harness implementations ↗ 54

## Slide 55

Frontend development
55

## Slide 56

Agent-powered frontend development
Localize
Find components
and event handlers
Edit
Change logic
and styles
Verify in the browser
Exercise behavior
Type → click → check saved state
Inspect the rendered page
Screenshot → visual understanding
Revise when a check fails
Yang et al., 2024 · SWE-bench Multimodal · browser and screenshot tools for SWE-agent ↗ 56

## Slide 57

Browser agents and automation scripts
Browser agent
Model chooses each next action
Observe → choose action
Type / click in the browser
Adaptive exploration · next class
Playwright script
Model writes a repeatable check
1 Fill Name with spaces fill()
2 Click Save contact click()
3 Assert saved state expect()
4 Capture an image screenshot()
Programmed sequence + assertions
Screenshots → visual inspection or approved-baseline comparison
Koh et al., 2024 · VisualWebArena ↗ Playwright actions ↗ Assertions ↗ Screenshot comparisons ↗ 57

## Slide 58

Verifying a frontend repair
Before: blank record saved
 After: blank name rejected
Edit value.length → value.trim().length
Behavior
0 records; valid names still save
Appearance
Error visible and readable beside Name
Runnable classroom example ↗ Playwright assertions ↗ Visual checks ↗ 58

## Slide 59

Evaluating visual issue resolution
Issue + image
Observed: blank name
Expected: reject it
Starting repository
Candidate patch
Change validation
Execution checks
Blank → error
No new record
Regression checks
Valid name → save
Existing tests pass
An image in the issue does not make image similarity the grading rule.
SWE-bench Multimodal · issue images and test-based patch evaluation ↗ 59

## Slide 60

Broader software development
60

## Slide 61

From requirements to maintenance
Requirements
User needs
Compatibility
Review
Diff + evidence
Release decision
Deploy / monitor
Production signals
Rollback path
Maintain
New requests
Observed failures
Implementation loop
Edit Test
A test pass is one step,
not the release decision.
61

## Slide 62

Where developers spend their time
15%
0% 10% 20% 30%
Share of reported workday
Meetings + email
Debugging / bug fixing
Running tests
Code review
Requirements + documentation
Helping + sync-ups + networking
Learning + admin + various
Breaks
25%
14%
8%
5%
6%
11%
8%
8%
Coding
Reading / writing
code and tests
Other activities: 85% combined
Meyer et al., 2019 · Table 2 · 5,928 self-reported Microsoft workdays ↗ 62

## Slide 63

Comparing software development tasks
Task Artifact Environment / veriﬁer Horizon
Repair Patch Repository / regression tests One issue
Library
creation Implementation Scaﬀold / package tests Many functions
Test generation New test Buggy + ﬁxed versions /
discrimination One behavior
CI repair Code or conﬁguration Workﬂow / required checks Build run
Evolution Accumulated
changes
Persistent app / milestone +
regressions
Dependent
tasks
63

## Slide 64

Task: localization
Search policy
Issue + repository
Inspect / search
Predicted file
django/…/datetime.py
Module: TruncDate
Function: as_sql
Reward
F1 at each
of 3 levels
Compare with locations in the gold patch; the patch is not policy input.
CodeScout, 2026 ↗ 64

## Slide 65

Task: app creation and modification
Requirements
Product / feature
description
Zero-to-One
Build a new application 15 apps
Vibe-on-Ref
Extend a reference MVP 45 apps
Vibe-on-Vibe
Extend the agent’s earlier MVP 45 apps
Each result is checked using human-authored browser test plans.
ViBench · collection and evaluator definitions checked 2026-09-07 ↗ 65

## Slide 66

Task: library implementation
Commit0 ProgramBench
Library scaffold
parse(…) → [missing body]
evaluate(…) → [missing body]
Documentation + tests
Implement together
Run integrated package tests
Reference executable
Probe inputs → observe outputs
New implementation
Match observable behavior
Check against the reference
Different internal designs can work
Commit0 ↗ ProgramBench ↗ 66

## Slide 67

Task: software maintenance
SWE-Milestone, 2026 ↗ 67

## Slide 68

Task: test generation
Mündler et al., 2024 · SWT-Bench ↗ 68

## Slide 69

Task: CI repair
Observed build failure
Inspect the package’s supported runtime.
Causally relevant change
Rerun install, build, and tests.
Runtime: Node 16
Package requires: Node >=18
npm ci: EBADENGINE
# setup-node configuration
with:
  node-version: '20'
LCA CI Builds Repair · dataset revision ebf12dad ↗ 69

## Slide 70

Learning skills for new tasks
Find relevant code
Search / dependencies
Implement functions
Specification → code
Write bug tests
Issue → executable check
Train policy
SFT or RL
Held-out tasks
New repositories
Repair an issue
Build a library
Detect a new bug
Equal inference budget
70

## Slide 71

Generating projects for coding practice
Zhu, Gandhi & Neubig · SWE-Playground ↗ 71

## Slide 72

Transferring training to new development tasks
Base 32B Hybrid-Gym 32B
SWE-bench Verified
Repair
7
32.4
SWT-Bench Verified
Test generation
9.01
16.86
Commit0 Lite
Library building
8.34
13.45
0 10 20 30 40
Success (%)
Defined separately per task
Hybrid-Gym, 2026 · selected 32B results ↗ 72

## Slide 73

Models that predict code
behavior
73

## Slide 74

Choosing actions and predicting their effects
History h
Inspected code
Tool results
Policy π(a | h)
Choose: run test
Real environment
Execute the test
Observed: assertion fails
World model p(o | h, a)
Predict the test result
Prediction can be wrong
History also conditions the prediction
74

## Slide 75

Predicting execution: shared references
Predict the next state
What are items and result?
True execution
Wrong prediction: treating alias as a copy.
items = [1]
alias = items
alias.append(2)
result = len(items)
items  = [1, 2]
alias  = [1, 2]
result = 2
75

## Slide 76

When predictions help an agent
Two repairs
A: correct patch
B: wrong patch
Predict test outcomes
Model says A fails
Model says B passes
Illustrative mistake
Wrong decision
Choose B; discard A
Run both candidates to check the model’s judgment.
Compare task success AND total latency / tokens / tool calls.
76

## Slide 77

Learning from program execution
FAIR CodeGen Team et al., 2025 · CWM ↗ 77

## Slide 78

Building and using simulators
Dainese et al., 2024 · Code World Models / GIF-MCTS ↗ 78

## Slide 79

Open questions about predicting code behavior
Better decisions? Measure prediction errors and task success on the same problems.
Lower cost? Include latency, tokens, and real environment calls.
New settings? Hold out programs, dependencies, and environments.
When to execute? Vary the fallback threshold and measure failures as well as
savings.
79

## Slide 80

Conclusion
80

## Slide 81

Designing a coding agent
Code models: pre-training, mid-training, and RL from execution rewards.
Agentic coding: localize, edit, and verify with the right tools.
Agent training: runnable tasks, repair rewards, and diverse harnesses.
Frontend development: browser interaction and visual veriﬁcation.
Broader development: localization, apps, libraries, maintenance, tests, and CI.
Code-behavior prediction: learned models that support execution and planning.
81

## Slide 82

Questions
N e x t  C l a s s :  D o m a i n s  2  —  G U I  A g e n t s
82

