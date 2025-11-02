"""
工作流监控API路由
提供LangGraph工作流的监控和管理功能
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from loguru import logger

from agents.langgraph_manager import workflow_manager

router = APIRouter(prefix="/api/workflow", tags=["工作流监控"])


@router.get("/status/{trip_plan_id}", summary="获取工作流状态")
async def get_workflow_status(trip_plan_id: str) -> Dict[str, Any]:
    """
    获取指定旅行计划的工作流执行状态
    
    参数:
        trip_plan_id: 旅行计划ID
    
    返回:
        工作流状态信息
    """
    try:
        logger.info(f"获取工作流状态: {trip_plan_id}")
        
        status_info = await workflow_manager.get_workflow_status(trip_plan_id)
        
        if status_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到旅行计划: {trip_plan_id}"
            )
        
        return {
            "success": True,
            "data": status_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取工作流状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工作流状态失败: {str(e)}"
        )


@router.post("/cancel/{trip_plan_id}", summary="取消工作流")
async def cancel_workflow(trip_plan_id: str) -> Dict[str, Any]:
    """
    取消指定旅行计划的工作流执行
    
    参数:
        trip_plan_id: 旅行计划ID
    
    返回:
        取消操作结果
    """
    try:
        logger.info(f"取消工作流: {trip_plan_id}")
        
        success = await workflow_manager.cancel_workflow(trip_plan_id)
        
        if success:
            return {
                "success": True,
                "message": f"工作流 {trip_plan_id} 已成功取消"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="取消工作流失败"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消工作流失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消工作流失败: {str(e)}"
        )


@router.get("/active", summary="获取活跃工作流")
async def get_active_workflows() -> Dict[str, Any]:
    """
    获取当前活跃的工作流列表
    
    返回:
        活跃工作流信息
    """
    try:
        logger.info("获取活跃工作流列表")
        
        active_workflows = await workflow_manager.get_active_workflows()
        
        return {
            "success": True,
            "data": active_workflows
        }
        
    except Exception as e:
        logger.error(f"获取活跃工作流失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取活跃工作流失败: {str(e)}"
        )


@router.get("/visualization", summary="获取工作流可视化")
async def get_workflow_visualization() -> Dict[str, Any]:
    """
    获取工作流图的可视化表示
    
    返回:
        工作流可视化信息
    """
    try:
        logger.info("获取工作流可视化")
        
        visualization = workflow_manager.get_workflow_visualization()
        
        return {
            "success": True,
            "data": {
                "visualization": visualization,
                "description": "LangGraph工作流图的可视化表示"
            }
        }
        
    except Exception as e:
        logger.error(f"获取工作流可视化失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工作流可视化失败: {str(e)}"
        )
