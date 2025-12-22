"""
Agent系统包
新架构：基于A2A协议的多Agent协同系统
"""
from .base.agent import BaseAgent, AgentResponse, AgentStatus
from .base.message import AgentMessage, RequestMessage, ResponseMessage, NotificationMessage
from .base.a2a_protocol import A2AProtocol, InMemoryA2AProtocol, get_a2a_protocol

# 新架构Agent
from .route_planning import RoutePlanningAgent
from .weather import WeatherAgent
from .poi import POIAgent
from .hotel import HotelAgent

__all__ = [
    # 基础类
    "BaseAgent",
    "AgentResponse",
    "AgentStatus",
    "AgentMessage",
    "RequestMessage",
    "ResponseMessage",
    "NotificationMessage",
    "A2AProtocol",
    "InMemoryA2AProtocol",
    "get_a2a_protocol",
    # 新架构Agent
    "RoutePlanningAgent",
    "WeatherAgent",
    "POIAgent",
    "HotelAgent"
]
