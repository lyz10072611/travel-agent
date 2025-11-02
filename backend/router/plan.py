import asyncio
from fastapi import APIRouter, HTTPException, status
from loguru import logger
from models.travel_plan import TravelPlanAgentRequest, TravelPlanResponse
from models.plan_task import TaskStatus
from services.plan_service import generate_travel_plan
from repository.plan_task_repository import create_plan_task, update_task_status
from typing import List

router = APIRouter(prefix="/api/plan", tags=["旅行计划"])


@router.post(
    "/trigger",
    response_model=TravelPlanResponse,
    summary="触发旅行规划代理",
    description="使用提供的旅行详情触发旅行计划代理",
)
async def trigger_trip_craft_agent(
    request: TravelPlanAgentRequest,
) -> TravelPlanResponse:
    """
    触发旅行规划代理以创建个性化的旅行行程。

    参数:
        request: 包含旅行详情和计划ID的旅行计划请求

    返回:
        TravelPlanResponse: 成功状态和旅行计划ID
    """
    try:
        logger.info(f"正在为旅行ID触发旅行计划代理: {request.trip_plan_id}")
        logger.info(f"旅行计划详情: {request.travel_plan}")

        # 创建初始任务
        task = await create_plan_task(
            trip_plan_id=request.trip_plan_id,
            task_type="travel_plan_generation",
            input_data=request.travel_plan.model_dump(),
        )

        logger.info(f"任务已创建: {task.id}")

        # 创建计划生成的后台任务
        async def generate_plan_with_tracking():
            try:
                # 当服务开始时更新任务状态为进行中
                await update_task_status(task.id, TaskStatus.in_progress)
                logger.info(f"任务已更新为进行中: {task.id}")

                result = await generate_travel_plan(request)

                # 使用成功状态和输出更新任务
                await update_task_status(
                    task.id, TaskStatus.success, output_data={"travel_plan": result}
                )
                logger.info(f"任务已更新为成功: {task.id}")
            except Exception as e:
                logger.error(f"生成旅行计划时出错: {str(e)}")
                # 使用错误状态更新任务
                await update_task_status(
                    task.id, TaskStatus.error, error_message=str(e)
                )
                logger.info(f"任务已更新为错误: {task.id}")
                raise

        asyncio.create_task(generate_plan_with_tracking())

        logger.info(
            f"旅行计划代理已成功触发，旅行ID: {request.trip_plan_id}"
        )

        return TravelPlanResponse(
            success=True,
            message="旅行计划代理已成功触发",
            trip_plan_id=request.trip_plan_id,
        )

    except Exception as e:
        logger.error(f"触发旅行计划代理时出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"触发旅行计划代理失败: {str(e)}",
        )
