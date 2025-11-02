"""
LangGraph工作流管理器
管理旅行规划工作流的执行和监控
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .langgraph_workflow import travel_planning_workflow
from .langgraph_state import TravelRequest, TravelPlanState
from repository.trip_plan_repository import (
    create_trip_plan_status,
    update_trip_plan_status,
    get_trip_plan_status,
    create_trip_plan_output,
    delete_trip_plan_outputs,
)


class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self):
        self.workflow = travel_planning_workflow
        self.active_workflows: Dict[str, Any] = {}
    
    async def start_workflow(
        self,
        travel_request: TravelRequest,
        trip_plan_id: str
    ) -> Dict[str, Any]:
        """启动工作流"""
        try:
            logger.info(f"启动工作流，计划ID: {trip_plan_id}")
            
            # 创建或更新状态
            status_entry = await get_trip_plan_status(trip_plan_id)
            if not status_entry:
                status_entry = await create_trip_plan_status(
                    trip_plan_id=trip_plan_id,
                    status="processing"
                )
            
            # 更新状态为处理中
            await update_trip_plan_status(
                trip_plan_id=trip_plan_id,
                status="processing",
                current_step="正在启动LangGraph工作流",
                started_at=datetime.now()
            )
            
            # 启动工作流
            result = await self.workflow.run(travel_request, trip_plan_id)
            
            # 处理结果
            if result.get("plan_status") == "completed":
                await self._handle_success(trip_plan_id, result)
            else:
                await self._handle_failure(trip_plan_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"工作流启动失败: {e}")
            await self._handle_failure(trip_plan_id, {"error_message": str(e)})
            raise
    
    async def _handle_success(self, trip_plan_id: str, result: Dict[str, Any]):
        """处理成功结果"""
        try:
            # 删除现有输出
            await delete_trip_plan_outputs(trip_plan_id=trip_plan_id)
            
            # 创建新输出
            await create_trip_plan_output(
                trip_plan_id=trip_plan_id,
                itinerary=result.get("final_plan", ""),
                summary="LangGraph工作流生成的完整旅行计划"
            )
            
            # 更新状态为完成
            await update_trip_plan_status(
                trip_plan_id=trip_plan_id,
                status="completed",
                current_step="LangGraph工作流计划已生成并保存",
                completed_at=datetime.now()
            )
            
            logger.info(f"工作流成功完成，计划ID: {trip_plan_id}")
            
        except Exception as e:
            logger.error(f"处理成功结果失败: {e}")
    
    async def _handle_failure(self, trip_plan_id: str, result: Dict[str, Any]):
        """处理失败结果"""
        try:
            # 更新状态为失败
            await update_trip_plan_status(
                trip_plan_id=trip_plan_id,
                status="failed",
                error=result.get("error_message", "未知错误"),
                completed_at=datetime.now()
            )
            
            logger.error(f"工作流执行失败，计划ID: {trip_plan_id}")
            
        except Exception as e:
            logger.error(f"处理失败结果失败: {e}")
    
    async def get_workflow_status(self, trip_plan_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流状态"""
        try:
            status_entry = await get_trip_plan_status(trip_plan_id)
            if status_entry:
                return {
                    "trip_plan_id": trip_plan_id,
                    "status": status_entry.status,
                    "current_step": status_entry.current_step,
                    "started_at": status_entry.started_at,
                    "completed_at": status_entry.completed_at,
                    "error": status_entry.error
                }
            return None
            
        except Exception as e:
            logger.error(f"获取工作流状态失败: {e}")
            return None
    
    async def cancel_workflow(self, trip_plan_id: str) -> bool:
        """取消工作流"""
        try:
            # 更新状态为取消
            await update_trip_plan_status(
                trip_plan_id=trip_plan_id,
                status="cancelled",
                current_step="工作流已取消",
                completed_at=datetime.now()
            )
            
            # 从活跃工作流中移除
            if trip_plan_id in self.active_workflows:
                del self.active_workflows[trip_plan_id]
            
            logger.info(f"工作流已取消，计划ID: {trip_plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"取消工作流失败: {e}")
            return False
    
    def get_workflow_visualization(self) -> str:
        """获取工作流可视化"""
        return self.workflow.get_graph_visualization()
    
    async def get_active_workflows(self) -> Dict[str, Any]:
        """获取活跃工作流列表"""
        return {
            "active_count": len(self.active_workflows),
            "workflows": list(self.active_workflows.keys())
        }


# 创建全局工作流管理器实例
workflow_manager = WorkflowManager()
