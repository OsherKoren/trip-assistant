"""FastAPI application.

Initializes the FastAPI app with CORS, request tracing, and routers.
"""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import build_graph, build_stream_graph, get_graph, get_stream_graph
from app.logger import logger
from app.middleware import add_request_id_header
from app.routers import feedback, health, messages, stream
from app.settings import get_settings


def _fetch_openai_key(ssm_parameter_name: str) -> None:
    """Load OpenAI key from SSM if not already in environment (cold start only)."""
    if ssm_parameter_name and "OPENAI_API_KEY" not in os.environ:
        ssm = boto3.client("ssm")
        response = ssm.get_parameter(Name=ssm_parameter_name, WithDecryption=True)
        os.environ["OPENAI_API_KEY"] = response["Parameter"]["Value"]
        logger.info("OpenAI API key loaded from SSM")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Wire the agent graph dependency once at startup."""
    settings = get_settings()
    logger.info(
        "Starting up",
        environment=settings.environment,
        agent_mode=settings.agent_mode,
    )
    if settings.agent_mode == "local":
        _fetch_openai_key(settings.ssm_parameter_name)
    graph = build_graph(
        settings.agent_mode,
        settings.agent_lambda_function_name,
        settings.aws_region,
    )
    stream_graph = build_stream_graph(
        settings.agent_mode,
        settings.stream_buffer_size,
        settings.agent_lambda_function_name,
        settings.aws_region,
    )
    app.dependency_overrides[get_graph] = lambda: graph
    app.dependency_overrides[get_stream_graph] = lambda: stream_graph
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
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request ID tracing middleware
app.middleware("http")(add_request_id_header)

# Include routers with /api prefix
app.include_router(messages.router, prefix="/api")
app.include_router(stream.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
