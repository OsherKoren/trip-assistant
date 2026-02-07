# API Service

FastAPI backend that exposes the LangGraph agent via HTTP.

## Architecture

```
API Gateway → Lambda → FastAPI (Mangum) → Agent
```

## Key Files

```
api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app + routes
│   ├── handler.py        # Lambda handler (Mangum)
│   ├── schemas.py        # Pydantic request/response models
│   ├── dependencies.py   # Agent initialization
│   └── logger.py         # Logging configuration (loguru)
├── tests/
├── Dockerfile
└── pyproject.toml
```

## Endpoints

### POST /api/messages
Send a message to the trip assistant.

```python
@app.post("/api/messages", response_model=MessageResponse)
async def create_message(request: MessageRequest):
    result = agent.invoke({"question": request.question})
    return MessageResponse(
        answer=result["answer"],
        category=result["category"],
        confidence=result["confidence"],
        source=result.get("source")
    )
```

### GET /api/health
Health check for Lambda warm-up.

## Schemas (Pydantic)

```python
class MessageRequest(BaseModel):
    question: str

class MessageResponse(BaseModel):
    answer: str
    category: str
    confidence: float
    source: str | None
```

## Lambda Handler

```python
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .

# For container deployment (ECS/local Docker)
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]

# Note: For Lambda, the handler is invoked directly, no CMD needed
```

## Logging

Uses **loguru** for structured logging (same as agent service).

```python
from app.logger import logger

# In routes
logger.info("Processing message request", question=request.question[:50])
logger.error("Agent invocation failed", error=str(e))

# In dependencies
logger.debug("Initializing agent graph")
```

**Configuration** (`app/logger.py`):
- Console output to stderr
- INFO level by default
- Colored output with timestamps
- Format: `{time} | {level} | {name}:{function}:{line} | {message}`

## Dependencies

- fastapi >= 0.115
- mangum >= 1.8 (Lambda adapter)
- loguru >= 0.7 (structured logging)
- agent service (local import)

## Setup

**Prerequisites:** Python 3.11+, [uv](https://github.com/astral-sh/uv) package manager

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install API package and dependencies
cd api
uv pip install -e .

# Install dev dependencies
uv pip install -e ".[dev]"
```

## Dev Commands

```bash
cd api

# Local development (auto-reload)
fastapi dev app/main.py

# Test endpoint
curl -X POST http://localhost:8000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"question": "What car did we rent?"}'
```

## Environment Variables

- `OPENAI_API_KEY` - From Parameter Store in Lambda
