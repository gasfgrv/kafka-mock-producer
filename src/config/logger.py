import logging
import sys
from logging import Logger, StreamHandler

from pythonjsonlogger import json as jsonlogger
from pythonjsonlogger.json import JsonFormatter


def configure_logger(name: str) -> Logger:
    logger: Logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler: StreamHandler = logging.StreamHandler(sys.stdout)

    formatter: JsonFormatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        json_ensure_ascii=False
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
