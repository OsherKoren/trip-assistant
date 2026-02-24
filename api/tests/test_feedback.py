"""Tests for feedback storage and email notification functions."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

import app.db.feedback as feedback_mod
from app.db.feedback import send_feedback_email, store_feedback
from tests.helpers import make_mock_boto3_session


@pytest.fixture
def feedback_item() -> dict[str, Any]:
    """Sample feedback item."""
    return {
        "id": "test-uuid",
        "created_at": "2026-02-22T14:30:00+00:00",
        "message_id": "msg-abc123",
        "message_preview": "Your flight departs at 3:00 PM",
        "rating": "down",
        "comment": "The departure time was wrong",
    }


class TestStoreFeedback:
    """Tests for store_feedback function."""

    @pytest.mark.asyncio
    async def test_stores_item_in_dynamodb(
        self, monkeypatch: pytest.MonkeyPatch, feedback_item: dict[str, Any]
    ) -> None:
        """Test that feedback is stored in DynamoDB."""
        table = AsyncMock()
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(feedback_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        await store_feedback("test-table", "us-east-2", feedback_item)

        dynamodb.Table.assert_awaited_once_with("test-table")
        table.put_item.assert_awaited_once_with(Item=feedback_item)

    @pytest.mark.asyncio
    async def test_raises_on_dynamodb_error(
        self, monkeypatch: pytest.MonkeyPatch, feedback_item: dict[str, Any]
    ) -> None:
        """Test that DynamoDB errors propagate."""
        table = AsyncMock()
        table.put_item.side_effect = Exception("DynamoDB error")
        dynamodb = AsyncMock()
        dynamodb.Table = AsyncMock(return_value=table)
        monkeypatch.setattr(feedback_mod, "_session", make_mock_boto3_session(resource=dynamodb))

        with pytest.raises(Exception, match="DynamoDB error"):
            await store_feedback("test-table", "us-east-2", feedback_item)


class TestSendFeedbackEmail:
    """Tests for send_feedback_email function."""

    @pytest.mark.asyncio
    async def test_sends_email_via_ses(
        self, monkeypatch: pytest.MonkeyPatch, feedback_item: dict[str, Any]
    ) -> None:
        """Test that email is sent via SES."""
        mock_ses = AsyncMock()
        monkeypatch.setattr(feedback_mod, "_session", make_mock_boto3_session(client=mock_ses))

        await send_feedback_email("test@example.com", "us-east-2", feedback_item)

        mock_ses.send_email.assert_awaited_once()
        call_kwargs = mock_ses.send_email.call_args[1]
        assert call_kwargs["Source"] == "test@example.com"
        assert call_kwargs["Destination"]["ToAddresses"] == ["test@example.com"]

    @pytest.mark.asyncio
    async def test_does_not_raise_on_ses_error(
        self, monkeypatch: pytest.MonkeyPatch, feedback_item: dict[str, Any]
    ) -> None:
        """Test that SES errors are logged but not raised."""
        mock_ses = AsyncMock()
        mock_ses.send_email.side_effect = Exception("SES error")
        monkeypatch.setattr(feedback_mod, "_session", make_mock_boto3_session(client=mock_ses))

        # Should not raise
        await send_feedback_email("test@example.com", "us-east-2", feedback_item)
