#!/usr/bin/env python3
"""
增强版摩旅智能助手使用示例
展示大模型能力和智能交互功能
"""
import sys
import os
import asyncio
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 注意：EnhancedMotoTravelAgent和EnhancedAgentRouter已迁移到新架构
# 此示例已过时，请参考 examples/basic_usage.py 和 examples/route_preferences_usage.py
# from app.agents.enhanced_moto_travel_agent import EnhancedMotoTravelAgent  # 已删除
# from app.agents.enhanced_router import EnhancedAgentRouter  # 已删除

# 使用新架构Agent
from app.agents.route_planning import RoutePlanningAgent
from app.agents.weather import WeatherAgent
from app.agents.poi import POIAgent
from app.agents.base.message import MessagePriority


async def example_intelligent_route_planning():
    """智能路线规划示例（新架构）"""
    print("=== 智能路线规划示例（新架构）===")
    print("⚠️ 注意：此示例已更新为新架构，请参考 examples/basic_usage.py")
    
    route_agent = RoutePlanningAgent()
    
    # 示例1: 基础路线规划（新架构）
    result = await route_agent.execute(
        origin="北京",
        destination="上海",
        waypoints=["泰山"],
        preferences={
            "highway_preference": "allow",
            "fuel_range_km": 300
        },
        user_id="user_001"
    )
    
    print(f"查询: 从北京到上海的摩旅规划，途经泰山")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 路线规划成功（新架构）")
        route_data = result.data
        print(f"距离: {route_data.get('final_route', {}).get('distance_km', 0)}km")
    else:
        print("✗ 路线规划失败")
    print()


async def example_fuel_budget_calculation():
    """油耗预算计算示例"""
    print("=== 油耗预算计算示例 ===")
    
    agent = EnhancedMotoTravelAgent()
    
    # 示例2: 油耗预算计算
    result = await agent.execute(
        query="我的摩托车油耗是4.2L/100km，从北京到上海1200公里，帮我算算油费",
        user_id="user_001",
        output_format="json"
    )
    
    print(f"查询: 我的摩托车油耗是4.2L/100km，从北京到上海1200公里，帮我算算油费")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 油耗预算计算成功")
        print(f"分析置信度: {result.metadata.get('analysis_confidence', 0)}")
    else:
        print("✗ 油耗预算计算失败")
    print()


async def example_weather_safety_analysis():
    """天气安全分析示例（新架构）"""
    print("=== 天气安全分析示例（新架构）===")
    
    weather_agent = WeatherAgent()
    
    # 示例3: 天气安全分析（新架构）
    result = await weather_agent.execute(
        location="北京",
        days=7,
        user_id="user_001"
    )
    
    print(f"查询: 北京的天气情况")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 天气查询成功（新架构）")
        weather_data = result.data
        print(f"当前温度: {weather_data.get('current', {}).get('temperature', 'N/A')}°C")
    else:
        print("✗ 天气查询失败")
    print()


async def example_poi_intelligent_recommendation():
    """POI智能推荐示例"""
    print("=== POI智能推荐示例 ===")
    
    router = EnhancedAgentRouter()
    
    # 示例4: POI智能推荐
    result = await router.execute(
        query="从北京到上海的路上，有什么好吃的餐厅？推荐几个摩托车友好的酒店，要有停车位",
        user_id="user_001"
    )
    
    print(f"查询: 从北京到上海的路上，有什么好吃的餐厅？推荐几个摩托车友好的酒店，要有停车位")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ POI智能推荐成功")
        print(f"工具调用描述: {result.metadata.get('tool_call_description', '')[:100]}...")
    else:
        print("✗ POI智能推荐失败")
    print()


async def example_policy_safety_search():
    """政策安全搜索示例"""
    print("=== 政策安全搜索示例 ===")
    
    router = EnhancedAgentRouter()
    
    # 示例5: 政策安全搜索
    result = await router.execute(
        query="摩托车能上高速吗？从北京到上海的路上有什么限行政策？路上有施工封路吗？",
        user_id="user_001"
    )
    
    print(f"查询: 摩托车能上高速吗？从北京到上海的路上有什么限行政策？路上有施工封路吗？")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 政策安全搜索成功")
        print(f"意图分析: {result.metadata.get('intent_analysis', {}).get('reasoning', '')}")
    else:
        print("✗ 政策安全搜索失败")
    print()


