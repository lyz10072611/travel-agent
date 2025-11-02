from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.trip_db import TripPlanStatus, TripPlanOutput
from models.travel_plan import (
    TravelPlanAgentRequest,
    TravelPlanRequest,
    TravelPlanTeamResponse,
)
from loguru import logger
# 导入LangGraph工作流系统
from agents.langgraph_manager import workflow_manager
from agents.langgraph_state import TravelRequest
import json
import time
from agents.structured_output import convert_to_model
from repository.trip_plan_repository import (
    create_trip_plan_status,
    update_trip_plan_status,
    get_trip_plan_status,
    create_trip_plan_output,
    delete_trip_plan_outputs,
)


def travel_request_to_markdown(data: TravelPlanRequest) -> str:
    # 旅行氛围到描述的映射
    travel_vibes = {
        "relaxing": "专注于健康、水疗体验和休闲活动的宁静度假",
        "adventure": "包括徒步、水上运动和肾上腺素活动的刺激体验",
        "romantic": "私人用餐、情侣活动和风景点的亲密体验",
        "cultural": "当地传统、博物馆和历史遗址的沉浸式体验",
        "food-focused": "包括烹饪课程、美食之旅和当地美食的烹饪体验",
        "nature": "国家公园、野生动物和风景景观的户外体验",
        "photography": "风景观景点、文化遗址和自然奇观的摄影地点",
    }

    # 旅行风格到描述的映射
    travel_styles = {
        "backpacker": "经济实惠的住宿、当地交通和真实体验",
        "comfort": "中档酒店、便利交通和平衡的舒适价值比",
        "luxury": "豪华住宿、私人接送和独家体验",
        "eco-conscious": "可持续住宿、环保活动和负责任旅游",
    }

    # 节奏级别（0-5）到描述的映射
    pace_levels = {
        0: "每天1-2个活动，有充足的自由时间和灵活性",
        1: "每天2-3个活动，活动之间有大量休息时间",
        2: "每天3-4个活动，平衡的活动和休息时间",
        3: "每天4-5个活动，活动之间有适度的休息",
        4: "每天5-6个活动，最少的休息时间",
        5: "每天6+个活动，连续安排",
    }

    def format_date(date_str: str, is_picker: bool) -> str:
        if not date_str:
            return "未指定"
        if is_picker:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt.strftime("%B %d, %Y")
            except ValueError:
                return date_str
        return date_str.strip()

    date_type = data.date_input_type
    is_picker = date_type == "picker"
    start_date = format_date(data.travel_dates.start, is_picker)
    end_date = format_date(data.travel_dates.end, is_picker)
    date_range = (
        f"在{start_date}和{end_date}之间"
        if end_date and end_date != "未指定"
        else start_date
    )

    vibes = data.vibes
    vibes_descriptions = [travel_vibes.get(v, v) for v in vibes]

    lines = [
        f"# 🧳 Travel Plan Request",
        "",
        "## 📍 Trip Overview",
        f"- **旅行者:** {data.name.title() if data.name else '未命名旅行者'}",
        f"- **路线:** {data.starting_location.title()} → {data.destination.title()}",
        f"- **持续时间:** {data.duration}天 ({date_range})",
        "",
        "## 👥 旅行团队",
        f"- **团队规模:** {data.adults}个成人，{data.children}个儿童",
        f"- **旅行伙伴:** {data.traveling_with or '未指定'}",
        f"- **年龄组:** {', '.join(data.age_groups) or '未指定'}",
        f"- **所需房间:** {data.rooms or '未指定'}",
        "",
        "## 💰 预算和偏好",
        f"- **每人预算:** {data.budget} {data.budget_currency} ({'灵活' if data.budget_flexible else '固定'})",
        f"- **旅行风格:** {travel_styles.get(data.travel_style, data.travel_style or '未指定')}",
        f"- **首选节奏:** {', '.join([pace_levels.get(p, str(p)) for p in data.pace]) or '未指定'}",
        "",
        "## ✨ 旅行偏好",
    ]

    if vibes_descriptions:
        lines.append("- **旅行氛围:**")
        for vibe in vibes_descriptions:
            lines.append(f"  - {vibe}")
    else:
        lines.append("- **旅行氛围:** 未指定")

    if data.priorities:
        lines.append(f"- **首要优先级:** {', '.join(data.priorities)}")
    if data.interests:
        lines.append(f"- **兴趣:** {data.interests}")

    lines.extend(
        [
            "",
            "## 🗺️ 目的地背景",
            f"- **之前访问:** {data.been_there_before.capitalize() if data.been_there_before else '未指定'}",
            f"- **喜爱的地方:** {data.loved_places or '未指定'}",
            f"- **附加备注:** {data.additional_info or '未指定'}",
        ]
    )

    return "\n".join(lines)


async def generate_travel_plan(request: TravelPlanAgentRequest) -> str:
    """基于请求生成旅行计划并将状态/输出记录到数据库。"""
    trip_plan_id = request.trip_plan_id
    logger.info(f"正在为tripPlanId生成旅行计划: {trip_plan_id}")

    try:
        # 将TravelPlanRequest转换为TravelRequest
        travel_request = TravelRequest(
            name=request.travel_plan.name,
            destination=request.travel_plan.destination,
            starting_location=request.travel_plan.starting_location,
            travel_dates_start=request.travel_plan.travel_dates.start,
            travel_dates_end=request.travel_plan.travel_dates.end,
            date_input_type=request.travel_plan.date_input_type,
            duration=request.travel_plan.duration,
            traveling_with=request.travel_plan.traveling_with,
            adults=request.travel_plan.adults,
            children=request.travel_plan.children,
            age_groups=request.travel_plan.age_groups,
            budget=request.travel_plan.budget,
            budget_currency=request.travel_plan.budget_currency,
            travel_style=request.travel_plan.travel_style,
            budget_flexible=request.travel_plan.budget_flexible,
            vibes=request.travel_plan.vibes,
            priorities=request.travel_plan.priorities,
            interests=request.travel_plan.interests,
            rooms=request.travel_plan.rooms,
            pace=request.travel_plan.pace,
            been_there_before=request.travel_plan.been_there_before,
            loved_places=request.travel_plan.loved_places,
            additional_info=request.travel_plan.additional_info
        )
        
        logger.info("正在使用LangGraph工作流生成旅行计划")
        
        # 使用LangGraph工作流管理器
        result = await workflow_manager.start_workflow(travel_request, trip_plan_id)
        
        if result.get("plan_status") == "completed":
            final_plan = result.get("final_plan", "")
            execution_time = result.get("total_execution_time", 0)
            
            logger.info(f"LangGraph工作流成功完成，耗时: {execution_time:.2f}秒")
            
            # 返回格式化的结果
            final_response = json.dumps({
                "itinerary": final_plan,
                "workflow_status": "success",
                "processing_time": f"{execution_time:.2f}秒",
                "trip_plan_id": trip_plan_id,
                "framework": "LangGraph"
            }, indent=2, ensure_ascii=False)

        return final_response
        else:
            error_message = result.get("error_message", "未知错误")
            logger.error(f"LangGraph工作流执行失败: {error_message}")
            
            return json.dumps({
                "error": error_message,
                "workflow_status": "failed",
                "trip_plan_id": trip_plan_id,
                "framework": "LangGraph"
            }, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(
            f"为{trip_plan_id}生成旅行计划时出错: {str(e)}", exc_info=True
        )
        # 更新状态为失败
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="failed",
            error=str(e),
            completed_at=datetime.now(timezone.utc),
        )
        raise
