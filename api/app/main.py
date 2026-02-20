"""FastAPI application.

This module initializes the FastAPI app with CORS support, request tracing,
and routes for the trip assistant agent.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import build_graph, get_graph
from app.logger import logger
from app.middleware import add_request_id_header
from app.routers import health, messages
from app.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Wire the agent graph dependency once at startup."""
    settings = get_settings()
    logger.info(
        "Starting up",
        environment=settings.environment,
        agent_mode=settings.agent_mode,
    )
    graph = build_graph(
        settings.agent_mode,
        settings.agent_lambda_function_name,
        settings.aws_region,
    )
    app.dependency_overrides[get_graph] = lambda: graph
    yield
    app.dependency_overrides.clear()


app = FastAPI(
    title="Trip Assistant API",
    version="0.1.0",
    description="FastAPI backend for LangGraph travel assistant",
    lifespan=lifespan,
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

# Add request ID tracing middleware
app.middleware("http")(add_request_id_header)

# Include routers with /api prefix
app.include_router(messages.router, prefix="/api")
app.include_router(health.router, prefix="/api")
