"""Messages endpoint for the trip assistant agent."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.db.messages import store_message
from app.dependencies import get_graph
from app.logger import logger
from app.settings import get_settings

from .schemas import ErrorResponse, MessageRequest, MessageResponse

router = APIRouter(tags=["messages"])


@router.post("/messages", response_model=MessageResponse, responses={500: {"model": ErrorResponse}})
async def create_message(
    request_body: MessageRequest, graph: Any = Depends(get_graph)
) -> MessageResponse:
    """Send a message to the trip assistant agent.

    Accepts a user question, invokes the LangGraph agent, and returns the
    agent's response with category classification and confidence score.
    The message is stored in DynamoDB (best-effort — failure does not block the response).

    Args:
        request_body: Message request containing user question.
        graph: Agent graph instance (injected dependency).

    Returns:
        MessageResponse with id, answer, category, confidence, and optional source.

    Raises:
        HTTPException: 500 error if agent invocation fails.
    """
    # Log incoming request (preview only, for privacy)
    logger.info(
        "Processing message request",
        question_preview=request_body.question[:50],
    )

    try:
        # Invoke agent with user question (async for better I/O performance)
        result = await graph.ainvoke({"question": request_body.question})

        message_id = str(uuid.uuid4())
        response = MessageResponse(
            id=message_id,
            answer=result["answer"],
            category=result["category"],
            confidence=result["confidence"],
            source=result.get("source"),
        )

        # Store message in DynamoDB (best-effort)
        settings = get_settings()
        if settings.messages_table_name:
            try:
                item: dict[str, Any] = {
                    "id": message_id,
                    "created_at": datetime.now(UTC).isoformat(),
                    "question": request_body.question,
                    "answer": result["answer"],
                    "category": result["category"],
                    "confidence": Decimal(str(result["confidence"])),
                    "source": result.get("source") or "",
                }
                await store_message(settings.messages_table_name, settings.aws_region, item)
            except Exception:
                logger.exception("Failed to store message", message_id=message_id)

        return response
    except HTTPException:
        raise
    except Exception as e:
        # Log error with full context for debugging
        logger.error(
            "Agent invocation failed",
            error=str(e),
            question_preview=request_body.question[:50],
        )
        # Return generic error to client (don't expose internals)
        raise HTTPException(status_code=500, detail="Processing failed") from e
