"""
应用配置管理
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "摩旅智能助手"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # 数据库配置
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    
    # AI模型配置
    qwen_api_key: str = Field(..., env="QWEN_API_KEY")
    qwen_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        env="QWEN_BASE_URL"
    )
    qwen_model: str = Field(default="qwen-plus", env="QWEN_MODEL")
    
    # 地图服务配置
    amap_api_key: str = Field(..., env="AMAP_API_KEY")
    amap_web_service_url: str = Field(
        default="https://restapi.amap.com/v3",
        env="AMAP_WEB_SERVICE_URL"
    )
    
    # 百度地图配置
    baidu_api_key: Optional[str] = Field(default=None, env="BAIDU_API_KEY")
    baidu_web_service_url: str = Field(
        default="https://api.map.baidu.com",
        env="BAIDU_WEB_SERVICE_URL"
    )
    
    # 天气服务配置
    qweather_api_key: str = Field(..., env="QWEATHER_API_KEY")
    qweather_base_url: str = Field(
        default="https://devapi.qweather.com/v7",
        env="QWEATHER_BASE_URL"
    )
    
    # 第三方服务配置
    meituan_api_key: Optional[str] = Field(default=None, env="MEITUAN_API_KEY")
    meituan_app_secret: Optional[str] = Field(default=None, env="MEITUAN_APP_SECRET")
    meituan_base_url: str = Field(
        default="https://openapi.meituan.com",
        env="MEITUAN_BASE_URL"
    )
    ctrip_api_key: Optional[str] = Field(default=None, env="CTRIP_API_KEY")
    ctrip_base_url: str = Field(
        default="https://openapi.ctrip.com",
        env="CTRIP_BASE_URL"
    )
    tongcheng_api_key: Optional[str] = Field(default=None, env="TONGCHENG_API_KEY")
    tongcheng_base_url: str = Field(
        default="https://openapi.ly.com",
        env="TONGCHENG_BASE_URL"
    )
    qunar_api_key: Optional[str] = Field(default=None, env="QUNAR_API_KEY")
    qunar_base_url: str = Field(
        default="https://openapi.qunar.com",
        env="QUNAR_BASE_URL"
    )
    fliggy_api_key: Optional[str] = Field(default=None, env="FLIGGY_API_KEY")
    fliggy_base_url: str = Field(
        default="https://openapi.fliggy.com",
        env="FLIGGY_BASE_URL"
    )
    dianping_api_key: Optional[str] = Field(default=None, env="DIANPING_API_KEY")
    
    # 安全配置
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    
    # 缓存配置
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    weather_cache_ttl: int = Field(default=1800, env="WEATHER_CACHE_TTL")
    route_cache_ttl: int = Field(default=7200, env="ROUTE_CACHE_TTL")
    
    # 限流配置
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    api_rate_limit_per_hour: int = Field(default=1000, env="API_RATE_LIMIT_PER_HOUR")
    
    # 摩旅专用配置
    default_daily_distance: int = Field(default=300, env="DEFAULT_DAILY_DISTANCE")
    max_daily_distance: int = Field(default=800, env="MAX_DAILY_DISTANCE")
    min_daily_distance: int = Field(default=100, env="MIN_DAILY_DISTANCE")
    
    # 摩托车配置
    default_fuel_consumption: float = Field(default=4.5, env="DEFAULT_FUEL_CONSUMPTION")  # L/100km
    default_speed: int = Field(default=60, env="DEFAULT_SPEED")  # km/h
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
