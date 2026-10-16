"""
InnoCore AI API模块
"""

try:
    from .main import app
    from .routes import *
    __all__ = ["app"]
except ImportError:
    # 当直接导入时，避免相对导入错误
    pass