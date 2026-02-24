"""Tests for message storage functions."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

import app.db.messages as messages_mod
from app.db.messages import get_message, store_message
from tests.helpers import make_mock_boto3_session


class TestStoreMessage:
    """Tests for store_message function."""

    @pytest.mark.asyncio
    async def test_stores_item_in_dynamodb(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that message is stored in DynamoDB."""
        table = AsyncMock()
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(messages_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        item: dict[str, Any] = {"id": "msg-123", "question": "Hello?", "answer": "Hi!"}
        await store_message("test-table", "us-east-2", item)

        dynamodb.Table.assert_awaited_once_with("test-table")
        table.put_item.assert_awaited_once_with(Item=item)

    @pytest.mark.asyncio
    async def test_raises_on_dynamodb_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that DynamoDB errors propagate."""
        table = AsyncMock()
        table.put_item.side_effect = Exception("DynamoDB error")
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(messages_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        with pytest.raises(Exception, match="DynamoDB error"):
            await store_message("test-table", "us-east-2", {"id": "msg-123"})


class TestGetMessage:
    """Tests for get_message function."""

    @pytest.mark.asyncio
    async def test_returns_item_when_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_message returns item from DynamoDB."""
        expected: dict[str, Any] = {"id": "msg-123", "answer": "Hi!"}
        table = AsyncMock()
        table.get_item.return_value = {"Item": expected}
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(messages_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        result = await get_message("test-table", "us-east-2", "msg-123")

        assert result == expected
        table.get_item.assert_awaited_once_with(Key={"id": "msg-123"})

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_message returns None when item doesn't exist."""
        table = AsyncMock()
        table.get_item.return_value = {}
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(messages_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        result = await get_message("test-table", "us-east-2", "nonexistent")

        assert result is None
