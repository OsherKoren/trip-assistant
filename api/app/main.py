"""FastAPI application.

This module initializes the FastAPI app with CORS support, request tracing,
and routes for the trip assistant agent.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware import add_request_id_header
from app.routers import health, messages

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

# Add request ID tracing middleware
app.middleware("http")(add_request_id_header)

# Include routers with /api prefix
app.include_router(messages.router, prefix="/api")
app.include_router(health.router, prefix="/api")
