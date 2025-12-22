"""
LangChain/LangGraph集成
提供Agent编排和工作流管理（适配新架构）
"""
from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, BaseMessage
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langgraph.checkpoint.memory import MemorySaver
from app.agents.route_planning import RoutePlanningAgent
from app.agents.weather import WeatherAgent
from app.agents.poi import POIAgent
from app.config import settings
from loguru import logger


class AgentState(TypedDict):
    """Agent状态定义"""
    messages: List[BaseMessage]
    user_id: str
    query: str
    current_agent: str
    results: Dict[str, Any]
    metadata: Dict[str, Any]


class MotoTravelTool(BaseTool):
    """摩旅工具包装器（适配新架构）"""
    
    def __init__(self):
        super().__init__()
        self.route_agent = RoutePlanningAgent()
        self.weather_agent = WeatherAgent()
        self.poi_agent = POIAgent()
        self.name = "moto_travel_agent"
        self.description = """
        摩旅智能助手工具，可以处理以下类型的请求：
        1. 路线规划 - 规划摩托车旅行路线（集成高德+百度地图）
        2. 天气查询 - 查询天气信息和预警
        3. POI服务 - 查找餐饮、住宿、修车、加油站等服务
        4. 禁摩政策检查 - 检查城市和路线的禁摩政策
        """
    
    def _run(self, query: str, user_id: str = "") -> str:
        """同步执行工具"""
        import asyncio
        return asyncio.run(self._arun(query, user_id))
    
    async def _arun(self, query: str, user_id: str = "") -> str:
        """异步执行工具"""
        try:
            query_lower = query.lower()
            
            # 根据查询内容路由到对应Agent
            if any(keyword in query_lower for keyword in ["路线", "路径", "导航", "从", "到"]):
                # 路线规划
                result = await self.route_agent.execute(query=query, user_id=user_id)
            elif any(keyword in query_lower for keyword in ["天气", "温度", "下雨", "预报"]):
                # 天气查询
                result = await self.weather_agent.execute(query=query, user_id=user_id)
            elif any(keyword in query_lower for keyword in ["餐厅", "酒店", "加油站", "修车", "禁摩", "政策"]):
                # POI查询或政策检查
                result = await self.poi_agent.execute(query=query, user_id=user_id)
            else:
                # 默认使用路线规划
                result = await self.route_agent.execute(query=query, user_id=user_id)
            
            if result.success:
                return f"执行成功: {result.message}\n结果: {result.data}"
            else:
                return f"执行失败: {result.message}"
                
        except Exception as e:
            return f"工具执行出错: {str(e)}"


