"""
Agent基类
支持A2A协议通信
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from .a2a_protocol import get_a2a_protocol, InMemoryA2AProtocol
from .message import RequestMessage, ResponseMessage, MessagePriority


class AgentStatus(Enum):
    """Agent状态"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentResponse:
    """Agent响应"""
    success: bool
    data: Any
    message: str
    agent_name: str
    execution_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "agent_name": self.agent_name,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.protocol: InMemoryA2AProtocol = get_a2a_protocol()
        self._execution_count = 0
        self._total_execution_time = 0.0
        
        # 注册到A2A协议
        self.protocol.register_agent(self.name, self)
    
    @abstractmethod
    async def handle_request(self, request: RequestMessage) -> ResponseMessage:
        """处理请求消息"""
        pass
    
    async def send_request(
        self,
        to_agent: str,
        action: str,
        payload: Dict[str, Any],
        timeout: Optional[float] = 30.0,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> ResponseMessage:
        """向其他Agent发送请求"""
        return await self.protocol.send_request(
            from_agent=self.name,
            to_agent=to_agent,
            action=action,
            payload=payload,
            timeout=timeout,
            priority=priority
        )
    
    async def send_notification(
        self,
        to_agent: str,
        action: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ):
        """向其他Agent发送通知"""
        await self.protocol.send_notification(
            from_agent=self.name,
            to_agent=to_agent,
            action=action,
            payload=payload,
            priority=priority
        )
    
    def register_action_handler(
        self,
        action: str,
        handler: callable
    ):
        """注册动作处理器"""
        async def async_handler(request: RequestMessage) -> ResponseMessage:
            try:
                result = await handler(request.payload)
                return ResponseMessage(
                    from_agent=self.name,
                    to_agent=request.from_agent,
                    action=action,
                    success=True,
                    payload=result if isinstance(result, dict) else {"result": result},
                    original_request_id=request.request_id
                )
            except Exception as e:
                logger.error(f"Handler error in {self.name}.{action}: {str(e)}")
                return ResponseMessage(
                    from_agent=self.name,
                    to_agent=request.from_agent,
                    action=action,
                    success=False,
                    error=str(e),
                    original_request_id=request.request_id,
                    payload={}
                )
        
        self.protocol.register_handler(self.name, action, async_handler)
    
    async def execute(self, **kwargs) -> AgentResponse:
        """执行Agent功能（兼容旧接口）"""
        start_time = datetime.utcnow()
        self.status = AgentStatus.PROCESSING
        
        try:
            result = await self._execute_async(**kwargs)
            self.status = AgentStatus.COMPLETED
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._execution_count += 1
            self._total_execution_time += execution_time
            return result
        except Exception as e:
            self.status = AgentStatus.ERROR
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Agent {self.name} execution failed: {str(e)}")
            return AgentResponse(
                success=False,
                data=None,
                message=f"执行失败: {str(e)}",
                agent_name=self.name,
                execution_time=execution_time,
                timestamp=datetime.utcnow()
            )
    
    @abstractmethod
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """异步执行具体功能"""
        pass
    
    def _create_success_response(
        self,
        data: Any,
        message: str = "执行成功",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """创建成功响应"""
        return AgentResponse(
            success=True,
            data=data,
            message=message,
            agent_name=self.name,
            execution_time=0.0,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
    
    def _create_error_response(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """创建错误响应"""
        return AgentResponse(
            success=False,
            data=None,
            message=message,
            agent_name=self.name,
            execution_time=0.0,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """获取Agent能力描述"""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "execution_count": self._execution_count,
            "average_execution_time": (
                self._total_execution_time / self._execution_count
                if self._execution_count > 0 else 0
            )
        }

