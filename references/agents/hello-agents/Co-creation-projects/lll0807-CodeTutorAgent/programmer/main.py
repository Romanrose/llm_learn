import os
import sys
from dotenv import load_dotenv
from hello_agents.core.llm import HelloAgentsLLM
from services.knowledge import LearningKnowledgeService

# 2. 初始化 Tutor（自动创建所有子智能体）
from agents.tutor import TutorAgent

load_dotenv()

if "src" not in sys.path:
    sys.path.append(os.path.abspath("src"))

# 初始化 LLM
llm = HelloAgentsLLM()

print("✅ 环境配置完成")
print("✅ LLM 已初始化")

print("创建智能编程导师...")
knowledge = LearningKnowledgeService(user_id="1")
tutor = TutorAgent(llm, knowledge)

while True:
    user_goal = input("请输入：")
    # 我想学习 Python 中的列表推导式
    # 我想更新学习计划
    print(f"用户目标: {user_goal}\n")

    # Tutor 会调用 call_planner 工具
    response = tutor.run(f"用户说：'{user_goal}'。")

    print("=== Tutor 回应 ===")
    print(response)
