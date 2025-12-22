"""
Agent消息定义
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid


class MessageType(Enum):
    """消息类型"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


class MessagePriority(Enum):
    """消息优先级"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class AgentMessage:
    """Agent消息基类"""
    from_agent: str
    to_agent: str
    message_type: MessageType
    action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.message_type.value,
            "action": self.action,
            "payload": self.payload,
            "metadata": {
                "request_id": self.request_id,
                "timestamp": self.timestamp,
                "priority": self.priority.value,
                **self.metadata
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """从字典创建"""
        return cls(
            from_agent=data["from"],
            to_agent=data["to"],
            message_type=MessageType(data["type"]),
            action=data["action"],
            payload=data.get("payload", {}),
            request_id=data.get("metadata", {}).get("request_id", str(uuid.uuid4())),
            timestamp=data.get("metadata", {}).get("timestamp", datetime.utcnow().isoformat()),
            priority=MessagePriority(data.get("metadata", {}).get("priority", "normal")),
            metadata=data.get("metadata", {})
        )


@dataclass
class RequestMessage(AgentMessage):
    """请求消息"""
    timeout: Optional[float] = None  # 超时时间（秒）
    
    def __post_init__(self):
        self.message_type = MessageType.REQUEST


@dataclass
class ResponseMessage(AgentMessage):
    """响应消息"""
    success: bool = True
    error: Optional[str] = None
    original_request_id: Optional[str] = None
    
    def __post_init__(self):
        self.message_type = MessageType.RESPONSE


@dataclass
class NotificationMessage(AgentMessage):
    """通知消息"""
    def __post_init__(self):
        self.message_type = MessageType.NOTIFICATION

