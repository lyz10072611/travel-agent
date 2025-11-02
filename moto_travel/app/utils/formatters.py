"""
格式化工具
提供数据格式化功能
"""
from typing import Union


def format_distance(distance_meters: Union[int, float]) -> str:
    """格式化距离显示"""
    if distance_meters < 1000:
        return f"{distance_meters:.0f}米"
    else:
        return f"{distance_meters / 1000:.1f}公里"


def format_duration(duration_seconds: Union[int, float]) -> str:
    """格式化时长显示"""
    if duration_seconds < 60:
        return f"{duration_seconds:.0f}秒"
    elif duration_seconds < 3600:
        return f"{duration_seconds / 60:.1f}分钟"
    else:
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"


def format_currency(amount: Union[int, float], currency: str = "CNY") -> str:
    """格式化货币显示"""
    if currency == "CNY":
        return f"¥{amount:.2f}"
    elif currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"


def format_percentage(value: Union[int, float], total: Union[int, float]) -> str:
    """格式化百分比显示"""
    if total == 0:
        return "0%"
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"


def format_rating(rating: Union[int, float]) -> str:
    """格式化评分显示"""
    return f"{rating:.1f}/5.0"


def format_coordinates(longitude: float, latitude: float) -> str:
    """格式化坐标显示"""
    return f"({longitude:.6f}, {latitude:.6f})"


def format_address(province: str, city: str, district: str, detail: str = "") -> str:
    """格式化地址显示"""
    address_parts = [province, city, district, detail]
    return "".join([part for part in address_parts if part])

