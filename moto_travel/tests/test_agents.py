"""
Agent测试
"""
import pytest
import asyncio
from app.agents.enhanced_router import EnhancedAgentRouter
from app.agents.enhanced_moto_travel_agent import EnhancedMotoTravelAgent


class TestEnhancedAgentRouter:
    """增强版Agent路由器测试"""
    
    @pytest.fixture
    def router(self):
        return EnhancedAgentRouter()
    
    @pytest.mark.asyncio
    async def test_intent_recognition(self, router):
        """测试意图识别"""
        # 测试路线规划意图
        result = await router.execute(
            query="从北京到上海的路线规划",
            user_id="test_user"
        )
        assert result.success
        assert result.metadata["routed_agent"] == "route"
    
    @pytest.mark.asyncio
    async def test_weather_intent(self, router):
        """测试天气查询意图"""
        result = await router.execute(
            query="北京的天气怎么样",
            user_id="test_user"
        )
        assert result.success
        assert result.metadata["routed_agent"] == "weather"
    
    @pytest.mark.asyncio
    async def test_poi_intent(self, router):
        """测试POI查询意图"""
        result = await router.execute(
            query="北京有什么好吃的餐厅",
            user_id="test_user"
        )
        assert result.success
        assert result.metadata["routed_agent"] == "poi"


class TestEnhancedMotoTravelAgent:
    """增强版摩旅Agent测试"""
    
    @pytest.fixture
    def agent(self):
        return EnhancedMotoTravelAgent()
    
    @pytest.mark.asyncio
    async def test_route_planning(self, agent):
        """测试路线规划"""
        result = await agent.execute(
            query="从北京到上海的摩旅规划",
            user_id="test_user",
            output_format="json"
        )
        assert result.success
        assert "intelligence_features" in result.metadata
    
    @pytest.mark.asyncio
    async def test_fuel_budget_calculation(self, agent):
        """测试油耗预算计算"""
        result = await agent.execute(
            query="我的摩托车油耗是4.5L/100km，帮我算算油费",
            user_id="test_user"
        )
        assert result.success

