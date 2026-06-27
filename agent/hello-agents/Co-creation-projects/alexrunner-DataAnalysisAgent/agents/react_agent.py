import json
from typing import Optional, List
from hello_agents import ReActAgent, HelloAgentsLLM, Config, Message, ToolRegistry
from dotenv import load_dotenv

MY_REACT_PROMPT = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下：
{tools}

请严格按照以下格式进行回应：

示例1：
{{
"Thought": "我需要先查询今天的美元兑人民币汇率，然后计算出净收益。",
"Action": {{"tool_name": "Search", "tool_input": "今天美元兑人民币汇率"}},
"Finish": []
}}

示例2：
{{
"Thought": "完成思考，准备给出最终答案。",
"Action": {{}},
"Finish": ["子任务1描述", "子任务2描述", "子任务3描述"]
}}

格式说明如下：
Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，格式必须是：`{{"tool_name": "Search", "tool_input": "今天美元兑人民币汇率"}}`，如果不采取行动，该项必须设置为{{}}。
Finish: 当你收集到足够的信息，能够回答用户的最终问题时，你必须在此处输出最终结果；如果没有，该项必须设置为[]。


现在，请开始解决以下问题：
Question: {question}
History: {history}
"""

# 加载环境变量
load_dotenv()

class NewReActAgent(ReActAgent):
    """
    重写的ReAct Agent - 推理与行动结合的智能体
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        tool_registry: ToolRegistry,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_steps: int = 5,
        custom_prompt: Optional[str] = None
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.current_history: List[str] = []
        self.prompt_template = custom_prompt if custom_prompt else MY_REACT_PROMPT
        print(f"✅ {name} 初始化完成，最大步数: {max_steps}")

    def run(self, input_text: str, **kwargs) -> str:
        """运行ReAct Agent"""
        self.current_history = []
        current_step = 0

        print(f"\n🤖 {self.name} 开始处理问题: {input_text}")

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- 第 {current_step} 步 ---")

            # 1. 构建提示词
            tools_desc = self.tool_registry.get_tools_description()
            history_str = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
                tools=tools_desc,
                question=input_text,
                history=history_str
            )

            # 2. 调用LLM
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm.invoke(messages, **kwargs)
            print(response_text)

            # 3. 解析输出
            thought, action, finish = self._parse_output(response_text)

            # 4. 检查完成条件
            if finish:
                final_answer = finish
                return final_answer

            # 5. 执行工具调用
            if action:
                tool_name, tool_input = self._parse_action(action)
                observation = self.tool_registry.execute_tool(tool_name, tool_input)
                self.current_history.append(f"Action: {action}")
                self.current_history.append(f"Observation: {observation}")

        # 达到最大步数：让 LLM 一次性输出最终答案
        print(f"\n⚠️ 达到最大步数 {self.max_steps}，开始生成最终答案")
        history_str = "\n".join(self.current_history)
        final_prompt = self.prompt_template.format(
                tools="",
                question=input_text,
                history=history_str +
                "\n\n请基于以上信息一次性给出最终答案（必须填入 Finish 字段）"
            )
        messages = [{"role": "user", "content": final_prompt}]
        final_response = self.llm.invoke(messages, **kwargs)
        thought, action, finish = self._parse_output(final_response)
        if finish:
            final_answer = finish
            return final_answer
        else:
            print("警告：在生成最终答案时，没有找到 Finish 字段。")
            return "抱歉，尝试生成最终答案时出错。"

    def _parse_output(self, text: str):
        # 清理模型输出，尝试提取JSON部分
        cleaned_text = self._extract_json_from_response(text)

        try:
            data = json.loads(cleaned_text)
            thought = data.get("Thought", "")
            action = data.get("Action")
            finish = data.get("Finish", [])
            return thought, action, finish
        except json.JSONDecodeError as e:
            print(f"警告：LLM返回的文本不是有效的JSON格式。原始文本: {text}")
            print(f"JSON解析错误: {e}")
            return "", None, ""

    def _extract_json_from_response(self, text: str) -> str:
        """从模型响应中提取JSON部分"""
        start = text.find('{')
        end = text.rfind('}')

        if start != -1 and end != -1 and start < end:
            candidate = text[start:end+1]
            # 验证这是否是有效的JSON
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

    def _parse_action(self, action_text: dict):
        # 提取 tool_name 和 tool_input
        if not action_text or not isinstance(action_text, dict):
            return None, None
        tool_name = action_text.get("tool_name")
        tool_input = action_text.get("tool_input")
        return tool_name, tool_input


if __name__ == "__main__":
    llm = HelloAgentsLLM()
    tool_registry = ToolRegistry()
    agent = NewReActAgent(
        name="Agent",
        llm=llm,
        tool_registry=tool_registry,
        max_steps=5
    )
    question = "请简单介绍你自己"
    try:
        answer = agent.run(question)
        print(f"最终答案: {answer}")
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
