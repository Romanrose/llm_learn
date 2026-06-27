"""LearningAgent 自定义异常类"""


class LearningAgentError(Exception):
    """基础异常类"""

    pass


class DomainNotFoundError(LearningAgentError):
    """领域不存在"""

    def __init__(self, domain: str):
        self.domain = domain
        super().__init__(f"领域 '{domain}' 不存在。请先使用 /create 创建学习计划。")


class FileReadError(LearningAgentError):
    """文件读取失败"""

    def __init__(self, message: str):
        super().__init__(f"文件读取失败：{message}")


class FileWriteError(LearningAgentError):
    """文件写入失败"""

    def __init__(self, message: str):
        super().__init__(f"文件写入失败：{message}")


class LLMError(LearningAgentError):
    """LLM 调用失败"""

    def __init__(self, message: str):
        super().__init__(f"AI服务错误：{message}")


class InvalidInputError(LearningAgentError):
    """无效输入"""

    def __init__(self, message: str):
        super().__init__(f"无效输入：{message}")
