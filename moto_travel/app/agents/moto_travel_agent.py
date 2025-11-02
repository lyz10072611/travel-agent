"""
摩旅智能助手主Agent
集成所有功能模块，提供完整的摩旅规划服务
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.agents.base_agent import AsyncAgent, AgentResponse, AgentType
from app.agents.router import AgentRouter
from app.templates.output_templates import MotoTravelPlan, OutputFormatter, OutputFormat
from app.templates.moto_travel_prompt import MotoTravelPromptTemplate
from loguru import logger


class MotoTravelAgent(AsyncAgent):
    """摩旅智能助手主Agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.ROUTE,  # 使用ROUTE作为主类型
            name="moto_travel_agent",
            description="摩旅智能助手主Agent，提供完整的摩旅规划服务"
        )
        self.agent_router = AgentRouter()
        self.output_formatter = OutputFormatter()
        self.prompt_template = MotoTravelPromptTemplate()
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行摩旅规划"""
        query = kwargs.get("query", "")
        user_id = kwargs.get("user_id", "")
        output_format = kwargs.get("output_format", "markdown")
        preferences = kwargs.get("preferences", {})
        
        try:
            if not query:
                return self._create_error_response("请提供摩旅规划需求")
            
            # 1. 分析用户需求
            user_requirements = await self._analyze_user_requirements(query, preferences)
            
            # 2. 执行多Agent协作规划
            planning_results = await self._execute_multi_agent_planning(
                user_requirements, user_id
            )
            
            # 3. 整合规划结果
            integrated_plan = await self._integrate_planning_results(
                user_requirements, planning_results
            )
            
            # 4. 生成最终输出
            if output_format.lower() == "json":
                final_output = self.output_formatter.format_output(
                    integrated_plan, OutputFormat.JSON
                )
            else:
                final_output = self.output_formatter.format_output(
                    integrated_plan, OutputFormat.MARKDOWN
                )
            
            return self._create_success_response(
                data=final_output,
                message="摩旅规划完成",
                metadata={
                    "user_id": user_id,
                    "output_format": output_format,
                    "plan_id": integrated_plan.plan_id,
                    "total_distance": integrated_plan.total_distance_km,
                    "total_days": integrated_plan.total_duration_days,
                    "total_budget": integrated_plan.total_budget
                }
            )
            
        except Exception as e:
            logger.error(f"Moto travel planning failed: {str(e)}")
            return self._create_error_response(f"摩旅规划失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        return self._validate_required_params(["query"], **kwargs)
    
    async def _analyze_user_requirements(
        self, 
        query: str, 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析用户需求"""
        
        # 这里可以使用LLM来分析用户需求
        # 暂时使用简单的规则提取
        
        requirements = {
            "origin": "",
            "destination": "",
            "waypoints": [],
            "start_date": "",
            "duration_days": 0,
            "daily_distance": 300,
            "route_type": "自然风光",
            "travel_style": "休闲",
            "budget_range": 5000,
            "companions": "独自",
            "special_requirements": [],
            "interests": []
        }
        
        # 简单的关键词提取
        if "从" in query and "到" in query:
            parts = query.split("到")
            if len(parts) >= 2:
                requirements["origin"] = parts[0].replace("从", "").strip()
                requirements["destination"] = parts[1].split()[0].strip()
        
        # 从偏好中提取信息
        if preferences:
            requirements.update(preferences)
        
        return requirements
    
    async def _execute_multi_agent_planning(
        self, 
        requirements: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """执行多Agent协作规划"""
        
        results = {}
        
        try:
            # 1. 路线规划
            if requirements.get("origin") and requirements.get("destination"):
                route_result = await self.agent_router.execute(
                    query=f"从{requirements['origin']}到{requirements['destination']}的路线规划",
                    origin=requirements["origin"],
                    destination=requirements["destination"],
                    daily_distance=requirements.get("daily_distance", 300),
                    user_id=user_id
                )
                results["route"] = route_result
            
            # 2. 天气查询
            weather_locations = [requirements.get("origin"), requirements.get("destination")]
            weather_results = {}
            for location in weather_locations:
                if location:
                    weather_result = await self.agent_router.execute(
                        query=f"{location}的天气",
                        location=location,
                        days=requirements.get("duration_days", 7),
                        user_id=user_id
                    )
                    weather_results[location] = weather_result
            results["weather"] = weather_results
            
            # 3. POI查询
            poi_locations = [requirements.get("origin"), requirements.get("destination")]
            poi_results = {}
            for location in poi_locations:
                if location:
                    # 查询餐厅
                    restaurant_result = await self.agent_router.execute(
                        query=f"{location}的餐厅",
                        location=location,
                        poi_type="restaurant",
                        user_id=user_id
                    )
                    
                    # 查询住宿
                    hotel_result = await self.agent_router.execute(
                        query=f"{location}的酒店",
                        location=location,
                        poi_type="hotel",
                        user_id=user_id
                    )
                    
                    # 查询加油站
                    gas_result = await self.agent_router.execute(
                        query=f"{location}的加油站",
                        location=location,
                        poi_type="gas_station",
                        user_id=user_id
                    )
                    
                    poi_results[location] = {
                        "restaurants": restaurant_result,
                        "hotels": hotel_result,
                        "gas_stations": gas_result
                    }
            results["poi"] = poi_results
            
            # 4. 预算计算
            if results.get("route") and results["route"].success:
                route_data = results["route"].data
                total_distance = route_data.get("route_summary", {}).get("total_distance_km", 0)
                total_days = len(route_data.get("daily_routes", []))
                
                budget_result = await self.agent_router.execute(
                    query="计算旅行预算",
                    total_distance=total_distance,
                    days=total_days,
                    user_id=user_id
                )
                results["budget"] = budget_result
            
            # 5. 个性化推荐
            personalization_result = await self.agent_router.execute(
                query="获取个性化推荐",
                action="get_recommendations",
                user_id=user_id
            )
            results["personalization"] = personalization_result
            
        except Exception as e:
            logger.error(f"Multi-agent planning failed: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    async def _integrate_planning_results(
        self, 
        requirements: Dict[str, Any], 
        results: Dict[str, Any]
    ) -> MotoTravelPlan:
        """整合规划结果"""
        
        # 创建计划ID
        plan_id = f"moto_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 构建完整的摩旅计划
        plan = MotoTravelPlan(
            plan_id=plan_id,
            user_id=requirements.get("user_id", ""),
            title=f"从{requirements.get('origin', '')}到{requirements.get('destination', '')}的摩旅计划",
            description=requirements.get("description", "摩旅智能规划"),
            created_at=datetime.utcnow().isoformat(),
            
            # 路线信息
            origin=self._create_location_info(requirements.get("origin", "")),
            destination=self._create_location_info(requirements.get("destination", "")),
            waypoints=[self._create_location_info(wp) for wp in requirements.get("waypoints", [])],
            total_distance_km=results.get("route", {}).get("data", {}).get("route_summary", {}).get("total_distance_km", 0),
            total_duration_days=len(results.get("route", {}).get("data", {}).get("daily_routes", [])),
            route_type=requirements.get("route_type", "自然风光"),
            
            # 每日路线
            daily_routes=self._create_daily_routes(results.get("route", {})),
            
            # 天气信息
            weather_forecast=self._create_weather_forecast(results.get("weather", {})),
            weather_alerts=[],
            
            # POI信息
            restaurants=self._create_poi_list(results.get("poi", {}), "restaurants"),
            accommodations=self._create_poi_list(results.get("poi", {}), "hotels"),
            gas_stations=self._create_poi_list(results.get("poi", {}), "gas_stations"),
            repair_shops=[],
            attractions=[],
            
            # 预算信息
            total_budget=results.get("budget", {}).get("data", {}).get("total_cost", 0),
            daily_budgets=self._create_daily_budgets(results.get("budget", {})),
            budget_breakdown=results.get("budget", {}).get("data", {}).get("cost_breakdown", {}),
            
            # 安全信息
            safety_alerts=[],
            safety_recommendations=[
                "遵守交通规则，安全第一",
                "定期检查车辆状况",
                "注意天气变化，适时调整行程",
                "保持充足的休息，避免疲劳驾驶"
            ],
            
            # 个性化信息
            user_preferences=requirements,
            personalized_recommendations=results.get("personalization", {}).get("data", {}).get("recommendations", []),
            
            # 元数据
            metadata={
                "planning_time": datetime.utcnow().isoformat(),
                "agents_used": list(results.keys()),
                "success_rate": len([r for r in results.values() if hasattr(r, 'success') and r.success]) / len(results) if results else 0
            }
        )
        
        return plan
    
    def _create_location_info(self, location_name: str) -> Dict[str, Any]:
        """创建位置信息"""
        return {
            "name": location_name,
            "address": location_name,
            "coordinates": {"longitude": 0.0, "latitude": 0.0},
            "province": "",
            "city": location_name,
            "district": ""
        }
    
    def _create_daily_routes(self, route_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建每日路线"""
        daily_routes = []
        
        if route_results.get("success") and route_results.get("data"):
            route_data = route_results["data"]
            daily_route_data = route_data.get("daily_routes", [])
            
            for i, day_data in enumerate(daily_route_data):
                daily_route = {
                    "day": i + 1,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "start_location": self._create_location_info("起点"),
                    "end_location": self._create_location_info("终点"),
                    "total_distance_km": day_data.get("distance_km", 0),
                    "estimated_duration_hours": day_data.get("duration_hours", 0),
                    "segments": [],
                    "recommended_stops": day_data.get("recommendations", {}).get("fuel_stops", []),
                    "accommodation": None
                }
                daily_routes.append(daily_route)
        
        return daily_routes
    
    def _create_weather_forecast(self, weather_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建天气预报"""
        weather_forecast = []
        
        for location, result in weather_results.items():
            if result.get("success") and result.get("data"):
                weather_data = result["data"]
                current_weather = weather_data.get("current", {})
                
                weather_info = {
                    "location": location,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "temperature": current_weather.get("temperature", 0),
                    "weather_condition": current_weather.get("weather", ""),
                    "humidity": current_weather.get("humidity", 0),
                    "wind_speed": current_weather.get("wind_speed", 0),
                    "wind_direction": current_weather.get("wind_direction", ""),
                    "visibility": current_weather.get("visibility", 10),
                    "safety_score": 80,
                    "safety_level": "良好",
                    "warnings": [],
                    "recommendations": ["天气条件良好，适合骑行"]
                }
                weather_forecast.append(weather_info)
        
        return weather_forecast
    
    def _create_poi_list(self, poi_results: Dict[str, Any], poi_type: str) -> List[Dict[str, Any]]:
        """创建POI列表"""
        poi_list = []
        
        for location, location_pois in poi_results.items():
            if poi_type in location_pois:
                poi_result = location_pois[poi_type]
                if poi_result.get("success") and poi_result.get("data"):
                    pois_data = poi_result["data"]
                    if isinstance(pois_data, dict) and "pois" in pois_data:
                        for poi in pois_data["pois"]:
                            poi_info = {
                                "id": poi.get("id", ""),
                                "name": poi.get("name", ""),
                                "category": poi.get("category", ""),
                                "location": self._create_location_info(location),
                                "rating": poi.get("rating", 0),
                                "price_level": poi.get("price", ""),
                                "business_hours": poi.get("opening_hours", ""),
                                "phone": poi.get("tel", ""),
                                "website": poi.get("website", ""),
                                "description": poi.get("address", ""),
                                "features": [],
                                "distance_from_route": poi.get("distance", 0)
                            }
                            poi_list.append(poi_info)
        
        return poi_list
    
    def _create_daily_budgets(self, budget_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建每日预算"""
        daily_budgets = []
        
        if budget_results.get("success") and budget_results.get("data"):
            budget_data = budget_results["data"]
            daily_budget_data = budget_data.get("daily_budgets", [])
            
            for day_data in daily_budget_data:
                daily_budget = {
                    "day": day_data.get("day", 1),
                    "date": day_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                    "items": [],
                    "total_cost": day_data.get("total_cost", 0),
                    "currency": "CNY"
                }
                daily_budgets.append(daily_budget)
        
        return daily_budgets
