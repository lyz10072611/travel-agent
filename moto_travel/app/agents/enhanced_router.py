"""
增强版Agent路由器
包含详细的工具调用描述和智能意图识别
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import re
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent, AgentResponse, AgentType
from app.agents.route_agent import RouteAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.poi_agent import POIAgent
from app.agents.search_agent import SearchAgent
from app.agents.attraction_agent import AttractionAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.personalization_agent import PersonalizationAgent
from app.config import settings
from loguru import logger


class EnhancedAgentRouter(BaseAgent):
    """增强版Agent路由器 - 智能意图识别和工具调用"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.ROUTE,
            name="enhanced_agent_router",
            description="增强版智能Agent路由器，具备强大的意图识别和工具调用能力"
        )
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model_name=settings.qwen_model,
            openai_api_key=settings.qwen_api_key,
            openai_api_base=settings.qwen_base_url,
            temperature=0.1,
            max_tokens=2000
        )
        
        # 注册所有Agent
        self.agents = {
            AgentType.ROUTE: RouteAgent(),
            AgentType.WEATHER: WeatherAgent(),
            AgentType.POI: POIAgent(),
            AgentType.SEARCH: SearchAgent(),
            AgentType.ATTRACTION: AttractionAgent(),
            AgentType.BUDGET: BudgetAgent(),
            AgentType.PERSONALIZATION: PersonalizationAgent()
        }
        
        # 智能意图识别提示词
        self.intent_recognition_prompt = """
您是一个专业的摩旅智能助手意图识别专家，具备以下核心能力：

## 🧠 智能意图识别能力
1. **深度语义理解**: 理解用户自然语言表达的深层意图
2. **上下文感知**: 结合对话历史和用户偏好进行意图分析
3. **多意图识别**: 识别复合意图和多重需求
4. **个性化适配**: 根据用户特征调整意图识别策略

## 🎯 可识别的意图类型

### 1. 路线规划意图 (route)
**触发关键词**: 路线、导航、路径、怎么走、从...到、途经、规划路线
**用户表达示例**:
- "从北京到上海的路线规划"
- "我想去西藏，帮我规划路线"
- "途经成都的摩旅路线"
- "不走高速的风景路线"

**工具调用描述**:
```
调用路线规划Agent，使用高德地图API进行智能路线规划：
• 地理编码：将起点终点转换为精确坐标
• 路线计算：基于摩托车特性选择最优路线
• 分段规划：根据日行距离合理分段
• 安全评估：评估路线安全性和难度
• 服务规划：沿途加油站、修车行、住宿点规划
```

### 2. 天气查询意图 (weather)
**触发关键词**: 天气、温度、下雨、下雪、风力、预报、气象、气候
**用户表达示例**:
- "北京未来几天的天气怎么样"
- "路上会下雨吗"
- "风力大不大，适合骑行吗"
- "温度太低，需要什么装备"

**工具调用描述**:
```
调用天气查询Agent，使用和风天气API进行安全分析：
• 实时天气：获取当前天气状况和关键指标
• 逐时预报：24小时精确天气预报
• 安全评估：基于天气条件评估骑行安全性
• 装备建议：根据天气推荐必要防护装备
• 风险预警：识别影响骑行的危险天气因素
```

### 3. POI服务意图 (poi)
**触发关键词**: 餐厅、酒店、住宿、加油站、修车、医院、药店、银行
**用户表达示例**:
- "路上有什么好吃的餐厅"
- "推荐几个摩托车友好的酒店"
- "哪里有24小时加油站"
- "附近有修车行吗"

**工具调用描述**:
```
调用POI服务Agent，智能推荐摩旅服务设施：
• 餐厅搜索：推荐摩托车友好、停车便利的餐厅
• 住宿查询：筛选摩托车友好、安全可靠的酒店
• 加油站：规划加油点，确保燃油充足
• 修车行：识别专业摩托车维修服务
• 医疗设施：查找沿途医院、诊所等医疗保障
```

### 4. 政策搜索意图 (search)
**触发关键词**: 政策、限行、禁行、规定、法规、路况、施工、封路
**用户表达示例**:
- "摩托车能上高速吗"
- "这个城市有限行政策吗"
- "路上有施工封路吗"
- "野生动物出没预警"

**工具调用描述**:
```
调用网页搜索Agent，获取政策和安全信息：
• 政策查询：搜索摩托车相关限行和通行政策
• 路况信息：获取实时路况和施工信息
• 安全预警：搜索野生动物出没和安全提醒
• 装备推荐：搜索摩旅装备和准备建议
• 法规解读：解读相关交通法规和限制
```

### 5. 景点推荐意图 (attraction)
**触发关键词**: 景点、景区、旅游、风景、名胜、古迹、公园、博物馆
**用户表达示例**:
- "沿途有什么好玩的景点"
- "推荐几个值得去的风景点"
- "有什么历史文化景点"
- "适合拍照的地方"

**工具调用描述**:
```
调用景点推荐Agent，推荐个性化旅游景点：
• 景点搜索：基于用户兴趣推荐相关景点
• 路线集成：将景点合理融入摩旅路线
• 时间规划：为每个景点安排合适的游览时间
• 体验优化：提供深度游览和拍照建议
• 文化解读：介绍景点历史文化和特色
```

### 6. 预算计算意图 (budget)
**触发关键词**: 预算、费用、花费、成本、多少钱、价格、收费、开销
**用户表达示例**:
- "这次旅行大概要花多少钱"
- "帮我算算预算"
- "我的车油耗4.5L/100km，油费多少"
- "住宿和餐饮费用怎么安排"

**工具调用描述**:
```
调用预算计算Agent，进行精确的摩旅成本分析：
• 燃油计算：基于实际油耗和油价计算燃油费用
• 住宿预算：根据偏好和地区价格计算住宿成本
• 餐饮规划：考虑当地消费水平规划餐饮预算
• 维护费用：包含车辆保养、维修、保险等费用
• 应急资金：预留意外支出和应急处理费用
• 成本优化：提供节省开支的实用建议
```

### 7. 个性化定制意图 (personalization)
**触发关键词**: 偏好、喜欢、习惯、个性化、定制、个人、我的
**用户表达示例**:
- "我喜欢自然风光路线"
- "我的日行距离不超过400公里"
- "帮我保存这些偏好"
- "根据我的习惯推荐"

**工具调用描述**:
```
调用个性化定制Agent，提供个性化服务：
• 偏好分析：分析用户的历史偏好和习惯
• 记忆管理：保存和管理用户个性化信息
• 智能推荐：基于偏好提供个性化推荐
• 行为分析：分析用户行为模式和改进建议
• 定制服务：根据个人需求定制专属服务
```

## 🎯 意图识别任务
请分析用户输入，识别主要意图和次要意图，返回JSON格式结果：

```json
{
  "primary_intent": "主要意图类型",
  "secondary_intents": ["次要意图1", "次要意图2"],
  "confidence_score": 0.95,
  "extracted_entities": {
    "locations": ["地点1", "地点2"],
    "dates": ["日期1", "日期2"],
    "numbers": ["数字1", "数字2"],
    "keywords": ["关键词1", "关键词2"]
  },
  "tool_call_description": "详细的工具调用描述",
  "reasoning": "意图识别的推理过程"
}
```

请基于用户输入进行深度分析，确保意图识别的准确性。
"""
        
        # 系统提示词
        self.system_prompt = """
您是一个智能的摩旅助手路由器，负责分析用户请求并路由到合适的Agent。

可用的Agent类型：
1. route - 路线规划：处理路线规划、导航、路径计算等
2. weather - 天气查询：处理天气查询、预报、预警等
3. poi - POI服务：处理餐饮、住宿、修车、加油站等本地服务
4. search - 网页搜索：处理政策查询、路况信息、安全信息等
5. attraction - 景点推荐：处理景点推荐、旅游信息等
6. budget - 预算计算：处理费用计算、预算规划等
7. personalization - 个性化定制：处理用户偏好、个性化设置等

请分析用户请求，返回最合适的Agent类型。如果请求涉及多个Agent，返回主要的一个。
只返回Agent类型名称，不要其他内容。
"""
    
    async def execute(self, **kwargs) -> AgentResponse:
        """执行增强版路由逻辑"""
        query = kwargs.get("query", "")
        user_id = kwargs.get("user_id")
        conversation_history = kwargs.get("conversation_history", [])
        
        if not query:
            return self._create_error_response("用户查询不能为空")
        
        try:
            # 1. 智能意图识别
            intent_analysis = await self._intelligent_intent_recognition(
                query, conversation_history
            )
            
            # 2. 工具调用描述生成
            tool_call_description = await self._generate_tool_call_description(
                intent_analysis, query
            )
            
            # 3. 路由到对应Agent
            primary_intent = intent_analysis.get("primary_intent")
            if primary_intent in self.agents:
                agent = self.agents[primary_intent]
                logger.info(f"Routing to {primary_intent.value} agent for query: {query}")
                
                # 将用户ID和工具调用描述传递给Agent
                kwargs["user_id"] = user_id
                kwargs["tool_call_description"] = tool_call_description
                kwargs["intent_analysis"] = intent_analysis
                
                result = await agent.execute(**kwargs)
                
                return self._create_success_response(
                    data=result.to_dict(),
                    message=f"已智能路由到{primary_intent.value}Agent",
                    metadata={
                        "routed_agent": primary_intent.value,
                        "intent_analysis": intent_analysis,
                        "tool_call_description": tool_call_description,
                        "original_query": query,
                        "confidence_score": intent_analysis.get("confidence_score", 0.9)
                    }
                )
            else:
                return self._create_error_response(f"无法识别请求意图: {query}")
                
        except Exception as e:
            logger.error(f"Enhanced agent routing failed: {str(e)}")
            return self._create_error_response(f"智能路由失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        return self._validate_required_params(["query"], **kwargs)
    
    async def _intelligent_intent_recognition(
        self, 
        query: str, 
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """智能意图识别"""
        
        try:
            # 构建上下文
            context = f"""
用户当前查询: {query}
对话历史: {json.dumps(conversation_history[-3:], ensure_ascii=False)}
"""
            
            messages = [
                SystemMessage(content=self.intent_recognition_prompt),
                HumanMessage(content=context)
            ]
            
            response = await self.llm.agenerate([messages])
            intent_result = response.generations[0][0].text.strip()
            
            # 解析JSON结果
            try:
                intent_data = json.loads(intent_result)
                return intent_data
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用备用方法
                return await self._fallback_intent_recognition(query)
                
        except Exception as e:
            logger.error(f"Intelligent intent recognition failed: {str(e)}")
            return await self._fallback_intent_recognition(query)
    
    async def _fallback_intent_recognition(self, query: str) -> Dict[str, Any]:
        """备用意图识别方法"""
        
        # 意图关键词映射
        intent_keywords = {
            AgentType.ROUTE: [
                "路线", "导航", "路径", "怎么走", "从", "到", "途经", "规划路线",
                "路线规划", "导航", "路径规划", "摩旅路线"
            ],
            AgentType.WEATHER: [
                "天气", "温度", "下雨", "下雪", "风力", "预报", "气象", "气候",
                "晴天", "阴天", "暴雨", "大风", "能见度"
            ],
            AgentType.POI: [
                "餐厅", "酒店", "住宿", "加油站", "修车", "医院", "药店", "银行",
                "ATM", "美食", "吃饭", "住宿", "加油", "维修", "医疗"
            ],
            AgentType.SEARCH: [
                "政策", "限行", "禁行", "规定", "法规", "路况", "施工", "封路",
                "野生动物", "安全", "装备", "推荐"
            ],
            AgentType.ATTRACTION: [
                "景点", "景区", "旅游", "风景", "名胜", "古迹", "公园", "博物馆",
                "推荐", "好玩", "值得去", "打卡"
            ],
            AgentType.BUDGET: [
                "预算", "费用", "花费", "成本", "多少钱", "价格", "收费", "开销",
                "经济", "省钱", "花费", "预算规划"
            ],
            AgentType.PERSONALIZATION: [
                "偏好", "喜欢", "习惯", "个性化", "定制", "个人", "我的", "偏好设置"
            ]
        }
        
        query_lower = query.lower()
        intent_scores = {}
        
        for agent_type, keywords in intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            if score > 0:
                intent_scores[agent_type] = score
        
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            return {
                "primary_intent": primary_intent,
                "secondary_intents": [],
                "confidence_score": 0.8,
                "extracted_entities": {
                    "locations": [],
                    "dates": [],
                    "numbers": [],
                    "keywords": []
                },
                "tool_call_description": f"调用{primary_intent.value}Agent处理用户请求",
                "reasoning": "基于关键词匹配的意图识别"
            }
        
        return {
            "primary_intent": AgentType.ROUTE,
            "secondary_intents": [],
            "confidence_score": 0.5,
            "extracted_entities": {
                "locations": [],
                "dates": [],
                "numbers": [],
                "keywords": []
            },
            "tool_call_description": "调用路线规划Agent作为默认处理",
            "reasoning": "未识别到明确意图，使用默认路由"
        }
    
    async def _generate_tool_call_description(
        self, 
        intent_analysis: Dict[str, Any], 
        query: str
    ) -> str:
        """生成工具调用描述"""
        
        primary_intent = intent_analysis.get("primary_intent")
        confidence_score = intent_analysis.get("confidence_score", 0.9)
        
        if primary_intent == AgentType.ROUTE:
            return f"""
🗺️ 调用路线规划Agent - 智能路线规划服务
【识别置信度】: {confidence_score:.2f}
【用户需求】: {query}
【工具功能】:
• 地理编码：将起点终点转换为精确坐标
• 路线计算：基于摩托车特性选择最优路线  
• 分段规划：根据日行距离合理分段
• 安全评估：评估路线安全性和难度
• 服务规划：沿途加油站、修车行、住宿点规划
【预期输出】: 详细的摩旅路线规划方案
"""
        
        elif primary_intent == AgentType.WEATHER:
            return f"""
🌤️ 调用天气查询Agent - 摩旅安全天气分析
【识别置信度】: {confidence_score:.2f}
【用户需求】: {query}
【工具功能】:
• 实时天气：获取当前天气状况和关键指标
• 逐时预报：24小时精确天气预报
• 安全评估：基于天气条件评估骑行安全性
• 装备建议：根据天气推荐必要防护装备
• 风险预警：识别影响骑行的危险天气因素
【预期输出】: 详细的天气分析和安全建议
"""
        
        elif primary_intent == AgentType.POI:
            return f"""
🏪 调用POI服务Agent - 摩旅服务设施推荐
【识别置信度】: {confidence_score:.2f}
【用户需求】: {query}
【工具功能】:
• 餐厅搜索：推荐摩托车友好、停车便利的餐厅
• 住宿查询：筛选摩托车友好、安全可靠的酒店
• 加油站：规划加油点，确保燃油充足
• 修车行：识别专业摩托车维修服务
• 医疗设施：查找沿途医院、诊所等医疗保障
【预期输出】: 个性化的服务设施推荐列表
"""
        
        elif primary_intent == AgentType.SEARCH:
            return f"""
🔍 调用网页搜索Agent - 政策和安全信息查询
【识别置信度】: {confidence_score:.2f}
【用户需求】: {query}
【工具功能】:
• 政策查询：搜索摩托车相关限行和通行政策
• 路况信息：获取实时路况和施工信息
• 安全预警：搜索野生动物出没和安全提醒
• 装备推荐：搜索摩旅装备和准备建议
• 法规解读：解读相关交通法规和限制
【预期输出】: 相关的政策法规和安全信息
"""
        
        elif primary_intent == AgentType.ATTRACTION:
            return f"""
🎯 调用景点推荐Agent - 个性化旅游景点推荐
【识别置信度】: {confidence_score:.2f}
【用户需求】: {query}
【工具功能】:
• 景点搜索：基于用户兴趣推荐相关景点
• 路线集成：将景点合理融入摩旅路线
• 时间规划：为每个景点安排合适的游览时间
• 体验优化：提供深度游览和拍照建议
• 文化解读：介绍景点历史文化和特色
【预期输出】: 个性化的景点推荐和游览方案
"""
        
        elif primary_intent == AgentType.BUDGET:
            return f"""
💰 调用预算计算Agent - 精确摩旅成本分析
【识别置信度】: {confidence_score:.2f}
【用户需求】: {query}
【工具功能】:
• 燃油计算：基于实际油耗和油价计算燃油费用
• 住宿预算：根据偏好和地区价格计算住宿成本
• 餐饮规划：考虑当地消费水平规划餐饮预算
• 维护费用：包含车辆保养、维修、保险等费用
• 应急资金：预留意外支出和应急处理费用
• 成本优化：提供节省开支的实用建议
【预期输出】: 详细的预算分析和成本优化建议
"""
        
        elif primary_intent == AgentType.PERSONALIZATION:
            return f"""
🎨 调用个性化定制Agent - 个性化服务定制
【识别置信度】: {confidence_score:.2f}
【用户需求】: {query}
【工具功能】:
• 偏好分析：分析用户的历史偏好和习惯
• 记忆管理：保存和管理用户个性化信息
• 智能推荐：基于偏好提供个性化推荐
• 行为分析：分析用户行为模式和改进建议
• 定制服务：根据个人需求定制专属服务
【预期输出】: 个性化的服务定制和推荐方案
"""
        
        else:
            return f"""
🤖 调用默认Agent - 通用摩旅服务
【识别置信度】: {confidence_score:.2f}
【用户需求】: {query}
【工具功能】: 提供通用的摩旅规划和建议服务
【预期输出】: 基础的摩旅服务响应
"""
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取所有Agent状态"""
        status = {}
        for agent_type, agent in self.agents.items():
            status[agent_type.value] = agent.get_capabilities()
        return status
    
    def get_available_agents(self) -> List[str]:
        """获取可用的Agent列表"""
        return [agent_type.value for agent_type in self.agents.keys()]
    
    async def execute_multi_agent(
        self, 
        query: str, 
        agent_types: List[AgentType], 
        **kwargs
    ) -> Dict[str, AgentResponse]:
        """执行多个Agent"""
        results = {}
        
        for agent_type in agent_types:
            if agent_type in self.agents:
                agent = self.agents[agent_type]
                try:
                    result = await agent.execute(query=query, **kwargs)
                    results[agent_type.value] = result
                except Exception as e:
                    logger.error(f"Multi-agent execution failed for {agent_type.value}: {str(e)}")
                    results[agent_type.value] = self._create_error_response(f"执行失败: {str(e)}")
        
        return results
