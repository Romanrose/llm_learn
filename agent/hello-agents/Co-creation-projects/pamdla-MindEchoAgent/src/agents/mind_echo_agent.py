# src/agents/mind_echo_agent.py

from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool, A2ATool
from src.tools.dialogue_state_tool import DialogueStateTool
from src.tools.mood_music_tool import MoodMusicTool
from src.tools.text_comfort_tool import TextComfortTool
from src.tools.mood_summary_tool import MoodSummaryTool
from src.utils.state import DialogueState

def create_mind_echo_agent(user_id: str = "user001"):
    llm = HelloAgentsLLM()

    system_prompt = """
你是 MindEchoAgent（心境回响），负责情绪陪伴与音乐推荐。
你需要：
1）识别用户心境，每次对话先判断状态（MOOD/COMFORT/MUSIC/ESCALATE）
2）状态决定调用哪个工具，比如提供安抚/音乐推荐
3）若用户出现“持续焦虑、睡不着、失眠”等关键词或状态为 ESCALATE，必须升级到 SleepAgent（A2A）
"""

    agent = SimpleAgent(
        name="MindEchoAgent",
        llm=llm,
        system_prompt=system_prompt
    )

    registry = ToolRegistry()
    registry.register_tool(MemoryTool(user_id=user_id))
    registry.register_tool(DialogueStateTool())
    registry.register_tool(TextComfortTool())
    registry.register_tool(MoodMusicTool())
    registry.register_tool(MoodSummaryTool())

    # A2A 工具：指向 SleepAgent 服务
    sleep_tool = A2ATool(
        agent_url="http://localhost:6000",  # SleepAgent 默认端口
        name="sleep_agent",
        description="睡眠专家，处理失眠/焦虑等问题"
    )
    registry.register_tool(sleep_tool)

    agent.tool_registry = registry
    agent.current_state = DialogueState.INIT.value

    return agent
