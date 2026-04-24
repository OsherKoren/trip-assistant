"""Streaming messages endpoint — Server-Sent Events (SSE)."""

import json
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.cache import hash_question, normalize_question
from app.db.cache import store_cached_response
from app.db.messages import store_message
from app.dependencies import StreamDone, StreamGraphProtocol, get_stream_graph
from app.logger import logger
from app.settings import Settings, get_settings

from .schemas import MessageRequest

router = APIRouter(tags=["messages"])


def format_sse_event(data: str) -> str:
    """Format data as a Server-Sent Event (SSE) message.

    Multi-line data uses repeated ``data:`` fields per the SSE spec so that
    embedded newlines never collide with the ``\\n\\n`` event terminator.

    Args:
        data: The event data to format.

    Returns:
        Properly formatted SSE message with a trailing blank line.
    """
    lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "".join(f"data: {line}\n" for line in lines) + "\n"


@router.post("/messages/stream")
async def stream_message(
    request_body: MessageRequest,
    stream_graph: StreamGraphProtocol = Depends(get_stream_graph),
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """Stream agent response token-by-token as Server-Sent Events.

    Each token chunk is emitted as ``data: <chunk>\\n\\n``.
    After the last chunk, a ``data: [DONE] <json>\\n\\n`` event closes the stream
    with the message id, category, and confidence.
    On error, ``data: [ERROR] <message>\\n\\n`` is emitted and the stream closes.

    Args:
        request_body: Message request with question and optional history.
        stream_graph: Streaming agent graph (injected dependency).
        settings: Application settings.

    Returns:
        StreamingResponse with ``text/event-stream`` content type.
    """
    logger.info(
        "Processing stream request",
        question_preview=request_body.question[:50],
        history_length=len(request_body.history),
    )

    state: dict[str, Any] = {
        "question": request_body.question,
        "history": [entry.model_dump() for entry in request_body.history],
    }

    return StreamingResponse(
        _sse_generator(state, stream_graph, request_body.question, settings),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _sse_generator(
    state: dict[str, Any],
    stream_graph: StreamGraphProtocol,
    question: str,
    settings: Settings,
) -> AsyncGenerator[str, None]:
    """Yield SSE-formatted events from the agent stream."""
    assembled: list[str] = []
    final_state: dict[str, Any] = {}

    try:
        async for item in stream_graph.astream(state):
            if isinstance(item, StreamDone):
                final_state = item.state
            else:
                assembled.append(item)
                yield format_sse_event(item)

        message_id = str(uuid.uuid4())
        done_payload = {
            "id": message_id,
            "category": final_state.get("category", "general"),
            "confidence": float(final_state.get("confidence", 0.0)),
        }
        yield format_sse_event(f"[DONE] {json.dumps(done_payload)}")

        # Store message and cache best-effort (after stream completes)
        assembled_answer = "".join(assembled)
        if assembled_answer:
            created_at = datetime.now(UTC).isoformat()
            category = final_state.get("category", "general")
            confidence = Decimal(str(final_state.get("confidence", 0.0)))
            source = final_state.get("source") or ""

            try:
                message_item: dict[str, Any] = {
                    "id": message_id,
                    "created_at": created_at,
                    "question": question,
                    "answer": assembled_answer,
                    "category": category,
                    "confidence": confidence,
                    "source": source,
                }
                await store_message(settings.messages_table_name, settings.aws_region, message_item)
            except Exception as e:
                logger.exception(
                    "Failed to store streamed message",
                    message_id=message_id,
                    error_type=type(e).__name__,
                )

            try:
                normalized = normalize_question(question)
                question_hash = hash_question(normalized)
                cache_item: dict[str, Any] = {
                    "question_hash": question_hash,
                    "question": question,
                    "answer": assembled_answer,
                    "category": category,
                    "confidence": confidence,
                    "source": source,
                    "created_at": created_at,
                }
                await store_cached_response(
                    settings.cache_table_name, settings.aws_region, cache_item
                )
            except Exception as e:
                logger.exception(
                    "Failed to store streamed cache entry",
                    question_hash=question_hash[:12],
                    error_type=type(e).__name__,
                )

    except Exception as e:
        logger.error(
            "Streaming failed",
            error=str(e),
            question_preview=question[:50],
        )
        yield format_sse_event("[ERROR] Processing failed")
