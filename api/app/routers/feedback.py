"""Feedback endpoint for rating assistant responses."""

import asyncio
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from app.feedback import send_feedback_email, store_feedback
from app.logger import logger
from app.settings import get_settings

from .schemas import ErrorResponse, FeedbackRequest, FeedbackResponse

router = APIRouter(tags=["feedback"])


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    responses={500: {"model": ErrorResponse}},
)
async def create_feedback(request_body: FeedbackRequest) -> FeedbackResponse:
    """Submit feedback for an assistant response.

    Stores feedback in DynamoDB and sends a notification email via SES.
    The email is fire-and-forget — it does not block the response.

    Args:
        request_body: Feedback request with rating and optional comment.

    Returns:
        FeedbackResponse with status and feedback ID.

    Raises:
        HTTPException: 500 error if DynamoDB storage fails.
    """
    settings = get_settings()
    feedback_id = str(uuid.uuid4())
    created_at = datetime.now(UTC).isoformat()

    item = {
        "id": feedback_id,
        "created_at": created_at,
        "message_content": request_body.message_content,
        "category": request_body.category or "",
        "rating": request_body.rating,
        "comment": request_body.comment or "",
    }

    logger.info(
        "Processing feedback",
        feedback_id=feedback_id,
        rating=request_body.rating,
    )

    try:
        await store_feedback(settings.feedback_table_name, settings.aws_region, item)
    except Exception as e:
        logger.error("Failed to store feedback", error=str(e), feedback_id=feedback_id)
        raise HTTPException(status_code=500, detail="Failed to store feedback") from e

    # Fire-and-forget SES notification — only for negative feedback with a comment
    if settings.feedback_email and request_body.rating == "down" and request_body.comment:
        asyncio.create_task(send_feedback_email(settings.feedback_email, settings.aws_region, item))

    return FeedbackResponse(status="received", id=feedback_id)
