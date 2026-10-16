# src/tools/mood_summary_tool.py

from hello_agents.tools import Tool as BaseTool

class MoodSummaryTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="mood_summary_tool",
            description="生成长期记忆的心境总结模板（LLM生成最终内容）"
        )
        self.name = "mood_summary_tool"
        self.description = "生成长期记忆的心境总结模板（LLM生成最终内容）"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "用户输入"}
            },
            "required": ["query"]
        }

    def run(self, query: str) -> str:
        return (
            "请根据以下内容生成一个简短的心境总结（用于长期记忆）：\n"
            f"用户输入：{query}\n"
            "需要包含：\n"
            "1. 当前心境（1-2句）\n"
            "2. 触发因素（如果有）\n"
            "3. 可能的长期偏好（音乐/情绪）\n"
        )
