from hello_agents import HelloAgentsLLM, SimpleAgent, ToolRegistry
import os
import sys
from pathlib import Path

# 添加项目根目录到路径，以便导入其他模块
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.tools.browser_tool import BrowserTool
from src.tools.terminal_tool import TerminalTool
from src.agents.config import (TERMINAL_SECURITY_MODE, AGENT_NAME, AGENT_SYSTEM_PROMPT_TEMPLATE)

class UniversalAgent(SimpleAgent):
    def __init__(self):
        # 从环境变量读取 LLM 配置
        llm = HelloAgentsLLM(
            provider=os.getenv('LLM_PROVIDER', 'modelscope'),
            model=os.getenv('LLM_MODEL', 'Qwen/Qwen3-VL-8B-Instruct'),
            api_key=os.getenv('LLM_API_KEY'),
            base_url=os.getenv('LLM_API_BASE')
        )
        
        # 创建工具注册表并注册工具
        tool_registry = ToolRegistry()
        tool_registry.register_tool(BrowserTool())
        tool_registry.register_tool(TerminalTool(security_mode=TERMINAL_SECURITY_MODE))
        
        # 将工具注册表传递给父类
        super().__init__(
            name=AGENT_NAME,
            llm=llm,
            system_prompt=AGENT_SYSTEM_PROMPT_TEMPLATE,
            tool_registry=tool_registry
        )
        
        # 存储会话上下文
        self.current_session_context = []
        self.last_query = None
        self.last_response = None
    
    def run(self, input_text: str, **kwargs) -> str:
        """运行Agent处理用户输入"""
        
        # 调用父类方法
        response = super().run(input_text, **kwargs)
        
        # 更新会话状态
        self.last_query = input_text
        self.last_response = response
        
        return response
