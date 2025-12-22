"""
POI工具（重构版）
从tools/poi_tools.py迁移，适配新架构
"""
from typing import Dict, List, Any, Optional
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
    """POI工具"""
    
    def __init__(self):
        super().__init__(
            name="poi_tool",
            description="POI智能搜索工具",
            requests_per_minute=100
        )
        self.api_key = settings.amap_api_key
        self.base_url = settings.amap_web_service_url
    
    async def search_poi(
        self,
        keywords: str,
        location: Optional[str] = None,
        radius: int = 3000,
        types: Optional[str] = None
    ) -> Dict[str, Any]:
        """搜索POI"""
        self.validate_params(["keywords"], keywords=keywords)
        
        url = f"{self.base_url}/place/text"
        params = {
            "keywords": keywords,
            "output": "json",
            "offset": 20,
            "page": 1,
            "extensions": "all",
            "key": self.api_key
        }
        
        if location:
            params["location"] = location
            params["radius"] = radius
        if types:
            params["types"] = types
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == "1":
            pois = result.get("pois", [])
            processed_pois = []
            
            for poi in pois:
                location_str = poi.get("location", "")
                if location_str:
                    lon, lat = map(float, location_str.split(","))
                    detail_info = poi.get("detail_info", {})
                    
                    processed_pois.append({
                        "id": poi.get("id"),
                        "name": poi.get("name"),
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
                        "opening_hours": detail_info.get("opening_hours", "")
                    })
            
            # 按距离排序
            processed_pois.sort(key=lambda x: x["distance"])
            
            return self.format_response({
                "pois": processed_pois,
                "total": len(processed_pois)
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"POI search failed: {result.get('info', 'Unknown error')}"
            )
    
    async def search_gas_stations(
        self,
        location: str,
        radius: int = 10000
    ) -> Dict[str, Any]:
        """搜索加油站"""
        return await self.search_poi(
            keywords="加油站|中石化|中石油|壳牌",
            location=location,
            radius=radius,
            types="060000"  # 高德地图加油站类型代码
        )
    
    async def search_restaurants(
        self,
        location: str,
        radius: int = 3000
    ) -> Dict[str, Any]:
        """搜索餐厅"""
        return await self.search_poi(
            keywords="餐厅|饭店|餐馆|美食",
            location=location,
            radius=radius,
            types="050000"  # 高德地图餐饮类型代码
        )
    
    async def search_hotels(
        self,
        location: str,
        radius: int = 5000
    ) -> Dict[str, Any]:
        """搜索酒店"""
        return await self.search_poi(
            keywords="酒店|宾馆|旅馆|民宿",
            location=location,
            radius=radius,
            types="100000"  # 高德地图住宿类型代码
        )
    
    async def search_repair_shops(
        self,
        location: str,
        radius: int = 20000
    ) -> Dict[str, Any]:
        """搜索修车行"""
        return await self.search_poi(
            keywords="汽车维修|摩托车维修|修车|汽修",
            location=location,
            radius=radius,
            types="030000"  # 高德地图汽车服务类型代码
        )

