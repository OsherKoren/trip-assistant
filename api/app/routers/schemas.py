"""Pydantic schemas for API request and response models."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MessageRequest(BaseModel):
    """Request model for message endpoint.

    Attributes:
        question: User's question about the trip (must not be empty)
    """

    question: str = Field(..., min_length=1, description="User's question about the trip")

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        """Validate that question is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Question cannot be empty or whitespace only")
        return v.strip()


class MessageResponse(BaseModel):
    """Response model for message endpoint.

    Attributes:
        answer: Agent's answer to the question
        category: Topic category (flight, car_rental, routes, etc.)
        confidence: Confidence score (0.0 to 1.0)
        source: Source document used (optional)
    """

    answer: str = Field(..., description="Agent's answer to the question")
    category: str = Field(..., description="Topic category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    source: str | None = Field(None, description="Source document used (optional)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "Your flight departs at 3:00 PM from Terminal 3",
                "category": "flight",
                "confidence": 0.95,
                "source": "flight.txt",
            }
        }
    }


class HealthResponse(BaseModel):
    """Response model for health check endpoint.

    Attributes:
        status: Health status (e.g., "healthy")
        service: Service name
        version: Service version
    """

    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "service": "trip-assistant-api",
                "version": "0.1.0",
            }
        }
    }


class FeedbackRequest(BaseModel):
    """Request model for feedback endpoint.

    Attributes:
        message_content: The assistant message being rated
        category: Topic category of the message (optional)
        rating: Thumbs up or down
        comment: Optional user comment explaining the rating
    """

    message_content: str = Field(..., min_length=1, description="Assistant message being rated")
    category: str | None = Field(None, description="Topic category of the message")
    rating: Literal["up", "down"] = Field(..., description="Feedback rating")
    comment: str | None = Field(None, description="Optional comment explaining the rating")


class FeedbackResponse(BaseModel):
    """Response model for feedback endpoint.

    Attributes:
        status: Feedback processing status
        id: Unique feedback ID
    """

    status: str = Field(..., description="Feedback processing status")
    id: str = Field(..., description="Unique feedback ID")


class ErrorResponse(BaseModel):
    """Response model for error responses.

    Attributes:
        detail: Error message or description
    """

    detail: str = Field(..., description="Error message or description")

    model_config = {"json_schema_extra": {"example": {"detail": "Internal server error"}}}
