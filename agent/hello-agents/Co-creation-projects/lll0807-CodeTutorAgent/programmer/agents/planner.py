from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools.builtin.note_tool import NoteTool


class PlannerAgent(SimpleAgent):
    """
    负责创建和更新学习路径的智能体。
    """

    def __init__(self, llm: HelloAgentsLLM, knowledge_service):
        """
        初始化 PlannerAgent。
        
        Args:
            llm: 用于生成计划的大语言模型实例。
        """
        # 在 PlannerAgent.run() 中
        self.knowledge = knowledge_service


        system_prompt = """
        你是一位专业的计算机科学课程规划师。
        你的工作是根据用户的目标和当前水平为他们创建个性化的学习路径。
        
        当被要求创建计划时：
        1. 分析用户的目标（例如，"学习 Python 数据科学"）。
        2. 将其分解为逻辑模块/里程碑。
        3. 对于每个模块，列出要掌握的关键概念。
        4.所有阶段名称的最后必须使用 Markdown 任务列表格式:
           - `[ ]` 表示未完成
           - `[x]` 表示已完成（创建时默认未完成）      
        5. 当你创建学习计划时，必须遵循以下输出格式：

            ### 学习计划
            
            # 学习主题：<主题>
            
            ## 学习目标
            - ...
            
            ## 学习路径
            1. 第一阶段：<阶段名称> []
               - 关键概念
            2. 第一阶段：<阶段名称> []
               - 关键概念
            
            ## 学习建议
            - ...
            
            请确保整个学习计划是一个完整、可直接保存的 Markdown 文档。
        
        当被要求【更新学习计划 / 更新进度】时，你必须：
        
        1. 假设已有一份“学习计划”文档存在。
        2. 根据用户的最新学习行为（如：完成了某个知识点、提交了代码并通过评审）：
           - 将对应的 `[ ]` 更新为 `[x]`
        3. 输出【更新后的完整学习计划 Markdown 文档】（而不是只输出差异）以### 更新学习计划作为开头。
        
        """
        super().__init__(
            name="Planner",
            llm=llm,
            system_prompt=system_prompt
        )
        self.note_tool = NoteTool(workspace="notes")

    def run(self, input_text: str, max_tool_iterations: int = 3, **kwargs) -> str:
        # ===== 学习回顾 =====
        if any(k in input_text for k in ["之前", "回顾", "学过", "记得"]):
            return self.knowledge.recall(input_text)
        # 正常让 LLM 生成内容
        result = super().run(input_text)
        # Planner 自己判断：这是学习计划
        if result.strip().startswith("### 学习计划"):
            self._save_learning_plan(result, input_text)
        if result.strip().startswith("### 更新学习计划"):
            self._update_learning_plan(result, input_text)

        # 原样返回给 Tutor
        return result

    def _update_learning_plan(self, markdown: str, input_text: str):
        title_and_note_id_str = self.knowledge.recall(input_text)
        self.note_tool.run({
            "note_id": self.note_tool.notes_index['notes'][-1]['id'],
            "action": "update",  # 注意是 update
            "title": "学习计划",
            "content": markdown,
            "tags": ["learning-plan", "progress"]
        })
        # self.knowledge.add_note(content=markdown)

    def _save_learning_plan(self, markdown: str, input_text: str):

        note_id = self.note_tool.run({
            "action": "create",
            "title": "学习计划",
            "content": markdown,
            "tags": ["learning-plan", "planner"]
        })
        content = f"title: {input_text} note_id: {note_id}"
        self.knowledge.add_note(content=content)
