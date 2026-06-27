# core/summary_manager.py
"""摘要更新管理器 - 混合策略：<5个文件完全重写，≥5个增量更新"""

from pathlib import Path
from typing import List
from hello_agents import HelloAgentsLLM
from config import Config


class SummaryManager:
    """
    管理知识摘要和会话摘要的更新

    使用混合策略：
    - 文件数 < 5：完全重写摘要
    - 文件数 ≥ 5：增量更新摘要

    Attributes:
        fm: FileManager 实例
        llm: HelloAgentsLLM 实例
    """

    def __init__(self, file_manager):
        """
        初始化摘要管理器

        Args:
            file_manager: FileManager 实例
        """
        self.fm = file_manager
        self.llm = HelloAgentsLLM()

    def update_knowledge_summary(self, domain: str, new_file: str) -> None:
        """
        更新 knowledge_summary.md

        Args:
            domain: 领域名称
            new_file: 新添加的文件名
        """
        domain_path = self.fm.BASE_DIR / domain
        knowledge_dir = domain_path / "knowledge"
        summary_path = knowledge_dir / "knowledge_summary.md"

        # 统计文件数（排除 summary.md）
        existing_files: List[Path] = list(knowledge_dir.glob("*.md"))
        file_count = len(
            [f for f in existing_files if f.name != "knowledge_summary.md"]
        )

        if file_count < Config.SUMMARY_FULL_REWRITE_THRESHOLD:
            self._full_rewrite_knowledge_summary(domain, knowledge_dir, summary_path)
        else:
            self._incremental_update_knowledge_summary(domain, new_file, summary_path)

    def _full_rewrite_knowledge_summary(
        self, domain: str, knowledge_dir: Path, summary_path: Path
    ) -> None:
        """
        完全重写知识摘要

        Args:
            domain: 领域名称
            knowledge_dir: 知识目录
            summary_path: 摘要文件路径
        """
        # 读取所有知识文件
        all_files: List[Path] = [
            f for f in knowledge_dir.glob("*.md") if f.name != "knowledge_summary.md"
        ]
        all_content = []
        for file in all_files:
            content = file.read_text(encoding="utf-8")
            all_content.append(f"## {file.stem}\n{content}\n")

        # 让 LLM 生成压缩摘要
        user_prompt = f"""以下是 {domain} 领域的所有知识笔记，请生成一个结构化的总结摘要：

{''.join(all_content)}

要求：
1. 按主题分类组织
2. 提取核心概念和关键知识点
3. 保持结构化（markdown格式）
4. 控制在原来内容的20%长度
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个知识总结助手，擅长提取核心概念并生成结构化摘要。",
            },
            {"role": "user", "content": user_prompt},
        ]

        try:
            summary = self.llm.invoke(messages)
            summary_path.write_text(summary, encoding="utf-8")
        except Exception:
            # 如果 LLM 调用失败，使用简单的合并
            fallback_summary = f"# {domain} 知识总结\n\n" + "\n".join(all_content)
            summary_path.write_text(fallback_summary, encoding="utf-8")

    def _incremental_update_knowledge_summary(
        self, domain: str, new_file: str, summary_path: Path
    ) -> None:
        """
        增量更新知识摘要

        Args:
            domain: 领域名称
            new_file: 新文件名
            summary_path: 摘要文件路径
        """
        # 读取当前摘要和新文件
        current_summary = summary_path.read_text(encoding="utf-8")
        new_content = (self.fm.BASE_DIR / domain / "knowledge" / new_file).read_text(
            encoding="utf-8"
        )

        # 让 LLM 合并
        user_prompt = f"""当前摘要：
{current_summary}

新增内容：
{new_content}

请将新增内容整合到摘要中，保持结构化和简洁性。
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个知识总结助手，擅长整合新内容到现有摘要中。",
            },
            {"role": "user", "content": user_prompt},
        ]

        try:
            updated_summary = self.llm.invoke(messages)
            summary_path.write_text(updated_summary, encoding="utf-8")
        except Exception:
            # 如果 LLM 调用失败，使用简单追加
            updated_summary = (
                current_summary + f"\n\n## {Path(new_file).stem}\n{new_content}"
            )
            summary_path.write_text(updated_summary, encoding="utf-8")

    def update_session_summary(self, domain: str, new_session_content: str) -> None:
        """
        更新 session_summary.md

        Args:
            domain: 领域名称
            new_session_content: 新会话内容
        """
        domain_path = self.fm.BASE_DIR / domain
        sessions_dir = domain_path / "sessions"
        summary_path = sessions_dir / "session_summary.md"

        # 统计文件数
        existing_files: List[Path] = list(sessions_dir.glob("session_*.md"))
        file_count = len(
            [f for f in existing_files if not f.name.startswith("session_summary")]
        )

        if file_count < Config.SUMMARY_FULL_REWRITE_THRESHOLD:
            self._full_rewrite_session_summary(domain, sessions_dir, summary_path)
        else:
            self._incremental_update_session_summary(new_session_content, summary_path)

    def _full_rewrite_session_summary(
        self, domain: str, sessions_dir: Path, summary_path: Path
    ) -> None:
        """
        完全重写会话摘要
        """
        all_sessions: List[Path] = [
            f
            for f in sessions_dir.glob("session_*.md")
            if not f.name.startswith("session_summary")
        ]
        all_content = []
        for file in all_sessions:
            content = file.read_text(encoding="utf-8")
            all_content.append(f"## {file.stem}\n{content}\n")

        user_prompt = f"""以下是 {domain} 领域的所有学习会话记录，请生成一个压缩的总结：

{''.join(all_content)}

要求：
1. 提取关键学习点
2. 记录进步轨迹
3. 识别需要复习的内容
4. 控制在原来内容的30%长度
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个学习历程总结助手，擅长提取关键学习点和进步轨迹。",
            },
            {"role": "user", "content": user_prompt},
        ]

        try:
            summary = self.llm.invoke(messages)
            summary_path.write_text(summary, encoding="utf-8")
        except Exception:
            fallback_summary = f"# {domain} 学习历程\n\n" + "\n".join(all_content)
            summary_path.write_text(fallback_summary, encoding="utf-8")

    def _incremental_update_session_summary(
        self, new_session_content: str, summary_path: Path
    ) -> None:
        """
        增量更新会话摘要
        """
        current_summary = summary_path.read_text(encoding="utf-8")

        user_prompt = f"""当前总结：
{current_summary}

新会话记录：
{new_session_content}

请将新会话整合到总结中。
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个学习历程总结助手，擅长整合新的学习会话到总结中。",
            },
            {"role": "user", "content": user_prompt},
        ]

        try:
            updated_summary = self.llm.invoke(messages)
            summary_path.write_text(updated_summary, encoding="utf-8")
        except Exception:
            updated_summary = current_summary + f"\n\n{new_session_content}"
            summary_path.write_text(updated_summary, encoding="utf-8")
