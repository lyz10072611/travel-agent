"""
预算计算Agent
处理费用计算、预算规划等
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.agents.base_agent import AsyncAgent, AgentResponse, AgentType
from tools.budget_tools import BudgetCalculator, CostAnalyzer
from loguru import logger


class BudgetAgent(AsyncAgent):
    """预算计算Agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.BUDGET,
            name="budget_agent",
            description="预算计算Agent，提供费用计算和预算规划服务"
        )
        self.budget_calculator = BudgetCalculator()
        self.cost_analyzer = CostAnalyzer()
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行预算计算"""
        query = kwargs.get("query", "")
        total_distance = kwargs.get("total_distance", 0)
        days = kwargs.get("days", 1)
        daily_routes = kwargs.get("daily_routes", [])
        preferences = kwargs.get("preferences", {})
        user_id = kwargs.get("user_id")
        
        try:
            # 如果没有提供距离，尝试从查询中提取
            if not total_distance:
                total_distance = await self._extract_distance_from_query(query)
            
            if not total_distance:
                return self._create_error_response("请提供旅行距离或天数")
            
            # 计算预算
            if daily_routes:
                # 基于详细路线的预算计算
                budget_result = await self._calculate_detailed_budget(
                    daily_routes, preferences
                )
            else:
                # 基于总距离的预算计算
                budget_result = await self._calculate_simple_budget(
                    total_distance, days, preferences
                )
            
            if not budget_result["success"]:
                return self._create_error_response(budget_result["message"])
            
            # 成本分析
            cost_analysis = self.cost_analyzer.analyze_cost_efficiency(budget_result["data"])
            
            result = {
                "budget_data": budget_result["data"],
                "cost_analysis": cost_analysis,
                "recommendations": await self._generate_budget_recommendations(
                    budget_result["data"], cost_analysis
                )
            }
            
            return self._create_success_response(
                data=result,
                message="预算计算完成",
                metadata={
                    "total_distance": total_distance,
                    "days": days,
                    "user_id": user_id
                }
            )
            
        except Exception as e:
            logger.error(f"Budget calculation failed: {str(e)}")
            return self._create_error_response(f"预算计算失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        has_query = bool(kwargs.get("query", ""))
        has_distance = bool(kwargs.get("total_distance", 0))
        has_daily_routes = bool(kwargs.get("daily_routes", []))
        
        return has_query or has_distance or has_daily_routes
    
    async def _extract_distance_from_query(self, query: str) -> float:
        """从查询中提取距离信息"""
        import re
        
        # 匹配距离模式
        distance_patterns = [
            r"(\d+)公里",
            r"(\d+)km",
            r"距离(\d+)",
            r"(\d+)千米"
        ]
        
        for pattern in distance_patterns:
            match = re.search(pattern, query)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    async def _calculate_simple_budget(
        self, 
        total_distance: float, 
        days: int, 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算简单预算"""
        
        try:
            # 使用预算计算器
            budget_result = await self.budget_calculator.calculate_trip_budget(
                total_distance=total_distance,
                days=days,
                fuel_price=preferences.get("fuel_price"),
                fuel_consumption=preferences.get("fuel_consumption"),
                hotel_budget=preferences.get("hotel_budget"),
                meal_budget=preferences.get("meal_budget"),
                include_attractions=preferences.get("include_attractions", True),
                include_equipment=preferences.get("include_equipment", False)
            )
            
            return budget_result
            
        except Exception as e:
            return {"success": False, "message": f"预算计算失败: {str(e)}"}
    
    async def _calculate_detailed_budget(
        self, 
        daily_routes: List[Dict[str, Any]], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算详细预算"""
        
        try:
            # 使用详细预算计算器
            budget_result = await self.budget_calculator.calculate_daily_budget(
                daily_routes=daily_routes,
                start_date=datetime.now().strftime("%Y-%m-%d"),
                preferences=preferences
            )
            
            return budget_result
            
        except Exception as e:
            return {"success": False, "message": f"详细预算计算失败: {str(e)}"}
    
    async def _generate_budget_recommendations(
        self, 
        budget_data: Dict[str, Any], 
        cost_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成预算建议"""
        
        recommendations = {
            "cost_optimization": [],
            "budget_planning": [],
            "savings_tips": []
        }
        
        # 成本优化建议
        if "recommendations" in cost_analysis:
            recommendations["cost_optimization"] = cost_analysis["recommendations"]
        
        # 预算规划建议
        total_cost = budget_data.get("total_cost", 0)
        daily_average = budget_data.get("daily_average", 0)
        
        if total_cost > 5000:
            recommendations["budget_planning"].append("预算较高，建议分阶段出行")
        elif total_cost < 1000:
            recommendations["budget_planning"].append("预算较低，建议选择经济型住宿和餐饮")
        
        if daily_average > 500:
            recommendations["budget_planning"].append("日均花费较高，建议优化住宿和餐饮选择")
        
        # 省钱建议
        recommendations["savings_tips"] = [
            "提前预订住宿可享受优惠价格",
            "选择当地特色小吃比高档餐厅更经济",
            "避开旅游旺季可节省住宿费用",
            "自备部分食物可减少餐饮开支",
            "选择经济型加油站可节省燃油费用"
        ]
        
        return recommendations
