from hello_agents import SimpleAgent, HelloAgentsLLM
from programmer.services.problem_repository import ProblemRepository
from hello_agents.tools import RAGTool
import re


class ExerciseAgent(SimpleAgent):
    """
    从本地题库中筛选编程题目的智能体（RAG + LLM 决策）
    """

    def __init__(self, llm: HelloAgentsLLM):
        system_prompt = """
你是一位【编程题目筛选助手】。

你的职责是：
- 理解用户对【难度】【知识点】【学习目标】的要求
- 输出你理解的用户需要的题目难度，只有两种选择Easy或Medium

⚠️ 重要规则：
- 不要生成新题目
你只需要输出Easy或Medium
"""
        super().__init__(
            name="Exercise",
            llm=llm,
            system_prompt=system_prompt
        )

        root_dir = r"E:\PycharmProject_lmx\HelloAgents-main\output"
        self.repo = ProblemRepository(root_dir)

        # ===== 初始化 RAG =====
        self.rag = RAGTool(
            collection_name="rag_knowledge_base",
            rag_namespace="problems"
        )
        # ===== 判断是否需要初始化题库 =====
        need_init = False

        try:
            # 尝试随便搜一个词，判断库是否为空
            test = self.rag.search(query="Easy", limit=1)
            if not test:
                need_init = True
        except Exception:
            # 向量库不存在 / 第一次运行
            need_init = True

        if need_init:
            # 第一次运行先添加题目到rag中
            for problem in self.repo.problems:
                self.rag.add_text(
                    text=f"""
                Title: {problem['title']}
                Difficulty: {problem['difficulty']}
                Tags: {", ".join(problem['tags'])}
                Description: {problem['description'][:200]}
                """.strip(),
                    document_id=problem["title"]
                )
        print("✅ 编程题目向量仓库构建完成")

    def run(self, input_text: str, max_tool_iterations: int = 3, **kwargs) -> str:

        result = super().run(input_text)
        # ========= RAG 语义召回 =========
        rag_results = self.rag.search(
            query=result,
            limit=3,
            min_score=0.3
        )
        titles = re.findall(r"Title:\s*(.+)", rag_results)

        user_problems = []
        # ========= 2️⃣ 本地题库精确过滤 =========
        for title in titles:
            problem = self.get_problem_by_title(title)
            if problem:
                user_problems.append(problem)

        if not user_problems:
            return "❌ 没有找到相关题目"

        # ========= 4️⃣ 返回标准化结果 =========
        return "\n\n".join(
            self._format_problem(problem)
            for problem in user_problems
        )

        # =========================================================
        # RAG 解析
        # =========================================================

    def get_problem_by_title(self, title: str):
        for problem in self.repo.problems:
            if problem.get("title") == title:
                return problem
        return None

    def _format_problem(self, problem: dict) -> str:
        examples_md = ""

        for i, ex in enumerate(problem["examples"], start=1):
            examples_md += f"""
    **Example {i}**

    Input: {ex["input"]}  
    Output: {ex["output"]}  
    """
            if ex["explanation"]:
                examples_md += f"Explanation: {ex['explanation']}\n"

        return f"""
    ### 推荐练习题：{problem['title']}

    **Difficulty:** {problem['difficulty']}  
    **Tags:** {", ".join(problem['tags'])}

    ---

    ## 📘 题目描述

    {problem['description']}

    ---

    ## 🧪 示例
    {examples_md}

    ---

    ## 📌 约束条件

    {problem['constraints']}

    ---

    💡 *请先尝试独立完成，不要直接查看题解。完成后可提交代码进行评审。*
    """
