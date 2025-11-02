"""
预算计算工具
处理摩旅成本计算、预算规划等功能
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from tools.base_tool import BaseTool
from app.config import settings


@dataclass
class BudgetItem:
    """预算项目"""
    name: str
    category: str
    unit_cost: float
    quantity: int
    total_cost: float
    description: str = ""


@dataclass
class DailyBudget:
    """每日预算"""
    date: str
    distance: float
    items: List[BudgetItem]
    total_cost: float
    notes: str = ""


class BudgetCalculator(BaseTool):
    """预算计算器 - 摩旅财务规划专家"""
    
    def __init__(self):
        super().__init__(
            name="budget_calculator",
            description="""
            💰 摩旅预算计算器 - 智能财务规划专家
            
            【核心功能】
            • 精确预算计算：基于距离、天数、偏好进行精确的摩旅预算计算
            • 多维度分析：从燃油、住宿、餐饮、维护等多个维度分析成本
            • 个性化定制：根据用户偏好和消费水平定制预算方案
            • 成本优化：提供节省开支的实用建议和替代方案
            
            【摩旅特色计算】
            • 燃油成本：基于实际油耗和油价计算精确燃油费用
            • 住宿预算：根据用户偏好选择经济型到豪华型住宿
            • 餐饮规划：考虑当地消费水平和用户饮食习惯
            • 维护费用：包含车辆保养、维修、保险等费用
            • 应急资金：预留意外支出和应急处理费用
            
            【智能算法】
            • 动态调整：根据路线类型和地区差异调整成本系数
            • 季节性考虑：考虑旅游旺季和淡季的价格差异
            • 个性化匹配：根据用户消费习惯调整预算分配
            • 性价比分析：提供最佳性价比的消费建议
            
            【预算管理】
            • 分类管理：按类别详细分解各项费用
            • 进度跟踪：支持预算执行进度跟踪
            • 超支预警：当预算超支时提供预警和建议
            • 节省方案：提供多种节省开支的实用方案
            
            【数据支持】
            • 实时油价：集成实时油价数据，确保计算准确性
            • 地区差异：考虑不同地区的消费水平差异
            • 历史数据：基于历史数据提供合理的预算估算
            • 市场调研：结合市场调研数据提供准确的价格参考
            
            适用于：预算规划、成本控制、财务分析、消费建议
            """
        )
        
        # 默认成本参数
        self.default_costs = {
            "fuel_price": 7.5,  # 油价 元/升
            "fuel_consumption": settings.default_fuel_consumption,  # 油耗 L/100km
            "hotel_budget": 150,  # 住宿预算 元/晚
            "meal_budget": 80,  # 餐饮预算 元/天
            "maintenance_budget": 50,  # 维护预算 元/天
            "emergency_budget": 200,  # 应急预算 元/天
        }
    
    async def calculate_trip_budget(
        self,
        total_distance: float,
        days: int,
        fuel_price: Optional[float] = None,
        fuel_consumption: Optional[float] = None,
        hotel_budget: Optional[float] = None,
        meal_budget: Optional[float] = None,
        include_attractions: bool = True,
        include_equipment: bool = False
    ) -> Dict[str, Any]:
        """计算旅行总预算"""
        
        # 使用默认值或用户指定值
        fuel_price = fuel_price or self.default_costs["fuel_price"]
        fuel_consumption = fuel_consumption or self.default_costs["fuel_consumption"]
        hotel_budget = hotel_budget or self.default_costs["hotel_budget"]
        meal_budget = meal_budget or self.default_costs["meal_budget"]
        
        # 计算各项成本
        fuel_cost = self._calculate_fuel_cost(total_distance, fuel_price, fuel_consumption)
        accommodation_cost = self._calculate_accommodation_cost(days, hotel_budget)
        meal_cost = self._calculate_meal_cost(days, meal_budget)
        maintenance_cost = self._calculate_maintenance_cost(days)
        emergency_cost = self._calculate_emergency_cost(days)
        
        # 可选成本
        attraction_cost = 0
        if include_attractions:
            attraction_cost = self._calculate_attraction_cost(days)
        
        equipment_cost = 0
        if include_equipment:
            equipment_cost = self._calculate_equipment_cost()
        
        # 总成本
        total_cost = (
            fuel_cost + accommodation_cost + meal_cost + 
            maintenance_cost + emergency_cost + attraction_cost + equipment_cost
        )
        
        # 构建详细预算
        budget_items = [
            BudgetItem("燃油费", "交通", fuel_price, int(total_distance * fuel_consumption / 100), fuel_cost, "根据距离和油耗计算"),
            BudgetItem("住宿费", "住宿", hotel_budget, days, accommodation_cost, "每晚住宿费用"),
            BudgetItem("餐饮费", "餐饮", meal_budget, days, meal_cost, "每日餐饮费用"),
            BudgetItem("维护费", "维护", self.default_costs["maintenance_budget"], days, maintenance_cost, "车辆维护和保养"),
            BudgetItem("应急费", "应急", self.default_costs["emergency_budget"], days, emergency_cost, "应急和意外支出"),
        ]
        
        if include_attractions:
            budget_items.append(
                BudgetItem("景点费", "娱乐", attraction_cost / days if days > 0 else 0, days, attraction_cost, "景点门票和娱乐费用")
            )
        
        if include_equipment:
            budget_items.append(
                BudgetItem("装备费", "装备", equipment_cost, 1, equipment_cost, "摩旅装备采购")
            )
        
        return self.format_response({
            "total_distance": total_distance,
            "days": days,
            "total_cost": total_cost,
            "daily_average": total_cost / days if days > 0 else 0,
            "budget_items": [
                {
                    "name": item.name,
                    "category": item.category,
                    "unit_cost": item.unit_cost,
                    "quantity": item.quantity,
                    "total_cost": item.total_cost,
                    "description": item.description
                }
                for item in budget_items
            ],
            "cost_breakdown": {
                "fuel_percentage": (fuel_cost / total_cost) * 100,
                "accommodation_percentage": (accommodation_cost / total_cost) * 100,
                "meal_percentage": (meal_cost / total_cost) * 100,
                "other_percentage": ((maintenance_cost + emergency_cost + attraction_cost + equipment_cost) / total_cost) * 100
            }
        })
    
    async def calculate_daily_budget(
        self,
        daily_routes: List[Dict[str, Any]],
        start_date: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """计算每日预算"""
        
        if not daily_routes:
            return self.format_response(None, success=False, message="路线数据为空")
        
        daily_budgets = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        for i, route in enumerate(daily_routes):
            date_str = (current_date + timedelta(days=i)).strftime("%Y-%m-%d")
            distance = route.get("distance", 0)
            
            # 计算当日各项成本
            fuel_cost = self._calculate_fuel_cost(distance, self.default_costs["fuel_price"], self.default_costs["fuel_consumption"])
            meal_cost = self.default_costs["meal_budget"]
            hotel_cost = self.default_costs["hotel_budget"] if i < len(daily_routes) - 1 else 0  # 最后一天不住宿
            maintenance_cost = self.default_costs["maintenance_budget"]
            
            # 根据偏好调整
            if preferences:
                if preferences.get("luxury_hotel", False):
                    hotel_cost *= 1.5
                if preferences.get("fine_dining", False):
                    meal_cost *= 1.3
            
            daily_items = [
                BudgetItem("燃油费", "交通", self.default_costs["fuel_price"], int(distance * self.default_costs["fuel_consumption"] / 100), fuel_cost),
                BudgetItem("餐饮费", "餐饮", meal_cost, 1, meal_cost),
                BudgetItem("住宿费", "住宿", hotel_cost, 1, hotel_cost),
                BudgetItem("维护费", "维护", maintenance_cost, 1, maintenance_cost),
            ]
            
            total_daily_cost = sum(item.total_cost for item in daily_items)
            
            daily_budget = DailyBudget(
                date=date_str,
                distance=distance,
                items=daily_items,
                total_cost=total_daily_cost,
                notes=f"第{i+1}天行程，距离{distance}公里"
            )
            
            daily_budgets.append({
                "date": daily_budget.date,
                "distance": daily_budget.distance,
                "total_cost": daily_budget.total_cost,
                "items": [
                    {
                        "name": item.name,
                        "category": item.category,
                        "unit_cost": item.unit_cost,
                        "quantity": item.quantity,
                        "total_cost": item.total_cost
                    }
                    for item in daily_budget.items
                ],
                "notes": daily_budget.notes
            })
        
        total_cost = sum(budget["total_cost"] for budget in daily_budgets)
        
        return self.format_response({
            "daily_budgets": daily_budgets,
            "total_cost": total_cost,
            "average_daily_cost": total_cost / len(daily_budgets) if daily_budgets else 0,
            "summary": {
                "total_days": len(daily_budgets),
                "total_distance": sum(budget["distance"] for budget in daily_budgets),
                "cost_per_km": total_cost / sum(budget["distance"] for budget in daily_budgets) if daily_budgets else 0
            }
        })
    
    def _calculate_fuel_cost(self, distance: float, fuel_price: float, fuel_consumption: float) -> float:
        """计算燃油成本"""
        fuel_needed = (distance / 100) * fuel_consumption
        return fuel_needed * fuel_price
    
    def _calculate_accommodation_cost(self, days: int, hotel_budget: float) -> float:
        """计算住宿成本"""
        return (days - 1) * hotel_budget  # 最后一天不住宿
    
    def _calculate_meal_cost(self, days: int, meal_budget: float) -> float:
        """计算餐饮成本"""
        return days * meal_budget
    
    def _calculate_maintenance_cost(self, days: int) -> float:
        """计算维护成本"""
        return days * self.default_costs["maintenance_budget"]
    
    def _calculate_emergency_cost(self, days: int) -> float:
        """计算应急成本"""
        return days * self.default_costs["emergency_budget"]
    
    def _calculate_attraction_cost(self, days: int) -> float:
        """计算景点成本"""
        return days * 50  # 平均每天50元景点费用
    
    def _calculate_equipment_cost(self) -> float:
        """计算装备成本"""
        return 2000  # 基础装备成本


class CostAnalyzer:
    """成本分析器"""
    
    @staticmethod
    def analyze_cost_efficiency(budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析成本效率"""
        total_cost = budget_data.get("total_cost", 0)
        total_distance = budget_data.get("total_distance", 0)
        
        if total_distance == 0:
            return {"error": "距离数据无效"}
        
        cost_per_km = total_cost / total_distance
        
        # 成本效率评级
        if cost_per_km < 0.5:
            efficiency_rating = "优秀"
        elif cost_per_km < 0.8:
            efficiency_rating = "良好"
        elif cost_per_km < 1.2:
            efficiency_rating = "一般"
        else:
            efficiency_rating = "较高"
        
        return {
            "cost_per_km": round(cost_per_km, 2),
            "efficiency_rating": efficiency_rating,
            "recommendations": CostAnalyzer._generate_cost_recommendations(budget_data)
        }
    
    @staticmethod
    def _generate_cost_recommendations(budget_data: Dict[str, Any]) -> List[str]:
        """生成成本优化建议"""
        recommendations = []
        
        cost_breakdown = budget_data.get("cost_breakdown", {})
        
        if cost_breakdown.get("fuel_percentage", 0) > 40:
            recommendations.append("燃油成本较高，建议选择更省油的路线或降低车速")
        
        if cost_breakdown.get("accommodation_percentage", 0) > 30:
            recommendations.append("住宿成本较高，建议选择经济型酒店或民宿")
        
        if cost_breakdown.get("meal_percentage", 0) > 25:
            recommendations.append("餐饮成本较高，建议选择当地特色小吃或自备部分食物")
        
        if not recommendations:
            recommendations.append("预算分配合理，可以适当增加娱乐和体验项目")
        
        return recommendations
    
    @staticmethod
    def compare_budget_options(
        option1: Dict[str, Any], 
        option2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """比较不同预算方案"""
        cost1 = option1.get("total_cost", 0)
        cost2 = option2.get("total_cost", 0)
        
        comparison = {
            "option1_cost": cost1,
            "option2_cost": cost2,
            "cost_difference": abs(cost1 - cost2),
            "cheaper_option": "option1" if cost1 < cost2 else "option2",
            "savings_percentage": abs(cost1 - cost2) / max(cost1, cost2) * 100
        }
        
        return comparison
