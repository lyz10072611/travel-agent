"""
Agent路由器
负责将用户请求路由到合适的Agent
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
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


class AgentRouter(BaseAgent):
    """Agent路由器"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.ROUTE,  # 使用ROUTE作为默认类型
            name="agent_router",
            description="智能Agent路由器，负责将用户请求路由到合适的Agent"
        )
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model_name=settings.qwen_model,
            openai_api_key=settings.qwen_api_key,
            openai_api_base=settings.qwen_base_url,
            temperature=0.1
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
        
        # 意图关键词映射
        self.intent_keywords = {
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
        
        # 系统提示词
        self.system_prompt = """
你是一个智能的摩旅助手路由器，负责分析用户请求并路由到合适的Agent。

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
        """执行路由逻辑"""
        user_query = kwargs.get("query", "")
        user_id = kwargs.get("user_id")
        
        if not user_query:
            return self._create_error_response("用户查询不能为空")
        
        try:
            # 1. 使用LLM进行意图识别
            llm_intent = await self._classify_intent_with_llm(user_query)
            
            # 2. 使用关键词匹配作为备选
            keyword_intent = self._classify_intent_with_keywords(user_query)
            
            # 3. 综合判断最终意图
            final_intent = self._resolve_intent(llm_intent, keyword_intent, user_query)
            
            # 4. 路由到对应Agent
            if final_intent in self.agents:
                agent = self.agents[final_intent]
                logger.info(f"Routing to {final_intent.value} agent for query: {user_query}")
                
                # 将用户ID传递给Agent
                kwargs["user_id"] = user_id
                result = await agent.execute(**kwargs)
                
                return self._create_success_response(
                    data=result.to_dict(),
                    message=f"已路由到{final_intent.value}Agent",
                    metadata={
                        "routed_agent": final_intent.value,
                        "llm_intent": llm_intent,
                        "keyword_intent": keyword_intent,
                        "original_query": user_query
                    }
                )
            else:
                return self._create_error_response(f"无法识别请求意图: {user_query}")
                
        except Exception as e:
            logger.error(f"Agent routing failed: {str(e)}")
            return self._create_error_response(f"路由失败: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        return self._validate_required_params(["query"], **kwargs)
    
    async def _classify_intent_with_llm(self, query: str) -> Optional[AgentType]:
        """使用LLM进行意图分类"""
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"用户请求: {query}")
            ]
            
            response = await self.llm.agenerate([messages])
            intent_text = response.generations[0][0].text.strip().lower()
            
            # 映射到AgentType
            intent_mapping = {
                "route": AgentType.ROUTE,
                "weather": AgentType.WEATHER,
                "poi": AgentType.POI,
                "search": AgentType.SEARCH,
                "attraction": AgentType.ATTRACTION,
                "budget": AgentType.BUDGET,
                "personalization": AgentType.PERSONALIZATION
            }
            
            return intent_mapping.get(intent_text)
            
        except Exception as e:
            logger.error(f"LLM intent classification failed: {str(e)}")
            return None
    
    def _classify_intent_with_keywords(self, query: str) -> Optional[AgentType]:
        """使用关键词进行意图分类"""
        query_lower = query.lower()
        intent_scores = {}
        
        for agent_type, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            if score > 0:
                intent_scores[agent_type] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return None
    
    def _resolve_intent(
        self, 
        llm_intent: Optional[AgentType], 
        keyword_intent: Optional[AgentType], 
        query: str
    ) -> Optional[AgentType]:
        """解析最终意图"""
        # 如果LLM和关键词识别结果一致，直接返回
        if llm_intent == keyword_intent and llm_intent is not None:
            return llm_intent
        
        # 如果LLM识别成功，优先使用LLM结果
        if llm_intent is not None:
            return llm_intent
        
        # 如果关键词识别成功，使用关键词结果
        if keyword_intent is not None:
            return keyword_intent
        
        # 特殊规则处理
        return self._apply_special_rules(query)
    
    def _apply_special_rules(self, query: str) -> Optional[AgentType]:
        """应用特殊规则"""
        query_lower = query.lower()
        
        # 复合查询规则
        if any(word in query_lower for word in ["路线", "导航", "怎么走"]):
            if any(word in query_lower for word in ["天气", "下雨", "温度"]):
                return AgentType.ROUTE  # 路线规划优先
            elif any(word in query_lower for word in ["预算", "费用", "花费"]):
                return AgentType.ROUTE  # 路线规划优先
        
        # 默认返回路线规划
        return AgentType.ROUTE
    
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
