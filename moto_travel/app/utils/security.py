"""
安全工具
提供密码加密、令牌生成等安全功能
"""
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from app.config import settings


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed


def generate_token(user_id: str, expires_in: int = 3600) -> str:
    """生成JWT令牌"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def verify_token(token: str) -> dict:
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def generate_api_key() -> str:
    """生成API密钥"""
    return secrets.token_urlsafe(32)


def generate_session_id() -> str:
    """生成会话ID"""
    return secrets.token_urlsafe(16)

