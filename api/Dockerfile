# Multi-stage build for Trip Assistant API (Lambda container image)
# Production image contains only API code - agent is invoked via Lambda proxy

# --- Builder Stage (same base as runtime to match glibc for native extensions) ---
FROM public.ecr.aws/lambda/python:3.11 AS builder

WORKDIR /build

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy only API package files (no agent code)
COPY pyproject.toml uv.lock* ./
COPY app/ ./app/

# Install API dependencies using uv into a virtual environment
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache .

# --- Runtime Stage (AWS Lambda base image includes RIC/RIE) ---
FROM public.ecr.aws/lambda/python:3.11

COPY --from=builder /opt/venv/lib/python3.11/site-packages ${LAMBDA_TASK_ROOT}/
COPY app/ ${LAMBDA_TASK_ROOT}/app/

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

CMD ["app.handler.handler"]
