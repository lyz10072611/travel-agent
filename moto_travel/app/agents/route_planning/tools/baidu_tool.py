"""
百度地图工具
实现百度地图API的路线规划、POI搜索等功能
"""
from typing import Dict, List, Any, Optional
import hashlib
import urllib.parse
from tools.base_tool import RateLimitedTool
from app.config import settings
from loguru import logger


class BaiduMapTool(RateLimitedTool):
    """百度地图工具 - 摩旅路线规划"""
    
    def __init__(self):
        super().__init__(
            name="baidu_map_tool",
            description="""
            🗺️ 百度地图智能路线规划工具
            
            【核心功能】
            • 地理编码：地址转坐标
            • 逆地理编码：坐标转地址
            • POI搜索：搜索服务设施
            • 路线规划：摩托车路线规划
            
            【摩旅特色】
            • 摩托车友好路线
            • 避开禁摩区域
            • 国道省道优先
            """,
            requests_per_minute=100
        )
        self.api_key = settings.baidu_api_key
        self.base_url = settings.baidu_web_service_url
    
    def _generate_sn(self, params: Dict[str, Any], sk: str) -> str:
        """生成百度地图SN签名"""
        if not sk:
            return ""
        
        # 按参数名排序
        sorted_params = sorted(params.items())
        # 拼接参数字符串
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        # 添加SK
        full_string = f"/direction/v2/driving?{query_string}{sk}"
        # MD5加密
        sn = hashlib.md5(urllib.parse.quote_plus(full_string).encode('utf-8')).hexdigest()
        return sn
    
    async def geocode(self, address: str, city: Optional[str] = None) -> Dict[str, Any]:
        """地理编码 - 地址转坐标"""
        self.validate_params(["address"], address=address)
        
        url = f"{self.base_url}/geocoding/v3"
        params = {
            "address": address,
            "output": "json",
            "ak": self.api_key
        }
        if city:
            params["city"] = city
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == 0:
            location = result.get("result", {}).get("location", {})
            return self.format_response({
                "longitude": location.get("lng", 0),
                "latitude": location.get("lat", 0),
                "formatted_address": result.get("result", {}).get("formatted_address", ""),
                "confidence": result.get("result", {}).get("confidence", 0)
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"Geocoding failed: {result.get('message', 'Unknown error')}"
            )
    
    async def reverse_geocode(self, longitude: float, latitude: float) -> Dict[str, Any]:
        """逆地理编码 - 坐标转地址"""
        self.validate_params(["longitude", "latitude"], longitude=longitude, latitude=latitude)
        
        url = f"{self.base_url}/reverse_geocoding/v3"
        params = {
            "ak": self.api_key,
            "output": "json",
            "coordtype": "wgs84ll",
            "location": f"{latitude},{longitude}"
        }
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == 0:
            result_data = result.get("result", {})
            address_component = result_data.get("addressComponent", {})
            
            return self.format_response({
                "formatted_address": result_data.get("formatted_address", ""),
                "province": address_component.get("province", ""),
                "city": address_component.get("city", ""),
                "district": address_component.get("district", ""),
                "street": address_component.get("street", ""),
                "street_number": address_component.get("street_number", "")
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"Reverse geocoding failed: {result.get('message', 'Unknown error')}"
            )
    
    async def get_route(
        self,
        origin: str,
        destination: str,
        waypoints: Optional[List[str]] = None,
        tactics: int = 12,  # 12:最短时间（默认，灵活标准，允许走高速）
        avoid_polygons: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        路线规划（灵活标准，默认允许走高速）
        
        Args:
            origin: 起点坐标 "纬度,经度" 或地址（百度是纬度在前）
            destination: 终点坐标 "纬度,经度" 或地址
            waypoints: 途经点列表
            tactics: 路线策略（灵活标准）
                - 12: 最短时间（默认，允许走高速，灵活选择）
                - 13: 最短距离（尽量避开高速）
                - 11: 不走高速（严格禁止）
            avoid_polygons: 避让区域
        """
        self.validate_params(["origin", "destination"], origin=origin, destination=destination)
        
        url = f"{self.base_url}/direction/v2/driving"
        params = {
            "ak": self.api_key,
            "origin": origin,
            "destination": destination,
            "tactics": tactics,
            "output": "json"
        }
        
        if waypoints:
            params["waypoints"] = "|".join(waypoints)
        if avoid_polygons:
            params["avoid_polygons"] = avoid_polygons
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == 0:
            route_data = result.get("result", {})
            routes = route_data.get("routes", [])
            
            if routes:
                route = routes[0]  # 取第一条路线
                steps = route.get("steps", [])
                
                processed_steps = []
                total_distance = 0
                total_duration = 0
                
                for step in steps:
                    distance = step.get("distance", 0)
                    duration = step.get("duration", 0)
                    total_distance += distance
                    total_duration += duration
                    
                    processed_steps.append({
                        "instruction": step.get("instructions", ""),
                        "road": step.get("road", ""),
                        "distance": distance,
                        "duration": duration,
                        "path": step.get("path", ""),
                        "direction": step.get("direction", 0)
                    })
                
                return self.format_response({
                    "distance": total_distance,
                    "duration": total_duration,
                    "steps": processed_steps,
                    "traffic_lights": route.get("traffic_lights", 0),
                    "tolls": route.get("tolls", 0),
                    "toll_distance": route.get("toll_distance", 0)
                })
        
        return self.format_response(
            None,
            success=False,
            message=f"Route planning failed: {result.get('message', 'Unknown error')}"
        )
    
    async def search_poi(
        self,
        query: str,
        location: Optional[str] = None,
        radius: int = 3000,
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """POI搜索"""
        self.validate_params(["query"], query=query)
        
        url = f"{self.base_url}/place/v2/search"
        params = {
            "ak": self.api_key,
            "query": query,
            "output": "json",
            "scope": 2,  # 返回详细结果
            "page_size": 20,
            "page_num": 0
        }
        
        if location:
            params["location"] = location
            params["radius"] = radius
        if tag:
            params["tag"] = tag
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == 0:
            pois = result.get("results", [])
            processed_pois = []
            
            for poi in pois:
                location_data = poi.get("location", {})
                processed_pois.append({
                    "name": poi.get("name", ""),
                    "address": poi.get("address", ""),
                    "longitude": location_data.get("lng", 0),
                    "latitude": location_data.get("lat", 0),
                    "tag": poi.get("tag", ""),
                    "distance": poi.get("distance", 0),
                    "uid": poi.get("uid", "")
                })
            
            return self.format_response({
                "pois": processed_pois,
                "total": len(processed_pois)
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"POI search failed: {result.get('message', 'Unknown error')}"
            )

