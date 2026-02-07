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

## Python Coding Standards

Follow these standards for production-ready code in mid-size organizations.

### Type Hints

- **Always type function signatures** - Include parameter types and return types
- **Avoid `Any` types** - Use specific types or unions instead
  - ✅ Good: `Callable[[Request], Awaitable[Response]]`, `str | None`
  - ❌ Bad: `Any`
  - Exception: Only use `Any` when truly necessary and add `# type: ignore` comment with explanation
- **Type intermediate variables** - Help mypy infer types: `response: Response = await call_next(request)`
- **Use union types** - Python 3.10+ syntax: `str | None` instead of `Optional[str]`

### Error Handling

- **Separation of concerns** - Different error details for different audiences:
  - **User-facing errors** (API responses): Generic, safe messages
  - **Developer logs** (CloudWatch, logs): Detailed errors with stack traces
- **Always log context** - Include request IDs, error details, relevant state
- **Use structured logging** - `logger.error("message", key=value)` not string formatting

Example:
```python
try:
    result = graph.invoke(state)
except Exception as e:
    logger.error("Graph invocation failed", error=str(e), request_id=request_id)
    raise HTTPException(status_code=500, detail="Processing failed") from e
```

### Testing

- **Type all test functions** - Add `-> None` return types even for tests
- **Use fixtures** - Don't repeat setup code across tests
- **Mock external dependencies** - Never call real APIs (OpenAI, agent) in unit tests
- **Test error handling** - Verify both success and failure paths

## FastAPI Coding Patterns

Follow these patterns for production-ready FastAPI code.

### Dependency Injection

- **Use `Depends()` for shared resources** - Agent graph, database connections, etc.
- **Accept `Request` in dependencies** - For Lambda context and request ID access
- **Test with `app.dependency_overrides`** - Mock dependencies in tests

```python
# dependencies.py
def get_graph(request: Request) -> CompiledGraph:
    lambda_context = request.scope.get("aws.context")
    request_id = lambda_context.request_id if lambda_context else "local"

    try:
        from src.graph import graph
        logger.debug("Graph initialized", request_id=request_id)
        return graph
    except ImportError as e:
        logger.error("Import failed", error=str(e), request_id=request_id)
        raise HTTPException(status_code=500, detail="Service unavailable") from e

# routes.py
@app.post("/api/messages")
async def create_message(
    message: MessageRequest,
    graph = Depends(get_graph)  # Injected dependency
):
    result = graph.invoke({"question": message.question})
    return MessageResponse(**result)
```

### Middleware

- **Type `call_next` properly** - Avoid `Any` types
- **Add request IDs to responses** - For client error reporting
- **Use Starlette Response** - Import from `starlette.responses`

```python
from collections.abc import Awaitable, Callable
from starlette.responses import Response

@app.middleware("http")
async def add_request_id_header(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response: Response = await call_next(request)

    # Extract Lambda request ID
    lambda_context = request.scope.get("aws.context")
    request_id = lambda_context.request_id if lambda_context else "local"

    response.headers["X-Request-ID"] = request_id
    return response
```

### Error Handling

- **Generic errors in responses** - Never expose internal details to clients
- **Detailed errors in logs** - Include full context for debugging
- **Always log request IDs** - For CloudWatch tracing

```python
# ✅ Good: Safe error handling
try:
    result = graph.invoke(state)
except Exception as e:
    logger.error("Graph invocation failed", error=str(e), request_id=request_id, state=state)
    raise HTTPException(status_code=500, detail="Processing failed") from e

# ❌ Bad: Exposes internals
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # Leaks stack traces!
```

### Testing

- **Override dependencies in tests** - Use `app.dependency_overrides`
- **Use TestClient** - From `fastapi.testclient`
- **Mock the agent** - Never call real OpenAI API in unit tests

```python
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

def test_create_message():
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"answer": "test", "category": "general"}

    # Override dependency
    app.dependency_overrides[get_graph] = lambda _request: mock_graph

    client = TestClient(app)
    response = client.post("/api/messages", json={"question": "test"})

    assert response.status_code == 200
    app.dependency_overrides.clear()  # Cleanup
```

### Request Tracing

- **Lambda provides request IDs** - No need to generate your own
- **Access via `request.scope["aws.context"]`** - Available in production
- **Return in response headers** - `X-Request-ID` for client reporting
- **Log in all error handlers** - For CloudWatch searching

**Production workflow:**
```
1. Client makes request
2. API Gateway assigns ID: "abc-123"
3. Lambda assigns ID: "xyz-789"
4. Your code logs errors with xyz-789
5. Response headers include X-Request-ID: xyz-789
6. Client reports error with xyz-789
7. Engineer searches CloudWatch for xyz-789
```
