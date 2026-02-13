# API Patterns

## Table of Contents
- [Endpoint Structure](#endpoint-structure)
- [Dependency Injection](#dependency-injection)
- [Schema Validation](#schema-validation)
- [Error Handling](#error-handling)
- [CORS Configuration](#cors-configuration)

---

## Endpoint Structure

### POST Endpoint with Request/Response Models

```python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from app.schemas import MessageRequest, MessageResponse
from app.dependencies import get_graph

@app.post("/api/messages", response_model=MessageResponse)
async def create_message(
    request: MessageRequest,
    agent = Depends(get_graph)
):
    """Process a user question through the agent."""
    try:
        result = agent.invoke({"question": request.question})
        return MessageResponse(
            answer=result["answer"],
            category=result["category"],
            confidence=result["confidence"],
            source=result.get("source")
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing failed: {str(e)}"
        )
```

### GET Endpoint (No Dependencies)

```python
@app.get("/api/health")
async def health_check():
    """Lightweight health check for Lambda warm-up."""
    return {
        "status": "healthy",
        "service": "trip-assistant-api",
        "version": "0.1.0"
    }
```

---

## Dependency Injection

### Agent Graph Dependency

```python
# app/dependencies.py
from fastapi import HTTPException

def get_graph():
    """Provides compiled agent graph as dependency.

    Raises:
        HTTPException: If agent import fails
    """
    try:
        from src.graph import graph
        return graph
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail="Agent service not available"
        )
```

### Using Dependencies in Routes

```python
# Inject dependency into route
@app.post("/api/messages")
async def create_message(
    request: MessageRequest,
    agent = Depends(get_graph)  # Dependency injection
):
    # agent is now available
    result = agent.invoke({"question": request.question})
    return result
```

### Testing with Overridden Dependencies

```python
# tests/conftest.py
from app.main import app
from app.dependencies import get_graph

@pytest.fixture
def client(mock_graph):
    # Override dependency for testing
    app.dependency_overrides[get_graph] = lambda: mock_graph
    yield TestClient(app)
    # Clean up
    app.dependency_overrides.clear()
```

---

## Schema Validation

### Request Schema with Validation

```python
# app/schemas.py
from pydantic import BaseModel, Field, field_validator

class MessageRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question cannot be empty or whitespace")
        return v.strip()
```

### Response Schema with Optional Fields

```python
class MessageResponse(BaseModel):
    answer: str
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "Your flight departs at 3:00 PM",
                "category": "flight",
                "confidence": 0.95,
                "source": "flight.txt"
            }
        }
    }
```

### Error Response Schema

```python
class ErrorResponse(BaseModel):
    detail: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Agent processing failed"
            }
        }
    }
```

---

## Error Handling

### Validation Errors (422) - Automatic

Pydantic automatically returns 422 for invalid requests:

```python
# Client sends: {"question": ""}
# FastAPI automatically returns:
{
    "detail": [
        {
            "loc": ["body", "question"],
            "msg": "String should have at least 1 character",
            "type": "string_too_short"
        }
    ]
}
```

### Application Errors (500) - Manual

```python
@app.post("/api/messages")
async def create_message(request: MessageRequest, agent = Depends(get_graph)):
    try:
        result = agent.invoke({"question": request.question})
        return MessageResponse(**result)
    except KeyError as e:
        # Agent returned incomplete state
        raise HTTPException(
            status_code=500,
            detail=f"Invalid agent response: missing {str(e)}"
        )
    except Exception as e:
        # Any other error
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

### Custom Exception Handlers

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

---

## CORS Configuration

### Development + Production

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",      # Local React dev server
    "http://127.0.0.1:3000",      # Alternative local
    "https://yourdomain.com",     # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Testing CORS

```python
def test_cors_headers(client):
    response = client.options(
        "/api/messages",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        }
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "POST" in response.headers["access-control-allow-methods"]
```
