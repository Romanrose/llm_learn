# agents/summary_agent.py
"""学习进度评估 Agent - 生成学习总结和建议"""

from hello_agents import SimpleAgent, HelloAgentsLLM
from core.file_manager import FileManager
from pathlib import Path


class SummaryAgent(SimpleAgent):
    """
    学习进度评估专家

    功能：
    - 读取学习目标（plan.md）
    - 读取已掌握知识（knowledge_summary.md）
    - 读取学习历程（session_summary.md）
    - 生成当前水平评估
    - 推荐下一步学习内容
    """

    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager, streaming: bool = None):
        """
        初始化 SummaryAgent

        Args:
            llm: HelloAgentsLLM 实例
            file_manager: FileManager 实例
            streaming: 是否启用流式输出（None = 自动检测）
        """
        system_prompt = """
你是学习评估专家。

任务：
1. 对比学习目标和现状，评估掌握程度（百分比）
2. 识别强项和弱项
3. 推荐下一步学习内容
4. 提供具体的学习建议

输出格式：
# 📊 学习进度报告

## 当前水平
- 整体掌握度：XX%
- 处于阶段：入门/熟练/精通

## ✅ 掌握良好的知识点
- [知识点1]：简短评价
- [知识点2]：简短评价

## ⚠️ 需要加强的知识点
- [知识点1]：原因分析
- [知识点2]：原因分析

## 📌 下一步学习建议
1. [具体主题1]：学习建议
2. [具体主题2]：学习建议

## 💡 总体建议
[鼓励和指导]
"""

        self.llm = llm
        self.file_manager = file_manager

        # 添加流式输出支持
        from utils.streaming import should_stream
        self.streaming = should_stream(streaming)

        # 使用父类初始化
        super().__init__("SummaryAgent", llm, system_prompt)

    def run(self, domain: str) -> str:
        """
        生成学习进度总结

        Args:
            domain: 领域名称

        Returns:
            学习进度报告
        """
        # 检查领域是否存在
        if not self.file_manager.domain_exists(domain):
            return f"❌ 领域 '{domain}' 不存在。请先使用 /create 创建学习计划。"

        # 读取必要的文件
        try:
            # 读取学习计划
            plan = self.file_manager.read_plan(domain)

            # 读取知识摘要
            knowledge_summary_path = (
                self.file_manager.BASE_DIR / domain / "knowledge" / "knowledge_summary.md"
            )
            if knowledge_summary_path.exists():
                knowledge_summary = knowledge_summary_path.read_text(encoding="utf-8")
            else:
                knowledge_summary = "暂无知识笔记"

            # 读取会话摘要
            session_summary_path = (
                self.file_manager.BASE_DIR / domain / "sessions" / "session_summary.md"
            )
            if session_summary_path.exists():
                session_summary = session_summary_path.read_text(encoding="utf-8")
            else:
                session_summary = "暂无学习记录"

        except Exception as e:
            return f"❌ 读取文件失败：{e}"

        # 生成总结
        user_prompt = f"""请分析以下学习情况：

【学习目标】
{plan[:2000]}

【已掌握知识】
{knowledge_summary[:2000]}

【学习历程】
{session_summary[:2000]}

请按照系统提示词的格式生成学习进度报告。
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个学习评估专家，擅长分析学习进度并提供针对性建议。",
            },
            {"role": "user", "content": user_prompt},
        ]

        try:
            if self.streaming:
                from utils.streaming import stream_response
                return stream_response(self.llm, messages)
            else:
                return self.llm.invoke(messages).strip()
        except Exception as e:
            # 如果 LLM 调用失败，返回简化版本
            return f"""# 📊 学习进度报告

## 当前水平
- 领域：{domain}
- 状态：学习进行中

## 📚 学习内容
- 学习计划：已创建
- 知识笔记：{'有' if knowledge_summary != '暂无知识笔记' else '无'}
- 学习记录：{'有' if session_summary != '暂无学习记录' else '无'}

## 💡 建议
请继续添加知识笔记和参与互动学习，以获得更准确的进度评估。

⚠️ 生成详细报告时遇到问题：{e}
"""
