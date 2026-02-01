import logging
import sys
from pathlib import Path

def setup_logging(log_file: str = "decksmith.log", level: int = logging.INFO):
    """
    Sets up the logging configuration.
    """
    # Create a custom logger
    logger = logging.getLogger("decksmith")
    logger.setLevel(level)

    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = logging.FileHandler(log_file, encoding="utf-8")
    c_handler.setLevel(level)
    f_handler.setLevel(level)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    if not logger.hasHandlers():
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger

logger = setup_logging()
