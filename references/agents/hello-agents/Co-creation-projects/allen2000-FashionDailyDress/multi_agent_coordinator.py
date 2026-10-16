"""
多智能体协调器
管理天气查询智能体和穿衣建议智能体的协作
"""
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import MCPTool
from fashion_agent import FashionAgent
import os
from dotenv import load_dotenv

load_dotenv()

class MultiAgentCoordinator:
    """多智能体协调器"""
    
    def __init__(self):
        """初始化协调器"""
        # 创建主协调智能体
        self.coordinator = SimpleAgent(
            name="智能体协调器",
            llm=HelloAgentsLLM(
                api_key=os.environ.get("LLM_API_KEY"),
                base_url=os.environ.get("LLM_BASE_URL"),
                model=os.environ.get("LLM_MODEL_ID")
            )
        )
        
        # 创建天气查询智能体
        self.weather_agent = self._create_weather_agent()
        
        # 创建穿衣建议智能体
        self.fashion_agent = FashionAgent()
        
        # 设置协调器的系统提示词
        self._setup_coordinator_prompt()
    
    def _create_weather_agent(self):
        """创建天气查询智能体"""
        weather_agent = SimpleAgent(
            name="天气查询助手",
            llm=HelloAgentsLLM(
                api_key=os.environ.get("LLM_API_KEY"),
                base_url=os.environ.get("LLM_BASE_URL"),
                model=os.environ.get("LLM_MODEL_ID")
            )
        )
        
        # 配置MCP工具使用本地的weather_mcp.py服务器
        mcp_tool = MCPTool(
            name="query_weather",
            server_command=["python", "weather_mcp.py"]
        )
        
        weather_agent.add_tool(mcp_tool)
        
        # 设置天气智能体的系统提示词
        weather_agent.system_prompt = """你是一个天气查询助手。你可以使用query_weather工具查询指定城市的天气信息。

请根据用户提供的城市名称查询天气，并返回详细的天气信息。"""
        
        return weather_agent
    
    def _setup_coordinator_prompt(self):
        """设置协调器的系统提示词"""
        system_prompt = """你是一个智能体协调器，负责管理天气查询智能体和穿衣建议智能体的协作。

你的工作流程：
1. 接收用户关于天气和穿衣建议的查询
2. 调用天气查询智能体获取指定城市的天气信息
3. 将天气信息传递给穿衣建议智能体
4. 整合两个智能体的结果，提供完整的天气和穿衣建议

协作规则：
- 首先获取准确的天气信息
- 然后基于天气信息提供专业的穿衣建议
- 确保信息的准确性和实用性
- 提供清晰、完整的最终结果

请按照这个流程处理用户的查询。"""
        
        self.coordinator.system_prompt = system_prompt
    
    def process_query(self, query):
        """
        处理用户查询，协调多个智能体完成任务
        
        Args:
            query: 用户查询字符串
            
        Returns:
            包含天气信息和穿衣建议的完整结果
        """
        print("=== 开始处理查询 ===")
        print(f"用户查询: {query}")
        print()
        
        # 步骤1: 使用天气智能体查询天气
        print("步骤1: 查询天气信息...")
        weather_response = self.weather_agent.run(query)
        print(f"天气查询结果: {weather_response}")
        print()
        
        # 步骤2: 使用穿衣建议智能体提供建议
        print("步骤2: 生成穿衣建议...")
        fashion_advice = self.fashion_agent.get_fashion_advice(weather_response)
        print(f"穿衣建议: {fashion_advice}")
        print()
        
        # 步骤3: 整合结果
        print("步骤3: 整合最终结果...")
        final_result = self._format_final_result(weather_response, fashion_advice)
        
        return final_result
    
    def _format_final_result(self, weather_info, fashion_advice):
        """
        格式化最终结果
        
        Args:
            weather_info: 天气信息
            fashion_advice: 穿衣建议
            
        Returns:
            格式化的完整结果
        """
        result = f"""🎯 智能体协作完成！以下是您的完整天气和穿衣建议：

🌤️ 天气信息：
{weather_info}

👗 穿衣建议：
{fashion_advice}

💡 温馨提示：
- 请根据实际体感温度调整穿着
- 考虑当天的具体活动安排
- 如有特殊需求，可进一步咨询"""
        
        return result
    
    def get_weather_only(self, city_name):
        """
        仅获取天气信息（不包含穿衣建议）
        
        Args:
            city_name: 城市名称
            
        Returns:
            天气信息
        """
        query = f"查询{city_name}的天气"
        return self.weather_agent.run(query)
    
    def get_fashion_advice_only(self, weather_info):
        """
        基于现有天气信息获取穿衣建议
        
        Args:
            weather_info: 天气信息字符串
            
        Returns:
            穿衣建议
        """
        return self.fashion_agent.get_fashion_advice(weather_info)


def main():
    """测试函数"""
    # 创建多智能体协调器
    coordinator = MultiAgentCoordinator()
    
    # 测试查询
    test_query = "查询上海的天气并给出穿衣建议"
    
    print("=== 多智能体协调器测试 ===")
    result = coordinator.process_query(test_query)
    print(result)


if __name__ == "__main__":
    main()