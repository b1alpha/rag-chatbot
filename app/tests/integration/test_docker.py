import time

import docker
import pytest
import requests
from docker.errors import NotFound


@pytest.fixture
def docker_client():
    return docker.from_env()


@pytest.fixture
def docker_image(docker_client):
    # Build the image
    image, _ = docker_client.images.build(
        path=".",
        tag="rag-chatbot:test",
        rm=True,  # Remove intermediate containers
    )

    yield image

    # Cleanup
    try:
        docker_client.images.remove(image.id, force=True)
    except NotFound:
        pass


@pytest.fixture
def docker_container(docker_client, docker_image):
    # Start the container
    container = docker_client.containers.run(
        "rag-chatbot:test",
        detach=True,
        environment={
            "OPENAI_API_KEY": "test-key",
            "CHROMA_PERSIST_DIR": "./chroma_store",
        },
        ports={"8000/tcp": 8000},
    )

    # Wait for the container to be ready
    time.sleep(2)  # Give it some time to start

    yield container

    # Cleanup
    try:
        container.stop()
        container.remove()
    except NotFound:
        pass


@pytest.mark.integration
def test_docker_health_endpoint(docker_container):
    # Test the health endpoint
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_docker_query_endpoint_validation(docker_container):
    # Test input validation
    response = requests.post("http://localhost:8000/query", json={"question": ""})
    assert response.status_code == 422  # FastAPI validation error
    assert "detail" in response.json()
