"""FastAPI application.

This module initializes the FastAPI app with CORS support, request tracing,
and routes for the trip assistant agent.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.dependencies import get_graph
from app.logger import logger
from app.schemas import ErrorResponse, HealthResponse, MessageRequest, MessageResponse

app = FastAPI(
    title="Trip Assistant API",
    version="0.1.0",
    description="FastAPI backend for LangGraph travel assistant",
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:5173",  # Vite default port
        # Production URLs will be added during deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Add Lambda request ID to response headers for tracing.

    In production (AWS Lambda), this extracts the Lambda request ID from the
    context and includes it in the response headers. Clients can use this ID
    to report errors, and engineers can search CloudWatch logs for the full
    request trace.

    In local development, returns "local" as the request ID.

    Args:
        request: Incoming HTTP request.
        call_next: Next middleware in chain (callable that takes Request and returns Response).

    Returns:
        Response with X-Request-ID header added.
    """
    response: Response = await call_next(request)

    # Extract Lambda request ID (available in production via Mangum)
    lambda_context = request.scope.get("aws.context")
    request_id = lambda_context.request_id if lambda_context else "local"

    # Add to response headers for client-side tracing
    response.headers["X-Request-ID"] = request_id

    return response


@app.post(
    "/api/messages", response_model=MessageResponse, responses={500: {"model": ErrorResponse}}
)
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
        # Invoke agent with user question
        result = graph.invoke({"question": request_body.question})

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


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for Lambda warm-up and monitoring.

    Lightweight check that doesn't require agent initialization. Used by
    API Gateway health checks and monitoring systems.

    Returns:
        HealthResponse with service status and version.
    """
    return HealthResponse(
        status="healthy",
        service="trip-assistant-api",
        version="0.1.0",
    )
