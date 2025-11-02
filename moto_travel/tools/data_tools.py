"""
数据处理工具
提供数据清洗、转换、地理计算等功能
"""
from typing import Dict, List, Any, Optional, Tuple, Union
import json
import re
from datetime import datetime, timedelta
from geopy.distance import geodesic
from geopy.point import Point
import pandas as pd
from tools.base_tool import BaseTool


class DataProcessor(BaseTool):
    """数据处理器"""
    
    def __init__(self):
        super().__init__(
            name="data_processor",
            description="数据处理工具，提供数据清洗和转换功能"
        )
    
    async def clean_poi_data(self, poi_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """清洗POI数据"""
        
        cleaned_pois = []
        duplicates_removed = 0
        
        # 用于去重的集合
        seen_names = set()
        
        for poi in poi_data:
            # 基本数据验证
            if not poi.get("name") or not poi.get("longitude") or not poi.get("latitude"):
                continue
            
            # 去重检查
            poi_name = poi["name"].strip().lower()
            if poi_name in seen_names:
                duplicates_removed += 1
                continue
            
            seen_names.add(poi_name)
            
            # 数据清洗
            cleaned_poi = {
                "id": poi.get("id", ""),
                "name": poi["name"].strip(),
                "category": poi.get("category", ""),
                "longitude": float(poi["longitude"]),
                "latitude": float(poi["latitude"]),
                "address": poi.get("address", "").strip(),
                "tel": self._clean_phone_number(poi.get("tel", "")),
                "rating": self._clean_rating(poi.get("rating", 0)),
                "price": poi.get("price", "").strip(),
                "distance": float(poi.get("distance", 0)),
                "business_hours": self._clean_business_hours(poi.get("opening_hours", "")),
                "website": self._clean_url(poi.get("website", "")),
                "photos": poi.get("photos", [])
            }
            
            cleaned_pois.append(cleaned_poi)
        
        # 按距离排序
        cleaned_pois.sort(key=lambda x: x["distance"])
        
        return self.format_response({
            "cleaned_pois": cleaned_pois,
            "original_count": len(poi_data),
            "cleaned_count": len(cleaned_pois),
            "duplicates_removed": duplicates_removed,
            "removal_rate": (duplicates_removed / len(poi_data)) * 100 if poi_data else 0
        })
    
    async def process_weather_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理天气数据"""
        
        processed_data = {
            "location": weather_data.get("location", ""),
            "current": {},
            "hourly": [],
            "daily": [],
            "alerts": []
        }
        
        # 处理当前天气
        current = weather_data.get("current", {})
        if current:
            processed_data["current"] = {
                "temperature": self._safe_float(current.get("temperature")),
                "feels_like": self._safe_float(current.get("feels_like")),
                "weather": current.get("weather", ""),
                "humidity": self._safe_float(current.get("humidity")),
                "wind_speed": self._safe_float(current.get("wind_speed")),
                "wind_direction": current.get("wind_direction", ""),
                "visibility": self._safe_float(current.get("visibility")),
                "pressure": self._safe_float(current.get("pressure")),
                "update_time": current.get("update_time", "")
            }
        
        # 处理逐小时天气
        hourly_data = weather_data.get("hourly_weather", [])
        for hour in hourly_data:
            processed_hour = {
                "time": hour.get("time", ""),
                "temperature": self._safe_float(hour.get("temperature")),
                "weather": hour.get("weather", ""),
                "humidity": self._safe_float(hour.get("humidity")),
                "wind_speed": self._safe_float(hour.get("wind_speed")),
                "precipitation": self._safe_float(hour.get("precipitation")),
                "pop": self._safe_float(hour.get("pop"))
            }
            processed_data["hourly"].append(processed_hour)
        
        # 处理逐日天气
        daily_data = weather_data.get("daily_weather", [])
        for day in daily_data:
            processed_day = {
                "date": day.get("date", ""),
                "weather_day": day.get("weather_day", ""),
                "weather_night": day.get("weather_night", ""),
                "temp_max": self._safe_float(day.get("temp_max")),
                "temp_min": self._safe_float(day.get("temp_min")),
                "humidity": self._safe_float(day.get("humidity")),
                "wind_speed": self._safe_float(day.get("wind_speed")),
                "precipitation": self._safe_float(day.get("precipitation")),
                "pop": self._safe_float(day.get("pop")),
                "uv_index": self._safe_float(day.get("uv_index"))
            }
            processed_data["daily"].append(processed_day)
        
        # 处理预警信息
        alerts = weather_data.get("warnings", [])
        for alert in alerts:
            processed_alert = {
                "title": alert.get("title", ""),
                "level": alert.get("level", ""),
                "type": alert.get("type", ""),
                "text": alert.get("text", ""),
                "pub_time": alert.get("pub_time", ""),
                "start_time": alert.get("start_time", ""),
                "end_time": alert.get("end_time", "")
            }
            processed_data["alerts"].append(processed_alert)
        
        return self.format_response(processed_data)
    
    async def process_route_data(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理路线数据"""
        
        processed_route = {
            "distance": route_data.get("distance", 0),
            "duration": route_data.get("duration", 0),
            "steps": [],
            "summary": {}
        }
        
        # 处理路线步骤
        steps = route_data.get("steps", [])
        for step in steps:
            processed_step = {
                "instruction": step.get("instruction", ""),
                "road": step.get("road", ""),
                "distance": step.get("distance", 0),
                "duration": step.get("duration", 0),
                "action": step.get("action", ""),
                "polyline": step.get("polyline", "")
            }
            processed_route["steps"].append(processed_step)
        
        # 生成路线摘要
        processed_route["summary"] = {
            "total_distance_km": round(route_data.get("distance", 0) / 1000, 2),
            "total_duration_hours": round(route_data.get("duration", 0) / 3600, 2),
            "average_speed_kmh": self._calculate_average_speed(
                route_data.get("distance", 0),
                route_data.get("duration", 0)
            ),
            "tolls": route_data.get("tolls", 0),
            "traffic_lights": route_data.get("traffic_lights", 0)
        }
        
        return self.format_response(processed_route)
    
    def _clean_phone_number(self, phone: str) -> str:
        """清洗电话号码"""
        if not phone:
            return ""
        
        # 移除所有非数字字符
        cleaned = re.sub(r'[^\d]', '', phone)
        
        # 验证电话号码格式
        if len(cleaned) >= 7 and len(cleaned) <= 15:
            return cleaned
        
        return ""
    
    def _clean_rating(self, rating: Union[str, int, float]) -> float:
        """清洗评分数据"""
        if isinstance(rating, (int, float)):
            return float(rating)
        elif isinstance(rating, str):
            # 提取数字
            numbers = re.findall(r'\d+\.?\d*', rating)
            if numbers:
                return float(numbers[0])
        
        return 0.0
    
    def _clean_business_hours(self, hours: str) -> str:
        """清洗营业时间"""
        if not hours:
            return ""
        
        # 标准化营业时间格式
        hours = hours.strip()
        
        # 常见的营业时间模式
        patterns = [
            r'(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})',
            r'(\d{1,2})点-(\d{1,2})点',
            r'(\d{1,2}):(\d{2})~(\d{1,2}):(\d{2})'
        ]
        
        for pattern in patterns:
            if re.search(pattern, hours):
                return hours
        
        return hours
    
    def _clean_url(self, url: str) -> str:
        """清洗URL"""
        if not url:
            return ""
        
        url = url.strip()
        
        # 添加协议前缀
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    def _safe_float(self, value: Any) -> float:
        """安全转换为浮点数"""
        if value is None:
            return 0.0
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _calculate_average_speed(self, distance: int, duration: int) -> float:
        """计算平均速度"""
        if duration <= 0:
            return 0.0
        
        # 距离单位转换为公里，时间单位转换为小时
        distance_km = distance / 1000
        duration_hours = duration / 3600
        
        return round(distance_km / duration_hours, 2)


class GeoUtils(BaseTool):
    """地理工具"""
    
    def __init__(self):
        super().__init__(
            name="geo_utils",
            description="地理计算工具，提供距离、面积等计算功能"
        )
    
    async def calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> Dict[str, Any]:
        """计算两点间距离"""
        
        try:
            distance_km = geodesic(point1, point2).kilometers
            distance_m = geodesic(point1, point2).meters
            
            return self.format_response({
                "point1": point1,
                "point2": point2,
                "distance_km": round(distance_km, 2),
                "distance_m": round(distance_m, 2)
            })
            
        except Exception as e:
            return self.format_response(
                None,
                success=False,
                message=f"距离计算失败: {str(e)}"
            )
    
    async def find_nearby_points(
        self,
        center_point: Tuple[float, float],
        points: List[Dict[str, Any]],
        radius_km: float = 10.0
    ) -> Dict[str, Any]:
        """查找附近的点"""
        
        nearby_points = []
        
        for point in points:
            if "longitude" in point and "latitude" in point:
                point_coords = (point["latitude"], point["longitude"])
                distance = geodesic(center_point, point_coords).kilometers
                
                if distance <= radius_km:
                    point_copy = point.copy()
                    point_copy["distance_km"] = round(distance, 2)
                    nearby_points.append(point_copy)
        
        # 按距离排序
        nearby_points.sort(key=lambda x: x["distance_km"])
        
        return self.format_response({
            "center_point": center_point,
            "radius_km": radius_km,
            "nearby_points": nearby_points,
            "count": len(nearby_points)
        })
    
    async def calculate_route_distance(
        self,
        route_points: List[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """计算路线总距离"""
        
        if len(route_points) < 2:
            return self.format_response(
                None,
                success=False,
                message="路线点数量不足"
            )
        
        total_distance = 0.0
        segment_distances = []
        
        for i in range(len(route_points) - 1):
            segment_distance = geodesic(route_points[i], route_points[i + 1]).kilometers
            total_distance += segment_distance
            segment_distances.append({
                "from": route_points[i],
                "to": route_points[i + 1],
                "distance_km": round(segment_distance, 2)
            })
        
        return self.format_response({
            "total_distance_km": round(total_distance, 2),
            "segment_count": len(segment_distances),
            "segment_distances": segment_distances,
            "average_segment_distance": round(total_distance / len(segment_distances), 2)
        })
    
    async def is_point_in_polygon(
        self,
        point: Tuple[float, float],
        polygon: List[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """判断点是否在多边形内"""
        
        try:
            # 使用射线投射算法
            x, y = point
            n = len(polygon)
            inside = False
            
            p1x, p1y = polygon[0]
            for i in range(1, n + 1):
                p2x, p2y = polygon[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            
            return self.format_response({
                "point": point,
                "polygon": polygon,
                "inside": inside
            })
            
        except Exception as e:
            return self.format_response(
                None,
                success=False,
                message=f"点在多边形判断失败: {str(e)}"
            )
    
    async def get_bounding_box(
        self,
        points: List[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """获取点的边界框"""
        
        if not points:
            return self.format_response(
                None,
                success=False,
                message="点列表为空"
            )
        
        lats = [point[0] for point in points]
        lons = [point[1] for point in points]
        
        bounding_box = {
            "north": max(lats),
            "south": min(lats),
            "east": max(lons),
            "west": min(lons),
            "center": (
                (max(lats) + min(lats)) / 2,
                (max(lons) + min(lons)) / 2
            )
        }
        
        return self.format_response({
            "points": points,
            "bounding_box": bounding_box,
            "point_count": len(points)
        })
