"""Shared fixtures for node tests."""

import pytest

from src.nodes.classifier import TopicClassification
from src.state import TopicCategory, TripAssistantState


@pytest.fixture
def sample_documents() -> dict[str, str]:
    """Sample trip documents for testing."""
    return {
        "flight": "Flight: El Al LY345, departs 10:00 AM",
        "car_rental": "Car rental: Sixt at Geneva Airport",
        "routes_to_aosta": "Routes to Aosta: 3 options available",
        "aosta_valley": "Aosta valley itinerary July 8-11",
        "chamonix": "Chamonix itinerary July 12-16",
        "annecy_geneva": "Annecy and Geneva itinerary July 16-20",
    }


@pytest.fixture
def sample_state(sample_documents: dict[str, str]) -> TripAssistantState:
    """Create a sample state for testing."""
    return {
        "question": "What time is our flight?",
        "category": "general",
        "confidence": 0.0,
        "documents": sample_documents,
        "current_context": "",
        "answer": "",
        "source": None,
    }


@pytest.fixture
def mock_classifier_llm(mocker):
    """Reusable LLM mock for classifier tests.

    Returns a function that accepts category and confidence,
    and mocks the ChatOpenAI LLM to return that classification.

    Usage:
        mock_classifier_llm("flight", 0.95)
        result = classify_question(state)
    """

    def _mock(category: TopicCategory, confidence: float):
        mock = mocker.patch("src.nodes.classifier.ChatOpenAI")
        mock.return_value.with_structured_output.return_value.invoke.return_value = (
            TopicClassification(category=category, confidence=confidence)
        )
        return mock

    return _mock
