"""数据模型定义"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ContentLevel(Enum):
    """内容层级"""
    TOPIC = 1      # 子话题层级
    SECTION = 2    # 小节层级
    DETAIL = 3     # 细节层级


@dataclass
class ContentNode:
    """内容树节点"""
    id: str                                    # 节点唯一标识
    title: str                                 # 节点标题
    level: ContentLevel                        # 内容层级
    description: str                           # 节点描述
    content: Optional[str] = None              # 实际内容（markdown）
    children: List['ContentNode'] = field(default_factory=list)  # 子节点列表
    metadata: Dict[str, Any] = field(default_factory=dict)       # 元数据
    revision_history: List[Dict[str, Any]] = field(default_factory=list)  # 修改历史
    
    def add_child(self, child: 'ContentNode'):
        """添加子节点"""
        self.children.append(child)
    
    def get_all_nodes(self) -> List['ContentNode']:
        """获取所有节点（深度优先）"""
        nodes = [self]
        for child in self.children:
            nodes.extend(child.get_all_nodes())
        return nodes
    
    def count_words(self) -> int:
        """统计节点及其子节点的总字数"""
        total = len(self.content) if self.content else 0
        for child in self.children:
            total += child.count_words()
        return total


@dataclass  
class ReviewResult:
    """评审结果"""
    score: int                                 # 总分 (0-100)
    grade: str                                 # 评级（优秀/良好/需改进/不合格）
    dimension_scores: Dict[str, int]           # 各维度得分
    detailed_feedback: Dict[str, Any]          # 详细反馈
    revision_plan: Dict[str, Any]              # 修改计划
    needs_revision: bool                       # 是否需要修改
    estimated_effort: str = ""                 # 预估修改工作量
    reviewer_notes: str = ""                   # 评审者备注
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReviewResult':
        """从字典创建评审结果"""
        return cls(
            score=data.get('score', 0),
            grade=data.get('grade', '未知'),
            dimension_scores=data.get('dimension_scores', {}),
            detailed_feedback=data.get('detailed_feedback', {}),
            revision_plan=data.get('revision_plan', {}),
            needs_revision=data.get('needs_revision', False),
            estimated_effort=data.get('estimated_revision_effort', ''),
            reviewer_notes=data.get('reviewer_notes', '')
        )


@dataclass
class ColumnPlan:
    """专栏规划"""
    column_title: str                          # 专栏标题
    column_description: str                    # 专栏描述
    target_audience: str                       # 目标读者
    topics: List[Dict[str, Any]]               # 子话题列表
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ColumnPlan':
        """从字典创建专栏规划"""
        return cls(
            column_title=data.get('column_title', ''),
            column_description=data.get('column_description', ''),
            target_audience=data.get('target_audience', ''),
            topics=data.get('topics', [])
        )
    
    def get_topic_count(self) -> int:
        """获取话题数量"""
        return len(self.topics)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于缓存）"""
        return {
            'column_title': self.column_title,
            'column_description': self.column_description,
            'target_audience': self.target_audience,
            'topics': self.topics
        }

