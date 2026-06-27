from hello_agents import SimpleAgent, HelloAgentsLLM

class ExerciseAgent(SimpleAgent):
    """
    负责生成编程练习的智能体。
    """
    
    def __init__(self, llm: HelloAgentsLLM):
        """
        初始化 ExerciseAgent。
        
        Args:
            llm: 用于生成练习的大语言模型实例。
        """
        system_prompt = """
        你是一位富有创造力的编程练习生成器。
        你的目标是创建测试特定概念的练习题。
        
        当生成练习时：
        1. 你将获得一个主题（例如，"Python 列表"）和一个难度级别。
        2. 创建题目描述。
        3. 提供输入/输出示例。
        4. 定义约束条件。
        5. 最初不要向用户提供解决方案代码。
        
        清晰地格式化你的输出，以便展示给学生。
        """
        super().__init__(
            name="Exercise",
            llm=llm,
            system_prompt=system_prompt
        )
