"""
美团酒店工具
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
from tools.base_tool import RateLimitedTool
from app.config import settings
from loguru import logger


class MeituanHotelTool(RateLimitedTool):
    """美团酒店工具"""
    
    def __init__(self):
        super().__init__(
            name="meituan_hotel_tool",
            description="美团酒店搜索和预订工具",
            requests_per_minute=60
        )
        self.api_key = settings.meituan_api_key
        self.base_url = settings.meituan_base_url or "https://openapi.meituan.com"
        self.app_secret = settings.meituan_app_secret
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """生成API签名"""
        if not self.app_secret:
            return ""
        sorted_params = sorted(params.items())
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_string = f"{param_string}&key={self.app_secret}"
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        return signature
    
    async def search_hotels(
        self,
        city: str,
        check_in_date: str,
        check_out_date: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        star_level: Optional[int] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        user_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """搜索酒店"""
        self.validate_params(["city", "check_in_date", "check_out_date"],
                            city=city, check_in_date=check_in_date, check_out_date=check_out_date)
        
        # 构建请求参数
        params = {
            "city": city,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "page": page,
            "page_size": page_size
        }
        
        if latitude and longitude:
            params["latitude"] = latitude
            params["longitude"] = longitude
        if price_min:
            params["price_min"] = price_min
        if price_max:
            params["price_max"] = price_max
        if star_level:
            params["star_level"] = star_level
        if keyword:
            params["keyword"] = keyword
        if user_token:
            params["token"] = user_token
        
        # 生成签名
        signature = self._generate_signature(params)
        if signature:
            params["sign"] = signature
        
        # 发送请求
        url = f"{self.base_url}/hotel/search"
        result = await self._make_request(url, params=params)
        
        if result.get("code") == "200" or result.get("status") == "1":
            hotels = result.get("data", {}).get("hotels", []) or result.get("hotels", [])
            return self.format_response({
                "source": "meituan",
                "hotels": hotels,
                "total": len(hotels),
                "page": page,
                "page_size": page_size
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"美团酒店搜索失败: {result.get('message', 'Unknown error')}"
            )
    
    async def get_hotel_details(
        self,
        hotel_id: str,
        check_in_date: str,
        check_out_date: str,
        user_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取酒店详情"""
        params = {
            "hotel_id": hotel_id,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date
        }
        if user_token:
            params["token"] = user_token
        
        signature = self._generate_signature(params)
        if signature:
            params["sign"] = signature
        
        url = f"{self.base_url}/hotel/detail"
        result = await self._make_request(url, params=params)
        
        if result.get("code") == "200" or result.get("status") == "1":
            return self.format_response({
                "source": "meituan",
                "hotel": result.get("data", {}).get("hotel") or result.get("hotel")
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"获取酒店详情失败: {result.get('message', 'Unknown error')}"
            )
    
    async def book_hotel(
        self,
        hotel_id: str,
        room_type_id: str,
        check_in_date: str,
        check_out_date: str,
        guest_name: str,
        guest_phone: str,
        num_rooms: int = 1,
        user_token: str
    ) -> Dict[str, Any]:
        """预订酒店"""
        params = {
            "hotel_id": hotel_id,
            "room_type_id": room_type_id,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "guest_name": guest_name,
            "guest_phone": guest_phone,
            "num_rooms": num_rooms,
            "token": user_token
        }
        
        signature = self._generate_signature(params)
        if signature:
            params["sign"] = signature
        
        url = f"{self.base_url}/hotel/book"
        result = await self._make_request(url, params=params, method="POST")
        
        if result.get("code") == "200" or result.get("status") == "1":
            return self.format_response({
                "source": "meituan",
                "order_id": result.get("data", {}).get("order_id") or result.get("order_id"),
                "order": result.get("data", {}).get("order") or result.get("order")
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"酒店预订失败: {result.get('message', 'Unknown error')}"
            )
    
    async def cancel_booking(
        self,
        order_id: str,
        user_token: str
    ) -> Dict[str, Any]:
        """取消预订"""
        params = {
            "order_id": order_id,
            "token": user_token
        }
        
        signature = self._generate_signature(params)
        if signature:
            params["sign"] = signature
        
        url = f"{self.base_url}/hotel/cancel"
        result = await self._make_request(url, params=params, method="POST")
        
        if result.get("code") == "200" or result.get("status") == "1":
            return self.format_response({
                "source": "meituan",
                "success": True,
                "message": "取消成功"
            })
        else:
            return self.format_response(
                None,
                success=False,
                message=f"取消预订失败: {result.get('message', 'Unknown error')}"
            )

