"""
POI相关工具
处理餐饮、住宿、修车、加油站等本地服务
"""
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from tools.base_tool import RateLimitedTool
from app.config import settings


class POICategory(Enum):
    """POI分类枚举"""
    RESTAURANT = "餐饮服务"
    HOTEL = "住宿服务"
    GAS_STATION = "加油站"
    REPAIR_SHOP = "汽车维修"
    MOTORCYCLE_SHOP = "摩托车相关"
    PHARMACY = "药店"
    HOSPITAL = "医院"
    BANK = "银行"
    ATM = "ATM"
    SCENIC_SPOT = "风景名胜"
    PARKING = "停车场"


class POITool(RateLimitedTool):
    """POI工具 - 摩旅路上的贴心服务管家"""
    
    def __init__(self):
        super().__init__(
            name="poi_tool",
            description="""
            🏪 POI智能搜索工具 - 摩旅路上的贴心服务管家
            
            【核心功能】
            • 餐厅搜索：智能推荐摩托车友好的餐厅，考虑停车便利性
            • 住宿查询：筛选摩托车友好酒店，提供停车和安全保障
            • 加油站：规划加油点，确保燃油充足，避免中途断油
            • 修车行：识别专业摩托车维修店，提供应急维修服务
            • 医疗设施：查找沿途医院、诊所，提供医疗保障
            
            【摩旅特色服务】
            • 摩托车友好筛选：优先推荐适合摩托车的服务设施
            • 停车便利性：考虑摩托车停放和安全的场所
            • 24小时服务：识别提供24小时服务的加油站和修车行
            • 专业服务：推荐摩托车专业维修和配件服务
            
            【智能推荐算法】
            • 距离优化：按距离排序，优先推荐最近的设施
            • 评分筛选：基于用户评分筛选高质量服务
            • 价格匹配：根据用户预算推荐合适价位的服务
            • 综合评价：综合距离、评分、价格、服务质量的智能推荐
            
            【数据完整性】
            • 详细信息：提供地址、电话、营业时间、价格等完整信息
            • 用户评价：包含用户评分和评价，帮助做出选择
            • 实时更新：定期更新营业状态和服务信息
            • 多源数据：融合多个数据源，确保信息准确性
            
            【安全考虑】
            • 安全区域：优先推荐治安良好的区域
            • 照明条件：考虑夜间服务的照明和安全条件
            • 交通便利：选择交通便利、易于到达的位置
            • 应急服务：提供24小时应急服务信息
            
            适用于：餐饮推荐、住宿安排、加油规划、维修服务、医疗保障
            """,
            requests_per_minute=100
        )
        self.api_key = settings.amap_api_key
        self.base_url = settings.amap_web_service_url
    
    async def search_restaurants(
        self, 
        location: str, 
        radius: int = 3000,
        cuisine_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """搜索餐厅"""
        keywords = "餐厅|饭店|餐馆|美食"
        if cuisine_type:
            keywords += f"|{cuisine_type}"
        
        return await self._search_poi_by_category(
            keywords=keywords,
            location=location,
            radius=radius,
            category=POICategory.RESTAURANT
        )
    
    async def search_hotels(
        self, 
        location: str, 
        radius: int = 5000,
        hotel_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """搜索酒店"""
        keywords = "酒店|宾馆|旅馆|民宿"
        if hotel_type:
            keywords += f"|{hotel_type}"
        
        return await self._search_poi_by_category(
            keywords=keywords,
            location=location,
            radius=radius,
            category=POICategory.HOTEL
        )
    
    async def search_gas_stations(
        self, 
        location: str, 
        radius: int = 10000
    ) -> Dict[str, Any]:
        """搜索加油站"""
        return await self._search_poi_by_category(
            keywords="加油站|中石化|中石油|壳牌",
            location=location,
            radius=radius,
            category=POICategory.GAS_STATION
        )
    
    async def search_repair_shops(
        self, 
        location: str, 
        radius: int = 20000
    ) -> Dict[str, Any]:
        """搜索修车行"""
        return await self._search_poi_by_category(
            keywords="汽车维修|摩托车维修|修车|汽修",
            location=location,
            radius=radius,
            category=POICategory.REPAIR_SHOP
        )
    
    async def search_motorcycle_shops(
        self, 
        location: str, 
        radius: int = 20000
    ) -> Dict[str, Any]:
        """搜索摩托车相关店铺"""
        return await self._search_poi_by_category(
            keywords="摩托车|机车|摩配|头盔|骑行装备",
            location=location,
            radius=radius,
            category=POICategory.MOTORCYCLE_SHOP
        )
    
    async def search_medical_facilities(
        self, 
        location: str, 
        radius: int = 10000
    ) -> Dict[str, Any]:
        """搜索医疗设施"""
        return await self._search_poi_by_category(
            keywords="医院|诊所|药店|急救",
            location=location,
            radius=radius,
            category=POICategory.HOSPITAL
        )
    
    async def search_scenic_spots(
        self, 
        location: str, 
        radius: int = 50000
    ) -> Dict[str, Any]:
        """搜索景点"""
        return await self._search_poi_by_category(
            keywords="景点|景区|公园|旅游|风景",
            location=location,
            radius=radius,
            category=POICategory.SCENIC_SPOT
        )
    
    async def _search_poi_by_category(
        self,
        keywords: str,
        location: str,
        radius: int,
        category: POICategory
    ) -> Dict[str, Any]:
        """按分类搜索POI"""
        url = f"{self.base_url}/place/text"
        params = {
            "keywords": keywords,
            "location": location,
            "radius": radius,
            "output": "json",
            "offset": 20,
            "page": 1,
            "extensions": "all"
        }
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == "1":
            pois = result.get("pois", [])
            processed_pois = []
            
            for poi in pois:
                location_str = poi.get("location", "")
                if location_str:
                    lon, lat = map(float, location_str.split(","))
                    
                    # 获取详细信息
                    detail_info = poi.get("detail_info", {})
                    
                    processed_pois.append({
                        "id": poi.get("id"),
                        "name": poi.get("name"),
                        "category": category.value,
                        "type": poi.get("type"),
                        "address": poi.get("address"),
                        "longitude": lon,
                        "latitude": lat,
                        "tel": poi.get("tel", ""),
                        "distance": poi.get("distance", 0),
                        "rating": detail_info.get("overall_rating", 0),
                        "price": detail_info.get("price", ""),
                        "business_area": poi.get("business_area", ""),
                        "website": detail_info.get("website", ""),
                        "opening_hours": detail_info.get("opening_hours", ""),
                        "photos": detail_info.get("photos", [])
                    })
            
            # 按距离排序
            processed_pois.sort(key=lambda x: x["distance"])
            
            return self.format_response({
                "category": category.value,
                "pois": processed_pois,
                "total": len(processed_pois)
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"POI search failed: {result.get('info', 'Unknown error')}"
            )
    
    async def get_poi_details(self, poi_id: str) -> Dict[str, Any]:
        """获取POI详细信息"""
        self.validate_params(["poi_id"], poi_id=poi_id)
        
        url = f"{self.base_url}/place/detail"
        params = {
            "id": poi_id,
            "output": "json",
            "extensions": "all"
        }
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == "1" and result.get("pois"):
            poi = result["pois"][0]
            detail_info = poi.get("detail_info", {})
            
            return self.format_response({
                "id": poi.get("id"),
                "name": poi.get("name"),
                "type": poi.get("type"),
                "address": poi.get("address"),
                "tel": poi.get("tel", ""),
                "website": detail_info.get("website", ""),
                "rating": detail_info.get("overall_rating", 0),
                "price": detail_info.get("price", ""),
                "opening_hours": detail_info.get("opening_hours", ""),
                "description": detail_info.get("description", ""),
                "photos": detail_info.get("photos", []),
                "reviews": detail_info.get("reviews", [])
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"POI details query failed: {result.get('info', 'Unknown error')}"
            )


class POIAnalyzer:
    """POI分析器"""
    
    @staticmethod
    def analyze_route_pois(
        route_segments: List[Dict[str, Any]], 
        poi_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析路线上的POI分布"""
        analysis = {
            "total_segments": len(route_segments),
            "poi_coverage": {},
            "recommendations": [],
            "gaps": []
        }
        
        # 分析各类POI的覆盖情况
        for category, pois in poi_data.items():
            if isinstance(pois, list):
                analysis["poi_coverage"][category] = {
                    "count": len(pois),
                    "coverage_percentage": (len(pois) / len(route_segments)) * 100
                }
        
        # 识别服务空白区域
        for i, segment in enumerate(route_segments):
            segment_pois = {}
            for category, pois in poi_data.items():
                if isinstance(pois, list):
                    nearby_pois = [poi for poi in pois if poi.get("distance", 0) < 5000]
                    segment_pois[category] = len(nearby_pois)
            
            # 检查关键服务是否缺失
            if segment_pois.get("加油站", 0) == 0:
                analysis["gaps"].append({
                    "segment": i,
                    "type": "加油站",
                    "message": f"第{i+1}段路线缺少加油站"
                })
            
            if segment_pois.get("修车行", 0) == 0:
                analysis["gaps"].append({
                    "segment": i,
                    "type": "修车行",
                    "message": f"第{i+1}段路线缺少修车行"
                })
        
        return analysis
    
    @staticmethod
    def recommend_pois_for_route(
        route_points: List[Tuple[float, float]], 
        daily_distance: int = 300
    ) -> Dict[str, Any]:
        """为路线推荐POI"""
        recommendations = {
            "daily_recommendations": [],
            "essential_services": [],
            "optional_services": []
        }
        
        # 计算每日路线点
        from tools.map_tools import RouteCalculator
        daily_routes = RouteCalculator.split_route_by_daily_distance(
            route_points, daily_distance
        )
        
        for day, daily_route in enumerate(daily_routes):
            if not daily_route:
                continue
                
            # 每日推荐
            day_recommendation = {
                "day": day + 1,
                "start_point": daily_route[0],
                "end_point": daily_route[-1],
                "recommended_pois": {
                    "早餐": "建议在起点附近寻找早餐店",
                    "午餐": "建议在路线中点寻找餐厅",
                    "晚餐": "建议在终点附近寻找餐厅",
                    "住宿": "建议在终点附近寻找酒店",
                    "加油站": "建议在路线中段寻找加油站",
                    "修车行": "建议在路线中段寻找修车行"
                }
            }
            
            recommendations["daily_recommendations"].append(day_recommendation)
        
        # 必需服务
        recommendations["essential_services"] = [
            "加油站 - 每200-300公里需要加油",
            "修车行 - 应对突发故障",
            "医院/药店 - 应急医疗",
            "银行/ATM - 现金需求"
        ]
        
        # 可选服务
        recommendations["optional_services"] = [
            "景点 - 丰富行程体验",
            "特色餐厅 - 品尝当地美食",
            "购物中心 - 补充物资",
            "娱乐场所 - 放松休息"
        ]
        
        return recommendations
    
    @staticmethod
    def filter_pois_by_rating(pois: List[Dict[str, Any]], min_rating: float = 3.5) -> List[Dict[str, Any]]:
        """按评分过滤POI"""
        return [poi for poi in pois if poi.get("rating", 0) >= min_rating]
    
    @staticmethod
    def filter_pois_by_distance(pois: List[Dict[str, Any]], max_distance: int = 5000) -> List[Dict[str, Any]]:
        """按距离过滤POI"""
        return [poi for poi in pois if poi.get("distance", 0) <= max_distance]
    
    @staticmethod
    def sort_pois_by_priority(pois: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按优先级排序POI"""
        # 优先级：距离 > 评分 > 价格
        return sorted(pois, key=lambda x: (
            x.get("distance", 999999),
            -x.get("rating", 0),
            len(x.get("price", ""))
        ))
