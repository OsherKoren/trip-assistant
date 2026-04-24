"""Health check endpoint for Lambda warm-up and monitoring."""

from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", responses={200: {"model": HealthResponse}})
async def health_check() -> StreamingResponse:
    """Health check endpoint for Lambda warm-up and monitoring.

    Returns a StreamingResponse so LWA 1.0.0 uses its streaming code path,
    which produces a valid Lambda proxy response. Plain JSON responses cause
    LWA to emit two concatenated JSON objects, resulting in a 502 from API GW.
    """
    body = HealthResponse(
        status="healthy",
        service="trip-assistant-api",
        version="0.1.0",
    ).model_dump_json()

    async def generate() -> AsyncGenerator[str, None]:
        yield body

    return StreamingResponse(generate(), media_type="application/json")
