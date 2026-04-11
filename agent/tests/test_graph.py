"""Tests for graph assembly."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.graph import graph
from src.nodes.classifier import TopicClassification


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
async def test_graph_routes_to_correct_specialist(
    mocker,
    initial_state,
    question,
    expected_category,
    expected_answer,
    expected_source,
) -> None:
    """Test that graph routes questions to correct specialist nodes."""
    initial_state["question"] = question

    # Mock classifier
    mock_classification = TopicClassification(category=expected_category, confidence=0.95)
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=mock_classification)
    mocker.patch("src.nodes.classifier._structured_llm", mock_structured)

    # Mock specialist LLM responses
    mock_response = MagicMock()
    mock_response.content = expected_answer
    mock_specialist_llm = MagicMock()
    mock_specialist_llm.ainvoke = AsyncMock(return_value=mock_response)
    mocker.patch("src.nodes.specialist_factory._llm", mock_specialist_llm)

    mock_general_llm = MagicMock()
    mock_general_llm.ainvoke = AsyncMock(return_value=mock_response)
    mocker.patch("src.nodes.general._llm", mock_general_llm)

    result = await graph.ainvoke(initial_state)

    assert result["category"] == expected_category
    assert result["answer"] == expected_answer
    assert result["source"] == expected_source


async def test_graph_end_to_end_with_answer(mocker, initial_state) -> None:
    """Test end-to-end graph execution returns complete answer."""
    # Mock classifier
    mock_classification = TopicClassification(category="flight", confidence=0.95)
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=mock_classification)
    mocker.patch("src.nodes.classifier._structured_llm", mock_structured)

    # Mock specialist (factory-generated)
    expected_answer = "Your flight departs at 10:00 AM on July 7, 2026"
    mock_response = MagicMock()
    mock_response.content = expected_answer
    mock_specialist_llm = MagicMock()
    mock_specialist_llm.ainvoke = AsyncMock(return_value=mock_response)
    mocker.patch("src.nodes.specialist_factory._llm", mock_specialist_llm)

    result = await graph.ainvoke(initial_state)

    assert "answer" in result
    assert result["answer"] == expected_answer
    assert result["source"] == "flight.txt"
    assert result["confidence"] == 0.95


async def test_graph_routes_unclear_question_to_general(mocker, initial_state) -> None:
    """Test that unclear questions route to general specialist."""
    initial_state["question"] = "What should I pack?"

    # Mock classifier to return general
    mock_classification = TopicClassification(category="general", confidence=0.6)
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=mock_classification)
    mocker.patch("src.nodes.classifier._structured_llm", mock_structured)

    # Mock general specialist
    expected_answer = "Pack hiking boots, warm clothes, and sunscreen"
    mock_response = MagicMock()
    mock_response.content = expected_answer
    mock_general_llm = MagicMock()
    mock_general_llm.ainvoke = AsyncMock(return_value=mock_response)
    mocker.patch("src.nodes.general._llm", mock_general_llm)

    result = await graph.ainvoke(initial_state)

    assert result["category"] == "general"
    assert result["answer"] == expected_answer
    assert result["source"] is None


async def test_graph_preserves_documents_through_flow(mocker, initial_state) -> None:
    """Test that documents are preserved throughout the graph execution."""
    # Mock classifier
    mock_classification = TopicClassification(category="flight", confidence=0.95)
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=mock_classification)
    mocker.patch("src.nodes.classifier._structured_llm", mock_structured)

    # Mock specialist (factory-generated)
    mock_response = MagicMock()
    mock_response.content = "Test answer"
    mock_specialist_llm = MagicMock()
    mock_specialist_llm.ainvoke = AsyncMock(return_value=mock_response)
    mocker.patch("src.nodes.specialist_factory._llm", mock_specialist_llm)

    result = await graph.ainvoke(initial_state)

    assert "documents" in result
    assert len(result["documents"]) == 6
    assert "flight" in result["documents"]
