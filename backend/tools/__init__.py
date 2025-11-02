"""
工具模块初始化文件
统一导入所有LangChain工具
"""

from .web_search_tool import WebSearchTool
from .hotel_search_tool import HotelSearchTool
from .flight_search_tool import FlightSearchTool
from .restaurant_search_tool import RestaurantSearchTool
from .attraction_search_tool import AttractionSearchTool
from .weather_search_tool import WeatherSearchTool

# 创建工具实例
web_search_tool = WebSearchTool()
hotel_search_tool = HotelSearchTool()
flight_search_tool = FlightSearchTool()
restaurant_search_tool = RestaurantSearchTool()
attraction_search_tool = AttractionSearchTool()
weather_search_tool = WeatherSearchTool()

# 导出所有工具
__all__ = [
    "WebSearchTool",
    "HotelSearchTool", 
    "FlightSearchTool",
    "RestaurantSearchTool",
    "AttractionSearchTool",
    "WeatherSearchTool",
    "web_search_tool",
    "hotel_search_tool",
    "flight_search_tool", 
    "restaurant_search_tool",
    "attraction_search_tool",
    "weather_search_tool"
]
