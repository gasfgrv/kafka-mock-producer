import json
from typing import Generator
from unittest.mock import patch, Mock

import pytest

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


def test_send_calls_produce_and_flush(mock_dependencies: Generator, basic_schema: dict):
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

    service.send(topic, record)

    mock_producer_instance.produce.assert_called_once_with(topic=topic, value=record)
    mock_producer_instance.flush.assert_called_once()


if __name__ == "__main__":
    pytest.main()
