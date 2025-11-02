"""
天气查询Agent
基于和风天气API实现天气查询和预警
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.agents.base_agent import AsyncAgent, AgentResponse, AgentType
from tools.weather_tools import QWeatherTool, WeatherAnalyzer
from tools.cache_tools import RedisCache
from loguru import logger


class WeatherAgent(AsyncAgent):
    """天气查询Agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.WEATHER,
            name="weather_agent",
            description="天气查询Agent，提供天气查询、预报和预警服务"
        )
        self.weather_tool = QWeatherTool()
        self.weather_analyzer = WeatherAnalyzer()
        self.cache = RedisCache()
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行天气查询"""
        query = kwargs.get("query", "")
        location = kwargs.get("location", "")
        days = kwargs.get("days", 7)
        user_id = kwargs.get("user_id")
        
        try:
            # 如果没有提供地点，尝试从查询中提取
            if not location:
                location = await self._extract_location_from_query(query)
            
            if not location:
                return self._create_error_response("请提供查询地点")
            
            # 检查缓存
            cached_result = await self.cache.get_cached_weather_data(location)
            if cached_result["success"]:
                logger.info("Using cached weather data")
                return self._create_success_response(
                    data=cached_result["data"],
                    message="使用缓存的天气数据"
                )
            
            # 执行天气查询
            weather_result = await self._get_weather_data(location, days)
            
            if not weather_result["success"]:
                return self._create_error_response(weather_result["message"])
            
            # 分析摩托车骑行安全性
            safety_analysis = await self._analyze_riding_safety(weather_result["data"])
            
            # 缓存结果
            await self.cache.cache_weather_data(location, weather_result["data"])
            
            # 构建完整结果
            result = {
                "location": location,
                "weather_data": weather_result["data"],
                "safety_analysis": safety_analysis,
                "recommendations": await self._generate_weather_recommendations(
                    weather_result["data"], safety_analysis
                )
            }
            
            return self._create_success_response(
                data=result,
                message="天气查询完成",
                metadata={
                    "location": location,
                    "days": days,
                    "user_id": user_id
                }
            )
            
        except Exception as e:
            logger.error(f"Weather query failed: {str(e)}")
            return self._create_error_response(f"天气查询失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        # 至少需要查询或地点
        has_query = bool(kwargs.get("query", ""))
        has_location = bool(kwargs.get("location", ""))
        
        return has_query or has_location
    
    async def _extract_location_from_query(self, query: str) -> str:
        """从查询中提取地点信息"""
        # 简单的关键词提取
        import re
        
        # 匹配城市名称
        city_patterns = [
            r"(.+?)的天气",
            r"(.+?)天气",
            r"(.+?)预报",
            r"(.+?)温度"
        ]
        
        for pattern in city_patterns:
            match = re.search(pattern, query)
            if match:
                location = match.group(1).strip()
                # 过滤掉一些无关词汇
                if location not in ["今天", "明天", "后天", "这", "那"]:
                    return location
        
        return ""
    
    async def _get_weather_data(self, location: str, days: int) -> Dict[str, Any]:
        """获取天气数据"""
        
        async with self.weather_tool:
            # 获取当前天气
            current_weather = await self.weather_tool.get_current_weather(location)
            if not current_weather["success"]:
                return {"success": False, "message": "获取当前天气失败"}
            
            # 获取逐小时天气
            hourly_weather = await self.weather_tool.get_hourly_weather(location, 24)
            
            # 获取逐日天气
            daily_weather = await self.weather_tool.get_daily_weather(location, days)
            
            # 获取天气预警
            weather_alerts = await self.weather_tool.get_weather_alerts(location)
            
            result = {
                "current": current_weather["data"],
                "hourly": hourly_weather["data"] if hourly_weather["success"] else {},
                "daily": daily_weather["data"] if daily_weather["success"] else {},
                "alerts": weather_alerts["data"] if weather_alerts["success"] else {}
            }
            
            return {"success": True, "data": result}
    
    async def _analyze_riding_safety(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析骑行安全性"""
        
        current_weather = weather_data.get("current", {})
        hourly_weather = weather_data.get("hourly", {}).get("hourly_weather", [])
        daily_weather = weather_data.get("daily", {}).get("daily_weather", [])
        alerts = weather_data.get("alerts", {}).get("warnings", [])
        
        # 分析当前天气安全性
        current_safety = self.weather_analyzer.analyze_motorcycle_safety(current_weather)
        
        # 分析未来24小时安全性
        hourly_safety = []
        for hour_data in hourly_weather[:24]:  # 取前24小时
            hour_safety = self.weather_analyzer.analyze_motorcycle_safety(hour_data)
            hourly_safety.append({
                "time": hour_data.get("time", ""),
                "safety": hour_safety
            })
        
        # 分析未来几天安全性
        daily_safety = []
        for day_data in daily_weather:
            day_safety = self.weather_analyzer.analyze_motorcycle_safety(day_data)
            daily_safety.append({
                "date": day_data.get("date", ""),
                "safety": day_safety
            })
        
        # 分析预警信息
        alert_analysis = self._analyze_weather_alerts(alerts)
        
        return {
            "current_safety": current_safety,
            "hourly_safety": hourly_safety,
            "daily_safety": daily_safety,
            "alert_analysis": alert_analysis,
            "overall_recommendation": self._get_overall_recommendation(
                current_safety, hourly_safety, daily_safety, alerts
            )
        }
    
    def _analyze_weather_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析天气预警"""
        
        if not alerts:
            return {"has_alerts": False, "message": "暂无天气预警"}
        
        # 按严重程度分类
        severity_levels = {"低": [], "中": [], "高": [], "极高": []}
        
        for alert in alerts:
            level = alert.get("level", "中")
            if level in severity_levels:
                severity_levels[level].append(alert)
        
        # 计算总体风险
        risk_score = 0
        if severity_levels["极高"]:
            risk_score = 4
        elif severity_levels["高"]:
            risk_score = 3
        elif severity_levels["中"]:
            risk_score = 2
        elif severity_levels["低"]:
            risk_score = 1
        
        return {
            "has_alerts": True,
            "risk_score": risk_score,
            "severity_distribution": {k: len(v) for k, v in severity_levels.items()},
            "alerts": alerts,
            "recommendation": self._get_alert_recommendation(risk_score)
        }
    
    def _get_alert_recommendation(self, risk_score: int) -> str:
        """获取预警建议"""
        recommendations = {
            0: "天气条件良好，适合骑行",
            1: "有轻微天气预警，注意观察天气变化",
            2: "有中等天气预警，建议谨慎出行",
            3: "有严重天气预警，建议推迟出行",
            4: "有极严重天气预警，强烈建议取消出行"
        }
        return recommendations.get(risk_score, "请关注天气变化")
    
    def _get_overall_recommendation(
        self, 
        current_safety: Dict[str, Any],
        hourly_safety: List[Dict[str, Any]],
        daily_safety: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """获取总体建议"""
        
        # 计算安全评分
        current_score = current_safety.get("safety_score", 100)
        
        # 计算未来24小时平均安全评分
        hourly_scores = [h["safety"]["safety_score"] for h in hourly_safety if h["safety"]["safety_score"]]
        avg_hourly_score = sum(hourly_scores) / len(hourly_scores) if hourly_scores else 100
        
        # 计算未来几天平均安全评分
        daily_scores = [d["safety"]["safety_score"] for d in daily_safety if d["safety"]["safety_score"]]
        avg_daily_score = sum(daily_scores) / len(daily_scores) if daily_scores else 100
        
        # 综合评分
        overall_score = (current_score + avg_hourly_score + avg_daily_score) / 3
        
        # 预警影响
        if alerts:
            overall_score -= len(alerts) * 10  # 每个预警减10分
        
        overall_score = max(0, min(100, overall_score))
        
        # 生成建议
        if overall_score >= 80:
            recommendation = "天气条件良好，适合骑行"
            suitable = True
        elif overall_score >= 60:
            recommendation = "天气条件一般，可以骑行但需注意安全"
            suitable = True
        elif overall_score >= 40:
            recommendation = "天气条件较差，建议谨慎出行"
            suitable = False
        else:
            recommendation = "天气条件恶劣，强烈建议取消出行"
            suitable = False
        
        return {
            "overall_score": round(overall_score, 1),
            "recommendation": recommendation,
            "suitable_for_riding": suitable,
            "confidence": "高" if len(hourly_scores) > 10 and len(daily_scores) > 3 else "中"
        }
    
    async def _generate_weather_recommendations(
        self, 
        weather_data: Dict[str, Any], 
        safety_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成天气相关建议"""
        
        recommendations = {
            "riding": [],
            "equipment": [],
            "timing": [],
            "safety": []
        }
        
        current_safety = safety_analysis.get("current_safety", {})
        overall_rec = safety_analysis.get("overall_recommendation", {})
        
        # 骑行建议
        if not overall_rec.get("suitable_for_riding", True):
            recommendations["riding"].append("建议推迟出行计划")
        else:
            recommendations["riding"].append("可以正常出行")
        
        # 装备建议
        current_weather = weather_data.get("current", {})
        temp = current_weather.get("temperature", 0)
        weather = current_weather.get("weather", "").lower()
        
        if temp < 10:
            recommendations["equipment"].append("温度较低，建议穿戴保暖装备")
        if temp > 30:
            recommendations["equipment"].append("温度较高，注意防暑降温")
        if "雨" in weather:
            recommendations["equipment"].append("有降水，建议携带雨具")
        if "雪" in weather:
            recommendations["equipment"].append("有降雪，建议使用防滑轮胎")
        
        # 时间建议
        hourly_safety = safety_analysis.get("hourly_safety", [])
        if hourly_safety:
            # 找出最安全的时段
            safe_hours = [h for h in hourly_safety if h["safety"]["suitable_for_riding"]]
            if safe_hours:
                recommendations["timing"].append("建议在安全时段出行")
            else:
                recommendations["timing"].append("全天天气条件不佳，建议调整出行时间")
        
        # 安全建议
        warnings = current_safety.get("warnings", [])
        for warning in warnings:
            recommendations["safety"].append(warning)
        
        return recommendations
