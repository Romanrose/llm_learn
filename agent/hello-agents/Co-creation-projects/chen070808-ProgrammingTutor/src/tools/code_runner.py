
import io
import contextlib
from hello_agents.tools import Tool
from typing import Dict, Any

class CodeRunner(Tool):
    """
    安全执行 Python 代码并返回输出的工具。
    警告：此工具使用 exec()，在生产环境中不安全。
    对于真实产品，请使用 Docker 等沙箱环境。
    """
    
    def __init__(self):
        super().__init__(
            name="code_runner",
            description="执行 Python 代码并返回标准输出/错误。输入应为包含 'code' 键的字典。"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "要执行的 Python 代码片段"
                }
            },
            "required": ["code"]
        }

    def run(self, parameters: Dict[str, Any]) -> str:
        code = parameters.get("code", "")
        if not code:
            return "错误：未提供代码。"

        # 捕获标准输出和标准错误
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                # 创建受限的全局作用域
                safe_globals = {
                    "__builtins__": __builtins__,
                    "print": print,
                    "range": range,
                    "len": len,
                    # 根据需要添加更多安全的内置函数
                }
                exec(code, safe_globals)
            
            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()
            
            result = ""
            if output:
                result += f"输出:\n{output}\n"
            if errors:
                result += f"错误:\n{errors}\n"
            
            if not result:
                result = "代码执行成功，无输出。"
                
            return result

        except Exception as e:
            return f"运行时错误: {str(e)}"
