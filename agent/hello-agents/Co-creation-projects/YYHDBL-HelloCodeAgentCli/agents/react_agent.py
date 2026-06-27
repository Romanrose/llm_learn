"""ReAct Agent实现 - 推理与行动结合的智能体"""

import re
from typing import Optional, List, Tuple, Callable, Dict, Any
from core.agent import Agent
from core.llm import HelloAgentsLLM
from core.config import Config
from core.message import Message
from tools.registry import ToolRegistry
from utils.cli_ui import Spinner, c, PRIMARY, ACCENT, INFO, hr, log_tool_event, clamp_text

# 默认ReAct提示词模板
DEFAULT_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤：

**Thought:** 分析当前问题，思考需要什么信息或采取什么行动。
**Action:** 选择一个行动，格式必须是以下之一：
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循：工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动："""

class ReActAgent(Agent):
    """
    ReAct (Reasoning and Acting) Agent
    
    结合推理和行动的智能体，能够：
    1. 分析问题并制定行动计划
    2. 调用外部工具获取信息
    3. 基于观察结果进行推理
    4. 迭代执行直到得出最终答案
    
    这是一个经典的Agent范式，特别适合需要外部信息的任务。
    """
    
    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        tool_registry: Optional[ToolRegistry] = None,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_steps: int = 5,
        custom_prompt: Optional[str] = None,
        observation_summarizer: Optional[Callable[[str, str, str], str]] = None,
        summarize_threshold_chars: int = 2000,
        finalize_on_max_steps: bool = True,
        early_stop_on_repeat: bool = True,
        repeat_action_threshold: int = 2,
    ):
        """
        初始化ReActAgent

        Args:
            name: Agent名称
            llm: LLM实例
            tool_registry: 工具注册表（可选，如果不提供则创建空的工具注册表）
            system_prompt: 系统提示词
            config: 配置对象
            max_steps: 最大执行步数
            custom_prompt: 自定义提示词模板
        """
        super().__init__(name, llm, system_prompt, config)

        # 如果没有提供tool_registry，创建一个空的
        if tool_registry is None:
            self.tool_registry = ToolRegistry()
        else:
            self.tool_registry = tool_registry

        self.max_steps = max_steps
        self.current_history: List[str] = []
        self.last_trace: List[Dict[str, Any]] = []
        self.observation_summarizer = observation_summarizer
        self.summarize_threshold_chars = summarize_threshold_chars
        self.finalize_on_max_steps = finalize_on_max_steps
        self.early_stop_on_repeat = early_stop_on_repeat
        self.repeat_action_threshold = repeat_action_threshold

        # 设置提示词模板：用户自定义优先，否则使用默认模板
        self.prompt_template = custom_prompt if custom_prompt else DEFAULT_REACT_PROMPT

    def add_tool(self, tool):
        """
        添加工具到工具注册表
        支持MCP工具的自动展开

        Args:
            tool: 工具实例(可以是普通Tool或MCPTool)
        """
        # 检查是否是MCP工具
        if hasattr(tool, 'auto_expand') and tool.auto_expand:
            # MCP工具会自动展开为多个工具
            if hasattr(tool, '_available_tools') and tool._available_tools:
                for mcp_tool in tool._available_tools:
                    # 创建包装工具
                    from tools.base import Tool
                    wrapped_tool = Tool(
                        name=f"{tool.name}_{mcp_tool['name']}",
                        description=mcp_tool.get('description', ''),
                        func=lambda input_text, t=tool, tn=mcp_tool['name']: t.run({
                            "action": "call_tool",
                            "tool_name": tn,
                            "arguments": {"input": input_text}
                        })
                    )
                    self.tool_registry.register_tool(wrapped_tool)
                print(f"✅ MCP工具 '{tool.name}' 已展开为 {len(tool._available_tools)} 个独立工具")
            else:
                self.tool_registry.register_tool(tool)
        else:
            self.tool_registry.register_tool(tool)

    def run(self, input_text: str, **kwargs) -> str:
        """
        运行ReAct Agent
        
        Args:
            input_text: 用户问题
            **kwargs: 其他参数
            
        Returns:
            最终答案
        """
        self.current_history = []
        self.last_trace = []
        current_step = 0
        
        # Avoid dumping huge stitched prompts to console (CLI UX)
        preview = input_text.replace("\n", " ")
        if len(preview) > 160:
            preview = preview[:160] + "..."
        print("\n" + hr("=", 80))
        print(c(f"🤖 {self.name}", PRIMARY) + " " + c(f"{preview}", INFO))
        print(hr("=", 80))
        
        repeat_count = 0
        last_action_sig: Optional[str] = None

        while current_step < self.max_steps:
            current_step += 1
            print(c(f"\n--- Step {current_step}/{self.max_steps} ---", ACCENT))
            
            # 构建提示词
            tools_desc = self.tool_registry.get_tools_description()
            history_str = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
                tools=tools_desc,
                question=input_text,
                history=history_str
            )
            
            # 调用LLM
            messages = [{"role": "user", "content": prompt}]
            spinner = Spinner("Thinking…")
            spinner.start()
            response_text = self.llm.invoke(messages, **kwargs)
            spinner.stop()
            
            if not response_text:
                print("❌ 错误：LLM未能返回有效响应。")
                break
            
            # 解析输出
            thought, action = self._parse_output(response_text)
            
            if thought:
                print(c("Thought:", INFO), thought)
            
            if not action:
                # One forced retry: ask model to rewrite in strict format (helps for greetings / bilingual models)
                try:
                    repair_sys = (
                        "You MUST output exactly two lines:\n"
                        "Thought: ...\n"
                        "Action: tool_name[tool_input] OR Finish[final answer]\n"
                        "No extra text. No markdown headers."
                    )
                    repair_user = f"Rewrite the following into the required two-line format:\n\n{response_text}"
                    spinner = Spinner("Repairing format…")
                    spinner.start()
                    repaired = self.llm.invoke(
                        [{"role": "system", "content": repair_sys}, {"role": "user", "content": repair_user}],
                        max_tokens=200,
                    )
                    spinner.stop()
                    thought, action = self._parse_output(repaired or "")
                except Exception:
                    pass

                if not action:
                    print("⚠️ 警告：未能解析出有效的Action，流程终止。")
                    break
            
            # 检查是否完成
            if action.startswith("Finish"):
                final_answer = self._parse_action_input(action)
                print(c("Finish:", PRIMARY))
                print(final_answer)
                
                # 保存到历史记录
                self.add_message(Message(input_text, "user"))
                self.add_message(Message(final_answer, "assistant"))
                
                return final_answer
            
            # 执行工具调用
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or tool_input is None:
                self.current_history.append("Observation: 无效的Action格式，请检查。")
                continue
            
            log_tool_event(tool_name, tool_input)
            
            # 调用工具
            observation = self.tool_registry.execute_tool(tool_name, tool_input)
            observation_full = observation
            observation_summary = None
            if (
                self.observation_summarizer is not None
                and isinstance(observation, str)
                and len(observation) > self.summarize_threshold_chars
            ):
                try:
                    observation_summary = self.observation_summarizer(tool_name, tool_input, observation)
                    if observation_summary and isinstance(observation_summary, str):
                        observation = observation_summary.strip() + "\n...truncated...\n"
                except Exception:
                    # fall back to raw observation
                    pass

            log_tool_event(f"{tool_name} result", clamp_text(str(observation), limit=6000))

            # 提前终止：重复相同 action 且无明显进展
            action_sig = f"{tool_name}|{tool_input}".strip()
            if self.early_stop_on_repeat:
                if last_action_sig == action_sig:
                    repeat_count += 1
                else:
                    repeat_count = 0
                last_action_sig = action_sig

                if repeat_count >= self.repeat_action_threshold:
                    self.current_history.append("Observation: 已检测到重复行动，建议停止继续工具调用并给出当前能提供的结论/下一步。")
                    break
            
            # 更新历史
            self.current_history.append(f"Action: {action}")
            self.current_history.append(f"Observation: {observation}")
            self.last_trace.append(
                {
                    "action": action,
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "observation_full_len": len(observation_full) if isinstance(observation_full, str) else None,
                    "observation_summary": observation_summary,
                }
            )
        
        # 未在循环内 Finish：进行兜底收敛
        if self.finalize_on_max_steps:
            try:
                tools_desc = self.tool_registry.get_tools_description()
                history_str = "\n".join(self.current_history[-24:])
                finalize_prompt = (
                    "你是一个 ReAct 代理的最终收敛器。现在工具调用阶段结束了。"
                    "请基于已有的 Thought/Action/Observation 历史，给出一个尽可能有用的最终回答。"
                    "要求：\n"
                    "1) 不要再调用工具\n"
                    "2) 明确已完成的证据/发现\n"
                    "3) 如果信息不足，说清楚缺少什么，并给出下一步最小化建议（1-3条）\n"
                )
                messages = [
                    {"role": "system", "content": finalize_prompt},
                    {"role": "user", "content": f"Question:\n{input_text}\n\nTools:\n{tools_desc}\n\nTrace:\n{history_str}"},
                ]
                final_answer = self.llm.invoke(messages, max_tokens=600)
                if final_answer:
                    self.add_message(Message(input_text, "user"))
                    self.add_message(Message(final_answer, "assistant"))
                    return final_answer
            except Exception:
                pass

        print("⏰ 已达到最大步数，流程终止。")
        final_answer = "抱歉，我无法在限定步数内完成这个任务。你可以缩小范围或指定目标文件/模块。"
        
        # 保存到历史记录
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_answer, "assistant"))
        
        return final_answer
    
    def _parse_output(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析LLM输出，提取思考和行动。

        兼容常见变体：
        - Thought/Action 的全角冒号（：）
        - 中文标签：思考/行动
        - Markdown 强调：**Thought:** / **Action:**
        """
        # Normalize to make regex easier
        t = (text or "").strip()

        # Primary: strict 2-line format, allow markdown markers and fullwidth colon
        m = re.search(
            r"(?:\*\*)?(Thought|思考)(?:\*\*)?\s*[:：]\s*(.*?)\n(?:\*\*)?(Action|行动)(?:\*\*)?\s*[:：]\s*(.*)\s*$",
            t,
            flags=re.DOTALL,
        )
        if m:
            thought = m.group(2).strip()
            action = m.group(4).strip()
            return thought or None, action or None

        # Fallback: find first Thought-like line and first Action-like line anywhere
        thought_match = re.search(r"(?:\*\*)?(Thought|思考)(?:\*\*)?\s*[:：]\s*(.*)", t)
        action_match = re.search(r"(?:\*\*)?(Action|行动)(?:\*\*)?\s*[:：]\s*(.*)", t)
        thought = thought_match.group(2).strip() if thought_match else None
        action_raw = action_match.group(2).strip() if action_match else None
        
        # 关键修复：如果 action 中包含另一个 Thought/Action/Observation，截断到该位置
        # 防止模型一次输出多个 Thought/Action 循环时，把后续内容都当作第一个 Action 的输入
        if action_raw:
            stop_patterns = [
                r"\nThought:", r"\n思考:", r"\nAction:", r"\n行动:",
                r"\nObservation:", r"\n观察:", r"\n\*\*Thought", r"\n\*\*Action",
            ]
            earliest_stop = len(action_raw)
            for pat in stop_patterns:
                m = re.search(pat, action_raw, re.IGNORECASE)
                if m and m.start() < earliest_stop:
                    earliest_stop = m.start()
            action_raw = action_raw[:earliest_stop].strip()
        
        return thought, action_raw
    
    def _parse_action(self, action_text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析行动文本，提取工具名称和输入
        
        使用括号匹配算法而非贪婪正则，正确处理嵌套 JSON。
        """
        # 先找工具名
        name_match = re.match(r"(\w+)\[", action_text)
        if not name_match:
            return None, None
        
        tool_name = name_match.group(1)
        start = name_match.end() - 1  # '[' 的位置
        
        # 使用括号匹配找到对应的 ']'
        depth = 0
        in_string = False
        escape = False
        end_pos = None
        
        for i, c in enumerate(action_text[start:], start):
            if escape:
                escape = False
                continue
            if c == '\\' and in_string:
                escape = True
                continue
            if c == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end_pos = i
                    break
        
        if end_pos is not None:
            tool_input = action_text[start + 1:end_pos]
            return tool_name, tool_input
        
        # fallback: 如果括号不匹配，尝试简单正则（不跨行）
        # 注意：不使用 re.DOTALL，这样 . 不会匹配换行符
        match = re.match(r"(\w+)\[([^\n]*)\]", action_text)
        if match:
            return match.group(1), match.group(2)
        
        return None, None
    
    def _parse_action_input(self, action_text: str) -> str:
        """解析行动输入

        兼容多种 Finish 书写：
        - Finish[...]
        - Finish：... / Finish: ...（无方括号）
        - Finish\n<content>（换行后直接给内容/补丁）
        """
        # 规范格式：Finish[...]
        match = re.match(r"\w+\[(.*)\]\s*$", action_text, flags=re.DOTALL)
        if match:
            return match.group(1)

        # 宽松格式：Finish: ... 或 Finish：...
        m2 = re.match(r"finish\s*[:：]\s*(.*)", action_text, flags=re.IGNORECASE | re.DOTALL)
        if m2:
            return m2.group(1)

        # 再宽松：去掉前缀 "Finish" 后的剩余内容
        if action_text.lower().startswith("finish"):
            return action_text[len("finish"):].strip()

        return ""
