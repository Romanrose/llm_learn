# src/tools/mood_music_tool.py

from hello_agents.tools import Tool as BaseTool
from src.utils.loader import load_mood_music_map

class MoodMusicTool(BaseTool):
    """
    情绪 -> 音乐推荐工具（完全模拟）
    """

    def __init__(self):
        super().__init__(
            name="mood_music_tool",
            description = "根据用户描述的心境，返回对应的音乐推荐列表"
        )
        self.name = "mood_music_tool"
        self.description = "根据用户描述的心境，返回对应的音乐推荐列表"
        self.mood_map = load_mood_music_map()

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "用户输入"}
            },
            "required": ["query"]
        }

    def run(self, query: str) -> str:
        """
        query: 用户输入的心境描述
        """
        # 极简规则匹配（稳）
        for mood, songs in self.mood_map.items():
            if mood in query:
                return self._format_result(mood, songs)

        # fallback
        return self._format_result(
            "未识别",
            ["Tycho - Awake", "Ólafur Arnalds - Near Light"]
        )

    def _format_result(self, mood, songs):
        result = f"🎧 当前识别的心境：{mood}\n\n推荐音乐：\n"
        for i, song in enumerate(songs, 1):
            result += f"{i}. {song}\n"
        return result
