"""
摩旅智能助手输出模板
提供标准化的JSON和Markdown输出格式
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class OutputFormat(Enum):
    """输出格式枚举"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class LocationInfo:
    """位置信息"""
    name: str
    address: str
    coordinates: Dict[str, float]  # {"longitude": 116.397, "latitude": 39.909}
    province: str
    city: str
    district: str


@dataclass
class RouteSegment:
    """路线路段"""
    segment_index: int
    start_location: LocationInfo
    end_location: LocationInfo
    distance_km: float
    duration_minutes: int
    road_type: str
    difficulty_level: str
    safety_notes: List[str]
    poi_along_route: List[Dict[str, Any]]


@dataclass
class DailyRoute:
    """每日路线"""
    day: int
    date: str
    start_location: LocationInfo
    end_location: LocationInfo
    total_distance_km: float
    estimated_duration_hours: float
    segments: List[RouteSegment]
    recommended_stops: List[Dict[str, Any]]
    accommodation: Optional[Dict[str, Any]] = None


@dataclass
class WeatherInfo:
    """天气信息"""
    location: str
    date: str
    temperature: float
    weather_condition: str
    humidity: float
    wind_speed: float
    wind_direction: str
    visibility: float
    safety_score: int
    safety_level: str
    warnings: List[str]
    recommendations: List[str]


@dataclass
class POIInfo:
    """POI信息"""
    id: str
    name: str
    category: str
    location: LocationInfo
    rating: float
    price_level: str
    business_hours: str
    phone: str
    website: str
    description: str
    features: List[str]
    distance_from_route: float


@dataclass
class BudgetItem:
    """预算项目"""
    category: str
    item_name: str
    unit_cost: float
    quantity: int
    total_cost: float
    description: str
    currency: str = "CNY"


@dataclass
class DailyBudget:
    """每日预算"""
    day: int
    date: str
    items: List[BudgetItem]
    total_cost: float
    currency: str = "CNY"


@dataclass
class SafetyAlert:
    """安全预警"""
    alert_type: str
    severity: str
    title: str
    description: str
    location: str
    start_time: str
    end_time: str
    recommendations: List[str]


@dataclass
class MotoTravelPlan:
    """摩旅计划"""
    # 基本信息
    plan_id: str
    user_id: str
    title: str
    description: str
    created_at: str
    
    # 路线信息
    origin: LocationInfo
    destination: LocationInfo
    waypoints: List[LocationInfo]
    total_distance_km: float
    total_duration_days: int
    route_type: str  # 自然风光、经典摩旅、历史人文
    
    # 每日路线
    daily_routes: List[DailyRoute]
    
    # 天气信息
    weather_forecast: List[WeatherInfo]
    weather_alerts: List[SafetyAlert]
    
    # POI信息
    restaurants: List[POIInfo]
    accommodations: List[POIInfo]
    gas_stations: List[POIInfo]
    repair_shops: List[POIInfo]
    attractions: List[POIInfo]
    
    # 预算信息
    total_budget: float
    daily_budgets: List[DailyBudget]
    budget_breakdown: Dict[str, float]
    
    # 安全信息
    safety_alerts: List[SafetyAlert]
    safety_recommendations: List[str]
    
    # 个性化信息
    user_preferences: Dict[str, Any]
    personalized_recommendations: List[str]
    
    # 元数据
    metadata: Dict[str, Any]


