"""
写作模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WritingDB(Base):
    """写作数据库模型"""
    __tablename__ = "writing"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    writing_type = Column(String(50), nullable=False)  # review, summary, critique, proposal
    content = Column(Text)
    outline = Column(JSON)  # 大纲结构
    sections = Column(JSON)  # 章节内容
    citations = Column(JSON)  # 引用信息
    metadata = Column(JSON)  # 额外元数据
    quality_score = Column(Float, default=0.0)
    word_count = Column(Integer, default=0)
    status = Column(String(20), default="draft")  # draft, reviewing, completed
    paper_ids = Column(JSON)  # 参考论文ID列表
    user_id = Column(Integer, index=True)
    task_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Writing(BaseModel):
    """写作响应模型"""
    id: int
    title: str
    writing_type: str
    content: Optional[str] = None
    outline: List[Dict[str, Any]] = []
    sections: Dict[str, str] = {}
    citations: List[Dict[str, Any]] = []
    quality_score: float = 0.0
    word_count: int = 0
    status: str = "draft"
    created_at: datetime
    
    class Config:
        from_attributes = True

class WritingCreate(BaseModel):
    """写作创建模型"""
    title: str = Field(..., min_length=1, max_length=200)
    writing_type: str = Field(..., regex=r'^(review|summary|critique|proposal)$')
    paper_ids: List[int] = []
    outline: Optional[List[Dict[str, Any]]] = None

class WritingUpdate(BaseModel):
    """写作更新模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    outline: Optional[List[Dict[str, Any]]] = None
    sections: Optional[Dict[str, str]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)

class LiteratureReview(BaseModel):
    """文献综述"""
    introduction: str
    methodology_review: str
    findings_synthesis: str
    discussion: str
    conclusion: str
    references: List[Dict[str, Any]]

class PaperSummary(BaseModel):
    """论文总结"""
    background: str
    methods: str
    results: str
    conclusions: str
    significance: str

class PaperCritique(BaseModel):
    """论文评述"""
    strengths: List[str]
    weaknesses: List[str]
    methodological_issues: List[str]
    interpretation_concerns: List[str]
    suggestions: List[str]

class ResearchProposal(BaseModel):
    """研究提案"""
    background: str
    problem_statement: str
    research_questions: List[str]
    methodology: str
    expected_outcomes: str
    significance: str
    timeline: str

class WritingSection(BaseModel):
    """写作章节"""
    title: str
    content: str
    subsections: List['WritingSection'] = []
    citations: List[str] = []

# 解决前向引用
WritingSection.model_rebuild()