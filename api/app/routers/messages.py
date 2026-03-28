"""Messages endpoint for the trip assistant agent."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.cache import hash_question, normalize_question
from app.db.cache import get_cached_response, store_cached_response
from app.db.messages import store_message
from app.dependencies import AgentGraphProtocol, get_graph
from app.logger import logger
from app.settings import get_settings

from .schemas import ErrorResponse, MessageRequest, MessageResponse

router = APIRouter(tags=["messages"])


@router.post("/messages", response_model=MessageResponse, responses={500: {"model": ErrorResponse}})
async def create_message(
    request_body: MessageRequest, graph: AgentGraphProtocol = Depends(get_graph)
) -> MessageResponse:
    """Send a message to the trip assistant agent.

    Accepts a user question, invokes the LangGraph agent, and returns the
    agent's response with category classification and confidence score.
    Checks the question cache first to avoid redundant LLM calls.
    The message is stored in DynamoDB (best-effort — failure does not block the response).

    Args:
        request_body: Message request containing user question.
        graph: Agent graph instance (injected dependency).

    Returns:
        MessageResponse with id, answer, category, confidence, and optional source.

    Raises:
        HTTPException: 500 error if agent invocation fails.
    """
    logger.info(
        "Processing message request",
        question_preview=request_body.question[:50],
        history_length=len(request_body.history),
    )

    settings = get_settings()

    try:
        # Check question cache before calling LLM
        normalized = normalize_question(request_body.question)
        question_hash = hash_question(normalized)

        try:
            cached_item = await get_cached_response(
                settings.cache_table_name, settings.aws_region, question_hash
            )
        except Exception as e:
            logger.exception(
                "Cache lookup failed, falling through to LLM",
                error_type=type(e).__name__,
            )
            cached_item = None

        if cached_item:
            message_id = str(uuid.uuid4())
            response = MessageResponse(
                id=message_id,
                answer=cached_item["answer"],
                category=cached_item["category"],
                confidence=float(cached_item["confidence"]),
                source=cached_item.get("source") or None,
                cached=True,
            )
            try:
                await store_message(
                    settings.messages_table_name,
                    settings.aws_region,
                    _build_message_item(message_id, request_body.question, cached_item),
                )
            except Exception as e:
                logger.exception(
                    "Failed to store cached message",
                    message_id=message_id,
                    error_type=type(e).__name__,
                )
            return response

        # Cache miss — invoke agent
        state = {
            "question": request_body.question,
            "history": [entry.model_dump() for entry in request_body.history],
        }
        result = await graph.ainvoke(state)

        message_id = str(uuid.uuid4())
        response = MessageResponse(
            id=message_id,
            answer=result["answer"],
            category=result["category"],
            confidence=result["confidence"],
            source=result.get("source"),
            cached=False,
        )

        # Store message (best-effort)
        try:
            await store_message(
                settings.messages_table_name,
                settings.aws_region,
                _build_message_item(message_id, request_body.question, result),
            )
        except Exception as e:
            logger.exception(
                "Failed to store message",
                message_id=message_id,
                error_type=type(e).__name__,
            )

        # Store in question cache (best-effort)
        try:
            cache_item: dict[str, Any] = {
                "question_hash": question_hash,
                "question": request_body.question,
                "answer": result["answer"],
                "category": result["category"],
                "confidence": Decimal(str(result["confidence"])),
                "source": result.get("source") or "",
                "created_at": datetime.now(UTC).isoformat(),
            }
            await store_cached_response(settings.cache_table_name, settings.aws_region, cache_item)
        except Exception as e:
            logger.exception(
                "Failed to store cache entry",
                question_hash=question_hash[:12],
                error_type=type(e).__name__,
            )

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Agent invocation failed",
            error=str(e),
            question_preview=request_body.question[:50],
        )
        raise HTTPException(status_code=500, detail="Processing failed") from e


def _build_message_item(message_id: str, question: str, result: dict[str, Any]) -> dict[str, Any]:
    """Build a message item dict for DynamoDB storage."""
    return {
        "id": message_id,
        "created_at": datetime.now(UTC).isoformat(),
        "question": question,
        "answer": result["answer"],
        "category": result["category"],
        "confidence": Decimal(str(result["confidence"])),
        "source": result.get("source") or "",
    }
