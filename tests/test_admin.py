from unittest.mock import Mock, patch

import pytest
from confluent_kafka import KafkaException

from src.kafka.admin import KafkaAdminService


@pytest.fixture
def service(mock_logger: Mock, mock_admin_client: Mock) -> KafkaAdminService:
    with patch("src.kafka.admin.AdminClient", return_value=mock_admin_client):
        return KafkaAdminService(
            broker="localhost:9092",
            logger=mock_logger
        )


def test_topic_exists_returns_true_when_topic_found(service: KafkaAdminService, mock_admin_client: Mock):
    metadata_mock = Mock()
    metadata_mock.topics = {"meu-topico": Mock()}
    mock_admin_client.list_topics.return_value = metadata_mock

    result = service.topic_exists("meu-topico")

    assert result is True
    mock_admin_client.list_topics.assert_called_once_with(timeout=5)


def test_topic_exists_returns_false_when_topic_not_found(service: KafkaAdminService, mock_admin_client: Mock):
    metadata_mock = Mock()
    metadata_mock.topics = {"outro-topico": Mock()}
    mock_admin_client.list_topics.return_value = metadata_mock

    result = service.topic_exists("meu-topico")

    assert result is False


def test_topic_exists_logs_error_on_exception(service: KafkaAdminService, mock_admin_client: Mock, mock_logger: Mock):
    mock_admin_client.list_topics.side_effect = KafkaException("Kafka error")

    result = service.topic_exists("meu-topico")

    assert result is False
    mock_logger.error.assert_called_once()
    assert "Erro verificando tópico" in mock_logger.error.call_args[0][0]


@patch("src.kafka.admin.AdminClient")
def test_admin_client_initialized_with_correct_config(admin_client_cls: Mock, mock_logger: Mock):
    KafkaAdminService(broker="broker:29092", logger=mock_logger)

    admin_client_cls.assert_called_once_with({"bootstrap.servers": "broker:29092"})


if __name__ == "__main__":
    pytest.main()
