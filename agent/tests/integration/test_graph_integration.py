"""Integration tests for complete graph with real OpenAI API."""

import pytest

from src.graph import graph
from src.state import TripAssistantState


@pytest.mark.integration
@pytest.mark.parametrize(
    "question,expected_category,expected_source",
    [
        pytest.param(
            "What time is our flight?",
            "flight",
            "flight.txt",
            id="flight_end_to_end",
        ),
        pytest.param(
            "Where do we pick up the rental car?",
            "car_rental",
            "car_rental.txt",
            id="car_rental_end_to_end",
        ),
        pytest.param(
            "What's the best route to Aosta?",
            "routes",
            "routes_to_aosta.txt",
            id="routes_end_to_end",
        ),
    ],
)
def test_graph_end_to_end_real_api(
    integration_state: TripAssistantState,
    question: str,
    expected_category: str,
    expected_source: str,
):
    """Test complete graph flow with real API calls."""
    integration_state["question"] = question

    result = graph.invoke(integration_state)

    # Verify classification
    assert result["category"] == expected_category

    # Verify answer was generated
    assert "answer" in result
    assert len(result["answer"]) > 0
    assert result["answer"] != ""

    # Verify source is correct
    assert result["source"] == expected_source

    # Verify confidence
    assert 0.0 <= result["confidence"] <= 1.0

    # Verify documents are preserved
    assert "documents" in result
    assert len(result["documents"]) == 6


@pytest.mark.integration
def test_graph_answer_quality(integration_state: TripAssistantState):
    """Test that graph generates relevant, quality answers."""
    integration_state["question"] = "What time does our flight depart?"

    result = graph.invoke(integration_state)

    answer = result["answer"].lower()

    # Answer should be relevant to the question
    # Should mention time or flight details
    assert any(
        keyword in answer for keyword in ["time", "depart", "flight", "10", "am", "pm", "leave"]
    ), f"Answer doesn't seem relevant to flight time: {answer}"

    # Answer should not be too short (low quality)
    assert len(answer) > 10, "Answer is too short"

    # Answer should not be an error message
    assert "error" not in answer.lower()
    assert "sorry" not in answer.lower() or "information" in answer.lower()


@pytest.mark.integration
def test_graph_multiple_categories(integration_state: TripAssistantState):
    """Test graph with questions from different categories."""
    test_questions = [
        ("What time is our flight?", "flight", "flight.txt"),
        ("Where do we pick up the car?", "car_rental", "car_rental.txt"),
        ("What's planned for July 10?", "aosta", "aosta_valley.txt"),
    ]

    for question, expected_category, expected_source in test_questions:
        integration_state["question"] = question

        result = graph.invoke(integration_state)

        assert result["category"] == expected_category
        assert result["source"] == expected_source
        assert len(result["answer"]) > 0
        assert result["confidence"] > 0.5


@pytest.mark.integration
def test_graph_preserves_state(integration_state: TripAssistantState):
    """Test that graph preserves and updates state correctly."""
    integration_state["question"] = "What airline is our flight?"

    result = graph.invoke(integration_state)

    # Original state should be updated
    assert result["question"] == "What airline is our flight?"

    # New fields should be populated
    assert result["category"] != "general" or result["confidence"] > 0
    assert result["answer"] != ""
    assert result["current_context"] != ""

    # Documents should be preserved
    assert result["documents"] == integration_state["documents"]


@pytest.mark.integration
@pytest.mark.slow
def test_graph_general_specialist(integration_state: TripAssistantState):
    """Test general specialist with unclear question."""
    integration_state["question"] = "What should I bring for the trip?"

    result = graph.invoke(integration_state)

    # Should route to general or a specific category
    assert result["category"] in [
        "general",
        "flight",
        "aosta",
        "chamonix",
        "annecy_geneva",
    ]

    # Should generate an answer
    assert len(result["answer"]) > 0

    # General specialist might return None as source
    # or route to a specific category
    assert result["source"] in [
        None,
        "flight.txt",
        "aosta_valley.txt",
        "chamonix.txt",
        "annecy_geneva.txt",
    ]
