"""
自定义MCP服务器示例

这是一个简单的MCP服务器，提供天气信息查询。
用于演示如何创建自己的MCP服务器。

运行方式：
    python my_mcp_server.py

或者作为MCP服务器被客户端调用：
    MCPClient(["python", "weather_mcp.py"])
"""
from fastmcp import FastMCP
from weather import Weather
# 创建MCP服务器实例
mcp = FastMCP("WeatherServer")


# ==================== 数学工具 ====================

@mcp.tool()
def query_wearher(city_name: str):
    """
    查询天气

    Args:
        city_name: 城市名称

    Returns:
        天气信息
    """
    weather = Weather()
    # 查询天气详细信息（字典格式）
    weather_details = weather.get_weather_details(city_name)
    
    # 如果查询成功，返回详细信息
    if "error" not in weather_details:
        return weather_details
    else:
        # 如果查询失败，返回格式化字符串
        return weather.get_weather(city_name)

@mcp.tool()
def get_weather_details(city_name: str):
    """
    获取详细的天气数据（结构化格式）

    Args:
        city_name: 城市名称

    Returns:
        包含详细天气数据的字典
    """
    weather = Weather()
    return weather.get_weather_details(city_name)

@mcp.resource("info://capabilities")
def get_capabilities() -> str:
    """
    获取指定城市的天气信息

    Returns:
        能力列表的文本描述
    """
    capabilities = """
服务器能力列表：

天气查询能力：
- query_weather: 获取指定城市的天气信息（结构化数据）
- get_weather_details: 获取详细的天气数据（字典格式）
"""
    return capabilities.strip()


# ==================== 提示词模板 ====================

@mcp.prompt()
def weather_helper() -> str:
    """
    天气信息查询提示词

    Returns:
        提示词模板
    """
    return """你是一个天气查询助手。你可以使用以下工具：
- query_weather(city_name): 获取指定城市的天气信息

请根据用户的问题选择合适的工具进行任务执行。"""



# ==================== 主程序 ====================

if __name__ == "__main__":
    # 运行MCP服务器
    # FastMCP会自动处理stdio传输
    mcp.run()