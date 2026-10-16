from hello_agents import SimpleAgent, HelloAgentsLLM

class PlannerAgent(SimpleAgent):
    """
    负责创建和更新学习路径的智能体。
    """
    
    def __init__(self, llm: HelloAgentsLLM):
        """
        初始化 PlannerAgent。
        
        Args:
            llm: 用于生成计划的大语言模型实例。
        """
        system_prompt = """
        你是一位专业的计算机科学课程规划师。
        你的工作是根据用户的目标和当前水平为他们创建个性化的学习路径。
        
        当被要求创建计划时：
        1. 分析用户的目标（例如，"学习 Python 数据科学"）。
        2. 将其分解为逻辑模块/里程碑。
        3. 对于每个模块，列出要掌握的关键概念。
        4. 以 Markdown 格式输出结构化的计划。
        
        当被要求更新计划时：
        1. 回顾用户最近的表现。
        2. 调整剩余模块的进度或深度。
        """
        super().__init__(
            name="Planner",
            llm=llm,
            system_prompt=system_prompt
        )
