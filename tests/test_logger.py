import importlib
import json
import logging
import sys
from typing import Generator

import pytest
from _pytest.capture import CaptureFixture
from pythonjsonlogger.json import JsonFormatter

from src.config.logger import configure_logger


@pytest.fixture(autouse=True)
def clean_logging_state() -> Generator:
    logging.shutdown()
    importlib.reload(logging)
    yield
    logging.shutdown()
    importlib.reload(logging)


def test_configure_logger_sets_name_and_level():
    logger = configure_logger("test_logger")
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO


def test_configure_logger_uses_stdout_stream():
    logger = configure_logger("test_logger")
    handler = logger.handlers[0]

    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream is sys.stdout


def test_configure_logger_uses_json_formatter():
    logger = configure_logger("test_logger")
    formatter = logger.handlers[0].formatter

    assert isinstance(formatter, JsonFormatter)
    for field in ["%(asctime)s", "%(name)s", "%(levelname)s", "%(message)s"]:
        assert field in formatter._fmt


def test_logger_outputs_structured_json(capsys: CaptureFixture):
    logger = configure_logger("test_logger")

    logger.info("test message")

    captured = capsys.readouterr()
    log_entry = json.loads(captured.out.strip())

    assert log_entry["name"] == "test_logger"
    assert log_entry["levelname"] == "INFO"
    assert log_entry["message"] == "test message"
    assert "asctime" in log_entry


if __name__ == "__main__":
    pytest.main()
