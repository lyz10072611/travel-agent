"""
餐厅搜索工具 - 使用大众点评API
适用于中文餐饮平台的LangChain工具
"""

import os
from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger


class RestaurantSearchInput(BaseModel):
    """餐厅搜索输入模型"""
    location: str = Field(description="搜索位置")
    cuisine: Optional[str] = Field(default=None, description="菜系类型")
    price_range: Optional[str] = Field(default=None, description="价格范围")


class RestaurantSearchTool(BaseTool):
    """餐厅搜索工具 - 使用大众点评API"""
    name = "restaurant_search"
    description = "搜索餐厅信息，使用大众点评等中文餐饮平台"
    args_schema = RestaurantSearchInput
    
    def _run(self, location: str, cuisine: Optional[str] = None, price_range: Optional[str] = None) -> str:
        """执行餐厅搜索"""
        try:
            logger.info(f"搜索餐厅: {location}, 菜系: {cuisine}, 价格: {price_range}")
            
            # 模拟餐厅搜索结果（实际应该调用大众点评API）
            mock_results = [
                {
                    "name": f"{location}特色餐厅",
                    "cuisine": cuisine or "当地菜",
                    "price_range": "¥80-120/人",
                    "rating": "4.6分",
                    "address": f"{location}美食街",
                    "description": "正宗当地风味，环境优雅",
                    "specialties": ["招牌菜1", "招牌菜2", "招牌菜3"],
                    "opening_hours": "11:00-22:00"
                },
                {
                    "name": f"{location}网红餐厅",
                    "cuisine": "创意菜",
                    "price_range": "¥120-200/人", 
                    "rating": "4.4分",
                    "address": f"{location}商业中心",
                    "description": "创意料理，适合拍照打卡",
                    "specialties": ["创意菜1", "创意菜2", "创意菜3"],
                    "opening_hours": "10:00-23:00"
                },
                {
                    "name": f"{location}传统老店",
                    "cuisine": "传统菜",
                    "price_range": "¥60-100/人",
                    "rating": "4.8分",
                    "address": f"{location}老城区",
                    "description": "百年老店，传承经典",
                    "specialties": ["传统菜1", "传统菜2", "传统菜3"],
                    "opening_hours": "09:00-21:00"
                }
            ]
            
            result_text = f"在{location}找到以下餐厅推荐：\n\n"
            for i, restaurant in enumerate(mock_results, 1):
                result_text += f"{i}. {restaurant['name']}\n"
                result_text += f"   菜系: {restaurant['cuisine']}\n"
                result_text += f"   价格: {restaurant['price_range']}\n"
                result_text += f"   评分: {restaurant['rating']}\n"
                result_text += f"   地址: {restaurant['address']}\n"
                result_text += f"   营业时间: {restaurant['opening_hours']}\n"
                result_text += f"   描述: {restaurant['description']}\n"
                result_text += f"   招牌菜: {', '.join(restaurant['specialties'])}\n\n"
            
            return result_text
            
        except Exception as e:
            logger.error(f"餐厅搜索工具执行失败: {e}")
            return f"餐厅搜索时出现错误: {str(e)}"
