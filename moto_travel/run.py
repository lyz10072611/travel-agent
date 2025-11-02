#!/usr/bin/env python3
"""
摩旅智能助手启动脚本
"""
import uvicorn
from app.api.main import app
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
