# Multi-stage build for Trip Assistant Agent (Lambda container image)
# Uses AWS Lambda base image which includes the Runtime Interface Client

# --- Builder Stage ---
FROM python:3.11-slim AS builder

WORKDIR /build

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies to a virtual environment
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache .

# --- Runtime Stage (AWS Lambda base image includes RIC/RIE) ---
FROM public.ecr.aws/lambda/python:3.11

COPY --from=builder /opt/venv/lib/python3.11/site-packages ${LAMBDA_TASK_ROOT}/
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY data/ ${LAMBDA_TASK_ROOT}/data/
COPY handler.py ${LAMBDA_TASK_ROOT}/

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

CMD ["handler.handler"]
