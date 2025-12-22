"""
天气分析器
分析摩托车骑行安全性
"""
from typing import Dict, List, Any


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
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except:
                temp = 0
        
        if temp < 5:
            safety_score -= 20
            warnings.append("温度过低，注意保暖")
            recommendations.append("穿戴保暖装备，避免长时间骑行")
        elif temp > 35:
            safety_score -= 15
            warnings.append("温度过高，注意防暑")
            recommendations.append("避免中午骑行，多补充水分")
        
        # 降水分析
        weather = str(weather_data.get("weather", "")).lower()
        if "雨" in weather or "雪" in weather:
            safety_score -= 30
            warnings.append("有降水，路面湿滑")
            recommendations.append("减速慢行，保持安全距离")
        
        # 风力分析
        wind_scale = weather_data.get("wind_scale", 0)
        if isinstance(wind_scale, str):
            try:
                wind_scale = float(wind_scale)
            except:
                wind_scale = 0
        
        if wind_scale >= 6:
            safety_score -= 25
            warnings.append("风力较大，影响骑行稳定性")
            recommendations.append("避免高速骑行，注意侧风影响")
        elif wind_scale >= 4:
            safety_score -= 10
            warnings.append("风力中等，注意侧风")
        
        # 能见度分析
        visibility = weather_data.get("visibility", 10)
        if isinstance(visibility, str):
            try:
                visibility = float(visibility)
            except:
                visibility = 10
        
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
            "safety_score": max(0, min(100, safety_score)),
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
            "safety_percentage": (safe_segments / total_segments) * 100 if total_segments > 0 else 0,
            "overall_warnings": unique_warnings,
            "recommendation": "建议调整行程" if dangerous_segments > total_segments * 0.3 else "可以正常出行"
        }

