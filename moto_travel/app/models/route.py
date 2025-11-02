"""
路线相关模型
"""
from sqlalchemy import Column, String, Text, JSON, Integer, Float, DateTime, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import uuid


class Route(BaseModel):
    """路线模型"""
    __tablename__ = "routes"
    
    # 基本信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 路线信息
    start_location = Column(String(100), nullable=False)
    end_location = Column(String(100), nullable=False)
    waypoints = Column(JSON, default=[])  # 途经点
    
    # 距离和时间
    total_distance = Column(Float, nullable=True)  # 总距离(公里)
    total_duration = Column(Integer, nullable=True)  # 总时长(分钟)
    estimated_duration = Column(Integer, nullable=True)  # 预估时长(分钟)
    
    # 路线数据
    route_geojson = Column(JSON, nullable=True)  # 路线GeoJSON
    route_steps = Column(JSON, default=[])  # 路线步骤
    route_polyline = Column(Text, nullable=True)  # 路线折线
    
    # 路线属性
    route_type = Column(String(50), nullable=True)  # 路线类型
    difficulty_level = Column(String(20), default="普通")  # 难度等级
    scenic_rating = Column(String(20), nullable=True)  # 风景评分
    
    # 道路信息
    road_types = Column(JSON, default=[])  # 道路类型分布
    highway_percentage = Column(Float, nullable=True)  # 高速占比
    toll_cost = Column(Float, nullable=True)  # 过路费
    
    # 摩托车相关
    motorcycle_friendly = Column(Boolean, default=True)  # 是否适合摩托车
    avoid_highway = Column(Boolean, default=False)  # 是否避开高速
    off_road_segments = Column(JSON, default=[])  # 非铺装路段
    
    # 安全信息
    safety_score = Column(Float, nullable=True)  # 安全评分
    hazards = Column(JSON, default=[])  # 危险因素
    restrictions = Column(JSON, default=[])  # 限制条件
    
    # 服务信息
    gas_stations = Column(JSON, default=[])  # 加油站
    repair_shops = Column(JSON, default=[])  # 修车行
    accommodations = Column(JSON, default=[])  # 住宿
    restaurants = Column(JSON, default=[])  # 餐厅
    
    # 景点信息
    attractions = Column(JSON, default=[])  # 景点
    scenic_spots = Column(JSON, default=[])  # 观景点
    
    # 数据来源
    source = Column(String(50), nullable=False)  # 数据来源
    source_id = Column(String(100), nullable=True)  # 来源ID
    
    # 使用统计
    usage_count = Column(Integer, default=0)  # 使用次数
    rating = Column(Float, nullable=True)  # 用户评分
    review_count = Column(Integer, default=0)  # 评价次数
    
    # 状态
    is_public = Column(Boolean, default=False)  # 是否公开
    is_verified = Column(Boolean, default=False)  # 是否已验证
    is_active = Column(Boolean, default=True)  # 是否活跃
    
    # 扩展信息
    metadata = Column(JSON, default={})  # 扩展元数据
    tags = Column(JSON, default=[])  # 标签
    
    # 创建索引
    __table_args__ = (
        Index('idx_route_locations', 'start_location', 'end_location'),
        Index('idx_route_type_difficulty', 'route_type', 'difficulty_level'),
        Index('idx_route_motorcycle', 'motorcycle_friendly', 'avoid_highway'),
    )
    
    def __repr__(self):
        return f"<Route(name={self.name}, distance={self.total_distance}km)>"


class RouteSegment(BaseModel):
    """路线路段模型"""
    __tablename__ = "route_segments"
    
    route_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    segment_index = Column(Integer, nullable=False)  # 路段序号
    
    # 位置信息
    start_location = Column(String(100), nullable=False)
    end_location = Column(String(100), nullable=False)
    start_coords = Column(JSON, nullable=True)  # 起点坐标
    end_coords = Column(JSON, nullable=True)  # 终点坐标
    
    # 距离和时间
    distance = Column(Float, nullable=True)  # 路段距离(公里)
    duration = Column(Integer, nullable=True)  # 路段时长(分钟)
    
    # 路线详情
    instruction = Column(Text, nullable=True)  # 导航指令
    road_name = Column(String(200), nullable=True)  # 道路名称
    road_type = Column(String(50), nullable=True)  # 道路类型
    action = Column(String(50), nullable=True)  # 动作类型
    
    # 路线数据
    polyline = Column(Text, nullable=True)  # 路段折线
    steps = Column(JSON, default=[])  # 详细步骤
    
    # 道路属性
    is_highway = Column(Boolean, default=False)  # 是否高速
    is_toll_road = Column(Boolean, default=False)  # 是否收费
    lane_count = Column(Integer, nullable=True)  # 车道数
    speed_limit = Column(Integer, nullable=True)  # 限速
    
    # 安全信息
    safety_notes = Column(Text, nullable=True)  # 安全提醒
    hazards = Column(JSON, default=[])  # 危险因素
    weather_sensitivity = Column(String(20), default="普通")  # 天气敏感性
    
    # 服务信息
    poi_along_segment = Column(JSON, default=[])  # 沿途POI
    
    # 摩托车相关
    motorcycle_suitable = Column(Boolean, default=True)  # 是否适合摩托车
    off_road_percentage = Column(Float, default=0.0)  # 非铺装路占比
    
    def __repr__(self):
        return f"<RouteSegment(route_id={self.route_id}, segment_index={self.segment_index})>"
