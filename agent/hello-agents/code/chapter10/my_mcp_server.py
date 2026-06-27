"""
自定义MCP服务器示例

这是一个简单的MCP服务器，提供基础的数学计算和文本处理工具。
用于演示如何创建自己的MCP服务器。

运行方式：
    python my_mcp_server.py

或者作为MCP服务器被客户端调用：
    MCPClient(["python", "my_mcp_server.py"])
"""

from fastmcp import FastMCP
import sys
import os

# 创建MCP服务器实例
mcp = FastMCP("MyCustomServer")


# ==================== 数学工具 ====================

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    加法计算器
    
    Args:
        a: 第一个数字
        b: 第二个数字
    
    Returns:
        两数之和
    """
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """
    减法计算器
    
    Args:
        a: 被减数
        b: 减数
    
    Returns:
        两数之差
    """
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    乘法计算器
    
    Args:
        a: 第一个数字
        b: 第二个数字
    
    Returns:
        两数之积
    """
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    除法计算器
    
    Args:
        a: 被除数
        b: 除数
    
    Returns:
        两数之商
    
    Raises:
        ValueError: 当除数为0时
    """
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


# ==================== 文本处理工具 ====================

@mcp.tool()
def reverse_text(text: str) -> str:
    """
    反转文本
    
    Args:
        text: 要反转的文本
    
    Returns:
        反转后的文本
    """
    return text[::-1]


@mcp.tool()
def count_words(text: str) -> int:
    """
    统计文本中的单词数量
    
    Args:
        text: 要统计的文本
    
    Returns:
        单词数量
    """
    return len(text.split())


@mcp.tool()
def to_uppercase(text: str) -> str:
    """
    将文本转换为大写
    
    Args:
        text: 要转换的文本
    
    Returns:
        大写文本
    """
    return text.upper()


@mcp.tool()
def to_lowercase(text: str) -> str:
    """
    将文本转换为小写
    
    Args:
        text: 要转换的文本
    
    Returns:
        小写文本
    """
    return text.lower()


# ==================== 资源定义 ====================

@mcp.resource("config://server")
def get_server_config() -> str:
    """
    获取服务器配置信息
    
    Returns:
        服务器配置的JSON字符串
    """
    import json
    config = {
        "name": "MyCustomServer",
        "version": "1.0.0",
        "tools_count": 8,
        "description": "自定义MCP服务器示例"
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


@mcp.resource("info://capabilities")
def get_capabilities() -> str:
    """
    获取服务器能力列表
    
    Returns:
        能力列表的文本描述
    """
    capabilities = """
服务器能力列表：

数学计算：
- add: 加法计算
- subtract: 减法计算
- multiply: 乘法计算
- divide: 除法计算

文本处理：
- reverse_text: 反转文本
- count_words: 统计单词数
- to_uppercase: 转换为大写
- to_lowercase: 转换为小写

资源：
- config://server: 服务器配置
- info://capabilities: 能力列表（本资源）
"""
    return capabilities.strip()


# ==================== 提示词模板 ====================

@mcp.prompt()
def math_helper() -> str:
    """
    数学计算助手提示词
    
    Returns:
        提示词模板
    """
    return """你是一个数学计算助手。你可以使用以下工具：
- add(a, b): 计算两数之和
- subtract(a, b): 计算两数之差
- multiply(a, b): 计算两数之积
- divide(a, b): 计算两数之商

请根据用户的问题选择合适的工具进行计算。"""


@mcp.prompt()
def text_processor() -> str:
    """
    文本处理助手提示词
    
    Returns:
        提示词模板
    """
    return """你是一个文本处理助手。你可以使用以下工具：
- reverse_text(text): 反转文本
- count_words(text): 统计单词数
- to_uppercase(text): 转换为大写
- to_lowercase(text): 转换为小写

请根据用户的需求选择合适的工具处理文本。"""


# ==================== 主程序 ====================

if __name__ == "__main__":
    # 运行MCP服务器
    # FastMCP会自动处理stdio传输
    mcp.run()

