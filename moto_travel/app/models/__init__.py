"""
数据模型包
"""
from .user import User, UserPreferences
from .trip import Trip, TripDay, TripSegment
from .poi import POI, POICategory
from .memory import Memory, MemoryType
from .alert import Alert, AlertType
from .route import Route, RouteSegment

__all__ = [
    "User",
    "UserPreferences", 
    "Trip",
    "TripDay",
    "TripSegment",
    "POI",
    "POICategory",
    "Memory",
    "MemoryType",
    "Alert",
    "AlertType",
    "Route",
    "RouteSegment"
]
