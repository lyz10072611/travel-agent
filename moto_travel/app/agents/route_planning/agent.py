"""
路径规划Agent
集成高德和百度地图，提供摩旅专用路线规划
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from app.agents.base.agent import BaseAgent, AgentResponse
from app.agents.base.message import RequestMessage, ResponseMessage
from app.agents.route_planning.tools.amap_tool import AmapTool
from app.agents.route_planning.tools.baidu_tool import BaiduMapTool
from app.agents.route_planning.strategies.moto_route_strategy import MotoRouteStrategy
from app.agents.route_planning.strategies.route_merger import RouteMerger
from app.agents.route_planning.strategies.route_preferences import (
    RoutePreferences,
    PreferenceQuestionnaire,
    HighwayPreference
)
from app.agents.route_planning.strategies.interactive_preferences import (
    InteractivePreferenceCollector,
    PreferenceInference
)


class RoutePlanningAgent(BaseAgent):
    """路径规划Agent"""
    
    def __init__(self):
        super().__init__(
            name="route_planning",
            description="路径规划Agent，集成高德和百度地图，提供摩旅专用路线规划"
        )
        self.amap_tool = AmapTool()
        self.baidu_tool = BaiduMapTool()
        self.moto_strategy = MotoRouteStrategy()
        self.route_merger = RouteMerger()
        
        # 注册A2A动作处理器
        self.register_action_handler("plan_route", self._handle_plan_route)
        self.register_action_handler("analyze_route", self._handle_analyze_route)
        self.register_action_handler("get_preference_questions", self._handle_get_preference_questions)
        self.register_action_handler("set_preferences", self._handle_set_preferences)
        self.register_action_handler("interactive_collect_preferences", self._handle_interactive_collect)
        self.register_action_handler("infer_preferences", self._handle_infer_preferences)
    
    async def handle_request(self, request: RequestMessage) -> ResponseMessage:
        """处理A2A请求"""
        action = request.action
        payload = request.payload
        
        try:
            if action == "plan_route":
                result = await self._handle_plan_route(payload)
            elif action == "analyze_route":
                result = await self._handle_analyze_route(payload)
            elif action == "get_preference_questions":
                result = await self._handle_get_preference_questions(payload)
            elif action == "set_preferences":
                result = await self._handle_set_preferences(payload)
            elif action == "interactive_collect_preferences":
                result = await self._handle_interactive_collect(payload)
            elif action == "infer_preferences":
                result = await self._handle_infer_preferences(payload)
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
            logger.error(f"Route planning agent error: {str(e)}")
            return ResponseMessage(
                from_agent=self.name,
                to_agent=request.from_agent,
                action=action,
                success=False,
                error=str(e),
                original_request_id=request.request_id,
                payload={}
            )
    
    async def _handle_plan_route(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理路线规划请求（支持用户偏好）"""
        origin = payload.get("origin")
        destination = payload.get("destination")
        waypoints = payload.get("waypoints", [])
        
        # 解析用户偏好（兼容旧接口）
        preferences_data = payload.get("preferences", {})
        if not preferences_data:
            # 兼容旧接口：avoid_highway参数
            avoid_highway = payload.get("avoid_highway", None)
            if avoid_highway is not None:
                preferences_data["highway_preference"] = "forbid" if avoid_highway else "allow"
            else:
                preferences_data["highway_preference"] = "allow"  # 默认允许
        
        # 创建偏好配置
        preferences = RoutePreferences.from_dict(preferences_data)
        
        if not origin or not destination:
            raise ValueError("Origin and destination are required")
        
        # 1. 地理编码
        async with self.amap_tool:
            origin_geo = await self.amap_tool.geocode(origin)
            dest_geo = await self.amap_tool.geocode(destination)
        
        if not origin_geo["success"] or not dest_geo["success"]:
            raise ValueError("Failed to geocode addresses")
        
        origin_coord = f"{origin_geo['data']['longitude']},{origin_geo['data']['latitude']}"
        dest_coord = f"{dest_geo['data']['longitude']},{dest_geo['data']['latitude']}"
        
        # 2. 并行获取高德和百度路线（根据用户偏好）
        amap_route = None
        baidu_route = None
        
        # 根据偏好选择策略
        strategy = preferences.get_highway_strategy()
        tactics = preferences.get_highway_tactics()
        
        async with self.amap_tool:
            amap_result = await self.amap_tool.get_route(
                origin=origin_coord,
                destination=dest_coord,
                waypoints=waypoints,
                strategy=strategy
            )
            if amap_result["success"]:
                amap_route = amap_result["data"]
        
        async with self.baidu_tool:
            baidu_result = await self.baidu_tool.get_route(
                origin=f"{origin_geo['data']['latitude']},{origin_geo['data']['longitude']}",  # 百度是纬度,经度
                destination=f"{dest_geo['data']['latitude']},{dest_geo['data']['longitude']}",
                waypoints=waypoints,
                tactics=tactics
            )
            if baidu_result["success"]:
                baidu_route = baidu_result["data"]
        
        # 3. 合并路线
        if amap_route and baidu_route:
            merged_result = self.route_merger.merge_routes(amap_route, baidu_route)
        elif amap_route:
            merged_result = {"recommended_route": "amap", "final_route": amap_route}
        elif baidu_route:
            merged_result = {"recommended_route": "baidu", "final_route": baidu_route}
        else:
            raise ValueError("Failed to get route from both maps")
        
        final_route = merged_result["final_route"]
        
        # 4. 摩旅路线分析（使用用户偏好）
        moto_analysis = self.moto_strategy.analyze_route_for_moto(final_route, preferences)
        
        # 5. 加油站规划
        gas_stations = self.moto_strategy.plan_gas_stations(final_route, preferences.fuel_range_km)
        
        # 6. 禁摩检查（需要从POI Agent获取政策信息）
        # 这里先返回空，实际应该调用POI Agent检查
        
        result = {
            "origin": {
                "address": origin,
                "coordinates": {
                    "longitude": origin_geo["data"]["longitude"],
                    "latitude": origin_geo["data"]["latitude"]
                }
            },
            "destination": {
                "address": destination,
                "coordinates": {
                    "longitude": dest_geo["data"]["longitude"],
                    "latitude": dest_geo["data"]["latitude"]
                }
            },
            "route_comparison": merged_result,
            "final_route": {
                "distance_km": round(final_route.get("distance", 0) / 1000, 2),
                "duration_min": round(final_route.get("duration", 0) / 60, 2),
                "steps": final_route.get("steps", []),
                "steps_count": len(final_route.get("steps", []))
            },
            "moto_analysis": moto_analysis,
            "gas_stations": gas_stations,
            "recommendations": merged_result.get("suggestions", []) + moto_analysis.get("recommendations", [])
        }
        
        return result
    
    async def _handle_analyze_route(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """分析路线（支持用户偏好）"""
        route_data = payload.get("route_data")
        if not route_data:
            raise ValueError("route_data is required")
        
        preferences_data = payload.get("preferences", {})
        preferences = RoutePreferences.from_dict(preferences_data) if preferences_data else RoutePreferences()
        
        analysis = self.moto_strategy.analyze_route_for_moto(route_data, preferences)
        return analysis
    
    async def _handle_get_preference_questions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """获取偏好问卷问题（支持交互式询问）"""
        required_only = payload.get("required_only", False)
        category = payload.get("category", "all")  # all, core, advanced
        
        questionnaire = PreferenceQuestionnaire()
        
        if category == "core" or required_only:
            questions = questionnaire.get_required_questions()
        elif category == "advanced":
            questions = questionnaire.get_optional_questions()
        else:  # all
            questions = questionnaire.get_required_questions()
            questions.extend(questionnaire.get_optional_questions())
        
        return {
            "questions": questions,
            "total": len(questions),
            "category": category,
            "message": "请回答以下问题以配置路线规划偏好"
        }
    
    async def _handle_set_preferences(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """设置用户偏好"""
        answers = payload.get("answers", {})
        
        questionnaire = PreferenceQuestionnaire()
        preferences = questionnaire.parse_answers(answers)
        
        return {
            "preferences": preferences.to_dict(),
            "message": "偏好设置成功",
            "summary": {
                "highway_preference": preferences.highway_preference.value,
                "avoid_national_road_at_night": preferences.avoid_national_road_at_night,
                "fuel_range_km": preferences.fuel_range_km
            }
        }
    
    async def _handle_interactive_collect(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """交互式收集偏好"""
        action = payload.get("action", "get_next")  # get_next, answer, complete
        collector_id = payload.get("collector_id", "default")
        context = payload.get("context", {})
        
        # 这里应该使用session或缓存存储collector，简化实现使用类变量
        if not hasattr(self, "_collectors"):
            self._collectors = {}
        
        if collector_id not in self._collectors:
            self._collectors[collector_id] = InteractivePreferenceCollector()
        
        collector = self._collectors[collector_id]
        
        if action == "get_next":
            # 获取下一个问题
            question = collector.get_next_question(context)
            if question:
                return {
                    "has_question": True,
                    "question": question,
                    "remaining": collector.get_remaining_count(),
                    "is_complete": collector.is_complete()
                }
            else:
                # 所有问题已回答，构建偏好
                preferences = collector.build_preferences()
                return {
                    "has_question": False,
                    "is_complete": True,
                    "preferences": preferences.to_dict(),
                    "summary": collector.get_summary()
                }
        
        elif action == "answer":
            # 回答问题
            key = payload.get("key")
            value = payload.get("value")
            
            if not key or value is None:
                raise ValueError("key and value are required")
            
            result = collector.answer_question(key, value)
            
            # 检查是否完成
            if collector.is_complete():
                preferences = collector.build_preferences()
                return {
                    "answered": result,
                    "is_complete": True,
                    "preferences": preferences.to_dict(),
                    "summary": collector.get_summary()
                }
            else:
                # 获取下一个问题
                next_question = collector.get_next_question(context)
                return {
                    "answered": result,
                    "is_complete": False,
                    "next_question": next_question,
                    "remaining": collector.get_remaining_count()
                }
        
        elif action == "complete":
            # 完成收集，构建偏好
            preferences = collector.build_preferences()
            return {
                "is_complete": True,
                "preferences": preferences.to_dict(),
                "summary": collector.get_summary()
            }
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _handle_infer_preferences(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """从查询中推断偏好"""
        query = payload.get("query", "")
        
        if not query:
            raise ValueError("query is required")
        
        inferred = PreferenceInference.infer_from_query(query)
        
        # 构建偏好配置
        questionnaire = PreferenceQuestionnaire()
        preferences = questionnaire.parse_answers(inferred)
        
        return {
            "inferred": inferred,
            "preferences": preferences.to_dict(),
            "message": "已从查询中推断偏好，您可以进一步调整"
        }
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行路线规划（兼容旧接口）"""
        try:
            origin = kwargs.get("origin")
            destination = kwargs.get("destination")
            
            if not origin or not destination:
                return self._create_error_response("请提供起点和终点")
            
            # 兼容旧接口：转换参数（默认允许走高速）
            preferences_data = kwargs.get("preferences", {})
            if not preferences_data:
                # 兼容旧接口
                avoid_highway = kwargs.get("avoid_highway", None)
                if avoid_highway is not None:
                    preferences_data["highway_preference"] = "forbid" if avoid_highway else "allow"
                else:
                    preferences_data["highway_preference"] = "allow"  # 默认允许（灵活标准）
                preferences_data["fuel_range_km"] = kwargs.get("fuel_range", 300)
            
            result = await self._handle_plan_route({
                "origin": origin,
                "destination": destination,
                "waypoints": kwargs.get("waypoints", []),
                "preferences": preferences_data
            })
            
            return self._create_success_response(
                data=result,
                message="路线规划完成",
                metadata={
                    "origin": origin,
                    "destination": destination,
                    "user_id": kwargs.get("user_id")
                }
            )
        except Exception as e:
            logger.error(f"Route planning failed: {str(e)}")
            return self._create_error_response(f"路线规划失败: {str(e)}")

