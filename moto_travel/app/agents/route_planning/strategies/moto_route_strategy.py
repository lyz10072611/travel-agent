"""
摩旅路线策略
考虑禁摩、国道、加油站等摩旅特殊需求
支持用户偏好配置和时间感知
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from .route_preferences import RoutePreferences


class MotoRouteStrategy:
    """摩旅路线策略"""
    
    @staticmethod
    def analyze_route_for_moto(
        route_data: Dict[str, Any],
        preferences: Optional[RoutePreferences] = None
    ) -> Dict[str, Any]:
        """分析路线是否适合摩托车（支持用户偏好）"""
        if preferences is None:
            preferences = RoutePreferences()
        
        analysis = {
            "suitable_for_moto": True,
            "highway_segments": [],
            "national_road_segments": [],
            "provincial_road_segments": [],
            "city_road_segments": [],
            "night_segments": [],  # 晚上时段的路段
            "warnings": [],
            "recommendations": [],
            "preferences_applied": preferences.to_dict()
        }
        
        steps = route_data.get("steps", [])
        departure_time = preferences.departure_time or datetime.now()
        
        # 计算每个路段的预计时间
        current_time = departure_time
        total_duration = 0
        
        for i, step in enumerate(steps):
            road = step.get("road", "").lower()
            instruction = step.get("instruction", "").lower()
            step_duration = step.get("duration", 0)  # 秒
            step_distance = step.get("distance", 0)  # 米
            
            # 计算路段结束时间
            from datetime import timedelta
            segment_end_time = current_time + timedelta(seconds=step_duration)
            
            # 检测高速公路
            is_highway = any(keyword in road or keyword in instruction for keyword in ["高速", "expressway", "highway"])
            if is_highway:
                highway_seg = {
                    "index": i,
                    "road": step.get("road", ""),
                    "distance": step_distance,
                    "duration": step_duration,
                    "start_time": current_time.isoformat(),
                    "end_time": segment_end_time.isoformat()
                }
                
                # 根据偏好添加警告（灵活处理，不是强制）
                if preferences.highway_preference.value == "forbid":
                    highway_seg["warning"] = "禁止走高速，但路线包含高速公路"
                    analysis["warnings"].append(f"路段{i+1}包含高速公路: {step.get('road', '')}（与您的偏好冲突）")
                    analysis["suitable_for_moto"] = False
                elif preferences.highway_preference.value == "avoid":
                    highway_seg["warning"] = "尽量避开高速，但路线包含高速公路"
                    analysis["warnings"].append(f"路段{i+1}包含高速公路: {step.get('road', '')}（建议避开，但非强制）")
                elif preferences.highway_preference.value == "prefer":
                    highway_seg["info"] = "路线包含高速公路（符合您的偏好）"
                else:  # ALLOW
                    highway_seg["info"] = "路线包含高速公路（允许走高速）"
                
                analysis["highway_segments"].append(highway_seg)
            
            # 检测国道
            is_national_road = "国道" in road or ("g" in road.lower() and "高速" not in road)
            if is_national_road:
                national_road_seg = {
                    "index": i,
                    "road": step.get("road", ""),
                    "distance": step_distance,
                    "duration": step_duration,
                    "start_time": current_time.isoformat(),
                    "end_time": segment_end_time.isoformat()
                }
                
                # 检查是否为晚上时段（晚上尽量远离国道）
                is_night = preferences.is_night_time(current_time) or preferences.is_night_time(segment_end_time)
                if is_night:
                    national_road_seg["is_night"] = True
                    national_road_seg["night_time"] = current_time.strftime("%H:%M")
                    analysis["night_segments"].append(national_road_seg)
                    
                    # 如果开启了晚上避开国道选项
                    if preferences.should_avoid_national_road(current_time):
                        national_road_seg["warning"] = "晚上时段经过国道（建议避开，提高安全性）"
                        national_road_seg["severity"] = "high"  # 高优先级警告
                        analysis["warnings"].append(
                            f"⚠️ 路段{i+1}在晚上时段（{current_time.strftime('%H:%M')}）经过国道: {step.get('road', '')}（建议避开）"
                        )
                    else:
                        national_road_seg["info"] = "晚上时段经过国道（已关闭避开选项）"
                
                analysis["national_road_segments"].append(national_road_seg)
            
            # 检测省道
            is_provincial_road = "省道" in road or ("s" in road.lower() and "高速" not in road)
            if is_provincial_road:
                analysis["provincial_road_segments"].append({
                    "index": i,
                    "road": step.get("road", ""),
                    "distance": step_distance,
                    "duration": step_duration
                })
            
            # 更新当前时间
            current_time = segment_end_time
            total_duration += step_duration
        
        # 评估适合度（基于偏好，灵活处理）
        highway_ratio = len(analysis["highway_segments"]) / len(steps) if steps else 0
        
        # 高速公路评估（不是强制，根据用户偏好）
        if preferences.highway_preference.value == "forbid" and highway_ratio > 0:
            analysis["suitable_for_moto"] = False
            analysis["recommendations"].append("⚠️ 路线包含高速公路，但您设置了禁止走高速，建议重新规划")
        elif preferences.highway_preference.value == "avoid" and highway_ratio > 0.3:
            analysis["recommendations"].append("💡 路线包含较多高速公路（{:.1%}），建议选择不走高速策略，但非强制".format(highway_ratio))
        elif preferences.highway_preference.value == "allow" and highway_ratio > 0:
            analysis["recommendations"].append("✅ 路线包含高速公路，符合您的偏好（允许走高速）")
        
        # 晚上国道警告（高优先级）
        night_national_count = len([s for s in analysis["night_segments"] if s.get("warning")])
        if night_national_count > 0:
            analysis["recommendations"].append(
                f"⚠️ 路线在晚上时段经过{night_national_count}个国道路段，建议调整出发时间或选择其他路线（提高安全性）"
            )
        elif len(analysis["night_segments"]) > 0:
            analysis["recommendations"].append(
                f"💡 路线在晚上时段经过{len(analysis['night_segments'])}个国道路段（已关闭避开选项）"
            )
        
        # 正面评价
        if len(analysis["national_road_segments"]) + len(analysis["provincial_road_segments"]) > len(steps) * 0.5:
            analysis["recommendations"].append("路线主要经过国道省道，适合摩托车行驶")
        
        return analysis
    
    @staticmethod
    def plan_gas_stations(
        route_data: Dict[str, Any],
        fuel_range: int = 300  # 摩托车续航里程（km）
    ) -> List[Dict[str, Any]]:
        """规划加油站位置"""
        total_distance = route_data.get("distance", 0) / 1000  # 转换为公里
        steps = route_data.get("steps", [])
        
        gas_stations = []
        current_distance = 0
        
        # 每fuel_range公里规划一个加油站
        target_distance = fuel_range
        
        for i, step in enumerate(steps):
            step_distance = step.get("distance", 0) / 1000  # 转换为公里
            current_distance += step_distance
            
            if current_distance >= target_distance:
                gas_stations.append({
                    "segment_index": i,
                    "distance_from_start": current_distance,
                    "location": step.get("road", ""),
                    "recommended": True,
                    "message": f"建议在{step.get('road', '')}附近加油"
                })
                target_distance += fuel_range
        
        return gas_stations
    
    @staticmethod
    def check_moto_restrictions(
        route_data: Dict[str, Any],
        city_policies: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """检查禁摩限制"""
        restrictions = {
            "has_restrictions": False,
            "restricted_segments": [],
            "warnings": []
        }
        
        if not city_policies:
            return restrictions
        
        steps = route_data.get("steps", [])
        
        for i, step in enumerate(steps):
            road = step.get("road", "")
            # 这里可以根据实际政策数据检查
            # 示例：检查是否在城市禁摩区域
            for city, policy in city_policies.items():
                if city in road and "禁摩" in policy:
                    restrictions["has_restrictions"] = True
                    restrictions["restricted_segments"].append({
                        "index": i,
                        "road": road,
                        "city": city,
                        "policy": policy
                    })
                    restrictions["warnings"].append(
                        f"路段{i+1}经过{city}，该城市有禁摩政策: {policy}"
                    )
        
        return restrictions

