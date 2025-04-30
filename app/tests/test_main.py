from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_query_endpoint():
    # Test with a valid question
    response = client.post(
        "/query",
        json={"question": "What is this document about?"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()

def test_query_endpoint_invalid_input():
    # Test with empty request body
    response = client.post(
        "/query",
        json={}
    )
    assert response.status_code == 422  # Pydantic validation error
    assert "detail" in response.json()

    # Test with empty question
    response = client.post(
        "/query",
        json={"question": ""}
    )
    assert response.status_code == 422  # Pydantic validation error for min_length
    assert "detail" in response.json()
    assert "string should have at least 1 character" in response.json()["detail"][0]["msg"].lower()

    # Test with non-string question
    response = client.post(
        "/query",
        json={"question": 123}
    )
    assert response.status_code == 422  # Pydantic validation error for type
    assert "detail" in response.json()
    assert any("string" in error["type"].lower() for error in response.json()["detail"]) 