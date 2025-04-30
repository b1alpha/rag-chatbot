import pytest
import docker
import time
import requests
from docker.errors import NotFound

@pytest.fixture(scope="module")
def docker_client():
    return docker.from_env()

@pytest.fixture(scope="module")
def docker_image(docker_client):
    # Build the image
    image, _ = docker_client.images.build(
        path=".",
        tag="rag-chatbot:test",
        rm=True  # Remove intermediate containers
    )
    
    yield image
    
    # Cleanup
    try:
        docker_client.images.remove("rag-chatbot:test", force=True)
    except NotFound:
        pass

@pytest.fixture(scope="module")
def docker_container(docker_client, docker_image):
    # Start the container
    container = docker_client.containers.run(
        "rag-chatbot:test",
        detach=True,
        environment={
            "OPENAI_API_KEY": "dummy-key-for-testing"  # Replace with a real key for integration tests
        },
        ports={'8000/tcp': 8000},
        remove=True
    )
    
    # Wait for the container to be ready
    time.sleep(2)  # Give it some time to start
    
    yield container
    
    # Cleanup
    try:
        container.stop()
    except NotFound:
        pass

def test_docker_health_endpoint(docker_container):
    # Test the health endpoint
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_docker_query_endpoint_validation(docker_container):
    # Test input validation
    response = requests.post(
        "http://localhost:8000/query",
        json={"question": ""}
    )
    assert response.status_code == 422  # Pydantic validation error
    
    response = requests.post(
        "http://localhost:8000/query",
        json={}
    )
    assert response.status_code == 422  # Pydantic validation error 