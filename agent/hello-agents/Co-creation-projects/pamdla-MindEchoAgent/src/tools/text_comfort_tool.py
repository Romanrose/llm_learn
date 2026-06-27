# src/tools/text_comfort_tool.py

from hello_agents.tools import Tool as BaseTool

class TextComfortTool(BaseTool):

    def __init__(self):
        super().__init__(
            name="text_comfort_tool",
            description="提供安抚要点，LLM 负责生成自然语言"
        )
        self.name = "text_comfort_tool"
        self.description = "提供安抚要点，LLM 负责生成自然语言"

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
            "安抚要点：\n"
            "1. 共情：承认情绪存在\n"
            "2. 允许停顿：不用强迫自己立刻变好\n"
            "3. 小动作：深呼吸、短暂休息、听轻音乐\n"
            "4. 若持续困扰，建议升级到 SleepAgent"
        )
