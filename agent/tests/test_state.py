"""Tests for state module."""

import pytest

from src.schemas import TopicCategory, TripAssistantState


def test_trip_assistant_state_instantiation():
    """Test that TripAssistantState can be instantiated with all required fields."""
    state: TripAssistantState = {
        "question": "What time is our flight?",
        "category": "flight",
        "confidence": 0.95,
        "documents": {"flight": "Flight details..."},
        "current_context": "Flight context",
        "answer": "Your flight is at 10:00 AM",
        "source": "flight.txt",
    }

    assert state["question"] == "What time is our flight?"
    assert state["category"] == "flight"
    assert state["confidence"] == 0.95
    assert state["documents"] == {"flight": "Flight details..."}
    assert state["current_context"] == "Flight context"
    assert state["answer"] == "Your flight is at 10:00 AM"
    assert state["source"] == "flight.txt"


@pytest.mark.parametrize(
    "category",
    [
        pytest.param("flight", id="flight_category"),
        pytest.param("car_rental", id="car_rental_category"),
        pytest.param("routes", id="routes_category"),
        pytest.param("aosta", id="aosta_category"),
        pytest.param("chamonix", id="chamonix_category"),
        pytest.param("annecy_geneva", id="annecy_geneva_category"),
        pytest.param("general", id="general_category"),
    ],
)
def test_valid_topic_categories(category: TopicCategory):
    """Test that all valid TopicCategory values are accepted."""
    state: TripAssistantState = {
        "question": "test question",
        "category": category,
        "confidence": 0.5,
        "documents": {},
        "current_context": "",
        "answer": "",
        "source": None,
    }
    assert state["category"] == category
