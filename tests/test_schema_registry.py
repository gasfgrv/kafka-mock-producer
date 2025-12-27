import json
from pathlib import Path

import pytest

from src.kafka.schema_registry import AvroSchemaLoader


def test_init_sets_correct_schema_path():
    path = "schemas/test.avsc"
    loader = AvroSchemaLoader(path)
    assert loader.schema_path == path


def test_load_returns_dict_from_valid_file(tmp_path: Path):
    schema_content = {
        "type": "record",
        "name": "Test",
        "fields": [{"name": "id", "type": "string"}]
    }
    schema_file = tmp_path / "schema.avsc"
    schema_file.write_text(json.dumps(schema_content))

    loader = AvroSchemaLoader(str(schema_file))

    result = loader.load()

    assert isinstance(result, dict)
    assert result == schema_content


def test_load_raises_file_not_found_error():
    loader = AvroSchemaLoader("non_existent.avsc")

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_load_raises_json_decode_error_on_invalid_content(tmp_path: Path):
    schema_file = tmp_path / "invalid.avsc"
    schema_file.write_text("{ not valid json }")
    loader = AvroSchemaLoader(str(schema_file))

    with pytest.raises(json.JSONDecodeError):
        loader.load()


if __name__ == "__main__":
    pytest.main()
