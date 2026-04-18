"""Tests for stream_agent async generator."""

from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import pytest

from src.graph import stream_agent
from src.schemas import TripAssistantState


def _make_stream_event(content: str) -> dict:
    chunk = MagicMock()
    chunk.content = content
    return {"event": "on_chat_model_stream", "data": {"chunk": chunk}}


def _make_other_event(event_name: str) -> dict:
    return {"event": event_name, "data": {}}


async def _async_iter(items: list[object]) -> AsyncGenerator[object, None]:
    for item in items:
        yield item


@pytest.fixture()
def base_state() -> TripAssistantState:
    return TripAssistantState(
        question="What time is our flight?",
        category="flight",
        confidence=0.9,
        documents={},
        current_context="",
        answer="",
        source=None,
        history=[],
    )


@pytest.fixture()
def mock_graph(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    m = MagicMock()
    monkeypatch.setattr("src.graph.graph", m)
    return m


@pytest.mark.asyncio
async def test_stream_agent_yields_tokens(
    mock_graph: MagicMock, base_state: TripAssistantState
) -> None:
    events = [
        _make_stream_event("Your "),
        _make_stream_event("flight "),
        _make_stream_event("departs at 10am."),
    ]
    mock_graph.astream_events.return_value = _async_iter(events)

    tokens = [t async for t in stream_agent(base_state)]

    assert tokens == ["Your ", "flight ", "departs at 10am."]


@pytest.mark.asyncio
async def test_stream_agent_filters_non_stream_events(
    mock_graph: MagicMock, base_state: TripAssistantState
) -> None:
    events = [
        _make_other_event("on_chain_start"),
        _make_stream_event("Hello"),
        _make_other_event("on_chain_end"),
        _make_stream_event(" world"),
    ]
    mock_graph.astream_events.return_value = _async_iter(events)

    tokens = [t async for t in stream_agent(base_state)]

    assert tokens == ["Hello", " world"]


@pytest.mark.asyncio
async def test_stream_agent_filters_empty_content(
    mock_graph: MagicMock, base_state: TripAssistantState
) -> None:
    events = [
        _make_stream_event(""),
        _make_stream_event("Real token"),
        _make_stream_event(""),
    ]
    mock_graph.astream_events.return_value = _async_iter(events)

    tokens = [t async for t in stream_agent(base_state)]

    assert tokens == ["Real token"]


@pytest.mark.asyncio
async def test_stream_agent_passes_state_to_graph(
    mock_graph: MagicMock, base_state: TripAssistantState
) -> None:
    mock_graph.astream_events.return_value = _async_iter([])

    _ = [t async for t in stream_agent(base_state)]

    mock_graph.astream_events.assert_called_once_with(base_state, version="v2")


@pytest.mark.asyncio
async def test_stream_agent_yields_nothing_for_empty_events(
    mock_graph: MagicMock, base_state: TripAssistantState
) -> None:
    mock_graph.astream_events.return_value = _async_iter([])

    tokens = [t async for t in stream_agent(base_state)]

    assert tokens == []
