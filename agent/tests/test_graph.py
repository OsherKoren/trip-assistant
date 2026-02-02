"""Tests for graph assembly."""

import pytest

from src.documents import load_documents
from src.graph import graph
from src.nodes.classifier import TopicClassification


@pytest.fixture
def initial_state():
    """Create initial state with question and loaded documents."""
    return {
        "question": "What time is our flight?",
        "category": "general",
        "confidence": 0.0,
        "documents": load_documents(),
        "current_context": "",
        "answer": "",
        "source": None,
    }


@pytest.mark.parametrize(
    "question,expected_category,expected_answer,expected_source",
    [
        pytest.param(
            "What time is our flight?",
            "flight",
            "Your flight departs at 10:00 AM",
            "flight.txt",
            id="flight_routing",
        ),
        pytest.param(
            "Where do we pick up the car?",
            "car_rental",
            "Pick up at Geneva Airport",
            "car_rental.txt",
            id="car_rental_routing",
        ),
        pytest.param(
            "How do we get to Aosta?",
            "routes",
            "Take the scenic mountain route",
            "routes_to_aosta.txt",
            id="routes_routing",
        ),
        pytest.param(
            "What's planned for July 9?",
            "aosta",
            "Hiking in Aosta Valley",
            "aosta_valley.txt",
            id="aosta_routing",
        ),
    ],
)
def test_graph_routes_to_correct_specialist(
    mocker,
    initial_state,
    question,
    expected_category,
    expected_answer,
    expected_source,
):
    """Test that graph routes questions to correct specialist nodes."""
    initial_state["question"] = question

    # Mock classifier
    mock_classification = TopicClassification(category=expected_category, confidence=0.95)
    mocker.patch(
        "src.nodes.classifier.ChatOpenAI"
    ).return_value.with_structured_output.return_value.invoke.return_value = mock_classification

    # Mock specialist LLM responses
    for module in [
        "flight",
        "car_rental",
        "routes",
        "aosta",
        "chamonix",
        "annecy_geneva",
        "general",
    ]:
        mock_llm = mocker.patch(f"src.nodes.{module}.ChatOpenAI")
        mock_llm.return_value.invoke.return_value.content = expected_answer

    result = graph.invoke(initial_state)

    assert result["category"] == expected_category
    assert result["answer"] == expected_answer
    assert result["source"] == expected_source


def test_graph_end_to_end_with_answer(mocker, initial_state):
    """Test end-to-end graph execution returns complete answer."""
    # Mock classifier
    mock_classification = TopicClassification(category="flight", confidence=0.95)
    mocker.patch(
        "src.nodes.classifier.ChatOpenAI"
    ).return_value.with_structured_output.return_value.invoke.return_value = mock_classification

    # Mock specialist
    expected_answer = "Your flight departs at 10:00 AM on July 7, 2026"
    mocker.patch(
        "src.nodes.flight.ChatOpenAI"
    ).return_value.invoke.return_value.content = expected_answer

    result = graph.invoke(initial_state)

    assert "answer" in result
    assert result["answer"] == expected_answer
    assert result["source"] == "flight.txt"
    assert result["confidence"] == 0.95


def test_graph_routes_unclear_question_to_general(mocker, initial_state):
    """Test that unclear questions route to general specialist."""
    initial_state["question"] = "What should I pack?"

    # Mock classifier to return general
    mock_classification = TopicClassification(category="general", confidence=0.6)
    mocker.patch(
        "src.nodes.classifier.ChatOpenAI"
    ).return_value.with_structured_output.return_value.invoke.return_value = mock_classification

    # Mock general specialist
    expected_answer = "Pack hiking boots, warm clothes, and sunscreen"
    mocker.patch(
        "src.nodes.general.ChatOpenAI"
    ).return_value.invoke.return_value.content = expected_answer

    result = graph.invoke(initial_state)

    assert result["category"] == "general"
    assert result["answer"] == expected_answer
    assert result["source"] is None


def test_graph_preserves_documents_through_flow(mocker, initial_state):
    """Test that documents are preserved throughout the graph execution."""
    # Mock classifier
    mock_classification = TopicClassification(category="flight", confidence=0.95)
    mocker.patch(
        "src.nodes.classifier.ChatOpenAI"
    ).return_value.with_structured_output.return_value.invoke.return_value = mock_classification

    # Mock specialist
    mocker.patch(
        "src.nodes.flight.ChatOpenAI"
    ).return_value.invoke.return_value.content = "Test answer"

    result = graph.invoke(initial_state)

    assert "documents" in result
    assert len(result["documents"]) == 6
    assert "flight" in result["documents"]
