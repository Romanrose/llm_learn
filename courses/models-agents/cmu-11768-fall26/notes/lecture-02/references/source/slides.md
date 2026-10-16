# Lecture 2 Slides：文本提取（待核）

- 官方来源：https://www.cmu-agents.com/slides/lecture-02-tool-use.pdf
- 提取日期：2026-10-03
- PDF SHA-256：671b9d0c849150aa9b5d95a9655b892dbe5fa2d6fc7a6c704c0f8e3f876e74ad
- 说明：按页提取；图示、公式和布局需对照官方 PDF，文本提取不能替代视觉核验。

## Slide 1

Tool Use for
Language Model Agents
Graham Neubig
Language Technologies Institute
H o w  m o d e l s  t u r n  t o k e n  p r e d i c t i o n s  i n t o  a c t i o n s
1


## Slide 2

Basic idea
2

## Slide 3

Tool definition
A tool is an interface through which a language model can invoke
an external computer program.
Search Calculator Browser Python API
The model proposes; external software decides whether and how to execute.
What Are Tools Anyway? · Wang et al., COLM 2024 ↗ 3

## Slide 4

Benefits of tools
Extend
Access information or actions unavailable in the model's
parameters.
Facilitate
Delegate operations external programs perform more
reliably or eﬃciently.
What Are Tools Anyway? · Wang et al., COLM 2024 ↗ 4

## Slide 5

Tool-use scenarios
Need Example tool Beneﬁt
Current information Search Fresh evidence
Exact computation Calculator or Python Reliable execution
Private state Account API Authorized application data
External action Browser or API Changes the environment
Call tools only when their beneﬁt outweighs latency, cost, failure, and risk.
5

## Slide 6

Examples of tools
6

## Slide 7

Building ChatGPT
What calls are necessary?
Start from the abilities we want, then
deﬁne a narrow interface for each
kind of interaction.
What sorts of things can you help me do?
I can answer questions, ﬁnd information, run code,
create images, and complete speciﬁc workﬂows.
7

## Slide 8

