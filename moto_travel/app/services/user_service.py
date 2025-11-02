"""
用户服务
处理用户相关的业务逻辑
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User, UserPreferences
from app.database import get_db_session
from loguru import logger


class UserService:
    """用户服务类"""
    
    @staticmethod
    async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建用户"""
        try:
            with get_db_session() as db:
                # 检查用户是否已存在
                existing_user = db.query(User).filter(
                    (User.username == user_data["username"]) | 
                    (User.email == user_data["email"])
                ).first()
                
                if existing_user:
                    return {
                        "success": False,
                        "message": "用户名或邮箱已存在"
                    }
                
                # 创建用户
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    phone=user_data.get("phone"),
                    nickname=user_data.get("nickname"),
                    password_hash=user_data["password_hash"],
                    preferences=user_data.get("preferences", {})
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
                
                return {
                    "success": True,
                    "data": user.to_dict(),
                    "message": "用户创建成功"
                }
                
        except Exception as e:
            logger.error(f"Create user failed: {str(e)}")
            return {
                "success": False,
                "message": f"用户创建失败: {str(e)}"
            }
    
    @staticmethod
    async def get_user(user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return {
                        "success": False,
                        "message": "用户不存在"
                    }
                
                return {
                    "success": True,
                    "data": user.to_dict(),
                    "message": "获取用户信息成功"
                }
                
        except Exception as e:
            logger.error(f"Get user failed: {str(e)}")
            return {
                "success": False,
                "message": f"获取用户信息失败: {str(e)}"
            }
    
    @staticmethod
    async def update_user_preferences(user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户偏好"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return {
                        "success": False,
                        "message": "用户不存在"
                    }
                
                # 更新偏好
                user.preferences.update(preferences)
                user.updated_at = datetime.utcnow()
                
                db.commit()
                
                return {
                    "success": True,
                    "data": user.preferences,
                    "message": "用户偏好更新成功"
                }
                
        except Exception as e:
            logger.error(f"Update user preferences failed: {str(e)}")
            return {
                "success": False,
                "message": f"更新用户偏好失败: {str(e)}"
            }

