# services/learning_knowledge_service.py

from hello_agents.tools import MemoryTool, RAGTool
from datetime import datetime
from typing import Optional


class LearningKnowledgeService:
    """
    学习记忆 + 知识检索服务
    供多智能体通过 A2A 调用
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.memory = MemoryTool(user_id=user_id)
        self.rag = RAGTool(rag_namespace=f"learning_{user_id}")
        self.active_learning_plan = {}

    def set_active_learning_plan(self, plan_id: str):
        self.active_learning_plan_id = plan_id

    def get_active_learning_plan(self):
        return self.active_learning_plan_id

    # ======================
    # 知识库相关
    # ======================
    def add_learning_material(self, file_path: str):
        return self.rag.run({
            "action": "add_document",
            "file_path": file_path,
            "chunk_size": 1000,
            "chunk_overlap": 200
        })

    def ask_knowledge(self, question: str):
        self._log_working_memory(f"提问: {question}")
        answer = self.rag.run({
            "action": "ask",
            "question": question,
            "limit": 5,
            "enable_advanced_search": True,
            "enable_mqe": True,
            "enable_hyde": True
        })

        self._log_episodic_memory(f"围绕问题 `{question}` 的学习")
        return answer

    # ======================
    # 记忆系统
    # ======================
    def add_note(self, content: str, concept: Optional[str] = None):
        self.memory.run({
            "action": "add",
            "content": content,
            "memory_type": "semantic",
            "importance": 0.8,
            "concept": concept or "general",
            "session_id": self.session_id
        })

    def recall(self, query: str):
        return self.memory.run({
            "action": "search",
            "query": query,
            "limit": 5
        })

    def summarize_learning(self):
        return self.memory.run({
            "action": "summary",
            "limit": 10
        })

    # ======================
    # 内部日志
    # ======================
    def _log_working_memory(self, content: str):
        self.memory.run({
            "action": "add",
            "content": content,
            "memory_type": "working",
            "importance": 0.6,
            "session_id": self.session_id
        })

    def _log_episodic_memory(self, content: str):
        self.memory.run({
            "action": "add",
            "content": content,
            "memory_type": "episodic",
            "importance": 0.7,
            "session_id": self.session_id
        })
