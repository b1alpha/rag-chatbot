from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.unit
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.unit
def test_query_endpoint_success(client):
    mock_qa_chain = MagicMock()
    mock_qa_chain.invoke.return_value = {"result": "Test answer"}

    mock_retriever = MagicMock()
    mock_retriever.as_retriever.return_value = MagicMock()

    mock_chat = MagicMock()

    with (
        patch("app.rag_pipeline.get_retriever") as mock_get_retriever,
        patch("app.rag_pipeline.RetrievalQA") as mock_retrieval_qa,
        patch("app.rag_pipeline.ChatOpenAI") as mock_chat_openai,
    ):
        mock_get_retriever.return_value = mock_retriever
        mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
        mock_chat_openai.return_value = mock_chat

        response = client.post(
            "/query", json={"question": "What is the capital of France?"}
        )
        assert response.status_code == 200
        assert response.json() == {"answer": "Test answer"}


@pytest.mark.unit
def test_query_endpoint_validation(client):
    # Test empty question
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422
    assert "question" in response.json()["detail"][0]["loc"]

    # Test missing question
    response = client.post("/query", json={})
    assert response.status_code == 422
    assert "question" in response.json()["detail"][0]["loc"]

    # Test non-string question
    response = client.post("/query", json={"question": 123})
    assert response.status_code == 422
    assert "question" in response.json()["detail"][0]["loc"]


@pytest.mark.unit
def test_query_endpoint_value_error(client):
    with patch("app.rag_pipeline.get_retriever") as mock_get_retriever:
        mock_get_retriever.side_effect = ValueError("Invalid question")
        response = client.post("/query", json={"question": "test"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid question"


@pytest.mark.unit
def test_query_endpoint_generic_error(client):
    with patch("app.rag_pipeline.get_retriever") as mock_get_retriever:
        mock_get_retriever.side_effect = Exception("Something went wrong")
        response = client.post("/query", json={"question": "test"})
        assert response.status_code == 500
        assert response.json()["detail"] == "Something went wrong"
