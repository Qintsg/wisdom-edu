"""操作日志中间件使用的日志器与展示映射配置。"""

from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path

from django.conf import settings


LOG_BASE_DIR = Path(settings.BASE_DIR) / "runtime_logs"
LOG_BASE_DIR.mkdir(parents=True, exist_ok=True)

OPERATION_LOG_DIR = LOG_BASE_DIR / "operations"
OPERATION_LOG_DIR.mkdir(parents=True, exist_ok=True)

DEBUG_LOG_DIR = LOG_BASE_DIR / "debug"
DEBUG_LOG_DIR.mkdir(parents=True, exist_ok=True)

DEBUG_LOG_DB_QUERIES = getattr(settings, "DEBUG_LOG_DB_QUERIES", False)
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

ACTION_TYPE_DISPLAY = {
    "create": "创建",
    "update": "更新",
    "delete": "删除",
    "read": "查询",
    "login": "登录",
    "logout": "登出",
    "export": "导出",
    "import": "导入",
    "other": "其他",
}

MODULE_DISPLAY = {
    "users": "用户模块",
    "courses": "课程模块",
    "knowledge": "知识模块",
    "exams": "考试模块",
    "assessments": "测评模块",
    "learning": "学习模块",
    "ai_services": "AI服务",
    "logs": "日志模块",
    "system": "系统管理",
}


# 维护意图：带 ANSI 颜色的控制台日志格式化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ColorFormatter(logging.Formatter):
    """带 ANSI 颜色的控制台日志格式化器。"""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[1;31m",
    }
    RESET = "\033[0m"
    DIM = "\033[2m"

    # 维护意图：Render colored console output for debug log records
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def format(self, record: logging.LogRecord) -> str:
        """Render colored console output for debug log records."""
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = self.formatTime(record, "%H:%M:%S")
        tag = f"{color}[{record.levelname}]{self.RESET}"
        return f"{self.DIM}{timestamp}{self.RESET} {tag} {record.name} | {record.getMessage()}"


# 维护意图：创建或复用操作日志文件 logger
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_operation_logger() -> logging.Logger:
    """创建或复用操作日志文件 logger。"""
    logger = logging.getLogger("operation_logs")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not any(
        isinstance(handler, logging.FileHandler)
        and "operations" in str(getattr(handler, "baseFilename", ""))
        for handler in logger.handlers
    ):
        handler = logging.FileHandler(OPERATION_LOG_DIR / "operations.log", encoding="utf-8")
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
        logger.addHandler(handler)
    return logger


# 维护意图：创建或复用 DEBUG 请求日志 logger
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_debug_logger() -> logging.Logger:
    """创建或复用 DEBUG 请求日志 logger。"""
    logger = logging.getLogger("debug_logs")
    logger.setLevel(logging.INFO if settings.DEBUG else logging.WARNING)
    logger.propagate = False
    if not settings.DEBUG:
        return logger
    if any(
        isinstance(handler, logging.FileHandler)
        and "debug" in str(getattr(handler, "baseFilename", ""))
        for handler in logger.handlers
    ):
        return logger

    today = datetime.now().strftime("%Y-%m-%d")
    debug_handler = logging.FileHandler(DEBUG_LOG_DIR / f"debug_{today}.log", encoding="utf-8")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(debug_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)
    return logger


operation_logger = _build_operation_logger()
debug_logger = _build_debug_logger()


__all__ = [
    "ACTION_TYPE_DISPLAY",
    "MODULE_DISPLAY",
    "DEBUG_LOG_DB_QUERIES",
    "operation_logger",
    "debug_logger",
]
