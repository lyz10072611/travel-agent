"""
用户认证服务
处理手机号+验证码登录
"""
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import random
import string
from sqlalchemy.orm import Session
from app.database import get_db_session
from app.models.user import User
from app.utils.security import generate_token, verify_token
from loguru import logger
import redis
from app.config import settings


class AuthService:
    """认证服务"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.code_expire_time = 300  # 验证码5分钟过期
        self.token_expire_time = 3600 * 24 * 7  # token 7天过期
    
    def generate_verification_code(self, length: int = 6) -> str:
        """生成验证码"""
        return ''.join(random.choices(string.digits, k=length))
    
    async def send_verification_code(self, phone: str) -> Dict[str, Any]:
        """发送验证码"""
        try:
            # 验证手机号格式
            if not self._validate_phone(phone):
                return {
                    "success": False,
                    "message": "手机号格式不正确"
                }
            
            # 生成验证码
            code = self.generate_verification_code()
            
            # 存储到Redis（5分钟过期）
            key = f"verification_code:{phone}"
            self.redis_client.setex(
                key,
                self.code_expire_time,
                code
            )
            
            # 这里应该调用短信服务发送验证码
            # 暂时只记录日志
            logger.info(f"Verification code for {phone}: {code}")
            
            # TODO: 集成短信服务
            # await self._send_sms(phone, code)
            
            return {
                "success": True,
                "message": "验证码已发送",
                "code": code  # 开发环境返回，生产环境应删除
            }
            
        except Exception as e:
            logger.error(f"Send verification code failed: {str(e)}")
            return {
                "success": False,
                "message": f"发送验证码失败: {str(e)}"
            }
    
    async def verify_code(self, phone: str, code: str) -> Dict[str, Any]:
        """验证验证码"""
        try:
            key = f"verification_code:{phone}"
            stored_code = self.redis_client.get(key)
            
            if not stored_code:
                return {
                    "success": False,
                    "message": "验证码已过期或不存在"
                }
            
            if stored_code.decode() != code:
                return {
                    "success": False,
                    "message": "验证码错误"
                }
            
            # 验证成功后删除验证码
            self.redis_client.delete(key)
            
            return {
                "success": True,
                "message": "验证码验证成功"
            }
            
        except Exception as e:
            logger.error(f"Verify code failed: {str(e)}")
            return {
                "success": False,
                "message": f"验证码验证失败: {str(e)}"
            }
    
    async def login_with_phone(self, phone: str, code: str) -> Dict[str, Any]:
        """手机号+验证码登录"""
        try:
            # 验证验证码
            verify_result = await self.verify_code(phone, code)
            if not verify_result["success"]:
                return verify_result
            
            # 查找或创建用户
            with get_db_session() as db:
                user = db.query(User).filter(User.phone == phone).first()
                
                if not user:
                    # 创建新用户
                    user = User(
                        username=f"user_{phone}",
                        email=f"{phone}@moto.travel",
                        phone=phone,
                        nickname=f"摩友_{phone[-4:]}",
                        password_hash="",  # 手机号登录不需要密码
                        is_active=True,
                        is_verified=True
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                
                # 生成token
                token = generate_token(str(user.id), self.token_expire_time)
                
                return {
                    "success": True,
                    "data": {
                        "user_id": str(user.id),
                        "username": user.username,
                        "phone": user.phone,
                        "nickname": user.nickname,
                        "token": token
                    },
                    "message": "登录成功"
                }
                
        except Exception as e:
            logger.error(f"Login with phone failed: {str(e)}")
            return {
                "success": False,
                "message": f"登录失败: {str(e)}"
            }
    
    async def get_user_by_token(self, token: str) -> Optional[User]:
        """通过token获取用户"""
        try:
            payload = verify_token(token)
            user_id = payload.get("user_id")
            
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                return user
                
        except Exception as e:
            logger.error(f"Get user by token failed: {str(e)}")
            return None
    
    def _validate_phone(self, phone: str) -> bool:
        """验证手机号格式"""
        # 简单的手机号验证（11位数字，1开头）
        if not phone or len(phone) != 11:
            return False
        if not phone.isdigit():
            return False
        if not phone.startswith('1'):
            return False
        return True
    
    async def _send_sms(self, phone: str, code: str) -> bool:
        """发送短信（需要集成短信服务）"""
        # TODO: 集成阿里云短信、腾讯云短信等服务
        # 这里只是占位符
        logger.info(f"Would send SMS to {phone} with code {code}")
        return True

