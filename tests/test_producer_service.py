from unittest.mock import Mock

import pytest

from src.kafka.admin import KafkaAdminService
from src.kafka.producer import KafkaProducerService
from src.services.producer_service import ProducerService
from src.validators.avro_validator import AvroValidator


@pytest.fixture
def mock_admin() -> Mock:
    admin = Mock(spec=KafkaAdminService)
    admin.topic_exists.return_value = True
    return admin


@pytest.fixture
def mock_validator() -> Mock:
    val = Mock(spec=AvroValidator)
    val.is_valid.return_value = True
    return val


@pytest.fixture
def mock_kafka_producer() -> Mock:
    return Mock(spec=KafkaProducerService)


@pytest.fixture
def producer_service(mock_admin: Mock, mock_validator: Mock, mock_kafka_producer: Mock,
                     mock_logger: Mock) -> ProducerService:
    return ProducerService(
        admin=mock_admin,
        validator=mock_validator,
        producer=mock_kafka_producer,
        logger=mock_logger
    )


def test_produce_success_flow(producer_service: ProducerService, mock_admin: Mock, mock_validator: Mock,
                              mock_kafka_producer: Mock, mock_logger: Mock):
    topic = "valid-topic"
    message = {"id": "1"}

    producer_service.produce(topic, message)

    mock_admin.topic_exists.assert_called_once_with(topic)
    mock_validator.is_valid.assert_called_once_with(message)
    mock_kafka_producer.send.assert_called_once_with(topic, message)
    mock_logger.info.assert_called()


def test_produce_raises_error_if_topic_missing(producer_service: ProducerService, mock_admin: Mock,
                                               mock_kafka_producer: Mock, mock_logger: Mock):
    mock_admin.topic_exists.return_value = False
    topic = "missing-topic"

    with pytest.raises(ValueError, match="does not exist"):
        producer_service.produce(topic, {"id": "1"})

    mock_kafka_producer.send.assert_not_called()
    mock_logger.error.assert_called()


def test_produce_raises_error_if_message_invalid(producer_service: ProducerService, mock_validator: Mock,
                                                 mock_kafka_producer: Mock, mock_logger: Mock):
    mock_validator.is_valid.return_value = False

    with pytest.raises(ValueError, match="is not valid"):
        producer_service.produce("topic", {"id": "1"})

    mock_kafka_producer.send.assert_not_called()
    mock_logger.error.assert_called()


if __name__ == "__main__":
    pytest.main()
