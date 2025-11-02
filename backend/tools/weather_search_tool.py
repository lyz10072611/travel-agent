"""
天气查询工具 - 使用中文天气API
适用于中文天气查询的LangChain工具
"""

import os
import requests
from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger


class WeatherSearchInput(BaseModel):
    """天气查询输入模型"""
    location: str = Field(description="查询地点")
    date: Optional[str] = Field(default=None, description="查询日期，格式：YYYY-MM-DD，默认为今天")


class WeatherSearchTool(BaseTool):
    """天气查询工具 - 使用中文天气API"""
    name = "weather_search"
    description = "查询天气信息，使用中国天气网等中文天气平台"
    args_schema = WeatherSearchInput
    
    def _run(self, location: str, date: Optional[str] = None) -> str:
        """执行天气查询"""
        try:
            logger.info(f"查询天气: {location}, 日期: {date or '今天'}")
            
            # 模拟天气查询结果（实际应该调用天气API）
            mock_weather_data = {
                "location": location,
                "date": date or "今天",
                "temperature": {
                    "high": "25°C",
                    "low": "18°C",
                    "current": "22°C"
                },
                "condition": "多云转晴",
                "humidity": "65%",
                "wind": "东南风 3-4级",
                "air_quality": "良好",
                "uv_index": "中等",
                "forecast": [
                    {"day": "今天", "condition": "多云转晴", "high": "25°C", "low": "18°C"},
                    {"day": "明天", "condition": "晴", "high": "27°C", "low": "20°C"},
                    {"day": "后天", "condition": "小雨", "high": "23°C", "low": "16°C"}
                ],
                "tips": [
                    "适合户外活动",
                    "建议携带薄外套",
                    "注意防晒",
                    "空气质量良好"
                ]
            }
            
            result_text = f"{location}的天气信息：\n\n"
            result_text += f"日期: {mock_weather_data['date']}\n"
            result_text += f"当前温度: {mock_weather_data['temperature']['current']}\n"
            result_text += f"最高温度: {mock_weather_data['temperature']['high']}\n"
            result_text += f"最低温度: {mock_weather_data['temperature']['low']}\n"
            result_text += f"天气状况: {mock_weather_data['condition']}\n"
            result_text += f"湿度: {mock_weather_data['humidity']}\n"
            result_text += f"风力: {mock_weather_data['wind']}\n"
            result_text += f"空气质量: {mock_weather_data['air_quality']}\n"
            result_text += f"紫外线指数: {mock_weather_data['uv_index']}\n\n"
            
            result_text += "未来3天天气预报：\n"
            for forecast in mock_weather_data['forecast']:
                result_text += f"{forecast['day']}: {forecast['condition']} {forecast['high']}/{forecast['low']}\n"
            
            result_text += f"\n出行建议：\n"
            for tip in mock_weather_data['tips']:
                result_text += f"• {tip}\n"
            
            return result_text
            
        except Exception as e:
            logger.error(f"天气查询工具执行失败: {e}")
            return f"天气查询时出现错误: {str(e)}"
