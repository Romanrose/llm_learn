"""
InnoCore AI 基础智能体类
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json
import logging

from core.config import get_config
from core.llm_adapter import get_llm_adapter
from core.exceptions import AgentException, TimeoutException

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """基础智能体抽象类"""
    
    def __init__(self, name: str, llm = None, 
                 max_steps: int = None, timeout: int = None):
        self.name = name
        self.config = get_config()
        self.llm = llm or get_llm_adapter()
        
        self.max_steps = max_steps or self.config.agent_max_steps
        self.timeout = timeout or self.config.agent_timeout
        
        self.history = []
        self.tools = {}
        self.state = "idle"
        self.created_at = datetime.now()
        
    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体任务"""
        pass
    
    def add_tool(self, tool_name: str, tool_func: Callable, description: str = ""):
        """添加工具"""
        self.tools[tool_name] = {
            "function": tool_func,
            "description": description
        }
    
    def get_tools_description(self) -> str:
        """获取工具描述"""
        if not self.tools:
            return "暂无可用工具"
        
        descriptions = []
        for name, tool_info in self.tools.items():
            descriptions.append(f"- {name}: {tool_info['description']}")
        
        return "\n".join(descriptions)
    
    async def call_tool(self, tool_name: str, tool_input: Any) -> Any:
        """调用工具"""
        if tool_name not in self.tools:
            raise AgentException(f"工具 '{tool_name}' 不存在")
        
        try:
            tool_func = self.tools[tool_name]["function"]
            if asyncio.iscoroutinefunction(tool_func):
                result = await asyncio.wait_for(
                    tool_func(tool_input), 
                    timeout=self.timeout
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(tool_func, tool_input),
                    timeout=self.timeout
                )
            
            self._add_to_history(f"Tool {tool_name} called with input: {tool_input}")
            self._add_to_history(f"Tool {tool_name} result: {result}")
            
            return result
            
        except asyncio.TimeoutError:
            raise TimeoutException(f"工具 '{tool_name}' 执行超时")
        except Exception as e:
            raise AgentException(f"工具 '{tool_name}' 执行失败: {str(e)}")
    
    async def think(self, prompt: str, context: Dict = None) -> str:
        """调用LLM进行思考"""
        try:
            # 构建完整的提示词
            full_prompt = prompt
            
            # 添加上下文信息
            if context:
                context_str = json.dumps(context, ensure_ascii=False, indent=2)
                full_prompt = f"上下文信息:\n{context_str}\n\n任务:\n{prompt}"
            
            # 添加历史记录
            if self.history:
                history_str = "\n".join(self.history[-10:])  # 只保留最近10条
                full_prompt += f"\n\n历史记录:\n{history_str}"
            
            # 调用 HelloAgent LLM
            response = await asyncio.wait_for(
                self.llm.ainvoke(full_prompt),
                timeout=self.timeout
            )
            
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            self._add_to_history(f"LLM prompt: {prompt}")
            self._add_to_history(f"LLM response: {response_text}")
            
            return response_text
            
        except asyncio.TimeoutError:
            raise TimeoutException("LLM思考超时")
        except Exception as e:
            raise AgentException(f"LLM思考失败: {str(e)}")
    
    def _add_to_history(self, message: str):
        """添加到历史记录"""
        timestamp = datetime.now().isoformat()
        self.history.append(f"[{timestamp}] {message}")
        
        # 限制历史记录长度
        if len(self.history) > 100:
            self.history = self.history[-50:]
    
    def get_history(self, limit: int = 10) -> List[str]:
        """获取历史记录"""
        return self.history[-limit:]
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
    
    def set_state(self, state: str):
        """设置智能体状态"""
        self.state = state
        logger.info(f"Agent {self.name} state changed to: {state}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "name": self.name,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "history_count": len(self.history),
            "tools_count": len(self.tools),
            "max_steps": self.max_steps,
            "timeout": self.timeout
        }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = self.get_required_fields()
        
        for field in required_fields:
            if field not in input_data:
                raise AgentException(f"缺少必需字段: {field}")
        
        return True
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """获取必需的输入字段"""
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', state='{self.state}')"
    
    def __repr__(self) -> str:
        return self.__str__()