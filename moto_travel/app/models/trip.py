"""
旅行相关模型
"""
from sqlalchemy import Column, String, Text, JSON, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import uuid


class Trip(BaseModel):
    """旅行模型"""
    __tablename__ = "trips"
    
    # 基本信息
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 路线信息
    start_location = Column(String(100), nullable=False)
    end_location = Column(String(100), nullable=False)
    waypoints = Column(JSON, default=[])  # 途经点
    route_geojson = Column(JSON, nullable=True)  # 路线GeoJSON数据
    
    # 时间信息
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    planned_duration = Column(Integer, nullable=True)  # 计划天数
    
    # 距离和预算
    total_distance = Column(Float, nullable=True)  # 总距离(公里)
    estimated_budget = Column(Float, nullable=True)  # 预估预算
    actual_budget = Column(Float, nullable=True)  # 实际预算
    
    # 状态
    status = Column(String(20), default="planning")  # planning, active, completed, cancelled
    is_public = Column(Boolean, default=False)  # 是否公开
    
    # 偏好设置
    preferences = Column(JSON, default={})
    
    # 关系
    user = relationship("User", back_populates="trips")
    days = relationship("TripDay", back_populates="trip", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Trip(title={self.title}, status={self.status})>"


class TripDay(BaseModel):
    """旅行日程模型"""
    __tablename__ = "trip_days"
    
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, index=True)
    day_index = Column(Integer, nullable=False)  # 第几天
    
    # 路线信息
    start_location = Column(String(100), nullable=False)
    end_location = Column(String(100), nullable=False)
    distance = Column(Float, nullable=True)  # 当日距离
    duration = Column(Integer, nullable=True)  # 当日时长(分钟)
    
    # 住宿信息
    accommodation = Column(JSON, nullable=True)  # 住宿推荐
    accommodation_booked = Column(Boolean, default=False)  # 是否已预订
    
    # 餐饮信息
    restaurants = Column(JSON, default=[])  # 餐厅推荐
    meals_planned = Column(JSON, default=[])  # 餐饮计划
    
    # 景点信息
    attractions = Column(JSON, default=[])  # 景点推荐
    activities = Column(JSON, default=[])  # 活动安排
    
    # 服务信息
    gas_stations = Column(JSON, default=[])  # 加油站
    repair_shops = Column(JSON, default=[])  # 修车行
    medical_facilities = Column(JSON, default=[])  # 医疗设施
    
    # 天气信息
    weather_forecast = Column(JSON, nullable=True)  # 天气预报
    weather_alerts = Column(JSON, default=[])  # 天气预警
    
    # 预算信息
    daily_budget = Column(Float, nullable=True)  # 当日预算
    actual_cost = Column(Float, nullable=True)  # 实际花费
    
    # 备注
    notes = Column(Text, nullable=True)
    
    # 关系
    trip = relationship("Trip", back_populates="days")
    segments = relationship("TripSegment", back_populates="day", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TripDay(trip_id={self.trip_id}, day_index={self.day_index})>"


class TripSegment(BaseModel):
    """旅行路段模型"""
    __tablename__ = "trip_segments"
    
    day_id = Column(UUID(as_uuid=True), ForeignKey("trip_days.id"), nullable=False, index=True)
    segment_index = Column(Integer, nullable=False)  # 路段序号
    
    # 路线信息
    start_location = Column(String(100), nullable=False)
    end_location = Column(String(100), nullable=False)
    distance = Column(Float, nullable=True)  # 路段距离
    duration = Column(Integer, nullable=True)  # 路段时长
    
    # 路线详情
    route_steps = Column(JSON, default=[])  # 路线步骤
    road_type = Column(String(50), nullable=True)  # 道路类型
    difficulty_level = Column(String(20), default="普通")  # 难度等级
    
    # 安全信息
    safety_notes = Column(Text, nullable=True)  # 安全提醒
    hazards = Column(JSON, default=[])  # 危险因素
    restrictions = Column(JSON, default=[])  # 限制条件
    
    # 服务信息
    poi_along_route = Column(JSON, default=[])  # 沿途POI
    
    # 关系
    day = relationship("TripDay", back_populates="segments")
    
    def __repr__(self):
        return f"<TripSegment(day_id={self.day_id}, segment_index={self.segment_index})>"
