"""
POI分析器
"""
from typing import Dict, List, Any


class POIAnalyzer:
    """POI分析器"""
    
    @staticmethod
    def filter_pois_by_rating(pois: List[Dict[str, Any]], min_rating: float = 3.5) -> List[Dict[str, Any]]:
        """按评分过滤POI"""
        return [poi for poi in pois if poi.get("rating", 0) >= min_rating]
    
    @staticmethod
    def filter_pois_by_distance(pois: List[Dict[str, Any]], max_distance: int = 5000) -> List[Dict[str, Any]]:
        """按距离过滤POI"""
        return [poi for poi in pois if poi.get("distance", 0) <= max_distance]
    
    @staticmethod
    def sort_pois_by_priority(pois: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按优先级排序POI"""
        return sorted(pois, key=lambda x: (
            x.get("distance", 999999),
            -x.get("rating", 0)
        ))
    
    @staticmethod
    def recommend_gas_stations_for_route(
        route_distance_km: float,
        fuel_range_km: int = 300
    ) -> Dict[str, Any]:
        """为路线推荐加油站位置"""
        recommendations = []
        current_distance = 0
        target_distance = fuel_range_km
        
        while current_distance < route_distance_km:
            recommendations.append({
                "recommended_distance_km": target_distance,
                "message": f"建议在{target_distance}km处寻找加油站"
            })
            target_distance += fuel_range_km
            current_distance = target_distance
        
        return {
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
            "fuel_range_km": fuel_range_km
        }

