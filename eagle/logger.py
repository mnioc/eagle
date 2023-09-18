from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | " +
            "<level>{level: <8}</level> | " +
            "<level>{message}</level>"
)
