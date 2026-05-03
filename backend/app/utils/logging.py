import logging
import time
from logging import Logger
from logging.handlers import RotatingFileHandler

from app.services.log_service import get_log_file_path

LOGGER_NAME = "echominutes"
LOG_FORMAT = "%(asctime)sZ | %(levelname)s | %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def configure_app_logging() -> Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    log_path = get_log_file_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        log_path,
        maxBytes=512 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def get_app_logger(name: str | None = None) -> Logger:
    base_logger = configure_app_logging()
    return base_logger if not name else base_logger.getChild(name)
