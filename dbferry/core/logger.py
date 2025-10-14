import logging
from pathlib import Path

LOG_FILE = Path("dbferry.log")


def setup_logger():
    logger = logging.getLogger("dbferry")
    logger.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)

    # Avoid duplicates
    if not logger.handlers:
        logger.addHandler(fh)

    return logger


logger = setup_logger()
