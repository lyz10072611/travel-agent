"""
酒店分析器
分析酒店数据，提供推荐和筛选
"""
from typing import Dict, List, Any, Optional


class HotelAnalyzer:
    """酒店分析器"""
    
    @staticmethod
    def analyze_hotels_for_moto_travel(
        hotels: List[Dict[str, Any]],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """分析酒店是否适合摩旅"""
        preferences = preferences or {}
        
        analyzed_hotels = []
        for hotel in hotels:
            score = 100
            reasons = []
            
            # 检查停车位
            if hotel.get("parking_available"):
                score += 20
                reasons.append("有停车位")
            else:
                score -= 30
                reasons.append("无停车位")
            
            # 检查位置（靠近主要路线）
            distance = hotel.get("distance", 999999)
            if distance < 5:
                score += 15
                reasons.append("位置便利")
            elif distance > 20:
                score -= 10
                reasons.append("位置较远")
            
            # 检查价格
            price = hotel.get("price", 0)
            budget_max = preferences.get("budget_max", 500)
            if price <= budget_max:
                score += 10
                reasons.append("价格合适")
            else:
                score -= 20
                reasons.append("超出预算")
            
            # 检查评分
            rating = hotel.get("rating", 0)
            if rating >= 4.5:
                score += 15
                reasons.append("评分优秀")
            elif rating < 3.5:
                score -= 15
                reasons.append("评分较低")
            
            # 检查设施
            facilities = hotel.get("facilities", [])
            if "wifi" in facilities or "WiFi" in facilities:
                score += 5
            if "restaurant" in facilities or "餐厅" in facilities:
                score += 5
            
            analyzed_hotels.append({
                **hotel,
                "moto_score": max(0, min(100, score)),
                "reasons": reasons,
                "suitable_for_moto": score >= 60
            })
        
        # 按摩旅适合度排序
        analyzed_hotels.sort(key=lambda x: x["moto_score"], reverse=True)
        
        return {
            "hotels": analyzed_hotels,
            "total": len(analyzed_hotels),
            "suitable_count": sum(1 for h in analyzed_hotels if h["suitable_for_moto"])
        }
    
    @staticmethod
    def recommend_hotels(
        hotels: List[Dict[str, Any]],
        preferences: Optional[Dict[str, Any]] = None,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """推荐酒店"""
        preferences = preferences or {}
        
        # 分析酒店
        analyzed = HotelAnalyzer.analyze_hotels_for_moto_travel(hotels, preferences)
        
        # 返回前N个
        return analyzed["hotels"][:top_n]
    
    @staticmethod
    def filter_by_room_type(
        hotels: List[Dict[str, Any]],
        room_type: str
    ) -> List[Dict[str, Any]]:
        """按房型筛选"""
        room_type_map = {
            "双床": ["twin", "double", "双床"],
            "大床": ["king", "queen", "大床"],
            "单人床": ["single", "单人"],
            "青旅": ["hostel", "青旅"],
            "连锁": ["chain", "连锁"],
            "民宿": ["homestay", "民宿", "客栈"]
        }
        
        keywords = room_type_map.get(room_type, [room_type])
        
        filtered = []
        for hotel in hotels:
            name = hotel.get("name", "").lower()
            description = hotel.get("description", "").lower()
            
            for keyword in keywords:
                if keyword.lower() in name or keyword.lower() in description:
                    filtered.append(hotel)
                    break
        
        return filtered

