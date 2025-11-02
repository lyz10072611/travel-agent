"""
预警相关模型
"""
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import uuid
from enum import Enum


class AlertType(Enum):
    """预警类型枚举"""
    WEATHER = "weather"  # 天气预警
    TRAFFIC = "traffic"  # 交通预警
    SAFETY = "safety"  # 安全预警
    POLICY = "policy"  # 政策预警
    WILDLIFE = "wildlife"  # 野生动物预警
    ROAD_CONDITION = "road_condition"  # 路况预警
    EMERGENCY = "emergency"  # 紧急预警


class Alert(BaseModel):
    """预警模型"""
    __tablename__ = "alerts"
    
    # 基本信息
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    alert_type = Column(String(50), nullable=False, index=True)
    
    # 严重程度
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    priority = Column(String(20), nullable=False, default="medium")  # low, medium, high
    
    # 位置信息
    location = Column(String(200), nullable=True)  # 位置描述
    longitude = Column(String(50), nullable=True)  # 经度
    latitude = Column(String(50), nullable=True)  # 纬度
    radius = Column(String(20), nullable=True)  # 影响半径(公里)
    
    # 时间信息
    start_time = Column(DateTime, nullable=True)  # 开始时间
    end_time = Column(DateTime, nullable=True)  # 结束时间
    effective_duration = Column(String(50), nullable=True)  # 有效时长
    
    # 来源信息
    source = Column(String(100), nullable=False)  # 数据来源
    source_url = Column(String(500), nullable=True)  # 来源URL
    source_id = Column(String(100), nullable=True)  # 来源ID
    
    # 关联信息
    related_trip_id = Column(UUID(as_uuid=True), nullable=True)  # 关联的旅行ID
    related_route_id = Column(UUID(as_uuid=True), nullable=True)  # 关联的路线ID
    
    # 处理信息
    is_processed = Column(Boolean, default=False)  # 是否已处理
    processed_at = Column(DateTime, nullable=True)  # 处理时间
    processed_by = Column(String(100), nullable=True)  # 处理人
    
    # 用户通知
    notified_users = Column(JSON, default=[])  # 已通知的用户列表
    notification_count = Column(String(20), default="0")  # 通知次数
    
    # 扩展信息
    metadata = Column(JSON, default={})  # 扩展元数据
    tags = Column(JSON, default=[])  # 标签
    
    # 状态
    is_active = Column(Boolean, default=True)  # 是否活跃
    is_verified = Column(Boolean, default=False)  # 是否已验证
    
    # 创建索引
    __table_args__ = (
        Index('idx_alert_type_severity', 'alert_type', 'severity'),
        Index('idx_alert_location', 'longitude', 'latitude'),
        Index('idx_alert_time', 'start_time', 'end_time'),
    )
    
    def __repr__(self):
        return f"<Alert(title={self.title}, type={self.alert_type}, severity={self.severity})>"
