"""Tests for feedback API endpoint."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import app.routers.feedback as feedback_router
from app.settings import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """Clear lru_cache on get_settings so env var changes take effect."""
    get_settings.cache_clear()


@pytest.fixture
def mock_store(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Mock store_feedback to succeed silently."""
    mock = AsyncMock()
    monkeypatch.setattr(feedback_router, "store_feedback", mock)
    return mock


@pytest.fixture
def mock_email(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Mock send_feedback_email to succeed silently."""
    mock = AsyncMock()
    monkeypatch.setattr(feedback_router, "send_feedback_email", mock)
    return mock


@pytest.fixture
def mock_get_message(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Mock get_message to return a message with an answer."""
    get_settings.cache_clear()
    monkeypatch.setenv("MESSAGES_TABLE_NAME", "test-messages-table")
    mock = AsyncMock(return_value={"id": "msg-123", "answer": "Your flight departs at 3:00 PM"})
    monkeypatch.setattr(feedback_router, "get_message", mock)
    return mock


@pytest.mark.usefixtures("mock_store", "mock_email", "mock_get_message")
class TestFeedbackEndpoint:
    """Tests for POST /api/feedback."""

    def test_valid_feedback_returns_200(
        self,
        client: TestClient,
        mock_store: AsyncMock,
    ) -> None:
        """Test valid feedback payload returns 200 with message_id."""
        response = client.post(
            "/api/feedback",
            json={"message_id": "msg-123", "rating": "up"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["message_id"] == "msg-123"
        mock_store.assert_awaited_once()

    def test_feedback_with_comment(
        self,
        client: TestClient,
        mock_store: AsyncMock,
    ) -> None:
        """Test feedback with optional comment."""
        response = client.post(
            "/api/feedback",
            json={
                "message_id": "msg-123",
                "rating": "down",
                "comment": "The departure time was wrong",
            },
        )

        assert response.status_code == 200
        item = mock_store.call_args[0][2]
        assert item["rating"] == "down"
        assert item["comment"] == "The departure time was wrong"

    def test_message_preview_from_lookup(
        self,
        client: TestClient,
        mock_store: AsyncMock,
    ) -> None:
        """Test that message_preview is extracted from message lookup."""
        response = client.post(
            "/api/feedback",
            json={"message_id": "msg-123", "rating": "up"},
        )

        assert response.status_code == 200
        item = mock_store.call_args[0][2]
        assert item["message_id"] == "msg-123"
        assert item["message_preview"] == "Your flight departs at 3:00 PM"

    def test_message_preview_empty_when_not_found(
        self,
        client: TestClient,
        mock_store: AsyncMock,
        mock_get_message: AsyncMock,
    ) -> None:
        """Test that message_preview is empty when message not found."""
        mock_get_message.return_value = None

        response = client.post(
            "/api/feedback",
            json={"message_id": "nonexistent", "rating": "up"},
        )

        assert response.status_code == 200
        item = mock_store.call_args[0][2]
        assert item["message_preview"] == ""

    def test_empty_message_id_returns_422(self, client: TestClient) -> None:
        """Test empty message_id returns 422 validation error."""
        response = client.post(
            "/api/feedback",
            json={"message_id": "", "rating": "up"},
        )
        assert response.status_code == 422

    def test_invalid_rating_returns_422(self, client: TestClient) -> None:
        """Test invalid rating value returns 422 validation error."""
        response = client.post(
            "/api/feedback",
            json={"message_id": "msg-123", "rating": "invalid"},
        )
        assert response.status_code == 422

    def test_dynamodb_failure_returns_500(
        self,
        client: TestClient,
        mock_store: AsyncMock,
    ) -> None:
        """Test DynamoDB failure returns 500."""
        mock_store.side_effect = Exception("DynamoDB error")

        response = client.post(
            "/api/feedback",
            json={"message_id": "msg-123", "rating": "up"},
        )
        assert response.status_code == 500

    def test_ses_failure_still_returns_200(
        self,
        client: TestClient,
        mock_email: AsyncMock,
    ) -> None:
        """Test SES failure does not affect response (fire-and-forget)."""
        mock_email.side_effect = Exception("SES error")

        response = client.post(
            "/api/feedback",
            json={
                "message_id": "msg-123",
                "rating": "down",
                "comment": "Bad answer",
            },
        )

        assert response.status_code == 200


@pytest.mark.usefixtures("mock_store", "mock_email", "mock_get_message")
class TestFeedbackEmailLogic:
    """Tests for email notification rules: only on thumbs down + comment."""

    def test_thumbs_up_does_not_send_email(
        self,
        client: TestClient,
        mock_store: AsyncMock,
        mock_email: AsyncMock,
    ) -> None:
        """Thumbs up -> DynamoDB only, no email."""
        client.post(
            "/api/feedback",
            json={"message_id": "msg-123", "rating": "up"},
        )

        mock_store.assert_awaited_once()
        mock_email.assert_not_called()

    def test_thumbs_down_without_comment_does_not_send_email(
        self,
        client: TestClient,
        mock_store: AsyncMock,
        mock_email: AsyncMock,
    ) -> None:
        """Thumbs down without comment -> DynamoDB only, no email."""
        client.post(
            "/api/feedback",
            json={"message_id": "msg-123", "rating": "down"},
        )

        mock_store.assert_awaited_once()
        mock_email.assert_not_called()

    def test_thumbs_down_with_comment_sends_email(
        self,
        client: TestClient,
        mock_store: AsyncMock,
    ) -> None:
        """Thumbs down with comment -> DynamoDB + email."""
        client.post(
            "/api/feedback",
            json={
                "message_id": "msg-123",
                "rating": "down",
                "comment": "The time was wrong",
            },
        )

        mock_store.assert_awaited_once()
