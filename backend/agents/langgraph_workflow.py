"""
LangGraph工作流定义
构建完整的旅行规划工作流
"""

from typing import Dict, Any, List
from datetime import datetime
from loguru import logger

from .langgraph_state import TravelPlanState, TravelRequest, AgentResult
from .langgraph_nodes import (
    destination_node,
    flight_node,
    hotel_node,
    dining_node,
    itinerary_node,
    budget_node
)


class TravelPlanningWorkflow:
    """旅行规划工作流"""
    
    def __init__(self):
        self.nodes = {
            "destination": destination_node,
            "flight": flight_node,
            "hotel": hotel_node,
            "dining": dining_node,
            "itinerary": itinerary_node,
            "budget": budget_node
        }
    
    async def _finalize_plan(self, state: TravelPlanState) -> Dict[str, Any]:
        """最终化计划"""
        try:
            logger.info("开始最终化旅行计划")
            
            # 收集所有代理结果
            results = {}
            for key, value in state.items():
                if key.endswith("_result") and value:
                    results[key] = value
            
            # 使用行程专家模型整合所有结果
            from config.llm import get_qwen_model
            model = get_qwen_model(temperature=0.3, max_tokens=8096)
            
            integration_prompt = f"""
            请将以下各专业代理的工作结果整合成一个完整的旅行计划：
            
            原始用户请求：
            - 目的地: {state['travel_request'].destination}
            - 出发地: {state['travel_request'].starting_location}
            - 旅行日期: {state['travel_request'].travel_dates_start} 到 {state['travel_request'].travel_dates_end}
            - 持续时间: {state['travel_request'].duration}天
            - 预算: {state['travel_request'].budget} {state['travel_request'].budget_currency}
            
            各代理结果：
            """
            
            for result_key, result in results.items():
                integration_prompt += f"\n{result_key}: {result.content}\n"
            
            integration_prompt += """
            
            请创建一个完整、连贯、实用的旅行计划，包含：
            1. 执行摘要
            2. 旅行物流
            3. 详细每日行程
            4. 住宿详情
            5. 精选体验
            6. 全面预算
            7. 基本信息
            
            请使用中文回复，格式要清晰易读。
            """
            
            response = await model.ainvoke([{"role": "user", "content": integration_prompt}])
            final_plan = response.content
            
            # 计算总执行时间
            end_time = datetime.now()
            start_time = state.get("start_time", end_time)
            total_time = (end_time - start_time).total_seconds()
            
            logger.info(f"旅行计划最终化完成，总耗时: {total_time:.2f}秒")
            
            return {
                "final_plan": final_plan,
                "plan_status": "completed",
                "end_time": end_time,
                "total_execution_time": total_time,
                "current_step": "计划完成"
            }
            
        except Exception as e:
            logger.error(f"最终化计划失败: {e}")
            return {
                "plan_status": "failed",
                "error_message": str(e),
                "current_step": "计划失败"
            }
    
    async def run(self, travel_request: TravelRequest, trip_plan_id: str) -> Dict[str, Any]:
        """运行工作流"""
        try:
            logger.info(f"开始执行旅行规划工作流，计划ID: {trip_plan_id}")
            
            # 初始化状态
            state = {
                "travel_request": travel_request,
                "trip_plan_id": trip_plan_id,
                "current_step": "开始",
                "completed_steps": [],
                "failed_steps": [],
                "destination_result": None,
                "flight_result": None,
                "hotel_result": None,
                "dining_result": None,
                "itinerary_result": None,
                "budget_result": None,
                "final_plan": None,
                "plan_status": "processing",
                "error_message": None,
                "start_time": datetime.now(),
                "end_time": None,
                "total_execution_time": None
            }
            
            # 按顺序执行各个节点
            node_order = ["destination", "flight", "hotel", "dining", "itinerary", "budget"]
            
            for node_name in node_order:
                try:
                    logger.info(f"执行节点: {node_name}")
                    node = self.nodes[node_name]
                    result = await node.execute(state)
                    state.update(result)
                    
                    if f"{node_name}_result" in result:
                        logger.info(f"节点 {node_name} 执行成功")
                    else:
                        logger.warning(f"节点 {node_name} 执行结果异常")
                        
                except Exception as e:
                    logger.error(f"节点 {node_name} 执行失败: {e}")
                    state["failed_steps"].append(node_name)
            
            # 最终化计划
            final_result = await self._finalize_plan(state)
            state.update(final_result)
            
            logger.info(f"旅行规划工作流执行完成，计划ID: {trip_plan_id}")
            
            return state
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            return {
                "plan_status": "failed",
                "error_message": str(e),
                "final_plan": f"工作流执行失败: {str(e)}"
            }
    
    def get_graph_visualization(self) -> str:
        """获取工作流图的可视化"""
        try:
            # 返回简单的文本描述
            return """
            旅行规划工作流:
            1. 目的地探索 → 2. 航班搜索 → 3. 酒店搜索 → 4. 餐饮搜索 → 5. 行程规划 → 6. 预算优化 → 7. 最终化
            """
        except Exception as e:
            logger.error(f"获取工作流可视化失败: {e}")
            return "无法生成工作流可视化"


# 创建全局工作流实例
travel_planning_workflow = TravelPlanningWorkflow()
