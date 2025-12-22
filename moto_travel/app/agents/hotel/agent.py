"""
酒店住宿Agent（新架构）
支持多数据源、ReAct模式、用户认证
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from app.agents.base.agent import BaseAgent, AgentResponse
from app.agents.base.message import RequestMessage, ResponseMessage, MessagePriority
from app.agents.hotel.tools.meituan_tool import MeituanHotelTool
from app.agents.hotel.tools.ctrip_tool import CtripHotelTool
from app.agents.hotel.tools.tongcheng_tool import TongchengHotelTool
from app.agents.hotel.tools.qunar_tool import QunarHotelTool
from app.agents.hotel.tools.fliggy_tool import FliggyHotelTool
from app.agents.hotel.tools.hotel_analyzer import HotelAnalyzer
from app.agents.hotel.tools.hotel_filter import HotelFilter
from app.services.auth_service import AuthService


class HotelAgent(BaseAgent):
    """酒店住宿Agent - 支持多数据源和ReAct模式"""
    
    # 支持的数据源
    AVAILABLE_SOURCES = ["meituan", "ctrip", "tongcheng", "qunar", "fliggy"]
    
    def __init__(self):
        super().__init__(
            name="hotel",
            description="酒店住宿Agent，提供酒店查询、筛选、预订、退订服务，支持多数据源和ReAct模式"
        )
        
        # 初始化数据源工具
        self.tools = {
            "meituan": MeituanHotelTool(),
            "ctrip": CtripHotelTool(),
            "tongcheng": TongchengHotelTool(),
            "qunar": QunarHotelTool(),
            "fliggy": FliggyHotelTool()
        }
        
        self.analyzer = HotelAnalyzer()
        self.filter = HotelFilter()
        self.auth_service = AuthService()
        
        # 注册A2A动作处理器
        self.register_action_handler("search_hotels", self._handle_search_hotels)
        self.register_action_handler("get_hotel_details", self._handle_get_hotel_details)
        self.register_action_handler("book_hotel", self._handle_book_hotel)
        self.register_action_handler("cancel_booking", self._handle_cancel_booking)
        self.register_action_handler("react_query", self._handle_react_query)
    
    async def handle_request(self, request: RequestMessage) -> ResponseMessage:
        """处理A2A请求"""
        action = request.action
        payload = request.payload
        
        try:
            if action == "search_hotels":
                result = await self._handle_search_hotels(payload)
            elif action == "get_hotel_details":
                result = await self._handle_get_hotel_details(payload)
            elif action == "book_hotel":
                result = await self._handle_book_hotel(payload)
            elif action == "cancel_booking":
                result = await self._handle_cancel_booking(payload)
            elif action == "react_query":
                result = await self._handle_react_query(payload)
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
            logger.error(f"Hotel agent error: {str(e)}")
            return ResponseMessage(
                from_agent=self.name,
                to_agent=request.from_agent,
                action=action,
                success=False,
                error=str(e),
                original_request_id=request.request_id,
                payload={}
            )
    
    async def _handle_search_hotels(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理酒店搜索请求"""
        city = payload.get("city")
        check_in_date = payload.get("check_in_date")
        check_out_date = payload.get("check_out_date")
        sources = payload.get("sources", self.AVAILABLE_SOURCES)  # 默认全选
        filters = payload.get("filters", {})
        user_token = payload.get("user_token")
        
        if not all([city, check_in_date, check_out_date]):
            raise ValueError("city, check_in_date, check_out_date are required")
        
        # 确保sources是列表
        if isinstance(sources, str):
            sources = [sources]
        
        # 验证数据源
        sources = [s for s in sources if s in self.AVAILABLE_SOURCES]
        if not sources:
            sources = self.AVAILABLE_SOURCES  # 默认全选
        
        # 并行搜索多个数据源
        results = []
        for source in sources:
            tool = self.tools.get(source)
            if tool:
                try:
                    async with tool:
                        result = await tool.search_hotels(
                            city=city,
                            check_in_date=check_in_date,
                            check_out_date=check_out_date,
                            latitude=payload.get("latitude"),
                            longitude=payload.get("longitude"),
                            price_min=filters.get("price_min"),
                            price_max=filters.get("price_max"),
                            star_level=filters.get("star_level"),
                            keyword=payload.get("keyword"),
                            page=payload.get("page", 1),
                            page_size=payload.get("page_size", 20),
                            user_token=user_token
                        )
                        if result.get("success"):
                            results.append(result)
                except Exception as e:
                    logger.error(f"Search failed for {source}: {str(e)}")
        
        # 合并结果
        all_hotels = self.filter.merge_results_from_multiple_sources(results)
        
        # 应用筛选
        if filters:
            all_hotels = self.filter.filter_hotels(all_hotels, filters)
        
        # 分析适合摩旅的酒店
        preferences = payload.get("preferences", {})
        analyzed = self.analyzer.analyze_hotels_for_moto_travel(all_hotels, preferences)
        
        return {
            "hotels": analyzed["hotels"],
            "total": analyzed["total"],
            "suitable_count": analyzed["suitable_count"],
            "sources_used": sources,
            "filters_applied": filters
        }
    
    async def _handle_get_hotel_details(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理获取酒店详情请求"""
        hotel_id = payload.get("hotel_id")
        source = payload.get("source", "meituan")
        check_in_date = payload.get("check_in_date")
        check_out_date = payload.get("check_out_date")
        user_token = payload.get("user_token")
        
        if not all([hotel_id, check_in_date, check_out_date]):
            raise ValueError("hotel_id, check_in_date, check_out_date are required")
        
        tool = self.tools.get(source)
        if not tool:
            raise ValueError(f"Unknown source: {source}")
        
        async with tool:
            result = await tool.get_hotel_details(
                hotel_id=hotel_id,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                user_token=user_token
            )
        
        if not result.get("success"):
            raise ValueError(result.get("message", "Failed to get hotel details"))
        
        return result["data"]
    
    async def _handle_book_hotel(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理酒店预订请求"""
        # 需要用户认证
        user_token = payload.get("user_token")
        if not user_token:
            raise ValueError("User authentication required")
        
        # 验证用户
        user = await self.auth_service.get_user_by_token(user_token)
        if not user:
            raise ValueError("Invalid user token")
        
        hotel_id = payload.get("hotel_id")
        source = payload.get("source", "meituan")
        room_type_id = payload.get("room_type_id")
        check_in_date = payload.get("check_in_date")
        check_out_date = payload.get("check_out_date")
        guest_name = payload.get("guest_name")
        guest_phone = payload.get("guest_phone")
        num_rooms = payload.get("num_rooms", 1)
        
        if not all([hotel_id, room_type_id, check_in_date, check_out_date, guest_name, guest_phone]):
            raise ValueError("Missing required booking parameters")
        
        tool = self.tools.get(source)
        if not tool:
            raise ValueError(f"Unknown source: {source}")
        
        async with tool:
            result = await tool.book_hotel(
                hotel_id=hotel_id,
                room_type_id=room_type_id,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                guest_name=guest_name,
                guest_phone=guest_phone,
                num_rooms=num_rooms,
                user_token=user_token
            )
        
        if not result.get("success"):
            raise ValueError(result.get("message", "Booking failed"))
        
        return result["data"]
    
    async def _handle_cancel_booking(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理取消预订请求"""
        user_token = payload.get("user_token")
        if not user_token:
            raise ValueError("User authentication required")
        
        order_id = payload.get("order_id")
        source = payload.get("source", "meituan")
        
        if not order_id:
            raise ValueError("order_id is required")
        
        tool = self.tools.get(source)
        if not tool:
            raise ValueError(f"Unknown source: {source}")
        
        async with tool:
            result = await tool.cancel_booking(
                order_id=order_id,
                user_token=user_token
            )
        
        if not result.get("success"):
            raise ValueError(result.get("message", "Cancel failed"))
        
        return result["data"]
    
    async def _handle_react_query(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理ReAct模式查询"""
        query = payload.get("query")
        user_token = payload.get("user_token")
        max_iterations = payload.get("max_iterations", 5)
        
        if not query:
            raise ValueError("query is required")
        
        # ReAct循环：思考 -> 行动 -> 观察
        thoughts = []
        actions = []
        observations = []
        
        current_query = query
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # 思考阶段：分析查询，决定下一步行动
            thought = self._think(current_query, thoughts, actions, observations)
            thoughts.append(thought)
            
            # 如果思考结果是最终答案，返回
            if thought.get("action") == "final_answer":
                return {
                    "answer": thought.get("answer"),
                    "thoughts": thoughts,
                    "actions": actions,
                    "observations": observations
                }
            
            # 行动阶段：执行动作
            action = thought.get("action")
            action_params = thought.get("params", {})
            action_params["user_token"] = user_token
            
            if action == "search_hotels":
                result = await self._handle_search_hotels(action_params)
            elif action == "get_hotel_details":
                result = await self._handle_get_hotel_details(action_params)
            elif action == "ask_user":
                # 询问用户
                return {
                    "action": "ask_user",
                    "question": action_params.get("question"),
                    "thoughts": thoughts,
                    "actions": actions,
                    "observations": observations
                }
            else:
                result = {"error": f"Unknown action: {action}"}
            
            actions.append({"action": action, "params": action_params})
            observations.append(result)
            
            # 更新当前查询
            current_query = f"Based on: {result}, continue to answer: {query}"
        
        # 达到最大迭代次数
        return {
            "answer": "无法完成查询，已达到最大迭代次数",
            "thoughts": thoughts,
            "actions": actions,
            "observations": observations
        }
    
    def _think(
        self,
        query: str,
        thoughts: List[Dict],
        actions: List[Dict],
        observations: List[Dict]
    ) -> Dict[str, Any]:
        """思考阶段：分析查询并决定下一步行动"""
        # 简单的规则引擎（实际应该使用LLM）
        
        # 检查是否需要更多信息
        if "预算" in query or "价格" in query:
            if not any("budget" in str(obs) for obs in observations):
                return {
                    "action": "ask_user",
                    "params": {"question": "请问您的预算范围是多少？"},
                    "reasoning": "需要了解用户预算"
                }
        
        if "房型" in query or "房间" in query:
            if not any("room_type" in str(obs) for obs in observations):
                return {
                    "action": "ask_user",
                    "params": {"question": "您希望什么房型？（双床、大床、单人床、青旅、连锁、民宿等）"},
                    "reasoning": "需要了解用户房型偏好"
                }
        
        # 如果有足够的观察结果，生成最终答案
        if len(observations) > 0:
            last_obs = observations[-1]
            if "hotels" in last_obs:
                return {
                    "action": "final_answer",
                    "answer": f"找到{last_obs.get('total', 0)}个酒店，其中{last_obs.get('suitable_count', 0)}个适合摩旅",
                    "reasoning": "已有足够的酒店信息"
                }
        
        # 默认执行搜索
        return {
            "action": "search_hotels",
            "params": {},
            "reasoning": "需要搜索酒店"
        }
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行酒店查询（兼容旧接口）"""
        try:
            query = kwargs.get("query", "")
            action = kwargs.get("action", "search")
            
            if action == "react_query":
                result = await self._handle_react_query({
                    "query": query,
                    "user_token": kwargs.get("user_token")
                })
            else:
                # 默认搜索
                result = await self._handle_search_hotels({
                    "city": kwargs.get("city", ""),
                    "check_in_date": kwargs.get("check_in_date"),
                    "check_out_date": kwargs.get("check_out_date"),
                    "sources": kwargs.get("sources", self.AVAILABLE_SOURCES),
                    "filters": kwargs.get("filters", {}),
                    "preferences": kwargs.get("preferences", {}),
                    "user_token": kwargs.get("user_token")
                })
            
            return self._create_success_response(
                data=result,
                message="酒店查询完成",
                metadata={
                    "action": action,
                    "user_id": kwargs.get("user_id")
                }
            )
        except Exception as e:
            logger.error(f"Hotel query failed: {str(e)}")
            return self._create_error_response(f"酒店查询失败: {str(e)}")

