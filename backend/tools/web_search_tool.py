"""
网络搜索工具 - 使用百度搜索API
适用于中文搜索的LangChain工具
"""

import os
import requests
from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger


class WebSearchInput(BaseModel):
    """网络搜索输入模型"""
    query: str = Field(description="搜索查询内容")


class WebSearchTool(BaseTool):
    """网络搜索工具 - 使用百度搜索API"""
    name = "web_search"
    description = "使用百度搜索API搜索网络内容，适用于中文搜索"
    args_schema = WebSearchInput
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("BAIDU_SEARCH_API_KEY")
        self.search_id = os.getenv("BAIDU_SEARCH_ID")
    
    def _run(self, query: str) -> str:
        """执行网络搜索"""
        try:
            logger.info(f"执行网络搜索: {query}")
            
            if not self.api_key or not self.search_id:
                logger.warning("百度搜索API密钥未配置，使用模拟搜索结果")
                return f"模拟搜索结果：关于'{query}'的信息（请配置百度搜索API密钥以获取真实结果）"
            
            # 百度搜索API调用
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.search_id,
                "q": query,
                "num": 5
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("items", []):
                    results.append(f"标题: {item.get('title', '')}\n链接: {item.get('link', '')}\n摘要: {item.get('snippet', '')}")
                
                return "\n\n".join(results) if results else f"未找到关于'{query}'的搜索结果"
            else:
                logger.error(f"百度搜索API调用失败: {response.status_code}")
                return f"搜索服务暂时不可用，请稍后重试"
                
        except Exception as e:
            logger.error(f"网络搜索工具执行失败: {e}")
            return f"搜索时出现错误: {str(e)}"
