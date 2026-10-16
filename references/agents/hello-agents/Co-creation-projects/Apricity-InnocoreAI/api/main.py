"""
InnoCore API 主应用
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn

from core.config import get_config
from core.database import db_manager
from core.vector_store import vector_store_manager
from agents.controller import agent_controller
from .routes import papers, users, tasks, analysis, writing, citations, workflow

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在启动InnoCore AI...")
    
    # 初始化数据库（可选）
    try:
        await db_manager.initialize()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.warning(f"数据库初始化失败（将以无数据库模式运行）: {str(e)}")
    
    # 初始化向量存储（可选）
    try:
        await vector_store_manager.initialize()
        logger.info("向量存储初始化完成")
    except Exception as e:
        logger.warning(f"向量存储初始化失败（将以无向量存储模式运行）: {str(e)}")
    
    # 初始化智能体控制器（可选）
    try:
        await agent_controller.initialize()
        logger.info("智能体控制器初始化完成")
        
        # 启动任务处理器
        import asyncio
        asyncio.create_task(agent_controller.start_task_processor())
        logger.info("任务处理器已启动")
    except Exception as e:
        logger.warning(f"智能体控制器初始化失败: {str(e)}")
    
    logger.info("InnoCore AI 启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭InnoCore AI...")
    await agent_controller.shutdown()
    await db_manager.close()
    await vector_store_manager.close()
    logger.info("InnoCore AI已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="InnoCore AI API",
    description="智能科研创新助手API",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS
config = get_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(papers.router, prefix="/api/v1/papers", tags=["papers"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(writing.router, prefix="/api/v1/writing", tags=["writing"])
app.include_router(citations.router, prefix="/api/v1/citations", tags=["citations"])
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["workflow"])

# 挂载静态文件
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# 挂载静态资源
if os.path.exists(os.path.join(FRONTEND_DIR, "static")):
    app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# 根路径 - 返回前端页面
@app.get("/")
async def root():
    """根路径 - 返回前端首页"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Welcome to InnoCore AI API",
        "version": "0.1.0",
        "status": "running"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查各组件状态
        agent_status = await agent_controller.get_agent_status()
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "components": {
                "database": "connected",
                "vector_store": "connected",
                "agents": agent_status
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"全局异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if config.debug else "Something went wrong"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "innocore_ai.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.debug,
        log_level="info"
    )