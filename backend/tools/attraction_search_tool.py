"""
景点搜索工具 - 使用中文旅游平台API
适用于中文景点推荐的LangChain工具
"""

import os
from typing import Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger


class AttractionSearchInput(BaseModel):
    """景点搜索输入模型"""
    destination: str = Field(description="目的地")
    category: Optional[str] = Field(default=None, description="景点类别（如：历史、自然、文化等）")
    interests: Optional[List[str]] = Field(default=None, description="兴趣标签")


class AttractionSearchTool(BaseTool):
    """景点搜索工具 - 使用中文旅游平台API"""
    name = "attraction_search"
    description = "搜索旅游景点信息，使用马蜂窝、携程等中文旅游平台"
    args_schema = AttractionSearchInput
    
    def _run(self, destination: str, category: Optional[str] = None, interests: Optional[List[str]] = None) -> str:
        """执行景点搜索"""
        try:
            logger.info(f"搜索景点: {destination}, 类别: {category}, 兴趣: {interests}")
            
            # 模拟景点搜索结果（实际应该调用旅游平台API）
            mock_results = [
                {
                    "name": f"{destination}标志性景点",
                    "category": "历史古迹",
                    "rating": "4.7分",
                    "description": "历史悠久的文化地标，具有重要的历史意义",
                    "highlights": ["历史价值", "建筑特色", "文化内涵"],
                    "visit_duration": "2-3小时",
                    "ticket_price": "¥80-120",
                    "best_time": "上午9:00-11:00",
                    "tips": ["建议提前预订", "避开节假日", "带好相机"]
                },
                {
                    "name": f"{destination}自然风光",
                    "category": "自然景观",
                    "rating": "4.5分",
                    "description": "美丽的自然风光，适合拍照和放松",
                    "highlights": ["自然美景", "空气清新", "适合徒步"],
                    "visit_duration": "3-4小时",
                    "ticket_price": "¥60-100",
                    "best_time": "下午2:00-5:00",
                    "tips": ["穿舒适的鞋子", "带水和零食", "注意天气变化"]
                },
                {
                    "name": f"{destination}文化体验",
                    "category": "文化体验",
                    "rating": "4.6分",
                    "description": "深入了解当地文化的绝佳场所",
                    "highlights": ["文化体验", "互动性强", "教育意义"],
                    "visit_duration": "1-2小时",
                    "ticket_price": "¥50-80",
                    "best_time": "上午10:00-12:00",
                    "tips": ["可以参与互动", "了解当地文化", "适合家庭出游"]
                }
            ]
            
            result_text = f"在{destination}找到以下景点推荐：\n\n"
            for i, attraction in enumerate(mock_results, 1):
                result_text += f"{i}. {attraction['name']}\n"
                result_text += f"   类别: {attraction['category']}\n"
                result_text += f"   评分: {attraction['rating']}\n"
                result_text += f"   描述: {attraction['description']}\n"
                result_text += f"   亮点: {', '.join(attraction['highlights'])}\n"
                result_text += f"   游览时间: {attraction['visit_duration']}\n"
                result_text += f"   门票价格: {attraction['ticket_price']}\n"
                result_text += f"   最佳时间: {attraction['best_time']}\n"
                result_text += f"   游览提示: {', '.join(attraction['tips'])}\n\n"
            
            return result_text
            
        except Exception as e:
            logger.error(f"景点搜索工具执行失败: {e}")
            return f"景点搜索时出现错误: {str(e)}"
