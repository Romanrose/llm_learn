# src/agents/sleep_agent.py

from hello_agents.protocols import A2AServer

# A2A 服务端：睡眠专家
sleep_agent = A2AServer(
    name="sleep_agent",
    description="睡眠专家，提供助眠建议与睡眠策略"
)

@sleep_agent.skill("answer")
def answer_sleep_question(text: str) -> str:
    # MVP：直接返回固定策略（可扩展）
    return (
        "睡眠建议：\n"
        "1. 关闭电子设备，做 5 分钟深呼吸\n"
        "2. 选择一首轻柔音乐，音量调低\n"
        "3. 若持续焦虑，建议记录当下思绪并写下 3 件感恩的事\n"
        "\n（如需要更个性化建议，可继续描述你的睡眠情况）"
    )
