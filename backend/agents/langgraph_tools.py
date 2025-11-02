"""
LangGraph工具管理
统一管理所有LangChain工具
"""

from typing import List, Dict, Any
from tools import (
    web_search_tool,
    hotel_search_tool,
    flight_search_tool,
    restaurant_search_tool,
    attraction_search_tool,
    weather_search_tool
)


# 工具映射
TOOL_MAP = {
    "web_search": web_search_tool,
    "hotel_search": hotel_search_tool,
    "flight_search": flight_search_tool,
    "restaurant_search": restaurant_search_tool,
    "attraction_search": attraction_search_tool,
    "weather_search": weather_search_tool
}


def get_all_tools(tool_names: List[str] = None) -> List:
    """获取指定的工具列表"""
    if tool_names is None:
        return list(TOOL_MAP.values())
    
    tools = []
    for name in tool_names:
        if name in TOOL_MAP:
            tools.append(TOOL_MAP[name])
        else:
            print(f"警告: 未找到工具 {name}")
    
    return tools


def get_tool_by_name(tool_name: str):
    """根据名称获取单个工具"""
    return TOOL_MAP.get(tool_name)


def get_available_tools() -> List[str]:
    """获取所有可用工具的名称列表"""
    return list(TOOL_MAP.keys())


# 预定义的工具组合
TOOL_COMBINATIONS = {
    "destination": ["web_search", "attraction_search", "weather_search"],
    "flight": ["flight_search", "web_search", "weather_search"],
    "hotel": ["hotel_search", "web_search", "weather_search"],
    "dining": ["restaurant_search", "web_search", "weather_search"],
    "itinerary": ["web_search", "attraction_search", "weather_search", "restaurant_search"],
    "budget": ["web_search", "hotel_search", "flight_search", "restaurant_search"]
}


def get_tools_for_agent(agent_type: str) -> List:
    """根据代理类型获取对应的工具组合"""
    if agent_type in TOOL_COMBINATIONS:
        return get_all_tools(TOOL_COMBINATIONS[agent_type])
    else:
        return get_all_tools()
