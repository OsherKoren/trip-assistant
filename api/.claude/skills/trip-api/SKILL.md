---
name: trip-api
description: |
  Build and modify the Trip Assistant FastAPI backend that exposes the agent via HTTP.
  Use when: (1) Adding or modifying API endpoints, (2) Working with Pydantic schemas,
  (3) Implementing dependency injection, (4) Testing API routes, (5) Configuring CORS
  or middleware, (6) Working with Lambda/Mangum handler, (7) Any task involving the api/ folder.
---

# Trip Assistant API Development

## Architecture

```
API Gateway → Lambda → FastAPI (Mangum) → Agent
```

The API exposes the LangGraph agent via HTTP endpoints with proper validation, error handling, and CORS.

## Core Patterns

### Pydantic Schemas (`app/schemas.py`)
```python
from pydantic import BaseModel, Field

class MessageRequest(BaseModel):
    question: str = Field(..., min_length=1)

class MessageResponse(BaseModel):
    answer: str
    category: str
    confidence: float
    source: str | None = None
```

### Dependency Injection (`app/dependencies.py`)
```python
from src.graph import graph

def get_graph():
    """Dependency that provides the compiled agent graph."""
    try:
        return graph
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail="Agent service not available"
        )
```

### FastAPI App Structure (`app/main.py`)
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import get_graph
from app.schemas import MessageRequest, MessageResponse

app = FastAPI(
    title="Trip Assistant API",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/messages", response_model=MessageResponse)
async def create_message(
    request: MessageRequest,
    agent = Depends(get_graph)
):
    try:
        result = agent.invoke({"question": request.question})
        return MessageResponse(
            answer=result["answer"],
            category=result["category"],
            confidence=result["confidence"],
            source=result.get("source")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "trip-assistant-api"}
```

### Lambda Handler (`app/handler.py`)
```python
from mangum import Mangum
from app.main import app

# Lambda handler - converts API Gateway events to FastAPI requests
handler = Mangum(app)
```

## Testing Patterns

### Test Fixtures (`tests/conftest.py`)
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.dependencies import get_graph

@pytest.fixture
def mock_graph():
    """Mock agent graph for testing."""
    graph = MagicMock()
    graph.invoke.return_value = {
        "answer": "Test answer",
        "category": "flight",
        "confidence": 0.95,
        "source": "flight.txt"
    }
    return graph

@pytest.fixture
def client(mock_graph):
    """TestClient with mocked agent dependency."""
    app.dependency_overrides[get_graph] = lambda: mock_graph
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Testing Endpoints (`tests/test_main.py`)
```python
def test_create_message_success(client):
    response = client.post(
        "/api/messages",
        json={"question": "What time is my flight?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["category"] == "flight"

def test_create_message_validation(client):
    response = client.post(
        "/api/messages",
        json={"question": ""}  # Empty string
    )
    assert response.status_code == 422  # Validation error
```

### Testing Lambda Handler (`tests/test_handler.py`)
```python
def test_handler_processes_api_gateway_event():
    event = {
        "version": "2.0",
        "routeKey": "POST /api/messages",
        "requestContext": {...},
        "body": '{"question": "Test question"}',
        "headers": {"content-type": "application/json"}
    }

    response = handler(event, {})
    assert response["statusCode"] == 200
```

## Adding New Endpoints

1. **Define schemas** in `app/schemas.py`
2. **Add route** in `app/main.py`
3. **Use dependencies** via `Depends()` for agent access
4. **Write tests first** (TDD) in `tests/test_main.py`
5. **Test validation** for request/response models

## Error Handling

### Validation Errors (422)
Pydantic automatically validates and returns 422 for invalid input.

### Application Errors (500)
```python
try:
    result = agent.invoke({"question": request.question})
    return MessageResponse(**result)
except Exception as e:
    logger.error(f"Agent invocation failed: {e}")
    raise HTTPException(
        status_code=500,
        detail="Failed to process request"
    )
```

## CORS Configuration

Configure early to avoid frontend integration issues:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://yourdomain.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## References

- **API patterns**: See [references/api-patterns.md](references/api-patterns.md) for endpoint structure and dependency injection
- **Testing patterns**: See [references/testing-patterns.md](references/testing-patterns.md) for TestClient and mocking strategies

## Quality Checks

Before committing:
```bash
pre-commit run --all-files
mypy app/
pytest tests/ -v
```

## Running Locally

```bash
# Development server (auto-reload)
fastapi dev app/main.py

# Test API
curl -X POST http://localhost:8000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"question": "What time is my flight?"}'
```
