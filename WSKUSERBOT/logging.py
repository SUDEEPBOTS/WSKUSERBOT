import logging
import sys
from pathlib import Path


LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "bot.log"


class ColorFormatter(logging.Formatter):
    GREY = "\033[38;5;244m"
    BLUE = "\033[38;5;39m"
    YELLOW = "\033[38;5;214m"
    RED = "\033[38;5;196m"
    BOLD_RED = "\033[38;5;196;1m"
    RESET = "\033[0m"

    FORMATS = {
        logging.DEBUG: GREY,
        logging.INFO: BLUE,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }

    def format(self, record):
        color = self.FORMATS.get(record.levelno, self.RESET)
        formatter = logging.Formatter(
            f"{color}%(asctime)s | %(levelname)-8s | %(name)s | %(message)s{self.RESET}",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return formatter.format(record)


def setup():
    logger = logging.getLogger("WSKUSERBOT")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColorFormatter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


LOGGER = setup()
