"""Messages endpoint for the trip assistant agent."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_graph
from app.logger import logger

from .schemas import ErrorResponse, MessageRequest, MessageResponse

router = APIRouter(tags=["messages"])


@router.post("/messages", response_model=MessageResponse, responses={500: {"model": ErrorResponse}})
async def create_message(
    request_body: MessageRequest, graph: Any = Depends(get_graph)
) -> MessageResponse:
    """Send a message to the trip assistant agent.

    Accepts a user question, invokes the LangGraph agent, and returns the
    agent's response with category classification and confidence score.

    Args:
        request_body: Message request containing user question.
        graph: Agent graph instance (injected dependency).

    Returns:
        MessageResponse with answer, category, confidence, and optional source.

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

        # Return structured response
        return MessageResponse(
            answer=result["answer"],
            category=result["category"],
            confidence=result["confidence"],
            source=result.get("source"),
        )
    except Exception as e:
        # Log error with full context for debugging
        logger.error(
            "Agent invocation failed",
            error=str(e),
            question_preview=request_body.question[:50],
        )
        # Return generic error to client (don't expose internals)
        raise HTTPException(status_code=500, detail="Processing failed") from e
