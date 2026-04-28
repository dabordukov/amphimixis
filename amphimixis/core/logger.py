"""Module to operate logging."""

import logging

LOG_FILE_NAME = "amphimixis.log"


def setup_logger(name: str) -> logging.Logger:
    """Create logger with specified name."""
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            handlers=[
                logging.FileHandler(LOG_FILE_NAME, encoding="utf-8"),
            ],
        )

    return logging.getLogger(name.upper())
