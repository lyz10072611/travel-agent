"""
酒店搜索工具 - 使用携程API
适用于中文酒店预订的LangChain工具
"""

import os
from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger


class HotelSearchInput(BaseModel):
    """酒店搜索输入模型"""
    destination: str = Field(description="目的地")
    check_in: str = Field(description="入住日期，格式：YYYY-MM-DD")
    check_out: str = Field(description="退房日期，格式：YYYY-MM-DD")
    adults: int = Field(default=1, description="成人数量")
    children: int = Field(default=0, description="儿童数量")


class HotelSearchTool(BaseTool):
    """酒店搜索工具 - 使用携程API"""
    name = "hotel_search"
    description = "搜索酒店信息，使用携程等中文酒店预订平台"
    args_schema = HotelSearchInput
    
    def _run(self, destination: str, check_in: str, check_out: str, adults: int = 1, children: int = 0) -> str:
        """执行酒店搜索"""
        try:
            logger.info(f"搜索酒店: {destination}, {check_in}到{check_out}")
            
            # 模拟酒店搜索结果（实际应该调用携程API）
            mock_results = [
                {
                    "name": f"{destination}豪华酒店",
                    "price": "¥588/晚",
                    "rating": "4.5分",
                    "address": f"{destination}市中心",
                    "amenities": ["免费WiFi", "健身房", "游泳池", "餐厅"],
                    "description": "位于市中心，交通便利，设施完善"
                },
                {
                    "name": f"{destination}商务酒店",
                    "price": "¥388/晚", 
                    "rating": "4.2分",
                    "address": f"{destination}商业区",
                    "amenities": ["免费WiFi", "会议室", "商务中心"],
                    "description": "适合商务出行，性价比高"
                },
                {
                    "name": f"{destination}精品酒店",
                    "price": "¥688/晚",
                    "rating": "4.7分",
                    "address": f"{destination}文化区",
                    "amenities": ["免费WiFi", "SPA", "艺术画廊", "屋顶酒吧"],
                    "description": "设计感强，文化氛围浓厚"
                }
            ]
            
            result_text = f"在{destination}找到以下酒店推荐：\n\n"
            for i, hotel in enumerate(mock_results, 1):
                result_text += f"{i}. {hotel['name']}\n"
                result_text += f"   价格: {hotel['price']}\n"
                result_text += f"   评分: {hotel['rating']}\n"
                result_text += f"   地址: {hotel['address']}\n"
                result_text += f"   设施: {', '.join(hotel['amenities'])}\n"
                result_text += f"   描述: {hotel['description']}\n\n"
            
            return result_text
            
        except Exception as e:
            logger.error(f"酒店搜索工具执行失败: {e}")
            return f"酒店搜索时出现错误: {str(e)}"
