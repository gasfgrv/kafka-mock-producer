from unittest.mock import Mock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.api.producer_controller import create_producer_blueprint


@pytest.fixture
def mock_producer_service() -> Mock:
    return Mock()


@pytest.fixture
def client(mock_producer_service: Mock, mock_logger: Mock) -> FlaskClient:
    app = Flask(__name__)
    app.testing = True
    blueprint = create_producer_blueprint(mock_producer_service, mock_logger)
    app.register_blueprint(blueprint)
    return app.test_client()


def test_produce_success_returns_200(client: FlaskClient):
    payload = {"topic": "test", "message": {"k": "v"}}
    response = client.post("/produce", json=payload)

    assert response.status_code == 200
    assert response.json == {"status": "ok", "topic": "test"}


def test_produce_missing_fields_returns_400(client: FlaskClient):
    response = client.post("/produce", json={})

    assert response.status_code == 400
    assert "must be provided" in response.json["error"]


def test_produce_validation_error_returns_400(client: FlaskClient, mock_producer_service: Mock):
    mock_producer_service.produce.side_effect = ValueError("Invalid schema")

    payload = {"topic": "test", "message": {}}
    response = client.post("/produce", json=payload)

    assert response.status_code == 400
    assert response.json["error"] == "topic and message must be provided"


def test_produce_internal_error_returns_500(client: FlaskClient, mock_producer_service: Mock):
    mock_producer_service.produce.side_effect = Exception("Boom")

    payload = {"topic": "test", "message": {"k": "v"}}
    response = client.post("/produce", json=payload)

    assert response.status_code == 500
    assert response.json["error"] == "Internal server error"


if __name__ == "__main__":
    pytest.main()
