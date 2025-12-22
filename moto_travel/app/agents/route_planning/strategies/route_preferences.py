"""
路线规划用户偏好配置
支持灵活的路由策略配置
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum


class HighwayPreference(Enum):
    """高速公路偏好"""
    ALLOW = "allow"  # 允许走高速
    PREFER = "prefer"  # 优先走高速
    AVOID = "avoid"  # 避开高速
    FORBID = "forbid"  # 禁止走高速


class RoadTypePreference(Enum):
    """道路类型偏好"""
    PREFER = "prefer"  # 优先
    NEUTRAL = "neutral"  # 中性
    AVOID = "avoid"  # 避开


@dataclass
class RoutePreferences:
    """路线规划偏好配置"""
    
    # 高速公路偏好（默认允许，不是必须避开）
    highway_preference: HighwayPreference = HighwayPreference.ALLOW
    
    # 道路类型偏好（晚上时段）
    avoid_national_road_at_night: bool = True  # 晚上避开国道（默认开启）
    night_start_time: time = time(18, 0)  # 晚上开始时间（18:00，可配置）
    night_end_time: time = time(6, 0)  # 晚上结束时间（次日6:00，可配置）
    
    # 道路类型偏好
    national_road_preference: RoadTypePreference = RoadTypePreference.NEUTRAL
    provincial_road_preference: RoadTypePreference = RoadTypePreference.PREFER
    city_road_preference: RoadTypePreference = RoadTypePreference.NEUTRAL
    
    # 其他偏好
    prefer_scenic_route: bool = False  # 优先风景路线
    avoid_tolls: bool = False  # 避开收费路段
    fuel_range_km: int = 300  # 续航里程
    
    # 时间相关
    departure_time: Optional[datetime] = None  # 出发时间
    estimated_arrival_time: Optional[datetime] = None  # 预计到达时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "highway_preference": self.highway_preference.value,
            "avoid_national_road_at_night": self.avoid_national_road_at_night,
            "night_start_time": self.night_start_time.strftime("%H:%M"),
            "night_end_time": self.night_end_time.strftime("%H:%M"),
            "national_road_preference": self.national_road_preference.value,
            "provincial_road_preference": self.provincial_road_preference.value,
            "city_road_preference": self.city_road_preference.value,
            "prefer_scenic_route": self.prefer_scenic_route,
            "avoid_tolls": self.avoid_tolls,
            "fuel_range_km": self.fuel_range_km,
            "departure_time": self.departure_time.isoformat() if self.departure_time else None,
            "estimated_arrival_time": self.estimated_arrival_time.isoformat() if self.estimated_arrival_time else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoutePreferences":
        """从字典创建"""
        prefs = cls()
        
        if "highway_preference" in data:
            prefs.highway_preference = HighwayPreference(data["highway_preference"])
        if "avoid_national_road_at_night" in data:
            prefs.avoid_national_road_at_night = data["avoid_national_road_at_night"]
        if "night_start_time" in data:
            prefs.night_start_time = datetime.strptime(data["night_start_time"], "%H:%M").time()
        if "night_end_time" in data:
            prefs.night_end_time = datetime.strptime(data["night_end_time"], "%H:%M").time()
        if "national_road_preference" in data:
            prefs.national_road_preference = RoadTypePreference(data["national_road_preference"])
        if "provincial_road_preference" in data:
            prefs.provincial_road_preference = RoadTypePreference(data["provincial_road_preference"])
        if "city_road_preference" in data:
            prefs.city_road_preference = RoadTypePreference(data["city_road_preference"])
        if "prefer_scenic_route" in data:
            prefs.prefer_scenic_route = data["prefer_scenic_route"]
        if "avoid_tolls" in data:
            prefs.avoid_tolls = data["avoid_tolls"]
        if "fuel_range_km" in data:
            prefs.fuel_range_km = data["fuel_range_km"]
        if "departure_time" in data and data["departure_time"]:
            prefs.departure_time = datetime.fromisoformat(data["departure_time"])
        if "estimated_arrival_time" in data and data["estimated_arrival_time"]:
            prefs.estimated_arrival_time = datetime.fromisoformat(data["estimated_arrival_time"])
        
        return prefs
    
    def is_night_time(self, check_time: Optional[datetime] = None) -> bool:
        """判断是否为晚上时段"""
        if not check_time:
            check_time = datetime.now()
        
        current_time = check_time.time()
        
        # 处理跨天的情况（如18:00-次日6:00）
        if self.night_start_time > self.night_end_time:
            # 跨天：18:00-次日6:00
            return current_time >= self.night_start_time or current_time <= self.night_end_time
        else:
            # 不跨天：如22:00-6:00（这种情况较少）
            return self.night_start_time <= current_time <= self.night_end_time
    
    def should_avoid_national_road(self, check_time: Optional[datetime] = None) -> bool:
        """判断是否应该避开国道"""
        if not self.avoid_national_road_at_night:
            return False
        
        return self.is_night_time(check_time)
    
    def get_highway_strategy(self) -> int:
        """获取高速公路策略（高德地图）"""
        # 高德地图策略：0=速度优先, 1=费用优先, 2=距离优先, 3=不走高速
        if self.highway_preference == HighwayPreference.FORBID:
            return 3  # 不走高速
        elif self.highway_preference == HighwayPreference.AVOID:
            return 1  # 费用优先（通常避开高速）
        elif self.highway_preference == HighwayPreference.PREFER:
            return 0  # 速度优先（通常走高速）
        else:  # ALLOW
            return 0  # 速度优先（允许但不强制）
    
    def get_highway_tactics(self) -> int:
        """获取高速公路策略（百度地图）"""
        # 百度地图策略：11=不走高速, 12=最短时间, 13=最短距离
        if self.highway_preference == HighwayPreference.FORBID:
            return 11  # 不走高速
        elif self.highway_preference == HighwayPreference.AVOID:
            return 13  # 最短距离（通常避开高速）
        elif self.highway_preference == HighwayPreference.PREFER:
            return 12  # 最短时间（通常走高速）
        else:  # ALLOW
            return 12  # 最短时间（允许但不强制）


class PreferenceQuestionnaire:
    """偏好问卷 - 用于交互式询问用户偏好"""
    
    @staticmethod
    def get_required_questions() -> List[Dict[str, Any]]:
        """获取必须询问的问题（核心偏好）"""
        return [
            {
                "key": "highway_preference",
                "question": "您对高速公路的偏好是什么？",
                "type": "choice",
                "options": [
                    {"value": "allow", "label": "允许走高速（默认，灵活选择）"},
                    {"value": "prefer", "label": "优先走高速（快速）"},
                    {"value": "avoid", "label": "尽量避开高速（安全）"},
                    {"value": "forbid", "label": "禁止走高速（严格）"}
                ],
                "default": "allow",
                "required": False,
                "description": "注意：避开高速不是必须的，您可以根据实际情况灵活选择"
            },
            {
                "key": "departure_time",
                "question": "您计划什么时候出发？（格式：YYYY-MM-DD HH:MM，留空则使用当前时间）",
                "type": "datetime",
                "required": False,
                "description": "用于计算晚上时段，避免晚上走国道"
            },
            {
                "key": "fuel_range_km",
                "question": "您的摩托车续航里程是多少公里？（默认300km）",
                "type": "number",
                "default": 300,
                "required": False,
                "description": "用于规划加油站位置"
            }
        ]
    
    @staticmethod
    def get_optional_questions() -> List[Dict[str, Any]]:
        """获取可选询问的问题（高级偏好）"""
        return [
            {
                "key": "avoid_national_road_at_night",
                "question": "晚上是否避开国道？（默认：是）",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "晚上（18:00-次日6:00）尽量远离国道，提高安全性"
            },
            {
                "key": "night_start_time",
                "question": "晚上时段开始时间（格式：HH:MM，默认18:00）",
                "type": "time",
                "default": "18:00",
                "required": False,
                "description": "用于判断晚上时段，避开国道"
            },
            {
                "key": "night_end_time",
                "question": "晚上时段结束时间（格式：HH:MM，默认06:00）",
                "type": "time",
                "default": "06:00",
                "required": False,
                "description": "用于判断晚上时段，避开国道"
            },
            {
                "key": "prefer_scenic_route",
                "question": "是否优先选择风景路线？",
                "type": "boolean",
                "default": False,
                "required": False
            },
            {
                "key": "avoid_tolls",
                "question": "是否避开收费路段？",
                "type": "boolean",
                "default": False,
                "required": False
            },
            {
                "key": "national_road_preference",
                "question": "您对国道的偏好是什么？",
                "type": "choice",
                "options": [
                    {"value": "neutral", "label": "中性（默认）"},
                    {"value": "prefer", "label": "优先走国道"},
                    {"value": "avoid", "label": "避开国道"}
                ],
                "default": "neutral",
                "required": False,
                "description": "注意：晚上时段会自动避开国道（如果开启了该选项）"
            },
            {
                "key": "provincial_road_preference",
                "question": "您对省道的偏好是什么？",
                "type": "choice",
                "options": [
                    {"value": "prefer", "label": "优先走省道（默认）"},
                    {"value": "neutral", "label": "中性"},
                    {"value": "avoid", "label": "避开省道"}
                ],
                "default": "prefer",
                "required": False
            }
        ]
    
    @staticmethod
    def parse_answers(answers: Dict[str, Any]) -> RoutePreferences:
        """解析用户答案，创建偏好配置"""
        prefs = RoutePreferences()
        
        # 高速公路偏好
        if "highway_preference" in answers:
            prefs.highway_preference = HighwayPreference(answers["highway_preference"])
        
        # 出发时间
        if "departure_time" in answers and answers["departure_time"]:
            try:
                prefs.departure_time = datetime.strptime(answers["departure_time"], "%Y-%m-%d %H:%M")
            except:
                pass
        
        # 续航里程
        if "fuel_range_km" in answers:
            prefs.fuel_range_km = int(answers["fuel_range_km"])
        
        # 晚上避开国道
        if "avoid_national_road_at_night" in answers:
            prefs.avoid_national_road_at_night = bool(answers["avoid_national_road_at_night"])
        
        # 晚上时段时间（可配置）
        if "night_start_time" in answers:
            try:
                prefs.night_start_time = datetime.strptime(answers["night_start_time"], "%H:%M").time()
            except:
                pass
        
        if "night_end_time" in answers:
            try:
                prefs.night_end_time = datetime.strptime(answers["night_end_time"], "%H:%M").time()
            except:
                pass
        
        # 道路类型偏好
        if "national_road_preference" in answers:
            prefs.national_road_preference = RoadTypePreference(answers["national_road_preference"])
        
        if "provincial_road_preference" in answers:
            prefs.provincial_road_preference = RoadTypePreference(answers["provincial_road_preference"])
        
        # 风景路线
        if "prefer_scenic_route" in answers:
            prefs.prefer_scenic_route = bool(answers["prefer_scenic_route"])
        
        # 避开收费
        if "avoid_tolls" in answers:
            prefs.avoid_tolls = bool(answers["avoid_tolls"])
        
        return prefs

