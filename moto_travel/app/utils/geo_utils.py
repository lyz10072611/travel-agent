"""
地理工具
提供地理计算和坐标处理功能
"""
from typing import Tuple
from geopy.distance import geodesic


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """计算两点间距离（公里）"""
    return geodesic(point1, point2).kilometers


def is_valid_coordinates(longitude: float, latitude: float) -> bool:
    """验证坐标有效性"""
    return -180 <= longitude <= 180 and -90 <= latitude <= 90


def format_coordinates(longitude: float, latitude: float) -> str:
    """格式化坐标显示"""
    return f"{longitude:.6f},{latitude:.6f}"


def parse_coordinates(coord_string: str) -> Tuple[float, float]:
    """解析坐标字符串"""
    try:
        parts = coord_string.split(",")
        if len(parts) == 2:
            longitude = float(parts[0].strip())
            latitude = float(parts[1].strip())
            if is_valid_coordinates(longitude, latitude):
                return (longitude, latitude)
    except (ValueError, IndexError):
        pass
    raise ValueError(f"Invalid coordinates: {coord_string}")


def calculate_bearing(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """计算方位角"""
    return geodesic(point1, point2).bearing


def is_point_in_china(longitude: float, latitude: float) -> bool:
    """判断点是否在中国境内"""
    # 中国大致边界
    return (73 <= longitude <= 135 and 18 <= latitude <= 54)

