#!/usr/bin/env python3
"""
摩旅智能助手基本使用示例（新架构）
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.route_planning import RoutePlanningAgent
from app.agents.weather import WeatherAgent
from app.agents.poi import POIAgent
from app.agents.base.message import MessagePriority

async def example_route_planning():
    """路线规划示例"""
    print("=== 路线规划示例（新架构）===")
    
    route_agent = RoutePlanningAgent()
    
    # 示例1: 基本路线规划
    result = await route_agent.execute(
        origin="北京",
        destination="上海",
        avoid_highway=True,
        fuel_range=300
    )
    
    print(f"查询: 从北京到上海的路线规划")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 路线规划成功")
        route_data = result.data
        print(f"  距离: {route_data['final_route']['distance_km']}km")
        print(f"  推荐: {route_data['route_comparison']['recommended_route']}")
        print(f"  加油站: {len(route_data['gas_stations'])}个")
    else:
        print(f"✗ 路线规划失败: {result.message}")
    
    print()


async def example_weather_query():
    """天气查询示例"""
    print("=== 天气查询示例（新架构）===")
    
    weather_agent = WeatherAgent()
    
    result = await weather_agent.execute(
        location="北京",
        days=3
    )
    
    print(f"查询: 北京的天气")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ 天气查询成功")
        weather_data = result.data
        if "safety_analysis" in weather_data:
            safety = weather_data["safety_analysis"]
            print(f"  安全评分: {safety.get('safety_score', 'N/A')}")
            print(f"  安全等级: {safety.get('safety_level', 'N/A')}")
    else:
        print(f"✗ 天气查询失败: {result.message}")
    
    print()


async def example_poi_search():
    """POI查询示例"""
    print("=== POI查询示例（新架构）===")
    
    poi_agent = POIAgent()
    
    # 搜索加油站
    result = await poi_agent.execute(
        location="北京",
        poi_type="gas_station",
        radius=10000
    )
    
    print(f"查询: 北京的加油站")
    print(f"结果: {result.message}")
    if result.success:
        print("✓ POI查询成功")
        poi_data = result.data
        print(f"  找到: {poi_data.get('total', 0)}个加油站")
    else:
        print(f"✗ POI查询失败: {result.message}")
    
    print()


async def example_a2a_communication():
    """A2A协议通信示例"""
    print("=== A2A协议通信示例 ===")
    
    route_agent = RoutePlanningAgent()
    weather_agent = WeatherAgent()
    poi_agent = POIAgent()
    
    # 1. 规划路线
    route_response = await route_agent.send_request(
        to_agent="route_planning",
        action="plan_route",
        payload={
            "origin": "北京",
            "destination": "上海",
            "avoid_highway": True
        },
        priority=MessagePriority.NORMAL
    )
    
    if route_response.success:
        print("✓ 路线规划成功（A2A）")
        route_data = route_response.payload
        
        # 2. 查询天气
        weather_response = await weather_agent.send_request(
            to_agent="weather",
            action="get_weather",
            payload={"location": "北京"}
        )
        
        if weather_response.success:
            print("✓ 天气查询成功（A2A）")
        
        # 3. 检查禁摩政策
        policy_response = await poi_agent.send_request(
            to_agent="poi",
            action="check_policy",
            payload={"city": "北京"}
        )
        
        if policy_response.success:
            print("✓ 政策检查成功（A2A）")
            policy_data = policy_response.payload
            if policy_data.get("policy", {}).get("has_restriction"):
                print(f"  ⚠️ 北京有禁摩政策: {policy_data['policy']['policy']}")
            else:
                print("  ✅ 北京无禁摩限制")
    
    print()


async def main():
    """主函数"""
    print("=" * 50)
    print("摩旅智能助手 - 新架构使用示例")
    print("=" * 50)
    print()
    
    try:
        await example_route_planning()
        await example_weather_query()
        await example_poi_search()
        await example_a2a_communication()
        
        print("=" * 50)
        print("所有示例执行完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"示例执行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
