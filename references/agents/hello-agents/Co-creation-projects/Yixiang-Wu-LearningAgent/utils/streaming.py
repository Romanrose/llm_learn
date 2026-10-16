# utils/streaming.py
"""流式输出工具函数"""

import sys
from typing import List
from hello_agents import HelloAgentsLLM


def should_stream(streaming: bool = None) -> bool:
    """
    判断是否应该使用流式输出

    Args:
        streaming: 手动指定的流式输出设置（None = 自动检测）

    Returns:
        是否使用流式输出
    """
    if streaming is None:
        # 自动检测：交互式终端使用流式输出
        return sys.stdout.isatty()
    return streaming


def stream_response(llm: HelloAgentsLLM, messages: List[dict], silent: bool = False) -> str:
    """
    执行流式 LLM 调用并打印结果

    Args:
        llm: HelloAgentsLLM 实例
        messages: LLM 消息列表
        silent: 是否静默模式（不打印输出）

    Returns:
        完整的响应文本
    """
    full_response = ""
    previous_length = 0

    try:
        for chunk in llm.stream_invoke(messages):
            # chunk 是累积式的，只打印新增部分
            if len(chunk) > previous_length:
                new_content = chunk[previous_length:]
                if not silent:
                    print(new_content, end='', flush=True)
                previous_length = len(chunk)

            # 保存完整响应
            full_response = chunk

        if not silent:
            print()  # 换行

        return full_response

    except Exception as e:
        # 如果流式输出失败，降级到普通输出
        if not silent:
            print(f"\n[流式输出失败，使用普通输出: {e}]")
        return llm.invoke(messages)
