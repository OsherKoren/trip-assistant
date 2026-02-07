"""Tests for FastAPI routes and middleware."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.conftest import MockGraph


def test_post_messages_success(client: TestClient, mock_graph_result: dict[str, Any]) -> None:
    """Test POST /api/messages returns successful response."""
    response = client.post("/api/messages", json={"question": "What time is our flight?"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == mock_graph_result["answer"]
    assert data["category"] == mock_graph_result["category"]
    assert data["confidence"] == mock_graph_result["confidence"]
    assert data["source"] == mock_graph_result["source"]


def test_post_messages_validation_empty_question(client: TestClient) -> None:
    """Test POST /api/messages rejects empty question."""
    response = client.post("/api/messages", json={"question": ""})

    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()


def test_post_messages_validation_whitespace_question(client: TestClient) -> None:
    """Test POST /api/messages rejects whitespace-only question."""
    response = client.post("/api/messages", json={"question": "   "})

    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()


def test_post_messages_agent_error(client: TestClient) -> None:
    """Test POST /api/messages handles agent invocation errors."""
    from app.dependencies import get_graph
    from app.main import app

    # Create a mock that raises an exception
    class ErrorGraph:
        def invoke(self, _state: dict[str, Any]) -> dict[str, Any]:
            raise Exception("Agent error")

        async def ainvoke(self, _state: dict[str, Any]) -> dict[str, Any]:
            raise Exception("Agent error")

    # Override dependency with error-raising mock
    def mock_error_graph() -> ErrorGraph:
        return ErrorGraph()

    app.dependency_overrides[get_graph] = mock_error_graph

    try:
        response = client.post("/api/messages", json={"question": "What time is our flight?"})

        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "Processing failed"
    finally:
        # Restore original mock
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "category",
    [
        "flight",
        "car_rental",
        "routes",
        "accommodation",
        "activities",
        "general",
        "packing",
    ],
)
def test_post_messages_all_categories(client: TestClient, category: str) -> None:
    """Test POST /api/messages handles all agent categories."""
    from app.dependencies import get_graph
    from app.main import app

    # Create mock with specific category
    mock_result = {
        "answer": f"Information about {category}",
        "category": category,
        "confidence": 0.85,
        "source": f"{category}.txt",
    }
    category_graph = MockGraph(return_value=mock_result)

    # Override dependency for this test
    def mock_category_graph() -> MockGraph:
        return category_graph

    app.dependency_overrides[get_graph] = mock_category_graph

    try:
        response = client.post("/api/messages", json={"question": f"Tell me about {category}"})

        assert response.status_code == 200
        data = response.json()
        assert data["category"] == category
        assert data["confidence"] == 0.85
    finally:
        # Restore original mock
        app.dependency_overrides.clear()


def test_get_health_success(client: TestClient) -> None:
    """Test GET /api/health returns healthy status."""
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "trip-assistant-api"


def test_get_health_includes_version(client: TestClient) -> None:
    """Test GET /api/health includes service version."""
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_cors_headers_present(client: TestClient) -> None:
    """Test CORS headers are present in responses."""
    response = client.post(
        "/api/messages",
        json={"question": "What time is our flight?"},
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers


def test_cors_preflight_options(client: TestClient) -> None:
    """Test CORS preflight OPTIONS request."""
    response = client.options(
        "/api/messages",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers


def test_request_id_header_present(client: TestClient) -> None:
    """Test X-Request-ID header is added to responses."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert "x-request-id" in response.headers
    # In test environment, should return "local"
    assert response.headers["x-request-id"] == "local"
