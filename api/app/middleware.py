"""HTTP middleware for request tracing and logging."""

from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import Response


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
