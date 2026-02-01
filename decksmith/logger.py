"""
This module configures the logging for the application.
"""

import logging
import sys


def setup_logging(log_file: str = "decksmith.log", level: int = logging.INFO):
    """
    Sets up the logging configuration.
    """
    # Create a custom logger
    log = logging.getLogger("decksmith")
    log.setLevel(level)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    console_handler.setLevel(level)
    file_handler.setLevel(level)

    # Create formatters and add it to handlers
    console_format = logging.Formatter("%(message)s")
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    if not log.hasHandlers():
        log.addHandler(console_handler)
        log.addHandler(file_handler)

    return log


logger = setup_logging()
