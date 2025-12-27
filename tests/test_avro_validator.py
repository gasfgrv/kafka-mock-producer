from unittest.mock import Mock

import pytest

from src.validators.avro_validator import AvroValidator


def test_init_parses_schema_successfully(basic_schema: dict, mock_logger: Mock):
    validator = AvroValidator(basic_schema, mock_logger)
    assert validator.parsed_schema is not None


def test_is_valid_returns_true_for_matching_schema(basic_schema: dict, mock_logger: Mock):
    validator = AvroValidator(basic_schema, mock_logger)
    message = {"id": "abc", "age": 30}

    assert validator.is_valid(message) is True


def test_is_valid_returns_false_missing_field(basic_schema: dict, mock_logger: Mock):
    validator = AvroValidator(basic_schema, mock_logger)
    message = {"id": "abc"}  # Missing age

    assert validator.is_valid(message) is False


def test_is_valid_returns_false_wrong_type(basic_schema: dict, mock_logger: Mock):
    validator = AvroValidator(basic_schema, mock_logger)
    message = {"id": "abc", "age": "thirty"}

    assert validator.is_valid(message) is False


if __name__ == "__main__":
    pytest.main()
