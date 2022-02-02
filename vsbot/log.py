from loguru import logger

logger.add("error.log", level="ERROR", rotation="100 MB")
logger.add("debug.log", level="DEBUG", rotation="100 MB")
