"""Tests for API schemas (Pydantic models)."""

import pytest
from pydantic import ValidationError

from app.routers.schemas import (
    ErrorResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    MessageRequest,
    MessageResponse,
)


class TestMessageRequest:
    """Tests for MessageRequest schema."""

    def test_valid_request(self) -> None:
        """Test MessageRequest with valid question."""
        request = MessageRequest(question="What time is my flight?")
        assert request.question == "What time is my flight?"

    @pytest.mark.parametrize(
        "invalid_question",
        [
            "",  # Empty string
            "   ",  # Whitespace only
            "\t",  # Tab only
            "\n",  # Newline only
        ],
    )
    def test_empty_question_rejected(self, invalid_question: str) -> None:
        """Test that empty or whitespace-only questions are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MessageRequest(question=invalid_question)
        errors = exc_info.value.errors()
        assert any("question" in str(error).lower() for error in errors)

    def test_missing_question_rejected(self) -> None:
        """Test that missing question field is rejected."""
        with pytest.raises(ValidationError):
            MessageRequest()  # type: ignore


class TestMessageResponse:
    """Tests for MessageResponse schema."""

    def test_valid_response(self) -> None:
        """Test MessageResponse with all fields."""
        response = MessageResponse(
            id="msg-123",
            answer="Your flight departs at 3:00 PM",
            category="flight",
            confidence=0.95,
            source="flight.txt",
        )
        assert response.id == "msg-123"
        assert response.answer == "Your flight departs at 3:00 PM"
        assert response.category == "flight"
        assert response.confidence == 0.95
        assert response.source == "flight.txt"

    def test_response_with_none_source(self) -> None:
        """Test MessageResponse with source=None."""
        response = MessageResponse(
            id="msg-456",
            answer="I'm not sure about that.",
            category="general",
            confidence=0.5,
            source=None,
        )
        assert response.source is None

    def test_serialization_round_trip(self) -> None:
        """Test serialization and deserialization."""
        original = MessageResponse(
            id="msg-789", answer="Test answer", category="test", confidence=0.9, source="test.txt"
        )
        # Serialize to dict
        data = original.model_dump()
        # Deserialize back
        restored = MessageResponse(**data)
        assert restored == original


class TestHealthResponse:
    """Tests for HealthResponse schema."""

    def test_valid_health_response(self) -> None:
        """Test HealthResponse structure."""
        response = HealthResponse(status="healthy", service="trip-assistant-api", version="0.1.0")
        assert response.status == "healthy"
        assert response.service == "trip-assistant-api"
        assert response.version == "0.1.0"


class TestFeedbackRequest:
    """Tests for FeedbackRequest schema."""

    def test_valid_feedback_request(self) -> None:
        """Test FeedbackRequest with valid fields."""
        request = FeedbackRequest(
            message_id="msg-123",
            rating="up",
        )
        assert request.message_id == "msg-123"
        assert request.rating == "up"
        assert request.comment is None

    def test_feedback_with_comment(self) -> None:
        """Test FeedbackRequest with optional comment."""
        request = FeedbackRequest(
            message_id="msg-456",
            rating="down",
            comment="The departure time was wrong",
        )
        assert request.rating == "down"
        assert request.comment == "The departure time was wrong"

    def test_empty_message_id_rejected(self) -> None:
        """Test that empty message_id is rejected."""
        with pytest.raises(ValidationError):
            FeedbackRequest(message_id="", rating="up")

    def test_invalid_rating_rejected(self) -> None:
        """Test that invalid rating value is rejected."""
        with pytest.raises(ValidationError):
            FeedbackRequest(message_id="msg-123", rating="invalid")  # type: ignore


class TestFeedbackResponse:
    """Tests for FeedbackResponse schema."""

    def test_valid_feedback_response(self) -> None:
        """Test FeedbackResponse structure."""
        response = FeedbackResponse(status="received", message_id="msg-123")
        assert response.status == "received"
        assert response.message_id == "msg-123"


class TestErrorResponse:
    """Tests for ErrorResponse schema."""

    def test_valid_error_response(self) -> None:
        """Test ErrorResponse structure."""
        response = ErrorResponse(detail="Something went wrong")
        assert response.detail == "Something went wrong"
