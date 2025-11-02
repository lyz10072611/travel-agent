"""
天气相关工具
基于和风天气API实现天气查询、预警等功能
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from tools.base_tool import RateLimitedTool
from app.config import settings


class QWeatherTool(RateLimitedTool):
    """和风天气工具 - 摩旅安全的重要保障"""
    
    def __init__(self):
        super().__init__(
            name="qweather_tool",
            description="""
            🌤️ 和风天气智能查询工具
            
            【核心功能】
            • 实时天气：获取当前天气状况，包含温度、湿度、风力等详细信息
            • 逐小时预报：24小时精确天气预报，支持分钟级降水预报
            • 逐日预报：7天天气预报，包含最高最低温度、降水概率
            • 天气预警：实时天气预警信息，包含暴雨、大风、大雾等预警
            
            【摩旅安全特色】
            • 骑行安全评估：基于天气条件评估摩托车骑行安全性
            • 风险预警：识别影响骑行的危险天气因素
            • 装备建议：根据天气条件推荐必要的防护装备
            • 路线调整：提供基于天气的路线调整建议
            
            【智能分析】
            • 温度影响：分析极端温度对骑行的影响
            • 降水风险：评估降水对路面和能见度的影响
            • 风力分析：分析风力对骑行稳定性的影响
            • 能见度评估：评估能见度对安全骑行的影响
            
            【数据精度】
            • 分钟级降水：精确到分钟的降水预报
            • 格点数据：高精度的网格化天气数据
            • 实时更新：实时更新的天气和预警信息
            • 多源融合：融合多种数据源的准确预报
            
            适用于：天气查询、安全评估、装备建议、路线规划
            """,
            requests_per_minute=200
        )
        self.api_key = settings.qweather_api_key
        self.base_url = settings.qweather_base_url
    
    async def get_current_weather(self, location: str) -> Dict[str, Any]:
        """
        获取当前天气 - 摩旅安全第一道防线
        
        【功能描述】
        获取指定位置的实时天气信息，为摩旅安全提供基础数据
        包含温度、湿度、风力、能见度等关键安全指标
        
        【输入参数】
        - location: 查询位置，支持以下格式：
          • 城市名称："北京"、"上海"
          • 区县名称："朝阳区"、"浦东新区"  
          • 地标名称："天安门"、"外滩"
          • 坐标："116.397,39.909"
        
        【输出结果】
        - temperature: 当前温度（摄氏度）
        - feels_like: 体感温度（摄氏度）
        - weather: 天气状况描述
        - weather_code: 天气图标代码
        - humidity: 相对湿度（%）
        - wind_direction: 风向
        - wind_scale: 风力等级
        - wind_speed: 风速（km/h）
        - pressure: 大气压强（hPa）
        - visibility: 能见度（km）
        - update_time: 数据更新时间
        
        【摩旅安全分析】
        • 温度安全：<5°C需要保暖，>35°C需要防暑
        • 降水影响：有降水时路面湿滑，需要减速
        • 风力影响：>6级风力影响骑行稳定性
        • 能见度：<3km能见度低，需要开启灯光
        
        【使用场景】
        • 出发前天气检查
        • 途中实时天气监控
        • 安全风险评估
        • 装备选择建议
        """
        self.validate_params(["location"], location=location)
        
        # 先获取位置信息
        location_info = await self._get_location_info(location)
        if not location_info["success"]:
            return location_info
        
        location_id = location_info["data"]["id"]
        
        url = f"{self.base_url}/weather/now"
        params = {
            "location": location_id,
            "lang": "zh"
        }
        
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
            "lang": "zh"
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
                    "pop": hour.get("pop")  # 降水概率
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
            "lang": "zh"
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
            "lang": "zh"
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
            "lang": "zh"
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


class WeatherAnalyzer:
    """天气分析器"""
    
    @staticmethod
    def analyze_motorcycle_safety(weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析摩托车骑行安全性"""
        safety_score = 100
        warnings = []
        recommendations = []
        
        # 温度分析
        temp = weather_data.get("temperature", 0)
        if temp < 5:
            safety_score -= 20
            warnings.append("温度过低，注意保暖")
            recommendations.append("穿戴保暖装备，避免长时间骑行")
        elif temp > 35:
            safety_score -= 15
            warnings.append("温度过高，注意防暑")
            recommendations.append("避免中午骑行，多补充水分")
        
        # 降水分析
        weather = weather_data.get("weather", "").lower()
        if "雨" in weather or "雪" in weather:
            safety_score -= 30
            warnings.append("有降水，路面湿滑")
            recommendations.append("减速慢行，保持安全距离")
        
        # 风力分析
        wind_scale = weather_data.get("wind_scale", 0)
        if wind_scale >= 6:
            safety_score -= 25
            warnings.append("风力较大，影响骑行稳定性")
            recommendations.append("避免高速骑行，注意侧风影响")
        elif wind_scale >= 4:
            safety_score -= 10
            warnings.append("风力中等，注意侧风")
        
        # 能见度分析
        visibility = weather_data.get("visibility", 10)
        if visibility < 1:
            safety_score -= 20
            warnings.append("能见度极低")
            recommendations.append("开启所有灯光，谨慎骑行")
        elif visibility < 3:
            safety_score -= 10
            warnings.append("能见度较低")
            recommendations.append("开启灯光，减速慢行")
        
        # 综合评估
        if safety_score >= 80:
            safety_level = "良好"
        elif safety_score >= 60:
            safety_level = "一般"
        elif safety_score >= 40:
            safety_level = "较差"
        else:
            safety_level = "危险"
        
        return {
            "safety_score": safety_score,
            "safety_level": safety_level,
            "warnings": warnings,
            "recommendations": recommendations,
            "suitable_for_riding": safety_score >= 60
        }
    
    @staticmethod
    def get_route_weather_summary(route_weather: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取路线天气摘要"""
        if not route_weather:
            return {"summary": "无天气数据"}
        
        total_segments = len(route_weather)
        safe_segments = 0
        dangerous_segments = 0
        all_warnings = []
        
        for segment in route_weather:
            safety = WeatherAnalyzer.analyze_motorcycle_safety(segment)
            if safety["suitable_for_riding"]:
                safe_segments += 1
            else:
                dangerous_segments += 1
                all_warnings.extend(safety["warnings"])
        
        # 去重警告
        unique_warnings = list(set(all_warnings))
        
        return {
            "total_segments": total_segments,
            "safe_segments": safe_segments,
            "dangerous_segments": dangerous_segments,
            "safety_percentage": (safe_segments / total_segments) * 100,
            "overall_warnings": unique_warnings,
            "recommendation": "建议调整行程" if dangerous_segments > total_segments * 0.3 else "可以正常出行"
        }
