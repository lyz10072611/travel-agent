"""
Agent基类
定义所有Agent的基础接口和通用功能
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
from loguru import logger


class AgentType(Enum):
    """Agent类型枚举"""
    ROUTE = "route"
    WEATHER = "weather"
    POI = "poi"
    SEARCH = "search"
    ATTRACTION = "attraction"
    BUDGET = "budget"
    PERSONALIZATION = "personalization"


class AgentStatus(Enum):
    """Agent状态枚举"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentResponse:
    """Agent响应数据类"""
    success: bool
    data: Any
    message: str
    agent_type: str
    execution_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "agent_type": self.agent_type,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, agent_type: AgentType, name: str, description: str):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self._execution_count = 0
        self._total_execution_time = 0.0
        
    @abstractmethod
    async def execute(self, **kwargs) -> AgentResponse:
        """执行Agent功能"""
        pass
    
    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """获取Agent能力描述"""
        return {
            "agent_type": self.agent_type.value,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "execution_count": self._execution_count,
            "average_execution_time": (
                self._total_execution_time / self._execution_count 
                if self._execution_count > 0 else 0
            )
        }
    
    async def _execute_with_timing(self, func, **kwargs) -> AgentResponse:
        """带计时的执行方法"""
        start_time = datetime.utcnow()
        self.status = AgentStatus.PROCESSING
        
        try:
            result = await func(**kwargs)
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
                agent_type=self.agent_type.value,
                execution_time=execution_time,
                timestamp=datetime.utcnow()
            )
    
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
            agent_type=self.agent_type.value,
            execution_time=0.0,  # 将在_execute_with_timing中设置
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
            agent_type=self.agent_type.value,
            execution_time=0.0,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
    
    def _validate_required_params(self, required_params: List[str], **kwargs) -> bool:
        """验证必需参数"""
        missing_params = [param for param in required_params if param not in kwargs]
        if missing_params:
            logger.warning(f"Missing required parameters: {missing_params}")
            return False
        return True
    
    def _validate_param_types(self, param_types: Dict[str, type], **kwargs) -> bool:
        """验证参数类型"""
        for param_name, expected_type in param_types.items():
            if param_name in kwargs:
                if not isinstance(kwargs[param_name], expected_type):
                    logger.warning(
                        f"Parameter {param_name} has wrong type. "
                        f"Expected {expected_type}, got {type(kwargs[param_name])}"
                    )
                    return False
        return True
    
    def _log_execution(self, operation: str, **kwargs):
        """记录执行日志"""
        logger.info(f"Agent {self.name} executing {operation} with params: {kwargs}")
    
    def reset_stats(self):
        """重置统计信息"""
        self._execution_count = 0
        self._total_execution_time = 0.0
        self.status = AgentStatus.IDLE


class AsyncAgent(BaseAgent):
    """异步Agent基类"""
    
    def __init__(self, agent_type: AgentType, name: str, description: str):
        super().__init__(agent_type, name, description)
        self._semaphore = asyncio.Semaphore(10)  # 限制并发数
    
    async def execute(self, **kwargs) -> AgentResponse:
        """异步执行Agent功能"""
        async with self._semaphore:
            return await self._execute_with_timing(self._execute_async, **kwargs)
    
    @abstractmethod
    async def _execute_async(self, **kwargs) -> AgentResponse:
        """异步执行具体功能"""
        pass


class SyncAgent(BaseAgent):
    """同步Agent基类"""
    
    async def execute(self, **kwargs) -> AgentResponse:
        """同步执行Agent功能"""
        return await self._execute_with_timing(self._execute_sync, **kwargs)
    
    @abstractmethod
    def _execute_sync(self, **kwargs) -> AgentResponse:
        """同步执行具体功能"""
        pass
