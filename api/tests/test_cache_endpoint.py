"""Tests for question cache integration in the messages endpoint."""

from collections.abc import Generator
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_graph
from app.main import app
from tests.conftest import MockGraph


@pytest.fixture
def mock_graph_result() -> dict[str, Any]:
    """Sample agent graph invocation result."""
    return {
        "answer": "Your flight departs at 3:00 PM from Terminal 3.",
        "category": "flight",
        "confidence": 0.95,
        "source": "flight.txt",
    }


@pytest.fixture
def mock_graph(mock_graph_result: dict[str, Any]) -> MockGraph:
    """Mock agent graph."""
    return MockGraph(return_value=mock_graph_result)


@pytest.fixture
def cached_item() -> dict[str, Any]:
    """Sample cached item from DynamoDB."""
    return {
        "question_hash": "abc123",
        "question": "what time is our flight?",
        "answer": "Cached: Your flight departs at 3:00 PM.",
        "category": "flight",
        "confidence": Decimal("0.95"),
        "source": "flight.txt",
        "created_at": "2026-03-28T12:00:00+00:00",
    }


@pytest.fixture
def client_with_cache(mock_graph: MockGraph) -> Generator[TestClient, None, None]:
    """Test client with cache_table_name configured."""
    with TestClient(app) as test_client:
        app.dependency_overrides[get_graph] = lambda: mock_graph
        with patch("app.routers.messages.get_settings") as mock_settings:
            settings = mock_settings.return_value
            settings.cache_table_name = "test-cache"
            settings.messages_table_name = ""
            settings.aws_region = "us-east-2"
            yield test_client
    app.dependency_overrides.clear()


class TestCacheHit:
    """Tests for cache hit scenario."""

    def test_returns_cached_response(
        self,
        client_with_cache: TestClient,
        cached_item: dict[str, Any],
        mock_graph: MockGraph,
    ) -> None:
        """Test that cache hit returns cached answer without calling LLM."""
        with patch("app.routers.messages.get_cached_response", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = cached_item

            response = client_with_cache.post(
                "/api/messages", json={"question": "What time is our flight?"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == cached_item["answer"]
        assert data["category"] == "flight"
        assert data["confidence"] == 0.95
        assert data["cached"] is True
        assert "id" in data
        # LLM should NOT have been called
        assert len(mock_graph.invoke_calls) == 0

    def test_cache_hit_generates_fresh_uuid(
        self,
        client_with_cache: TestClient,
        cached_item: dict[str, Any],
    ) -> None:
        """Test that each cache hit gets a unique message ID."""
        with patch("app.routers.messages.get_cached_response", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = cached_item

            r1 = client_with_cache.post(
                "/api/messages", json={"question": "What time is our flight?"}
            )
            r2 = client_with_cache.post(
                "/api/messages", json={"question": "What time is our flight?"}
            )

        assert r1.json()["id"] != r2.json()["id"]


class TestCacheMiss:
    """Tests for cache miss scenario."""

    def test_calls_llm_on_miss(
        self,
        client_with_cache: TestClient,
        mock_graph: MockGraph,
        mock_graph_result: dict[str, Any],
    ) -> None:
        """Test that cache miss falls through to LLM."""
        with (
            patch("app.routers.messages.get_cached_response", new_callable=AsyncMock) as mock_get,
            patch(
                "app.routers.messages.store_cached_response", new_callable=AsyncMock
            ) as mock_store,
        ):
            mock_get.return_value = None

            response = client_with_cache.post(
                "/api/messages", json={"question": "What time is our flight?"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == mock_graph_result["answer"]
        assert data["cached"] is False
        assert len(mock_graph.invoke_calls) == 1
        # Cache store should have been called
        mock_store.assert_awaited_once()

    def test_stores_result_in_cache(
        self,
        client_with_cache: TestClient,
    ) -> None:
        """Test that LLM result is stored in cache after miss."""
        with (
            patch("app.routers.messages.get_cached_response", new_callable=AsyncMock) as mock_get,
            patch(
                "app.routers.messages.store_cached_response", new_callable=AsyncMock
            ) as mock_store,
        ):
            mock_get.return_value = None

            client_with_cache.post("/api/messages", json={"question": "What time is our flight?"})

        mock_store.assert_awaited_once()
        stored_item = mock_store.call_args[0][2]  # third positional arg
        assert "question_hash" in stored_item
        assert stored_item["answer"] == "Your flight departs at 3:00 PM from Terminal 3."
        assert stored_item["category"] == "flight"


class TestCacheErrors:
    """Tests for cache error handling."""

    def test_cache_lookup_failure_falls_through_to_llm(
        self,
        client_with_cache: TestClient,
        mock_graph: MockGraph,
        mock_graph_result: dict[str, Any],
    ) -> None:
        """Test that cache lookup error falls through to LLM gracefully."""
        with patch("app.routers.messages.get_cached_response", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("DynamoDB timeout")

            response = client_with_cache.post(
                "/api/messages", json={"question": "What time is our flight?"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == mock_graph_result["answer"]
        assert data["cached"] is False
        assert len(mock_graph.invoke_calls) == 1

    def test_cache_store_failure_still_returns_response(
        self,
        client_with_cache: TestClient,
        mock_graph_result: dict[str, Any],
    ) -> None:
        """Test that cache store error does not block response."""
        with (
            patch("app.routers.messages.get_cached_response", new_callable=AsyncMock) as mock_get,
            patch(
                "app.routers.messages.store_cached_response", new_callable=AsyncMock
            ) as mock_store,
        ):
            mock_get.return_value = None
            mock_store.side_effect = Exception("DynamoDB write error")

            response = client_with_cache.post(
                "/api/messages", json={"question": "What time is our flight?"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == mock_graph_result["answer"]
        assert data["cached"] is False


class TestCacheDisabled:
    """Tests when cache is not configured."""

    def test_no_cache_when_table_not_set(
        self,
        client: TestClient,
        mock_graph: MockGraph,
    ) -> None:
        """Test that caching is skipped when cache_table_name is empty."""
        response = client.post("/api/messages", json={"question": "What time is our flight?"})

        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is False
        # LLM should have been called (no cache configured = always miss)
        assert len(mock_graph.invoke_calls) == 1


@pytest.fixture
def client(mock_graph: MockGraph) -> Generator[TestClient, None, None]:
    """Test client without cache configured (default)."""
    with TestClient(app) as test_client:
        app.dependency_overrides[get_graph] = lambda: mock_graph
        yield test_client
    app.dependency_overrides.clear()
