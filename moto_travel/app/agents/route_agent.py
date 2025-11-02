"""
路线规划Agent
基于高德地图API实现摩托车路线规划
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.agents.base_agent import AsyncAgent, AgentResponse, AgentType
from tools.map_tools import AmapTool, RouteCalculator
from tools.cache_tools import RedisCache
from app.config import settings
from loguru import logger


class RouteAgent(AsyncAgent):
    """路线规划Agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.ROUTE,
            name="route_agent",
            description="路线规划Agent，提供摩托车专用路线规划服务"
        )
        self.amap_tool = AmapTool()
        self.route_calculator = RouteCalculator()
        self.cache = RedisCache()
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行路线规划"""
        query = kwargs.get("query", "")
        origin = kwargs.get("origin", "")
        destination = kwargs.get("destination", "")
        waypoints = kwargs.get("waypoints", [])
        daily_distance = kwargs.get("daily_distance", settings.default_daily_distance)
        avoid_highway = kwargs.get("avoid_highway", False)
        user_id = kwargs.get("user_id")
        
        try:
            # 如果没有提供起终点，尝试从查询中提取
            if not origin or not destination:
                extracted_locations = await self._extract_locations_from_query(query)
                origin = origin or extracted_locations.get("origin", "")
                destination = destination or extracted_locations.get("destination", "")
            
            if not origin or not destination:
                return self._create_error_response("请提供起点和终点")
            
            # 检查缓存
            cache_key = f"route:{origin}:{destination}:{daily_distance}:{avoid_highway}"
            cached_result = await self.cache.get_cached_route_data(origin, destination)
            
            if cached_result["success"]:
                logger.info("Using cached route data")
                return self._create_success_response(
                    data=cached_result["data"],
                    message="使用缓存的路线数据"
                )
            
            # 执行路线规划
            route_result = await self._plan_route(
                origin=origin,
                destination=destination,
                waypoints=waypoints,
                daily_distance=daily_distance,
                avoid_highway=avoid_highway
            )
            
            if not route_result["success"]:
                return self._create_error_response(route_result["message"])
            
            # 缓存结果
            await self.cache.cache_route_data(origin, destination, route_result["data"])
            
            return self._create_success_response(
                data=route_result["data"],
                message="路线规划完成",
                metadata={
                    "origin": origin,
                    "destination": destination,
                    "daily_distance": daily_distance,
                    "avoid_highway": avoid_highway,
                    "user_id": user_id
                }
            )
            
        except Exception as e:
            logger.error(f"Route planning failed: {str(e)}")
            return self._create_error_response(f"路线规划失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        # 至少需要查询或起终点
        has_query = bool(kwargs.get("query", ""))
        has_locations = bool(kwargs.get("origin", "")) and bool(kwargs.get("destination", ""))
        
        return has_query or has_locations
    
    async def _extract_locations_from_query(self, query: str) -> Dict[str, str]:
        """从查询中提取地点信息"""
        # 简单的正则表达式提取
        import re
        
        # 匹配"从...到..."模式
        pattern = r"从(.+?)到(.+?)(?:\s|$)"
        match = re.search(pattern, query)
        
        if match:
            return {
                "origin": match.group(1).strip(),
                "destination": match.group(2).strip()
            }
        
        # 匹配"...到..."模式
        pattern = r"(.+?)到(.+?)(?:\s|$)"
        match = re.search(pattern, query)
        
        if match:
            return {
                "origin": match.group(1).strip(),
                "destination": match.group(2).strip()
            }
        
        return {}
    
    async def _plan_route(
        self,
        origin: str,
        destination: str,
        waypoints: List[str] = None,
        daily_distance: int = 300,
        avoid_highway: bool = False
    ) -> Dict[str, Any]:
        """规划路线"""
        
        async with self.amap_tool:
            # 1. 地理编码
            origin_geocode = await self.amap_tool.geocode(origin)
            if not origin_geocode["success"]:
                return {"success": False, "message": f"起点地理编码失败: {origin}"}
            
            dest_geocode = await self.amap_tool.geocode(destination)
            if not dest_geocode["success"]:
                return {"success": False, "message": f"终点地理编码失败: {destination}"}
            
            # 2. 路线规划
            origin_coords = f"{origin_geocode['data']['longitude']},{origin_geocode['data']['latitude']}"
            dest_coords = f"{dest_geocode['data']['longitude']},{dest_geocode['data']['latitude']}"
            
            # 选择路线策略
            strategy = 3 if avoid_highway else 0  # 3=不走高速, 0=速度优先
            
            route_result = await self.amap_tool.get_route(
                origin=origin_coords,
                destination=dest_coords,
                waypoints=waypoints,
                strategy=strategy
            )
            
            if not route_result["success"]:
                return {"success": False, "message": "路线规划失败"}
            
            route_data = route_result["data"]
            
            # 3. 路线分段
            daily_routes = await self._split_route_by_daily_distance(
                route_data, daily_distance
            )
            
            # 4. 优化路线
            optimized_route = self.route_calculator.optimize_route_for_motorcycle(
                route_data, avoid_highway=avoid_highway
            )
            
            # 5. 构建完整结果
            result = {
                "origin": {
                    "name": origin,
                    "coordinates": {
                        "longitude": origin_geocode['data']['longitude'],
                        "latitude": origin_geocode['data']['latitude']
                    },
                    "address": origin_geocode['data']['formatted_address']
                },
                "destination": {
                    "name": destination,
                    "coordinates": {
                        "longitude": dest_geocode['data']['longitude'],
                        "latitude": dest_geocode['data']['latitude']
                    },
                    "address": dest_geocode['data']['formatted_address']
                },
                "route_summary": {
                    "total_distance": route_data["distance"],
                    "total_duration": route_data["duration"],
                    "total_distance_km": round(route_data["distance"] / 1000, 2),
                    "total_duration_hours": round(route_data["duration"] / 3600, 2),
                    "tolls": route_data.get("tolls", 0),
                    "traffic_lights": route_data.get("traffic_lights", 0)
                },
                "route_details": {
                    "steps": route_data["steps"],
                    "strategy": "避开高速" if avoid_highway else "速度优先"
                },
                "daily_routes": daily_routes,
                "motorcycle_optimized": optimized_route,
                "recommendations": await self._generate_route_recommendations(
                    route_data, daily_routes
                )
            }
            
            return {"success": True, "data": result}
    
    async def _split_route_by_daily_distance(
        self, 
        route_data: Dict[str, Any], 
        daily_distance: int
    ) -> List[Dict[str, Any]]:
        """按日行距离分割路线"""
        
        total_distance = route_data["distance"] / 1000  # 转换为公里
        total_duration = route_data["duration"] / 3600  # 转换为小时
        
        # 计算需要天数
        days_needed = max(1, int(total_distance / daily_distance))
        if total_distance % daily_distance > daily_distance * 0.3:  # 如果剩余距离超过30%，增加一天
            days_needed += 1
        
        daily_routes = []
        
        for day in range(days_needed):
            day_distance = min(daily_distance, total_distance - day * daily_distance)
            day_duration = (day_distance / total_distance) * total_duration
            
            daily_route = {
                "day": day + 1,
                "distance_km": round(day_distance, 2),
                "duration_hours": round(day_duration, 2),
                "estimated_start_time": "08:00",
                "estimated_end_time": self._calculate_end_time(day_duration),
                "recommendations": {
                    "fuel_stops": self._recommend_fuel_stops(day_distance),
                    "rest_stops": self._recommend_rest_stops(day_duration),
                    "accommodation": "建议在终点附近寻找住宿" if day < days_needed - 1 else "行程结束"
                }
            }
            
            daily_routes.append(daily_route)
        
        return daily_routes
    
    def _calculate_end_time(self, duration_hours: float) -> str:
        """计算结束时间"""
        start_hour = 8  # 8点开始
        end_hour = start_hour + int(duration_hours)
        end_minute = int((duration_hours % 1) * 60)
        
        if end_hour >= 24:
            end_hour -= 24
        
        return f"{end_hour:02d}:{end_minute:02d}"
    
    def _recommend_fuel_stops(self, distance_km: float) -> List[str]:
        """推荐加油点"""
        recommendations = []
        
        if distance_km > 200:
            recommendations.append("建议在路线中点寻找加油站")
        if distance_km > 400:
            recommendations.append("建议在路线1/3和2/3处寻找加油站")
        
        return recommendations
    
    def _recommend_rest_stops(self, duration_hours: float) -> List[str]:
        """推荐休息点"""
        recommendations = []
        
        if duration_hours > 2:
            recommendations.append("建议每2小时休息一次")
        if duration_hours > 4:
            recommendations.append("建议在路线中点进行长时间休息")
        if duration_hours > 6:
            recommendations.append("建议分多次休息，避免疲劳驾驶")
        
        return recommendations
    
    async def _generate_route_recommendations(
        self, 
        route_data: Dict[str, Any], 
        daily_routes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成路线建议"""
        
        total_distance = route_data["distance"] / 1000
        total_duration = route_data["duration"] / 3600
        
        recommendations = {
            "safety": [],
            "planning": [],
            "equipment": [],
            "weather": []
        }
        
        # 安全建议
        if total_distance > 500:
            recommendations["safety"].append("长途骑行，建议结伴出行")
        if total_duration > 8:
            recommendations["safety"].append("长时间骑行，注意休息和补充水分")
        
        # 规划建议
        if len(daily_routes) > 1:
            recommendations["planning"].append(f"建议分{len(daily_routes)}天完成行程")
        recommendations["planning"].append("提前预订住宿，避免旺季无房")
        
        # 装备建议
        recommendations["equipment"].append("携带必要的维修工具和备件")
        recommendations["equipment"].append("准备充足的防护装备")
        
        # 天气建议
        recommendations["weather"].append("出行前关注天气预报")
        recommendations["weather"].append("准备雨具和保暖衣物")
        
        return recommendations
