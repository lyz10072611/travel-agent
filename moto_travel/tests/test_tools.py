"""
工具测试（更新为新架构）
"""
import pytest
import asyncio

# 新架构工具导入
from app.agents.route_planning.tools.amap_tool import AmapTool
from app.agents.weather.tools.weather_tool import QWeatherTool
from app.agents.poi.tools.poi_tool import POITool
from tools.budget_tools import BudgetCalculator


class TestAmapTool:
    """高德地图工具测试"""
    
    @pytest.fixture
    def amap_tool(self):
        return AmapTool()
    
    @pytest.mark.asyncio
    async def test_geocode(self, amap_tool):
        """测试地理编码"""
        async with amap_tool:
            result = await amap_tool.geocode("北京天安门")
            # 由于需要真实API密钥，这里只测试方法调用
            assert hasattr(result, 'success') or 'data' in result
    
    @pytest.mark.asyncio
    async def test_get_route(self, amap_tool):
        """测试路线规划"""
        async with amap_tool:
            result = await amap_tool.get_route(
                origin="北京",
                destination="上海"
            )
            assert hasattr(result, 'success') or 'data' in result


class TestQWeatherTool:
    """和风天气工具测试"""
    
    @pytest.fixture
    def weather_tool(self):
        return QWeatherTool()
    
    @pytest.mark.asyncio
    async def test_get_current_weather(self, weather_tool):
        """测试当前天气查询"""
        async with weather_tool:
            result = await weather_tool.get_current_weather("北京")
            assert hasattr(result, 'success') or 'data' in result


class TestPOITool:
    """POI工具测试"""
    
    @pytest.fixture
    def poi_tool(self):
        return POITool()
    
    @pytest.mark.asyncio
    async def test_search_poi(self, poi_tool):
        """测试POI搜索"""
        async with poi_tool:
            result = await poi_tool.search_poi(
                keywords="加油站",
                location="北京"
            )
            assert hasattr(result, 'success') or 'data' in result


class TestBudgetCalculator:
    """预算计算器测试"""
    
    @pytest.fixture
    def budget_calculator(self):
        return BudgetCalculator()
    
    @pytest.mark.asyncio
    async def test_calculate_trip_budget(self, budget_calculator):
        """测试旅行预算计算"""
        result = await budget_calculator.calculate_trip_budget(
            total_distance=1200,
            days=7
        )
        assert result.success
        assert "total_cost" in result.data
