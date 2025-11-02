"""
记忆相关模型
"""
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from .base import BaseModel
import uuid
from enum import Enum


class MemoryType(Enum):
    """记忆类型枚举"""
    PREFERENCE = "preference"  # 用户偏好
    EXPERIENCE = "experience"  # 旅行经验
    FEEDBACK = "feedback"  # 用户反馈
    KNOWLEDGE = "knowledge"  # 知识库
    ROUTE = "route"  # 路线记忆
    POI = "poi"  # POI记忆


class Memory(BaseModel):
    """记忆模型"""
    __tablename__ = "memories"
    
    # 基本信息
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)  # 可为空，支持系统级记忆
    memory_type = Column(String(50), nullable=False, index=True)
    
    # 内容信息
    content_text = Column(Text, nullable=False)  # 文本内容
    embedding = Column(JSON, nullable=True)  # 向量嵌入
    metadata = Column(JSON, default={})  # 元数据
    
    # 关联信息
    related_trip_id = Column(UUID(as_uuid=True), nullable=True)  # 关联的旅行ID
    related_poi_id = Column(UUID(as_uuid=True), nullable=True)  # 关联的POI ID
    
    # 权重和重要性
    importance_score = Column(String(20), default="medium")  # 重要性评分
    confidence_score = Column(String(20), default="medium")  # 置信度评分
    
    # 使用统计
    access_count = Column(String(20), default="0")  # 访问次数
    last_accessed = Column(DateTime, nullable=True)  # 最后访问时间
    
    # 状态
    is_active = Column(String(20), default="true")  # 是否活跃
    is_public = Column(String(20), default="false")  # 是否公开
    
    # 关系
    user = relationship("User", back_populates="memories")
    
    # 创建索引
    __table_args__ = (
        Index('idx_memory_type_user', 'memory_type', 'user_id'),
        Index('idx_memory_embedding', 'embedding', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<Memory(type={self.memory_type}, user_id={self.user_id})>"
