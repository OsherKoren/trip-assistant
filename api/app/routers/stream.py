"""Streaming messages endpoint — Server-Sent Events (SSE)."""

import json
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.db.messages import store_message
from app.dependencies import StreamDone, StreamGraphProtocol, get_stream_graph
from app.logger import logger
from app.settings import Settings, get_settings

from .schemas import MessageRequest

router = APIRouter(tags=["messages"])


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
                yield f"data: {item}\n\n"

        message_id = str(uuid.uuid4())
        done_payload = {
            "id": message_id,
            "category": final_state.get("category", "general"),
            "confidence": float(final_state.get("confidence", 0.0)),
        }
        yield f"data: [DONE] {json.dumps(done_payload)}\n\n"

        # Store message best-effort (after stream completes)
        assembled_answer = "".join(assembled)
        if assembled_answer:
            try:
                message_item: dict[str, Any] = {
                    "id": message_id,
                    "created_at": datetime.now(UTC).isoformat(),
                    "question": question,
                    "answer": assembled_answer,
                    "category": final_state.get("category", "general"),
                    "confidence": Decimal(str(final_state.get("confidence", 0.0))),
                    "source": final_state.get("source") or "",
                }
                await store_message(settings.messages_table_name, settings.aws_region, message_item)
            except Exception as e:
                logger.exception(
                    "Failed to store streamed message",
                    message_id=message_id,
                    error_type=type(e).__name__,
                )

    except Exception as e:
        logger.error(
            "Streaming failed",
            error=str(e),
            question_preview=question[:50],
        )
        yield "data: [ERROR] Processing failed\n\n"
