"""Health check endpoint for Lambda warm-up and monitoring."""

from fastapi import APIRouter

from .schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
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
