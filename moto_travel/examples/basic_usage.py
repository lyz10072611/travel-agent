#!/usr/bin/env python3
"""
摩旅智能助手基本使用示例
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.router import AgentRouter
from app.langchain_integration import LangChainIntegration

async def example_route_planning():
    """路线规划示例"""
    print("=== 路线规划示例 ===")
    
    router = AgentRouter()
    
    # 示例1: 基本路线规划
    result = await router.execute(
        query="从北京到上海的路线规划",
        user_id="user_001"
    )
    
    print(f"查询: 从北京到上海的路线规划")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 路线规划成功")
    else:
        print("✗ 路线规划失败")
    print()

async def example_weather_query():
    """天气查询示例"""
    print("=== 天气查询示例 ===")
    
    router = AgentRouter()
    
    # 示例2: 天气查询
    result = await router.execute(
        query="北京未来3天的天气",
        user_id="user_001"
    )
    
    print(f"查询: 北京未来3天的天气")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 天气查询成功")
    else:
        print("✗ 天气查询失败")
    print()

async def example_poi_search():
    """POI搜索示例"""
    print("=== POI搜索示例 ===")
    
    router = AgentRouter()
    
    # 示例3: POI搜索
    result = await router.execute(
        query="上海有什么好吃的餐厅",
        user_id="user_001"
    )
    
    print(f"查询: 上海有什么好吃的餐厅")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ POI搜索成功")
    else:
        print("✗ POI搜索失败")
    print()

async def example_budget_calculation():
    """预算计算示例"""
    print("=== 预算计算示例 ===")
    
    router = AgentRouter()
    
    # 示例4: 预算计算
    result = await router.execute(
        query="计算从北京到上海500公里的旅行预算",
        user_id="user_001"
    )
    
    print(f"查询: 计算从北京到上海500公里的旅行预算")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 预算计算成功")
    else:
        print("✗ 预算计算失败")
    print()

async def example_langchain_integration():
    """LangChain集成示例"""
    print("=== LangChain集成示例 ===")
    
    langchain = LangChainIntegration()
    
    # 示例5: 使用LangChain处理查询
    result = await langchain.process_query(
        query="我想规划一次从北京到上海的摩旅，需要了解天气和预算",
        user_id="user_001",
        thread_id="conversation_001"
    )
    
    print(f"查询: 我想规划一次从北京到上海的摩旅，需要了解天气和预算")
    print(f"响应: {result['response']}")
    print(f"使用的Agent: {result.get('agent_used', '未知')}")
    if result['success']:
        print("✓ LangChain处理成功")
    else:
        print("✗ LangChain处理失败")
    print()

async def main():
    """主函数"""
    print("摩旅智能助手使用示例")
    print("=" * 50)
    
    # 运行各种示例
    await example_route_planning()
    await example_weather_query()
    await example_poi_search()
    await example_budget_calculation()
    await example_langchain_integration()
    
    print("=" * 50)
    print("所有示例运行完成！")

if __name__ == "__main__":
    asyncio.run(main())
