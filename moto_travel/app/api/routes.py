"""
API路由定义
使用新架构的Agent（A2A协议）
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from app.langchain_integration import LangChainIntegration
from app.agents.route_planning import RoutePlanningAgent
from app.agents.weather import WeatherAgent
from app.agents.poi import POIAgent
from app.agents.hotel import HotelAgent
from app.agents.base.message import MessagePriority
from app.services.auth_service import AuthService
from app.database import get_db_session
from app.models.user import User
from app.models.trip import Trip

router = APIRouter()


# Pydantic模型定义
class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str = Field(..., description="用户查询内容")
    user_id: Optional[str] = Field(None, description="用户ID")
    context: Optional[Dict[str, Any]] = Field(default={}, description="上下文信息")


class QueryResponse(BaseModel):
    """查询响应模型"""
    success: bool = Field(..., description="是否成功")
    response: str = Field(..., description="响应内容")
    agent_used: Optional[str] = Field(None, description="使用的Agent")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="元数据")


class RouteRequest(BaseModel):
    """路线规划请求模型"""
    origin: str = Field(..., description="起点")
    destination: str = Field(..., description="终点")
    waypoints: Optional[List[str]] = Field(default=[], description="途经点")
    daily_distance: Optional[int] = Field(default=300, description="日行距离")
    avoid_highway: Optional[bool] = Field(default=None, description="是否避开高速（已废弃，使用preferences.highway_preference）")
    fuel_range: Optional[int] = Field(default=300, description="续航里程(km)")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="路线偏好配置（灵活标准）")
    user_id: Optional[str] = Field(None, description="用户ID")


class WeatherRequest(BaseModel):
    """天气查询请求模型"""
    location: str = Field(..., description="查询地点")
    days: Optional[int] = Field(default=7, description="查询天数")
    user_id: Optional[str] = Field(None, description="用户ID")


class POIRequest(BaseModel):
    """POI查询请求模型"""
    location: str = Field(..., description="查询地点")
    poi_type: Optional[str] = Field(default="all", description="POI类型")
    radius: Optional[int] = Field(default=5000, description="搜索半径")
    user_id: Optional[str] = Field(None, description="用户ID")


class PolicyCheckRequest(BaseModel):
    """禁摩政策检查请求模型"""
    city: Optional[str] = Field(None, description="城市名称")
    route_segments: Optional[List[Dict[str, Any]]] = Field(default=[], description="路线路段")
    user_id: Optional[str] = Field(None, description="用户ID")


class GasStationRequest(BaseModel):
    """加油站查询请求模型"""
    location: str = Field(..., description="查询地点")
    route_distance_km: Optional[float] = Field(None, description="路线总距离(km)")
    fuel_range_km: Optional[int] = Field(default=300, description="续航里程(km)")
    radius: Optional[int] = Field(default=10000, description="搜索半径")
    user_id: Optional[str] = Field(None, description="用户ID")


class PreferenceQuestionRequest(BaseModel):
    """偏好问题请求模型"""
    required_only: Optional[bool] = Field(default=False, description="仅必需问题")
    category: Optional[str] = Field(default="all", description="问题类别：all, core, advanced")


class PreferenceAnswerRequest(BaseModel):
    """偏好答案请求模型"""
    answers: Dict[str, Any] = Field(..., description="用户答案")


class InteractivePreferenceRequest(BaseModel):
    """交互式偏好收集请求模型"""
    action: str = Field(..., description="动作：get_next, answer, complete")
    collector_id: Optional[str] = Field(default="default", description="收集器ID")
    key: Optional[str] = Field(None, description="问题key（answer时必需）")
    value: Optional[Any] = Field(None, description="答案值（answer时必需）")
    context: Optional[Dict[str, Any]] = Field(default={}, description="上下文信息")


class InferPreferenceRequest(BaseModel):
    """推断偏好请求模型"""
    query: str = Field(..., description="用户查询")


# 依赖函数
async def get_langchain_integration(request: Request) -> LangChainIntegration:
    """获取LangChain集成实例"""
    return request.app.state.langchain_integration


def get_route_agent() -> RoutePlanningAgent:
    """获取路径规划Agent实例"""
    return RoutePlanningAgent()


def get_weather_agent() -> WeatherAgent:
    """获取天气Agent实例"""
    return WeatherAgent()


def get_poi_agent() -> POIAgent:
    """获取POI Agent实例"""
    return POIAgent()


def get_hotel_agent() -> HotelAgent:
    """获取酒店Agent实例"""
    return HotelAgent()


def get_auth_service() -> AuthService:
    """获取认证服务实例"""
    return AuthService()


# 通用查询接口
@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    langchain: LangChainIntegration = Depends(get_langchain_integration)
):
    """通用查询接口"""
    try:
        logger.info(f"Processing query: {request.query}")
        
        result = await langchain.process_query(
            query=request.query,
            user_id=request.user_id or "anonymous",
            thread_id=request.user_id or "default"
        )
        
        return QueryResponse(
            success=result["success"],
            response=result["response"],
            agent_used=result.get("agent_used"),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询处理失败: {str(e)}"
        )


# 路线规划接口
@router.post("/route/plan")
async def plan_route(
    request: RouteRequest,
    route_agent: RoutePlanningAgent = Depends(get_route_agent)
):
    """路线规划接口（支持灵活偏好配置）"""
    try:
        logger.info(f"Planning route from {request.origin} to {request.destination}")
        
        # 构建偏好配置
        preferences_data = request.preferences or {}
        
        # 兼容旧接口
        if request.avoid_highway is not None:
            preferences_data["highway_preference"] = "forbid" if request.avoid_highway else "allow"
        elif "highway_preference" not in preferences_data:
            preferences_data["highway_preference"] = "allow"  # 默认允许（灵活标准）
        
        if "fuel_range_km" not in preferences_data:
            preferences_data["fuel_range_km"] = request.fuel_range
        
        result = await route_agent.execute(
            origin=request.origin,
            destination=request.destination,
            waypoints=request.waypoints,
            preferences=preferences_data,
            user_id=request.user_id
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.data,
                    "message": result.message,
                    "metadata": result.metadata
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
            
    except Exception as e:
        logger.error(f"Route planning failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"路线规划失败: {str(e)}"
        )


# 偏好配置接口
@router.post("/route/preferences/questions")
async def get_preference_questions(
    request: PreferenceQuestionRequest,
    route_agent: RoutePlanningAgent = Depends(get_route_agent)
):
    """获取偏好配置问题"""
    try:
        result = await route_agent.send_request(
            to_agent="route_planning",
            action="get_preference_questions",
            payload={
                "required_only": request.required_only,
                "category": request.category
            }
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.payload,
                    "message": "获取偏好问题成功"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
    except Exception as e:
        logger.error(f"Get preference questions failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取偏好问题失败: {str(e)}"
        )


@router.post("/route/preferences/set")
async def set_preferences(
    request: PreferenceAnswerRequest,
    route_agent: RoutePlanningAgent = Depends(get_route_agent)
):
    """设置路线偏好"""
    try:
        result = await route_agent.send_request(
            to_agent="route_planning",
            action="set_preferences",
            payload={"answers": request.answers}
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.payload,
                    "message": "偏好设置成功"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
    except Exception as e:
        logger.error(f"Set preferences failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"设置偏好失败: {str(e)}"
        )


@router.post("/route/preferences/interactive")
async def interactive_collect_preferences(
    request: InteractivePreferenceRequest,
    route_agent: RoutePlanningAgent = Depends(get_route_agent)
):
    """交互式收集偏好"""
    try:
        result = await route_agent.send_request(
            to_agent="route_planning",
            action="interactive_collect_preferences",
            payload={
                "action": request.action,
                "collector_id": request.collector_id,
                "key": request.key,
                "value": request.value,
                "context": request.context
            }
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.payload,
                    "message": "交互式偏好收集完成"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
    except Exception as e:
        logger.error(f"Interactive collect preferences failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"交互式偏好收集失败: {str(e)}"
        )


@router.post("/route/preferences/infer")
async def infer_preferences(
    request: InferPreferenceRequest,
    route_agent: RoutePlanningAgent = Depends(get_route_agent)
):
    """从查询中推断偏好"""
    try:
        result = await route_agent.send_request(
            to_agent="route_planning",
            action="infer_preferences",
            payload={"query": request.query}
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.payload,
                    "message": "偏好推断完成"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
    except Exception as e:
        logger.error(f"Infer preferences failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"偏好推断失败: {str(e)}"
        )


# 天气查询接口
@router.post("/weather/query")
async def query_weather(
    request: WeatherRequest,
    weather_agent: WeatherAgent = Depends(get_weather_agent)
):
    """天气查询接口"""
    try:
        logger.info(f"Querying weather for {request.location}")
        
        result = await weather_agent.execute(
            location=request.location,
            days=request.days,
            user_id=request.user_id
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.data,
                    "message": result.message,
                    "metadata": result.metadata
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
            
    except Exception as e:
        logger.error(f"Weather query failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"天气查询失败: {str(e)}"
        )


# POI查询接口
@router.post("/poi/search")
async def search_poi(
    request: POIRequest,
    poi_agent: POIAgent = Depends(get_poi_agent)
):
    """POI查询接口"""
    try:
        logger.info(f"Searching POI in {request.location}")
        
        result = await poi_agent.execute(
            location=request.location,
            poi_type=request.poi_type,
            radius=request.radius,
            user_id=request.user_id
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.data,
                    "message": result.message,
                    "metadata": result.metadata
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
            
    except Exception as e:
        logger.error(f"POI search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"POI查询失败: {str(e)}"
        )


# 禁摩政策检查接口
@router.post("/poi/check_policy")
async def check_policy(
    request: PolicyCheckRequest,
    poi_agent: POIAgent = Depends(get_poi_agent)
):
    """禁摩政策检查接口"""
    try:
        logger.info(f"Checking policy for {request.city or 'route'}")
        
        payload = {}
        if request.city:
            payload["city"] = request.city
        if request.route_segments:
            payload["route_segments"] = request.route_segments
        
        response = await poi_agent.send_request(
            to_agent="poi",
            action="check_policy",
            payload=payload,
            priority=MessagePriority.NORMAL
        )
        
        if response.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": response.payload,
                    "message": "政策检查完成"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.error
            )
            
    except Exception as e:
        logger.error(f"Policy check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"政策检查失败: {str(e)}"
        )


# 加油站查询接口
@router.post("/poi/gas_stations")
async def find_gas_stations(
    request: GasStationRequest,
    poi_agent: POIAgent = Depends(get_poi_agent)
):
    """加油站查询接口"""
    try:
        logger.info(f"Finding gas stations near {request.location}")
        
        response = await poi_agent.send_request(
            to_agent="poi",
            action="find_gas_stations",
            payload={
                "location": request.location,
                "route_distance_km": request.route_distance_km,
                "fuel_range_km": request.fuel_range_km,
                "radius": request.radius
            },
            priority=MessagePriority.NORMAL
        )
        
        if response.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": response.payload,
                    "message": "加油站查询完成"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.error
            )
            
    except Exception as e:
        logger.error(f"Gas station search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"加油站查询失败: {str(e)}"
        )


# Agent状态接口
@router.get("/agents/status")
async def get_agents_status():
    """获取Agent状态"""
    try:
        from app.agents.base.a2a_protocol import get_a2a_protocol
        
        protocol = get_a2a_protocol()
        agents = protocol.agents
        
        status_info = {}
        for agent_name, agent_instance in agents.items():
            if hasattr(agent_instance, 'get_capabilities'):
                status_info[agent_name] = agent_instance.get_capabilities()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "data": status_info,
                "message": "获取Agent状态成功"
            }
        )
        
    except Exception as e:
        logger.error(f"Get agents status failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取Agent状态失败: {str(e)}"
        )


# 可用Agent列表接口
@router.get("/agents/available")
async def get_available_agents():
    """获取可用Agent列表"""
    try:
        from app.agents.base.a2a_protocol import get_a2a_protocol
        
        protocol = get_a2a_protocol()
        agents = list(protocol.agents.keys())
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "data": agents,
                "message": "获取可用Agent列表成功"
            }
        )
        
    except Exception as e:
        logger.error(f"Get available agents failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取可用Agent列表失败: {str(e)}"
        )


# ==================== 认证相关接口 ====================

class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., description="手机号")


class LoginRequest(BaseModel):
    """登录请求"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码")


