"""
POI相关模型
"""
from sqlalchemy import Column, String, Text, JSON, Float, Integer, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import uuid


class POI(BaseModel):
    """POI模型"""
    __tablename__ = "pois"
    
    # 基本信息
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True)
    
    # 位置信息
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    address = Column(String(500), nullable=True)
    province = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    
    # 联系信息
    phone = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    email = Column(String(100), nullable=True)
    
    # 评价信息
    rating = Column(Float, nullable=True, default=0.0)
    review_count = Column(Integer, nullable=True, default=0)
    price_level = Column(String(20), nullable=True)  # 价格等级
    
    # 营业信息
    business_hours = Column(JSON, nullable=True)  # 营业时间
    is_24h = Column(Boolean, default=False)  # 是否24小时营业
    
    # 服务信息
    services = Column(JSON, default=[])  # 提供的服务
    facilities = Column(JSON, default=[])  # 设施信息
    payment_methods = Column(JSON, default=[])  # 支付方式
    
    # 媒体信息
    photos = Column(JSON, default=[])  # 照片URL
    videos = Column(JSON, default=[])  # 视频URL
    
    # 数据来源
    source = Column(String(50), nullable=False)  # 数据来源(amap, meituan, etc.)
    source_id = Column(String(100), nullable=True)  # 来源ID
    external_url = Column(String(500), nullable=True)  # 外部链接
    
    # 状态信息
    is_verified = Column(Boolean, default=False)  # 是否已验证
    is_active = Column(Boolean, default=True)  # 是否活跃
    last_updated = Column(DateTime, nullable=True)  # 最后更新时间
    
    # 扩展信息
    metadata = Column(JSON, default={})  # 扩展元数据
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_poi_location', 'longitude', 'latitude'),
        Index('idx_poi_category_location', 'category', 'longitude', 'latitude'),
    )
    
    def __repr__(self):
        return f"<POI(name={self.name}, category={self.category})>"


class POICategory(BaseModel):
    """POI分类模型"""
    __tablename__ = "poi_categories"
    
    # 分类信息
    name = Column(String(50), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 层级信息
    parent_id = Column(UUID(as_uuid=True), nullable=True)  # 父分类ID
    level = Column(Integer, nullable=False, default=1)  # 分类层级
    sort_order = Column(Integer, nullable=False, default=0)  # 排序顺序
    
    # 图标和颜色
    icon = Column(String(100), nullable=True)  # 图标
    color = Column(String(20), nullable=True)  # 颜色
    
    # 搜索关键词
    keywords = Column(JSON, default=[])  # 搜索关键词
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<POICategory(name={self.name}, level={self.level})>"