Textual responses
finish(text)
Return the ﬁnal text and stop the
agent loop. This is a harness control
action, not an external program.
CONTROL
CALL
finish("Accra is the capital of
Ghana.")
What is the capital of Ghana?
Accra is the capital of Ghana.
8

## Slide 9

Information retrieval
search_web(query)
Retrieve information from the web.
TOOL
CALL
search_web("site:cmu.edu announced
today")
TOOL
RESULT
Three matching news items...
What did CMU announce today?
CMU announced three items today...
9

## Slide 10

Code execution
execute_code(code
)
Run a program in an isolated
environment and return its output.
TOOL
CALL
execute_code("sum([18,23,41,54])/4")
TOOL
RESULT
34.0
What is the mean of 18, 23, 41, and 54?
The mean is 34.
10

## Slide 11

Image generation
generate_image(qu
ery)
Generate an image from a textual
description.
TOOL
CALL
generate_image("watercolor robot
studying in a library")
TOOL
RESULT
generated_image.png
Create a watercolor robot studying in a library.
Here is the generated image.
11

## Slide 12

Custom functions
create_grocery_ca
rt(items)
Expose an application-speciﬁc
capability through one typed call.
TOOL
CALL
create_grocery_cart(["bananas","milk",
"coffee"])
TOOL
RESULT
Cart C17 · 3 items · $31.42
Make a cart with bananas, milk, and coﬀee.
I created a three-item cart totaling $31.42.
12

## Slide 13

Programmatic tool calling
13

## Slide 14

Code as a meta-tool
Code composes control ﬂow, libraries, and multiple operations in one action.
What Are Tools Anyway? · Wang et al., COLM 2024 ↗ 14

## Slide 15

Programmatic composition
CodeAct · Wang et al., ICML 2024 ↗ 15

## Slide 16

CodeAct results
In the displayed subset, code had the best success rate
for 8/8 models.
Code used the fewest turns for 7/8; across all 17 models,
both counts are 12/17.
CodeAct · Wang et al., ICML 2024 ↗ 16

## Slide 17

Code is a high-power tool
Expressive
Loops · variables · libraries
Good for multi-step data
manipulation and composition.
Harder to constrain
Broad action space
Validation is less precise than for a
narrow typed function.
Higher impact
Files · network · processes
Use sandboxing, resource limits,
permissions, and audit logs.
17

## Slide 18

Mechanics of providing tools
18

## Slide 19

Tool calls as tokens
Text continuation
The weather is sunny.
Tool continuation
<tool_call>
get_weather(...)
The model requests an action. The harness executes it.
19

## Slide 20

Quick review: messages become model input
API messages
system Be concise.
user Weather in Pittsburgh?
assistant I need current data.
chat template
→
Qwen input sequence
<|im_start|>system
Be concise.<|im_end|>
<|im_start|>user
Weather in Pittsburgh?<|im_end|>
<|im_start|>assistant
I need current data.<|im_end|>
Roles structure the API; the template serializes one model-input sequence.
20

## Slide 21

Tools add structure to the request
Tool definition
{
"type": "function",
"function": {
"name": "get_weather",
"parameters": {
"type": "object",
"properties": {"city": {"type": "string"}},
"required": ["city"]
}
}
}
API request
response =
client.chat.completions.create(
model=model,
messages=messages,
tools=[weather_tool],
)
The harness sends messages and tool schemas; the template exposes both to the model.
21

## Slide 22

Definition in, tool call out
Prompt contains
<tools>
{"name":"get_weather", ...}
</tools>
model
→
Model emits
<tool_call>
{"name":"get_weather",
"arguments":{"city":"Pittsburgh"}}
</tool_call>
The model emits the call content; the API response attaches a unique call ID.
22

## Slide 23

Same tool call, different model protocols
Qwen 3.8
Function + parameter tags
<|im_start|>assistant
<tool_call>
<function=get_weather>
<parameter=city>
Pittsburgh
</parameter>
</function>
</tool_call><|im_end|>
Mistral Small 4
Control token + call ID
[TOOL_CALLS] [{"name": 
"get_weather", 
"arguments": {"city": 
"Pittsburgh"}, "id": 
"abc123xyz"}]</s>
DeepSeek V3.2
DSML invocation block
< ｜ DSML ｜ function_calls>
< ｜ DSML ｜ invoke
name="get_weather">
< ｜ DSML ｜ parameter
name="city"
string="true">Pittsburgh<
/ ｜ DSML ｜ parameter>
</ ｜ DSML ｜ invoke>
</ ｜ DSML ｜ function_calls>
One schema; model-speciﬁc serialization and parsing.
23

## Slide 24

How OpenHands dispatches a tool call
1 Register at initialization
Tool spec
BashTool → Resolve + conﬁgure
resolve_tool(spec, state) →
Name → deﬁnition
tools_map[name]
ToolDeﬁnition: schema · Action ·
executor
2 Dispatch each model call
Parse
{ name, args
}
→ Lookup
tools_map[name]→
Validate
action_from_
arguments(args)
→ Execute
executor(action)→
Return
ObservationEvent
(call_id)
24

## Slide 25

Results return by call ID
Assistant tool call
{
"id": "call_123",
"name": "get_weather",
"arguments": {"city": 
"Pittsburgh"}
}
↔
Tool-result message
{
"role": "tool",
"tool_call_id": "call_123",
"content": "72°F · sunny"
}
tool_call_id matches results to calls, including parallel calls.
25

## Slide 26

Constrained decoding
26

## Slide 27

Malformed tool calls
Model output
{"name":"get_weather",
 "arguments":{"city":"Pittsburgh"}
×
Missing }
The harness cannot parse it.
27

## Slide 28

Tool-call constraints
Syntax
valid JSON
Shape
expected ﬁelds
Types
city is a string
Values
units is C or F
Constraints ensure form—not truth, permissions, tool choice, or task success.
28

## Slide 29

JSON Schema
Vocabulary for describing JSON data
Types, required ﬁelds, allowed values
Machine-readable validation rules
{
  "type": "object",
  "properties": {
    "city": {"type": "string"},
    "units": {"enum": ["C", "F"]}
  },
  "required": ["city"],
  "additionalProperties": false
}
JSON Schema Core · Draft 2020-12 ↗ 29

## Slide 30

Schema-valid vs. schema-invalid
Schema-valid
{"city":"Pgh","units":"F"}
object
{ members }
member , member
"city" : string "units" : unit
"Pgh" "F"
Schema-invalid
{"city":"Pgh","units":"K"}
object
{ members }
member , member
"city" : string "units" : unit
"Pgh" "K"×
Both are JSON; only "F" derives from unit →  "C" | "F".
30

## Slide 31

A pushdown automaton adds a stack
Finite control
expect
value → inside
value → expect
separator
State records the local position in a grammar
rule.
Stack memory
{
push
object
→
[
push
array
object
→
]
pop
object
→
}
pop
empty
The stack remembers arbitrarily deep nesting.
State tracks the current rule; the stack remembers where nested rules return.
31

## Slide 32

Grammar checking happens below tokenization
Compile once
unit →  "C" |
"F" → byte-level
PDA
Check every candidate token
Token
t ₁ : "F"} →
Decoded
bytes
22 46 22
7D
→
Run all
bytes
advance(bytes)
→
Keep or
mask
allowed ✓
A token may cross several grammar terminals—or end partway through one
—so token boundaries cannot be treated as grammar boundaries.
XGrammar · Dong et al., MLSys 2025 ↗ 32

## Slide 33

Example: cached token-mask generation
1 · Parse the preﬁx
Advance persistent PDA stacks over the bytes already
emitted.
2 · Fetch cached decisions
The stack-top node indexes precomputed validity for
context-independent tokens.
3 · Check the minority
Run context-dependent candidate tokens against the full
stack; union results across matching stacks.
4 · Mask and continue
Combine the decisions, mask the logits, sample a token,
and update the PDA stacks.
XGrammar · Dong et al., MLSys 2025 ↗ 33

## Slide 34

Token masking
XGrammar · Dong et al., MLSys 2025 ↗ 34

## Slide 35

Case study: where the speedup comes from
Caching handles most tokens; persistent stacks support branching; CPU work overlaps GPU inference.
XGrammar · Dong et al., MLSys 2025 ↗ 35

## Slide 36

REST API Calling
36

## Slide 37

Libraries expose in-process APIs
Caller and function share one process
Python supplies the name, arguments, types, and
return type.
Not remotely callable yet
A network client still needs an address, protocol,
serialization, and authentication.
A library API is a typed programming interface—not a network service.
# weather_lib.py
from typing import Literal
from pydantic import BaseModel
class Weather(BaseModel):
    summary: str
    temperature: float
def get_weather(
    city: str,
    units: Literal["C", "F"] = "F",
) -> Weather:
    return provider.lookup(city, units)
37

## Slide 38

REST APIs expose functions over HTTP
GET /weather
city=Pittsburgh
units=F
Header: X-API-Key
Response: Weather as JSON
FastAPI binds the library function to a REST endpoint and documents its API-key header.
# api.py
from typing import Annotated, Literal
from fastapi import FastAPI, Security
from fastapi.security import APIKeyHeader
from weather_lib import Weather, get_weather
app = FastAPI(title="Weather API")
key_header = APIKeyHeader(name="X-API-Key")
@app.get("/weather", operation_id="get_weather")
def weather(
    city: str,
    key: Annotated[str, Security(key_header)],
    units: Literal["C", "F"] = "F",
) -> Weather:
    verify(key)
    return get_weather(city, units)
FastAPI security and OpenAPI ↗ 38

## Slide 39

REST API servers publish OpenAPI descriptions
OpenAPI describes the HTTP operation; embedded JSON Schema describes its values.
{
  "paths": {"/weather": {"get": {
    "operationId": "get_weather",
    "parameters": [
      {"name": "city", "in": "query", "required": true,
       "schema": {"type": "string"}},
      {"name": "units", "in": "query",
       "schema": {"type": "string", "enum": ["C", "F"], "default": "F"}}
    ],
    "security": [{"APIKeyHeader": []}]
  }}},
  "components": {"securitySchemes": {"APIKeyHeader": {
    "type": "apiKey", "in": "header", "name": "X-API-Key"
  }}}
}
FastAPI · generated OpenAPI ↗ 39

## Slide 40

Coding agents often call REST APIs with curl
1 · Read the API description
Select the operation and required
parameters.
2 · Construct the command
The shell expands the environment
variable; curl sends HTTP.
3 · Limit the credential
A coding agent with shell access may
also read or misuse that secret.
Direct REST access is simple, but the agent's shell receives the API credential.
curl -sS -G https://weather.example/weather \
  --data-urlencode "city=Pittsburgh" \
  --data-urlencode "units=F" \
  -H "X-API-Key: $WEATHER_API_KEY"
40

## Slide 41

MCP
41

## Slide 42

MCP connects a host to servers
MCP HOST
AI application
Client A
Client B
LOCAL · STDIO
Filesystem server
REMOTE · HTTP
Sentry server
MCP is an alternative agent-facing interface—not a requirement for calling REST APIs.
42

## Slide 43

FastMCP projects OpenAPI operations as MCP
tools
OpenAPI operation
GET /weather
↓
MCP tool
get_weather(city, units)
By default, FastMCP converts each OpenAPI route into a discoverable MCP tool.
import httpx2
from fastmcp import FastMCP
spec = httpx2.get(
    "https://weather.example/openapi.json"
).json()
mcp = FastMCP.from_openapi(
    openapi_spec=spec,
    client=httpx2.AsyncClient(
        base_url="https://weather.example"
    ),
    name="Weather MCP",
)
FastMCP · OpenAPI integration ↗ 43

## Slide 44

Start MCP with separate credentials
UPSTREAM_API_KEY authorizes API calls; MCP_API_KEY protects the MCP endpoint.
Static tokens are for teaching/development; production deployments should verify JWTs or use OAuth.
import os, httpx2
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
upstream = httpx2.AsyncClient(
    base_url="https://weather.example",
    headers={"X-API-Key": os.environ["UPSTREAM_API_KEY"]})
mcp_auth = StaticTokenVerifier(tokens={
    os.environ["MCP_API_KEY"]: {"client_id": "course-agent"}})
mcp = FastMCP.from_openapi(
    openapi_spec=spec, client=upstream,
    name="Weather MCP", auth=mcp_auth)
mcp.run(transport="http", port=8001)
FastMCP · token verification ↗ 44

## Slide 45

The MCP client uses its own API key
Agent
harness
MCP key
→
MCP server
validate ·
authorize ·
dispatch
→
Weather API
upstream
key
Credential brokering: the server accepts one credential
and uses a diﬀerent credential upstream. The model
sees neither secret.
Separate credentials let the MCP server mediate access instead of forwarding its upstream secret.
import os
from fastmcp import Client
async with Client(
    "https://mcp.example/mcp",
    auth=os.environ["MCP_API_KEY"],
) as client:
    tools = await client.list_tools()
    result = await client.call_tool(
        "get_weather",
        {"city": "Pittsburgh", "units": "F"},
    )
FastMCP · bearer client authentication ↗ 45

## Slide 46

REST APIs and MCP: shared schemas, different
contracts
OpenAPI / HTTP API MCP
Shared Names, descriptions, and JSON Schema for structured inputs
Discovery Fetch an OpenAPI document Call tools/list at runtime
Invocation HTTP verb + path + parameters tools/call over an MCP transport
Authentication Client authenticates to the API Client authenticates to MCP; upstream auth is separate
Scope Describes HTTP operations Also supports resources, prompts, and extensions
OpenAPI describes a web API; MCP standardizes how an AI host discovers and invokes capabilities.
46

## Slide 47

Orchestrating multiple calls
47

## Slide 48

Serial tool-call cost
Generate
0.8s +
Weather
1.2s +
Generate
0.8s +
Calendar
0.9s +
Generate
0.8s +
Flight
1.1s +
Generate
0.8s
≈ 6.4 seconds
48

## Slide 49

Parallel tool calls
Model
Weather
Calendar
Flights
ONE ROUND TRIP
3 results
Independent calls can share one generation and one wait.
Two generation phases plus the slowest tool: 2 × 0.8 + max(1.2, 0.9, 1.1) ≈ 2.8 seconds.
49

## Slide 50

Parallelize only without dependencies
Safe to parallelize
Weather for Pittsburgh
Read today's calendar
Look up ﬂight status
↔
Must be sequenced
Find customer ID
Use ID to fetch orders
Refund selected order
Parallelize only independent, safely concurrent calls.
50

## Slide 51

Concurrent execution
Preserve call IDs when results ﬁnish out of order.
async def execute(call):
    args = json.loads(call.arguments)
    value = await TOOLS[call.name](**args)
    return call.call_id, value
results = await asyncio.gather(
    *(execute(call) for call in function_calls),
    return_exceptions=True,
)
51

## Slide 52

Evaluating tool use
52

## Slide 53

Berkeley Function Calling Leaderboard
Single turn
simple · multiple · parallel · multiple-parallel
Multi-turn
base · missing function · missing parameter · long
context
Agentic
web search · memory
Robustness
hallucination measurement · format sensitivity
Berkeley Function-Calling Leaderboard V4 ↗ 53

## Slide 54

Evaluate the whole stack
Level Question Example metric Execution? Typical failure
Selection Right tool? Precision / recall No Missing or extra call
Arguments Right values? AST / schema match No Wrong ﬁeld or value
Trajectory Right order? Sequence success Usually Bad dependency
Task Goal achieved? End-to-end success Yes Plausible wrong answer
54

## Slide 55

Quality has operational dimensions
Eﬃciency
Latency · calls · tokens · cost
A correct agent can still be unusably
slow or expensive.
Reliability
Timeouts · retries · partial failure
Report task success under realistic
provider behavior.
Safety
Policy · permissions · side eﬀects
Test adversarial outputs and
consequential actions.
55

## Slide 56

Operational tool failures
Model
wrong tool · bad arguments ·
ignores result
Harness
parse · auth · validation · ID
mismatch
Provider or tool
timeout · rate limit · execution
error
Production evaluation needs benchmark accuracy and operational failure rates.
56

## Slide 57

Provider tool-call error rates
OpenRouter provider analytics · Aug. 27, 2026 ↗ 57

## Slide 58

Takeaways
58

## Slide 59

Tool use is a layered system
1 Capabilities: tools add retrieval, execution, generation, and application actions.
2 Mechanics: schemas enter the prompt; model protocols emit calls; harnesses validate, dispatch,
and match results by ID.
3 Constraints: JSON Schema and grammar masks guarantee form—not semantic correctness.
4 Interfaces: direct REST calls and MCP are alternative ways to expose capabilities and manage
credentials.
5 Systems: orchestrate dependencies and concurrency; evaluate selection, arguments, outcomes,
cost, and operational failures.
59

## Slide 60

Thank you, Questions?
N e x t  C l a s s :  A g e n t  C a p a b i l i t i e s  2  —  C o n t e x t  M a n a g e m e n t  f o r  L o n g - C o n t e x t  L L M s
60