class MotoTravelOutputTemplate:
    """摩旅输出模板"""
    
    @staticmethod
    def create_json_template() -> Dict[str, Any]:
        """创建JSON输出模板"""
        return {
            "success": True,
            "data": {
                "plan_id": "string",
                "user_id": "string",
                "title": "string",
                "description": "string",
                "created_at": "2024-01-01T00:00:00Z",
                "origin": {
                    "name": "string",
                    "address": "string",
                    "coordinates": {"longitude": 0.0, "latitude": 0.0},
                    "province": "string",
                    "city": "string",
                    "district": "string"
                },
                "destination": {
                    "name": "string",
                    "address": "string",
                    "coordinates": {"longitude": 0.0, "latitude": 0.0},
                    "province": "string",
                    "city": "string",
                    "district": "string"
                },
                "waypoints": [],
                "total_distance_km": 0.0,
                "total_duration_days": 0,
                "route_type": "string",
                "daily_routes": [],
                "weather_forecast": [],
                "weather_alerts": [],
                "restaurants": [],
                "accommodations": [],
                "gas_stations": [],
                "repair_shops": [],
                "attractions": [],
                "total_budget": 0.0,
                "daily_budgets": [],
                "budget_breakdown": {},
                "safety_alerts": [],
                "safety_recommendations": [],
                "user_preferences": {},
                "personalized_recommendations": [],
                "metadata": {}
            },
            "message": "string",
            "metadata": {
                "execution_time": 0.0,
                "agent_used": "string",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    
    @staticmethod
    def create_markdown_template() -> str:
        """创建Markdown输出模板"""
        return """# 🏍️ 摩旅智能规划报告

## 📋 执行摘要

### 🎯 旅行目的与愿景
- **主要目标**: {travel_purpose}
- **期望体验**: {expected_experience}
- **特殊需求**: {special_requirements}
- **关键偏好**: {key_preferences}

### 🛣️ 路线概览
- **出发地**: {origin_name}
- **目的地**: {destination_name}
- **总距离**: {total_distance} 公里
- **预计天数**: {total_days} 天
- **路线类型**: {route_type}
- **整体风格**: {travel_style}
- **总预算**: ¥{total_budget}

### 💫 体验亮点
- **标志性路段**: {signature_routes}
- **独特体验**: {unique_experiences}
- **拍照圣地**: {photo_spots}
- **文化体验**: {cultural_experiences}

## 🗺️ 详细路线规划

### 路线总览
- **起点**: {origin_address}
- **终点**: {destination_address}
- **途经点**: {waypoints}
- **总里程**: {total_distance} 公里
- **预计时长**: {total_duration} 小时

### 每日详细行程

{daily_routes_content}

## 🌤️ 天气与安全分析

### 天气预报
{weather_forecast_content}

### 安全预警
{safety_alerts_content}

### 骑行安全建议
{safety_recommendations_content}

## 🍽️ 餐饮推荐

### 沿途餐厅
{restaurants_content}

## 🏨 住宿推荐

### 推荐住宿
{accommodations_content}

## ⛽ 服务设施

### 加油站
{gas_stations_content}

### 修车行
{repair_shops_content}

## 🎯 景点推荐

### 沿途景点
{attractions_content}

## 💰 预算分析

### 总预算概览
- **总预算**: ¥{total_budget}
- **日均预算**: ¥{daily_average_budget}
- **每公里成本**: ¥{cost_per_km}

### 详细预算分解
{budget_breakdown_content}

### 每日预算明细
{daily_budgets_content}

## 🛡️ 安全与应急

### 安全提醒
{safety_reminders_content}

### 应急联系
{emergency_contacts_content}

### 装备建议
{equipment_recommendations_content}

## 📱 实用信息

### 必备应用
{essential_apps_content}

### 预订信息
{booking_info_content}

### 当地提示
{local_tips_content}

## 🎨 个性化推荐

### 基于您的偏好
{personalized_recommendations_content}

### 特别提醒
{special_reminders_content}

---

*本报告由摩旅智能助手生成，祝您旅途愉快！* 🏍️✨
"""
    
    @staticmethod
    def format_daily_route_markdown(daily_route: DailyRoute) -> str:
        """格式化每日路线Markdown"""
        return f"""
### 第{daily_route.day}天 - {daily_route.date}

#### 🚀 路线信息
- **起点**: {daily_route.start_location.name}
- **终点**: {daily_route.end_location.name}
- **距离**: {daily_route.total_distance_km} 公里
- **预计时长**: {daily_route.estimated_duration_hours} 小时

#### 🛣️ 路段详情
{chr(10).join([f"- **路段{i+1}**: {segment.start_location.name} → {segment.end_location.name} ({segment.distance_km}km, {segment.duration_minutes}分钟)" for i, segment in enumerate(daily_route.segments)])}

#### 🛑 推荐停靠点
{chr(10).join([f"- **{stop['name']}**: {stop['description']} (距离: {stop['distance']}km)" for stop in daily_route.recommended_stops])}

#### 🏨 住宿推荐
{daily_route.accommodation['name'] if daily_route.accommodation else '待定'}
"""
    
    @staticmethod
    def format_weather_markdown(weather_info: WeatherInfo) -> str:
        """格式化天气信息Markdown"""
        return f"""
#### {weather_info.date} - {weather_info.location}
- **温度**: {weather_info.temperature}°C
- **天气**: {weather_info.weather_condition}
- **风力**: {weather_info.wind_speed}km/h {weather_info.wind_direction}
- **能见度**: {weather_info.visibility}km
- **安全评分**: {weather_info.safety_score}/100 ({weather_info.safety_level})
- **提醒**: {', '.join(weather_info.warnings)}
- **建议**: {', '.join(weather_info.recommendations)}
"""
    
    @staticmethod
    def format_poi_markdown(poi: POIInfo) -> str:
        """格式化POI信息Markdown"""
        return f"""
#### {poi.name}
- **类型**: {poi.category}
- **地址**: {poi.location.address}
- **评分**: {poi.rating}/5.0
- **价格**: {poi.price_level}
- **营业时间**: {poi.business_hours}
- **电话**: {poi.phone}
- **距离**: {poi.distance_from_route}km
- **特色**: {', '.join(poi.features)}
"""
    
    @staticmethod
    def format_budget_markdown(budget_item: BudgetItem) -> str:
        """格式化预算项目Markdown"""
        return f"- **{budget_item.item_name}**: ¥{budget_item.total_cost} ({budget_item.quantity} × ¥{budget_item.unit_cost})"
    
    @staticmethod
    def create_agent_prompt_template() -> str:
        """创建Agent提示词模板"""
        return """
您是摩旅智能助手的首席规划师，专门为摩托车旅行提供专业、安全、个性化的行程规划服务。

## 您的使命
将用户的摩旅需求转化为详细、实用、安全的旅行计划，确保每次出行都是一次难忘的冒险体验。

## 核心职责

### 1. 深度需求分析
仔细分析用户输入中的完整摩旅偏好：
- **路线偏好**: 起点、终点、途经点、路线类型（自然风光/经典摩旅/历史人文）
- **时间安排**: 出发日期、旅行天数、每日骑行时长偏好
- **距离偏好**: 日行距离范围（短途<300km/中途300-500km/长途>500km）
- **骑行风格**: 休闲观光/激情驾驶/探险挑战
- **预算范围**: 总预算、日均预算、各项费用分配
- **同伴信息**: 独自/双人/团队，经验水平
- **特殊需求**: 装备要求、身体状况、兴趣偏好
- **安全要求**: 风险承受度、经验水平、安全优先级

### 2. 专业路线规划
- **路线设计**: 基于高德地图API规划最优摩托车路线
- **路段分析**: 详细分析每个路段的距离、时长、难度、安全等级
- **每日分段**: 根据用户日行偏好合理分割长途路线
- **替代方案**: 提供备选路线和应急调整方案
- **路况考虑**: 避开施工、拥堵、危险路段

### 3. 安全风险评估
- **天气分析**: 基于和风天气API分析骑行安全性
- **路况预警**: 识别潜在危险和风险因素
- **装备建议**: 根据路线和天气推荐必要装备
- **应急准备**: 提供应急联系方式和处理方案
- **健康提醒**: 考虑长时间骑行的身体负荷

### 4. 服务设施规划
- **加油站**: 规划加油点，确保燃油充足
- **修车行**: 识别沿途维修服务点
- **餐饮推荐**: 推荐适合摩旅的餐厅和小吃
- **住宿安排**: 选择摩托车友好的住宿
- **景点推荐**: 根据用户兴趣推荐沿途景点

### 5. 预算精确计算
- **燃油费用**: 基于距离和油耗计算
- **住宿成本**: 根据偏好和地区价格
- **餐饮预算**: 考虑当地消费水平
- **维护费用**: 包含车辆保养和维修
- **应急资金**: 预留意外支出
- **装备成本**: 必要装备采购费用

### 6. 个性化定制
- **偏好记忆**: 基于用户历史偏好定制
- **体验优化**: 根据兴趣调整活动安排
- **节奏匹配**: 适应个人骑行节奏
- **风格统一**: 保持整体旅行风格一致

## 输出要求

### JSON格式输出
提供结构化的JSON数据，包含：
- 完整的路线信息
- 详细的每日安排
- 天气和安全分析
- POI推荐列表
- 精确预算计算
- 个性化建议

### Markdown文档输出
生成美观的Markdown格式旅行报告：
- 清晰的章节结构
- 丰富的表情符号
- 详细的每日行程
- 实用的安全提醒
- 完整的预算分析
- 个性化的推荐

## 质量标准
- ✅ 路线安全可靠，适合摩托车骑行
- ✅ 预算合理准确，符合用户预期
- ✅ 时间安排合理，避免疲劳驾驶
- ✅ 服务设施齐全，满足基本需求
- ✅ 个性化程度高，符合用户偏好
- ✅ 信息准确完整，便于实际执行
- ✅ 格式美观易读，用户体验良好

请始终以用户的安全和体验为核心，提供专业、贴心、实用的摩旅规划服务。
"""
    
    @staticmethod
    def create_success_criteria() -> List[str]:
        """创建成功标准"""
        return [
            "✅ 路线规划完整，包含所有必要信息",
            "✅ 安全分析全面，识别所有潜在风险",
            "✅ 预算计算准确，符合用户预期",
            "✅ 服务设施齐全，满足摩旅需求",
            "✅ 个性化程度高，符合用户偏好",
            "✅ 时间安排合理，避免过度疲劳",
            "✅ 信息准确可靠，便于实际执行",
            "✅ 格式美观易读，用户体验良好",
            "✅ 包含应急方案，确保出行安全",
            "✅ 提供实用建议，提升旅行体验"
        ]


class OutputFormatter:
    """输出格式化器"""
    
    def __init__(self):
        self.template = MotoTravelOutputTemplate()
    
    def format_json_output(self, data: MotoTravelPlan) -> Dict[str, Any]:
        """格式化JSON输出"""
        return {
            "success": True,
            "data": asdict(data),
            "message": "摩旅规划完成",
            "metadata": {
                "execution_time": 0.0,
                "agent_used": "moto_travel_agent",
                "timestamp": datetime.utcnow().isoformat(),
                "format": "json"
            }
        }
    
    def format_markdown_output(self, data: MotoTravelPlan) -> str:
        """格式化Markdown输出"""
        template = self.template.create_markdown_template()
        
        # 格式化每日路线
        daily_routes_content = ""
        for daily_route in data.daily_routes:
            daily_routes_content += self.template.format_daily_route_markdown(daily_route)
        
        # 格式化天气信息
        weather_forecast_content = ""
        for weather in data.weather_forecast:
            weather_forecast_content += self.template.format_weather_markdown(weather)
        
        # 格式化POI信息
        restaurants_content = ""
        for restaurant in data.restaurants:
            restaurants_content += self.template.format_poi_markdown(restaurant)
        
        accommodations_content = ""
        for accommodation in data.accommodations:
            accommodations_content += self.template.format_poi_markdown(accommodation)
        
        gas_stations_content = ""
        for gas_station in data.gas_stations:
            gas_stations_content += self.template.format_poi_markdown(gas_station)
        
        repair_shops_content = ""
        for repair_shop in data.repair_shops:
            repair_shops_content += self.template.format_poi_markdown(repair_shop)
        
        attractions_content = ""
        for attraction in data.attractions:
            attractions_content += self.template.format_poi_markdown(attraction)
        
        # 格式化预算信息
        budget_breakdown_content = ""
        for category, amount in data.budget_breakdown.items():
            budget_breakdown_content += f"- **{category}**: ¥{amount}\n"
        
        daily_budgets_content = ""
        for daily_budget in data.daily_budgets:
            daily_budgets_content += f"\n### 第{daily_budget.day}天 - {daily_budget.date}\n"
            daily_budgets_content += f"**总预算**: ¥{daily_budget.total_cost}\n"
            for item in daily_budget.items:
                daily_budgets_content += self.template.format_budget_markdown(item) + "\n"
        
        # 替换模板变量
        return template.format(
            travel_purpose=data.description,
            expected_experience="安全、愉快的摩托车旅行体验",
            special_requirements=", ".join(data.user_preferences.get("special_requirements", [])),
            key_preferences=", ".join(data.user_preferences.get("key_preferences", [])),
            origin_name=data.origin.name,
            destination_name=data.destination.name,
            total_distance=data.total_distance_km,
            total_days=data.total_duration_days,
            route_type=data.route_type,
            travel_style=data.user_preferences.get("travel_style", "休闲"),
            total_budget=data.total_budget,
            signature_routes=", ".join([route.title for route in data.daily_routes[:3]]),
            unique_experiences=", ".join(data.personalized_recommendations[:3]),
            photo_spots="沿途风景优美的观景点",
            cultural_experiences="当地特色文化体验",
            origin_address=data.origin.address,
            destination_address=data.destination.address,
            waypoints=", ".join([wp.name for wp in data.waypoints]),
            total_duration=sum([route.estimated_duration_hours for route in data.daily_routes]),
            daily_routes_content=daily_routes_content,
            weather_forecast_content=weather_forecast_content,
            safety_alerts_content="\n".join([f"- **{alert.title}**: {alert.description}" for alert in data.safety_alerts]),
            safety_recommendations_content="\n".join([f"- {rec}" for rec in data.safety_recommendations]),
            restaurants_content=restaurants_content,
            accommodations_content=accommodations_content,
            gas_stations_content=gas_stations_content,
            repair_shops_content=repair_shops_content,
            attractions_content=attractions_content,
            daily_average_budget=data.total_budget / data.total_duration_days if data.total_duration_days > 0 else 0,
            cost_per_km=data.total_budget / data.total_distance_km if data.total_distance_km > 0 else 0,
            budget_breakdown_content=budget_breakdown_content,
            daily_budgets_content=daily_budgets_content,
            safety_reminders_content="\n".join([f"- {reminder}" for reminder in data.safety_recommendations]),
            emergency_contacts_content="110 (报警), 120 (急救), 119 (火警)",
            equipment_recommendations_content="头盔、护具、维修工具、应急药品",
            essential_apps_content="高德地图、和风天气、摩旅助手",
            booking_info_content="提前预订住宿，确认加油站营业时间",
            local_tips_content="遵守当地交通规则，注意天气变化",
            personalized_recommendations_content="\n".join([f"- {rec}" for rec in data.personalized_recommendations]),
            special_reminders_content="注意安全，享受旅程"
        )
    
    def format_output(self, data: MotoTravelPlan, format_type: OutputFormat) -> Any:
        """格式化输出"""
        if format_type == OutputFormat.JSON:
            return self.format_json_output(data)
        elif format_type == OutputFormat.MARKDOWN:
            return self.format_markdown_output(data)
        else:
            raise ValueError(f"不支持的输出格式: {format_type}")
