#!/usr/bin/env python3
"""
路线规划偏好配置使用示例
展示灵活的标准配置和交互式偏好收集
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.route_planning import RoutePlanningAgent
from app.agents.route_planning.strategies.route_preferences import (
    RoutePreferences,
    HighwayPreference
)


async def example_flexible_highway_preference():
    """示例1：灵活的高速公路偏好"""
    print("=== 示例1：灵活的高速公路偏好 ===")
    
    route_agent = RoutePlanningAgent()
    
    # 方式1：允许走高速（默认，灵活标准）
    print("\n1. 允许走高速（默认）")
    result1 = await route_agent.execute(
        origin="北京",
        destination="上海",
        preferences={
            "highway_preference": "allow"  # 允许，但不强制
        }
    )
    if result1.success:
        analysis = result1.data.get("moto_analysis", {})
        print(f"   高速公路路段: {len(analysis.get('highway_segments', []))}个")
        print(f"   警告: {analysis.get('warnings', [])}")
        print(f"   建议: {analysis.get('recommendations', [])}")
    
    # 方式2：尽量避开高速（建议，但非强制）
    print("\n2. 尽量避开高速（建议）")
    result2 = await route_agent.execute(
        origin="北京",
        destination="上海",
        preferences={
            "highway_preference": "avoid"  # 尽量避开，但非强制
        }
    )
    if result2.success:
        analysis = result2.data.get("moto_analysis", {})
        print(f"   高速公路路段: {len(analysis.get('highway_segments', []))}个")
        print(f"   警告: {analysis.get('warnings', [])}")
        print(f"   建议: {analysis.get('recommendations', [])}")
    
    # 方式3：禁止走高速（严格）
    print("\n3. 禁止走高速（严格）")
    result3 = await route_agent.execute(
        origin="北京",
        destination="上海",
        preferences={
            "highway_preference": "forbid"  # 严格禁止
        }
    )
    if result3.success:
        analysis = result3.data.get("moto_analysis", {})
        print(f"   适合摩旅: {analysis.get('suitable_for_moto', False)}")
        print(f"   警告: {analysis.get('warnings', [])}")
    
    print()


async def example_night_national_road_avoidance():
    """示例2：晚上避开国道"""
    print("=== 示例2：晚上避开国道 ===")
    
    route_agent = RoutePlanningAgent()
    
    # 晚上出发，自动避开国道
    print("\n1. 晚上出发（18:00），自动避开国道")
    result = await route_agent.execute(
        origin="北京",
        destination="上海",
        preferences={
            "departure_time": "2024-01-15 18:00",  # 晚上出发
            "avoid_national_road_at_night": True,  # 开启避开（默认）
            "night_start_time": "18:00",
            "night_end_time": "06:00"
        }
    )
    
    if result.success:
        analysis = result.data.get("moto_analysis", {})
        night_segments = analysis.get("night_segments", [])
        print(f"   晚上国道路段: {len(night_segments)}个")
        for seg in night_segments[:3]:  # 显示前3个
            print(f"   - 路段{seg.get('index')+1}: {seg.get('road')} "
                  f"({seg.get('night_time')}) - {seg.get('warning', '')}")
        print(f"   建议: {analysis.get('recommendations', [])}")
    
    # 关闭避开选项
    print("\n2. 关闭晚上避开国道选项")
    result2 = await route_agent.execute(
        origin="北京",
        destination="上海",
        preferences={
            "departure_time": "2024-01-15 18:00",
            "avoid_national_road_at_night": False  # 关闭
        }
    )
    
    if result2.success:
        analysis = result2.data.get("moto_analysis", {})
        print(f"   晚上国道路段: {len(analysis.get('night_segments', []))}个")
        print(f"   建议: {analysis.get('recommendations', [])}")
    
    print()


async def example_interactive_preferences():
    """示例3：交互式偏好收集"""
    print("=== 示例3：交互式偏好收集 ===")
    
    route_agent = RoutePlanningAgent()
    collector_id = "test_user_001"
    
    # 1. 获取第一个问题
    print("\n1. 获取第一个问题")
    response = await route_agent.send_request(
        to_agent="route_planning",
        action="interactive_collect_preferences",
        payload={
            "action": "get_next",
            "collector_id": collector_id,
            "context": {"query": "我想从北京到上海"}
        }
    )
    
    if response.success:
        if response.payload.get("has_question"):
            question = response.payload["question"]
            print(f"   问题: {question['question']}")
            print(f"   选项: {[opt['label'] for opt in question.get('options', [])]}")
            print(f"   默认值: {question.get('default', '无')}")
            
            # 2. 回答问题
            print("\n2. 回答问题")
            answer = "allow"  # 用户选择"允许走高速"
            response2 = await route_agent.send_request(
                to_agent="route_planning",
                action="interactive_collect_preferences",
                payload={
                    "action": "answer",
                    "collector_id": collector_id,
                    "key": question["key"],
                    "value": answer
                }
            )
            
            if response2.success:
                print(f"   已回答: {question['key']} = {answer}")
                print(f"   剩余问题: {response2.payload.get('remaining', 0)}个")
                
                if response2.payload.get("is_complete"):
                    print("\n3. 偏好收集完成")
                    prefs = response2.payload.get("preferences", {})
                    print(f"   偏好配置: {prefs}")
    
    print()


async def example_infer_preferences():
    """示例4：从查询中推断偏好"""
    print("=== 示例4：从查询中推断偏好 ===")
    
    route_agent = RoutePlanningAgent()
    
    queries = [
        "我想从北京到上海，不走高速",
        "我想从北京到上海，尽量避开高速",
        "我想从北京到上海，晚上出发",
        "我想从北京到上海，优先走高速，续航300公里"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        response = await route_agent.send_request(
            to_agent="route_planning",
            action="infer_preferences",
            payload={"query": query}
        )
        
        if response.success:
            inferred = response.payload.get("inferred", {})
            print(f"   推断的偏好: {inferred}")
    
    print()


async def example_custom_night_time():
    """示例5：自定义晚上时段"""
    print("=== 示例5：自定义晚上时段 ===")
    
    route_agent = RoutePlanningAgent()
    
    # 自定义晚上时段为20:00-08:00
    result = await route_agent.execute(
        origin="北京",
        destination="上海",
        preferences={
            "departure_time": "2024-01-15 19:00",
            "avoid_national_road_at_night": True,
            "night_start_time": "20:00",  # 自定义开始时间
            "night_end_time": "08:00"     # 自定义结束时间
        }
    )
    
    if result.success:
        analysis = result.data.get("moto_analysis", {})
        print(f"   晚上时段: 20:00 - 08:00")
        print(f"   晚上国道路段: {len(analysis.get('night_segments', []))}个")
        print(f"   建议: {analysis.get('recommendations', [])}")
    
    print()


async def main():
    """主函数"""
    print("=" * 60)
    print("路线规划偏好配置使用示例")
    print("=" * 60)
    print()
    
    try:
        await example_flexible_highway_preference()
        await example_night_national_road_avoidance()
        await example_interactive_preferences()
        await example_infer_preferences()
        await example_custom_night_time()
        
        print("=" * 60)
        print("所有示例执行完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"示例执行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

