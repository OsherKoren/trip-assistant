"""Dependency injection for the agent graph.

This module provides FastAPI dependencies for initializing and accessing
the LangGraph agent. Using dependency injection allows easy mocking in tests
via app.dependency_overrides without modifying production code.
"""

from typing import Any

from fastapi import HTTPException

from app.logger import logger


def get_graph() -> Any:
    """Get the compiled LangGraph agent.

    This dependency returns the agent graph instance, which can be invoked
    to process user questions. Import errors are caught and converted to
    HTTP 500 errors for graceful failure in production.

    Returns:
        The compiled agent graph with an invoke() method.

    Raises:
        HTTPException: 500 error if agent cannot be imported.

    Example:
        ```python
        @app.post("/api/messages")
        async def create_message(
            request: MessageRequest,
            graph = Depends(get_graph)
        ):
            result = graph.invoke({"question": request.question})
            return MessageResponse(**result)
        ```
    """
    try:
        # Import agent graph (installed separately via pip install -e ../agent)
        from src.graph import graph

        logger.debug("Agent graph initialized successfully")
        return graph
    except ImportError as e:
        logger.error("Failed to import agent graph", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Agent graph not available. Ensure agent package is installed.",
        ) from e
