#!/usr/bin/env python3
"""
摩旅智能助手模板使用示例
展示如何使用输出模板和提示词模板
"""
import sys
import os
import asyncio
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.moto_travel_agent import MotoTravelAgent
from app.templates.output_templates import MotoTravelPlan, OutputFormatter, OutputFormat
from app.templates.moto_travel_prompt import MotoTravelPromptTemplate


async def example_json_output():
    """JSON输出示例"""
    print("=== JSON输出示例 ===")
    
    # 创建示例数据
    sample_plan = create_sample_plan()
    
    # 使用输出格式化器
    formatter = OutputFormatter()
    json_output = formatter.format_output(sample_plan, OutputFormat.JSON)
    
    print("JSON输出格式:")
    print(json.dumps(json_output, ensure_ascii=False, indent=2))
    print()


async def example_markdown_output():
    """Markdown输出示例"""
    print("=== Markdown输出示例 ===")
    
    # 创建示例数据
    sample_plan = create_sample_plan()
    
    # 使用输出格式化器
    formatter = OutputFormatter()
    markdown_output = formatter.format_output(sample_plan, OutputFormat.MARKDOWN)
    
    print("Markdown输出格式:")
    print(markdown_output)
    print()


async def example_agent_usage():
    """Agent使用示例"""
    print("=== Agent使用示例 ===")
    
    # 创建摩旅Agent
    agent = MotoTravelAgent()
    
    # 执行规划
    result = await agent.execute(
        query="从北京到上海的摩旅规划，预算5000元，7天时间",
        user_id="user_001",
        output_format="markdown",
        preferences={
            "daily_distance": 400,
            "route_type": "自然风光",
            "travel_style": "休闲",
            "budget_range": 5000
        }
    )
    
    if result.success:
        print("规划成功!")
        print(f"消息: {result.message}")
        print(f"数据: {result.data}")
    else:
        print("规划失败!")
        print(f"错误: {result.message}")
    print()


def example_prompt_templates():
    """提示词模板示例"""
    print("=== 提示词模板示例 ===")
    
    # 获取系统提示词
    system_prompt = MotoTravelPromptTemplate.get_system_prompt()
    print("系统提示词长度:", len(system_prompt))
    print("系统提示词前200字符:")
    print(system_prompt[:200] + "...")
    print()
    
    # 获取完整提示词
    complete_prompt = MotoTravelPromptTemplate.get_complete_prompt()
    print("完整提示词长度:", len(complete_prompt))
    print("完整提示词前200字符:")
    print(complete_prompt[:200] + "...")
    print()
    
    # 获取成功标准
    success_criteria = MotoTravelPromptTemplate.get_success_criteria()
    print("成功标准:")
    for criterion in success_criteria:
        print(f"  {criterion}")
    print()


