"""
WebSocket接口
提供实时通信功能
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from loguru import logger

from app.langchain_integration import LangChainIntegration


class WebSocketManager:
    """WebSocket管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.session_users: Dict[str, str] = {}  # session_id -> user_id
    
    async def connect(self, websocket: WebSocket, user_id: str = "anonymous"):
        """建立WebSocket连接"""
        await websocket.accept()
        
        # 生成会话ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # 保存连接信息
        self.active_connections[session_id] = websocket
        self.user_sessions[user_id] = session_id
        self.session_users[session_id] = user_id
        
        logger.info(f"WebSocket connected: user_id={user_id}, session_id={session_id}")
        
        # 发送连接成功消息
        await self.send_message(session_id, {
            "type": "connection_established",
            "message": "连接成功",
            "session_id": session_id,
            "user_id": user_id
        })
    
    def disconnect(self, session_id: str):
        """断开WebSocket连接"""
        if session_id in self.active_connections:
            user_id = self.session_users.get(session_id, "unknown")
            
            # 清理连接信息
            del self.active_connections[session_id]
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
            if session_id in self.session_users:
                del self.session_users[session_id]
            
            logger.info(f"WebSocket disconnected: user_id={user_id}, session_id={session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        """发送消息到指定会话"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {str(e)}")
                self.disconnect(session_id)
    
    async def broadcast_message(self, message: dict, exclude_session: str = None):
        """广播消息到所有连接"""
        for session_id in list(self.active_connections.keys()):
            if session_id != exclude_session:
                await self.send_message(session_id, message)
    
    async def send_to_user(self, user_id: str, message: dict):
        """发送消息到指定用户"""
        if user_id in self.user_sessions:
            session_id = self.user_sessions[user_id]
            await self.send_message(session_id, message)
    
    def get_connected_users(self) -> List[str]:
        """获取已连接用户列表"""
        return list(self.user_sessions.keys())
    
    def get_connection_count(self) -> int:
        """获取连接数量"""
        return len(self.active_connections)


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()


async def websocket_endpoint(websocket: WebSocket, user_id: str = "anonymous"):
    """WebSocket端点"""
    await websocket_manager.connect(websocket, user_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理消息
            await handle_websocket_message(websocket, message, user_id)
            
    except WebSocketDisconnect:
        # 获取会话ID并断开连接
        session_id = None
        for sid, ws in websocket_manager.active_connections.items():
            if ws == websocket:
                session_id = sid
                break
        
        if session_id:
            websocket_manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        # 获取会话ID并断开连接
        session_id = None
        for sid, ws in websocket_manager.active_connections.items():
            if ws == websocket:
                session_id = sid
                break
        
        if session_id:
            websocket_manager.disconnect(session_id)


async def handle_websocket_message(websocket: WebSocket, message: dict, user_id: str):
    """处理WebSocket消息"""
    try:
        message_type = message.get("type", "")
        
        if message_type == "query":
            # 处理查询请求
            await handle_query_message(websocket, message, user_id)
        elif message_type == "ping":
            # 处理心跳
            await handle_ping_message(websocket, message)
        elif message_type == "get_status":
            # 处理状态查询
            await handle_status_message(websocket, message)
        else:
            # 未知消息类型
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"未知的消息类型: {message_type}"
            }, ensure_ascii=False))
            
    except Exception as e:
        logger.error(f"Failed to handle WebSocket message: {str(e)}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"消息处理失败: {str(e)}"
        }, ensure_ascii=False))


async def handle_query_message(websocket: WebSocket, message: dict, user_id: str):
    """处理查询消息"""
    try:
        query = message.get("query", "")
        if not query:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "查询内容不能为空"
            }, ensure_ascii=False))
            return
        
        # 发送处理中消息
        await websocket.send_text(json.dumps({
            "type": "processing",
            "message": "正在处理您的请求...",
            "query": query
        }, ensure_ascii=False))
        
        # 这里需要获取LangChain集成实例
        # 由于WebSocket上下文中没有request对象，我们需要其他方式获取
        # 这里暂时使用一个全局实例或者从应用状态中获取
        
        # 模拟处理过程
        await asyncio.sleep(1)  # 模拟处理时间
        
        # 发送结果消息
        await websocket.send_text(json.dumps({
            "type": "query_result",
            "message": "查询完成",
            "query": query,
            "result": f"这是对'{query}'的回复",
            "user_id": user_id
        }, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Failed to handle query message: {str(e)}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"查询处理失败: {str(e)}"
        }, ensure_ascii=False))


async def handle_ping_message(websocket: WebSocket, message: dict):
    """处理心跳消息"""
    try:
        await websocket.send_text(json.dumps({
            "type": "pong",
            "message": "pong",
            "timestamp": "2024-01-01T00:00:00Z"
        }, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Failed to handle ping message: {str(e)}")


async def handle_status_message(websocket: WebSocket, message: dict):
    """处理状态查询消息"""
    try:
        status_info = {
            "type": "status",
            "message": "系统状态正常",
            "connected_users": websocket_manager.get_connected_users(),
            "connection_count": websocket_manager.get_connection_count(),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        await websocket.send_text(json.dumps(status_info, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Failed to handle status message: {str(e)}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"状态查询失败: {str(e)}"
        }, ensure_ascii=False))
