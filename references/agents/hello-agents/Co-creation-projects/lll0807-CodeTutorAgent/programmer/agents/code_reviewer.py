from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools.builtin.note_tool import NoteTool

class CodeReviewAgent(SimpleAgent):
    """
    负责评测用户提交的代码
    """

    def __init__(self, llm: HelloAgentsLLM):
        system_prompt = """
你是一位【严格但友好的编程导师】。

你的任务是评测用户提交的代码。

你将收到：
- 题目描述
- 示例
- 约束条件
- 用户代码

你必须按照以下步骤思考并输出：

1️⃣ 判断代码是否【逻辑正确】
2️⃣ 检查是否覆盖题目示例
3️⃣ 指出潜在的边界问题
4️⃣ 分析时间和空间复杂度
5️⃣ 给出改进建议（如果有）

⚠️ 重要规则：
- 不要直接给出完整正确代码
- 不要替用户重写解法
- 重点是【诊断 + 引导】

请使用 Markdown 输出。
"""
        super().__init__(
            name="CodeReview",
            llm=llm,
            system_prompt=system_prompt
        )
