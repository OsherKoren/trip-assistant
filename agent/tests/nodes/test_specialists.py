"""Tests for specialist nodes."""

import pytest

from src.nodes import (
    handle_annecy_geneva,
    handle_aosta,
    handle_car_rental,
    handle_chamonix,
    handle_flight,
    handle_general,
    handle_routes,
)
from src.prompts import SPECIALIST_PROMPT_TEMPLATE
from src.schemas import TripAssistantState


@pytest.mark.parametrize(
    "handler,source,question,context,expected_answer",
    [
        pytest.param(
            handle_flight,
            "flight.txt",
            "What time is our flight?",
            "Flight: El Al LY345, departs 10:00 AM",
            "Your flight departs at 10:00 AM",
            id="flight_specialist",
        ),
        pytest.param(
            handle_car_rental,
            "car_rental.txt",
            "Where do we pick up the car?",
            "Car rental: Sixt at Geneva Airport",
            "You pick up the car at Geneva Airport",
            id="car_rental_specialist",
        ),
        pytest.param(
            handle_routes,
            "routes_to_aosta.txt",
            "How do we get to Aosta?",
            "Routes to Aosta: 3 options available",
            "There are 3 route options to Aosta",
            id="routes_specialist",
        ),
        pytest.param(
            handle_aosta,
            "aosta_valley.txt",
            "What's planned for July 9?",
            "Aosta valley itinerary July 8-11",
            "On July 9, you have activities in Aosta",
            id="aosta_specialist",
        ),
        pytest.param(
            handle_chamonix,
            "chamonix.txt",
            "Tell me about Lac Blanc hike",
            "Chamonix itinerary July 12-16: Lac Blanc hike",
            "Lac Blanc hike is part of your Chamonix itinerary",
            id="chamonix_specialist",
        ),
        pytest.param(
            handle_annecy_geneva,
            "annecy_geneva.txt",
            "Paragliding information?",
            "Annecy and Geneva: paragliding available",
            "Paragliding is available in Annecy",
            id="annecy_geneva_specialist",
        ),
    ],
)
def test_specialist_generates_answer(
    mock_specialist_llm,
    sample_state: TripAssistantState,
    handler,
    source: str,
    question: str,
    context: str,
    expected_answer: str,
):
    """Test that each specialist generates answer from context."""
    sample_state["question"] = question
    sample_state["current_context"] = context
    mock_specialist_llm(expected_answer)

    result = handler(sample_state)

    assert result["answer"] == expected_answer
    assert result["source"] == source


@pytest.mark.parametrize(
    "handler,expected_source",
    [
        pytest.param(handle_flight, "flight.txt", id="flight_source"),
        pytest.param(handle_car_rental, "car_rental.txt", id="car_rental_source"),
        pytest.param(handle_routes, "routes_to_aosta.txt", id="routes_source"),
        pytest.param(handle_aosta, "aosta_valley.txt", id="aosta_source"),
        pytest.param(handle_chamonix, "chamonix.txt", id="chamonix_source"),
        pytest.param(handle_annecy_geneva, "annecy_geneva.txt", id="annecy_geneva_source"),
        pytest.param(handle_general, None, id="general_source"),
    ],
)
def test_specialist_returns_correct_source(
    mock_specialist_llm,
    sample_state: TripAssistantState,
    handler,
    expected_source: str | None,
):
    """Test that each specialist returns the correct source."""
    mock_specialist_llm("Test answer")

    result = handler(sample_state)

    assert result["source"] == expected_source


def test_flight_handles_empty_context(
    mock_specialist_llm,
    sample_state: TripAssistantState,
):
    """Test that specialists handle empty context gracefully."""
    sample_state["current_context"] = ""
    mock_specialist_llm("I don't have information about that")

    result = handle_flight(sample_state)

    assert "answer" in result
    assert result["source"] == "flight.txt"


def test_specialist_prompt_includes_trip_timeline() -> None:
    """Test that specialist prompt template includes trip timeline reference."""
    assert "Trip timeline reference:" in SPECIALIST_PROMPT_TEMPLATE
    assert "Day 1: July 7" in SPECIALIST_PROMPT_TEMPLATE
    assert "Day 13: July 19" in SPECIALIST_PROMPT_TEMPLATE
    assert "Day 14: July 20" in SPECIALIST_PROMPT_TEMPLATE


def test_specialist_prompt_formats_with_timeline() -> None:
    """Test that the formatted prompt includes timeline for date-specific queries."""
    formatted = SPECIALIST_PROMPT_TEMPLATE.format(
        topic="the Annecy and Geneva itinerary",
        context="Day 13 (July 19): Annecy -> Geneva",
        question="What's planned for July 19?",
    )
    assert "Day 13: July 19" in formatted
    assert "What's planned for July 19?" in formatted
    assert "Day 13 (July 19): Annecy -> Geneva" in formatted


def test_general_specialist_uses_all_documents(
    mock_specialist_llm,
    sample_state: TripAssistantState,
):
    """Test that general specialist can access all documents."""
    sample_state["question"] = "What should I bring?"
    mock_specialist_llm("Bring hiking boots and warm clothes")

    result = handle_general(sample_state)

    assert result["answer"] == "Bring hiking boots and warm clothes"
    assert result["source"] is None
