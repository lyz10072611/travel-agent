from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from services.db_service import initialize_db_pool, close_db_pool
from router.plan import router as plan_router
from router.workflow import router as workflow_router

router = APIRouter(prefix="/api")


@router.get("/health", summary="API健康检查")
async def health_check():
    logger.debug("健康检查请求")
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动逻辑
    logger.info("API服务器已启动")

    # 初始化数据库连接池
    logger.info("正在初始化数据库连接池")
    await initialize_db_pool()
    logger.info("数据库连接池已初始化")

    yield

    # 关闭逻辑
    # 关闭数据库连接池
    logger.info("正在关闭数据库连接池")
    await close_db_pool()

    logger.info("API服务器正在关闭")


app = FastAPI(
    title="TripCraft AI API",
    description="用于在后台运行智能旅行规划的API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(plan_router)
app.include_router(workflow_router)
