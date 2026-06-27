"""
写作服务
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.writing import WritingDB, Writing, WritingCreate, WritingUpdate
from ..core.exceptions import WritingNotFoundError
from ..services.paper_service import PaperService
from ..utils.citation_formatter import CitationFormatter
import json
import re

class WritingService:
    """写作服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.paper_service = PaperService(db)
        self.citation_formatter = CitationFormatter()
    
    def get_writing_by_id(self, writing_id: int) -> Optional[Writing]:
        """根据ID获取写作"""
        writing_db = self.db.query(WritingDB).filter(WritingDB.id == writing_id).first()
        if not writing_db:
            raise WritingNotFoundError(f"Writing with id {writing_id} not found")
        return Writing.from_orm(writing_db)
    
    def get_writings_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Writing]:
        """获取用户的写作列表"""
        writings_db = self.db.query(WritingDB).filter(
            WritingDB.user_id == user_id
        ).order_by(WritingDB.created_at.desc()).offset(skip).limit(limit).all()
        return [Writing.from_orm(writing) for writing in writings_db]
    
    def create_writing(self, writing_create: WritingCreate, user_id: int, task_id: Optional[int] = None) -> Writing:
        """创建写作"""
        # 计算字数
        content = writing_create.content or ""
        word_count = len(re.findall(r'\S+', content))
        
        writing_db = WritingDB(
            title=writing_create.title,
            writing_type=writing_create.writing_type,
            content=content,
            outline=json.dumps(writing_create.outline or []),
            paper_ids=json.dumps(writing_create.paper_ids),
            word_count=word_count,
            user_id=user_id,
            task_id=task_id
        )
        
        self.db.add(writing_db)
        self.db.commit()
        self.db.refresh(writing_db)
        
        return Writing.from_orm(writing_db)
    
    def update_writing(self, writing_id: int, writing_update: WritingUpdate) -> Writing:
        """更新写作"""
        writing_db = self.db.query(WritingDB).filter(WritingDB.id == writing_id).first()
        if not writing_db:
            raise WritingNotFoundError(f"Writing with id {writing_id} not found")
        
        # 更新字段
        update_data = writing_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['outline', 'sections', 'citations', 'paper_ids']:
                setattr(writing_db, field, json.dumps(value))
            else:
                setattr(writing_db, field, value)
        
        # 重新计算字数
        if 'content' in update_data:
            writing_db.word_count = len(re.findall(r'\S+', writing_db.content or ""))
        
        self.db.commit()
        self.db.refresh(writing_db)
        
        return Writing.from_orm(writing_db)
    
    def delete_writing(self, writing_id: int) -> bool:
        """删除写作"""
        writing_db = self.db.query(WritingDB).filter(WritingDB.id == writing_id).first()
        if not writing_db:
            raise WritingNotFoundError(f"Writing with id {writing_id} not found")
        
        self.db.delete(writing_db)
        self.db.commit()
        
        return True
    
    def get_writing_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取写作统计信息"""
        total_writings = self.db.query(WritingDB).filter(WritingDB.user_id == user_id).count()
        
        # 按类型统计
        type_stats = self.db.query(
            WritingDB.writing_type,
            self.db.func.count(WritingDB.id)
        ).filter(WritingDB.user_id == user_id).group_by(WritingDB.writing_type).all()
        
        # 按状态统计
        status_stats = self.db.query(
            WritingDB.status,
            self.db.func.count(WritingDB.id)
        ).filter(WritingDB.user_id == user_id).group_by(WritingDB.status).all()
        
        # 总字数
        total_words = self.db.query(
            self.db.func.sum(WritingDB.word_count)
        ).filter(WritingDB.user_id == user_id).scalar() or 0
        
        # 平均质量分数
        avg_quality = self.db.query(
            self.db.func.avg(WritingDB.quality_score)
        ).filter(WritingDB.user_id == user_id).scalar() or 0
        
        return {
            'total_writings': total_writings,
            'total_words': int(total_words),
            'average_quality': float(avg_quality),
            'type_distribution': dict(type_stats),
            'status_distribution': dict(status_stats)
        }
    
    def format_citations(self, writing_id: int, style: str = "APA") -> Dict[str, Any]:
        """格式化引用"""
        writing = self.get_writing_by_id(writing_id)
        
        # 获取参考论文
        paper_ids = json.loads(writing.paper_ids or "[]")
        papers = []
        for paper_id in paper_ids:
            try:
                paper = self.paper_service.get_paper_by_id(paper_id)
                papers.append(paper)
            except Exception:
                continue
        
        # 格式化引用
        formatted_citations = self.citation_formatter.format_papers(papers, style)
        
        # 更新写作中的引用
        citations_data = [
            {
                'id': paper.id,
                'title': paper.title,
                'authors': paper.authors,
                'journal': paper.journal,
                'year': paper.publication_year,
                'formatted': formatted_citations.get(str(paper.id), "")
            }
            for paper in papers
        ]
        
        self.update_writing(writing_id, WritingUpdate(citations=citations_data))
        
        return {
            'citations': citations_data,
            'bibliography': self.citation_formatter.generate_bibliography(papers, style)
        }
    
    def export_writing(self, writing_id: int, format: str = "markdown", include_citations: bool = True) -> Dict[str, Any]:
        """导出写作"""
        writing = self.get_writing_by_id(writing_id)
        
        if format == "markdown":
            return self._export_to_markdown(writing, include_citations)
        elif format == "latex":
            return self._export_to_latex(writing, include_citations)
        elif format == "docx":
            return self._export_to_docx(writing, include_citations)
        elif format == "pdf":
            return self._export_to_pdf(writing, include_citations)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_markdown(self, writing: Writing, include_citations: bool = True) -> str:
        """导出为Markdown格式"""
        markdown = f"# {writing.title}\n\n"
        markdown += f"**类型**: {writing.writing_type}\n\n"
        markdown += f"**字数**: {writing.word_count}\n\n"
        markdown += f"**创建时间**: {writing.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if writing.content:
            markdown += f"{writing.content}\n\n"
        
        if include_citations and writing.citations:
            markdown += "## 参考文献\n\n"
            for citation in writing.citations:
                markdown += f"- {citation.get('formatted', '')}\n"
        
        return markdown
    
    def _export_to_latex(self, writing: Writing, include_citations: bool = True) -> str:
        """导出为LaTeX格式"""
        latex = "\\documentclass{article}\n"
        latex += "\\usepackage[utf8]{inputenc}\n"
        latex += "\\usepackage{cite}\n\n"
        latex += "\\begin{document}\n\n"
        latex += f"\\title{{{writing.title}}}\n"
        latex += "\\maketitle\n\n"
        
        if writing.content:
            # 简单的Markdown到LaTeX转换
            content = writing.content.replace("**", "\\textbf{").replace("**", "}")
            content = content.replace("*", "\\textit{").replace("*", "}")
            latex += f"{content}\n\n"
        
        if include_citations and writing.citations:
            latex += "\\bibliographystyle{plain}\n"
            latex += "\\bibliography{references}\n"
        
        latex += "\\end{document}"
        
        return latex
    
    def _export_to_docx(self, writing: Writing, include_citations: bool = True) -> bytes:
        """导出为Word文档格式"""
        # 这里可以使用python-docx库
        # 暂时返回Markdown内容的字节
        content = self._export_to_markdown(writing, include_citations)
        return content.encode('utf-8')
    
    def _export_to_pdf(self, writing: Writing, include_citations: bool = True) -> bytes:
        """导出为PDF格式"""
        # 这里可以使用reportlab或其他PDF生成库
        # 暂时返回Markdown内容的字节
        content = self._export_to_markdown(writing, include_citations)
        return content.encode('utf-8')
    
    def generate_outline(self, topic: str, paper_ids: List[int], writing_type: str = "review") -> List[Dict[str, Any]]:
        """生成写作大纲"""
        # 获取参考论文
        papers = []
        for paper_id in paper_ids:
            try:
                paper = self.paper_service.get_paper_by_id(paper_id)
                papers.append(paper)
            except Exception:
                continue
        
        # 根据写作类型生成大纲模板
        if writing_type == "review":
            outline = [
                {"title": "引言", "level": 1, "content": "研究背景和意义"},
                {"title": "文献综述", "level": 1, "content": "相关研究工作总结"},
                {"title": "方法论分析", "level": 1, "content": "研究方法比较"},
                {"title": "主要发现", "level": 1, "content": "研究成果总结"},
                {"title": "讨论与展望", "level": 1, "content": "研究局限性和未来方向"},
                {"title": "结论", "level": 1, "content": "研究总结"}
            ]
        elif writing_type == "summary":
            outline = [
                {"title": "研究背景", "level": 1, "content": "研究动机和目标"},
                {"title": "研究方法", "level": 1, "content": "实验设计和数据分析"},
                {"title": "主要结果", "level": 1, "content": "关键发现和数据分析"},
                {"title": "结论与意义", "level": 1, "content": "研究贡献和影响"}
            ]
        elif writing_type == "critique":
            outline = [
                {"title": "论文概述", "level": 1, "content": "研究内容总结"},
                {"title": "优点分析", "level": 1, "content": "研究的创新性和贡献"},
                {"title": "问题与局限", "level": 1, "content": "研究中存在的问题"},
                {"title": "改进建议", "level": 1, "content": "对研究的改进意见"}
            ]
        else:
            outline = [
                {"title": "研究背景", "level": 1, "content": ""},
                {"title": "研究目标", "level": 1, "content": ""},
                {"title": "研究方法", "level": 1, "content": ""},
                {"title": "预期结果", "level": 1, "content": ""},
                {"title": "研究意义", "level": 1, "content": ""}
            ]
        
        return outline