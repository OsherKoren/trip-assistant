"""Feedback endpoint for rating assistant responses."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from app.db.feedback import send_feedback_email, store_feedback
from app.db.messages import get_message
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

    Looks up the message by ID to extract a preview, stores feedback in DynamoDB,
    and sends a notification email via SES.

    Args:
        request_body: Feedback request with message_id, rating, and optional comment.

    Returns:
        FeedbackResponse with status and feedback ID.

    Raises:
        HTTPException: 500 error if DynamoDB storage fails.
    """
    settings = get_settings()
    feedback_id = str(uuid.uuid4())
    created_at = datetime.now(UTC).isoformat()

    # Look up message for preview (best-effort)
    message_preview = ""
    if settings.messages_table_name:
        try:
            message = await get_message(
                settings.messages_table_name, settings.aws_region, request_body.message_id
            )
            if message:
                message_preview = message.get("answer", "")[:100]
        except Exception:
            logger.exception("Failed to look up message", message_id=request_body.message_id)

    item: dict[str, object] = {
        "id": feedback_id,
        "created_at": created_at,
        "message_id": request_body.message_id,
        "message_preview": message_preview,
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

    # SES notification — only for negative feedback with a comment
    # Awaited (not fire-and-forget) because Lambda freezes after response,
    # killing background tasks before they complete.
    if settings.feedback_email and request_body.rating == "down" and request_body.comment:
        await send_feedback_email(settings.feedback_email, settings.aws_region, item)

    return FeedbackResponse(status="received", id=feedback_id)