@router.post("/auth/send_code")
async def send_verification_code(
    request: SendCodeRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """发送验证码"""
    try:
        result = await auth_service.send_verification_code(request.phone)
        
        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=result
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        logger.error(f"Send verification code failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送验证码失败: {str(e)}"
        )


@router.post("/auth/login")
async def login_with_phone(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """手机号+验证码登录"""
    try:
        result = await auth_service.login_with_phone(request.phone, request.code)
        
        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=result
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


# ==================== 酒店相关接口 ====================

class HotelSearchRequest(BaseModel):
    """酒店搜索请求"""
    city: str = Field(..., description="城市")
    check_in_date: str = Field(..., description="入住日期 (YYYY-MM-DD)")
    check_out_date: str = Field(..., description="离店日期 (YYYY-MM-DD)")
    sources: Optional[List[str]] = Field(default=None, description="数据源列表，默认全选")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    keyword: Optional[str] = Field(None, description="关键词")
    filters: Optional[Dict[str, Any]] = Field(default={}, description="筛选条件")
    preferences: Optional[Dict[str, Any]] = Field(default={}, description="用户偏好")
    page: Optional[int] = Field(1, description="页码")
    page_size: Optional[int] = Field(20, description="每页数量")
    user_token: Optional[str] = Field(None, description="用户token")


class HotelDetailsRequest(BaseModel):
    """酒店详情请求"""
    hotel_id: str = Field(..., description="酒店ID")
    source: str = Field("meituan", description="数据源")
    check_in_date: str = Field(..., description="入住日期")
    check_out_date: str = Field(..., description="离店日期")
    user_token: Optional[str] = Field(None, description="用户token")


class HotelBookingRequest(BaseModel):
    """酒店预订请求"""
    hotel_id: str = Field(..., description="酒店ID")
    source: str = Field("meituan", description="数据源")
    room_type_id: str = Field(..., description="房型ID")
    check_in_date: str = Field(..., description="入住日期")
    check_out_date: str = Field(..., description="离店日期")
    guest_name: str = Field(..., description="入住人姓名")
    guest_phone: str = Field(..., description="入住人电话")
    num_rooms: int = Field(1, description="房间数量")
    user_token: str = Field(..., description="用户token")


class HotelCancelRequest(BaseModel):
    """取消预订请求"""
    order_id: str = Field(..., description="订单ID")
    source: str = Field("meituan", description="数据源")
    user_token: str = Field(..., description="用户token")


class HotelReActRequest(BaseModel):
    """酒店ReAct查询请求"""
    query: str = Field(..., description="查询内容")
    user_token: Optional[str] = Field(None, description="用户token")
    max_iterations: Optional[int] = Field(5, description="最大迭代次数")


@router.post("/hotel/search")
async def search_hotels(
    request: HotelSearchRequest,
    hotel_agent: HotelAgent = Depends(get_hotel_agent)
):
    """搜索酒店"""
    try:
        result = await hotel_agent.send_request(
            to_agent="hotel",
            action="search_hotels",
            payload={
                "city": request.city,
                "check_in_date": request.check_in_date,
                "check_out_date": request.check_out_date,
                "sources": request.sources,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "keyword": request.keyword,
                "filters": request.filters,
                "preferences": request.preferences,
                "page": request.page,
                "page_size": request.page_size,
                "user_token": request.user_token
            },
            priority=MessagePriority.NORMAL
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.payload,
                    "message": "酒店搜索完成"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
    except Exception as e:
        logger.error(f"Hotel search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"酒店搜索失败: {str(e)}"
        )


@router.post("/hotel/details")
async def get_hotel_details(
    request: HotelDetailsRequest,
    hotel_agent: HotelAgent = Depends(get_hotel_agent)
):
    """获取酒店详情"""
    try:
        result = await hotel_agent.send_request(
            to_agent="hotel",
            action="get_hotel_details",
            payload={
                "hotel_id": request.hotel_id,
                "source": request.source,
                "check_in_date": request.check_in_date,
                "check_out_date": request.check_out_date,
                "user_token": request.user_token
            }
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.payload,
                    "message": "获取酒店详情成功"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
    except Exception as e:
        logger.error(f"Get hotel details failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取酒店详情失败: {str(e)}"
        )


@router.post("/hotel/book")
async def book_hotel(
    request: HotelBookingRequest,
    hotel_agent: HotelAgent = Depends(get_hotel_agent)
):
    """预订酒店"""
    try:
        result = await hotel_agent.send_request(
            to_agent="hotel",
            action="book_hotel",
            payload={
                "hotel_id": request.hotel_id,
                "source": request.source,
                "room_type_id": request.room_type_id,
                "check_in_date": request.check_in_date,
                "check_out_date": request.check_out_date,
                "guest_name": request.guest_name,
                "guest_phone": request.guest_phone,
                "num_rooms": request.num_rooms,
                "user_token": request.user_token
            }
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.payload,
                    "message": "酒店预订成功"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
    except Exception as e:
        logger.error(f"Hotel booking failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"酒店预订失败: {str(e)}"
        )


@router.post("/hotel/cancel")
async def cancel_booking(
    request: HotelCancelRequest,
    hotel_agent: HotelAgent = Depends(get_hotel_agent)
):
    """取消预订"""
    try:
        result = await hotel_agent.send_request(
            to_agent="hotel",
            action="cancel_booking",
            payload={
                "order_id": request.order_id,
                "source": request.source,
                "user_token": request.user_token
            }
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.payload,
                    "message": "取消预订成功"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
    except Exception as e:
        logger.error(f"Cancel booking failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消预订失败: {str(e)}"
        )


@router.post("/hotel/react_query")
async def hotel_react_query(
    request: HotelReActRequest,
    hotel_agent: HotelAgent = Depends(get_hotel_agent)
):
    """酒店ReAct模式查询"""
    try:
        result = await hotel_agent.send_request(
            to_agent="hotel",
            action="react_query",
            payload={
                "query": request.query,
                "user_token": request.user_token,
                "max_iterations": request.max_iterations
            }
        )
        
        if result.success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": result.payload,
                    "message": "ReAct查询完成"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
    except Exception as e:
        logger.error(f"Hotel ReAct query failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ReAct查询失败: {str(e)}"
        )
