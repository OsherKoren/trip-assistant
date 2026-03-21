"""Shared fixtures for node tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.nodes.classifier import TopicClassification
from src.schemas import TopicCategory, TripAssistantState


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
        "history": [],
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
    and mocks the module-level _structured_llm to return that classification.

    Usage:
        mock_classifier_llm("flight", 0.95)
        result = await classify_question(state)
    """

    def _mock(category: TopicCategory, confidence: float):
        mock_structured = MagicMock()
        mock_structured.ainvoke = AsyncMock(
            return_value=TopicClassification(category=category, confidence=confidence)
        )
        mocker.patch("src.nodes.classifier._structured_llm", mock_structured)
        return mock_structured

    return _mock


@pytest.fixture
def mock_specialist_llm(mocker):
    """Reusable LLM mock for specialist node tests.

    Returns a function that accepts an answer string,
    and mocks the module-level _llm instances to return that answer.

    Usage:
        mock_specialist_llm("Your flight departs at 10:00 AM")
        result = await handle_flight(state)
    """

    def _mock(answer: str):
        mock_response = MagicMock()
        mock_response.content = answer

        # Patch specialist_factory module-level LLM (used by all factory-generated specialists)
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mocker.patch("src.nodes.specialist_factory._llm", mock_llm)

        # Patch general specialist module-level LLM
        mock_general_llm = MagicMock()
        mock_general_llm.ainvoke = AsyncMock(return_value=mock_response)
        mocker.patch("src.nodes.general._llm", mock_general_llm)

        return mock_llm

    return _mock
