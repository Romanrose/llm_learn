"""
分析服务
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.analysis import AnalysisDB, Analysis, AnalysisCreate, AnalysisUpdate
from ..core.exceptions import AnalysisNotFoundError
from ..services.paper_service import PaperService
import json

class AnalysisService:
    """分析服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.paper_service = PaperService(db)
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Analysis]:
        """根据ID获取分析"""
        analysis_db = self.db.query(AnalysisDB).filter(AnalysisDB.id == analysis_id).first()
        if not analysis_db:
            raise AnalysisNotFoundError(f"Analysis with id {analysis_id} not found")
        return Analysis.from_orm(analysis_db)
    
    def get_analyses_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Analysis]:
        """获取用户的分析列表"""
        analyses_db = self.db.query(AnalysisDB).filter(
            AnalysisDB.user_id == user_id
        ).order_by(AnalysisDB.created_at.desc()).offset(skip).limit(limit).all()
        return [Analysis.from_orm(analysis) for analysis in analyses_db]
    
    def create_analysis(self, analysis_create: AnalysisCreate, user_id: int, task_id: Optional[int] = None) -> Analysis:
        """创建分析"""
        analysis_db = AnalysisDB(
            title=analysis_create.title,
            analysis_type=analysis_create.analysis_type,
            paper_ids=json.dumps(analysis_create.paper_ids),
            methodology=analysis_create.methodology,
            user_id=user_id,
            task_id=task_id
        )
        
        self.db.add(analysis_db)
        self.db.commit()
        self.db.refresh(analysis_db)
        
        return Analysis.from_orm(analysis_db)
    
    def update_analysis(self, analysis_id: int, analysis_update: AnalysisUpdate) -> Analysis:
        """更新分析"""
        analysis_db = self.db.query(AnalysisDB).filter(AnalysisDB.id == analysis_id).first()
        if not analysis_db:
            raise AnalysisNotFoundError(f"Analysis with id {analysis_id} not found")
        
        # 更新字段
        update_data = analysis_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'findings':
                setattr(analysis_db, field, json.dumps(value))
            else:
                setattr(analysis_db, field, value)
        
        self.db.commit()
        self.db.refresh(analysis_db)
        
        return Analysis.from_orm(analysis_db)
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """删除分析"""
        analysis_db = self.db.query(AnalysisDB).filter(AnalysisDB.id == analysis_id).first()
        if not analysis_db:
            raise AnalysisNotFoundError(f"Analysis with id {analysis_id} not found")
        
        self.db.delete(analysis_db)
        self.db.commit()
        
        return True
    
    def get_analysis_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取分析统计信息"""
        total_analyses = self.db.query(AnalysisDB).filter(AnalysisDB.user_id == user_id).count()
        
        # 按类型统计
        type_stats = self.db.query(
            AnalysisDB.analysis_type,
            self.db.func.count(AnalysisDB.id)
        ).filter(AnalysisDB.user_id == user_id).group_by(AnalysisDB.analysis_type).all()
        
        # 平均分数
        avg_scores = self.db.query(
            self.db.func.avg(AnalysisDB.confidence_score),
            self.db.func.avg(AnalysisDB.novelty_score),
            self.db.func.avg(AnalysisDB.impact_score)
        ).filter(AnalysisDB.user_id == user_id).first()
        
        return {
            'total_analyses': total_analyses,
            'type_distribution': dict(type_stats),
            'average_confidence': float(avg_scores[0] or 0),
            'average_novelty': float(avg_scores[1] or 0),
            'average_impact': float(avg_scores[2] or 0)
        }
    
    def get_related_analyses(self, analysis_id: int, limit: int = 5) -> List[Analysis]:
        """获取相关分析"""
        analysis_db = self.db.query(AnalysisDB).filter(AnalysisDB.id == analysis_id).first()
        if not analysis_db:
            raise AnalysisNotFoundError(f"Analysis with id {analysis_id} not found")
        
        # 获取相同类型的分析
        related_analyses = self.db.query(AnalysisDB).filter(
            and_(
                AnalysisDB.user_id == analysis_db.user_id,
                AnalysisDB.analysis_type == analysis_db.analysis_type,
                AnalysisDB.id != analysis_id
            )
        ).order_by(AnalysisDB.created_at.desc()).limit(limit).all()
        
        return [Analysis.from_orm(analysis) for analysis in related_analyses]
    
    def export_analysis(self, analysis_id: int, format: str = "json") -> Dict[str, Any]:
        """导出分析结果"""
        analysis = self.get_analysis_by_id(analysis_id)
        
        if format == "json":
            return analysis.dict()
        elif format == "markdown":
            return self._export_to_markdown(analysis)
        elif format == "pdf":
            return self._export_to_pdf(analysis)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_markdown(self, analysis: Analysis) -> str:
        """导出为Markdown格式"""
        markdown = f"# {analysis.title}\n\n"
        markdown += f"**分析类型**: {analysis.analysis_type}\n\n"
        markdown += f"**创建时间**: {analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if analysis.methodology:
            markdown += f"## 方法论\n\n{analysis.methodology}\n\n"
        
        if analysis.findings:
            markdown += "## 主要发现\n\n"
            for key, value in analysis.findings.items():
                markdown += f"### {key}\n\n{value}\n\n"
        
        if analysis.insights:
            markdown += f"## 洞察\n\n{analysis.insights}\n\n"
        
        if analysis.limitations:
            markdown += f"## 局限性\n\n{analysis.limitations}\n\n"
        
        if analysis.recommendations:
            markdown += f"## 建议\n\n{analysis.recommendations}\n\n"
        
        # 添加评分
        markdown += "## 评分\n\n"
        markdown += f"- **置信度**: {analysis.confidence_score:.2f}\n"
        markdown += f"- **新颖性**: {analysis.novelty_score:.2f}\n"
        markdown += f"- **影响力**: {analysis.impact_score:.2f}\n"
        
        return markdown
    
    def _export_to_pdf(self, analysis: Analysis) -> bytes:
        """导出为PDF格式"""
        # 这里可以使用reportlab或其他PDF生成库
        # 暂时返回Markdown内容的字节
        markdown_content = self._export_to_markdown(analysis)
        return markdown_content.encode('utf-8')