# core/file_manager.py
"""文件管理器 - 统一管理 ~/.learningAgent/ 下的所有文件操作"""

from pathlib import Path
from datetime import datetime
from typing import List
from utils.exceptions import FileReadError, FileWriteError


class FileManager:
    """
    统一管理 ~/.learningAgent/ 下的所有文件操作

    Attributes:
        BASE_DIR: 基础目录路径
    """

    BASE_DIR = Path.home() / ".learningAgent"

    def __init__(self):
        """初始化文件管理器，确保基础目录存在"""
        self.ensure_structure()

    def ensure_structure(self) -> None:
        """确保基础目录结构存在"""
        self.BASE_DIR.mkdir(exist_ok=True)

    def create_domain(self, domain: str) -> None:
        """
        创建新的学习领域目录

        Args:
            domain: 领域名称
        """
        domain_path = self.BASE_DIR / domain
        domain_path.mkdir(exist_ok=True)
        (domain_path / "knowledge").mkdir(exist_ok=True)
        (domain_path / "sessions").mkdir(exist_ok=True)

        # 创建空的 summary 文件
        (domain_path / "knowledge" / "knowledge_summary.md").write_text(
            "# 知识总结\n\n> 暂无知识笔记\n", encoding="utf-8"
        )
        (domain_path / "sessions" / "session_summary.md").write_text(
            "# 学习历程\n\n> 暂无学习记录\n", encoding="utf-8"
        )

    def save_plan(self, domain: str, plan_content: str) -> None:
        """
        保存学习计划

        Args:
            domain: 领域名称
            plan_content: 计划内容（markdown格式）
        """
        plan_path = self.BASE_DIR / domain / "plan.md"
        try:
            plan_path.write_text(plan_content, encoding="utf-8")
        except Exception as e:
            raise FileWriteError(f"无法保存学习计划：{e}")

    def save_knowledge(self, domain: str, filename: str, content: str) -> None:
        """
        保存知识笔记

        Args:
            domain: 领域名称
            filename: 文件名
            content: 文件内容
        """
        knowledge_path = self.BASE_DIR / domain / "knowledge" / filename
        try:
            knowledge_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise FileWriteError(f"无法保存知识笔记：{e}")

    def save_session(self, domain: str, session_content: str) -> Path:
        """
        保存单次学习会话记录

        Args:
            domain: 领域名称
            session_content: 会话内容

        Returns:
            保存的文件路径
        """
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H-%M")
        session_path = self.BASE_DIR / domain / "sessions" / f"session_{date}_{time}.md"

        try:
            session_path.write_text(session_content, encoding="utf-8")
        except Exception as e:
            raise FileWriteError(f"无法保存会话记录：{e}")

        return session_path

    def read_plan(self, domain: str) -> str:
        """
        读取学习计划

        Args:
            domain: 领域名称

        Returns:
            计划内容

        Raises:
            FileNotFoundError: 如果计划不存在
        """
        plan_path = self.BASE_DIR / domain / "plan.md"
        if not plan_path.exists():
            raise FileNotFoundError(f"学习计划不存在：{domain}")

        try:
            return plan_path.read_text(encoding="utf-8")
        except Exception as e:
            raise FileReadError(f"无法读取学习计划：{e}")

    def domain_exists(self, domain: str) -> bool:
        """
        检查领域是否存在

        Args:
            domain: 领域名称

        Returns:
            是否存在
        """
        return (self.BASE_DIR / domain).exists()

    def list_domains(self) -> List[str]:
        """
        列出所有学习领域

        Returns:
            领域名称列表
        """
        if not self.BASE_DIR.exists():
            return []

        return [d.name for d in self.BASE_DIR.iterdir() if d.is_dir()]
