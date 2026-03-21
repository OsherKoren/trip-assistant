"""Messages endpoint for the trip assistant agent."""

import json
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.db.messages import store_message
from app.dependencies import get_graph
from app.logger import logger
from app.settings import get_settings

from .schemas import ErrorResponse, MessageRequest, MessageResponse

router = APIRouter(tags=["messages"])

# Nodes that generate the answer (classifier tokens are excluded from the stream)
_SPECIALIST_NODES = frozenset(
    {"flight", "car_rental", "routes", "aosta", "chamonix", "annecy_geneva", "general"}
)


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
        history_length=len(request_body.history),
    )

    try:
        # Invoke agent with user question and optional history (async for better I/O performance)
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


@router.post("/messages/stream")
async def stream_message(
    request_body: MessageRequest, graph: Any = Depends(get_graph)
) -> StreamingResponse:
    """Stream the agent response token-by-token using Server-Sent Events.

    Emits a sequence of SSE events:
      - ``{"token": "..."}``  — one per LLM output token (specialist node only)
      - ``{"done": true, "id": "...", "answer": "...", "category": "...",
            "confidence": 0.95, "source": "..."}``  — final metadata
      - ``{"error": "..."}``  — on failure

    Args:
        request_body: Message request containing user question and optional history.
        graph: Agent graph instance (injected dependency).

    Returns:
        StreamingResponse with ``text/event-stream`` content type.
    """
    state = {
        "question": request_body.question,
        "history": [entry.model_dump() for entry in request_body.history],
    }

    async def event_stream() -> Any:
        message_id = str(uuid.uuid4())
        accumulated_answer = ""
        final_result: dict[str, Any] = {}

        try:
            async for event in graph.astream_events(state, version="v2"):
                if event["event"] == "on_chat_model_stream":
                    node = event.get("metadata", {}).get("langgraph_node", "")
                    if node in _SPECIALIST_NODES:
                        chunk = event["data"]["chunk"]
                        token: str = getattr(chunk, "content", "")
                        if token:
                            accumulated_answer += token
                            yield f"data: {json.dumps({'token': token})}\n\n"

                elif event["event"] == "on_chain_end" and event.get("name") == "LangGraph":
                    final_result = event["data"].get("output", {})

            # Store message in DynamoDB (best-effort)
            answer = accumulated_answer or final_result.get("answer", "")
            settings = get_settings()
            if settings.messages_table_name:
                try:
                    item: dict[str, Any] = {
                        "id": message_id,
                        "created_at": datetime.now(UTC).isoformat(),
                        "question": request_body.question,
                        "answer": answer,
                        "category": final_result.get("category", ""),
                        "confidence": Decimal(str(final_result.get("confidence", 0.0))),
                        "source": final_result.get("source") or "",
                    }
                    await store_message(settings.messages_table_name, settings.aws_region, item)
                except Exception:
                    logger.exception("Failed to store streamed message", message_id=message_id)

            done_payload = {
                "done": True,
                "id": message_id,
                "answer": answer,
                "category": final_result.get("category", ""),
                "confidence": final_result.get("confidence", 0.0),
                "source": final_result.get("source"),
            }
            yield f"data: {json.dumps(done_payload)}\n\n"

        except Exception as e:
            logger.error(
                "Streaming failed",
                error=str(e),
                question_preview=request_body.question[:50],
            )
            yield f"data: {json.dumps({'error': 'Processing failed'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
