"""Tests for classifier node."""

import pytest

from src.nodes.classifier import classify_question
from src.state import TripAssistantState


@pytest.mark.parametrize(
    "question,expected_category,expected_doc_key",
    [
        pytest.param(
            "What time is our flight?",
            "flight",
            "flight",
            id="flight_question",
        ),
        pytest.param(
            "Where do we pick up the car?",
            "car_rental",
            "car_rental",
            id="car_rental_question",
        ),
        pytest.param(
            "How do we get to Aosta?",
            "routes",
            "routes_to_aosta",
            id="routes_question",
        ),
        pytest.param(
            "What's planned for July 9?",
            "aosta",
            "aosta_valley",
            id="aosta_question",
        ),
        pytest.param(
            "Tell me about Lac Blanc hike",
            "chamonix",
            "chamonix",
            id="chamonix_question",
        ),
        pytest.param(
            "Paragliding information?",
            "annecy_geneva",
            "annecy_geneva",
            id="annecy_geneva_question",
        ),
    ],
)
def test_classify_question_categories(
    mock_classifier_llm,
    sample_state: TripAssistantState,
    question: str,
    expected_category: str,
    expected_doc_key: str,
):
    """Test that classifier correctly classifies different question types."""
    sample_state["question"] = question
    mock_classifier_llm(expected_category, 0.95)

    result = classify_question(sample_state)

    assert result["category"] == expected_category
    assert result["confidence"] == 0.95
    assert result["current_context"] == sample_state["documents"][expected_doc_key]


def test_classify_question_returns_confidence(
    mock_classifier_llm,
    sample_state: TripAssistantState,
):
    """Test that classifier returns a confidence score between 0 and 1."""
    mock_classifier_llm("flight", 0.87)

    result = classify_question(sample_state)

    assert 0.0 <= result["confidence"] <= 1.0
    assert result["confidence"] == 0.87


def test_classify_question_sets_current_context(
    mock_classifier_llm,
    sample_state: TripAssistantState,
):
    """Test that classifier sets current_context from the correct document."""
    mock_classifier_llm("flight", 0.95)

    result = classify_question(sample_state)

    expected_content = sample_state["documents"]["flight"]
    assert result["current_context"] == expected_content
    assert "El Al LY345" in result["current_context"]


def test_classify_question_general_category(
    mock_classifier_llm,
    sample_state: TripAssistantState,
):
    """Test that unclear questions are classified as general."""
    sample_state["question"] = "What should I bring?"
    mock_classifier_llm("general", 0.6)

    result = classify_question(sample_state)

    assert result["category"] == "general"
    assert result["confidence"] == 0.6
    # For general category, context should be empty or combine all docs
    assert "current_context" in result
