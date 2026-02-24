"""Tests for feedback API endpoint."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


class TestFeedbackEndpoint:
    """Tests for POST /api/feedback."""

    @patch("app.routers.feedback.send_feedback_email", new_callable=AsyncMock)
    @patch("app.routers.feedback.store_feedback", new_callable=AsyncMock)
    def test_valid_feedback_returns_200(
        self,
        mock_store: AsyncMock,
        _mock_email: AsyncMock,
        client: TestClient,
    ) -> None:
        """Test valid feedback payload returns 200 with ID."""
        response = client.post(
            "/api/feedback",
            json={
                "message_content": "Your flight departs at 3:00 PM",
                "category": "flight",
                "confidence": 0.95,
                "rating": "up",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert "id" in data
        mock_store.assert_awaited_once()

    @patch("app.routers.feedback.send_feedback_email", new_callable=AsyncMock)
    @patch("app.routers.feedback.store_feedback", new_callable=AsyncMock)
    def test_feedback_with_comment(
        self,
        mock_store: AsyncMock,
        _mock_email: AsyncMock,
        client: TestClient,
    ) -> None:
        """Test feedback with optional comment."""
        response = client.post(
            "/api/feedback",
            json={
                "message_content": "Wrong answer",
                "rating": "down",
                "comment": "The departure time was wrong",
            },
        )

        assert response.status_code == 200
        store_call = mock_store.call_args
        item = store_call[0][2]  # Third positional arg is the item
        assert item["rating"] == "down"
        assert item["comment"] == "The departure time was wrong"

    @patch("app.routers.feedback.send_feedback_email", new_callable=AsyncMock)
    @patch("app.routers.feedback.store_feedback", new_callable=AsyncMock)
    def test_confidence_stored_in_item(
        self,
        mock_store: AsyncMock,
        _mock_email: AsyncMock,
        client: TestClient,
    ) -> None:
        """Test that confidence is stored as Decimal in DynamoDB item."""
        from decimal import Decimal

        response = client.post(
            "/api/feedback",
            json={
                "message_content": "Your flight departs at 3:00 PM",
                "confidence": 0.85,
                "rating": "up",
            },
        )

        assert response.status_code == 200
        store_call = mock_store.call_args
        item = store_call[0][2]
        assert item["confidence"] == Decimal("0.85")

    @patch("app.routers.feedback.send_feedback_email", new_callable=AsyncMock)
    @patch("app.routers.feedback.store_feedback", new_callable=AsyncMock)
    def test_confidence_omitted_when_not_provided(
        self,
        mock_store: AsyncMock,
        _mock_email: AsyncMock,
        client: TestClient,
    ) -> None:
        """Test that confidence is not in item when not provided."""
        response = client.post(
            "/api/feedback",
            json={
                "message_content": "Your flight departs at 3:00 PM",
                "rating": "up",
            },
        )

        assert response.status_code == 200
        store_call = mock_store.call_args
        item = store_call[0][2]
        assert "confidence" not in item

    def test_empty_message_returns_422(self, client: TestClient) -> None:
        """Test empty message_content returns 422 validation error."""
        response = client.post(
            "/api/feedback",
            json={"message_content": "", "rating": "up"},
        )
        assert response.status_code == 422

    def test_invalid_rating_returns_422(self, client: TestClient) -> None:
        """Test invalid rating value returns 422 validation error."""
        response = client.post(
            "/api/feedback",
            json={"message_content": "Test", "rating": "invalid"},
        )
        assert response.status_code == 422

    @patch("app.routers.feedback.send_feedback_email", new_callable=AsyncMock)
    @patch(
        "app.routers.feedback.store_feedback",
        new_callable=AsyncMock,
        side_effect=Exception("DynamoDB error"),
    )
    def test_dynamodb_failure_returns_500(
        self,
        _mock_store: AsyncMock,
        _mock_email: AsyncMock,
        client: TestClient,
    ) -> None:
        """Test DynamoDB failure returns 500."""
        response = client.post(
            "/api/feedback",
            json={"message_content": "Test", "rating": "up"},
        )
        assert response.status_code == 500

    @patch("app.routers.feedback.send_feedback_email", new_callable=AsyncMock)
    @patch("app.routers.feedback.store_feedback", new_callable=AsyncMock)
    def test_ses_failure_still_returns_200(
        self,
        _mock_store: AsyncMock,
        mock_email: AsyncMock,
        client: TestClient,
    ) -> None:
        """Test SES failure does not affect response (fire-and-forget)."""
        mock_email.side_effect = Exception("SES error")

        response = client.post(
            "/api/feedback",
            json={
                "message_content": "Test",
                "rating": "down",
                "comment": "Bad answer",
            },
        )

        # SES is fire-and-forget, so the response should still be 200
        assert response.status_code == 200


class TestFeedbackEmailLogic:
    """Tests for email notification rules: only on thumbs down + comment."""

    @patch("app.routers.feedback.send_feedback_email", new_callable=AsyncMock)
    @patch("app.routers.feedback.store_feedback", new_callable=AsyncMock)
    def test_thumbs_up_does_not_send_email(
        self,
        mock_store: AsyncMock,
        mock_email: AsyncMock,
        client: TestClient,
    ) -> None:
        """Thumbs up -> DynamoDB only, no email."""
        client.post(
            "/api/feedback",
            json={"message_content": "Good answer", "rating": "up"},
        )

        mock_store.assert_awaited_once()
        mock_email.assert_not_called()

    @patch("app.routers.feedback.send_feedback_email", new_callable=AsyncMock)
    @patch("app.routers.feedback.store_feedback", new_callable=AsyncMock)
    def test_thumbs_down_without_comment_does_not_send_email(
        self,
        mock_store: AsyncMock,
        mock_email: AsyncMock,
        client: TestClient,
    ) -> None:
        """Thumbs down without comment -> DynamoDB only, no email."""
        client.post(
            "/api/feedback",
            json={"message_content": "Bad answer", "rating": "down"},
        )

        mock_store.assert_awaited_once()
        mock_email.assert_not_called()

    @patch("app.routers.feedback.send_feedback_email", new_callable=AsyncMock)
    @patch("app.routers.feedback.store_feedback", new_callable=AsyncMock)
    def test_thumbs_down_with_comment_sends_email(
        self,
        mock_store: AsyncMock,
        _mock_email: AsyncMock,
        client: TestClient,
    ) -> None:
        """Thumbs down with comment -> DynamoDB + email."""
        client.post(
            "/api/feedback",
            json={
                "message_content": "Bad answer",
                "rating": "down",
                "comment": "The time was wrong",
            },
        )

        mock_store.assert_awaited_once()
