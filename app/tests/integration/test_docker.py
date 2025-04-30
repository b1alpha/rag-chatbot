import pytest
import requests


@pytest.mark.integration
def test_docker_health_endpoint():
    # Test the health endpoint
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_docker_query_endpoint_validation():
    # Test input validation
    response = requests.post("http://localhost:8000/query", json={"question": ""})
    assert response.status_code == 422  # FastAPI validation error
    assert "detail" in response.json()
