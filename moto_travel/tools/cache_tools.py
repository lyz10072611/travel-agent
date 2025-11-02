"""
缓存管理工具
处理Redis缓存、数据缓存等功能
"""
from typing import Dict, List, Any, Optional, Union
import json
import pickle
import hashlib
from datetime import datetime, timedelta
import redis
from tools.base_tool import BaseTool
from app.config import settings


class CacheManager(BaseTool):
    """缓存管理器"""
    
    def __init__(self):
        super().__init__(
            name="cache_manager",
            description="缓存管理工具，提供数据缓存功能"
        )
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.default_ttl = settings.cache_ttl
    
    async def set_cache(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize_method: str = "json"
    ) -> Dict[str, Any]:
        """设置缓存"""
        
        try:
            # 序列化数据
            if serialize_method == "json":
                serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            elif serialize_method == "pickle":
                serialized_value = pickle.dumps(value)
            else:
                serialized_value = str(value)
            
            # 设置缓存
            ttl = ttl or self.default_ttl
            self.redis_client.setex(key, ttl, serialized_value)
            
            return self.format_response({
                "key": key,
                "cached": True,
                "ttl": ttl,
                "method": serialize_method
            })
            
        except Exception as e:
            return self.format_response(
                None,
                success=False,
                message=f"设置缓存失败: {str(e)}"
            )
    
    async def get_cache(
        self,
        key: str,
        serialize_method: str = "json"
    ) -> Dict[str, Any]:
        """获取缓存"""
        
        try:
            cached_value = self.redis_client.get(key)
            
            if cached_value is None:
                return self.format_response(
                    None,
                    success=False,
                    message="缓存不存在"
                )
            
            # 反序列化数据
            if serialize_method == "json":
                value = json.loads(cached_value)
            elif serialize_method == "pickle":
                value = pickle.loads(cached_value)
            else:
                value = cached_value
            
            return self.format_response({
                "key": key,
                "value": value,
                "found": True
            })
            
        except Exception as e:
            return self.format_response(
                None,
                success=False,
                message=f"获取缓存失败: {str(e)}"
            )
    
    async def delete_cache(self, key: str) -> Dict[str, Any]:
        """删除缓存"""
        
        try:
            deleted = self.redis_client.delete(key)
            
            return self.format_response({
                "key": key,
                "deleted": bool(deleted)
            })
            
        except Exception as e:
            return self.format_response(
                None,
                success=False,
                message=f"删除缓存失败: {str(e)}"
            )
    
    async def clear_cache_pattern(self, pattern: str) -> Dict[str, Any]:
        """按模式清除缓存"""
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
            else:
                deleted = 0
            
            return self.format_response({
                "pattern": pattern,
                "keys_found": len(keys),
                "keys_deleted": deleted
            })
            
        except Exception as e:
            return self.format_response(
                None,
                success=False,
                message=f"清除缓存失败: {str(e)}"
            )
    
    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数组合成字符串
        key_parts = [prefix]
        
        # 添加位置参数
        for arg in args:
            key_parts.append(str(arg))
        
        # 添加关键字参数
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        # 生成哈希
        key_string = "|".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{prefix}:{key_hash}"


