# Lambda container image for Trip Assistant Agent
# Uses the AWS Lambda Python runtime (RIC) — standard pattern for Python Lambda containers

FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
COPY src/ ./src/
COPY data/ ./data/
COPY handler.py ./

RUN uv pip install --system --no-cache .

CMD ["handler.handler"]
