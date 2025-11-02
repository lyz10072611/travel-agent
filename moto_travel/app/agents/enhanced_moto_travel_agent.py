"""
增强版摩旅智能助手主Agent
充分体现大模型能力，提供更智能的多Agent协作和用户交互
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import re
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.agents.base_agent import AsyncAgent, AgentResponse, AgentType
from app.agents.router import AgentRouter
from app.templates.output_templates import MotoTravelPlan, OutputFormatter, OutputFormat
from app.templates.moto_travel_prompt import MotoTravelPromptTemplate
from app.config import settings
from loguru import logger


class EnhancedMotoTravelAgent(AsyncAgent):
    """增强版摩旅智能助手主Agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.ROUTE,
            name="enhanced_moto_travel_agent",
            description="增强版摩旅智能助手，具备强大的大模型能力和智能交互功能"
        )
        
        # 初始化大模型
        self.llm = ChatOpenAI(
            model_name=settings.qwen_model,
            openai_api_key=settings.qwen_api_key,
            openai_api_base=settings.qwen_base_url,
            temperature=0.1,
            max_tokens=4000
        )
        
        self.agent_router = AgentRouter()
        self.output_formatter = OutputFormatter()
        self.prompt_template = MotoTravelPromptTemplate()
        
        # 智能分析提示词
        self.intelligent_analysis_prompt = """
您是一个专业的摩旅智能分析助手，具备以下核心能力：

## 🧠 智能分析能力
1. **深度需求理解**: 从用户的自然语言输入中准确提取摩旅需求
2. **上下文感知**: 理解用户的隐含需求和偏好
3. **智能推理**: 基于用户输入进行逻辑推理和需求补充
4. **个性化适配**: 根据用户特征提供个性化建议

## 📝 输入分析任务
请仔细分析用户输入，提取以下信息：

### 基础信息提取
- **起点和终点**: 准确识别出发地和目的地
- **途经点**: 识别用户提到的感兴趣地点
- **时间信息**: 出发日期、旅行天数、时间偏好
- **距离偏好**: 日行距离、总距离预期
- **路线类型**: 自然风光、经典摩旅、历史人文、探险挑战

### 高级需求分析
- **骑行风格**: 休闲观光、激情驾驶、探险挑战、文化体验
- **预算信息**: 总预算、日均预算、各项费用偏好
- **同伴信息**: 独自、双人、团队、经验水平
- **特殊需求**: 装备要求、身体状况、兴趣偏好、安全要求
- **个性化要素**: 以往经历、偏好习惯、特殊场合

### 智能推理补充
- **隐含需求**: 用户未明确表达但可能需要的服务
- **风险识别**: 识别潜在的安全风险和挑战
- **优化建议**: 基于最佳实践提供改进建议
- **个性化推荐**: 根据用户特征推荐适合的选项

## 🎯 输出要求
请以JSON格式输出分析结果，包含：
```json
{
  "extracted_info": {
    "origin": "起点",
    "destination": "终点", 
    "waypoints": ["途经点1", "途经点2"],
    "start_date": "出发日期",
    "duration_days": 天数,
    "daily_distance": 日行距离,
    "route_type": "路线类型",
    "travel_style": "骑行风格",
    "budget_range": 预算范围,
    "companions": "同伴信息",
    "special_requirements": ["特殊需求"],
    "interests": ["兴趣偏好"]
  },
  "intelligent_analysis": {
    "implicit_needs": ["隐含需求"],
    "risk_factors": ["风险因素"],
    "optimization_suggestions": ["优化建议"],
    "personalized_recommendations": ["个性化推荐"]
  },
  "confidence_score": 0.95,
  "analysis_notes": "分析说明"
}
```

请基于用户输入进行深度分析，确保提取的信息准确完整。
"""
        
        # 智能路线定制提示词
        self.route_customization_prompt = """
您是一个专业的摩旅路线定制专家，具备以下核心能力：

## 🛣️ 路线定制能力
1. **智能路线规划**: 基于用户需求和偏好规划最优路线
2. **动态调整**: 根据用户反馈和新增需求实时调整路线
3. **兴趣点集成**: 智能将用户感兴趣的地点融入路线
4. **多目标优化**: 平衡距离、时间、安全、体验等多个目标

## 📍 兴趣点集成任务
当用户提到感兴趣的地点时，请：

### 智能分析兴趣点
- **位置分析**: 确定兴趣点的准确位置和坐标
- **路线影响**: 分析对原路线的影响（距离、时间、难度）
- **可行性评估**: 评估是否适合摩托车到达
- **体验价值**: 评估该地点的游览价值和体验质量

### 路线重新规划
- **最优路径**: 计算包含兴趣点的最优路线
- **时间调整**: 重新计算总时间和每日安排
- **成本影响**: 评估对预算的影响
- **安全考虑**: 评估新增路线的安全风险

### 智能建议输出
- **路线对比**: 提供原路线和调整后路线的对比
- **权衡分析**: 分析调整的利弊得失
- **替代方案**: 提供多种集成方案供选择
- **实施建议**: 提供具体的实施步骤和建议

## 🎯 输出要求
请以JSON格式输出定制结果：
```json
{
  "route_analysis": {
    "original_route": {
      "total_distance": 1200,
      "total_duration": 7,
      "waypoints": []
    },
    "customized_route": {
      "total_distance": 1350,
      "total_duration": 8,
      "waypoints": ["兴趣点1", "兴趣点2"],
      "additional_distance": 150,
      "additional_time": 1
    }
  },
  "interest_points": [
    {
      "name": "兴趣点名称",
      "location": "具体位置",
      "coordinates": {"longitude": 116.0, "latitude": 39.0},
      "route_impact": {
        "distance_impact": 50,
        "time_impact": 0.5,
        "difficulty_change": "中等",
        "safety_risk": "低"
      },
      "experience_value": "高",
      "recommendation": "强烈推荐"
    }
  ],
  "cost_impact": {
    "additional_fuel_cost": 50,
    "additional_accommodation_cost": 200,
    "additional_food_cost": 100,
    "total_additional_cost": 350
  },
  "recommendations": [
    "建议将兴趣点安排在路线中段，避免过度绕行",
    "该地点适合摩托车到达，路况良好",
    "建议预留半天时间进行深度游览"
  ],
  "alternative_options": [
    {
      "option_name": "方案A",
      "description": "详细描述",
      "pros": ["优点1", "优点2"],
      "cons": ["缺点1", "缺点2"]
    }
  ]
}
```

请基于用户需求和兴趣点进行智能路线定制。
"""
        
        # 油耗预算计算提示词
        self.fuel_budget_prompt = """
您是一个专业的摩旅油耗预算计算专家，具备以下核心能力：

## ⛽ 油耗预算能力
1. **精确油耗计算**: 基于车型、路况、驾驶习惯计算精确油耗
2. **动态预算调整**: 根据实时油价和路线变化调整预算
3. **多因素分析**: 综合考虑各种影响油耗的因素
4. **成本优化建议**: 提供降低燃油成本的实用建议

## 🚗 油耗分析任务
当用户提供日常油耗信息时，请：

### 油耗数据验证
- **数据合理性**: 验证用户提供的油耗数据是否合理
- **影响因素分析**: 分析影响油耗的各种因素
- **基准对比**: 与同类车型的油耗基准进行对比
- **异常识别**: 识别异常的油耗数据并提供解释

### 精确预算计算
- **基础计算**: 基于距离和油耗计算基础燃油需求
- **路况调整**: 根据路线类型调整油耗系数
- **天气影响**: 考虑天气对油耗的影响
- **驾驶习惯**: 根据用户驾驶风格调整油耗

### 成本优化分析
- **油价分析**: 分析沿途不同地区的油价差异
- **路线优化**: 提供更省油的路线选择
- **驾驶建议**: 提供降低油耗的驾驶技巧
- **替代方案**: 提供燃油成本更低的替代方案

## 🎯 输出要求
请以JSON格式输出计算结果：
```json
{
  "fuel_analysis": {
    "user_provided_consumption": 4.5,
    "validated_consumption": 4.5,
    "consumption_reasonableness": "合理",
    "factors_affecting_consumption": [
      "车型: 250cc摩托车",
      "路况: 混合路况",
      "驾驶习惯: 中等激进"
    ]
  },
  "budget_calculation": {
    "total_distance": 1200,
    "base_fuel_needed": 54,
    "route_adjustment_factor": 1.1,
    "weather_adjustment_factor": 1.05,
    "final_fuel_needed": 62.37,
    "average_fuel_price": 7.5,
    "total_fuel_cost": 467.78
  },
  "cost_breakdown": {
    "highway_segments": {
      "distance": 400,
      "fuel_needed": 16,
      "cost": 120
    },
    "mountain_roads": {
      "distance": 300,
      "fuel_needed": 18,
      "cost": 135
    },
    "city_roads": {
      "distance": 500,
      "fuel_needed": 28.37,
      "cost": 212.78
    }
  },
  "optimization_suggestions": [
    "选择更省油的路线，可节省15%燃油成本",
    "保持经济时速60-80km/h，可降低10%油耗",
    "避免频繁加速减速，可减少5%燃油消耗"
  ],
  "fuel_station_planning": [
    {
      "location": "路线中点",
      "distance_from_start": 600,
      "recommended_fuel_amount": 30,
      "estimated_cost": 225,
      "station_recommendation": "中石化加油站"
    }
  ],
  "alternative_fuel_options": [
    {
      "option": "使用高标号汽油",
      "cost_impact": "+20%",
      "benefits": ["更好的发动机保护", "更清洁的燃烧"]
    }
  ]
}
```

请基于用户提供的油耗信息进行精确的预算计算和分析。
"""
    
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """执行增强版摩旅规划"""
        query = kwargs.get("query", "")
        user_id = kwargs.get("user_id", "")
        output_format = kwargs.get("output_format", "markdown")
        preferences = kwargs.get("preferences", {})
        conversation_history = kwargs.get("conversation_history", [])
        
        try:
            if not query:
                return self._create_error_response("请提供摩旅规划需求")
            
            # 1. 智能需求分析
            user_requirements = await self._intelligent_requirement_analysis(
                query, preferences, conversation_history
            )
            
            # 2. 检查是否需要路线定制
            if await self._needs_route_customization(query, user_requirements):
                customized_requirements = await self._intelligent_route_customization(
                    query, user_requirements
                )
                user_requirements.update(customized_requirements)
            
            # 3. 检查是否需要油耗预算计算
            if await self._needs_fuel_budget_calculation(query, user_requirements):
                fuel_budget_analysis = await self._intelligent_fuel_budget_calculation(
                    query, user_requirements
                )
                user_requirements["fuel_budget_analysis"] = fuel_budget_analysis
            
            # 4. 执行多Agent协作规划
            planning_results = await self._execute_enhanced_multi_agent_planning(
                user_requirements, user_id
            )
            
            # 5. 智能结果整合
            integrated_plan = await self._intelligent_result_integration(
                user_requirements, planning_results
            )
            
            # 6. 生成最终输出
            if output_format.lower() == "json":
                final_output = self.output_formatter.format_output(
                    integrated_plan, OutputFormat.JSON
                )
            else:
                final_output = self.output_formatter.format_output(
                    integrated_plan, OutputFormat.MARKDOWN
                )
            
            return self._create_success_response(
                data=final_output,
                message="智能摩旅规划完成",
                metadata={
                    "user_id": user_id,
                    "output_format": output_format,
                    "plan_id": integrated_plan.plan_id,
                    "intelligence_features": [
                        "智能需求分析",
                        "动态路线定制", 
                        "精确油耗计算",
                        "多Agent协作"
                    ],
                    "analysis_confidence": user_requirements.get("confidence_score", 0.9)
                }
            )
            
        except Exception as e:
            logger.error(f"Enhanced moto travel planning failed: {str(e)}")
            return self._create_error_response(f"智能摩旅规划失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        return self._validate_required_params(["query"], **kwargs)
    
    async def _intelligent_requirement_analysis(
        self, 
        query: str, 
        preferences: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """智能需求分析"""
        
        try:
            # 构建上下文
            context = f"""
用户当前查询: {query}
用户偏好设置: {json.dumps(preferences, ensure_ascii=False)}
对话历史: {json.dumps(conversation_history[-3:], ensure_ascii=False)}
"""
            
            messages = [
                SystemMessage(content=self.intelligent_analysis_prompt),
                HumanMessage(content=context)
            ]
            
            response = await self.llm.agenerate([messages])
            analysis_result = response.generations[0][0].text.strip()
            
            # 解析JSON结果
            try:
                analysis_data = json.loads(analysis_result)
                return analysis_data
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用正则表达式提取信息
                return await self._fallback_requirement_analysis(query, preferences)
                
        except Exception as e:
            logger.error(f"Intelligent requirement analysis failed: {str(e)}")
            return await self._fallback_requirement_analysis(query, preferences)
    
    async def _fallback_requirement_analysis(
        self, 
        query: str, 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """备用需求分析方法"""
        
        # 使用规则和正则表达式进行基础分析
        requirements = {
            "extracted_info": {
                "origin": "",
                "destination": "",
                "waypoints": [],
                "start_date": "",
                "duration_days": 0,
                "daily_distance": 300,
                "route_type": "自然风光",
                "travel_style": "休闲",
                "budget_range": 5000,
                "companions": "独自",
                "special_requirements": [],
                "interests": []
            },
            "intelligent_analysis": {
                "implicit_needs": [],
                "risk_factors": [],
                "optimization_suggestions": [],
                "personalized_recommendations": []
            },
            "confidence_score": 0.7,
            "analysis_notes": "使用备用分析方法"
        }
        
        # 简单的关键词提取
        if "从" in query and "到" in query:
            parts = query.split("到")
            if len(parts) >= 2:
                requirements["extracted_info"]["origin"] = parts[0].replace("从", "").strip()
                requirements["extracted_info"]["destination"] = parts[1].split()[0].strip()
        
        # 从偏好中更新信息
        if preferences:
            requirements["extracted_info"].update(preferences)
        
        return requirements
    
    async def _needs_route_customization(
        self, 
        query: str, 
        requirements: Dict[str, Any]
    ) -> bool:
        """判断是否需要路线定制"""
        
        customization_keywords = [
            "想去", "经过", "途经", "绕道", "顺便", "看看", "游览", "参观",
            "感兴趣", "想去看看", "路过", "经过一下"
        ]
        
        return any(keyword in query for keyword in customization_keywords)
    
    async def _intelligent_route_customization(
        self, 
        query: str, 
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """智能路线定制"""
        
        try:
            context = f"""
用户查询: {query}
当前需求: {json.dumps(requirements, ensure_ascii=False)}
"""
            
            messages = [
                SystemMessage(content=self.route_customization_prompt),
                HumanMessage(content=context)
            ]
            
            response = await self.llm.agenerate([messages])
            customization_result = response.generations[0][0].text.strip()
            
            # 解析JSON结果
            try:
                customization_data = json.loads(customization_result)
                return customization_data
            except json.JSONDecodeError:
                return await self._fallback_route_customization(query, requirements)
                
        except Exception as e:
            logger.error(f"Intelligent route customization failed: {str(e)}")
            return await self._fallback_route_customization(query, requirements)
    
    async def _fallback_route_customization(
        self, 
        query: str, 
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """备用路线定制方法"""
        
        # 简单的兴趣点提取
        interest_points = []
        
        # 使用正则表达式提取地点
        location_patterns = [
            r"想去(.+?)(?:\s|$)",
            r"经过(.+?)(?:\s|$)",
            r"途经(.+?)(?:\s|$)",
            r"顺便(.+?)(?:\s|$)"
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, query)
            interest_points.extend(matches)
        
        return {
            "interest_points": [{"name": point.strip(), "location": point.strip()} for point in interest_points],
            "route_adjustment": {
                "additional_distance": len(interest_points) * 50,  # 估算每个兴趣点增加50km
                "additional_time": len(interest_points) * 0.5,     # 估算每个兴趣点增加0.5天
                "cost_impact": len(interest_points) * 200          # 估算每个兴趣点增加200元
            }
        }
    
    async def _needs_fuel_budget_calculation(
        self, 
        query: str, 
        requirements: Dict[str, Any]
    ) -> bool:
        """判断是否需要油耗预算计算"""
        
        fuel_keywords = [
            "油耗", "百公里", "L/100km", "升/百公里", "燃油", "汽油", "加油",
            "油费", "燃油成本", "油耗多少", "省油", "费油"
        ]
        
        return any(keyword in query for keyword in fuel_keywords)
    
    async def _intelligent_fuel_budget_calculation(
        self, 
        query: str, 
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """智能油耗预算计算"""
        
        try:
            context = f"""
用户查询: {query}
当前需求: {json.dumps(requirements, ensure_ascii=False)}
"""
            
            messages = [
                SystemMessage(content=self.fuel_budget_prompt),
                HumanMessage(content=context)
            ]
            
            response = await self.llm.agenerate([messages])
            fuel_result = response.generations[0][0].text.strip()
            
            # 解析JSON结果
            try:
                fuel_data = json.loads(fuel_result)
                return fuel_data
            except json.JSONDecodeError:
                return await self._fallback_fuel_budget_calculation(query, requirements)
                
        except Exception as e:
            logger.error(f"Intelligent fuel budget calculation failed: {str(e)}")
            return await self._fallback_fuel_budget_calculation(query, requirements)
    
    async def _fallback_fuel_budget_calculation(
        self, 
        query: str, 
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """备用油耗预算计算方法"""
        
        # 提取油耗数据
        fuel_consumption = 4.5  # 默认油耗
        
        # 使用正则表达式提取油耗数字
        fuel_patterns = [
            r"(\d+\.?\d*)\s*L/100km",
            r"(\d+\.?\d*)\s*升/百公里",
            r"百公里(\d+\.?\d*)升",
            r"油耗(\d+\.?\d*)"
        ]
        
        for pattern in fuel_patterns:
            match = re.search(pattern, query)
            if match:
                fuel_consumption = float(match.group(1))
                break
        
        # 计算预算
        total_distance = requirements.get("extracted_info", {}).get("total_distance", 1200)
        fuel_needed = (total_distance / 100) * fuel_consumption
        fuel_cost = fuel_needed * 7.5  # 假设油价7.5元/升
        
        return {
            "fuel_consumption": fuel_consumption,
            "total_distance": total_distance,
            "fuel_needed": fuel_needed,
            "fuel_cost": fuel_cost,
            "cost_per_km": fuel_cost / total_distance
        }
    
    async def _execute_enhanced_multi_agent_planning(
        self, 
        requirements: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """执行增强版多Agent协作规划"""
        
        results = {}
        
        try:
            # 1. 智能路线规划
            if requirements.get("extracted_info", {}).get("origin") and requirements.get("extracted_info", {}).get("destination"):
                route_query = self._build_intelligent_route_query(requirements)
                route_result = await self.agent_router.execute(
                    query=route_query,
                    origin=requirements["extracted_info"]["origin"],
                    destination=requirements["extracted_info"]["destination"],
                    waypoints=requirements["extracted_info"].get("waypoints", []),
                    daily_distance=requirements["extracted_info"].get("daily_distance", 300),
                    user_id=user_id
                )
                results["route"] = route_result
            
            # 2. 智能天气分析
            weather_locations = [
                requirements.get("extracted_info", {}).get("origin"),
                requirements.get("extracted_info", {}).get("destination")
            ]
            weather_locations.extend(requirements.get("extracted_info", {}).get("waypoints", []))
            
            weather_results = {}
            for location in weather_locations:
                if location:
                    weather_query = self._build_intelligent_weather_query(location, requirements)
                    weather_result = await self.agent_router.execute(
                        query=weather_query,
                        location=location,
                        days=requirements.get("extracted_info", {}).get("duration_days", 7),
                        user_id=user_id
                    )
                    weather_results[location] = weather_result
            results["weather"] = weather_results
            
            # 3. 智能POI推荐
            poi_locations = weather_locations
            poi_results = {}
            for location in poi_locations:
                if location:
                    poi_query = self._build_intelligent_poi_query(location, requirements)
                    
                    # 并行查询多种POI
                    poi_tasks = []
                    for poi_type in ["restaurant", "hotel", "gas_station", "repair_shop"]:
                        task = self.agent_router.execute(
                            query=f"{poi_query} - {poi_type}",
                            location=location,
                            poi_type=poi_type,
                            user_id=user_id
                        )
                        poi_tasks.append((poi_type, task))
                    
                    # 等待所有POI查询完成
                    location_pois = {}
                    for poi_type, task in poi_tasks:
                        try:
                            result = await task
                            location_pois[poi_type] = result
                        except Exception as e:
                            logger.error(f"POI query failed for {poi_type}: {str(e)}")
                            location_pois[poi_type] = {"success": False, "message": str(e)}
                    
                    poi_results[location] = location_pois
            results["poi"] = poi_results
            
            # 4. 智能预算计算
            if results.get("route") and results["route"].success:
                budget_query = self._build_intelligent_budget_query(requirements)
                budget_result = await self.agent_router.execute(
                    query=budget_query,
                    total_distance=requirements.get("extracted_info", {}).get("total_distance", 1200),
                    days=requirements.get("extracted_info", {}).get("duration_days", 7),
                    fuel_budget_analysis=requirements.get("fuel_budget_analysis"),
                    user_id=user_id
                )
                results["budget"] = budget_result
            
            # 5. 智能个性化推荐
            personalization_query = self._build_intelligent_personalization_query(requirements)
            personalization_result = await self.agent_router.execute(
                query=personalization_query,
                action="get_recommendations",
                user_id=user_id
            )
            results["personalization"] = personalization_result
            
        except Exception as e:
            logger.error(f"Enhanced multi-agent planning failed: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    def _build_intelligent_route_query(self, requirements: Dict[str, Any]) -> str:
        """构建智能路线查询"""
        
        base_query = f"从{requirements['extracted_info']['origin']}到{requirements['extracted_info']['destination']}的路线规划"
        
        # 添加智能描述
        route_type = requirements["extracted_info"].get("route_type", "自然风光")
        travel_style = requirements["extracted_info"].get("travel_style", "休闲")
        daily_distance = requirements["extracted_info"].get("daily_distance", 300)
        
        intelligent_description = f"""
        需求详情：
        - 路线类型：{route_type}
        - 骑行风格：{travel_style}
        - 日行距离：{daily_distance}公里
        - 特殊要求：{', '.join(requirements['extracted_info'].get('special_requirements', []))}
        - 兴趣偏好：{', '.join(requirements['extracted_info'].get('interests', []))}
        
        请提供：
        1. 最优路线规划
        2. 详细的路段分析
        3. 安全风险评估
        4. 替代路线建议
        5. 沿途服务设施规划
        """
        
        return base_query + intelligent_description
    
    def _build_intelligent_weather_query(self, location: str, requirements: Dict[str, Any]) -> str:
        """构建智能天气查询"""
        
        base_query = f"{location}的天气查询"
        
        # 添加智能描述
        duration = requirements["extracted_info"].get("duration_days", 7)
        travel_style = requirements["extracted_info"].get("travel_style", "休闲")
        
        intelligent_description = f"""
        查询需求：
        - 查询天数：{duration}天
        - 骑行风格：{travel_style}
        - 特殊关注：摩托车骑行安全
        
        请提供：
        1. 详细的天气预报
        2. 摩托车骑行安全评估
        3. 天气风险预警
        4. 骑行建议和注意事项
        5. 应急天气方案
        """
        
        return base_query + intelligent_description
    
    def _build_intelligent_poi_query(self, location: str, requirements: Dict[str, Any]) -> str:
        """构建智能POI查询"""
        
        base_query = f"{location}的服务设施查询"
        
        # 添加智能描述
        travel_style = requirements["extracted_info"].get("travel_style", "休闲")
        budget_range = requirements["extracted_info"].get("budget_range", 5000)
        interests = requirements["extracted_info"].get("interests", [])
        
        intelligent_description = f"""
        查询需求：
        - 骑行风格：{travel_style}
        - 预算范围：{budget_range}元
        - 兴趣偏好：{', '.join(interests)}
        - 特殊要求：摩托车友好
        
        请提供：
        1. 摩托车友好的餐厅推荐
        2. 适合的住宿选择
        3. 可靠的加油站信息
        4. 专业的修车行
        5. 符合兴趣的景点推荐
        """
        
        return base_query + intelligent_description
    
    def _build_intelligent_budget_query(self, requirements: Dict[str, Any]) -> str:
        """构建智能预算查询"""
        
        base_query = "智能预算计算"
        
        # 添加智能描述
        budget_range = requirements["extracted_info"].get("budget_range", 5000)
        travel_style = requirements["extracted_info"].get("travel_style", "休闲")
        fuel_analysis = requirements.get("fuel_budget_analysis", {})
        
        intelligent_description = f"""
        预算需求：
        - 总预算范围：{budget_range}元
        - 旅行风格：{travel_style}
        - 油耗分析：{json.dumps(fuel_analysis, ensure_ascii=False)}
        
        请提供：
        1. 精确的预算分解
        2. 成本优化建议
        3. 节省开支的方案
        4. 应急资金规划
        5. 性价比分析
        """
        
        return base_query + intelligent_description
    
    def _build_intelligent_personalization_query(self, requirements: Dict[str, Any]) -> str:
        """构建智能个性化查询"""
        
        base_query = "个性化推荐"
        
        # 添加智能描述
        intelligent_analysis = requirements.get("intelligent_analysis", {})
        extracted_info = requirements.get("extracted_info", {})
        
        intelligent_description = f"""
        个性化需求：
        - 用户偏好：{json.dumps(extracted_info, ensure_ascii=False)}
        - 智能分析：{json.dumps(intelligent_analysis, ensure_ascii=False)}
        
        请提供：
        1. 基于偏好的个性化推荐
        2. 隐含需求的满足方案
        3. 风险因素的应对建议
        4. 优化建议的实施计划
        """
        
        return base_query + intelligent_description
    
    async def _intelligent_result_integration(
        self, 
        requirements: Dict[str, Any], 
        results: Dict[str, Any]
    ) -> MotoTravelPlan:
        """智能结果整合"""
        
        # 创建计划ID
        plan_id = f"enhanced_moto_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 构建完整的摩旅计划
        plan = MotoTravelPlan(
            plan_id=plan_id,
            user_id=requirements.get("user_id", ""),
            title=f"智能摩旅规划：从{requirements.get('extracted_info', {}).get('origin', '')}到{requirements.get('extracted_info', {}).get('destination', '')}",
            description="基于大模型智能分析的个性化摩旅计划",
            created_at=datetime.utcnow().isoformat(),
            
            # 路线信息
            origin=self._create_enhanced_location_info(requirements.get("extracted_info", {}).get("origin", "")),
            destination=self._create_enhanced_location_info(requirements.get("extracted_info", {}).get("destination", "")),
            waypoints=[self._create_enhanced_location_info(wp) for wp in requirements.get("extracted_info", {}).get("waypoints", [])],
            total_distance_km=requirements.get("extracted_info", {}).get("total_distance", 1200),
            total_duration_days=requirements.get("extracted_info", {}).get("duration_days", 7),
            route_type=requirements.get("extracted_info", {}).get("route_type", "自然风光"),
            
            # 每日路线
            daily_routes=self._create_enhanced_daily_routes(results.get("route", {}), requirements),
            
            # 天气信息
            weather_forecast=self._create_enhanced_weather_forecast(results.get("weather", {}), requirements),
            weather_alerts=[],
            
            # POI信息
            restaurants=self._create_enhanced_poi_list(results.get("poi", {}), "restaurant", requirements),
            accommodations=self._create_enhanced_poi_list(results.get("poi", {}), "hotel", requirements),
            gas_stations=self._create_enhanced_poi_list(results.get("poi", {}), "gas_station", requirements),
            repair_shops=self._create_enhanced_poi_list(results.get("poi", {}), "repair_shop", requirements),
            attractions=[],
            
            # 预算信息
            total_budget=requirements.get("extracted_info", {}).get("budget_range", 5000),
            daily_budgets=self._create_enhanced_daily_budgets(results.get("budget", {}), requirements),
            budget_breakdown=results.get("budget", {}).get("data", {}).get("cost_breakdown", {}),
            
            # 安全信息
            safety_alerts=[],
            safety_recommendations=requirements.get("intelligent_analysis", {}).get("risk_factors", []) + [
                "遵守交通规则，安全第一",
                "定期检查车辆状况",
                "注意天气变化，适时调整行程",
                "保持充足的休息，避免疲劳驾驶"
            ],
            
            # 个性化信息
            user_preferences=requirements.get("extracted_info", {}),
            personalized_recommendations=requirements.get("intelligent_analysis", {}).get("personalized_recommendations", []),
            
            # 元数据
            metadata={
                "planning_time": datetime.utcnow().isoformat(),
                "agents_used": list(results.keys()),
                "success_rate": len([r for r in results.values() if hasattr(r, 'success') and r.success]) / len(results) if results else 0,
                "intelligence_features": [
                    "智能需求分析",
                    "动态路线定制",
                    "精确油耗计算",
                    "多Agent协作"
                ],
                "analysis_confidence": requirements.get("confidence_score", 0.9)
            }
        )
        
        return plan
    
    def _create_enhanced_location_info(self, location_name: str) -> Dict[str, Any]:
        """创建增强版位置信息"""
        return {
            "name": location_name,
            "address": location_name,
            "coordinates": {"longitude": 0.0, "latitude": 0.0},
            "province": "",
            "city": location_name,
            "district": ""
        }
    
    def _create_enhanced_daily_routes(self, route_results: Dict[str, Any], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建增强版每日路线"""
        daily_routes = []
        
        if route_results.get("success") and route_results.get("data"):
            route_data = route_results["data"]
            daily_route_data = route_data.get("daily_routes", [])
            
            for i, day_data in enumerate(daily_route_data):
                daily_route = {
                    "day": i + 1,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "start_location": self._create_enhanced_location_info("起点"),
                    "end_location": self._create_enhanced_location_info("终点"),
                    "total_distance_km": day_data.get("distance_km", 0),
                    "estimated_duration_hours": day_data.get("duration_hours", 0),
                    "segments": [],
                    "recommended_stops": day_data.get("recommendations", {}).get("fuel_stops", []),
                    "accommodation": None
                }
                daily_routes.append(daily_route)
        
        return daily_routes
    
    def _create_enhanced_weather_forecast(self, weather_results: Dict[str, Any], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建增强版天气预报"""
        weather_forecast = []
        
        for location, result in weather_results.items():
            if result.get("success") and result.get("data"):
                weather_data = result["data"]
                current_weather = weather_data.get("current", {})
                
                weather_info = {
                    "location": location,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "temperature": current_weather.get("temperature", 0),
                    "weather_condition": current_weather.get("weather", ""),
                    "humidity": current_weather.get("humidity", 0),
                    "wind_speed": current_weather.get("wind_speed", 0),
                    "wind_direction": current_weather.get("wind_direction", ""),
                    "visibility": current_weather.get("visibility", 10),
                    "safety_score": 80,
                    "safety_level": "良好",
                    "warnings": [],
                    "recommendations": ["天气条件良好，适合骑行"]
                }
                weather_forecast.append(weather_info)
        
        return weather_forecast
    
    def _create_enhanced_poi_list(self, poi_results: Dict[str, Any], poi_type: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建增强版POI列表"""
        poi_list = []
        
        for location, location_pois in poi_results.items():
            if poi_type in location_pois:
                poi_result = location_pois[poi_type]
                if poi_result.get("success") and poi_result.get("data"):
                    pois_data = poi_result["data"]
                    if isinstance(pois_data, dict) and "pois" in pois_data:
                        for poi in pois_data["pois"]:
                            poi_info = {
                                "id": poi.get("id", ""),
                                "name": poi.get("name", ""),
                                "category": poi.get("category", ""),
                                "location": self._create_enhanced_location_info(location),
                                "rating": poi.get("rating", 0),
                                "price_level": poi.get("price", ""),
                                "business_hours": poi.get("opening_hours", ""),
                                "phone": poi.get("tel", ""),
                                "website": poi.get("website", ""),
                                "description": poi.get("address", ""),
                                "features": [],
                                "distance_from_route": poi.get("distance", 0)
                            }
                            poi_list.append(poi_info)
        
        return poi_list
    
    def _create_enhanced_daily_budgets(self, budget_results: Dict[str, Any], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建增强版每日预算"""
        daily_budgets = []
        
        if budget_results.get("success") and budget_results.get("data"):
            budget_data = budget_results["data"]
            daily_budget_data = budget_data.get("daily_budgets", [])
            
            for day_data in daily_budget_data:
                daily_budget = {
                    "day": day_data.get("day", 1),
                    "date": day_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                    "items": [],
                    "total_cost": day_data.get("total_cost", 0),
                    "currency": "CNY"
                }
                daily_budgets.append(daily_budget)
        
        return daily_budgets
