"""
A2A 协议 + HelloAgents SimpleAgent 集成案例

展示如何将 A2A 协议的 Agent 作为工具集成到 SimpleAgent 中
"""

from hello_agents.protocols import A2AServer, A2AClient
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import ToolRegistry, Tool, ToolParameter
import threading
import time
from typing import Dict, Any

# ============================================================
# 1. 创建专业 A2A Agent 服务
# ============================================================

# 技术专家 Agent
tech_expert = A2AServer(
    name="tech_expert",
    description="技术专家，回答技术相关问题",
    version="1.0.0"
)

@tech_expert.skill("answer")
def answer_tech_question(text: str) -> str:
    """回答技术问题"""
    import re
    match = re.search(r'answer\s+(.+)', text, re.IGNORECASE)
    question = match.group(1).strip() if match else text
    
    print(f"  [技术专家] 回答问题: {question}")
    return f"技术回答：关于'{question}'，这是一个技术问题的专业解答..."

# 销售顾问 Agent
sales_advisor = A2AServer(
    name="sales_advisor",
    description="销售顾问，回答销售问题",
    version="1.0.0"
)

@sales_advisor.skill("answer")
def answer_sales_question(text: str) -> str:
    """回答销售问题"""
    import re
    match = re.search(r'answer\s+(.+)', text, re.IGNORECASE)
    question = match.group(1).strip() if match else text
    
    print(f"  [销售顾问] 回答问题: {question}")
    return f"销售回答：关于'{question}'，我们有特别优惠..."

# ============================================================
# 2. 启动 A2A Agent 服务
# ============================================================

print("="*60)
print("🚀 启动专业 Agent 服务")
print("="*60)

threading.Thread(target=lambda: tech_expert.run(port=6000), daemon=True).start()
threading.Thread(target=lambda: sales_advisor.run(port=6001), daemon=True).start()

print("✓ 技术专家 Agent 启动在 http://localhost:6000")
print("✓ 销售顾问 Agent 启动在 http://localhost:6001")

print("\n⏳ 等待服务启动...")
time.sleep(3)

# ============================================================
# 3. 创建 A2A 工具（封装 A2A Agent 为 Tool）
# ============================================================

class A2ATool(Tool):
    """将 A2A Agent 封装为 HelloAgents Tool"""

    def __init__(self, name: str, description: str, agent_url: str, skill_name: str = "answer"):
        self.agent_url = agent_url
        self.skill_name = skill_name
        self.client = A2AClient(agent_url)
        self._name = name
        self._description = description
        self._parameters = [
            ToolParameter(
                name="question",
                type="string",
                description="要问的问题",
                required=True
            )
        ]

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def get_parameters(self) -> list[ToolParameter]:
        """获取工具参数"""
        return self._parameters

    def run(self, **kwargs) -> str:
        """执行工具"""
        question = kwargs.get('question', '')
        result = self.client.execute_skill(self.skill_name, f"answer {question}")
        if result.get('status') == 'success':
            return result.get('result', 'No response')
        else:
            return f"Error: {result.get('error', 'Unknown error')}"

# 创建工具
tech_tool = A2ATool(
    name="tech_expert",
    description="技术专家，回答技术相关问题",
    agent_url="http://localhost:6000"
)

sales_tool = A2ATool(
    name="sales_advisor",
    description="销售顾问，回答销售相关问题",
    agent_url="http://localhost:6001"
)

# ============================================================
# 4. 创建 SimpleAgent（使用 A2A 工具）
# ============================================================

print("\n" + "="*60)
print("🤖 创建接待员 SimpleAgent")
print("="*60)

# 初始化 LLM
llm = HelloAgentsLLM()

# 创建接待员 Agent
receptionist = SimpleAgent(
    name="接待员",
    llm=llm,
    system_prompt="""你是客服接待员，负责：
1. 分析客户问题类型（技术问题 or 销售问题）
2. 使用合适的工具（tech_expert 或 sales_advisor）获取答案
3. 整理答案并返回给客户

可用工具：
- tech_expert: 回答技术问题
- sales_advisor: 回答销售问题

请保持礼貌和专业。"""
)

# 添加 A2A 工具
receptionist.add_tool(tech_tool)
receptionist.add_tool(sales_tool)

print("✓ 接待员 Agent 创建完成")
print("✓ 已集成 A2A 工具: tech_expert, sales_advisor")

# ============================================================
# 5. 测试集成系统
# ============================================================

print("\n" + "="*60)
print("🧪 测试 A2A + SimpleAgent 集成")
print("="*60)

# 测试问题
test_questions = [
    "你们的产品有什么优惠活动吗？",
    "如何配置服务器的SSL证书？",
    "我想了解一下价格方案"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n问题 {i}: {question}")
    print("-" * 60)

    try:
        # 使用 SimpleAgent 的 run 方法
        response = receptionist.run(question)
        print(f"回答: {response}")
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

    print()

# ============================================================
# 6. 保持服务运行
# ============================================================

print("="*60)
print("💡 系统仍在运行")
print("="*60)
print("你可以继续测试或按 Ctrl+C 停止\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\n✅ 系统已停止")

