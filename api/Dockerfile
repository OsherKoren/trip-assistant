# Multi-stage build for Trip Assistant API (Lambda container image with LWA)
# Build context must be the repo root: docker build -f api/Dockerfile .
# AWS Lambda Web Adapter proxies HTTP to uvicorn, enabling true SSE streaming.
# AGENT_MODE=local bundles agent/src/ + agent/data/ in-process — no second Lambda hop.

# --- Builder Stage ---
FROM public.ecr.aws/docker/library/python:3.12-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir uv

# Install API dependencies
COPY api/pyproject.toml api/uv.lock* ./
COPY api/app/ ./app/

RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache .

# Install agent runtime dependencies from its pyproject.toml
COPY agent/ /build/agent/

RUN . /opt/venv/bin/activate && \
    uv pip install --no-cache /build/agent

# --- Runtime Stage ---
FROM public.ecr.aws/docker/library/python:3.12-slim

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:1.0.0 /lambda-adapter /opt/extensions/lambda-adapter
COPY --from=builder /opt/venv /opt/venv
COPY api/app/ /var/task/app/
COPY agent/src/ /var/task/src/
COPY agent/data/ /var/task/data/

WORKDIR /var/task

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV PYTHONPATH=/var/task
ENV AGENT_MODE=local

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
