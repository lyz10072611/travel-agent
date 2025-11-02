import sys
import logging
import inspect
from typing import Dict, Any, Callable
from loguru import logger
from pathlib import Path

# 如果不存在则创建日志目录
# LOGS_DIR = Path("logs")
# LOGS_DIR.mkdir(exist_ok=True)


def configure_logger(console_level: str = "INFO", log_format: str = None) -> None:
    """配置loguru日志记录器，包含控制台和文件输出

    参数:
        console_level: 控制台日志的最小级别
        file_level: 文件日志的最小级别
        rotation: 何时轮换日志文件（大小或时间）
        retention: 保留日志文件多长时间
        log_format: 可选的自定义格式字符串
    """
    # 移除默认配置
    logger.remove()

    # 如果没有提供格式，使用默认格式
    if log_format is None:
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    # 添加控制台处理器
    logger.add(
        sys.stderr,
        format=log_format,
        level=console_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # # 添加文件处理器
    # logger.add(
    #     LOGS_DIR / "app.log",
    #     format=log_format,
    #     level=console_level,
    # )


# 拦截标准库日志记录到loguru
class InterceptHandler(logging.Handler):
    """拦截标准库日志记录并重定向到loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        # 如果存在，获取对应的Loguru级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找记录消息的调用者来源
        frame, depth = inspect.currentframe(), 0
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def patch_std_logging():
    """修补所有标准库日志记录器以使用loguru"""
    # 用InterceptHandler替换所有现有处理器
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 更新所有现有日志记录器
    for name in logging.root.manager.loggerDict.keys():
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    # 更新特定的常用库
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]


def setup_logging(console_level: str = "INFO", intercept_stdlib: bool = True) -> None:
    """为整个应用程序设置日志记录

    参数:
        console_level: 控制台输出的最小级别
        file_level: 文件输出的最小级别
        intercept_stdlib: 是否修补标准库日志记录
    """
    # 配置loguru
    configure_logger(console_level=console_level)

    # 可选地修补标准库日志记录
    if intercept_stdlib:
        patch_std_logging()

    # 为日志记录器添加额外上下文
    logger.configure(extra={"app_name": "decipher-research-agent"})

    logger.info("日志记录已成功配置")


def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """包装工具执行的钩子函数"""
    logger.info(f"即将调用{function_name}，参数: {arguments}")
    result = function_call(**arguments)
    logger.info(f"函数调用完成，结果: {result}")
    return result