def create_sample_plan() -> MotoTravelPlan:
    """创建示例计划"""
    from datetime import datetime
    
    return MotoTravelPlan(
        plan_id="sample_plan_001",
        user_id="user_001",
        title="从北京到上海的摩旅计划",
        description="一次精彩的摩旅体验",
        created_at=datetime.utcnow().isoformat(),
        
        # 路线信息
        origin={
            "name": "北京",
            "address": "北京市朝阳区",
            "coordinates": {"longitude": 116.397, "latitude": 39.909},
            "province": "北京市",
            "city": "北京",
            "district": "朝阳区"
        },
        destination={
            "name": "上海",
            "address": "上海市黄浦区",
            "coordinates": {"longitude": 121.473, "latitude": 31.230},
            "province": "上海市",
            "city": "上海",
            "district": "黄浦区"
        },
        waypoints=[],
        total_distance_km=1200.0,
        total_duration_days=7,
        route_type="自然风光",
        
        # 每日路线
        daily_routes=[
            {
                "day": 1,
                "date": "2024-07-01",
                "start_location": {"name": "北京", "address": "北京市朝阳区"},
                "end_location": {"name": "天津", "address": "天津市和平区"},
                "total_distance_km": 120.0,
                "estimated_duration_hours": 2.5,
                "segments": [],
                "recommended_stops": [
                    {"name": "加油站", "description": "途中加油站", "distance": 60}
                ],
                "accommodation": {
                    "name": "天津摩旅酒店",
                    "address": "天津市和平区",
                    "price": 200
                }
            }
        ],
        
        # 天气信息
        weather_forecast=[
            {
                "location": "北京",
                "date": "2024-07-01",
                "temperature": 25.0,
                "weather_condition": "晴天",
                "humidity": 60.0,
                "wind_speed": 10.0,
                "wind_direction": "东南风",
                "visibility": 15.0,
                "safety_score": 85,
                "safety_level": "良好",
                "warnings": [],
                "recommendations": ["天气条件良好，适合骑行"]
            }
        ],
        weather_alerts=[],
        
        # POI信息
        restaurants=[
            {
                "id": "rest_001",
                "name": "北京烤鸭店",
                "category": "餐饮",
                "location": {"name": "北京", "address": "北京市朝阳区"},
                "rating": 4.5,
                "price_level": "中等",
                "business_hours": "10:00-22:00",
                "phone": "010-12345678",
                "website": "http://example.com",
                "description": "正宗北京烤鸭",
                "features": ["停车位", "WiFi"],
                "distance_from_route": 0.5
            }
        ],
        accommodations=[
            {
                "id": "hotel_001",
                "name": "摩旅友好酒店",
                "category": "住宿",
                "location": {"name": "天津", "address": "天津市和平区"},
                "rating": 4.2,
                "price_level": "经济",
                "business_hours": "24小时",
                "phone": "022-87654321",
                "website": "http://hotel.com",
                "description": "摩托车友好酒店",
                "features": ["摩托车停放", "维修工具"],
                "distance_from_route": 1.0
            }
        ],
        gas_stations=[
            {
                "id": "gas_001",
                "name": "中石化加油站",
                "category": "加油站",
                "location": {"name": "北京", "address": "北京市朝阳区"},
                "rating": 4.0,
                "price_level": "标准",
                "business_hours": "24小时",
                "phone": "010-11111111",
                "website": "",
                "description": "24小时营业加油站",
                "features": ["95号汽油", "92号汽油"],
                "distance_from_route": 2.0
            }
        ],
        repair_shops=[],
        attractions=[],
        
        # 预算信息
        total_budget=5000.0,
        daily_budgets=[
            {
                "day": 1,
                "date": "2024-07-01",
                "items": [
                    {
                        "category": "燃油",
                        "item_name": "汽油",
                        "unit_cost": 7.5,
                        "quantity": 20,
                        "total_cost": 150.0,
                        "description": "95号汽油"
                    }
                ],
                "total_cost": 500.0,
                "currency": "CNY"
            }
        ],
        budget_breakdown={
            "燃油费": 800.0,
            "住宿费": 1400.0,
            "餐饮费": 1200.0,
            "其他费用": 1600.0
        },
        
        # 安全信息
        safety_alerts=[],
        safety_recommendations=[
            "遵守交通规则，安全第一",
            "定期检查车辆状况",
            "注意天气变化，适时调整行程"
        ],
        
        # 个性化信息
        user_preferences={
            "daily_distance": 400,
            "route_type": "自然风光",
            "travel_style": "休闲"
        },
        personalized_recommendations=[
            "建议选择风景优美的国道",
            "推荐在当地特色餐厅用餐",
            "注意避开高峰时段出行"
        ],
        
        # 元数据
        metadata={
            "planning_time": datetime.utcnow().isoformat(),
            "agents_used": ["route", "weather", "poi", "budget"],
            "success_rate": 1.0
        }
    )


async def main():
    """主函数"""
    print("摩旅智能助手模板使用示例")
    print("=" * 50)
    
    # 运行各种示例
    await example_json_output()
    await example_markdown_output()
    await example_agent_usage()
    example_prompt_templates()
    
    print("=" * 50)
    print("所有示例运行完成！")


if __name__ == "__main__":
    asyncio.run(main())
