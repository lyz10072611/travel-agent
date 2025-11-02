"""
网页搜索Agent
处理政策查询、路况信息、安全信息等
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.agents.base_agent import AsyncAgent, AgentResponse, AgentType
from tools.search_tools import WebSearchTool, PolicySearchTool, SafetyInfoTool
from loguru import logger


class SearchAgent(AsyncAgent):
    """网页搜索Agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.SEARCH,
            name="search_agent",
            description="网页搜索Agent，提供政策查询、路况信息、安全信息等搜索服务"
        )
        self.web_search_tool = WebSearchTool()
        self.policy_search_tool = PolicySearchTool()
        self.safety_info_tool = SafetyInfoTool()
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行搜索查询"""
        query = kwargs.get("query", "")
        search_type = kwargs.get("search_type", "general")
        location = kwargs.get("location", "")
        user_id = kwargs.get("user_id")
        
        try:
            if not query:
                return self._create_error_response("请提供搜索查询")
            
            # 根据搜索类型执行不同的搜索
            if search_type == "policy" or "政策" in query or "限行" in query:
                result = await self._search_policies(query, location)
            elif search_type == "safety" or "安全" in query or "路况" in query:
                result = await self._search_safety_info(query, location)
            else:
                result = await self._search_general(query)
            
            if not result["success"]:
                return self._create_error_response(result["message"])
            
            return self._create_success_response(
                data=result["data"],
                message="搜索完成",
                metadata={
                    "query": query,
                    "search_type": search_type,
                    "location": location,
                    "user_id": user_id
                }
            )
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return self._create_error_response(f"搜索失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        return self._validate_required_params(["query"], **kwargs)
    
    async def _search_policies(self, query: str, location: str) -> Dict[str, Any]:
        """搜索政策信息"""
        try:
            async with self.policy_search_tool:
                if location:
                    result = await self.policy_search_tool.search_city_motorcycle_policy(location)
                else:
                    # 从查询中提取城市信息
                    city = self._extract_city_from_query(query)
                    if city:
                        result = await self.policy_search_tool.search_city_motorcycle_policy(city)
                    else:
                        result = {"success": False, "message": "无法识别城市信息"}
                
                return result
        except Exception as e:
            return {"success": False, "message": f"政策搜索失败: {str(e)}"}
    
    async def _search_safety_info(self, query: str, location: str) -> Dict[str, Any]:
        """搜索安全信息"""
        try:
            async with self.safety_info_tool:
                if location:
                    result = await self.safety_info_tool.get_road_safety_info(location)
                else:
                    result = {"success": False, "message": "请提供具体位置"}
                
                return result
        except Exception as e:
            return {"success": False, "message": f"安全信息搜索失败: {str(e)}"}
    
    async def _search_general(self, query: str) -> Dict[str, Any]:
        """通用搜索"""
        try:
            async with self.web_search_tool:
                if "装备" in query:
                    result = await self.web_search_tool.search_equipment_recommendations()
                elif "修车" in query:
                    result = await self.web_search_tool.search_repair_shops(query)
                else:
                    result = await self.web_search_tool.search_motorcycle_policies(query)
                
                return result
        except Exception as e:
            return {"success": False, "message": f"通用搜索失败: {str(e)}"}
    
    def _extract_city_from_query(self, query: str) -> str:
        """从查询中提取城市信息"""
        import re
        
        # 简单的城市名称提取
        city_patterns = [
            r"(.+?)市",
            r"(.+?)省",
            r"(.+?)区",
            r"(.+?)县"
        ]
        
        for pattern in city_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        return ""
