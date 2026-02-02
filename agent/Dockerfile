# Multi-stage Dockerfile for Trip Assistant Agent Service
# Optimized for AWS Lambda container images

# ========================================
# Stage 1: Builder
# ========================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies to a virtual environment
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache -e .

# ========================================
# Stage 2: Runtime
# ========================================
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Add venv to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "from src.graph import graph; print('OK')" || exit 1

# Default command - can be overridden
CMD ["python", "-c", "from src.graph import graph; print('Agent loaded successfully')"]
