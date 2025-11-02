"""
API路由定义
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from app.langchain_integration import LangChainIntegration
from app.agents.router import AgentRouter
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
    avoid_highway: Optional[bool] = Field(default=False, description="是否避开高速")
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


class BudgetRequest(BaseModel):
    """预算计算请求模型"""
    total_distance: Optional[float] = Field(None, description="总距离")
    days: Optional[int] = Field(default=1, description="天数")
    daily_routes: Optional[List[Dict[str, Any]]] = Field(default=[], description="每日路线")
    preferences: Optional[Dict[str, Any]] = Field(default={}, description="偏好设置")
    user_id: Optional[str] = Field(None, description="用户ID")


class UserPreferencesRequest(BaseModel):
    """用户偏好请求模型"""
    user_id: str = Field(..., description="用户ID")
    preferences: Dict[str, Any] = Field(..., description="偏好设置")


# 依赖函数
async def get_langchain_integration(request: Request) -> LangChainIntegration:
    """获取LangChain集成实例"""
    return request.app.state.langchain_integration


async def get_agent_router() -> AgentRouter:
    """获取Agent路由器实例"""
    return AgentRouter()


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
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """路线规划接口"""
    try:
        logger.info(f"Planning route from {request.origin} to {request.destination}")
        
        result = await agent_router.execute(
            query=f"从{request.origin}到{request.destination}的路线规划",
            origin=request.origin,
            destination=request.destination,
            waypoints=request.waypoints,
            daily_distance=request.daily_distance,
            avoid_highway=request.avoid_highway,
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


# 天气查询接口
@router.post("/weather/query")
async def query_weather(
    request: WeatherRequest,
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """天气查询接口"""
    try:
        logger.info(f"Querying weather for {request.location}")
        
        result = await agent_router.execute(
            query=f"{request.location}的天气",
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
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """POI查询接口"""
    try:
        logger.info(f"Searching POI in {request.location}")
        
        result = await agent_router.execute(
            query=f"{request.location}的{request.poi_type}",
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


# 预算计算接口
@router.post("/budget/calculate")
async def calculate_budget(
    request: BudgetRequest,
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """预算计算接口"""
    try:
        logger.info("Calculating budget")
        
        result = await agent_router.execute(
            query="计算旅行预算",
            total_distance=request.total_distance,
            days=request.days,
            daily_routes=request.daily_routes,
            preferences=request.preferences,
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
        logger.error(f"Budget calculation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"预算计算失败: {str(e)}"
        )


# 用户偏好接口
@router.post("/user/preferences")
async def save_user_preferences(
    request: UserPreferencesRequest,
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """保存用户偏好"""
    try:
        logger.info(f"Saving preferences for user {request.user_id}")
        
        result = await agent_router.execute(
            query="保存用户偏好",
            action="save_preferences",
            user_id=request.user_id,
            preferences=request.preferences
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
        logger.error(f"Save preferences failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存偏好失败: {str(e)}"
        )


@router.get("/user/preferences/{user_id}")
async def get_user_preferences(
    user_id: str,
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """获取用户偏好"""
    try:
        logger.info(f"Getting preferences for user {user_id}")
        
        result = await agent_router.execute(
            query="获取用户偏好",
            action="get_preferences",
            user_id=user_id
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
        logger.error(f"Get preferences failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取偏好失败: {str(e)}"
        )


# Agent状态接口
@router.get("/agents/status")
async def get_agents_status(
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """获取Agent状态"""
    try:
        status_info = agent_router.get_agent_status()
        
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
async def get_available_agents(
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """获取可用Agent列表"""
    try:
        agents = agent_router.get_available_agents()
        
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
