from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_get_answer():
    with patch("app.main.get_answer") as mock:
        mock.return_value = "Test answer"
        yield mock


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_endpoint(mock_get_answer):
    response = client.post(
        "/query", json={"question": "What is the capital of France?"}
    )
    assert response.status_code == 200
    assert response.json() == {"answer": "Test answer"}
    mock_get_answer.assert_called_once_with("What is the capital of France?")


def test_query_endpoint_invalid_input():
    # Test empty question
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422

    # Test missing question
    response = client.post("/query", json={})
    assert response.status_code == 422

    # Test non-string question
    response = client.post("/query", json={"question": 123})
    assert response.status_code == 422


def test_query_endpoint_error_handling(mock_get_answer):
    # Test ValueError handling
    mock_get_answer.side_effect = ValueError("Invalid question")
    response = client.post("/query", json={"question": "test"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid question"

    # Test general exception handling
    mock_get_answer.side_effect = Exception("Unexpected error")
    response = client.post("/query", json={"question": "test"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Unexpected error"