class RedisCache(BaseTool):
    """Redis缓存工具"""
    
    def __init__(self):
        super().__init__(
            name="redis_cache",
            description="Redis缓存工具，提供高级缓存功能"
        )
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    async def cache_weather_data(
        self,
        location: str,
        weather_data: Dict[str, Any],
        ttl: int = None
    ) -> Dict[str, Any]:
        """缓存天气数据"""
        
        ttl = ttl or settings.weather_cache_ttl
        cache_key = f"weather:{location}:{datetime.now().strftime('%Y%m%d%H')}"
        
        return await self._cache_data(cache_key, weather_data, ttl)
    
    async def get_cached_weather_data(self, location: str) -> Dict[str, Any]:
        """获取缓存的天气数据"""
        
        # 尝试获取当前小时的缓存
        current_hour_key = f"weather:{location}:{datetime.now().strftime('%Y%m%d%H')}"
        result = await self._get_cached_data(current_hour_key)
        
        if result["success"]:
            return result
        
        # 尝试获取上一小时的缓存
        prev_hour = datetime.now() - timedelta(hours=1)
        prev_hour_key = f"weather:{location}:{prev_hour.strftime('%Y%m%d%H')}"
        return await self._get_cached_data(prev_hour_key)
    
    async def cache_route_data(
        self,
        origin: str,
        destination: str,
        route_data: Dict[str, Any],
        ttl: int = None
    ) -> Dict[str, Any]:
        """缓存路线数据"""
        
        ttl = ttl or settings.route_cache_ttl
        cache_key = f"route:{origin}:{destination}:{datetime.now().strftime('%Y%m%d')}"
        
        return await self._cache_data(cache_key, route_data, ttl)
    
    async def get_cached_route_data(self, origin: str, destination: str) -> Dict[str, Any]:
        """获取缓存的路线数据"""
        
        cache_key = f"route:{origin}:{destination}:{datetime.now().strftime('%Y%m%d')}"
        return await self._get_cached_data(cache_key)
    
    async def cache_poi_data(
        self,
        location: str,
        poi_type: str,
        poi_data: Dict[str, Any],
        ttl: int = 3600
    ) -> Dict[str, Any]:
        """缓存POI数据"""
        
        cache_key = f"poi:{location}:{poi_type}:{datetime.now().strftime('%Y%m%d')}"
        return await self._cache_data(cache_key, poi_data, ttl)
    
    async def get_cached_poi_data(self, location: str, poi_type: str) -> Dict[str, Any]:
        """获取缓存的POI数据"""
        
        cache_key = f"poi:{location}:{poi_type}:{datetime.now().strftime('%Y%m%d')}"
        return await self._get_cached_data(cache_key)
    
    async def cache_user_session(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        ttl: int = 86400  # 24小时
    ) -> Dict[str, Any]:
        """缓存用户会话数据"""
        
        cache_key = f"session:{user_id}"
        return await self._cache_data(cache_key, session_data, ttl)
    
    async def get_cached_user_session(self, user_id: str) -> Dict[str, Any]:
        """获取缓存的用户会话数据"""
        
        cache_key = f"session:{user_id}"
        return await self._get_cached_data(cache_key)
    
    async def _cache_data(self, key: str, data: Dict[str, Any], ttl: int) -> Dict[str, Any]:
        """缓存数据的内部方法"""
        
        try:
            serialized_data = json.dumps(data, ensure_ascii=False, default=str)
            self.redis_client.setex(key, ttl, serialized_data)
            
            return self.format_response({
                "key": key,
                "cached": True,
                "ttl": ttl
            })
            
        except Exception as e:
            return self.format_response(
                None,
                success=False,
                message=f"缓存数据失败: {str(e)}"
            )
    
    async def _get_cached_data(self, key: str) -> Dict[str, Any]:
        """获取缓存数据的内部方法"""
        
        try:
            cached_data = self.redis_client.get(key)
            
            if cached_data is None:
                return self.format_response(
                    None,
                    success=False,
                    message="缓存不存在"
                )
            
            data = json.loads(cached_data)
            
            return self.format_response({
                "key": key,
                "data": data,
                "found": True
            })
            
        except Exception as e:
            return self.format_response(
                None,
                success=False,
                message=f"获取缓存数据失败: {str(e)}"
            )
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        
        try:
            info = self.redis_client.info()
            
            stats = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
            
            # 计算命中率
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            total = hits + misses
            
            if total > 0:
                stats["hit_rate"] = (hits / total) * 100
            else:
                stats["hit_rate"] = 0
            
            return self.format_response(stats)
            
        except Exception as e:
            return self.format_response(
                None,
                success=False,
                message=f"获取缓存统计失败: {str(e)}"
            )
