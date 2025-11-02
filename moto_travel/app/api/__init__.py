"""
API接口包
提供RESTful API和WebSocket接口
"""
from .main import app
from .routes import router
from .websocket import websocket_manager

__all__ = ["app", "router", "websocket_manager"]
