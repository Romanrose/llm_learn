# agents/create_plan_agent.py
"""学习计划生成 Agent"""

import re
from hello_agents import ReActAgent, HelloAgentsLLM
from core.file_manager import FileManager


class CreatePlanAgent(ReActAgent):
    """
    学习计划生成专家
    支持三种输入：领域描述、GitHub URL、PDF 论文
    """

    def __init__(self, llm: HelloAgentsLLM, streaming: bool = None):
        """
        初始化 CreatePlanAgent

        Args:
            llm: HelloAgentsLLM 实例
            streaming: 是否启用流式输出（None = 自动检测）
        """
        self.max_steps = 5
        self.file_manager = FileManager()

        # 添加流式输出支持
        from utils.streaming import should_stream
        self.streaming = should_stream(streaming)

        # 系统提示词
        system_prompt = """
        你是学习规划专家。工作流程：

        1. 识别输入类型：
           - 领域描述（如："我想学习数学"）
           - GitHub URL（如："https://github.com/user/project"）
           - PDF 论文路径（如："/path/to/paper.pdf"）

        2. 如果是 URL/文件，调用相应工具深度分析

        3. 询问用户的学习目标：
           - 使用自然语言描述（如："想在工作中应用"，"想达到研究生水平"）

        4. 根据分析结果和学习目标，搜索该领域的最佳学习路径

        5. 生成结构化的学习计划（Markdown格式），包括：
           - 领域概述
           - 前置知识要求
           - 学习路径（分阶段）
           - 推荐资源
           - 里程碑和检查点

        使用 ReAct 格式：
        Thought: 你的思考过程
        Action: tool_name[input]
        Observation: 工具返回结果
        ...
        Finish: [最终生成的学习计划]
        """

        # 使用父类初始化
        super().__init__("CreatePlanAgent", llm, system_prompt)

    def _identify_input_type(self, input_data: str) -> str:
        """
        识别输入类型

        Args:
            input_data: 用户输入

        Returns:
            输入类型（github_url/pdf_paper/domain_description）
        """
        # 检查 GitHub URL
        if input_data.startswith("https://github.com/"):
            return "github_url"

        # 检查 PDF 文件路径
        if (
            input_data.endswith(".pdf")
            or input_data.startswith("~/")
            or input_data.startswith("/")
        ):
            return "pdf_paper"

        # 默认为领域描述
        return "domain_description"

    def _analyze_github_repo(self, url: str) -> dict:
        """
        分析 GitHub 仓库

        Args:
            url: GitHub URL

        Returns:
            分析结果字典
        """
        from specialist.repo_analyzer import RepoAnalyzerAgent
        import os

        # 获取 GitHub Token（如果配置了）
        github_token = os.getenv("GITHUB_TOKEN")

        # 创建 RepoAnalyzerAgent
        repo_analyzer = RepoAnalyzerAgent(self.llm, github_token)

        # 分析仓库
        try:
            analysis = repo_analyzer.analyze(url)
            return {
                "domain": analysis.get("domain", ""),
                "tech_stack": analysis.get("tech_stack", []),
                "prerequisites": analysis.get("prerequisites", []),
                "description": analysis.get("description", ""),
                "stars": analysis.get("stars", 0),
            }
        except Exception as e:
            # 降级：使用简化实现
            repo_name = url.rstrip(".git").split("/")[-1]
            return {
                "domain": repo_name.replace("-", " ").replace("_", " "),
                "tech_stack": [],
                "prerequisites": [],
                "description": f"GitHub 仓库分析失败：{e}",
                "stars": 0,
            }

    def _analyze_pdf_paper(self, file_path: str) -> dict:
        """
        分析 PDF 论文

        Args:
            file_path: PDF 文件路径

        Returns:
            分析结果字典
        """
        from specialist.paper_analyzer import PaperAnalyzerAgent

        # 创建 PaperAnalyzerAgent
        paper_analyzer = PaperAnalyzerAgent(self.llm)

        # 分析论文
        try:
            analysis = paper_analyzer.analyze(file_path)
            return {
                "domain": analysis.get("domain", ""),
                "title": analysis.get("title", ""),
                "prerequisites": analysis.get("prerequisites", []),
                "core_concepts": analysis.get("core_concepts", []),
            }
        except Exception as e:
            # 降级：使用简化实现
            import os

            filename = os.path.basename(file_path).replace(".pdf", "").replace("-", " ")
            return {
                "domain": filename,
                "title": filename,
                "prerequisites": [],
                "core_concepts": [],
                "error": f"PDF 分析失败：{e}",
            }

    def _ask_learning_goal(self, analysis: dict) -> str:
        """
        询问学习目标

        Args:
            analysis: 分析结果

        Returns:
            学习目标描述
        """
        print(f"\n📚 分析结果：{analysis.get('domain', '未知领域')}")
        if analysis.get("tech_stack"):
            print(f"技术栈：{', '.join(analysis['tech_stack'])}")
        if analysis.get("prerequisites"):
            print(f"前置知识：{', '.join(analysis['prerequisites'])}")
        if analysis.get("title"):
            print(f"论文标题：{analysis['title']}")
        if analysis.get("core_concepts"):
            print(
                f"核心概念：{', '.join(analysis['core_concepts'][:5])}"
            )  # 最多显示5个
        if analysis.get("description"):
            print(f"描述：{analysis['description']}")
        if analysis.get("stars", 0) > 0:
            print(f"⭐ Stars: {analysis['stars']}")

        return input("\n🎯 你想达到什么学习程度？（请用自然语言描述）\n> ")

    def _search_learning_resources(self, query: str) -> str:
        """
        搜索学习资源

        Args:
            query: 搜索查询

        Returns:
            搜索结果
        """
        # 简化实现，返回通用建议
        return f"为 '{query}' 找到的学习资源：在线课程、书籍、文档、实战项目"

    def _generate_plan(self, analysis: dict, goal: str, resources: str) -> str:
        """
        生成学习计划

        Args:
            analysis: 分析结果
            goal: 学习目标
            resources: 学习资源

        Returns:
            学习计划内容
        """
        user_prompt = f"""请为以下场景生成学习计划（Markdown格式）：

【领域/主题】
{analysis.get('domain', '未知')}

【技术栈】
{', '.join(analysis.get('tech_stack', ['无']))}

【前置知识要求】
{', '.join(analysis.get('prerequisites', ['无']))}

【学习目标】
{goal}

【参考资源】
{resources}

请生成结构化的学习计划，包括：
1. 领域概述（100字）
2. 前置知识检查清单
3. 分阶段学习路径（3-5个阶段）
4. 每个阶段的具体学习内容
5. 推荐资源（书籍、课程、文档）
6. 里程碑和自我评估标准
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的学习规划助手，擅长创建结构化的学习计划。",
            },
            {"role": "user", "content": user_prompt},
        ]

        if self.streaming:
            from utils.streaming import stream_response
            return stream_response(self.llm, messages)
        else:
            return self.llm.invoke(messages)

    def run(self, input_data: str) -> str:
        """
        执行学习计划创建流程

        Args:
            input_data: 用户输入（领域描述/GitHub URL/PDF路径）

        Returns:
            执行结果
        """
        # 步骤1：识别输入类型
        input_type = self._identify_input_type(input_data)

        # 步骤2：根据类型处理
        if input_type == "github_url":
            analysis = self._analyze_github_repo(input_data)
        elif input_type == "pdf_paper":
            analysis = self._analyze_pdf_paper(input_data)
        else:  # domain_description
            analysis = {"domain": input_data, "tech_stack": [], "prerequisites": []}

        # 步骤3：确认学习目标
        learning_goal = self._ask_learning_goal(analysis)

        # 步骤4：搜索学习路径
        search_query = f"{analysis['domain']} 学习路径 {learning_goal}"
        learning_resources = self._search_learning_resources(search_query)

        # 步骤5：生成计划
        plan = self._generate_plan(analysis, learning_goal, learning_resources)

        # 步骤6：保存计划
        domain = analysis["domain"]
        self.file_manager.create_domain(domain)
        self.file_manager.save_plan(domain, plan)

        return f"✅ 学习计划已创建：{domain}\n\n{plan}"
