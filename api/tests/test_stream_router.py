"""Tests for POST /api/messages/stream (SSE streaming endpoint)."""

import json
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.dependencies import StreamDone, get_stream_graph
from app.main import app


class MockStreamGraph:
    """Mock streaming graph that yields a list of text chunks then a StreamDone."""

    def __init__(
        self,
        chunks: list[str],
        final_state: dict[str, Any] | None = None,
    ) -> None:
        self.chunks = chunks
        self.final_state = final_state or {
            "category": "flight",
            "confidence": 0.95,
        }

    async def astream(self, state: dict[str, Any]) -> AsyncGenerator[str | StreamDone, None]:  # noqa: ARG002
        for chunk in self.chunks:
            yield chunk
        yield StreamDone(self.final_state)


class ErrorStreamGraph:
    """Mock streaming graph that raises after yielding one chunk."""

    async def astream(self, state: dict[str, Any]) -> AsyncGenerator[str | StreamDone, None]:  # noqa: ARG002
        yield "Some chunk"
        raise ValueError("Simulated stream error")


@pytest.fixture
def stream_client() -> Generator[TestClient, None, None]:
    mock = MockStreamGraph(["Hello", " world"])
    with TestClient(app) as test_client:
        app.dependency_overrides[get_stream_graph] = lambda: mock
        yield test_client
    app.dependency_overrides.clear()


def test_stream_returns_200_and_event_stream_content_type(stream_client: TestClient) -> None:
    response = stream_client.post(
        "/api/messages/stream",
        json={"question": "What time is our flight?"},
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


def test_stream_contains_text_chunks(stream_client: TestClient) -> None:
    response = stream_client.post(
        "/api/messages/stream",
        json={"question": "What time is our flight?"},
    )
    assert "data: Hello\n\n" in response.text
    assert "data:  world\n\n" in response.text


def test_stream_contains_done_event_with_metadata(stream_client: TestClient) -> None:
    response = stream_client.post(
        "/api/messages/stream",
        json={"question": "What time is our flight?"},
    )
    assert "data: [DONE]" in response.text

    # Extract and parse the DONE payload
    for line in response.text.splitlines():
        if line.startswith("data: [DONE] "):
            payload = json.loads(line[len("data: [DONE] ") :])
            assert "id" in payload
            assert payload["category"] == "flight"
            assert payload["confidence"] == pytest.approx(0.95)
            return
    pytest.fail("data: [DONE] line not found in response")


def test_stream_error_yields_error_event_and_closes() -> None:
    with TestClient(app) as test_client:
        app.dependency_overrides[get_stream_graph] = lambda: ErrorStreamGraph()
        response = test_client.post(
            "/api/messages/stream",
            json={"question": "What time is our flight?"},
        )
    app.dependency_overrides.clear()

    # The response should still be 200 (SSE — status is sent before the stream body)
    assert response.status_code == 200
    assert "data: [ERROR]" in response.text
