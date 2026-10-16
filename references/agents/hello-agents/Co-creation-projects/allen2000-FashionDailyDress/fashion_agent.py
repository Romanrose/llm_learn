"""
穿衣建议智能体
专门处理基于天气信息的穿衣建议
"""
from hello_agents import SimpleAgent, HelloAgentsLLM
import os
from dotenv import load_dotenv

load_dotenv()

class FashionAgent:
    """穿衣建议智能体"""
    
    def __init__(self, name="时尚顾问"):
        """初始化穿衣建议智能体"""
        self.name = name
        self.agent = SimpleAgent(
            name=name, 
            llm=HelloAgentsLLM(
                api_key=os.environ.get("LLM_API_KEY"),
                base_url=os.environ.get("LLM_BASE_URL"),
                model=os.environ.get("LLM_MODEL_ID")
            )
        )
        
        # 设置智能体的系统提示词
        self._setup_prompt()
    
    def _setup_prompt(self):
        """设置智能体的系统提示词"""
        system_prompt = """你是一个专业的时尚顾问，专门根据天气信息提供穿衣建议。

你的职责：
1. 根据天气信息（温度、湿度、风速、天气状况）提供合适的穿衣建议
2. 考虑不同季节、场合和人群的穿衣需求
3. 提供具体的服装搭配建议，包括上衣、裤子、外套、鞋子等
4. 考虑保暖、防晒、防雨等实际需求
5. 给出时尚且实用的建议

穿衣建议指南：
- 高温天气（>30°C）：建议轻薄透气的衣物，注意防晒
- 温暖天气（20-30°C）：建议舒适的单层衣物
- 凉爽天气（10-20°C）：建议长袖衣物，可搭配薄外套
- 寒冷天气（<10°C）：建议保暖衣物，如毛衣、羽绒服等
- 雨天：建议防水外套和雨具
- 大风天气：建议防风衣物

请根据具体的天气信息提供详细、实用的穿衣建议。"""
        
        self.agent.system_prompt = system_prompt
    
    def get_fashion_advice(self, weather_info):
        """
        基于天气信息获取穿衣建议
        
        Args:
            weather_info: 天气信息字符串或字典
            
        Returns:
            穿衣建议字符串
        """
        # 构建查询提示
        query = f"""请根据以下天气信息提供穿衣建议：

天气信息：
{weather_info}

请提供详细的穿衣建议，包括：
1. 适合的服装类型
2. 具体的搭配建议
3. 注意事项
4. 时尚建议"""
        
        # 使用智能体获取建议
        response = self.agent.run(query)
        return response
    
    def get_detailed_fashion_advice(self, weather_data):
        """
        基于结构化天气数据获取更详细的穿衣建议
        
        Args:
            weather_data: 包含天气信息的字典
            
        Returns:
            详细的穿衣建议字符串
        """
        if isinstance(weather_data, dict):
            # 从字典中提取关键信息
            temperature = weather_data.get('temperature', '未知')
            description = weather_data.get('description', '未知')
            humidity = weather_data.get('humidity', '未知')
            wind_speed = weather_data.get('wind_speed', '未知')
            
            query = f"""请根据以下详细的天气数据提供专业的穿衣建议：

详细天气信息：
- 温度: {temperature}°C
- 天气状况: {description}
- 湿度: {humidity}%
- 风速: {wind_speed} m/s

请提供：
1. 适合的服装材质和类型
2. 分层穿衣建议（适合不同温度变化）
3. 配饰建议（帽子、围巾、手套等）
4. 特殊天气条件下的注意事项
5. 时尚搭配技巧"""
        else:
            query = f"请根据以下天气信息提供穿衣建议：\n\n{weather_data}"
        
        response = self.agent.run(query)
        return response


def main():
    """测试函数"""
    # 创建穿衣建议智能体
    fashion_agent = FashionAgent()
    
    # 测试数据
    test_weather = """🏙️ 城市: Shanghai
🌡️ 温度: 25°C
📝 天气: 晴朗
💧 湿度: 60%
🌬️ 风速: 3 m/s"""
    
    print("=== 穿衣建议智能体测试 ===")
    advice = fashion_agent.get_fashion_advice(test_weather)
    print(advice)


if __name__ == "__main__":
    main()