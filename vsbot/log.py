from loguru import logger

logger.add("volumes/error.log", level="ERROR")
logger.add("volumes/debug.log", level="DEBUG")
