# core/main_agent.py
"""主 Agent - 协调层，负责意图识别和路由"""

from hello_agents import SimpleAgent, HelloAgentsLLM
from core.file_manager import FileManager


class MainAgent(SimpleAgent):
    """
    系统协调者，负责意图识别和路由

    职责：
    - 接收用户输入
    - 识别用户意图（create/add/vibe/summary/help/exit）
    - 路由到相应的子 Agent 或处理器
    - 管理基本命令（help, list, exit）
    """

    # 意图关键词映射（按优先级排序，更具体的在前）
    INTENT_KEYWORDS = {
        "create": [
            "/create",
            "创建计划",
            "制定学习路径",
            "我想学",
            "我想学习",
            "学习计划",  # 移除单独的"学习"以避免冲突
        ],
        "add": ["/add", "添加笔记", "记录知识", "添加知识"],
        "vibe": ["/vibe", "开始学习", "互动学习", "练习", "考察"],
        "summary": ["/summary", "学习进度", "总结", "评估"],
        "help": ["/help", "帮助", "help"],
        "list": ["/list", "列出所有", "所有领域", "列表"],
        "exit": ["/exit", "退出", "quit", "exit"],
    }

    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager, streaming: bool = None):
        """
        初始化主 Agent

        Args:
            llm: HelloAgentsLLM 实例
            file_manager: FileManager 实例
            streaming: 是否启用流式输出（None = 自动检测）
        """
        system_prompt = """
        你是 LearningAgent 学习助手的主界面。

        支持的功能：
        1. 创建学习计划 (/create, "我想学习")
        2. 添加知识笔记 (/add, "添加笔记")
        3. 开始互动学习 (/vibe, "开始学习")
        4. 查看学习总结 (/summary, "总结")
        5. 显示帮助 (/help, "帮助")
        6. 列出所有领域 (/list)
        7. 退出程序 (/exit, "退出")

        识别用户意图后，调用相应的功能。
        如果意图模糊，询问用户确认。
        """

        self.llm = llm
        self.file_manager = file_manager

        # 添加流式输出支持
        from utils.streaming import should_stream
        self.streaming = should_stream(streaming)

        # 会话状态管理
        self.active_session = None  # {"domain": str, "mode": str, "round": int}

        # 使用父类初始化
        super().__init__("MainAgent", llm, system_prompt)

    def _identify_intent(self, user_input: str) -> str:
        """
        识别用户意图

        Args:
            user_input: 用户输入

        Returns:
            意图类型（create/add/vibe/summary/help/list/exit/unknown）
        """
        user_input_lower = user_input.lower().strip()

        # 检查每个意图的关键词
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    return intent

        return "unknown"

    def process_command(self, user_input: str) -> str:
        """
        处理用户命令

        Args:
            user_input: 用户输入

        Returns:
            处理结果
        """
        # 检查是否有活跃的 vibe 会话
        if self.active_session is not None:
            # 检查是否要退出会话
            if self._is_exit_command(user_input):
                return self._end_vibe_session()
            # 否则继续对话
            return self._continue_vibe_session(user_input)

        # 正常命令处理
        intent = self._identify_intent(user_input)

        if intent == "create":
            return self._route_to_create_plan(user_input)
        elif intent == "add":
            return self._route_to_add_knowledge(user_input)
        elif intent == "vibe":
            return self._route_to_vibe_learning(user_input)
        elif intent == "summary":
            return self._route_to_summary(user_input)
        elif intent == "help":
            return self._show_help()
        elif intent == "list":
            return self._list_domains()
        elif intent == "exit":
            return "EXIT"
        elif intent == "unknown":
            return "❓ 未识别的命令。输入 /help 查看帮助。"

    def _route_to_create_plan(self, input_data: str) -> str:
        """
        路由到 CreatePlanAgent

        Args:
            input_data: 用户输入

        Returns:
            执行结果
        """
        from agents.create_plan_agent import CreatePlanAgent

        try:
            # 去掉命令前缀，只保留参数部分
            # 支持: "/create 数学", "创建计划 数学", "我想学习数学"
            clean_input = input_data

            # 去掉 /create 前缀
            for prefix in ["/create", "/CREATE"]:
                if clean_input.startswith(prefix):
                    clean_input = clean_input[len(prefix) :].strip()
                    break

            # 如果是自然语言形式，保留原样
            # 例如: "我想学习数学", "创建一个学习计划"
            if not clean_input or clean_input == input_data:
                clean_input = input_data

            agent = CreatePlanAgent(self.llm, streaming=self.streaming)
            return agent.run(clean_input)
        except Exception as e:
            return f"❌ 创建学习计划失败：{e}"

    def _route_to_add_knowledge(self, input_data: str) -> str:
        """
        路由到 AddKnowledgeProcessor

        Args:
            input_data: 用户输入

        Returns:
            执行结果
        """
        from processors.add_knowledge import AddKnowledgeProcessor

        try:
            # 去掉命令前缀，只保留参数部分
            # 支持: "/add 数学 算法", "添加笔记", "记录知识"
            clean_input = input_data

            # 去掉 /add 前缀
            for prefix in ["/add", "/ADD"]:
                if clean_input.startswith(prefix):
                    clean_input = clean_input[len(prefix) :].strip()
                    break

            # 如果是自然语言形式，需要询问用户输入内容和领域
            if not clean_input or clean_input == input_data or len(clean_input) < 10:
                return self._ask_for_knowledge_input()

            # 解析输入（格式：领域 内容）
            # 例如: "机器学习 决策树算法"
            parts = clean_input.split(maxsplit=1)
            if len(parts) == 2:
                domain, content = parts
                domain = domain.strip()
                content = content.strip()
            else:
                # 无法解析，询问用户
                return self._ask_for_knowledge_input()

            processor = AddKnowledgeProcessor(self.llm, self.file_manager)
            return processor.add(domain, content)
        except Exception as e:
            return f"❌ 添加知识失败：{e}"

    def _ask_for_knowledge_input(self) -> str:
        """
        询问用户知识内容和领域

        Returns:
            提示信息
        """
        return """📝 添加知识笔记

请按以下格式输入：

> /add <领域> <知识内容>

例如：
> /add 机器学习 # 决策树算法简介

或者直接输入内容（会询问领域）：
> /add 决策树是一种监督学习算法，用于分类和回归...

💡 提示：长内容可以先在编辑器中准备好，然后一次性粘贴。
"""

    def _route_to_vibe_learning(self, input_data: str) -> str:
        """
        路由到 VibeLearningAgent

        Args:
            input_data: 用户输入

        Returns:
            执行结果
        """
        from agents.vibe_learning_agent import VibeLearningAgent

        try:
            # 去掉命令前缀，只保留参数部分
            # 支持: "/vibe Python", "/vibe Python --mode quiz"
            clean_input = input_data

            # 去掉 /vibe 前缀
            for prefix in ["/vibe", "/VIBE", "/Vibe"]:
                if clean_input.startswith(prefix):
                    clean_input = clean_input[len(prefix):].strip()
                    break

            # 如果是自然语言形式，询问用户
            if not clean_input or len(clean_input.split()) < 1:
                return self._ask_for_vibe_input()

            # 解析输入
            # 格式: <领域> [--mode <mode>]
            parts = clean_input.split()
            domain = parts[0].strip()

            # 检查是否有模式选项
            mode = "free"  # 默认模式
            if "--mode" in parts:
                mode_idx = parts.index("--mode")
                if mode_idx + 1 < len(parts):
                    mode = parts[mode_idx + 1].strip().lower()
                    if mode not in ["free", "quiz"]:
                        return "❌ 无效的模式。请使用 --mode free 或 --mode quiz"

            # 启动学习会话
            agent = VibeLearningAgent(self.llm, self.file_manager,
                                     streaming=self.streaming)
            result = agent.start_session(domain, mode=mode)

            # 设置活跃会话
            self.active_session = {
                "domain": domain,
                "mode": mode,
                "round": 1,
                "agent": agent,
                "streaming": self.streaming  # 保存 streaming 设置
            }

            return result

        except Exception as e:
            return f"❌ 启动互动学习失败：{e}"

    def _route_to_summary(self, input_data: str) -> str:
        """
        路由到 SummaryAgent

        Args:
            input_data: 用户输入

        Returns:
            执行结果
        """
        from agents.summary_agent import SummaryAgent

        try:
            # 去掉命令前缀，只保留参数部分
            # 支持: "/summary Python", "总结学习进度"
            clean_input = input_data

            # 去掉 /summary 前缀
            for prefix in ["/summary", "/SUMMARY", "/Summary"]:
                if clean_input.startswith(prefix):
                    clean_input = clean_input[len(prefix):].strip()
                    break

            # 如果是自然语言形式，询问用户
            if not clean_input or len(clean_input.split()) < 1:
                return self._ask_for_summary_input()

            # 解析输入
            # 格式: <领域>
            domain = clean_input.split()[0].strip()

            # 生成学习总结
            agent = SummaryAgent(self.llm, self.file_manager,
                                streaming=self.streaming)
            return agent.run(domain)

        except Exception as e:
            return f"❌ 生成学习总结失败：{e}"

    def _is_exit_command(self, user_input: str) -> bool:
        """
        检查是否是退出命令

        Args:
            user_input: 用户输入

        Returns:
            是否是退出命令
        """
        exit_keywords = ["/exit", "exit", "退出", "quit", "/quit", "结束", "完成"]
        return user_input.strip().lower() in exit_keywords

    def _end_vibe_session(self) -> str:
        """
        结束 vibe 会话

        Returns:
            结束消息
        """
        domain = self.active_session["domain"]
        mode = self.active_session["mode"]
        rounds = self.active_session["round"]

        # 清除会话状态
        self.active_session = None

        return f"""✅ 会话已结束

📁 领域: {domain}
📝 模式: {mode}
💬 对话轮数: {rounds}

💡 上下文已保存。输入 /help 查看可用命令。
"""

    def _continue_vibe_session(self, user_input: str) -> str:
        """
        继续 vibe 会话

        Args:
            user_input: 用户回答

        Returns:
            反馈和下一个问题
        """
        try:
            agent = self.active_session["agent"]
            domain = self.active_session["domain"]
            mode = self.active_session["mode"]

            # 确保 streaming 设置一致
            agent.streaming = self.active_session.get("streaming", agent.streaming)

            # 继续对话（获取反馈和下一个问题）
            result = agent.continue_session(domain, user_input, mode)

            # 增加轮次计数
            self.active_session["round"] += 1

            return result

        except Exception as e:
            # 发生错误时清除会话状态
            self.active_session = None
            return f"❌ 对话过程中发生错误：{e}\n\n会话已结束。"

    def _ask_for_vibe_input(self) -> str:
        """
        询问用户互动学习参数

        Returns:
            提示信息
        """
        return """📝 互动学习

请按以下格式输入：

> /vibe <领域> [--mode <模式>]

例如：
> /vibe Python
> /vibe Python --mode quiz

模式说明：
- free: 自由对话模式（默认）
- quiz: 测验模式

💡 提示：需要先使用 /create 创建学习计划。
"""

    def _ask_for_summary_input(self) -> str:
        """
        询问用户学习总结参数

        Returns:
            提示信息
        """
        return """📝 学习进度总结

请按以下格式输入：

> /summary <领域>

例如：
> /summary Python
> /summary 机器学习

💡 提示：需要先使用 /create 创建学习计划。
"""

    def _show_help(self) -> str:
        """显示帮助信息"""
        return """
# 🤖 LearningAgent 帮助

## 命令列表

### 创建学习计划
- `/create <领域>` - 创建学习计划
  例：`/create 数学`
  例：`/create https://github.com/user/project`
  例：`/create ~/paper.pdf`

- 自然语言：`我想学习数学`

### 添加知识笔记 ✨ 新功能
- `/add <领域> <内容>` - 添加知识笔记
  例：`/add 机器学习 # 决策树算法简介`
  例：`/add Python 这是一个列表推导式的例子...`

- 文件输入：`/add ~/notes.md`

- 自然语言：`添加笔记` `记录知识`

### 开始互动学习 ✨ 新功能
- `/vibe <领域>` - 开始互动学习
  例：`/vibe Python`
  例：`/vibe Python --mode quiz`

- 模式说明：
  - `free`: 自由对话模式（默认）
  - `quiz`: 测验模式

- 退出会话：输入"退出"、"exit"或"/exit"即可随时结束

- 自然语言：`开始学习数学` `练习一下`

### 查看学习总结 ✨ 新功能
- `/summary <领域>` - 查看学习总结
  例：`/summary Python`
  例：`/summary 机器学习`

- 自然语言：`总结学习进度` `评估我的水平`

### 其他命令
- `/list` - 列出所有学习领域
- `/help` - 显示帮助
- `/exit` 或 `exit` - 退出程序

## 提示
- 支持命令前缀（如 `/create`）和自然语言（如"我想学习"）
- 添加知识时，内容会自动分析、分类并打标签
- 随时输入 `/help` 查看帮助
"""

    def _list_domains(self) -> str:
        """列出所有学习领域"""
        domains = self.file_manager.list_domains()

        if not domains:
            return "📭 还没有创建任何学习领域。\n使用 `/create` 创建第一个学习计划。"

        domain_list = "\n".join([f"- {domain}" for domain in domains])
        return f"# 📚 学习领域\n\n{domain_list}\n\n共 {len(domains)} 个领域"

    def list_domains(self) -> list:
        """
        获取所有领域列表

        Returns:
            领域名称列表
        """
        return self.file_manager.list_domains()
