"""
Agent-to-Agent (A2A) 通信协议
"""
from typing import Dict, Any, Optional, Callable, Awaitable
from abc import ABC, abstractmethod
import asyncio
from loguru import logger

from .message import (
    AgentMessage, RequestMessage, ResponseMessage, NotificationMessage,
    MessageType, MessagePriority
)


class A2AProtocol(ABC):
    """A2A协议接口"""
    
    @abstractmethod
    async def send_message(self, message: AgentMessage) -> Optional[ResponseMessage]:
        """发送消息"""
        pass
    
    @abstractmethod
    async def register_handler(
        self, 
        action: str, 
        handler: Callable[[RequestMessage], Awaitable[ResponseMessage]]
    ):
        """注册消息处理器"""
        pass


class InMemoryA2AProtocol(A2AProtocol):
    """内存中的A2A协议实现（用于单进程）"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}  # agent_name -> agent_instance
        self.handlers: Dict[str, Dict[str, Callable]] = {}  # agent_name -> {action -> handler}
        self.pending_requests: Dict[str, asyncio.Future] = {}  # request_id -> Future
        
    def register_agent(self, agent_name: str, agent_instance: Any):
        """注册Agent"""
        self.agents[agent_name] = agent_instance
        self.handlers[agent_name] = {}
        logger.info(f"Registered agent: {agent_name}")
    
    async def register_handler(
        self,
        agent_name: str,
        action: str,
        handler: Callable[[RequestMessage], Awaitable[ResponseMessage]]
    ):
        """注册消息处理器"""
        if agent_name not in self.handlers:
            self.handlers[agent_name] = {}
        self.handlers[agent_name][action] = handler
        logger.info(f"Registered handler: {agent_name}.{action}")
    
    async def send_message(self, message: AgentMessage) -> Optional[ResponseMessage]:
        """发送消息"""
        if message.to_agent not in self.agents:
            logger.error(f"Agent not found: {message.to_agent}")
            return None
        
        if message.message_type == MessageType.REQUEST:
            return await self._handle_request(message)
        elif message.message_type == MessageType.NOTIFICATION:
            await self._handle_notification(message)
            return None
        elif message.message_type == MessageType.RESPONSE:
            await self._handle_response(message)
            return None
        
        return None
    
    async def _handle_request(self, request: RequestMessage) -> ResponseMessage:
        """处理请求消息"""
        agent_name = request.to_agent
        action = request.action
        
        # 查找处理器
        handler = self.handlers.get(agent_name, {}).get(action)
        if not handler:
            logger.error(f"No handler found for {agent_name}.{action}")
            return ResponseMessage(
                from_agent=agent_name,
                to_agent=request.from_agent,
                action=action,
                success=False,
                error=f"No handler found for action: {action}",
                original_request_id=request.request_id,
                payload={}
            )
        
        try:
            # 调用处理器
            response = await handler(request)
            response.original_request_id = request.request_id
            return response
        except Exception as e:
            logger.error(f"Handler error for {agent_name}.{action}: {str(e)}")
            return ResponseMessage(
                from_agent=agent_name,
                to_agent=request.from_agent,
                action=action,
                success=False,
                error=str(e),
                original_request_id=request.request_id,
                payload={}
            )
    
    async def _handle_notification(self, notification: NotificationMessage):
        """处理通知消息"""
        agent_name = notification.to_agent
        action = notification.action
        
        handler = self.handlers.get(agent_name, {}).get(action)
        if handler:
            try:
                # 通知消息不需要响应
                await handler(notification)
            except Exception as e:
                logger.error(f"Notification handler error: {str(e)}")
    
    async def _handle_response(self, response: ResponseMessage):
        """处理响应消息"""
        # 如果有等待的请求，设置结果
        if response.original_request_id in self.pending_requests:
            future = self.pending_requests.pop(response.original_request_id)
            if not future.done():
                future.set_result(response)
    
    async def send_request(
        self,
        from_agent: str,
        to_agent: str,
        action: str,
        payload: Dict[str, Any],
        timeout: Optional[float] = 30.0,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> ResponseMessage:
        """发送请求并等待响应"""
        request = RequestMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            action=action,
            payload=payload,
            timeout=timeout,
            priority=priority
        )
        
        # 创建Future等待响应
        future = asyncio.Future()
        self.pending_requests[request.request_id] = future
        
        try:
            # 发送请求
            response = await self.send_message(request)
            
            if response:
                # 直接返回响应
                if not future.done():
                    future.set_result(response)
                return response
            
            # 等待响应
            if timeout:
                response = await asyncio.wait_for(future, timeout=timeout)
            else:
                response = await future
            
            return response
            
        except asyncio.TimeoutError:
            self.pending_requests.pop(request.request_id, None)
            return ResponseMessage(
                from_agent=to_agent,
                to_agent=from_agent,
                action=action,
                success=False,
                error="Request timeout",
                original_request_id=request.request_id,
                payload={}
            )
        except Exception as e:
            self.pending_requests.pop(request.request_id, None)
            return ResponseMessage(
                from_agent=to_agent,
                to_agent=from_agent,
                action=action,
                success=False,
                error=str(e),
                original_request_id=request.request_id,
                payload={}
            )
    
    async def send_notification(
        self,
        from_agent: str,
        to_agent: str,
        action: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ):
        """发送通知（不需要响应）"""
        notification = NotificationMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            action=action,
            payload=payload,
            priority=priority
        )
        await self.send_message(notification)


# 全局A2A协议实例
_global_protocol: Optional[InMemoryA2AProtocol] = None


def get_a2a_protocol() -> InMemoryA2AProtocol:
    """获取全局A2A协议实例"""
    global _global_protocol
    if _global_protocol is None:
        _global_protocol = InMemoryA2AProtocol()
    return _global_protocol


def set_a2a_protocol(protocol: InMemoryA2AProtocol):
    """设置全局A2A协议实例"""
    global _global_protocol
    _global_protocol = protocol

