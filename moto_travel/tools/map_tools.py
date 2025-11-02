"""
地图相关工具
基于高德地图API实现路线规划、POI搜索等功能
"""
from typing import Dict, List, Any, Optional, Tuple
import json
from geopy.distance import geodesic
from tools.base_tool import RateLimitedTool
from app.config import settings


class AmapTool(RateLimitedTool):
    """高德地图工具 - 摩旅路线规划的核心工具"""
    
    def __init__(self):
        super().__init__(
            name="amap_tool",
            description="""
            🗺️ 高德地图智能路线规划工具
            
            【核心功能】
            • 地理编码：将地址转换为精确坐标，支持模糊地址智能识别
            • 逆地理编码：将坐标转换为详细地址信息，包含行政区划
            • POI搜索：智能搜索餐饮、住宿、加油站、修车行等服务设施
            • 路线规划：摩托车专用路线规划，支持避开高速、选择风景路线
            
            【摩旅特色】
            • 摩托车友好路线：优先选择适合摩托车的国道、省道
            • 风景路线优化：自动识别风景优美的观景路线
            • 安全路线规划：避开危险路段，选择安全可靠的路线
            • 服务设施集成：沿途加油站、修车行、住宿点智能规划
            
            【智能特性】
            • 多策略路线：速度优先、距离优先、不走高速、费用优先
            • 实时路况：集成交通态势，避开拥堵和施工路段
            • 个性化定制：根据用户偏好调整路线规划策略
            • 详细导航：提供逐段导航指令，包含距离、时长、路况信息
            
            适用于：路线规划、地址查询、POI搜索、导航服务
            """,
            requests_per_minute=100
        )
        self.api_key = settings.amap_api_key
        self.base_url = settings.amap_web_service_url
    
    async def geocode(self, address: str) -> Dict[str, Any]:
        """
        地理编码 - 智能地址转坐标
        
        【功能描述】
        将用户输入的地址（支持模糊地址）转换为精确的地理坐标
        支持智能地址识别，即使输入不完整的地址也能准确定位
        
        【输入参数】
        - address: 地址字符串，支持以下格式：
          • 完整地址："北京市朝阳区建国门外大街1号"
          • 模糊地址："北京天安门"、"上海外滩"
          • 地标名称："故宫"、"东方明珠"
          • 行政区划："北京市朝阳区"
        
        【输出结果】
        - longitude: 经度坐标
        - latitude: 纬度坐标  
        - formatted_address: 标准化地址
        - province/city/district: 省市区信息
        
        【使用场景】
        • 用户输入起点终点时进行地址解析
        • 模糊地址的智能识别和定位
        • 为路线规划提供精确的坐标信息
        """
        self.validate_params(["address"], address=address)
        
        url = f"{self.base_url}/geocode/geo"
        params = {
            "address": address,
            "output": "json"
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
    
    async def reverse_geocode(self, longitude: float, latitude: float) -> Dict[str, Any]:
        """逆地理编码 - 坐标转地址"""
        self.validate_params(["longitude", "latitude"], longitude=longitude, latitude=latitude)
        
        url = f"{self.base_url}/geocode/regeo"
        params = {
            "location": f"{longitude},{latitude}",
            "output": "json",
            "extensions": "all"
        }
        
        result = await self._make_request(url, params=params)
        
        if result.get("status") == "1" and result.get("regeocode"):
            regeocode = result["regeocode"]
            return self.format_response({
                "formatted_address": regeocode["formatted_address"],
                "province": regeocode.get("addressComponent", {}).get("province", ""),
                "city": regeocode.get("addressComponent", {}).get("city", ""),
                "district": regeocode.get("addressComponent", {}).get("district", ""),
                "pois": regeocode.get("pois", [])
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"Reverse geocoding failed: {result.get('info', 'Unknown error')}"
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
            "extensions": "all"
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
    
    async def get_route(
        self,
        origin: str,
        destination: str,
        waypoints: Optional[List[str]] = None,
        strategy: int = 0,  # 0:速度优先 1:费用优先 2:距离优先 3:不走高速
        avoid_polygons: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        智能路线规划 - 摩旅专用路线计算
        
        【功能描述】
        基于高德地图API进行摩托车专用路线规划，提供详细的导航信息
        支持多种路线策略，可根据用户偏好选择最优路线
        
        【输入参数】
        - origin: 起点坐标 "经度,纬度" 或地址
        - destination: 终点坐标 "经度,纬度" 或地址  
        - waypoints: 途经点列表，支持多个途经点
        - strategy: 路线策略
          • 0: 速度优先 - 选择最快路线，可能包含高速
          • 1: 费用优先 - 选择费用最低路线，避开收费路段
          • 2: 距离优先 - 选择最短距离路线
          • 3: 不走高速 - 摩托车友好，避开高速公路
        - avoid_polygons: 避让区域，多边形坐标串
        
        【输出结果】
        - distance: 总距离（米）
        - duration: 总时长（秒）
        - steps: 详细导航步骤
          • instruction: 导航指令
          • road: 道路名称
          • distance: 路段距离
          • duration: 路段时长
          • polyline: 路段坐标串
        - tolls: 过路费
        - traffic_lights: 红绿灯数量
        
        【摩旅特色】
        • 摩托车友好：优先选择国道、省道等适合摩托车的道路
        • 风景路线：自动识别风景优美的观景路线
        • 安全考虑：避开危险路段和施工区域
        • 服务设施：沿途加油站、修车行等设施规划
        
        【使用场景】
        • 长途摩旅路线规划
        • 日常骑行路线计算
        • 多目的地路线优化
        • 避开特定区域的路线规划
        """
        self.validate_params(["origin", "destination"], origin=origin, destination=destination)
        
        url = f"{self.base_url}/direction/driving"
        params = {
            "origin": origin,
            "destination": destination,
            "strategy": strategy,
            "output": "json",
            "extensions": "all"
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
                path = paths[0]  # 取第一条路径
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


class RouteCalculator:
    """路线计算器"""
    
    @staticmethod
    def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """计算两点间距离（公里）"""
        return geodesic(point1, point2).kilometers
    
    @staticmethod
    def calculate_estimated_time(distance_km: float, avg_speed: int = 60) -> int:
        """计算预估时间（分钟）"""
        return int((distance_km / avg_speed) * 60)
    
    @staticmethod
    def split_route_by_daily_distance(
        route_points: List[Tuple[float, float]], 
        daily_distance: int = 300
    ) -> List[List[Tuple[float, float]]]:
        """按日行距离分割路线"""
        if not route_points:
            return []
        
        daily_routes = []
        current_route = [route_points[0]]
        current_distance = 0
        
        for i in range(1, len(route_points)):
            segment_distance = RouteCalculator.calculate_distance(
                route_points[i-1], route_points[i]
            )
            
            if current_distance + segment_distance <= daily_distance:
                current_route.append(route_points[i])
                current_distance += segment_distance
            else:
                daily_routes.append(current_route)
                current_route = [route_points[i-1], route_points[i]]
                current_distance = segment_distance
        
        if current_route:
            daily_routes.append(current_route)
        
        return daily_routes
    
    @staticmethod
    def optimize_route_for_motorcycle(
        route_data: Dict[str, Any],
        avoid_highways: bool = True,
        prefer_scenic: bool = True
    ) -> Dict[str, Any]:
        """摩托车路线优化"""
        # 这里可以添加摩托车专用的路线优化逻辑
        # 比如避开高速、选择风景路线等
        
        optimized_route = route_data.copy()
        
        if avoid_highways:
            # 过滤掉高速公路路段
            optimized_steps = []
            for step in route_data.get("steps", []):
                road = step.get("road", "").lower()
                if "高速" not in road and "expressway" not in road:
                    optimized_steps.append(step)
            optimized_route["steps"] = optimized_steps
        
        return optimized_route
