"""Integration tests for API endpoints with real OpenAI API calls.

These tests use the real agent graph and make actual OpenAI API calls.
They require:
- OPENAI_API_KEY environment variable
- Agent package installed: uv pip install -e ../agent
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_post_messages_flight_question(integration_client: TestClient) -> None:
    """Test POST /api/messages with real flight question."""
    response = integration_client.post(
        "/api/messages", json={"question": "What time is our flight from Paris to Nice?"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "answer" in data
    assert "category" in data
    assert "confidence" in data

    # Verify answer is not empty
    assert len(data["answer"]) > 0

    # Verify category is flight
    assert data["category"] == "flight"

    # Verify confidence is reasonable
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["confidence"] > 0.5


@pytest.mark.integration
@pytest.mark.parametrize(
    "question,expected_category",
    [
        ("What time is our flight to Nice?", "flight"),
        ("What car did we rent?", "car_rental"),
        ("How do we get from Paris to Chamonix?", "routes"),
        ("What is planned for July 9 in Aosta?", "aosta"),
        ("Tell me about the Lac Blanc hike in Chamonix", "chamonix"),
        ("What can we do near Annecy or Geneva?", "annecy_geneva"),
        ("What is the weather like in July?", "general"),
    ],
)
def test_post_messages_all_categories(
    integration_client: TestClient, question: str, expected_category: str
) -> None:
    """Test POST /api/messages correctly classifies all 7 categories."""
    response = integration_client.post("/api/messages", json={"question": question})

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "answer" in data
    assert "category" in data
    assert "confidence" in data

    # Verify answer is not empty and relevant
    assert len(data["answer"]) > 0

    # Verify category matches expected
    assert data["category"] == expected_category, (
        f"Expected category '{expected_category}', got '{data['category']}' for question: {question}"
    )

    # Verify confidence is reasonable
    assert 0.0 <= data["confidence"] <= 1.0


@pytest.mark.integration
def test_get_health_returns_healthy(integration_client: TestClient) -> None:
    """Test GET /api/health returns healthy status."""
    response = integration_client.get("/api/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "trip-assistant-api"
    assert "version" in data


@pytest.mark.integration
def test_general_question_handling(integration_client: TestClient) -> None:
    """Test general questions are handled with reasonable confidence."""
    response = integration_client.post("/api/messages", json={"question": "Tell me about the trip"})

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "answer" in data
    assert "category" in data
    assert "confidence" in data

    # General questions should have category "general"
    assert data["category"] == "general"

    # Answer should not be empty
    assert len(data["answer"]) > 0

    # Confidence should be present
    assert 0.0 <= data["confidence"] <= 1.0


@pytest.mark.integration
def test_request_id_header_present(integration_client: TestClient) -> None:
    """Test X-Request-ID header is present in responses."""
    response = integration_client.post("/api/messages", json={"question": "What car did we rent?"})

    assert response.status_code == 200

    # Verify request ID header is present
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0
