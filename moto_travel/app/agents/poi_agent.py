"""
POI服务Agent
处理餐饮、住宿、修车、加油站等本地服务
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.agents.base_agent import AsyncAgent, AgentResponse, AgentType
from tools.poi_tools import POITool, POIAnalyzer, POICategory
from tools.cache_tools import RedisCache
from loguru import logger


class POIAgent(AsyncAgent):
    """POI服务Agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.POI,
            name="poi_agent",
            description="POI服务Agent，提供餐饮、住宿、修车、加油站等本地服务查询"
        )
        self.poi_tool = POITool()
        self.poi_analyzer = POIAnalyzer()
        self.cache = RedisCache()
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行POI查询"""
        query = kwargs.get("query", "")
        location = kwargs.get("location", "")
        poi_type = kwargs.get("poi_type", "")
        radius = kwargs.get("radius", 5000)
        user_id = kwargs.get("user_id")
        
        try:
            # 如果没有提供地点，尝试从查询中提取
            if not location:
                location = await self._extract_location_from_query(query)
            
            if not location:
                return self._create_error_response("请提供查询地点")
            
            # 如果没有提供POI类型，尝试从查询中识别
            if not poi_type:
                poi_type = await self._identify_poi_type_from_query(query)
            
            # 执行POI查询
            poi_result = await self._search_pois(location, poi_type, radius)
            
            if not poi_result["success"]:
                return self._create_error_response(poi_result["message"])
            
            # 分析和推荐
            analysis_result = await self._analyze_pois(poi_result["data"], location)
            
            # 缓存结果
            await self.cache.cache_poi_data(location, poi_type, poi_result["data"])
            
            # 构建完整结果
            result = {
                "location": location,
                "poi_type": poi_type,
                "pois": poi_result["data"],
                "analysis": analysis_result,
                "recommendations": await self._generate_poi_recommendations(
                    poi_result["data"], analysis_result
                )
            }
            
            return self._create_success_response(
                data=result,
                message="POI查询完成",
                metadata={
                    "location": location,
                    "poi_type": poi_type,
                    "radius": radius,
                    "user_id": user_id
                }
            )
            
        except Exception as e:
            logger.error(f"POI query failed: {str(e)}")
            return self._create_error_response(f"POI查询失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        # 至少需要查询或地点
        has_query = bool(kwargs.get("query", ""))
        has_location = bool(kwargs.get("location", ""))
        
        return has_query or has_location
    
    async def _extract_location_from_query(self, query: str) -> str:
        """从查询中提取地点信息"""
        import re
        
        # 匹配地点模式
        location_patterns = [
            r"(.+?)的(.+?)",
            r"(.+?)附近(.+?)",
            r"(.+?)有什么(.+?)",
            r"(.+?)推荐(.+?)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query)
            if match:
                location = match.group(1).strip()
                # 过滤掉一些无关词汇
                if location not in ["这里", "附近", "周围"]:
                    return location
        
        return ""
    
    async def _identify_poi_type_from_query(self, query: str) -> str:
        """从查询中识别POI类型"""
        query_lower = query.lower()
        
        # POI类型关键词映射
        poi_keywords = {
            "restaurant": ["餐厅", "饭店", "餐馆", "美食", "吃饭", "小吃", "火锅", "烧烤"],
            "hotel": ["酒店", "宾馆", "民宿", "住宿", "旅馆", "客栈"],
            "gas_station": ["加油站", "加油", "中石化", "中石油", "壳牌"],
            "repair_shop": ["修车", "汽修", "维修", "保养", "修车行"],
            "motorcycle_shop": ["摩托车", "机车", "摩配", "头盔", "骑行装备"],
            "medical": ["医院", "诊所", "药店", "医疗", "急救"],
            "scenic_spot": ["景点", "景区", "旅游", "风景", "名胜", "公园"],
            "bank": ["银行", "ATM", "取款", "存款"]
        }
        
        for poi_type, keywords in poi_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return poi_type
        
        return "all"  # 默认查询所有类型
    
    async def _search_pois(self, location: str, poi_type: str, radius: int) -> Dict[str, Any]:
        """搜索POI"""
        
        async with self.poi_tool:
            if poi_type == "all":
                # 搜索所有类型的POI
                all_pois = {}
                
                for category in POICategory:
                    try:
                        if category == POICategory.RESTAURANT:
                            result = await self.poi_tool.search_restaurants(location, radius)
                        elif category == POICategory.HOTEL:
                            result = await self.poi_tool.search_hotels(location, radius)
                        elif category == POICategory.GAS_STATION:
                            result = await self.poi_tool.search_gas_stations(location, radius)
                        elif category == POICategory.REPAIR_SHOP:
                            result = await self.poi_tool.search_repair_shops(location, radius)
                        elif category == POICategory.MOTORCYCLE_SHOP:
                            result = await self.poi_tool.search_motorcycle_shops(location, radius)
                        elif category == POICategory.MEDICAL:
                            result = await self.poi_tool.search_medical_facilities(location, radius)
                        elif category == POICategory.SCENIC_SPOT:
                            result = await self.poi_tool.search_scenic_spots(location, radius)
                        else:
                            continue
                        
                        if result["success"]:
                            all_pois[category.value] = result["data"]
                            
                    except Exception as e:
                        logger.warning(f"Failed to search {category.value}: {str(e)}")
                        continue
                
                return {"success": True, "data": all_pois}
            
            else:
                # 搜索特定类型的POI
                if poi_type == "restaurant":
                    result = await self.poi_tool.search_restaurants(location, radius)
                elif poi_type == "hotel":
                    result = await self.poi_tool.search_hotels(location, radius)
                elif poi_type == "gas_station":
                    result = await self.poi_tool.search_gas_stations(location, radius)
                elif poi_type == "repair_shop":
                    result = await self.poi_tool.search_repair_shops(location, radius)
                elif poi_type == "motorcycle_shop":
                    result = await self.poi_tool.search_motorcycle_shops(location, radius)
                elif poi_type == "medical":
                    result = await self.poi_tool.search_medical_facilities(location, radius)
                elif poi_type == "scenic_spot":
                    result = await self.poi_tool.search_scenic_spots(location, radius)
                else:
                    return {"success": False, "message": f"不支持的POI类型: {poi_type}"}
                
                return result
    
    async def _analyze_pois(self, pois_data: Dict[str, Any], location: str) -> Dict[str, Any]:
        """分析POI数据"""
        
        analysis = {
            "summary": {},
            "quality_analysis": {},
            "coverage_analysis": {},
            "recommendations": {}
        }
        
        if isinstance(pois_data, dict):
            # 多类型POI分析
            for poi_type, pois in pois_data.items():
                if isinstance(pois, dict) and "pois" in pois:
                    poi_list = pois["pois"]
                    
                    # 基本统计
                    analysis["summary"][poi_type] = {
                        "count": len(poi_list),
                        "average_rating": self._calculate_average_rating(poi_list),
                        "price_range": self._analyze_price_range(poi_list)
                    }
                    
                    # 质量分析
                    analysis["quality_analysis"][poi_type] = {
                        "high_quality_count": len([p for p in poi_list if p.get("rating", 0) >= 4.0]),
                        "medium_quality_count": len([p for p in poi_list if 3.0 <= p.get("rating", 0) < 4.0]),
                        "low_quality_count": len([p for p in poi_list if p.get("rating", 0) < 3.0])
                    }
                    
                    # 覆盖分析
                    analysis["coverage_analysis"][poi_type] = {
                        "within_1km": len([p for p in poi_list if p.get("distance", 0) <= 1000]),
                        "within_3km": len([p for p in poi_list if p.get("distance", 0) <= 3000]),
                        "within_5km": len([p for p in poi_list if p.get("distance", 0) <= 5000])
                    }
        
        return analysis
    
    def _calculate_average_rating(self, pois: List[Dict[str, Any]]) -> float:
        """计算平均评分"""
        ratings = [poi.get("rating", 0) for poi in pois if poi.get("rating", 0) > 0]
        return sum(ratings) / len(ratings) if ratings else 0.0
    
    def _analyze_price_range(self, pois: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析价格范围"""
        prices = []
        for poi in pois:
            price_str = poi.get("price", "")
            if price_str:
                # 简单的价格提取逻辑
                import re
                price_numbers = re.findall(r'\d+', price_str)
                if price_numbers:
                    prices.extend([int(p) for p in price_numbers])
        
        if prices:
            return {
                "min": min(prices),
                "max": max(prices),
                "average": sum(prices) / len(prices)
            }
        return {"min": 0, "max": 0, "average": 0}
    
    async def _generate_poi_recommendations(
        self, 
        pois_data: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成POI推荐"""
        
        recommendations = {
            "top_recommendations": {},
            "budget_options": {},
            "convenience_options": {},
            "quality_options": {}
        }
        
        if isinstance(pois_data, dict):
            for poi_type, pois in pois_data.items():
                if isinstance(pois, dict) and "pois" in pois:
                    poi_list = pois["pois"]
                    
                    if not poi_list:
                        continue
                    
                    # 按评分排序
                    sorted_by_rating = sorted(poi_list, key=lambda x: x.get("rating", 0), reverse=True)
                    recommendations["top_recommendations"][poi_type] = sorted_by_rating[:3]
                    
                    # 按距离排序
                    sorted_by_distance = sorted(poi_list, key=lambda x: x.get("distance", 999999))
                    recommendations["convenience_options"][poi_type] = sorted_by_distance[:3]
                    
                    # 按价格排序（如果有价格信息）
                    poi_with_price = [p for p in poi_list if p.get("price")]
                    if poi_with_price:
                        sorted_by_price = sorted(poi_with_price, key=lambda x: len(x.get("price", "")))
                        recommendations["budget_options"][poi_type] = sorted_by_price[:3]
        
        return recommendations
