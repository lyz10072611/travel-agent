from dotenv import load_dotenv
from loguru import logger

# 加载环境变量
logger.info("正在加载环境变量")
load_dotenv()
logger.info("环境变量已加载")

# 导入并设置日志配置
from config.logger import setup_logging

# 使用loguru配置日志
setup_logging(console_level="INFO")

from api.app import app

if __name__ == "__main__":
    logger.info("正在启动TripCraft AI API服务器")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
