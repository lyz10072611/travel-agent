"""
路线合并策略
综合高德和百度地图的路线，给出中肯建议
"""
from typing import Dict, List, Any, Optional
from loguru import logger


class RouteMerger:
    """路线合并器"""
    
    @staticmethod
    def merge_routes(
        amap_route: Dict[str, Any],
        baidu_route: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并两条路线，给出综合建议"""
        
        amap_distance = amap_route.get("distance", 0) / 1000  # 转换为公里
        baidu_distance = baidu_route.get("distance", 0) / 1000
        
        amap_duration = amap_route.get("duration", 0) / 60  # 转换为分钟
        baidu_duration = baidu_route.get("duration", 0) / 60
        
        # 计算差异
        distance_diff = abs(amap_distance - baidu_distance)
        duration_diff = abs(amap_duration - baidu_duration)
        
        # 选择推荐路线
        recommended_route = None
        recommendation_reason = ""
        
        # 如果距离差异小于5%，选择时间更短的
        if distance_diff / max(amap_distance, baidu_distance) < 0.05:
            if amap_duration < baidu_duration:
                recommended_route = "amap"
                recommendation_reason = "距离相近，高德路线时间更短"
            else:
                recommended_route = "baidu"
                recommendation_reason = "距离相近，百度路线时间更短"
        else:
            # 距离差异较大，选择距离更短的
            if amap_distance < baidu_distance:
                recommended_route = "amap"
                recommendation_reason = "高德路线距离更短"
            else:
                recommended_route = "baidu"
                recommendation_reason = "百度路线距离更短"
        
        merged_result = {
            "amap_route": {
                "distance_km": round(amap_distance, 2),
                "duration_min": round(amap_duration, 2),
                "steps_count": len(amap_route.get("steps", [])),
                "tolls": amap_route.get("tolls", 0),
                "traffic_lights": amap_route.get("traffic_lights", 0)
            },
            "baidu_route": {
                "distance_km": round(baidu_distance, 2),
                "duration_min": round(baidu_duration, 2),
                "steps_count": len(baidu_route.get("steps", [])),
                "tolls": baidu_route.get("tolls", 0),
                "traffic_lights": baidu_route.get("traffic_lights", 0)
            },
            "comparison": {
                "distance_diff_km": round(distance_diff, 2),
                "duration_diff_min": round(duration_diff, 2),
                "distance_diff_percent": round(
                    distance_diff / max(amap_distance, baidu_distance) * 100, 2
                )
            },
            "recommended_route": recommended_route,
            "recommendation_reason": recommendation_reason,
            "final_route": amap_route if recommended_route == "amap" else baidu_route,
            "suggestions": RouteMerger._generate_suggestions(
                amap_route, baidu_route, recommended_route
            )
        }
        
        return merged_result
    
    @staticmethod
    def _generate_suggestions(
        amap_route: Dict[str, Any],
        baidu_route: Dict[str, Any],
        recommended: str
    ) -> List[str]:
        """生成建议"""
        suggestions = []
        
        amap_distance = amap_route.get("distance", 0) / 1000
        baidu_distance = baidu_route.get("distance", 0) / 1000
        
        # 如果两条路线距离差异较大
        if abs(amap_distance - baidu_distance) > 50:
            suggestions.append(
                "两条路线距离差异较大，建议根据实际需求选择："
                f"高德路线{amap_distance:.1f}km，百度路线{baidu_distance:.1f}km"
            )
        
        # 检查是否有高速公路
        amap_has_highway = any(
            "高速" in step.get("road", "").lower() 
            for step in amap_route.get("steps", [])
        )
        baidu_has_highway = any(
            "高速" in step.get("road", "").lower() 
            for step in baidu_route.get("steps", [])
        )
        
        if amap_has_highway or baidu_has_highway:
            suggestions.append("注意：路线可能包含高速公路，摩托车通行可能受限")
        
        # 推荐路线说明
        suggestions.append(f"推荐使用{recommended}路线：{RouteMerger._get_recommendation_reason(amap_route, baidu_route, recommended)}")
        
        return suggestions
    
    @staticmethod
    def _get_recommendation_reason(
        amap_route: Dict[str, Any],
        baidu_route: Dict[str, Any],
        recommended: str
    ) -> str:
        """获取推荐理由"""
        if recommended == "amap":
            return "高德地图路线更优"
        else:
            return "百度地图路线更优"

