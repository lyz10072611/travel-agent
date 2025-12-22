"""
高德地图工具（重构版）
从tools/map_tools.py迁移，适配新架构
"""
from typing import Dict, List, Any, Optional
from tools.base_tool import RateLimitedTool
from app.config import settings
from loguru import logger


class AmapTool(RateLimitedTool):
    """高德地图工具 - 摩旅路线规划"""
    
    def __init__(self):
        super().__init__(
            name="amap_tool",
            description="高德地图智能路线规划工具",
            requests_per_minute=100
        )
        self.api_key = settings.amap_api_key
        self.base_url = settings.amap_web_service_url
    
    async def geocode(self, address: str) -> Dict[str, Any]:
        """地理编码"""
        self.validate_params(["address"], address=address)
        
        url = f"{self.base_url}/geocode/geo"
        params = {
            "address": address,
            "output": "json",
            "key": self.api_key
        }
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == "1" and result.get("geocodes"):
            geocode = result["geocodes"][0]
            location = geocode["location"].split(",")
            return self.format_response({
                "longitude": float(location[0]),
                "latitude": float(location[1]),
                "formatted_address": geocode["formatted_address"],
                "province": geocode.get("province", ""),
                "city": geocode.get("city", ""),
                "district": geocode.get("district", "")
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"Geocoding failed: {result.get('info', 'Unknown error')}"
            )
    
    async def get_route(
        self,
        origin: str,
        destination: str,
        waypoints: Optional[List[str]] = None,
        strategy: int = 0,  # 0:速度优先（默认，灵活标准，允许走高速）
        avoid_polygons: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        路线规划（灵活标准，默认允许走高速）
        
        Args:
            origin: 起点坐标 "经度,纬度" 或地址
            destination: 终点坐标 "经度,纬度" 或地址
            waypoints: 途经点列表
            strategy: 路线策略（灵活标准）
                - 0: 速度优先（默认，允许走高速，灵活选择）
                - 1: 费用优先（尽量避开高速）
                - 2: 距离优先（最短路线）
                - 3: 不走高速（严格禁止）
            avoid_polygons: 避让区域
        """
        self.validate_params(["origin", "destination"], origin=origin, destination=destination)
        
        url = f"{self.base_url}/direction/driving"
        params = {
            "origin": origin,
            "destination": destination,
            "strategy": strategy,
            "output": "json",
            "extensions": "all",
            "key": self.api_key
        }
        
        if waypoints:
            params["waypoints"] = "|".join(waypoints)
        if avoid_polygons:
            params["avoidpolygons"] = avoid_polygons
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == "1" and result.get("route"):
            route = result["route"]
            paths = route.get("paths", [])
            
            if paths:
                path = paths[0]
                steps = path.get("steps", [])
                
                processed_steps = []
                total_distance = 0
                total_duration = 0
                
                for step in steps:
                    distance = int(step.get("distance", 0))
                    duration = int(step.get("duration", 0))
                    total_distance += distance
                    total_duration += duration
                    
                    processed_steps.append({
                        "instruction": step.get("instruction", ""),
                        "road": step.get("road", ""),
                        "distance": distance,
                        "duration": duration,
                        "polyline": step.get("polyline", ""),
                        "action": step.get("action", "")
                    })
                
                return self.format_response({
                    "distance": total_distance,
                    "duration": total_duration,
                    "steps": processed_steps,
                    "tolls": path.get("tolls", 0),
                    "toll_distance": path.get("toll_distance", 0),
                    "traffic_lights": path.get("traffic_lights", 0)
                })
        
        return self.format_response(
            None,
            success=False,
            message=f"Route planning failed: {result.get('info', 'Unknown error')}"
        )
    
    async def search_poi(
        self,
        keywords: str,
        location: Optional[str] = None,
        radius: int = 3000,
        types: Optional[str] = None
    ) -> Dict[str, Any]:
        """POI搜索"""
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
                    processed_pois.append({
                        "id": poi.get("id"),
                        "name": poi.get("name"),
                        "type": poi.get("type"),
                        "address": poi.get("address"),
                        "longitude": lon,
                        "latitude": lat,
                        "tel": poi.get("tel", ""),
                        "distance": poi.get("distance", 0)
                    })
            
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

