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
│   └── dependencies.py   # Agent initialization
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

## Dependencies

- fastapi
- mangum (Lambda adapter)
- agent service (local import)

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
