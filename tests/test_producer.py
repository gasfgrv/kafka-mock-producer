from datetime import datetime
import hashlib
import json
from typing import Generator
from unittest.mock import patch, Mock
from uuid import UUID

import pytest
from freezegun import freeze_time

from src.kafka.producer import KafkaProducerService


@pytest.fixture
def mock_dependencies() -> Generator:
    with patch("src.kafka.producer.SchemaRegistryClient") as mock_sr, \
            patch("src.kafka.producer.AvroSerializer") as mock_serializer, \
            patch("src.kafka.producer.SerializingProducer") as mock_producer:
        yield mock_sr, mock_serializer, mock_producer


def test_init_configures_producer_correctly(mock_dependencies: Generator, basic_schema: dict):
    mock_sr_cls, mock_serializer_cls, mock_producer_cls = mock_dependencies

    mock_sr_instance = Mock()
    mock_sr_cls.return_value = mock_sr_instance

    mock_serializer_instance = Mock()
    mock_serializer_cls.return_value = mock_serializer_instance

    _ = KafkaProducerService(
        broker="localhost:9092",
        schema_registry_url="http://localhost:8081",
        schema=basic_schema
    )

    mock_sr_cls.assert_called_once_with({"url": "http://localhost:8081"})

    mock_serializer_cls.assert_called_once_with(
        schema_registry_client=mock_sr_instance,
        schema_str=json.dumps(basic_schema),
        to_dict=None
    )

    mock_producer_cls.assert_called_once_with({
        "bootstrap.servers": "localhost:9092",
        "value.serializer": mock_serializer_instance
    })


@freeze_time("2024-01-01T00:00:00")
@patch("src.kafka.producer.uuid4")
def test_send_calls_produce_and_flush(mock_uuid: Mock, mock_dependencies: Generator, basic_schema: dict):
    mock_uuid.return_value = UUID("123e4567-e89b-12d3-a456-426614174000")

    _, _, mock_producer_cls = mock_dependencies
    mock_producer_instance = Mock()
    mock_producer_cls.return_value = mock_producer_instance

    service = KafkaProducerService(
        broker="localhost",
        schema_registry_url="http://sr",
        schema=basic_schema
    )

    topic = "my-topic"
    record = {"id": "1"}

    hash_dict = record.copy()
    hash_dict.update({"timestamp": datetime.now().isoformat(),
                     "uuid": "123e4567-e89b-12d3-a456-426614174000"})
    serialized_record = json.dumps(hash_dict, sort_keys=True).encode("utf-8")
    key = hashlib.md5(serialized_record).hexdigest()

    service.send(topic, record)

    mock_producer_instance.produce.assert_called_once_with(
        topic=topic, key=key, value=record)
    mock_producer_instance.flush.assert_called_once()


if __name__ == "__main__":
    pytest.main()
