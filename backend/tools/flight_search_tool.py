"""
航班搜索工具 - 使用去哪儿网API
适用于中文航班预订的LangChain工具
"""

import os
from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger


class FlightSearchInput(BaseModel):
    """航班搜索输入模型"""
    departure: str = Field(description="出发城市")
    destination: str = Field(description="目的地城市")
    date: str = Field(description="出发日期，格式：YYYY-MM-DD")
    return_date: Optional[str] = Field(default=None, description="返程日期，格式：YYYY-MM-DD")
    adults: int = Field(default=1, description="成人数量")
    children: int = Field(default=0, description="儿童数量")


class FlightSearchTool(BaseTool):
    """航班搜索工具 - 使用去哪儿网API"""
    name = "flight_search"
    description = "搜索航班信息，使用去哪儿网等中文航班预订平台"
    args_schema = FlightSearchInput
    
    def _run(self, departure: str, destination: str, date: str, return_date: Optional[str] = None, adults: int = 1, children: int = 0) -> str:
        """执行航班搜索"""
        try:
            logger.info(f"搜索航班: {departure}到{destination}, {date}")
            
            # 模拟航班搜索结果（实际应该调用去哪儿网API）
            mock_results = [
                {
                    "flight_number": "CA1234",
                    "airline": "中国国际航空",
                    "departure_time": "08:30",
                    "arrival_time": "11:45",
                    "duration": "3小时15分钟",
                    "price": "¥1,280",
                    "stops": 0,
                    "aircraft": "波音737-800"
                },
                {
                    "flight_number": "MU5678",
                    "airline": "中国东方航空", 
                    "departure_time": "14:20",
                    "arrival_time": "17:35",
                    "duration": "3小时15分钟",
                    "price": "¥1,150",
                    "stops": 0,
                    "aircraft": "空客A320"
                },
                {
                    "flight_number": "CZ9012",
                    "airline": "中国南方航空",
                    "departure_time": "19:45",
                    "arrival_time": "23:00",
                    "duration": "3小时15分钟",
                    "price": "¥1,320",
                    "stops": 0,
                    "aircraft": "波音787"
                }
            ]
            
            result_text = f"从{departure}到{destination}的航班推荐：\n\n"
            for i, flight in enumerate(mock_results, 1):
                result_text += f"{i}. {flight['airline']} {flight['flight_number']}\n"
                result_text += f"   出发时间: {flight['departure_time']}\n"
                result_text += f"   到达时间: {flight['arrival_time']}\n"
                result_text += f"   飞行时间: {flight['duration']}\n"
                result_text += f"   价格: {flight['price']}\n"
                result_text += f"   机型: {flight['aircraft']}\n"
                result_text += f"   中转: {'直飞' if flight['stops'] == 0 else f'{flight['stops']}次中转'}\n\n"
            
            if return_date:
                result_text += f"\n返程航班（{return_date}）:\n"
                result_text += "返程航班信息将根据实际需求进行搜索...\n"
            
            return result_text
            
        except Exception as e:
            logger.error(f"航班搜索工具执行失败: {e}")
            return f"航班搜索时出现错误: {str(e)}"
