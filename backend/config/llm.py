# 导入必要的模块
import os
from langchain_openai import ChatOpenAI
from langchain_dashscope import ChatTongyi
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger

# 配置qwen-plus模型（通过阿里云DashScope API）
def get_qwen_model(temperature: float = 0.3, max_tokens: int = 8096):
    """获取配置好的qwen-plus模型实例"""
    try:
        # 使用LangChain的ChatTongyi类调用qwen模型
        model = ChatTongyi(
            model_name="qwen-plus",
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        logger.info("成功初始化qwen-plus模型")
        return model
    except Exception as e:
        logger.error(f"初始化qwen-plus模型失败: {e}")
        # 备用方案：使用OpenAI兼容接口
        return ChatOpenAI(
            model="qwen-plus",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=temperature,
            max_tokens=max_tokens,
        )

# 主要模型配置
model = get_qwen_model(temperature=0.3, max_tokens=8096)

# 备用模型配置（更保守的参数）
model2 = get_qwen_model(temperature=0.1, max_tokens=4096)

# 轻量级模型配置（使用qwen-turbo）
def get_qwen_turbo_model(temperature: float = 0.1, max_tokens: int = 4096):
    """获取qwen-turbo轻量级模型实例"""
    try:
        model = ChatTongyi(
            model_name="qwen-turbo",
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        logger.info("成功初始化qwen-turbo模型")
        return model
    except Exception as e:
        logger.error(f"初始化qwen-turbo模型失败: {e}")
        return get_qwen_model(temperature, max_tokens)

model_zero = get_qwen_turbo_model(temperature=0.1, max_tokens=4096)
