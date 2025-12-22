"""
酒店筛选器
提供多维度筛选功能
"""
from typing import Dict, List, Any, Optional


class HotelFilter:
    """酒店筛选器"""
    
    @staticmethod
    def filter_hotels(
        hotels: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """综合筛选"""
        filtered = hotels
        
        # 价格筛选
        if "price_min" in filters or "price_max" in filters:
            filtered = HotelFilter.filter_by_price(
                filtered,
                price_min=filters.get("price_min"),
                price_max=filters.get("price_max")
            )
        
        # 评分筛选
        if "rating_min" in filters:
            filtered = HotelFilter.filter_by_rating(
                filtered,
                min_rating=filters.get("rating_min")
            )
        
        # 房型筛选
        if "room_type" in filters:
            filtered = HotelFilter.filter_by_room_type(
                filtered,
                room_type=filters.get("room_type")
            )
        
        # 位置筛选
        if "max_distance" in filters:
            filtered = HotelFilter.filter_by_distance(
                filtered,
                max_distance=filters.get("max_distance")
            )
        
        # 设施筛选
        if "facilities" in filters:
            filtered = HotelFilter.filter_by_facilities(
                filtered,
                facilities=filters.get("facilities")
            )
        
        return filtered
    
    @staticmethod
    def filter_by_price(
        hotels: List[Dict[str, Any]],
        price_min: Optional[int] = None,
        price_max: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """按价格筛选"""
        filtered = []
        for hotel in hotels:
            price = hotel.get("price", 0)
            if price_min and price < price_min:
                continue
            if price_max and price > price_max:
                continue
            filtered.append(hotel)
        return filtered
    
    @staticmethod
    def filter_by_rating(
        hotels: List[Dict[str, Any]],
        min_rating: float = 3.5
    ) -> List[Dict[str, Any]]:
        """按评分筛选"""
        return [h for h in hotels if h.get("rating", 0) >= min_rating]
    
    @staticmethod
    def filter_by_room_type(
        hotels: List[Dict[str, Any]],
        room_type: str
    ) -> List[Dict[str, Any]]:
        """按房型筛选"""
        # 这里需要根据实际的房型数据结构来实现
        # 暂时返回所有酒店
        return hotels
    
    @staticmethod
    def filter_by_distance(
        hotels: List[Dict[str, Any]],
        max_distance: float
    ) -> List[Dict[str, Any]]:
        """按距离筛选"""
        return [h for h in hotels if h.get("distance", 999999) <= max_distance]
    
    @staticmethod
    def filter_by_facilities(
        hotels: List[Dict[str, Any]],
        facilities: List[str]
    ) -> List[Dict[str, Any]]:
        """按设施筛选"""
        filtered = []
        for hotel in hotels:
            hotel_facilities = hotel.get("facilities", [])
            if all(f in hotel_facilities for f in facilities):
                filtered.append(hotel)
        return filtered
    
    @staticmethod
    def merge_results_from_multiple_sources(
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并多个数据源的结果"""
        all_hotels = []
        seen_ids = set()
        
        for result in results:
            if not result.get("success"):
                continue
            
            hotels = result.get("data", {}).get("hotels", [])
            source = result.get("data", {}).get("source", "unknown")
            
            for hotel in hotels:
                # 使用酒店名称+地址作为唯一标识
                hotel_key = f"{hotel.get('name', '')}_{hotel.get('address', '')}"
                
                if hotel_key not in seen_ids:
                    hotel["source"] = source
                    all_hotels.append(hotel)
                    seen_ids.add(hotel_key)
        
        # 按评分和价格排序
        all_hotels.sort(
            key=lambda x: (
                -x.get("rating", 0),
                x.get("price", 999999)
            )
        )
        
        return all_hotels

