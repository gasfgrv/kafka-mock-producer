from unittest.mock import patch

import pytest
from confluent_kafka import KafkaException

from main import app, topic_exists, validate_message


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_produce_missing_fields(client):
    data = {}

    response = client.post("/produce", json=data)

    assert response.status_code == 400
    assert "Campos obrigatórios" in response.get_json()["error"]


@patch("main.topic_exists", return_value=False)
def test_produce_topic_not_exists(mock_topic_exists, client):
    data = {
        "topic": "notopic",
        "message": {
            "foo": "bar"
        }
    }

    response = client.post("/produce", json=data)

    assert response.status_code == 404
    assert "Tópico" in response.get_json()["erros"]


@patch("main.topic_exists", return_value=True)
@patch("main.validate_message", return_value=False)
def test_produce_invalid_schema(mock_validate, mock_topic_exists, client):
    data = {
        "topic": "mytopic",
        "message": {
            "foo": "bar"
        }
    }

    response = client.post("/produce", json=data)

    assert response.status_code == 400
    assert "conformidade" in response.get_json()["error"]


@patch("main.topic_exists", return_value=True)
@patch("main.validate_message", return_value=True)
@patch("main.producer")
def test_produce_kafka_error(mock_producer, mock_validate, mock_topic_exists, client):
    mock_producer.produce.side_effect = Exception("Kafka error")
    data = {
        "topic": "mytopic",
        "message": {
            "foo": "bar"
        }
    }

    response = client.post("/produce", json=data)

    assert response.status_code == 500
    assert "Kafka error" in response.get_json()["error"]


@patch("main.topic_exists", return_value=True)
@patch("main.validate_message", return_value=True)
@patch("main.producer")
def test_produce_success(mock_producer, mock_validate, mock_topic_exists, client):
    mock_producer.produce.return_value = None
    mock_producer.flush.return_value = None
    data = {
        "topic": "mytopic",
        "message": {
            "foo": "bar"
        }
    }

    response = client.post("/produce", json=data)
    resp_json = response.get_json()

    assert response.status_code == 200
    assert resp_json["status"] == "ok"
    assert resp_json["topic"] == "mytopic"
    assert resp_json["message"] == {"foo": "bar"}


@patch("main.admin_client")
def test_topic_exists_true(mock_admin_client):
    mock_admin_client.list_topics.return_value.topics = {"exists": None}

    assert topic_exists("exists") is True


@patch("main.admin_client")
def test_topic_exists_false(mock_admin_client):
    mock_admin_client.list_topics.return_value.topics = {}

    assert topic_exists("notfound") is False


@patch("main.admin_client")
def test_topic_exists_kafka_exception(mock_admin_client):
    mock_admin_client.list_topics.side_effect = KafkaException("error")

    assert topic_exists("any") is False


def test_validate_message_valid():
    schema = {
        "type": "record",
        "name": "Test",
        "fields": [
            {"name": "foo",
             "type": "string"
             }
        ]
    }
    message = {"foo": "bar"}

    assert validate_message(schema, message) is True


def test_validate_message_invalid():
    schema = {
        "type": "record",
        "name": "Test",
        "fields": [
            {
                "name": "foo",
                "type": "string"
            }
        ]
    }
    message = {"bar": "baz"}
    
    assert validate_message(schema, message) is False
