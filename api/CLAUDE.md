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
│   ├── main.py           # FastAPI app config, CORS, include routers & middleware
│   ├── middleware.py     # HTTP middleware (request ID tracing)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── messages.py   # POST /messages endpoint
│   │   ├── health.py     # GET /health endpoint
│   │   └── schemas.py    # Pydantic request/response models
│   ├── handler.py        # Lambda handler (Mangum)
│   ├── settings.py       # pydantic-settings config (env vars, validation)
│   ├── dependencies.py   # Agent graph factory + dependency stub
│   └── logger.py         # Logging configuration (loguru)
├── tests/
├── Dockerfile
└── pyproject.toml
```

## Endpoints

### POST /api/messages
Send a message to the trip assistant.

```python
# routers/messages.py
from fastapi import APIRouter, Depends

router = APIRouter(tags=["messages"])

@router.post("/messages", response_model=MessageResponse)
async def create_message(
    request_body: MessageRequest,
    graph = Depends(get_graph)
):
    result = graph.invoke({"question": request_body.question})
    return MessageResponse(
        answer=result["answer"],
        category=result["category"],
        confidence=result["confidence"],
        source=result.get("source")
    )

# main.py
app.include_router(messages.router, prefix="/api")
```

### GET /api/health
Health check for Lambda warm-up.

```python
# routers/health.py
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="trip-assistant-api",
        version="0.1.0"
    )

# main.py
app.include_router(health.router, prefix="/api")
```

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
- pydantic-settings >= 2.0 (env var config with validation)
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

## SAM Local Testing

AWS SAM provides production-identical local Lambda testing. Use this for testing the Lambda handler before deployment.

### Installation

**macOS/Linux:**
```bash
brew install aws-sam-cli
```

**Windows:**
```bash
# Using pip
pip install aws-sam-cli

# Or download installer from AWS
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
```

**Verify installation:**
```bash
sam --version
```

### Prerequisites

1. **Docker Desktop** - Must be running (SAM uses Docker to simulate Lambda)
2. **Environment file** - Create `.env` from `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

### Local Commands

```bash
cd api

# Validate SAM template
sam validate

# Invoke function with test event (single invocation)
sam local invoke -e tests/events/health-get.json
sam local invoke -e tests/events/messages-post.json

# Start local API server (persistent, auto-reload)
sam local start-api

# Test health endpoint
curl http://localhost:3001/api/health

# Test messages endpoint
curl -X POST http://localhost:3001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"question": "What car did we rent?"}'
```

### SAM Configuration

**`samconfig.toml`** configures SAM behavior:
- Port: 3001 (avoids conflict with frontend on 3000)
- Environment: Loads from `.env` file
- Docker network: `host` for accessing agent Lambda
- Warm containers: `EAGER` for faster testing

**`template.yaml`** defines Lambda function and API Gateway:
- Runtime: Python 3.11
- Handler: `app.handler.handler`
- Memory: 512MB, Timeout: 30s
- Events: HTTP API routes for `/api/health` and `/api/messages`

### Troubleshooting

**"Docker daemon not running"**
```bash
# Ensure Docker Desktop is running
docker ps
```

**"Module not found" or import errors**
```bash
# Rebuild SAM dependencies
sam build

# Force clean build
sam build --use-container
```

**"Permission denied" on .env file**
```bash
# Check file permissions
chmod 644 .env
```

**Agent Lambda not accessible**
```bash
# Verify AGENT_MODE variable in .env
# For local testing: AGENT_MODE=local (imports local agent, default)
# For production testing: AGENT_MODE=lambda (calls agent Lambda)
```

**Port 3001 already in use**
```bash
# Kill process using port 3001
lsof -ti:3001 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :3001   # Windows (find PID, then taskkill)
```

### Production vs. Local Mode

The API supports two modes via the `AGENT_MODE` environment variable:

- **`AGENT_MODE=local`** (default): Imports agent graph directly from `../agent/src/graph.py`
  - Use for: Local development, SAM local testing, CI/CD unit tests
  - Requires: Agent package installed via `uv pip install -e ../agent`

- **`AGENT_MODE=lambda`** (production): Calls agent via Lambda proxy
  - Use for: Production deployment, integration testing with deployed agent
  - Requires: `AGENT_LAMBDA_FUNCTION_NAME` and AWS credentials

`AGENT_MODE` defaults to `local` — zero config for local dev. `ENVIRONMENT` is the environment name (e.g. `dev`, `prod`) and is separate from execution mode.

## Environment Variables

- `OPENAI_API_KEY` - From Parameter Store in Lambda (or `.env` for local)
- `ENVIRONMENT` - Environment name (`dev`, `prod`) — used for logging/config, not mode selection
- `AGENT_MODE` - `local` (direct import) or `lambda` (Lambda proxy) — defaults to `local`
- `AGENT_LAMBDA_FUNCTION_NAME` - Agent Lambda function name (required when `AGENT_MODE=lambda`)
- `AWS_REGION` - AWS region (defaults to `us-east-2`)

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
- **Wire dependencies at startup via lifespan** - Not per-request
- **Test with `app.dependency_overrides`** - Mock dependencies in tests

```python
# settings.py — validated config at startup
class Settings(BaseSettings):
    agent_mode: Literal["local", "lambda"] = "local"
    agent_lambda_function_name: str = ""

# dependencies.py — pure factory + stub
def build_graph(agent_mode, function_name, region) -> AgentGraphProtocol:
    if agent_mode == "lambda":
        return AgentLambdaProxy(function_name=function_name, region=region)
    from src.graph import graph
    return graph

def get_graph() -> AgentGraphProtocol:  # Stub, overridden by lifespan
    raise RuntimeError("Not wired")

# main.py — wire once at startup
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    graph = build_graph(settings.agent_mode, ...)
    app.dependency_overrides[get_graph] = lambda: graph
    yield
    app.dependency_overrides.clear()
```

### Middleware

- **Type `call_next` properly** - Avoid `Any` types
- **Add request IDs to responses** - For client error reporting
- **Use Starlette Response** - Import from `starlette.responses`

```python
# middleware.py
from collections.abc import Awaitable, Callable
from fastapi import Request
from starlette.responses import Response

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

# main.py
from app.middleware import add_request_id_header

app.middleware("http")(add_request_id_header)
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

# conftest.py — override AFTER TestClient enters (lifespan runs on enter)
@pytest.fixture
def client(mock_graph: MockGraph) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        app.dependency_overrides[get_graph] = lambda: mock_graph
        yield test_client
    app.dependency_overrides.clear()
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
