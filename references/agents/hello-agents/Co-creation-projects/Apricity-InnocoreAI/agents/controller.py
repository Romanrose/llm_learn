"""
InnoCore AI 智能体控制器
负责四大智能体的协同调度和任务编排
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json
import logging
from enum import Enum

from agents.base import BaseAgent
from agents.hunter import HunterAgent
from agents.miner import MinerAgent
from agents.coach import CoachAgent
from agents.validator import ValidatorAgent
from core.config import get_config
from core.exceptions import AgentException, TimeoutException

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """任务类型枚举"""
    PAPER_HUNTING = "paper_hunting"
    PAPER_ANALYSIS = "paper_analysis"
    WRITING_ASSISTANCE = "writing_assistance"
    CITATION_VALIDATION = "citation_validation"
    FULL_WORKFLOW = "full_workflow"

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentController:
    """智能体控制器"""
    
    def __init__(self):
        self.config = get_config()
        
        # 初始化智能体
        self.agents = {
            "hunter": HunterAgent(),
            "miner": MinerAgent(),
            "coach": CoachAgent(),
            "validator": ValidatorAgent()
        }
        
        # 任务管理
        self.active_tasks = {}
        self.task_history = []
        self.task_queue = asyncio.Queue()
        
        # 并发控制
        self.semaphore = asyncio.Semaphore(self.config.concurrent_agents)
        
        # 事件回调
        self.event_callbacks = {
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
            "agent_status_changed": []
        }
    
    async def initialize(self):
        """初始化控制器"""
        logger.info("初始化Agent Controller...")
        
        # 这里可以添加智能体的初始化逻辑
        # 例如加载模型、建立连接等
        
        logger.info("Agent Controller初始化完成")
    
    async def submit_task(self, task_type: TaskType, input_data: Dict[str, Any], 
                         priority: int = 0, callback: Callable = None) -> str:
        """提交任务"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_tasks)}"
        
        task = {
            "id": task_id,
            "type": task_type,
            "input_data": input_data,
            "status": TaskStatus.PENDING,
            "priority": priority,
            "callback": callback,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "agent_results": {}
        }
        
        self.active_tasks[task_id] = task
        await self.task_queue.put((priority, task))
        
        logger.info(f"任务已提交: {task_id}, 类型: {task_type.value}")
        return task_id
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """执行单个任务"""
        if task_id not in self.active_tasks:
            raise AgentException(f"任务不存在: {task_id}")
        
        task = self.active_tasks[task_id]
        
        async with self.semaphore:  # 并发控制
            try:
                task["status"] = TaskStatus.RUNNING
                task["started_at"] = datetime.now()
                
                await self._trigger_event("task_started", task)
                
                # 根据任务类型执行相应的逻辑
                if task["type"] == TaskType.PAPER_HUNTING:
                    result = await self._execute_paper_hunting(task)
                elif task["type"] == TaskType.PAPER_ANALYSIS:
                    result = await self._execute_paper_analysis(task)
                elif task["type"] == TaskType.WRITING_ASSISTANCE:
                    result = await self._execute_writing_assistance(task)
                elif task["type"] == TaskType.CITATION_VALIDATION:
                    result = await self._execute_citation_validation(task)
                elif task["type"] == TaskType.FULL_WORKFLOW:
                    result = await self._execute_full_workflow(task)
                else:
                    raise AgentException(f"不支持的任务类型: {task['type']}")
                
                task["status"] = TaskStatus.COMPLETED
                task["completed_at"] = datetime.now()
                task["result"] = result
                
                await self._trigger_event("task_completed", task)
                
                # 执行回调
                if task["callback"]:
                    await task["callback"](task)
                
                return result
                
            except Exception as e:
                task["status"] = TaskStatus.FAILED
                task["completed_at"] = datetime.now()
                task["error"] = str(e)
                
                await self._trigger_event("task_failed", task)
                
                logger.error(f"任务执行失败 {task_id}: {str(e)}")
                raise AgentException(f"任务执行失败: {str(e)}")
            
            finally:
                # 移动到历史记录
                self.task_history.append(task.copy())
                del self.active_tasks[task_id]
    
    async def _execute_paper_hunting(self, task: Dict) -> Dict[str, Any]:
        """执行论文抓取任务"""
        input_data = task["input_data"]
        
        # 调用Hunter Agent
        hunter_result = await self.agents["hunter"].run(input_data)
        task["agent_results"]["hunter"] = hunter_result
        
        return {
            "task_type": "paper_hunting",
            "papers_found": hunter_result.get("downloaded_papers", []),
            "statistics": {
                "total_found": hunter_result.get("total_found", 0),
                "downloaded": hunter_result.get("downloaded_papers", 0)
            }
        }
    
    async def _execute_paper_analysis(self, task: Dict) -> Dict[str, Any]:
        """执行论文分析任务"""
        input_data = task["input_data"]
        
        # 调用Miner Agent
        miner_result = await self.agents["miner"].run(input_data)
        task["agent_results"]["miner"] = miner_result
        
        return {
            "task_type": "paper_analysis",
            "analysis_report": miner_result,
            "paper_id": input_data.get("paper_id")
        }
    
    async def _execute_writing_assistance(self, task: Dict) -> Dict[str, Any]:
        """执行写作辅助任务"""
        input_data = task["input_data"]
        
        # 调用Coach Agent
        coach_result = await self.agents["coach"].run(input_data)
        task["agent_results"]["coach"] = coach_result
        
        return {
            "task_type": "writing_assistance",
            "assistance_result": coach_result,
            "user_id": input_data.get("user_id")
        }
    
    async def _execute_citation_validation(self, task: Dict) -> Dict[str, Any]:
        """执行引用校验任务"""
        input_data = task["input_data"]
        
        # 调用Validator Agent
        validator_result = await self.agents["validator"].run(input_data)
        task["agent_results"]["validator"] = validator_result
        
        return {
            "task_type": "citation_validation",
            "validation_result": validator_result,
            "paper_info": input_data.get("paper_info")
        }
    
    async def _execute_full_workflow(self, task: Dict) -> Dict[str, Any]:
        """执行完整工作流"""
        input_data = task["input_data"]
        user_id = input_data.get("user_id")
        keywords = input_data.get("keywords", [])
        
        workflow_result = {
            "task_type": "full_workflow",
            "stages": {},
            "final_papers": [],
            "analysis_reports": []
        }
        
        try:
            # Stage 1: 论文抓取
            self._add_to_history("开始论文抓取阶段")
            hunting_input = {
                "keywords": keywords,
                "max_papers": input_data.get("max_papers", 10),
                "sources": input_data.get("sources", ["arxiv"])
            }
            
            hunting_result = await self.agents["hunter"].run(hunting_input)
            workflow_result["stages"]["hunting"] = hunting_result
            task["agent_results"]["hunter"] = hunting_result
            
            downloaded_papers = hunting_result.get("papers", [])
            workflow_result["final_papers"] = downloaded_papers
            
            # Stage 2: 论文分析
            self._add_to_history("开始论文分析阶段")
            for paper in downloaded_papers:
                if paper.get("db_id"):
                    analysis_input = {
                        "paper_id": paper["db_id"],
                        "user_id": user_id,
                        "analysis_type": "full"
                    }
                    
                    try:
                        analysis_result = await self.agents["miner"].run(analysis_input)
                        workflow_result["analysis_reports"].append(analysis_result)
                    except Exception as e:
                        self._add_to_history(f"论文分析失败 {paper.get('title', 'Unknown')}: {str(e)}")
            
            # Stage 3: 引用校验（可选）
            if input_data.get("validate_citations", False):
                self._add_to_history("开始引用校验阶段")
                for paper in downloaded_papers:
                    paper_info = {
                        "title": paper.get("title", ""),
                        "authors": paper.get("authors", []),
                        "doi": paper.get("doi", ""),
                        "year": datetime.now().year
                    }
                    
                    validation_input = {
                        "paper_info": paper_info,
                        "formats": ["bibtex", "apa"],
                        "verify_external": True
                    }
                    
                    try:
                        validation_result = await self.agents["validator"].run(validation_input)
                        paper["citations"] = validation_result.get("citations", {})
                    except Exception as e:
                        self._add_to_history(f"引用校验失败 {paper.get('title', 'Unknown')}: {str(e)}")
            
            self._add_to_history("完整工作流执行完成")
            
        except Exception as e:
            self._add_to_history(f"工作流执行失败: {str(e)}")
            raise
        
        return workflow_result
    
    async def start_task_processor(self):
        """启动任务处理器"""
        logger.info("启动任务处理器...")
        
        while True:
            try:
                # 获取任务（按优先级排序）
                priority, task = await self.task_queue.get()
                
                # 异步执行任务
                asyncio.create_task(self.execute_task(task["id"]))
                
            except Exception as e:
                logger.error(f"任务处理器异常: {str(e)}")
                await asyncio.sleep(1)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "id": task["id"],
                "type": task["type"].value,
                "status": task["status"].value,
                "created_at": task["created_at"].isoformat(),
                "started_at": task["started_at"].isoformat() if task["started_at"] else None,
                "completed_at": task["completed_at"].isoformat() if task["completed_at"] else None,
                "priority": task["priority"]
            }
        else:
            # 在历史记录中查找
            for task in self.task_history:
                if task["id"] == task_id:
                    return {
                        "id": task["id"],
                        "type": task["type"].value,
                        "status": task["status"].value,
                        "created_at": task["created_at"].isoformat(),
                        "started_at": task["started_at"].isoformat() if task["started_at"] else None,
                        "completed_at": task["completed_at"].isoformat() if task["completed_at"] else None,
                        "priority": task["priority"]
                    }
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task["status"] == TaskStatus.PENDING:
                task["status"] = TaskStatus.CANCELLED
                task["completed_at"] = datetime.now()
                
                # 移动到历史记录
                self.task_history.append(task.copy())
                del self.active_tasks[task_id]
                
                logger.info(f"任务已取消: {task_id}")
                return True
        
        return False
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """获取所有智能体状态"""
        agent_status = {}
        for name, agent in self.agents.items():
            agent_status[name] = agent.get_status()
        
        return {
            "agents": agent_status,
            "active_tasks": len(self.active_tasks),
            "queued_tasks": self.task_queue.qsize(),
            "completed_tasks": len(self.task_history),
            "max_concurrent": self.config.concurrent_agents
        }
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """添加事件回调"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    async def _trigger_event(self, event_type: str, data: Any):
        """触发事件"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"事件回调执行失败 {event_type}: {str(e)}")
    
    def _add_to_history(self, message: str):
        """添加到控制器历史记录"""
        timestamp = datetime.now().isoformat()
        logger.info(f"[{timestamp}] Controller: {message}")
    
    async def shutdown(self):
        """关闭控制器"""
        logger.info("关闭Agent Controller...")
        
        # 取消所有待处理任务
        for task_id in list(self.active_tasks.keys()):
            await self.cancel_task(task_id)
        
        # 清理智能体资源
        for agent in self.agents.values():
            if hasattr(agent, 'close'):
                await agent.close()
        
        logger.info("Agent Controller已关闭")

# 全局控制器实例
agent_controller = AgentController()