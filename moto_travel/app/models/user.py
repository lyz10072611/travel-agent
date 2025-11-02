"""
用户相关模型
"""
from sqlalchemy import Column, String, Text, JSON, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import uuid


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    # 基本信息
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    nickname = Column(String(50), nullable=True)
    
    # 认证信息
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # 用户偏好
    preferences = Column(JSON, default={})
    
    # 关系
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"


class UserPreferences(BaseModel):
    """用户偏好模型"""
    __tablename__ = "user_preferences"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # 摩旅偏好
    daily_distance_min = Column(String(20), default="300")  # 最小日行距离
    daily_distance_max = Column(String(20), default="500")  # 最大日行距离
    preferred_route_type = Column(String(50), default="自然风光")  # 偏好路线类型
    avoid_highway = Column(Boolean, default=False)  # 是否避开高速
    night_riding = Column(Boolean, default=False)  # 是否接受夜骑
    
    # 住宿偏好
    accommodation_type = Column(String(50), default="经济型")  # 住宿类型
    accommodation_budget_min = Column(String(20), default="100")  # 住宿预算下限
    accommodation_budget_max = Column(String(20), default="300")  # 住宿预算上限
    
    # 餐饮偏好
    cuisine_preference = Column(JSON, default=[])  # 餐饮偏好
    meal_budget_min = Column(String(20), default="50")  # 餐饮预算下限
    meal_budget_max = Column(String(20), default="150")  # 餐饮预算上限
    
    # 装备偏好
    equipment_level = Column(String(20), default="基础")  # 装备等级
    safety_priority = Column(String(20), default="中等")  # 安全优先级
    
    # 其他偏好
    travel_style = Column(String(50), default="休闲")  # 旅行风格
    group_size = Column(String(20), default="1-2人")  # 团队规模
    season_preference = Column(JSON, default=[])  # 季节偏好
    
    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id})>"
