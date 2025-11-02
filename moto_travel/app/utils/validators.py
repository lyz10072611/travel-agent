"""
验证器工具
提供各种数据验证功能
"""
import re
from typing import Tuple, Optional


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_coordinates(longitude: float, latitude: float) -> bool:
    """验证坐标有效性"""
    return -180 <= longitude <= 180 and -90 <= latitude <= 90


def validate_distance(distance: float) -> bool:
    """验证距离有效性"""
    return 0 <= distance <= 10000  # 最大10000公里


def validate_duration(duration: int) -> bool:
    """验证时长有效性"""
    return 0 <= duration <= 86400  # 最大24小时（秒）


def validate_budget(budget: float) -> bool:
    """验证预算有效性"""
    return 0 <= budget <= 100000  # 最大10万元


def validate_fuel_consumption(consumption: float) -> bool:
    """验证油耗有效性"""
    return 1.0 <= consumption <= 20.0  # 1-20L/100km


def validate_route_type(route_type: str) -> bool:
    """验证路线类型"""
    valid_types = ["自然风光", "经典摩旅", "历史人文", "探险挑战"]
    return route_type in valid_types


def validate_travel_style(travel_style: str) -> bool:
    """验证旅行风格"""
    valid_styles = ["休闲", "中等", "激情", "探险"]
    return travel_style in valid_styles

