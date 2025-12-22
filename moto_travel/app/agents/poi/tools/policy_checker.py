"""
禁摩政策检查工具
检查城市和路段的摩托车通行政策
"""
from typing import Dict, List, Any, Optional
from loguru import logger


class PolicyChecker:
    """禁摩政策检查器"""
    
    # 禁摩城市数据库（示例数据，实际应该从数据库或API获取）
    MOTORCYCLE_RESTRICTIONS = {
        "北京": {
            "restricted": True,
            "policy": "五环内禁摩，五环外部分区域限行",
            "details": "工作日7:00-20:00五环内禁行",
            "exceptions": ["京A牌照可在五环内行驶"]
        },
        "上海": {
            "restricted": True,
            "policy": "外环内禁摩",
            "details": "外环线以内区域禁止摩托车通行",
            "exceptions": []
        },
        "广州": {
            "restricted": True,
            "policy": "部分区域限行",
            "details": "中心城区部分路段限行",
            "exceptions": []
        },
        "深圳": {
            "restricted": True,
            "policy": "全市大部分区域禁摩",
            "details": "除部分郊区外，大部分区域禁止摩托车通行",
            "exceptions": []
        }
    }
    
    @classmethod
    def check_city_policy(cls, city: str) -> Dict[str, Any]:
        """检查城市禁摩政策"""
        city_clean = city.replace("市", "").replace("省", "")
        
        # 精确匹配
        if city in cls.MOTORCYCLE_RESTRICTIONS:
            policy = cls.MOTORCYCLE_RESTRICTIONS[city]
            return {
                "city": city,
                "has_restriction": policy["restricted"],
                "policy": policy["policy"],
                "details": policy["details"],
                "exceptions": policy["exceptions"],
                "recommendation": cls._get_recommendation(policy)
            }
        
        # 模糊匹配
        for city_name, policy in cls.MOTORCYCLE_RESTRICTIONS.items():
            if city_clean in city_name or city_name in city_clean:
                return {
                    "city": city,
                    "has_restriction": policy["restricted"],
                    "policy": policy["policy"],
                    "details": policy["details"],
                    "exceptions": policy["exceptions"],
                    "recommendation": cls._get_recommendation(policy)
                }
        
        # 默认无限制
        return {
            "city": city,
            "has_restriction": False,
            "policy": "未查询到禁摩政策",
            "details": "建议查询当地交管部门确认",
            "exceptions": [],
            "recommendation": "可以正常通行，但建议提前查询当地政策"
        }
    
    @classmethod
    def check_route_policy(cls, route_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """检查路线上的禁摩政策"""
        restricted_segments = []
        warnings = []
        
        for i, segment in enumerate(route_segments):
            road = segment.get("road", "")
            # 简单提取城市名称（实际应该使用地理编码）
            cities_in_road = [city for city in cls.MOTORCYCLE_RESTRICTIONS.keys() if city in road]
            
            for city in cities_in_road:
                policy = cls.check_city_policy(city)
                if policy["has_restriction"]:
                    restricted_segments.append({
                        "segment_index": i,
                        "road": road,
                        "city": city,
                        "policy": policy
                    })
                    warnings.append(
                        f"路段{i+1}经过{city}，该城市有禁摩政策: {policy['policy']}"
                    )
        
        return {
            "has_restrictions": len(restricted_segments) > 0,
            "restricted_segments": restricted_segments,
            "warnings": warnings,
            "recommendation": cls._get_route_recommendation(restricted_segments)
        }
    
    @classmethod
    def _get_recommendation(cls, policy: Dict[str, Any]) -> str:
        """获取政策建议"""
        if not policy["restricted"]:
            return "可以正常通行"
        
        if policy["exceptions"]:
            return f"注意：{policy['policy']}，但有例外情况：{', '.join(policy['exceptions'])}"
        
        return f"警告：{policy['policy']}，建议绕行或查询详细政策"
    
    @classmethod
    def _get_route_recommendation(cls, restricted_segments: List[Dict[str, Any]]) -> str:
        """获取路线建议"""
        if not restricted_segments:
            return "路线无禁摩限制，可以正常通行"
        
        if len(restricted_segments) == 1:
            seg = restricted_segments[0]
            return f"路线经过{seg['city']}，建议查询详细政策或考虑绕行"
        
        return f"路线经过{len(restricted_segments)}个禁摩城市，强烈建议重新规划路线或查询详细政策"

