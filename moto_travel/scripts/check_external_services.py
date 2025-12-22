#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部服务接口检查脚本
检查所有外部API服务的配置和可用性
"""
import sys
import os
import asyncio
from typing import Dict, List, Any, Optional

# 设置UTF-8编码（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 尝试加载配置，如果失败则使用环境变量
try:
    from app.config import settings
except Exception as e:
    print(f"Warning: Cannot load config: {e}")
    print("Will check environment variables directly...")
    settings = None

# 可选：使用loguru，如果没有则使用print
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ServiceChecker:
    """外部服务检查器"""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
    
    def check_config(self, service_name: str, required_keys: List[str]) -> Dict[str, Any]:
        """检查服务配置"""
        result = {
            "service": service_name,
            "configured": True,
            "missing_keys": [],
            "status": "unknown"
        }
        
        for key in required_keys:
            if settings:
                value = getattr(settings, key, None)
            else:
                # 直接从环境变量读取
                env_key = key.upper()
                value = os.getenv(env_key)
            
            if not value:
                result["configured"] = False
                result["missing_keys"].append(key)
        
        if result["configured"]:
            result["status"] = "configured"
        else:
            result["status"] = "missing_config"
        
        return result
    
    async def check_amap_service(self) -> Dict[str, Any]:
        """检查高德地图服务"""
        print("\n[检查] 高德地图API...")
        
        result = self.check_config("高德地图", [
            "amap_api_key",
            "amap_web_service_url"
        ])
        
        if result["configured"]:
            try:
                from app.agents.route_planning.tools.amap_tool import AmapTool
                tool = AmapTool()
                
                # 测试地理编码
                test_result = await tool.geocode("北京市")
                if test_result.get("success"):
                    result["status"] = "available"
                    result["message"] = "[OK] 高德地图API可用"
                else:
                    result["status"] = "error"
                    result["message"] = f"[ERROR] 高德地图API错误: {test_result.get('message', 'Unknown error')}"
            except Exception as e:
                result["status"] = "error"
                result["message"] = f"[ERROR] 高德地图API异常: {str(e)}"
        else:
            result["message"] = f"[WARN] 高德地图API未配置，缺少: {', '.join(result['missing_keys'])}"
        
        return result
    
    async def check_baidu_service(self) -> Dict[str, Any]:
        """检查百度地图服务"""
        print("\n[检查] 百度地图API...")
        
        result = self.check_config("百度地图", [
            "baidu_api_key",
            "baidu_web_service_url"
        ])
        
        if result["configured"]:
            try:
                from app.agents.route_planning.tools.baidu_tool import BaiduMapTool
                tool = BaiduMapTool()
                
                # 测试地理编码
                test_result = await tool.geocode("北京市")
                if test_result.get("success"):
                    result["status"] = "available"
                    result["message"] = "[OK] 百度地图API可用"
                else:
                    result["status"] = "error"
                    result["message"] = f"[ERROR] 百度地图API错误: {test_result.get('message', 'Unknown error')}"
            except Exception as e:
                result["status"] = "error"
                result["message"] = f"[ERROR] 百度地图API异常: {str(e)}"
        else:
            result["message"] = f"[WARN] 百度地图API未配置，缺少: {', '.join(result['missing_keys'])}"
        
        return result
    
    async def check_qweather_service(self) -> Dict[str, Any]:
        """检查和风天气服务"""
        print("\n[检查] 和风天气API...")
        
        result = self.check_config("和风天气", [
            "qweather_api_key",
            "qweather_base_url"
        ])
        
        if result["configured"]:
            try:
                from app.agents.weather.tools.weather_tool import QWeatherTool
                tool = QWeatherTool()
                
                # 测试当前天气
                test_result = await tool.get_current_weather("北京")
                if test_result.get("success"):
                    result["status"] = "available"
                    result["message"] = "[OK] 和风天气API可用"
                else:
                    result["status"] = "error"
                    result["message"] = f"[ERROR] 和风天气API错误: {test_result.get('message', 'Unknown error')}"
            except Exception as e:
                result["status"] = "error"
                result["message"] = f"[ERROR] 和风天气API异常: {str(e)}"
        else:
            result["message"] = f"[WARN] 和风天气API未配置，缺少: {', '.join(result['missing_keys'])}"
        
        return result
    
    async def check_meituan_service(self) -> Dict[str, Any]:
        """检查美团服务"""
        print("\n[检查] 美团API...")
        
        result = self.check_config("美团", [
            "meituan_api_key",
            "meituan_app_secret",
            "meituan_base_url"
        ])
        
        if result["configured"]:
            try:
                from app.agents.hotel.tools.meituan_tool import MeituanHotelTool
                tool = MeituanHotelTool()
                
                # 检查工具是否正常初始化
                if tool:
                    result["status"] = "configured"
                    result["message"] = "[OK] 美团API已配置（需要实际调用测试）"
                else:
                    result["status"] = "error"
                    result["message"] = "[ERROR] 美团API工具初始化失败"
            except Exception as e:
                result["status"] = "error"
                result["message"] = f"[ERROR] 美团API异常: {str(e)}"
        else:
            result["message"] = f"[WARN] 美团API未配置，缺少: {', '.join(result['missing_keys'])}"
        
        return result
    
    async def check_other_hotel_services(self) -> List[Dict[str, Any]]:
        """检查其他酒店服务"""
        services = [
            ("携程", "ctrip_api_key"),
            ("同程", "tongcheng_api_key"),
            ("去哪儿", "qunar_api_key"),
            ("飞猪", "fliggy_api_key")
        ]
        
        results = []
        for name, key_name in services:
            print(f"\n[检查] {name}API...")
            
            result = self.check_config(name, [key_name])
            
            if result["configured"]:
                result["status"] = "configured"
                result["message"] = f"[OK] {name}API已配置（框架已创建，待实现）"
            else:
                result["message"] = f"[WARN] {name}API未配置，缺少: {key_name}"
            
            results.append(result)
        
        return results
    
    async def check_database_service(self) -> Dict[str, Any]:
        """检查数据库服务"""
        print("\n[检查] 数据库服务...")
        
        result = {
            "service": "PostgreSQL",
            "configured": True,
            "status": "unknown",
            "missing_keys": []
        }
        
        required_keys = ["database_url", "redis_url"]
        for key in required_keys:
            if settings:
                value = getattr(settings, key, None)
            else:
                value = os.getenv(key.upper())
            if not value:
                result["configured"] = False
                result["missing_keys"].append(key)
        
        if result["configured"]:
            try:
                from app.database import get_db_session
                # 尝试创建数据库会话（不实际连接）
                result["status"] = "configured"
                result["message"] = "[OK] 数据库配置已设置（需要实际连接测试）"
            except Exception as e:
                result["status"] = "error"
                result["message"] = f"[ERROR] 数据库配置异常: {str(e)}"
        else:
            result["message"] = f"[WARN] 数据库未配置，缺少: {', '.join(result['missing_keys'])}"
        
        return result
    
    async def check_redis_service(self) -> Dict[str, Any]:
        """检查Redis服务"""
        print("\n[检查] Redis服务...")
        
        result = {
            "service": "Redis",
            "configured": True,
            "status": "unknown",
            "missing_keys": []
        }
        
        if settings:
            redis_url = getattr(settings, "redis_url", None)
        else:
            redis_url = os.getenv("REDIS_URL")
        
        if not redis_url:
            result["configured"] = False
            result["missing_keys"].append("redis_url")
        
        if result["configured"]:
            try:
                from tools.cache_tools import RedisCache
                # 检查Redis配置
                result["status"] = "configured"
                result["message"] = "[OK] Redis配置已设置（需要实际连接测试）"
            except Exception as e:
                result["status"] = "error"
                result["message"] = f"[ERROR] Redis配置异常: {str(e)}"
        else:
            result["message"] = f"[WARN] Redis未配置，缺少: redis_url"
        
        return result
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检查"""
        print("=" * 60)
        print("外部服务接口检查")
        print("=" * 60)
        
        # 检查地图服务
        amap_result = await self.check_amap_service()
        baidu_result = await self.check_baidu_service()
        
        # 检查天气服务
        qweather_result = await self.check_qweather_service()
        
        # 检查酒店服务
        meituan_result = await self.check_meituan_service()
        other_hotel_results = await self.check_other_hotel_services()
        
        # 检查数据库服务
        db_result = await self.check_database_service()
        redis_result = await self.check_redis_service()
        
        # 汇总结果
        all_results = {
            "地图服务": [amap_result, baidu_result],
            "天气服务": [qweather_result],
            "酒店服务": [meituan_result] + other_hotel_results,
            "数据存储": [db_result, redis_result]
        }
        
        return all_results
    
    def print_summary(self, results: Dict[str, List[Dict[str, Any]]]):
        """打印检查摘要"""
        print("\n" + "=" * 60)
        print("检查摘要")
        print("=" * 60)
        
        total_services = 0
        configured_services = 0
        available_services = 0
        error_services = 0
        
        for category, services in results.items():
            print(f"\n[{category}]:")
            for service in services:
                total_services += 1
                status = service.get("status", "unknown")
                message = service.get("message", "")
                
                if status == "available":
                    available_services += 1
                    print(f"  [OK] {service['service']}: {message}")
                elif status == "configured":
                    configured_services += 1
                    print(f"  [CONFIG] {service['service']}: {message}")
                elif status == "missing_config":
                    print(f"  [WARN] {service['service']}: {message}")
                elif status == "error":
                    error_services += 1
                    print(f"  [ERROR] {service['service']}: {message}")
                else:
                    print(f"  [UNKNOWN] {service['service']}: 状态未知")
        
        print("\n" + "=" * 60)
        print("统计信息")
        print("=" * 60)
        print(f"总服务数: {total_services}")
        print(f"[OK] 可用服务: {available_services}")
        print(f"[CONFIG] 已配置服务: {configured_services}")
        print(f"[WARN] 未配置服务: {total_services - configured_services - available_services - error_services}")
        print(f"[ERROR] 错误服务: {error_services}")
        
        # 建议
        print("\n" + "=" * 60)
        print("建议")
        print("=" * 60)
        
        if available_services == total_services:
            print("[OK] 所有服务都可用！")
        elif configured_services + available_services == total_services:
            print("[OK] 所有服务都已配置！")
        else:
            print("[WARN] 部分服务未配置，请检查 .env 文件")
            print("       参考 env.example 文件配置所需的环境变量")


async def main():
    """主函数"""
    checker = ServiceChecker()
    results = await checker.run_all_checks()
    checker.print_summary(results)
    
    # 返回结果用于测试
    return results


if __name__ == "__main__":
    asyncio.run(main())

