"""
天气查询Agent（重构版）
支持A2A协议
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from app.agents.base.agent import BaseAgent, AgentResponse
from app.agents.base.message import RequestMessage, ResponseMessage
from app.agents.weather.tools.weather_tool import QWeatherTool
from app.agents.weather.tools.weather_analyzer import WeatherAnalyzer


class WeatherAgent(BaseAgent):
    """天气查询Agent"""
    
    def __init__(self):
        super().__init__(
            name="weather",
            description="天气查询Agent，提供天气查询、预报和预警服务，支持摩旅安全评估"
        )
        self.weather_tool = QWeatherTool()
        self.weather_analyzer = WeatherAnalyzer()
        
        # 注册A2A动作处理器
        self.register_action_handler("get_weather", self._handle_get_weather)
        self.register_action_handler("get_forecast", self._handle_get_forecast)
        self.register_action_handler("check_weather_risk", self._handle_check_weather_risk)
    
    async def handle_request(self, request: RequestMessage) -> ResponseMessage:
        """处理A2A请求"""
        action = request.action
        payload = request.payload
        
        try:
            if action == "get_weather":
                result = await self._handle_get_weather(payload)
            elif action == "get_forecast":
                result = await self._handle_get_forecast(payload)
            elif action == "check_weather_risk":
                result = await self._handle_check_weather_risk(payload)
            else:
                return ResponseMessage(
                    from_agent=self.name,
                    to_agent=request.from_agent,
                    action=action,
                    success=False,
                    error=f"Unknown action: {action}",
                    original_request_id=request.request_id,
                    payload={}
                )
            
            return ResponseMessage(
                from_agent=self.name,
                to_agent=request.from_agent,
                action=action,
                success=True,
                payload=result if isinstance(result, dict) else {"result": result},
                original_request_id=request.request_id
            )
        except Exception as e:
            logger.error(f"Weather agent error: {str(e)}")
            return ResponseMessage(
                from_agent=self.name,
                to_agent=request.from_agent,
                action=action,
                success=False,
                error=str(e),
                original_request_id=request.request_id,
                payload={}
            )
    
    async def _handle_get_weather(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理天气查询请求"""
        location = payload.get("location")
        if not location:
            raise ValueError("Location is required")
        
        async with self.weather_tool:
            # 获取当前天气
            current_result = await self.weather_tool.get_current_weather(location)
            if not current_result["success"]:
                raise ValueError(f"Failed to get weather: {current_result['message']}")
            
            current_weather = current_result["data"]
            
            # 分析安全性
            safety_analysis = self.weather_analyzer.analyze_motorcycle_safety(current_weather)
            
            return {
                "location": location,
                "current_weather": current_weather,
                "safety_analysis": safety_analysis
            }
    
    async def _handle_get_forecast(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理天气预报请求"""
        location = payload.get("location")
        days = payload.get("days", 7)
        
        if not location:
            raise ValueError("Location is required")
        
        async with self.weather_tool:
            # 获取逐小时天气
            hourly_result = await self.weather_tool.get_hourly_weather(location, 24)
            
            # 获取逐日天气
            daily_result = await self.weather_tool.get_daily_weather(location, days)
            
            # 获取预警
            alerts_result = await self.weather_tool.get_weather_alerts(location)
            
            return {
                "location": location,
                "hourly_forecast": hourly_result["data"] if hourly_result["success"] else {},
                "daily_forecast": daily_result["data"] if daily_result["success"] else {},
                "alerts": alerts_result["data"] if alerts_result["success"] else {}
            }
    
    async def _handle_check_weather_risk(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """检查天气风险"""
        location = payload.get("location")
        if not location:
            raise ValueError("Location is required")
        
        async with self.weather_tool:
            # 获取当前天气和预警
            current_result = await self.weather_tool.get_current_weather(location)
            alerts_result = await self.weather_tool.get_weather_alerts(location)
            
            if not current_result["success"]:
                raise ValueError(f"Failed to get weather: {current_result['message']}")
            
            current_weather = current_result["data"]
            alerts = alerts_result["data"].get("warnings", []) if alerts_result["success"] else []
            
            # 分析风险
            safety_analysis = self.weather_analyzer.analyze_motorcycle_safety(current_weather)
            
            # 评估预警风险
            risk_level = "低"
            if alerts:
                high_level_alerts = [a for a in alerts if a.get("level") in ["高", "极高"]]
                if high_level_alerts:
                    risk_level = "高"
                else:
                    risk_level = "中"
            
            return {
                "location": location,
                "risk_level": risk_level,
                "safety_analysis": safety_analysis,
                "alerts": alerts,
                "recommendation": self._get_risk_recommendation(safety_analysis, alerts)
            }
    
    def _get_risk_recommendation(
        self,
        safety_analysis: Dict[str, Any],
        alerts: List[Dict[str, Any]]
    ) -> str:
        """获取风险建议"""
        if not safety_analysis.get("suitable_for_riding", True):
            return "天气条件不适合骑行，建议推迟出行"
        
        if alerts:
            high_alerts = [a for a in alerts if a.get("level") in ["高", "极高"]]
            if high_alerts:
                return "有严重天气预警，建议取消或推迟出行"
            else:
                return "有天气预警，建议谨慎出行"
        
        return "天气条件良好，可以正常出行"
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行天气查询（兼容旧接口）"""
        try:
            location = kwargs.get("location") or kwargs.get("query", "")
            days = kwargs.get("days", 7)
            
            if not location:
                return self._create_error_response("请提供查询地点")
            
            result = await self._handle_get_forecast({
                "location": location,
                "days": days
            })
            
            # 添加安全分析
            if result.get("daily_forecast", {}).get("daily_weather"):
                first_day = result["daily_forecast"]["daily_weather"][0]
                safety_analysis = self.weather_analyzer.analyze_motorcycle_safety(first_day)
                result["safety_analysis"] = safety_analysis
            
            return self._create_success_response(
                data=result,
                message="天气查询完成",
                metadata={
                    "location": location,
                    "days": days,
                    "user_id": kwargs.get("user_id")
                }
            )
        except Exception as e:
            logger.error(f"Weather query failed: {str(e)}")
            return self._create_error_response(f"天气查询失败: {str(e)}")

