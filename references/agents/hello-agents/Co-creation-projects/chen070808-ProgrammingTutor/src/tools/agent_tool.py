"""
AgentTool: 将 SimpleAgent 包装为 Tool，实现直接调用
这是比 A2A 协议更简单的多智能体模式
"""
from hello_agents import SimpleAgent
from hello_agents.tools import Tool
from typing import Dict, Any

class AgentTool(Tool):
    """将一个 SimpleAgent 包装为可被其他 Agent 调用的工具"""
    
    def __init__(self, agent: SimpleAgent, name: str, description: str):
        """
        Args:
            agent: 要包装的 SimpleAgent 实例
            name: 工具名称
            description: 工具描述
        """
        self.agent = agent
        self._name = name
        self._description = description
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    def get_parameters(self) -> list:
        """定义工具参数"""
        from hello_agents.tools.base import ToolParameter
        return [
            ToolParameter(
                name="query",
                type="string",
                description="发送给智能体的查询或指令",
                required=True
            )
        ]
    
    def run(self, parameters: Dict[str, Any]) -> str:
        """执行工具 - 直接调用被包装的 agent"""
        query = parameters.get('query', '')
        
        if not query:
            return "错误：需要提供 query 参数"
        
        try:
            # 直接调用 agent 的 run 方法
            return self.agent.run(query)
        except Exception as e:
            return f"调用 {self.name} 时出错: {str(e)}"
