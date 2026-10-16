"""
LLM 适配器 - 基于 HelloAgent 框架
"""

import logging
from typing import Dict, Any, Optional
from core.config import get_config

logger = logging.getLogger(__name__)

class LLMAdapter:
    """LLM 适配器，基于 HelloAgent 框架"""
    
    def __init__(self):
        """初始化 LLM 适配器"""
        self.config = get_config()
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """初始化 HelloAgent LLM"""
        try:
            from hello_agents import HelloAgentsLLM
            
            # 根据文档，HelloAgentsLLM 的初始化参数
            self.llm = HelloAgentsLLM(
                model=self.config.llm.model_name,
                api_key=self.config.llm.api_key,
                base_url=self.config.llm.base_url,
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens,
                timeout=self.config.llm.timeout
            )
            logger.info(f"HelloAgent LLM 初始化成功: {self.config.llm.model_name}")
        except ImportError as e:
            logger.error(f"hello-agents 未安装: {str(e)}")
            raise ImportError("请安装 hello-agents: pip install 'hello-agents[all]>=0.2.7'")
        except Exception as e:
            logger.error(f"HelloAgent LLM 初始化失败: {str(e)}")
            raise
    
    def _format_messages(self, prompt: str) -> list:
        """
        将提示词格式化为消息列表
        
        Args:
            prompt: 提示词字符串
            
        Returns:
            消息列表，格式为 [{"role": "user", "content": "..."}]
        """
        if isinstance(prompt, str):
            return [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list):
            return prompt
        else:
            return [{"role": "user", "content": str(prompt)}]
    
    async def ainvoke(self, prompt: str, **kwargs) -> str:
        """
        异步调用 LLM
        
        Args:
            prompt: 提示词（字符串或消息列表）
            **kwargs: 额外参数
            
        Returns:
            LLM 响应文本
        """
        try:
            # 格式化消息
            messages = self._format_messages(prompt)
            
            # HelloAgent 使用同步 invoke，在异步上下文中调用
            import asyncio
            response = await asyncio.to_thread(self.llm.invoke, messages, **kwargs)
            
            # 提取文本内容
            if isinstance(response, str):
                return response
            elif hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
        except Exception as e:
            logger.error(f"LLM 异步调用失败: {str(e)}")
            raise
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """
        同步调用 LLM
        
        Args:
            prompt: 提示词（字符串或消息列表）
            **kwargs: 额外参数
            
        Returns:
            LLM 响应文本
        """
        try:
            # 格式化消息
            messages = self._format_messages(prompt)
            
            # HelloAgent 的同步调用
            response = self.llm.invoke(messages, **kwargs)
            
            # 提取文本内容
            if isinstance(response, str):
                return response
            elif hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
        except Exception as e:
            logger.error(f"LLM 同步调用失败: {str(e)}")
            raise

# 全局 LLM 适配器实例
_llm_adapter = None

def get_llm_adapter() -> LLMAdapter:
    """获取全局 LLM 适配器实例"""
    global _llm_adapter
    if _llm_adapter is None:
        _llm_adapter = LLMAdapter()
    return _llm_adapter