async def example_attraction_recommendation():
    """景点推荐示例"""
    print("=== 景点推荐示例 ===")
    
    router = EnhancedAgentRouter()
    
    # 示例6: 景点推荐
    result = await router.execute(
        query="从北京到上海的路上有什么好玩的景点？我喜欢自然风光和历史古迹，推荐几个值得去的地方",
        user_id="user_001"
    )
    
    print(f"查询: 从北京到上海的路上有什么好玩的景点？我喜欢自然风光和历史古迹，推荐几个值得去的地方")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 景点推荐成功")
        print(f"提取的实体: {result.metadata.get('intent_analysis', {}).get('extracted_entities', {})}")
    else:
        print("✗ 景点推荐失败")
    print()


async def example_personalization_service():
    """个性化服务示例"""
    print("=== 个性化服务示例 ===")
    
    router = EnhancedAgentRouter()
    
    # 示例7: 个性化服务
    result = await router.execute(
        query="我喜欢自然风光路线，日行距离不超过400公里，帮我保存这些偏好，以后推荐路线时考虑这些",
        user_id="user_001"
    )
    
    print(f"查询: 我喜欢自然风光路线，日行距离不超过400公里，帮我保存这些偏好，以后推荐路线时考虑这些")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 个性化服务成功")
        print(f"主要意图: {result.metadata.get('intent_analysis', {}).get('primary_intent')}")
    else:
        print("✗ 个性化服务失败")
    print()


async def example_complex_multi_intent_query():
    """复杂多意图查询示例"""
    print("=== 复杂多意图查询示例 ===")
    
    agent = EnhancedMotoTravelAgent()
    
    # 示例8: 复杂多意图查询
    result = await agent.execute(
        query="""
        我想规划一次从北京到西藏的摩旅，预算8000元，15天时间。
        我的摩托车油耗是5L/100km，喜欢自然风光路线。
        路上会经过哪些城市？天气怎么样？有什么好吃的？
        需要什么装备？有什么注意事项？
        """,
        user_id="user_001",
        output_format="markdown",
        conversation_history=[
            {"role": "user", "content": "我喜欢摩旅"},
            {"role": "assistant", "content": "很高兴为您提供摩旅服务"}
        ]
    )
    
    print(f"查询: 复杂多意图查询（北京到西藏摩旅规划）")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 复杂多意图查询成功")
        print(f"智能功能: {result.metadata.get('intelligence_features', [])}")
        print(f"分析置信度: {result.metadata.get('analysis_confidence', 0)}")
    else:
        print("✗ 复杂多意图查询失败")
    print()


async def example_route_customization():
    """路线定制示例"""
    print("=== 路线定制示例 ===")
    
    agent = EnhancedMotoTravelAgent()
    
    # 示例9: 路线定制
    result = await agent.execute(
        query="从北京到上海的原定路线，我想顺便去看看泰山和曲阜，帮我重新规划路线",
        user_id="user_001",
        output_format="json"
    )
    
    print(f"查询: 从北京到上海的原定路线，我想顺便去看看泰山和曲阜，帮我重新规划路线")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 路线定制成功")
        print("智能识别了用户的兴趣点并重新规划路线")
    else:
        print("✗ 路线定制失败")
    print()


async def main():
    """主函数"""
    print("增强版摩旅智能助手使用示例")
    print("=" * 60)
    
    # 运行各种示例
    await example_intelligent_route_planning()
    await example_fuel_budget_calculation()
    await example_weather_safety_analysis()
    await example_poi_intelligent_recommendation()
    await example_policy_safety_search()
    await example_attraction_recommendation()
    await example_personalization_service()
    await example_complex_multi_intent_query()
    await example_route_customization()
    
    print("=" * 60)
    print("所有增强版示例运行完成！")
    print("\n🎯 系统特色功能:")
    print("• 智能意图识别 - 深度理解用户需求")
    print("• 动态路线定制 - 自动集成用户兴趣点")
    print("• 精确油耗计算 - 基于实际油耗的预算分析")
    print("• 多Agent协作 - 智能路由和工具调用")
    print("• 个性化服务 - 基于用户偏好的定制化服务")
    print("• 安全风险评估 - 全面的摩旅安全分析")


if __name__ == "__main__":
    asyncio.run(main())
