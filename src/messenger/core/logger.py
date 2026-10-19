import logging
import sys
from messenger.core.config import settings


def setup_logging():
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    file_handler = logging.FileHandler(settings.LOG_FILE_PATH, encoding="utf_8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if settings.ENABLE_CONSOLE_LOG:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
