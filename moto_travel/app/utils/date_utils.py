"""
日期时间工具
提供日期时间处理功能
"""
from datetime import datetime, timedelta
from typing import Optional
import pytz


def parse_date(date_string: str) -> datetime:
    """解析日期字符串"""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%Y/%m/%d %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_string}")


def format_date(dt: datetime, format_string: str = "%Y-%m-%d") -> str:
    """格式化日期显示"""
    return dt.strftime(format_string)


def calculate_duration(start_time: datetime, end_time: datetime) -> timedelta:
    """计算时间间隔"""
    return end_time - start_time


def add_days_to_date(date: datetime, days: int) -> datetime:
    """日期加减"""
    return date + timedelta(days=days)


def get_current_time_utc() -> datetime:
    """获取当前UTC时间"""
    return datetime.utcnow()


def get_current_time_beijing() -> datetime:
    """获取当前北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz)


def format_duration(duration: timedelta) -> str:
    """格式化时长显示"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}小时{minutes}分钟"
    elif minutes > 0:
        return f"{minutes}分钟{seconds}秒"
    else:
        return f"{seconds}秒"


def is_business_hours(dt: datetime, start_hour: int = 9, end_hour: int = 18) -> bool:
    """判断是否在营业时间内"""
    return start_hour <= dt.hour < end_hour and dt.weekday() < 5

