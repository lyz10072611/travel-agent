"""
工具基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime
import asyncio
import aiohttp
from loguru import logger
from app.config import settings


class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_delay = 1.0  # 默认1秒延迟
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "MotoTravel-Agent/1.0"}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具功能"""
        pass
    
    async def _make_request(
        self, 
        url: str, 
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """发送HTTP请求"""
        if not self.session:
            raise RuntimeError("Tool not initialized. Use async context manager.")
        
        try:
            # 添加默认参数
            if params is None:
                params = {}
            if headers is None:
                headers = {}
                
            # 添加API密钥
            if hasattr(self, 'api_key'):
                params['key'] = self.api_key
            
            logger.info(f"Making {method} request to {url}")
            
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                # 添加速率限制延迟
                await asyncio.sleep(self._rate_limit_delay)
                
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in request: {e}")
            raise
    
    def validate_params(self, required_params: List[str], **kwargs) -> None:
        """验证必需参数"""
        missing_params = [param for param in required_params if param not in kwargs]
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
    
    def format_response(self, data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
        """格式化响应"""
        return {
            "success": success,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "tool": self.name
        }


class RateLimitedTool(BaseTool):
    """带速率限制的工具基类"""
    
    def __init__(self, name: str, description: str, requests_per_minute: int = 60):
        super().__init__(name, description)
        self.requests_per_minute = requests_per_minute
        self._rate_limit_delay = 60.0 / requests_per_minute
        self._last_request_time = 0.0
        self._request_count = 0
        self._window_start = datetime.utcnow().timestamp()
    
    async def _check_rate_limit(self):
        """检查速率限制"""
        current_time = datetime.utcnow().timestamp()
        
        # 重置窗口
        if current_time - self._window_start >= 60:
            self._request_count = 0
            self._window_start = current_time
        
        # 检查是否超过限制
        if self._request_count >= self.requests_per_minute:
            sleep_time = 60 - (current_time - self._window_start)
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                self._request_count = 0
                self._window_start = datetime.utcnow().timestamp()
        
        self._request_count += 1
