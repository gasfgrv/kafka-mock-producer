from unittest.mock import patch, MagicMock

import pytest

from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestProduceMessage:
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.schema = {
            "type": "record",
            "name": "User",
            "fields": [
                {
                    "name": "id",
                    "type": "int"
                }
            ]
        }
        self.patcher_get_avro = patch("main._get_avro", return_value=self.schema)
        self.patcher_parse_schema = patch("main.parse_schema", return_value=self.schema)
        self.mock_get_avro = self.patcher_get_avro.start()
        self.mock_parse_schema = self.patcher_parse_schema.start()
        yield
        self.patcher_get_avro.stop()
        self.patcher_parse_schema.stop()

    @patch("main._topic_exists", return_value=True)
    @patch("main._validate_message", return_value=True)
    @patch("main.SerializingProducer")
    @patch("main.AvroSerializer")
    @patch("main.SchemaRegistryClient")
    def test_success(self, mock_schema_client, mock_avro_serializer, mock_producer, mock_validate, mock_topic_exists,
                     client):
        # Arrange
        mock_producer.return_value.produce = MagicMock()
        mock_producer.return_value.flush = MagicMock()
        data = {
            "topic": "test-topic",
            "message": {
                "id": 1
            }
        }

        # Act
        response = client.post("/produce", json=data)

        # Assert
        mock_schema_client.assert_called()
        mock_avro_serializer.assert_called()
        mock_validate.assert_called()
        mock_topic_exists.assert_called()

        assert response.status_code == 200
        assert response.json["status"] == "ok"
        assert response.json["topic"] == "test-topic"
        assert response.json["message"] == {"id": 1}

    @patch("main._topic_exists", return_value=True)
    @patch("main._validate_message", return_value=False)
    def test_invalid_avro(self, mock_validate, mock_topic_exists, client):
        # Arrange
        data = {
            "topic": "test-topic",
            "message": {
                "id": "not-an-int"
            }
        }

        # Act
        response = client.post("/produce", json=data)

        # Assert
        mock_validate.assert_called()
        mock_topic_exists.assert_called()

        assert response.status_code == 400
        assert "Avro" in response.json["error"]

    @patch("main._topic_exists", return_value=False)
    def test_topic_not_exists(self, mock_topic_exists, client):
        # Arrange
        data = {
            "topic": "missing-topic",
            "message":
                {
                    "id": 1
                }
        }

        # Act
        response = client.post("/produce", json=data)

        # Assert
        mock_topic_exists.assert_called()

        assert response.status_code == 404
        assert "não existe" in response.json["erros"]

    def test_missing_fields(self, client):
        # Act
        response = client.post("/produce", json={})

        # Assert
        assert response.status_code == 400
        assert "Campos obrigatórios" in response.json["error"]

    @patch("main._topic_exists", return_value=True)
    @patch("main._validate_message", return_value=True)
    @patch("main.SerializingProducer")
    @patch("main.AvroSerializer")
    @patch("main.SchemaRegistryClient")
    def test_kafka_exception(self, mock_schema_client, mock_avro_serializer, mock_producer, mock_validate,
                             mock_topic_exists, client):
        # Arrange
        mock_producer.return_value.produce.side_effect = Exception("Kafka error")

        data = {
            "topic": "test-topic",
            "message": {
                "id": 1
            }
        }

        # Act
        response = client.post("/produce", json=data)

        # Assert
        mock_schema_client.assert_called()
        mock_avro_serializer.assert_called()
        mock_validate.assert_called()
        mock_topic_exists.assert_called()

        assert response.status_code == 500
        assert "Kafka error" in response.json["error"]
