"""Root conftest.py with shared fixtures for all tests."""

import os

import pytest

# Set dummy API key so module-level ChatOpenAI instances can be created without a real key.
# Unit tests mock the LLM, so this value is never used for actual API calls.
os.environ.setdefault("OPENAI_API_KEY", "test-dummy-key")

from src.documents import load_documents
from src.schemas import TripAssistantState


@pytest.fixture
def initial_state() -> TripAssistantState:
    """Initial state with question and loaded documents (for graph-level tests)."""
    return {
        "question": "What time is our flight?",
        "category": "general",
        "confidence": 0.0,
        "documents": load_documents(),
        "current_context": "",
        "answer": "",
        "source": None,
    }


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
