from logging import Logger
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_logger() -> Mock:
    return Mock(spec=Logger)


@pytest.fixture
def basic_schema() -> dict:
    return {
        "type": "record",
        "name": "TestRecord",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "age", "type": "int"}
        ]
    }


@pytest.fixture
def mock_admin_client() -> Mock:
    return Mock()


@pytest.fixture
def mock_producer_instance() -> Mock:
    return Mock()
