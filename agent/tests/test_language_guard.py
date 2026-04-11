"""Tests for the language_guard node."""

from unittest.mock import AsyncMock, MagicMock

from src.graph import graph
from src.nodes.classifier import TopicClassification
from src.nodes.language_guard import UNSUPPORTED_LANGUAGE_MSG, language_guard
from src.schemas import TripAssistantState


async def test_hebrew_input_is_blocked(sample_state: TripAssistantState) -> None:
    """Hebrew question should set answer and category."""
    sample_state["question"] = "מה שעת הטיסה?"

    result = await language_guard(sample_state)

    assert result["answer"] == UNSUPPORTED_LANGUAGE_MSG
    assert result["category"] == "general"
    assert result["confidence"] == 0.0


async def test_english_input_passes_through(sample_state: TripAssistantState) -> None:
    """English question should return empty dict (no state change)."""
    sample_state["question"] = "What time is our flight?"

    result = await language_guard(sample_state)

    assert result == {}


async def test_mixed_hebrew_english_is_blocked(sample_state: TripAssistantState) -> None:
    """Mixed Hebrew/English input should be blocked."""
    sample_state["question"] = "What is שלום?"

    result = await language_guard(sample_state)

    assert result["answer"] == UNSUPPORTED_LANGUAGE_MSG


async def test_empty_question_passes_through(sample_state: TripAssistantState) -> None:
    """Empty string should not be blocked (no Hebrew chars)."""
    sample_state["question"] = ""

    result = await language_guard(sample_state)

    assert result == {}


async def test_other_languages_pass_through(sample_state: TripAssistantState) -> None:
    """Non-Hebrew, non-English input (e.g. French) passes through."""
    sample_state["question"] = "Quelle heure est notre vol?"

    result = await language_guard(sample_state)

    assert result == {}


async def test_graph_short_circuits_on_hebrew(mocker, initial_state) -> None:
    """Graph should return fixed message for Hebrew input without calling classifier."""
    from src.graph import graph

    initial_state["question"] = "מה שעת הטיסה?"

    # Classifier should NOT be called
    mock_structured = mocker.patch("src.nodes.classifier._structured_llm")

    result = await graph.ainvoke(initial_state)

    assert result["answer"] == UNSUPPORTED_LANGUAGE_MSG
    mock_structured.ainvoke.assert_not_called()


async def test_graph_proceeds_normally_for_english(mocker, initial_state) -> None:
    """Graph should proceed to classifier for English input."""
    initial_state["question"] = "What time is our flight?"

    mock_classification = TopicClassification(category="flight", confidence=0.95)
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=mock_classification)
    mocker.patch("src.nodes.classifier._structured_llm", mock_structured)

    mock_response = MagicMock()
    mock_response.content = "Your flight departs at 10:00 AM"
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    mocker.patch("src.nodes.specialist_factory._llm", mock_llm)

    result = await graph.ainvoke(initial_state)

    assert result["answer"] == "Your flight departs at 10:00 AM"
    mock_structured.ainvoke.assert_called_once()
