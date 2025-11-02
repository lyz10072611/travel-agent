"""
使用SQLAlchemy连接PostgreSQL的数据库服务模块。

此模块提供使用SQLAlchemy连接PostgreSQL数据库的工具，
包括连接池、会话管理和适当的资源管理上下文管理器。
"""

import os
from typing import Any, AsyncGenerator, Dict, Optional
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from loguru import logger

# 从环境变量获取数据库连接字符串
# 如果需要，将psycopg转换为SQLAlchemy格式
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL.startswith("postgresql://"):
    # 转换为SQLAlchemy异步的asyncpg格式
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# 全局引擎和会话工厂
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

async def initialize_db_pool(pool_size: int = 10, max_overflow: int = 20) -> None:
    """初始化SQLAlchemy引擎和会话工厂。

    参数:
        pool_size: 连接池的池大小
        max_overflow: 可以创建的超出池大小的最大连接数
    """
    global _engine, _session_factory
    if _engine is not None:
        return

    logger.info("正在初始化SQLAlchemy引擎和会话工厂")

    try:
        _engine = create_async_engine(
            DATABASE_URL,
            echo=False,  # 设置为True以记录SQL查询日志
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # 在使用连接前验证连接
        )

        _session_factory = async_sessionmaker(
            _engine,
            expire_on_commit=False,
            autoflush=False,
        )

        # 测试连接
        async with _session_factory() as session:
            await session.execute(text("SELECT 1"))

        logger.info("SQLAlchemy引擎和会话工厂已成功初始化")
    except Exception as e:
        logger.error(f"初始化SQLAlchemy引擎和会话工厂失败: {e}")
        raise

async def close_db_pool() -> None:
    """关闭SQLAlchemy引擎和连接池。"""
    global _engine
    if _engine is not None:
        logger.info("正在关闭SQLAlchemy引擎和连接池")
        await _engine.dispose()
        _engine = None

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取用于数据库操作的SQLAlchemy会话。

    返回:
        AsyncSession: SQLAlchemy异步会话

    示例:
        ```python
        async with get_db_session() as session:
            result = await session.execute(text("SELECT * FROM users"))
            users = result.fetchall()
        ```
    """
    if _session_factory is None:
        await initialize_db_pool()

    async with _session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话操作失败: {e}")
            raise

async def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> list:
    """执行数据库查询并返回结果。

    参数:
        query: 要执行的SQL查询（原始SQL）
        params: 查询参数（用于参数化查询）

    返回:
        list: 查询结果

    示例:
        ```python
        results = await execute_query(
            "SELECT * FROM users WHERE email = :email",
            {"email": "user@example.com"}
        )
        ```
    """
    async with get_db_session() as session:
        try:
            result = await session.execute(text(query), params or {})
            try:
                return result.fetchall()
            except Exception:
                # 没有结果可获取
                return []
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            raise