#!/usr/bin/env python3
"""
Agent测试脚本
"""
import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.router import AgentRouter
from app.agents.route_agent import RouteAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.poi_agent import POIAgent

async def test_route_agent():
    """测试路线规划Agent"""
    print("测试路线规划Agent...")
    
    agent = RouteAgent()
    
    try:
        result = await agent.execute(
            query="从北京到上海的路线规划",
            origin="北京",
            destination="上海",
            daily_distance=400
        )
        
        if result.success:
            print("✓ 路线规划Agent测试成功")
            print(f"  消息: {result.message}")
        else:
            print("✗ 路线规划Agent测试失败")
            print(f"  错误: {result.message}")
            
    except Exception as e:
        print(f"✗ 路线规划Agent测试异常: {str(e)}")

async def test_weather_agent():
    """测试天气查询Agent"""
    print("测试天气查询Agent...")
    
    agent = WeatherAgent()
    
    try:
        result = await agent.execute(
            query="北京的天气",
            location="北京",
            days=3
        )
        
        if result.success:
            print("✓ 天气查询Agent测试成功")
            print(f"  消息: {result.message}")
        else:
            print("✗ 天气查询Agent测试失败")
            print(f"  错误: {result.message}")
            
    except Exception as e:
        print(f"✗ 天气查询Agent测试异常: {str(e)}")

async def test_poi_agent():
    """测试POI查询Agent"""
    print("测试POI查询Agent...")
    
    agent = POIAgent()
    
    try:
        result = await agent.execute(
            query="北京的餐厅",
            location="北京",
            poi_type="restaurant"
        )
        
        if result.success:
            print("✓ POI查询Agent测试成功")
            print(f"  消息: {result.message}")
        else:
            print("✗ POI查询Agent测试失败")
            print(f"  错误: {result.message}")
            
    except Exception as e:
        print(f"✗ POI查询Agent测试异常: {str(e)}")

async def test_agent_router():
    """测试Agent路由器"""
    print("测试Agent路由器...")
    
    router = AgentRouter()
    
    try:
        result = await router.execute(
            query="从北京到上海的路线规划",
            user_id="test_user"
        )
        
        if result.success:
            print("✓ Agent路由器测试成功")
            print(f"  消息: {result.message}")
        else:
            print("✗ Agent路由器测试失败")
            print(f"  错误: {result.message}")
            
    except Exception as e:
        print(f"✗ Agent路由器测试异常: {str(e)}")

async def main():
    """主函数"""
    print("开始测试Agent系统...")
    print("=" * 50)
    
    # 测试各个Agent
    await test_route_agent()
    print()
    
    await test_weather_agent()
    print()
    
    await test_poi_agent()
    print()
    
    await test_agent_router()
    print()
    
    print("=" * 50)
    print("Agent系统测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
