"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.debug,
    future=True
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 导入所有模型以确保它们被注册
from app.models import *


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """设置数据库连接参数"""
    if "postgresql" in settings.database_url:
        # PostgreSQL特定设置
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET timezone TO 'UTC'")
            cursor.execute("SET search_path TO public")
    elif "sqlite" in settings.database_url:
        # SQLite特定设置
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    获取数据库会话上下文管理器
    用于手动管理数据库会话
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """创建所有表"""
    from app.models.base import Base
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def drop_tables():
    """删除所有表"""
    from app.models.base import Base
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


def init_database():
    """初始化数据库"""
    try:
        # 创建表
        create_tables()
        
        # 创建初始数据
        create_initial_data()
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def create_initial_data():
    """创建初始数据"""
    from app.models.poi import POICategory
    from app.models.base import Base
    
    with get_db_session() as db:
        # 创建POI分类
        categories = [
            {
                "name": "restaurant",
                "display_name": "餐饮服务",
                "description": "餐厅、饭店、小吃店等",
                "keywords": ["餐厅", "饭店", "小吃", "美食", "餐馆"],
                "icon": "restaurant",
                "color": "#FF6B6B"
            },
            {
                "name": "hotel",
                "display_name": "住宿服务",
                "description": "酒店、宾馆、民宿等",
                "keywords": ["酒店", "宾馆", "民宿", "旅馆", "住宿"],
                "icon": "hotel",
                "color": "#4ECDC4"
            },
            {
                "name": "gas_station",
                "display_name": "加油站",
                "description": "加油站、加气站等",
                "keywords": ["加油站", "中石化", "中石油", "壳牌", "加气站"],
                "icon": "local_gas_station",
                "color": "#45B7D1"
            },
            {
                "name": "repair_shop",
                "display_name": "修车行",
                "description": "汽车维修、摩托车维修等",
                "keywords": ["修车", "汽修", "摩托车维修", "保养"],
                "icon": "build",
                "color": "#96CEB4"
            },
            {
                "name": "motorcycle_shop",
                "display_name": "摩托车相关",
                "description": "摩托车销售、配件、装备等",
                "keywords": ["摩托车", "机车", "摩配", "头盔", "骑行装备"],
                "icon": "motorcycle",
                "color": "#FFEAA7"
            },
            {
                "name": "medical",
                "display_name": "医疗设施",
                "description": "医院、诊所、药店等",
                "keywords": ["医院", "诊所", "药店", "急救"],
                "icon": "local_hospital",
                "color": "#DDA0DD"
            },
            {
                "name": "scenic_spot",
                "display_name": "景点",
                "description": "旅游景点、公园、风景区等",
                "keywords": ["景点", "景区", "公园", "旅游", "风景"],
                "icon": "landscape",
                "color": "#98D8C8"
            },
            {
                "name": "bank",
                "display_name": "银行",
                "description": "银行、ATM等",
                "keywords": ["银行", "ATM", "取款机"],
                "icon": "account_balance",
                "color": "#F7DC6F"
            }
        ]
        
        for cat_data in categories:
            # 检查是否已存在
            existing = db.query(POICategory).filter_by(name=cat_data["name"]).first()
            if not existing:
                category = POICategory(**cat_data)
                db.add(category)
        
        db.commit()
        logger.info("Initial data created successfully")


# 数据库健康检查
def check_database_health() -> bool:
    """检查数据库连接健康状态"""
    try:
        with get_db_session() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
