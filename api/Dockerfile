# Multi-stage build for Trip Assistant API (Lambda container image with LWA)
# AWS Lambda Web Adapter replaces Mangum — proxies HTTP to Lambda, enabling true SSE streaming

# --- LWA Stage ---
FROM public.ecr.aws/awsguru/aws-lambda-web-adapter:latest AS lwa

# --- Builder Stage ---
FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
COPY app/ ./app/

RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache .

# --- Runtime Stage ---
FROM python:3.12-slim

COPY --from=lwa /lambda-adapter /opt/extensions/lambda-adapter
COPY --from=builder /opt/venv /opt/venv
COPY app/ /var/task/app/

WORKDIR /var/task

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV AWS_LWA_PORT=8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
