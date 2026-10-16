"""
InnoCore AI 自定义异常类
"""

class InnoCoreException(Exception):
    """InnoCore AI 基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AgentException(InnoCoreException):
    """Agent相关异常"""
    pass

class VectorStoreException(InnoCoreException):
    """向量存储异常"""
    pass

class DatabaseException(InnoCoreException):
    """数据库异常"""
    pass

class LLMException(InnoCoreException):
    """LLM调用异常"""
    pass

class PDFParsingException(InnoCoreException):
    """PDF解析异常"""
    pass

class ExternalAPIException(InnoCoreException):
    """外部API调用异常"""
    pass

class ConfigurationException(InnoCoreException):
    """配置异常"""
    pass

class ValidationException(InnoCoreException):
    """数据验证异常"""
    pass

class TimeoutException(InnoCoreException):
    """超时异常"""
    pass

class ResourceExhaustedException(InnoCoreException):
    """资源耗尽异常"""
    pass