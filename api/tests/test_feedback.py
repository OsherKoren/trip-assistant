"""Tests for feedback storage and email notification functions."""

from unittest.mock import AsyncMock, patch

import pytest

from app.feedback import send_feedback_email, store_feedback


@pytest.fixture
def feedback_item() -> dict:
    """Sample feedback item."""
    return {
        "id": "test-uuid",
        "created_at": "2026-02-22T14:30:00+00:00",
        "message_content": "Your flight departs at 3:00 PM",
        "category": "flight",
        "confidence": "0.95",
        "rating": "down",
        "comment": "The departure time was wrong",
    }


class TestStoreFeedback:
    """Tests for store_feedback function."""

    @pytest.mark.asyncio
    async def test_stores_item_in_dynamodb(self, feedback_item: dict) -> None:
        """Test that feedback is stored in DynamoDB."""
        mock_table = AsyncMock()
        mock_table.put_item = AsyncMock()

        mock_dynamodb = AsyncMock()
        mock_dynamodb.Table = AsyncMock(return_value=mock_table)

        with patch("app.feedback._session") as mock_session:
            mock_session.resource.return_value.__aenter__ = AsyncMock(return_value=mock_dynamodb)
            mock_session.resource.return_value.__aexit__ = AsyncMock(return_value=False)

            await store_feedback("test-table", "us-east-2", feedback_item)

        mock_dynamodb.Table.assert_awaited_once_with("test-table")
        mock_table.put_item.assert_awaited_once_with(Item=feedback_item)

    @pytest.mark.asyncio
    async def test_raises_on_dynamodb_error(self, feedback_item: dict) -> None:
        """Test that DynamoDB errors propagate."""
        mock_table = AsyncMock()
        mock_table.put_item = AsyncMock(side_effect=Exception("DynamoDB error"))

        mock_dynamodb = AsyncMock()
        mock_dynamodb.Table = AsyncMock(return_value=mock_table)

        with patch("app.feedback._session") as mock_session:
            mock_session.resource.return_value.__aenter__ = AsyncMock(return_value=mock_dynamodb)
            mock_session.resource.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(Exception, match="DynamoDB error"):
                await store_feedback("test-table", "us-east-2", feedback_item)


class TestSendFeedbackEmail:
    """Tests for send_feedback_email function."""

    @pytest.mark.asyncio
    async def test_sends_email_via_ses(self, feedback_item: dict) -> None:
        """Test that email is sent via SES."""
        mock_ses = AsyncMock()
        mock_ses.send_email = AsyncMock()

        with patch("app.feedback._session") as mock_session:
            mock_session.client.return_value.__aenter__ = AsyncMock(return_value=mock_ses)
            mock_session.client.return_value.__aexit__ = AsyncMock(return_value=False)

            await send_feedback_email("test@example.com", "us-east-2", feedback_item)

        mock_ses.send_email.assert_awaited_once()
        call_kwargs = mock_ses.send_email.call_args[1]
        assert call_kwargs["Source"] == "test@example.com"
        assert call_kwargs["Destination"]["ToAddresses"] == ["test@example.com"]

    @pytest.mark.asyncio
    async def test_does_not_raise_on_ses_error(self, feedback_item: dict) -> None:
        """Test that SES errors are logged but not raised."""
        mock_ses = AsyncMock()
        mock_ses.send_email = AsyncMock(side_effect=Exception("SES error"))

        with patch("app.feedback._session") as mock_session:
            mock_session.client.return_value.__aenter__ = AsyncMock(return_value=mock_ses)
            mock_session.client.return_value.__aexit__ = AsyncMock(return_value=False)

            # Should not raise
            await send_feedback_email("test@example.com", "us-east-2", feedback_item)
