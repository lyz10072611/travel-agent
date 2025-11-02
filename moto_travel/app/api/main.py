"""
FastAPI主应用
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from app.config import settings
from app.database import init_database, check_database_health
from app.api.routes import router
from app.api.websocket import websocket_manager, websocket_endpoint
from app.langchain_integration import LangChainIntegration


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("Starting Moto Travel Agent API...")
    
    try:
        # 初始化数据库
        init_database()
        logger.info("Database initialized successfully")
        
        # 检查数据库健康状态
        if not check_database_health():
            raise Exception("Database health check failed")
        
        # 初始化LangChain集成
        app.state.langchain_integration = LangChainIntegration()
        logger.info("LangChain integration initialized successfully")
        
        logger.info("Moto Travel Agent API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("Shutting down Moto Travel Agent API...")
    # 这里可以添加清理逻辑


# 创建FastAPI应用
app = FastAPI(
    title="摩旅智能助手API",
    description="基于AI的摩托车旅行规划助手API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加信任主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 生产环境中应该限制具体主机
)

# 包含路由
app.include_router(router, prefix="/api/v1")

# 添加WebSocket路由
app.add_websocket_route("/ws", websocket_endpoint)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "摩旅智能助手API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        db_healthy = check_database_health()
        
        # 检查LangChain集成
        langchain_healthy = hasattr(app.state, 'langchain_integration')
        
        if db_healthy and langchain_healthy:
            return {
                "status": "healthy",
                "database": "connected",
                "langchain": "initialized",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unhealthy"
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "服务器内部错误，请稍后重试",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )