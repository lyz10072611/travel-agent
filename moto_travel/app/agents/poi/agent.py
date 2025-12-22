"""
POI查询Agent（重构版）
支持A2A协议，包含禁摩政策检查
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from app.agents.base.agent import BaseAgent, AgentResponse
from app.agents.base.message import RequestMessage, ResponseMessage
from app.agents.poi.tools.poi_tool import POITool
from app.agents.poi.tools.poi_analyzer import POIAnalyzer
from app.agents.poi.tools.policy_checker import PolicyChecker


class POIAgent(BaseAgent):
    """POI查询Agent"""
    
    def __init__(self):
        super().__init__(
            name="poi",
            description="POI查询Agent，提供餐饮、住宿、修车、加油站等本地服务查询，支持禁摩政策检查"
        )
        self.poi_tool = POITool()
        self.poi_analyzer = POIAnalyzer()
        self.policy_checker = PolicyChecker()
        
        # 注册A2A动作处理器
        self.register_action_handler("search_poi", self._handle_search_poi)
        self.register_action_handler("check_policy", self._handle_check_policy)
        self.register_action_handler("find_gas_stations", self._handle_find_gas_stations)
    
    async def handle_request(self, request: RequestMessage) -> ResponseMessage:
        """处理A2A请求"""
        action = request.action
        payload = request.payload
        
        try:
            if action == "search_poi":
                result = await self._handle_search_poi(payload)
            elif action == "check_policy":
                result = await self._handle_check_policy(payload)
            elif action == "find_gas_stations":
                result = await self._handle_find_gas_stations(payload)
            else:
                return ResponseMessage(
                    from_agent=self.name,
                    to_agent=request.from_agent,
                    action=action,
                    success=False,
                    error=f"Unknown action: {action}",
                    original_request_id=request.request_id,
                    payload={}
                )
            
            return ResponseMessage(
                from_agent=self.name,
                to_agent=request.from_agent,
                action=action,
                success=True,
                payload=result if isinstance(result, dict) else {"result": result},
                original_request_id=request.request_id
            )
        except Exception as e:
            logger.error(f"POI agent error: {str(e)}")
            return ResponseMessage(
                from_agent=self.name,
                to_agent=request.from_agent,
                action=action,
                success=False,
                error=str(e),
                original_request_id=request.request_id,
                payload={}
            )
    
    async def _handle_search_poi(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理POI搜索请求"""
        location = payload.get("location")
        poi_type = payload.get("poi_type", "all")
        radius = payload.get("radius", 5000)
        
        if not location:
            raise ValueError("Location is required")
        
        async with self.poi_tool:
            if poi_type == "gas_station" or poi_type == "加油站":
                result = await self.poi_tool.search_gas_stations(location, radius)
            elif poi_type == "restaurant" or poi_type == "餐厅":
                result = await self.poi_tool.search_restaurants(location, radius)
            elif poi_type == "hotel" or poi_type == "酒店":
                result = await self.poi_tool.search_hotels(location, radius)
            elif poi_type == "repair_shop" or poi_type == "修车":
                result = await self.poi_tool.search_repair_shops(location, radius)
            else:
                # 通用搜索
                result = await self.poi_tool.search_poi(
                    keywords=poi_type,
                    location=location,
                    radius=radius
                )
        
        if not result["success"]:
            raise ValueError(result["message"])
        
        pois = result["data"].get("pois", [])
        
        # 分析和推荐
        filtered_pois = self.poi_analyzer.filter_pois_by_distance(pois, radius)
        sorted_pois = self.poi_analyzer.sort_pois_by_priority(filtered_pois)
        
        return {
            "location": location,
            "poi_type": poi_type,
            "pois": sorted_pois[:20],  # 返回前20个
            "total": len(pois),
            "recommendations": self._generate_poi_recommendations(sorted_pois)
        }
    
    async def _handle_check_policy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理禁摩政策检查请求"""
        city = payload.get("city")
        route_segments = payload.get("route_segments", [])
        
        if city:
            # 检查城市政策
            policy = self.policy_checker.check_city_policy(city)
            return {
                "check_type": "city",
                "city": city,
                "policy": policy
            }
        elif route_segments:
            # 检查路线政策
            route_policy = self.policy_checker.check_route_policy(route_segments)
            return {
                "check_type": "route",
                "route_policy": route_policy
            }
        else:
            raise ValueError("Either city or route_segments is required")
    
    async def _handle_find_gas_stations(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理加油站查找请求"""
        location = payload.get("location")
        route_distance_km = payload.get("route_distance_km", 0)
        fuel_range_km = payload.get("fuel_range_km", 300)
        radius = payload.get("radius", 10000)
        
        if not location:
            raise ValueError("Location is required")
        
        async with self.poi_tool:
            result = await self.poi_tool.search_gas_stations(location, radius)
        
        if not result["success"]:
            raise ValueError(result["message"])
        
        gas_stations = result["data"].get("pois", [])
        
        # 如果提供了路线距离，推荐加油站位置
        recommendations = None
        if route_distance_km > 0:
            recommendations = self.poi_analyzer.recommend_gas_stations_for_route(
                route_distance_km, fuel_range_km
            )
        
        return {
            "location": location,
            "gas_stations": gas_stations[:10],  # 返回前10个
            "total": len(gas_stations),
            "recommendations": recommendations
        }
    
    def _generate_poi_recommendations(self, pois: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成POI推荐"""
        if not pois:
            return {"message": "未找到相关POI"}
        
        top_3 = pois[:3]
        return {
            "top_recommendations": top_3,
            "criteria": "基于距离和评分推荐"
        }
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行POI查询（兼容旧接口）"""
        try:
            location = kwargs.get("location") or kwargs.get("query", "")
            poi_type = kwargs.get("poi_type", "all")
            radius = kwargs.get("radius", 5000)
            
            if not location:
                return self._create_error_response("请提供查询地点")
            
            result = await self._handle_search_poi({
                "location": location,
                "poi_type": poi_type,
                "radius": radius
            })
            
            return self._create_success_response(
                data=result,
                message="POI查询完成",
                metadata={
                    "location": location,
                    "poi_type": poi_type,
                    "radius": radius,
                    "user_id": kwargs.get("user_id")
                }
            )
        except Exception as e:
            logger.error(f"POI query failed: {str(e)}")
            return self._create_error_response(f"POI查询失败: {str(e)}")

