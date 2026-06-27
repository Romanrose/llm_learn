"""
分析模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AnalysisDB(Base):
    """分析数据库模型"""
    __tablename__ = "analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    analysis_type = Column(String(50), nullable=False)
    paper_ids = Column(JSON)  # 分析的论文ID列表
    methodology = Column(Text)
    findings = Column(JSON)  # 分析发现
    insights = Column(Text)
    limitations = Column(Text)
    recommendations = Column(Text)
    confidence_score = Column(Float, default=0.0)
    novelty_score = Column(Float, default=0.0)
    impact_score = Column(Float, default=0.0)
    metadata = Column(JSON)
    user_id = Column(Integer, index=True)
    task_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Analysis(BaseModel):
    """分析响应模型"""
    id: int
    title: str
    analysis_type: str
    methodology: Optional[str] = None
    findings: Dict[str, Any] = {}
    insights: Optional[str] = None
    limitations: Optional[str] = None
    recommendations: Optional[str] = None
    confidence_score: float = 0.0
    novelty_score: float = 0.0
    impact_score: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisCreate(BaseModel):
    """分析创建模型"""
    title: str = Field(..., min_length=1, max_length=200)
    analysis_type: str = Field(..., regex=r'^(comprehensive|methodology|findings|gap|trend)$')
    paper_ids: List[int] = []
    methodology: Optional[str] = None

class AnalysisUpdate(BaseModel):
    """分析更新模型"""
    title: Optional[str] = None
    methodology: Optional[str] = None
    findings: Optional[Dict[str, Any]] = None
    insights: Optional[str] = None
    limitations: Optional[str] = None
    recommendations: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    novelty_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    impact_score: Optional[float] = Field(None, ge=0.0, le=1.0)

class ComprehensiveAnalysis(BaseModel):
    """综合分析结果"""
    summary: str
    key_findings: List[str]
    methodological_trends: List[str]
    research_gaps: List[str]
    future_directions: List[str]
    quality_assessment: Dict[str, float]
    citation_network: Dict[str, Any]

class MethodologyAnalysis(BaseModel):
    """方法论分析结果"""
    common_methods: List[str]
    method_comparison: Dict[str, Any]
    strengths_weaknesses: Dict[str, List[str]]
    best_practices: List[str]

class FindingsAnalysis(BaseModel):
    """研究发现分析"""
    consensus_points: List[str]
    controversial_points: List[str]
    emerging_patterns: List[str]
    evidence_strength: Dict[str, float]

class GapAnalysis(BaseModel):
    """研究缺口分析"""
    identified_gaps: List[str]
    gap_categories: Dict[str, List[str]]
    opportunity_areas: List[str]
    research_questions: List[str]

class TrendAnalysis(BaseModel):
    """趋势分析结果"""
    temporal_trends: Dict[str, Any]
    topic_evolution: List[str]
    emerging_topics: List[str]
    citation_trends: Dict[str, Any]