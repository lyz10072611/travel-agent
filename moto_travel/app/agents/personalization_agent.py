"""
个性化定制Agent
处理用户偏好、个性化设置等
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.agents.base_agent import AsyncAgent, AgentResponse, AgentType
from tools.memory_tools import MemoryManager, VectorSearch
from loguru import logger


class PersonalizationAgent(AsyncAgent):
    """个性化定制Agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.PERSONALIZATION,
            name="personalization_agent",
            description="个性化定制Agent，处理用户偏好和个性化设置"
        )
        self.memory_manager = MemoryManager()
        self.vector_search = VectorSearch()
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行个性化定制"""
        query = kwargs.get("query", "")
        user_id = kwargs.get("user_id", "")
        action = kwargs.get("action", "get_preferences")
        preferences = kwargs.get("preferences", {})
        
        try:
            if not user_id:
                return self._create_error_response("请提供用户ID")
            
            if action == "save_preferences":
                result = await self._save_user_preferences(user_id, preferences)
            elif action == "get_preferences":
                result = await self._get_user_preferences(user_id)
            elif action == "get_recommendations":
                result = await self._get_personalized_recommendations(user_id, query)
            elif action == "save_experience":
                result = await self._save_trip_experience(user_id, preferences)
            else:
                return self._create_error_response(f"不支持的操作: {action}")
            
            if not result["success"]:
                return self._create_error_response(result["message"])
            
            return self._create_success_response(
                data=result["data"],
                message="个性化定制完成",
                metadata={
                    "user_id": user_id,
                    "action": action
                }
            )
            
        except Exception as e:
            logger.error(f"Personalization failed: {str(e)}")
            return self._create_error_response(f"个性化定制失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        return self._validate_required_params(["user_id"], **kwargs)
    
    async def _save_user_preferences(
        self, 
        user_id: str, 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """保存用户偏好"""
        
        try:
            async with self.memory_manager:
                results = []
                
                for pref_type, pref_data in preferences.items():
                    result = await self.memory_manager.save_user_preference(
                        user_id=user_id,
                        preference_type=pref_type,
                        preference_data=pref_data,
                        description=f"用户{pref_type}偏好设置"
                    )
                    results.append(result)
                
                return {
                    "success": True,
                    "data": {
                        "saved_preferences": results,
                        "total_count": len(results)
                    }
                }
                
        except Exception as e:
            return {"success": False, "message": f"保存偏好失败: {str(e)}"}
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        
        try:
            async with self.memory_manager:
                result = await self.memory_manager.get_user_preferences(user_id)
                return result
                
        except Exception as e:
            return {"success": False, "message": f"获取偏好失败: {str(e)}"}
    
    async def _get_personalized_recommendations(
        self, 
        user_id: str, 
        query: str
    ) -> Dict[str, Any]:
        """获取个性化推荐"""
        
        try:
            async with self.vector_search:
                result = await self.vector_search.get_personalized_recommendations(
                    user_id=user_id,
                    current_query=query,
                    limit=5
                )
                return result
                
        except Exception as e:
            return {"success": False, "message": f"获取推荐失败: {str(e)}"}
    
    async def _save_trip_experience(
        self, 
        user_id: str, 
        trip_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """保存旅行经验"""
        
        try:
            async with self.memory_manager:
                result = await self.memory_manager.save_trip_experience(
                    user_id=user_id,
                    trip_data=trip_data,
                    feedback=trip_data.get("feedback", "")
                )
                return result
                
        except Exception as e:
            return {"success": False, "message": f"保存经验失败: {str(e)}"}
    
    async def _analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """分析用户行为"""
        
        try:
            # 获取用户历史偏好
            preferences = await self.memory_manager.get_user_preferences(user_id)
            
            if not preferences["success"]:
                return {"success": False, "message": "无法获取用户偏好"}
            
            # 分析偏好模式
            behavior_analysis = {
                "preference_patterns": {},
                "travel_style": "未知",
                "risk_tolerance": "中等",
                "budget_level": "中等"
            }
            
            user_prefs = preferences["data"]["preferences"]
            
            # 分析旅行风格
            distance_prefs = [p for p in user_prefs if p["type"] == "daily_distance"]
            if distance_prefs:
                distances = [p["data"].get("distance", 300) for p in distance_prefs]
                avg_distance = sum(distances) / len(distances)
                
                if avg_distance > 500:
                    behavior_analysis["travel_style"] = "长途骑行"
                elif avg_distance > 300:
                    behavior_analysis["travel_style"] = "中长途骑行"
                else:
                    behavior_analysis["travel_style"] = "短途骑行"
            
            # 分析预算水平
            budget_prefs = [p for p in user_prefs if "budget" in p["type"]]
            if budget_prefs:
                behavior_analysis["budget_level"] = "较高"  # 简化处理
            
            return {
                "success": True,
                "data": behavior_analysis
            }
            
        except Exception as e:
            return {"success": False, "message": f"行为分析失败: {str(e)}"}
    
    async def _generate_personalized_plan(
        self, 
        user_id: str, 
        trip_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成个性化计划"""
        
        try:
            # 获取用户偏好
            preferences = await self._get_user_preferences(user_id)
            if not preferences["success"]:
                return {"success": False, "message": "无法获取用户偏好"}
            
            # 分析用户行为
            behavior = await self._analyze_user_behavior(user_id)
            if not behavior["success"]:
                return {"success": False, "message": "无法分析用户行为"}
            
            # 生成个性化建议
            personalized_plan = {
                "user_profile": behavior["data"],
                "recommendations": {},
                "customized_settings": {}
            }
            
            # 基于用户偏好生成建议
            user_prefs = preferences["data"]["preferences"]
            
            # 日行距离建议
            distance_prefs = [p for p in user_prefs if p["type"] == "daily_distance"]
            if distance_prefs:
                avg_distance = sum([p["data"].get("distance", 300) for p in distance_prefs]) / len(distance_prefs)
                personalized_plan["recommendations"]["daily_distance"] = int(avg_distance)
            
            # 住宿偏好建议
            accommodation_prefs = [p for p in user_prefs if p["type"] == "accommodation"]
            if accommodation_prefs:
                personalized_plan["recommendations"]["accommodation_type"] = "经济型"  # 简化处理
            
            return {
                "success": True,
                "data": personalized_plan
            }
            
        except Exception as e:
            return {"success": False, "message": f"生成个性化计划失败: {str(e)}"}
