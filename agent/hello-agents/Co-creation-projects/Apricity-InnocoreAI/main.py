"""
研创·智核 - 主应用入口
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from innocore_ai.core.config import settings
from innocore_ai.core.database import engine, Base
from innocore_ai.core.exceptions import InnoCoreException
from innocore_ai.api.routes import papers, users, tasks, analysis, writing
from innocore_ai.agents.controller import AgentController

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局智能体控制器
agent_controller = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting InnoCore AI application...")
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # 初始化智能体控制器
    global agent_controller
    agent_controller = AgentController()
    await agent_controller.initialize()
    logger.info("Agent controller initialized")
    
    yield
    
    # 关闭时执行
    logger.info("Shutting down InnoCore AI application...")
    if agent_controller:
        await agent_controller.shutdown()
    logger.info("Application shutdown complete")

# 创建FastAPI应用
app = FastAPI(
    title="研创·智核 API",
    description="基于多智能体架构的智能科研助手平台",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# 挂载静态文件
try:
    app.mount("/static", StaticFiles(directory="innocore_ai/frontend/static"), name="static")
except Exception:
    # 如果路径不存在，尝试相对路径
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# 注册路由
app.include_router(users.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(papers.router, prefix="/api/v1/papers", tags=["论文管理"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["任务管理"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["分析报告"])
app.include_router(writing.router, prefix="/api/v1/writing", tags=["学术写作"])

# 前端路由
@app.get("/")
async def read_root():
    """前端主页"""
    try:
        from fastapi.responses import FileResponse
        return FileResponse("innocore_ai/frontend/index.html")
    except Exception:
        return FileResponse("frontend/index.html")

@app.get("/dashboard")
async def dashboard():
    """仪表板页面"""
    try:
        from fastapi.responses import FileResponse
        return FileResponse("innocore_ai/frontend/templates/dashboard.html")
    except Exception:
        return FileResponse("frontend/templates/dashboard.html")

@app.get("/login")
async def login():
    """登录页面"""
    try:
        from fastapi.responses import FileResponse
        return FileResponse("innocore_ai/frontend/templates/login.html")
    except Exception:
        return FileResponse("frontend/templates/login.html")

# 处理前端路由的通配符（用于SPA）
@app.get("/frontend/{path:path}")
async def frontend_files(path: str):
    """前端静态文件"""
    try:
        from fastapi.responses import FileResponse
        file_path = f"innocore_ai/frontend/{path}"
        return FileResponse(file_path)
    except Exception:
        file_path = f"frontend/{path}"
        return FileResponse(file_path)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "InnoCore AI"
    }

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats(request: Request):
    """获取仪表板统计数据"""
    # 这里应该从数据库获取真实数据
    return {
        "total_papers": 156,
        "total_tasks": 42,
        "total_analyses": 28,
        "total_writings": 15,
        "recent_activities": [
            {"type": "paper_added", "title": "深度学习在医学图像分析中的应用", "time": "2小时前"},
            {"type": "task_completed", "title": "文献搜索：机器学习", "time": "4小时前"},
            {"type": "analysis_generated", "title": "10篇论文综合分析", "time": "1天前"}
        ]
    }

# 全局异常处理
@app.exception_handler(InnoCoreException)
async def innocore_exception_handler(request: Request, exc: InnoCoreException):
    """处理自定义异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误",
            "details": str(exc) if settings.DEBUG else None
        }
    )

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = asyncio.get_event_loop().time()
    
    # 记录请求
    logger.info(f"Request: {request.method} {request.url}")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = asyncio.get_event_loop().time() - start_time
    
    # 记录响应
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

def create_app():
    """创建应用实例"""
    return app

if __name__ == "__main__":
    uvicorn.run(
        "innocore_ai.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )