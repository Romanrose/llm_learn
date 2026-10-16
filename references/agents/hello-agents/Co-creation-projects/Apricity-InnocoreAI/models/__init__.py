"""
数据模型定义
"""

from .user import User
from .paper import Paper
from .task import Task
from .analysis import Analysis
from .writing import Writing

__all__ = ['User', 'Paper', 'Task', 'Analysis', 'Writing']