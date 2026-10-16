# src/tools/dialogue_state_tool.py

from hello_agents.tools import Tool as BaseTool
from src.utils.state import DialogueState

class DialogueStateTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="dialogue_state_tool",
            description="判断当前对话应处于哪个阶段"
        )
        self.name = "dialogue_state_tool"
        self.description = "判断当前对话应处于哪个阶段"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "用户输入"},
                "current_state": {"type": "string", "description": "当前状态"}
            },
            "required": ["query"]
        }

    def run(self, query: str, current_state: str = "") -> str:
        # 初级版本--MVP规则：关键字触发
        if "睡不着" in query or "失眠" in query or "焦虑" in query:
            return DialogueState.ESCALATE.value
        if "听" in query or "音乐" in query:
            return DialogueState.MUSIC.value
        if "难受" in query or "不开心" in query:
            return DialogueState.COMFORT.value
        return DialogueState.MOOD.value
