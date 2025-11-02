"""
记忆管理工具
处理用户偏好、历史记录、向量检索等功能
"""
from typing import Dict, List, Any, Optional, Tuple
import json
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from tools.base_tool import BaseTool
from app.config import settings


class MemoryManager(BaseTool):
    """记忆管理器"""
    
    def __init__(self):
        super().__init__(
            name="memory_manager",
            description="用户记忆管理工具，处理偏好和历史记录"
        )
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    async def save_user_preference(
        self,
        user_id: str,
        preference_type: str,
        preference_data: Dict[str, Any],
        description: str = ""
    ) -> Dict[str, Any]:
        """保存用户偏好"""
        
        # 生成文本描述用于向量化
        text_content = self._generate_preference_text(preference_type, preference_data)
        
        # 生成向量嵌入
        embedding = self.embedding_model.encode(text_content).tolist()
        
        with self.SessionLocal() as session:
            try:
                # 保存到数据库
                insert_query = text("""
                    INSERT INTO memories (user_id, memory_type, content_text, embedding, metadata, created_at)
                    VALUES (:user_id, :memory_type, :content_text, :embedding, :metadata, :created_at)
                """)
                
                session.execute(insert_query, {
                    "user_id": user_id,
                    "memory_type": preference_type,
                    "content_text": text_content,
                    "embedding": json.dumps(embedding),
                    "metadata": json.dumps(preference_data),
                    "created_at": datetime.utcnow()
                })
                
                session.commit()
                
                return self.format_response({
                    "user_id": user_id,
                    "preference_type": preference_type,
                    "saved": True,
                    "description": description
                })
                
            except Exception as e:
                session.rollback()
                return self.format_response(
                    None,
                    success=False,
                    message=f"保存偏好失败: {str(e)}"
                )
    
    async def get_user_preferences(
        self,
        user_id: str,
        preference_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取用户偏好"""
        
        with self.SessionLocal() as session:
            try:
                query = text("""
                    SELECT memory_type, content_text, metadata, created_at
                    FROM memories
                    WHERE user_id = :user_id
                """)
                
                params = {"user_id": user_id}
                if preference_type:
                    query = text("""
                        SELECT memory_type, content_text, metadata, created_at
                        FROM memories
                        WHERE user_id = :user_id AND memory_type = :memory_type
                    """)
                    params["memory_type"] = preference_type
                
                result = session.execute(query, params)
                preferences = []
                
                for row in result:
                    preferences.append({
                        "type": row.memory_type,
                        "content": row.content_text,
                        "data": json.loads(row.metadata) if row.metadata else {},
                        "created_at": row.created_at.isoformat()
                    })
                
                return self.format_response({
                    "user_id": user_id,
                    "preferences": preferences,
                    "count": len(preferences)
                })
                
            except Exception as e:
                return self.format_response(
                    None,
                    success=False,
                    message=f"获取偏好失败: {str(e)}"
                )
    
    async def save_trip_experience(
        self,
        user_id: str,
        trip_data: Dict[str, Any],
        feedback: str = ""
    ) -> Dict[str, Any]:
        """保存旅行经验"""
        
        # 生成经验文本
        experience_text = self._generate_experience_text(trip_data, feedback)
        
        # 生成向量嵌入
        embedding = self.embedding_model.encode(experience_text).tolist()
        
        with self.SessionLocal() as session:
            try:
                insert_query = text("""
                    INSERT INTO memories (user_id, memory_type, content_text, embedding, metadata, created_at)
                    VALUES (:user_id, :memory_type, :content_text, :embedding, :metadata, :created_at)
                """)
                
                session.execute(insert_query, {
                    "user_id": user_id,
                    "memory_type": "trip_experience",
                    "content_text": experience_text,
                    "embedding": json.dumps(embedding),
                    "metadata": json.dumps(trip_data),
                    "created_at": datetime.utcnow()
                })
                
                session.commit()
                
                return self.format_response({
                    "user_id": user_id,
                    "experience_saved": True,
                    "feedback": feedback
                })
                
            except Exception as e:
                session.rollback()
                return self.format_response(
                    None,
                    success=False,
                    message=f"保存经验失败: {str(e)}"
                )
    
    def _generate_preference_text(self, preference_type: str, data: Dict[str, Any]) -> str:
        """生成偏好文本描述"""
        if preference_type == "daily_distance":
            return f"用户偏好日行距离: {data.get('distance', 0)}公里"
        elif preference_type == "accommodation":
            return f"用户偏好住宿类型: {data.get('type', '')}, 预算: {data.get('budget', 0)}元"
        elif preference_type == "dining":
            return f"用户偏好餐饮: {data.get('cuisine', '')}, 预算: {data.get('budget', 0)}元"
        elif preference_type == "route_type":
            return f"用户偏好路线类型: {data.get('type', '')}, 是否避开高速: {data.get('avoid_highway', False)}"
        else:
            return f"用户偏好 {preference_type}: {json.dumps(data, ensure_ascii=False)}"
    
    def _generate_experience_text(self, trip_data: Dict[str, Any], feedback: str) -> str:
        """生成经验文本描述"""
        route = trip_data.get("route", "")
        duration = trip_data.get("duration", 0)
        distance = trip_data.get("distance", 0)
        
        experience_parts = [
            f"路线: {route}",
            f"距离: {distance}公里",
            f"时长: {duration}天"
        ]
        
        if feedback:
            experience_parts.append(f"反馈: {feedback}")
        
        return " | ".join(experience_parts)


class VectorSearch(BaseTool):
    """向量搜索工具"""
    
    def __init__(self):
        super().__init__(
            name="vector_search",
            description="向量搜索工具，用于相似性检索"
        )
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    async def search_similar_memories(
        self,
        query: str,
        user_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """搜索相似记忆"""
        
        # 生成查询向量
        query_embedding = self.embedding_model.encode(query).tolist()
        
        with self.SessionLocal() as session:
            try:
                # 构建SQL查询
                base_query = """
                    SELECT id, user_id, memory_type, content_text, metadata, created_at,
                           embedding <=> :query_embedding as distance
                    FROM memories
                    WHERE 1=1
                """
                
                params = {"query_embedding": json.dumps(query_embedding)}
                
                if user_id:
                    base_query += " AND user_id = :user_id"
                    params["user_id"] = user_id
                
                if memory_type:
                    base_query += " AND memory_type = :memory_type"
                    params["memory_type"] = memory_type
                
                base_query += " ORDER BY distance LIMIT :limit"
                params["limit"] = limit
                
                result = session.execute(text(base_query), params)
                similar_memories = []
                
                for row in result:
                    similar_memories.append({
                        "id": str(row.id),
                        "user_id": row.user_id,
                        "memory_type": row.memory_type,
                        "content": row.content_text,
                        "data": json.loads(row.metadata) if row.metadata else {},
                        "created_at": row.created_at.isoformat(),
                        "similarity": 1 - row.distance  # 转换为相似度分数
                    })
                
                return self.format_response({
                    "query": query,
                    "similar_memories": similar_memories,
                    "count": len(similar_memories)
                })
                
            except Exception as e:
                return self.format_response(
                    None,
                    success=False,
                    message=f"搜索相似记忆失败: {str(e)}"
                )
    
    async def find_similar_trips(
        self,
        trip_description: str,
        user_id: Optional[str] = None,
        limit: int = 3
    ) -> Dict[str, Any]:
        """查找相似旅行"""
        
        return await self.search_similar_memories(
            query=trip_description,
            user_id=user_id,
            memory_type="trip_experience",
            limit=limit
        )
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        current_query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """获取个性化推荐"""
        
        # 搜索用户的历史偏好和经验
        similar_memories = await self.search_similar_memories(
            query=current_query,
            user_id=user_id,
            limit=limit
        )
        
        if not similar_memories["success"]:
            return similar_memories
        
        # 分析相似记忆生成推荐
        recommendations = self._generate_recommendations_from_memories(
            similar_memories["data"]["similar_memories"]
        )
        
        return self.format_response({
            "user_id": user_id,
            "query": current_query,
            "recommendations": recommendations,
            "based_on_memories": len(similar_memories["data"]["similar_memories"])
        })
    
    def _generate_recommendations_from_memories(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从记忆中生成推荐"""
        recommendations = []
        
        # 分析偏好类型
        preference_types = {}
        for memory in memories:
            memory_type = memory.get("memory_type", "")
            if memory_type not in preference_types:
                preference_types[memory_type] = []
            preference_types[memory_type].append(memory)
        
        # 为每种偏好类型生成推荐
        for pref_type, pref_memories in preference_types.items():
            if pref_type == "daily_distance":
                # 分析日行距离偏好
                distances = []
                for memory in pref_memories:
                    data = memory.get("data", {})
                    if "distance" in data:
                        distances.append(data["distance"])
                
                if distances:
                    avg_distance = sum(distances) / len(distances)
                    recommendations.append({
                        "type": "daily_distance",
                        "recommendation": f"建议日行距离: {int(avg_distance)}公里",
                        "confidence": len(pref_memories) / 10.0
                    })
            
            elif pref_type == "accommodation":
                # 分析住宿偏好
                accommodation_types = {}
                for memory in pref_memories:
                    data = memory.get("data", {})
                    acc_type = data.get("type", "未知")
                    if acc_type not in accommodation_types:
                        accommodation_types[acc_type] = 0
                    accommodation_types[acc_type] += 1
                
                if accommodation_types:
                    preferred_type = max(accommodation_types, key=accommodation_types.get)
                    recommendations.append({
                        "type": "accommodation",
                        "recommendation": f"推荐住宿类型: {preferred_type}",
                        "confidence": accommodation_types[preferred_type] / len(pref_memories)
                    })
        
        return recommendations