class LangChainIntegration:
    """LangChain集成类（适配新架构）"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=settings.qwen_model,
            openai_api_key=settings.qwen_api_key,
            openai_api_base=settings.qwen_base_url,
            temperature=0.1
        )
        
        self.moto_travel_tool = MotoTravelTool()
        self.tool_executor = ToolExecutor([self.moto_travel_tool])
        
        # 创建状态图
        self.workflow = self._create_workflow()
        
        # 内存保存器
        self.memory = MemorySaver()
    
    def _create_workflow(self) -> StateGraph:
        """创建工作流"""
        
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("execute_agent", self._execute_agent)
        workflow.add_node("generate_response", self._generate_response)
        
        # 添加边
        workflow.set_entry_point("classify_intent")
        workflow.add_edge("classify_intent", "execute_agent")
        workflow.add_edge("execute_agent", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # 编译工作流
        return workflow.compile(checkpointer=self.memory)
    
    async def _classify_intent(self, state: AgentState) -> AgentState:
        """分类意图"""
        
        try:
            query = state["query"]
            user_id = state["user_id"]
            
            # 使用LLM分类意图
            system_prompt = """
            你是一个摩旅智能助手的意图分类器。请分析用户请求，确定需要调用哪个Agent。
            
            可用的Agent类型：
            1. route_planning - 路线规划：处理路线规划、导航、路径计算等
            2. weather - 天气查询：处理天气查询、预报、预警等
            3. poi - POI服务：处理餐饮、住宿、修车、加油站等本地服务，以及禁摩政策检查
            
            请返回最合适的Agent类型名称。
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"用户请求: {query}")
            ]
            
            response = await self.llm.agenerate([messages])
            intent = response.generations[0][0].text.strip().lower()
            
            # 更新状态
            state["current_agent"] = intent
            state["metadata"]["intent_classification"] = intent
            
            logger.info(f"Classified intent: {intent} for query: {query}")
            
            return state
            
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            state["current_agent"] = "route_planning"  # 默认使用路线规划
            return state
    
    async def _execute_agent(self, state: AgentState) -> AgentState:
        """执行Agent"""
        
        try:
            query = state["query"]
            user_id = state["user_id"]
            current_agent = state["current_agent"]
            
            # 使用工具执行器调用Agent
            result = await self.tool_executor.ainvoke(
                {"query": query, "user_id": user_id}
            )
            
            # 更新状态
            state["results"][current_agent] = result
            state["metadata"]["execution_time"] = datetime.utcnow().isoformat()
            
            logger.info(f"Executed agent {current_agent} successfully")
            
            return state
            
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            state["results"]["error"] = str(e)
            return state
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """生成响应"""
        
        try:
            query = state["query"]
            user_id = state["user_id"]
            current_agent = state["current_agent"]
            results = state["results"]
            
            # 获取Agent执行结果
            agent_result = results.get(current_agent, "")
            
            # 使用LLM生成自然语言响应
            system_prompt = """
            你是一个摩旅智能助手，请根据Agent的执行结果生成自然、友好的回复。
            回复应该：
            1. 简洁明了
            2. 包含有用的信息
            3. 语气友好
            4. 提供后续建议（如果需要）
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"用户问题: {query}\nAgent结果: {agent_result}")
            ]
            
            response = await self.llm.agenerate([messages])
            final_response = response.generations[0][0].text.strip()
            
            # 更新状态
            state["results"]["final_response"] = final_response
            state["metadata"]["response_generated"] = datetime.utcnow().isoformat()
            
            return state
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            state["results"]["final_response"] = "抱歉，处理您的请求时出现了问题。"
            return state
    
    async def process_query(
        self, 
        query: str, 
        user_id: str = "",
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """处理用户查询"""
        
        try:
            # 创建初始状态
            initial_state = AgentState(
                messages=[],
                user_id=user_id,
                query=query,
                current_agent="",
                results={},
                metadata={}
            )
            
            # 执行工作流
            config = {"configurable": {"thread_id": thread_id}}
            final_state = await self.workflow.ainvoke(initial_state, config)
            
            return {
                "success": True,
                "response": final_state["results"].get("final_response", ""),
                "agent_used": final_state["current_agent"],
                "raw_results": final_state["results"],
                "metadata": final_state["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，处理您的请求时出现了问题。"
            }
    
    async def process_multi_turn_conversation(
        self, 
        messages: List[BaseMessage], 
        user_id: str = "",
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """处理多轮对话"""
        
        try:
            # 获取最后一条用户消息
            last_message = messages[-1] if messages else None
            if not last_message or not isinstance(last_message, HumanMessage):
                return {
                    "success": False,
                    "error": "无效的消息格式"
                }
            
            query = last_message.content
            
            # 创建状态
            initial_state = AgentState(
                messages=messages,
                user_id=user_id,
                query=query,
                current_agent="",
                results={},
                metadata={}
            )
            
            # 执行工作流
            config = {"configurable": {"thread_id": thread_id}}
            final_state = await self.workflow.ainvoke(initial_state, config)
            
            return {
                "success": True,
                "response": final_state["results"].get("final_response", ""),
                "agent_used": final_state["current_agent"],
                "raw_results": final_state["results"],
                "metadata": final_state["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Multi-turn conversation processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，处理您的请求时出现了问题。"
            }
    
    def get_conversation_history(self, thread_id: str = "default") -> List[BaseMessage]:
        """获取对话历史"""
        
        try:
            config = {"configurable": {"thread_id": thread_id}}
            # 这里需要根据LangGraph的API获取历史消息
            # 具体实现取决于LangGraph的版本和API
            return []
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []
    
    async def clear_conversation_history(self, thread_id: str = "default") -> bool:
        """清除对话历史"""
        
        try:
            # 这里需要根据LangGraph的API清除历史
            # 具体实现取决于LangGraph的版本和API
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear conversation history: {str(e)}")
            return False
