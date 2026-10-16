"""工具注册表 - HelloAgents原生工具系统"""

from typing import Optional, Any, Callable
import json
from .base import Tool

class ToolRegistry:
    """
    HelloAgents工具注册表

    提供工具的注册、管理和执行功能。
    支持两种工具注册方式：
    1. Tool对象注册（推荐）
    2. 函数直接注册（简便）
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool: Tool):
        """
        注册Tool对象

        Args:
            tool: Tool实例
        """
        if tool.name in self._tools:
            print(f"⚠️ 警告：工具 '{tool.name}' 已存在，将被覆盖。")

        self._tools[tool.name] = tool
        print(f"✅ 工具 '{tool.name}' 已注册。")

    def register_function(self, name: str, description: str, func: Callable[[str], str]):
        """
        直接注册函数作为工具（简便方式）

        Args:
            name: 工具名称
            description: 工具描述
            func: 工具函数，接受字符串参数，返回字符串结果
        """
        if name in self._functions:
            print(f"⚠️ 警告：工具 '{name}' 已存在，将被覆盖。")

        self._functions[name] = {
            "description": description,
            "func": func
        }
        print(f"✅ 工具 '{name}' 已注册。")

    def unregister(self, name: str):
        """注销工具"""
        if name in self._tools:
            del self._tools[name]
            print(f"🗑️ 工具 '{name}' 已注销。")
        elif name in self._functions:
            del self._functions[name]
            print(f"🗑️ 工具 '{name}' 已注销。")
        else:
            print(f"⚠️ 工具 '{name}' 不存在。")

    def get_tool(self, name: str) -> Optional[Tool]:
        """获取Tool对象"""
        return self._tools.get(name)

    def get_function(self, name: str) -> Optional[Callable]:
        """获取工具函数"""
        func_info = self._functions.get(name)
        return func_info["func"] if func_info else None

    def execute_tool(self, name: str, input_text: str) -> str:
        """
        执行工具

        Args:
            name: 工具名称
            input_text: 输入参数

        Returns:
            工具执行结果
        """
        # 优先查找Tool对象
        if name in self._tools:
            tool = self._tools[name]
            try:
                raw = (input_text or "").strip()
                
                # 预处理：如果输入包含换行和另一个 Action，只取第一行
                if '\n' in raw and 'Action:' in raw:
                    lines = raw.split('\n')
                    raw = lines[0].strip()

                # 1) JSON 直通：允许 ReAct 里用 tool[{"k":"v"}] 精确传参
                def _try_json(txt: str):
                    try:
                        return json.loads(txt)
                    except Exception:
                        return None

                obj = None
                # 1a 单个对象
                if raw.startswith("{") and raw.endswith("}"):
                    obj = _try_json(raw)
                # 1b 常见模型输出尾部多了一个 ']' 的容错
                if obj is None and raw.startswith("{") and raw.endswith("}]"):
                    obj = _try_json(raw[:-1].strip())
                # 1c 模型输出为数组包裹一个对象
                if obj is None and raw.startswith("[") and raw.endswith("]"):
                    arr = _try_json(raw)
                    if isinstance(arr, list) and len(arr) == 1 and isinstance(arr[0], dict):
                        obj = arr[0]
                # 1d 错位尾括号（常见：{"a":1,"b":2}])
                if obj is None and raw.endswith("}]") and raw.count("{") == 1 and raw.count("}") == 2:
                    obj = _try_json(raw[:-1])
                # 1e 正则兜底：提取首个完整 JSON 对象
                if obj is None and "{" in raw and "}" in raw:
                    try:
                        import re
                        # 使用括号匹配而非简单正则
                        def extract_first_json_object(text: str):
                            """从文本中提取第一个完整的 JSON 对象"""
                            start = text.find('{')
                            if start == -1:
                                return None
                            depth = 0
                            in_string = False
                            escape = False
                            for i, c in enumerate(text[start:], start):
                                if escape:
                                    escape = False
                                    continue
                                if c == '\\' and in_string:
                                    escape = True
                                    continue
                                if c == '"' and not escape:
                                    in_string = not in_string
                                    continue
                                if in_string:
                                    continue
                                if c == '{':
                                    depth += 1
                                elif c == '}':
                                    depth -= 1
                                    if depth == 0:
                                        return text[start:i+1]
                            return None
                        
                        json_str = extract_first_json_object(raw)
                        if json_str:
                            obj = json.loads(json_str)
                    except Exception:
                        pass

                if isinstance(obj, dict):
                    return tool.run(obj)

                # 2) 单参数兜底：如果工具只有一个必填参数，把 input_text 映射到该参数名
                params = tool.get_parameters()
                required = [p for p in params if p.required]
                if len(required) == 1:
                    return tool.run({required[0].name: input_text})

                # 3) 兼容旧行为：若存在 input 参数，使用 input
                if any(p.name == "input" for p in params):
                    return tool.run({"input": input_text})

                return (
                    f"错误：工具 '{name}' 需要结构化参数。"
                    "请使用 JSON 形式传参，例如：tool[{\"param\":\"value\"}]"
                )
            except Exception as e:
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"

        # 查找函数工具
        elif name in self._functions:
            func = self._functions[name]["func"]
            try:
                return func(input_text)
            except Exception as e:
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"

        else:
            return f"错误：未找到名为 '{name}' 的工具。"

    def get_tools_description(self) -> str:
        """
        获取所有可用工具的格式化描述字符串

        Returns:
            工具描述字符串，用于构建提示词
        """
        descriptions = []

        # Tool对象描述
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")

        # 函数工具描述
        for name, info in self._functions.items():
            descriptions.append(f"- {name}: {info['description']}")

        return "\n".join(descriptions) if descriptions else "暂无可用工具"

    def list_tools(self) -> list[str]:
        """列出所有工具名称"""
        return list(self._tools.keys()) + list(self._functions.keys())

    def get_all_tools(self) -> list[Tool]:
        """获取所有Tool对象"""
        return list(self._tools.values())

    def clear(self):
        """清空所有工具"""
        self._tools.clear()
        self._functions.clear()
        print("🧹 所有工具已清空。")

# 全局工具注册表
global_registry = ToolRegistry()
