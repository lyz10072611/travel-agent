"""
天气工具（重构版）
从tools/weather_tools.py迁移，适配新架构
"""
from typing import Dict, List, Any, Optional
from tools.base_tool import RateLimitedTool
from app.config import settings
from loguru import logger


class QWeatherTool(RateLimitedTool):
    """和风天气工具"""
    
    def __init__(self):
        super().__init__(
            name="qweather_tool",
            description="和风天气智能查询工具",
            requests_per_minute=200
        )
        self.api_key = settings.qweather_api_key
        self.base_url = settings.qweather_base_url
    
    async def get_current_weather(self, location: str) -> Dict[str, Any]:
        """获取当前天气"""
        self.validate_params(["location"], location=location)
        
        location_info = await self._get_location_info(location)
        if not location_info["success"]:
            return location_info
        
        location_id = location_info["data"]["id"]
        
        url = f"{self.base_url}/weather/now"
        params = {
            "location": location_id,
            "lang": "zh"
        }
        
        # base_tool会自动添加api_key到params['key']
        result = await self._make_request(url, params=params)
        
        if result.get("code") == "200":
            now = result.get("now", {})
            return self.format_response({
                "location": location_info["data"]["name"],
                "temperature": now.get("temp"),
                "feels_like": now.get("feelsLike"),
                "weather": now.get("text"),
                "weather_code": now.get("icon"),
                "humidity": now.get("humidity"),
                "wind_direction": now.get("windDir"),
                "wind_scale": now.get("windScale"),
                "wind_speed": now.get("windSpeed"),
                "pressure": now.get("pressure"),
                "visibility": now.get("vis"),
                "update_time": now.get("obsTime")
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"Weather query failed: {result.get('code')}"
            )
    
    async def get_hourly_weather(self, location: str, hours: int = 24) -> Dict[str, Any]:
        """获取逐小时天气"""
        self.validate_params(["location"], location=location)
        
        location_info = await self._get_location_info(location)
        if not location_info["success"]:
            return location_info
        
        location_id = location_info["data"]["id"]
        
        url = f"{self.base_url}/weather/24h"
        params = {
            "location": location_id,
            "lang": "zh",
            "key": self.api_key
        }
        
        result = await self._make_request(url, params=params)
        
        if result.get("code") == "200":
            hourly_data = result.get("hourly", [])[:hours]
            processed_hourly = []
            
            for hour in hourly_data:
                processed_hourly.append({
                    "time": hour.get("fxTime"),
                    "temperature": hour.get("temp"),
                    "weather": hour.get("text"),
                    "weather_code": hour.get("icon"),
                    "humidity": hour.get("humidity"),
                    "wind_direction": hour.get("windDir"),
                    "wind_scale": hour.get("windScale"),
                    "wind_speed": hour.get("windSpeed"),
                    "pressure": hour.get("pressure"),
                    "precipitation": hour.get("precip"),
                    "pop": hour.get("pop")
                })
            
            return self.format_response({
                "location": location_info["data"]["name"],
                "hourly_weather": processed_hourly
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"Hourly weather query failed: {result.get('code')}"
            )
    
    async def get_daily_weather(self, location: str, days: int = 7) -> Dict[str, Any]:
        """获取逐日天气"""
        self.validate_params(["location"], location=location)
        
        location_info = await self._get_location_info(location)
        if not location_info["success"]:
            return location_info
        
        location_id = location_info["data"]["id"]
        
        url = f"{self.base_url}/weather/7d"
        params = {
            "location": location_id,
            "lang": "zh",
            "key": self.api_key
        }
        
        result = await self._make_request(url, params=params)
        
        if result.get("code") == "200":
            daily_data = result.get("daily", [])[:days]
            processed_daily = []
            
            for day in daily_data:
                processed_daily.append({
                    "date": day.get("fxDate"),
                    "weather_day": day.get("textDay"),
                    "weather_night": day.get("textNight"),
                    "temp_max": day.get("tempMax"),
                    "temp_min": day.get("tempMin"),
                    "humidity": day.get("humidity"),
                    "wind_direction": day.get("windDirDay"),
                    "wind_scale": day.get("windScaleDay"),
                    "wind_speed": day.get("windSpeedDay"),
                    "precipitation": day.get("precip"),
                    "pop": day.get("pop"),
                    "uv_index": day.get("uvIndex")
                })
            
            return self.format_response({
                "location": location_info["data"]["name"],
                "daily_weather": processed_daily
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"Daily weather query failed: {result.get('code')}"
            )
    
    async def get_weather_alerts(self, location: str) -> Dict[str, Any]:
        """获取天气预警"""
        self.validate_params(["location"], location=location)
        
        location_info = await self._get_location_info(location)
        if not location_info["success"]:
            return location_info
        
        location_id = location_info["data"]["id"]
        
        url = f"{self.base_url}/warning/now"
        params = {
            "location": location_id,
            "lang": "zh",
            "key": self.api_key
        }
        
        result = await self._make_request(url, params=params)
        
        if result.get("code") == "200":
            warnings = result.get("warning", [])
            processed_warnings = []
            
            for warning in warnings:
                processed_warnings.append({
                    "title": warning.get("title"),
                    "status": warning.get("status"),
                    "level": warning.get("level"),
                    "type": warning.get("type"),
                    "type_name": warning.get("typeName"),
                    "text": warning.get("text"),
                    "pub_time": warning.get("pubTime"),
                    "start_time": warning.get("startTime"),
                    "end_time": warning.get("endTime")
                })
            
            return self.format_response({
                "location": location_info["data"]["name"],
                "warnings": processed_warnings
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"Weather alerts query failed: {result.get('code')}"
            )
    
    async def _get_location_info(self, location: str) -> Dict[str, Any]:
        """获取位置信息"""
        url = f"{self.base_url}/city/lookup"
        params = {
            "location": location,
            "lang": "zh",
            "key": self.api_key
        }
        
        result = await self._make_request(url, params=params)
        
        if result.get("code") == "200" and result.get("location"):
            locations = result["location"]
            if locations:
                location_data = locations[0]
                return self.format_response({
                    "id": location_data.get("id"),
                    "name": location_data.get("name"),
                    "country": location_data.get("country"),
                    "adm1": location_data.get("adm1"),
                    "adm2": location_data.get("adm2"),
                    "lat": location_data.get("lat"),
                    "lon": location_data.get("lon")
                })
        
        return self.format_response(
            None,
            success=False,
            message=f"Location lookup failed: {result.get('code')}"
        )

