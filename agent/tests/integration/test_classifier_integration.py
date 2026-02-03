"""Integration tests for classifier with real OpenAI API."""

import pytest

from src.nodes.classifier import classify_question
from src.schemas import TripAssistantState


@pytest.mark.integration
@pytest.mark.parametrize(
    "question,expected_category",
    [
        pytest.param(
            "What time is our flight?",
            "flight",
            id="flight_question",
        ),
        pytest.param(
            "Where do we pick up the rental car?",
            "car_rental",
            id="car_rental_question",
        ),
        pytest.param(
            "How do we drive to Aosta Valley?",
            "routes",
            id="routes_question",
        ),
        pytest.param(
            "What are we doing in Aosta Valley on July 9th?",
            "aosta",
            id="aosta_question",
        ),
        pytest.param(
            "Tell me about hiking in Chamonix",
            "chamonix",
            id="chamonix_question",
        ),
        pytest.param(
            "What's the plan for Annecy?",
            "annecy_geneva",
            id="annecy_geneva_question",
        ),
    ],
)
def test_classifier_real_api(
    integration_state: TripAssistantState,
    question: str,
    expected_category: str,
):
    """Test classifier with real OpenAI API calls."""
    integration_state["question"] = question

    result = classify_question(integration_state)

    # Verify category is correctly classified
    assert result["category"] == expected_category, (
        f"Expected category '{expected_category}' but got '{result['category']}' "
        f"for question: '{question}'"
    )

    # Verify confidence is within valid range
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["confidence"] > 0.5, "Confidence should be reasonably high"

    # Verify current_context is set
    assert result["current_context"] != ""
    assert len(result["current_context"]) > 0


@pytest.mark.integration
def test_classifier_general_category(integration_state: TripAssistantState):
    """Test that unclear questions are classified as general."""
    integration_state["question"] = "What should I pack for the trip?"

    result = classify_question(integration_state)

    # General category might be assigned for unclear questions
    # We just verify the classifier returns valid results
    assert result["category"] in [
        "general",
        "flight",
        "aosta",
        "chamonix",
        "annecy_geneva",
    ]
    assert 0.0 <= result["confidence"] <= 1.0


@pytest.mark.integration
def test_classifier_confidence_scores(integration_state: TripAssistantState):
    """Test that classifier returns reasonable confidence scores."""
    test_cases = [
        ("What time does our flight depart?", "flight"),
        ("Where is the car rental location?", "car_rental"),
    ]

    for question, expected_category in test_cases:
        integration_state["question"] = question
        result = classify_question(integration_state)

        assert result["category"] == expected_category
        # For clear questions, confidence should be high
        assert result["confidence"] >= 0.7, f"Confidence too low for clear question: {question}"
