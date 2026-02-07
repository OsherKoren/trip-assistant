"""Dependency injection for the agent graph.

This module provides FastAPI dependencies for initializing and accessing
the LangGraph agent. Using dependency injection allows easy mocking in tests
via app.dependency_overrides without modifying production code.
"""

from typing import Any

from fastapi import HTTPException, Request

from app.logger import logger


def get_graph(request: Request) -> Any:
    """Get the compiled LangGraph agent.

    This dependency returns the agent graph instance, which can be invoked
    to process user questions. Import errors are caught and converted to
    HTTP 500 errors for graceful failure in production.

    Args:
        request: FastAPI request object (provides Lambda context in production).

    Returns:
        The compiled agent graph with invoke() and ainvoke() methods.

    Raises:
        HTTPException: 500 error if agent cannot be imported.

    Example:
        ```python
        @app.post("/api/messages")
        async def create_message(
            message: MessageRequest,
            graph = Depends(get_graph)
        ):
            result = await graph.ainvoke({"question": message.question})
            return MessageResponse(**result)
        ```
    """
    # Extract request ID for tracing (Lambda context available in production)
    lambda_context = request.scope.get("aws.context")
    request_id = lambda_context.request_id if lambda_context else "local"

    try:
        # Import agent graph (installed separately via uv pip install -e ../agent)
        from src.graph import graph

        logger.debug("Agent graph initialized successfully", request_id=request_id)
        return graph
    except ImportError as e:
        logger.error(
            "Failed to import agent graph",
            error=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Agent graph not available. Ensure agent package is installed.",
        ) from e
