from enum import Enum
import logging


class LoggingLevel(Enum):
    DEFAULT = 0
    INFO = 1
    DEBUG = 2


class ColourFormatter(logging.Formatter):
    COLOURS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[1;31m",  # Bold Red
    }
    RESET = "\033[0m"

    def format(self, record):
        colour = self.COLOURS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{colour}{message}{self.RESET}"


def set_log_level(level: LoggingLevel):
    formatter = ColourFormatter("[%(levelname)s]: %(message)s")
    if level == LoggingLevel.DEFAULT:
        pass
    elif level == LoggingLevel.INFO:
        logger.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)
    elif level == LoggingLevel.DEBUG:
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
        formatter = ColourFormatter("[%(levelname)s] (%(filename)s:%(lineno)d): %(message)s")

    handler.setFormatter(formatter)


logger = logging.getLogger(__package__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
formatter = ColourFormatter("[%(levelname)s]: %(message)s")
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)

logger.propagate = False
