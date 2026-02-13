# Multi-stage build for Trip Assistant API (Lambda deployment)
# Production image contains only API code - agent is invoked via Lambda proxy

# --- Builder Stage ---
FROM python:3.11-slim AS builder

# Install uv package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy only API package files (no agent code)
COPY pyproject.toml ./
COPY app/ ./app/

# Install API dependencies using uv
# Note: Agent is NOT installed - production uses Lambda proxy
RUN uv pip install --system --no-cache .

# --- Runtime Stage ---
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=prod

# Add labels for version tracking
LABEL service="trip-assistant-api" \
      version="0.1.0" \
      description="FastAPI backend for trip assistant agent (Lambda deployment)"

# Lambda Runtime Interface Emulator (for local testing with SAM CLI)
# In production Lambda, AWS provides the runtime and invokes handler directly
CMD ["python", "-m", "awslambdaric", "app.handler.handler"]
