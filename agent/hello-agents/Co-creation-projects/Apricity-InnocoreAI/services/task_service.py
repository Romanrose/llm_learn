"""
任务服务
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from ..core.database import get_db
from ..models.task import TaskDB, Task, TaskCreate, TaskUpdate
from ..core.exceptions import TaskNotFoundError
from ..agents.controller import AgentController
import json
import asyncio

class TaskService:
    """任务服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_controller = AgentController()
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        task_db = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if not task_db:
            raise TaskNotFoundError(f"Task with id {task_id} not found")
        return Task.from_orm(task_db)
    
    def get_tasks_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Task]:
        """获取用户的任务列表"""
        tasks_db = self.db.query(TaskDB).filter(
            TaskDB.user_id == user_id
        ).order_by(TaskDB.created_at.desc()).offset(skip).limit(limit).all()
        return [Task.from_orm(task) for task in tasks_db]
    
    def create_task(self, task_create: TaskCreate, user_id: int) -> Task:
        """创建任务"""
        task_db = TaskDB(
            title=task_create.title,
            description=task_create.description,
            task_type=task_create.task_type,
            priority=task_create.priority,
            parameters=task_create.parameters,
            user_id=user_id
        )
        
        self.db.add(task_db)
        self.db.commit()
        self.db.refresh(task_db)
        
        # 异步执行任务
        self._execute_task_async(task_db.id)
        
        return Task.from_orm(task_db)
    
    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task:
        """更新任务"""
        task_db = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if not task_db:
            raise TaskNotFoundError(f"Task with id {task_id} not found")
        
        # 更新字段
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task_db, field, value)
        
        # 如果任务完成，设置完成时间
        if task_update.status == "completed":
            task_db.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task_db)
        
        return Task.from_orm(task_db)
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        task_db = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if not task_db:
            raise TaskNotFoundError(f"Task with id {task_id} not found")
        
        self.db.delete(task_db)
        self.db.commit()
        
        return True
    
    def cancel_task(self, task_id: int) -> Task:
        """取消任务"""
        return self.update_task(task_id, TaskUpdate(status="failed", error_message="Task cancelled by user"))
    
    def retry_task(self, task_id: int) -> Task:
        """重试任务"""
        # 重置任务状态
        task = self.update_task(task_id, TaskUpdate(
            status="pending",
            progress=0,
            error_message=None
        ))
        
        # 重新执行任务
        self._execute_task_async(task_id)
        
        return task
    
    def get_task_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取任务统计信息"""
        total_tasks = self.db.query(TaskDB).filter(TaskDB.user_id == user_id).count()
        
        # 按状态统计
        status_stats = self.db.query(
            TaskDB.status,
            self.db.func.count(TaskDB.id)
        ).filter(TaskDB.user_id == user_id).group_by(TaskDB.status).all()
        
        # 按类型统计
        type_stats = self.db.query(
            TaskDB.task_type,
            self.db.func.count(TaskDB.id)
        ).filter(TaskDB.user_id == user_id).group_by(TaskDB.task_type).all()
        
        # 成功率
        completed_tasks = self.db.query(TaskDB).filter(
            and_(TaskDB.user_id == user_id, TaskDB.status == "completed")
        ).count()
        
        success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'success_rate': success_rate,
            'status_distribution': dict(status_stats),
            'type_distribution': dict(type_stats)
        }
    
    def _execute_task_async(self, task_id: int):
        """异步执行任务"""
        try:
            # 获取任务信息
            task_db = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
            if not task_db:
                return
            
            # 更新任务状态为运行中
            task_db.status = "running"
            task_db.progress = 0
            self.db.commit()
            
            # 根据任务类型执行相应的智能体
            if task_db.task_type == "literature_search":
                result = asyncio.run(self._execute_literature_search(task_db))
            elif task_db.task_type == "analysis":
                result = asyncio.run(self._execute_analysis(task_db))
            elif task_db.task_type == "writing":
                result = asyncio.run(self._execute_writing(task_db))
            else:
                raise ValueError(f"Unknown task type: {task_db.task_type}")
            
            # 更新任务结果
            task_db.status = "completed"
            task_db.progress = 100
            task_db.results = result
            task_db.completed_at = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            # 更新任务状态为失败
            task_db.status = "failed"
            task_db.error_message = str(e)
            self.db.commit()
    
    async def _execute_literature_search(self, task_db: TaskDB) -> Dict[str, Any]:
        """执行文献搜索任务"""
        parameters = task_db.parameters or {}
        query = parameters.get('query', '')
        max_papers = parameters.get('max_papers', 20)
        
        # 使用猎手智能体进行文献搜索
        hunter_agent = self.agent_controller.get_agent('hunter')
        
        # 更新进度
        await self._update_task_progress(task_db.id, 20)
        
        # 执行搜索
        search_results = await hunter_agent.search_papers(query, max_papers)
        
        # 更新进度
        await self._update_task_progress(task_db.id, 60)
        
        # 使用矿工智能体进行深度挖掘
        miner_agent = self.agent_controller.get_agent('miner')
        enriched_results = await miner_agent.enrich_papers(search_results)
        
        # 更新进度
        await self._update_task_progress(task_db.id, 90)
        
        # 保存论文到数据库
        paper_service = PaperService(self.db)
        saved_papers = []
        for paper_data in enriched_results:
            try:
                paper = paper_service.create_paper(
                    PaperCreate(**paper_data),
                    task_db.user_id
                )
                saved_papers.append(paper.dict())
            except Exception as e:
                print(f"Error saving paper: {e}")
        
        return {
            'query': query,
            'total_found': len(enriched_results),
            'papers_saved': len(saved_papers),
            'papers': saved_papers
        }
    
    async def _execute_analysis(self, task_db: TaskDB) -> Dict[str, Any]:
        """执行分析任务"""
        parameters = task_db.parameters or {}
        paper_ids = parameters.get('paper_ids', [])
        analysis_type = parameters.get('analysis_type', 'comprehensive')
        
        # 使用教练智能体进行分析
        coach_agent = self.agent_controller.get_agent('coach')
        
        # 更新进度
        await self._update_task_progress(task_db.id, 30)
        
        # 执行分析
        analysis_result = await coach_agent.analyze_papers(paper_ids, analysis_type)
        
        # 更新进度
        await self._update_task_progress(task_db.id, 80)
        
        # 保存分析结果
        analysis_service = AnalysisService(self.db)
        analysis = analysis_service.create_analysis(
            {
                'title': f"Analysis of {len(paper_ids)} papers",
                'analysis_type': analysis_type,
                'paper_ids': paper_ids,
                'methodology': analysis_result.get('methodology', ''),
                'findings': analysis_result.get('findings', {}),
                'insights': analysis_result.get('insights', ''),
                'limitations': analysis_result.get('limitations', ''),
                'recommendations': analysis_result.get('recommendations', ''),
                'confidence_score': analysis_result.get('confidence_score', 0.0),
                'novelty_score': analysis_result.get('novelty_score', 0.0),
                'impact_score': analysis_result.get('impact_score', 0.0)
            },
            task_db.user_id,
            task_db.id
        )
        
        return {
            'analysis_id': analysis.id,
            'analysis_type': analysis_type,
            'papers_analyzed': len(paper_ids),
            'result': analysis.dict()
        }
    
    async def _execute_writing(self, task_db: TaskDB) -> Dict[str, Any]:
        """执行写作任务"""
        parameters = task_db.parameters or {}
        paper_ids = parameters.get('paper_ids', [])
        writing_type = parameters.get('writing_type', 'review')
        outline = parameters.get('outline')
        
        # 使用教练智能体进行写作
        coach_agent = self.agent_controller.get_agent('coach')
        
        # 更新进度
        await self._update_task_progress(task_db.id, 25)
        
        # 生成内容
        writing_result = await coach_agent.generate_writing(paper_ids, writing_type, outline)
        
        # 更新进度
        await self._update_task_progress(task_db.id, 75)
        
        # 保存写作结果
        writing_service = WritingService(self.db)
        writing = writing_service.create_writing(
            {
                'title': writing_result.get('title', 'Generated Writing'),
                'writing_type': writing_type,
                'content': writing_result.get('content', ''),
                'outline': writing_result.get('outline', []),
                'sections': writing_result.get('sections', {}),
                'citations': writing_result.get('citations', []),
                'paper_ids': paper_ids
            },
            task_db.user_id,
            task_db.id
        )
        
        return {
            'writing_id': writing.id,
            'writing_type': writing_type,
            'papers_referenced': len(paper_ids),
            'word_count': writing.word_count,
            'result': writing.dict()
        }
    
    async def _update_task_progress(self, task_id: int, progress: int):
        """更新任务进度"""
        task_db = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if task_db:
            task_db.progress = progress
            self.db.commit()