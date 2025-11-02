"""
景点推荐Agent
处理景点推荐、旅游信息等
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.agents.base_agent import AsyncAgent, AgentResponse, AgentType
from tools.poi_tools import POITool
from loguru import logger


class AttractionAgent(AsyncAgent):
    """景点推荐Agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.ATTRACTION,
            name="attraction_agent",
            description="景点推荐Agent，提供景点推荐和旅游信息服务"
        )
        self.poi_tool = POITool()
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行景点推荐"""
        query = kwargs.get("query", "")
        location = kwargs.get("location", "")
        route_type = kwargs.get("route_type", "自然风光")
        user_id = kwargs.get("user_id")
        
        try:
            if not location:
                location = await self._extract_location_from_query(query)
            
            if not location:
                return self._create_error_response("请提供查询地点")
            
            # 搜索景点
            attractions_result = await self._search_attractions(location, route_type)
            
            if not attractions_result["success"]:
                return self._create_error_response(attractions_result["message"])
            
            # 生成推荐
            recommendations = await self._generate_attraction_recommendations(
                attractions_result["data"], route_type
            )
            
            result = {
                "location": location,
                "route_type": route_type,
                "attractions": attractions_result["data"],
                "recommendations": recommendations
            }
            
            return self._create_success_response(
                data=result,
                message="景点推荐完成",
                metadata={
                    "location": location,
                    "route_type": route_type,
                    "user_id": user_id
                }
            )
            
        except Exception as e:
            logger.error(f"Attraction recommendation failed: {str(e)}")
            return self._create_error_response(f"景点推荐失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        has_query = bool(kwargs.get("query", ""))
        has_location = bool(kwargs.get("location", ""))
        return has_query or has_location
    
    async def _extract_location_from_query(self, query: str) -> str:
        """从查询中提取地点信息"""
        import re
        
        location_patterns = [
            r"(.+?)的景点",
            r"(.+?)有什么好玩的",
            r"(.+?)推荐",
            r"(.+?)旅游"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        return ""
    
    async def _search_attractions(self, location: str, route_type: str) -> Dict[str, Any]:
        """搜索景点"""
        try:
            async with self.poi_tool:
                result = await self.poi_tool.search_scenic_spots(location, 50000)
                return result
        except Exception as e:
            return {"success": False, "message": f"景点搜索失败: {str(e)}"}
    
    async def _generate_attraction_recommendations(
        self, 
        attractions_data: Dict[str, Any], 
        route_type: str
    ) -> Dict[str, Any]:
        """生成景点推荐"""
        
        recommendations = {
            "top_attractions": [],
            "by_category": {},
            "itinerary_suggestions": []
        }
        
        if isinstance(attractions_data, dict) and "pois" in attractions_data:
            pois = attractions_data["pois"]
            
            # 按评分排序
            sorted_by_rating = sorted(pois, key=lambda x: x.get("rating", 0), reverse=True)
            recommendations["top_attractions"] = sorted_by_rating[:5]
            
            # 按类型分类
            for poi in pois:
                poi_type = poi.get("type", "其他")
                if poi_type not in recommendations["by_category"]:
                    recommendations["by_category"][poi_type] = []
                recommendations["by_category"][poi_type].append(poi)
            
            # 生成行程建议
            recommendations["itinerary_suggestions"] = self._generate_itinerary_suggestions(
                sorted_by_rating[:10], route_type
            )
        
        return recommendations
    
    def _generate_itinerary_suggestions(
        self, 
        attractions: List[Dict[str, Any]], 
        route_type: str
    ) -> List[Dict[str, Any]]:
        """生成行程建议"""
        
        suggestions = []
        
        if len(attractions) >= 3:
            # 一日游建议
            suggestions.append({
                "title": "一日游推荐",
                "duration": "1天",
                "attractions": attractions[:3],
                "description": "精选3个最值得游览的景点"
            })
        
        if len(attractions) >= 6:
            # 两日游建议
            suggestions.append({
                "title": "两日游推荐",
                "duration": "2天",
                "attractions": attractions[:6],
                "description": "深度游览，体验当地文化"
            })
        
        return suggestions
