"""Tests for question cache storage functions."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

import app.db.cache as cache_mod
from app.db.cache import get_cached_response, store_cached_response
from tests.helpers import make_mock_boto3_session


class TestGetCachedResponse:
    """Tests for get_cached_response function."""

    @pytest.mark.asyncio
    async def test_returns_item_when_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_cached_response returns cached item from DynamoDB."""
        expected: dict[str, Any] = {
            "question_hash": "abc123",
            "answer": "Your flight is at 3 PM",
            "category": "flight",
        }
        table = AsyncMock()
        table.get_item.return_value = {"Item": expected}
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(cache_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        result = await get_cached_response("test-cache", "us-east-2", "abc123")

        assert result == expected
        table.get_item.assert_awaited_once_with(Key={"question_hash": "abc123"})

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_cached_response returns None on cache miss."""
        table = AsyncMock()
        table.get_item.return_value = {}
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(cache_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        result = await get_cached_response("test-cache", "us-east-2", "nonexistent")

        assert result is None


class TestStoreCachedResponse:
    """Tests for store_cached_response function."""

    @pytest.mark.asyncio
    async def test_stores_item_in_dynamodb(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that cache item is stored in DynamoDB."""
        table = AsyncMock()
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(cache_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        item: dict[str, Any] = {"question_hash": "abc123", "answer": "Hi!"}
        await store_cached_response("test-cache", "us-east-2", item)

        dynamodb.Table.assert_awaited_once_with("test-cache")
        table.put_item.assert_awaited_once_with(Item=item)

    @pytest.mark.asyncio
    async def test_raises_on_dynamodb_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that DynamoDB errors propagate."""
        table = AsyncMock()
        table.put_item.side_effect = Exception("DynamoDB error")
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(cache_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        with pytest.raises(Exception, match="DynamoDB error"):
            await store_cached_response("test-cache", "us-east-2", {"question_hash": "abc123"})
