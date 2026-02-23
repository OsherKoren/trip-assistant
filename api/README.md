# Trip Assistant API

FastAPI backend that exposes the LangGraph trip assistant agent via HTTP. Deployed as an AWS Lambda function using Mangum.

## Features

- **REST API** - Clean HTTP interface to the trip assistant agent
- **Lambda-Ready** - Runs on AWS Lambda via Mangum adapter
- **Request Tracing** - Lambda request ID propagation via middleware
- **Dependency Injection** - Pluggable agent backend (local import or Lambda proxy)
- **Structured Logging** - Loguru-based logging with request context
- **Comprehensive Testing** - 73 unit tests with mocked dependencies

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key (for the agent)

### Installation

1. **Navigate to the api directory:**
   ```bash
   cd api/
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Install the agent package (for local mode):**
   ```bash
   uv pip install -e ../agent
   ```

### Run Locally

```bash
fastapi dev app/main.py
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Send a message
curl -X POST http://localhost:8000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"question": "What car did we rent?"}'
```

## API Endpoints

### POST /api/messages

Send a question to the trip assistant.

**Request:**
```json
{"question": "What time is our flight?"}
```

**Response:**
```json
{
  "answer": "Your flight departs at ...",
  "category": "flight",
  "confidence": 0.95,
  "source": "flight.txt"
}
```

### POST /api/feedback

Submit feedback on an answer.

### GET /api/health

Health check for Lambda warm-up.

**Response:**
```json
{
  "status": "healthy",
  "service": "trip-assistant-api",
  "version": "0.1.0"
}
```

## Architecture

```
API Gateway -> Lambda -> FastAPI (Mangum) -> Agent
```

### Agent Modes

The API supports two modes via the `AGENT_MODE` environment variable:

- **`local`** (default) - Imports agent graph directly. Use for local development and testing.
- **`lambda`** - Calls agent via Lambda proxy. Use for production deployment.

## Project Structure

```
api/
├── app/
│   ├── main.py           # FastAPI app, CORS, routers, middleware
│   ├── middleware.py      # Request ID tracing middleware
│   ├── handler.py         # Lambda handler (Mangum)
│   ├── settings.py        # pydantic-settings config
│   ├── dependencies.py    # Agent graph factory + DI stub
│   ├── feedback.py        # Feedback logic
│   ├── logger.py          # Loguru logging config
│   └── routers/
│       ├── messages.py    # POST /messages endpoint
│       ├── health.py      # GET /health endpoint
│       ├── feedback.py    # POST /feedback endpoint
│       └── schemas.py     # Pydantic request/response models
├── tests/
│   ├── conftest.py        # Shared fixtures
│   ├── events/            # SAM local test events
│   └── test_*.py          # Unit tests (73 tests)
├── template.yaml          # SAM template (Lambda + API Gateway)
├── samconfig.toml         # SAM configuration
├── Dockerfile             # Container deployment
├── pyproject.toml         # Dependencies and tooling config
├── CLAUDE.md              # Detailed developer docs
└── README.md              # This file
```

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ -v --cov=app

# Run specific test file
uv run pytest tests/test_schemas.py -v
```

## SAM Local Testing

Test the Lambda handler locally with AWS SAM:

```bash
# Start local API server
sam local start-api

# Test endpoints (port 3001)
curl http://localhost:3001/api/health
curl -X POST http://localhost:3001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"question": "What car did we rent?"}'
```

Requires Docker Desktop running. See `CLAUDE.md` for full SAM setup details.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `AGENT_MODE` | No | `local` | `local` (direct import) or `lambda` (Lambda proxy) |
| `AGENT_LAMBDA_FUNCTION_NAME` | When lambda | - | Agent Lambda function name |
| `ENVIRONMENT` | No | `dev` | Environment name (`dev`, `prod`) |
| `AWS_REGION` | No | `us-east-2` | AWS region |

## Dependencies

### Core
- **fastapi** >= 0.115 - Web framework
- **mangum** >= 0.18 - Lambda adapter
- **pydantic-settings** >= 2.0 - Environment config with validation
- **loguru** >= 0.7 - Structured logging
- **aioboto3** >= 13.0 - Async AWS SDK

### Development
- **pytest** - Testing framework
- **httpx** - Async test client
- **mypy** - Type checking
- **ruff** - Linting and formatting

## Code Quality

```bash
# Run all quality checks
uv run pre-commit run --all-files

# Individual checks
uv run mypy app/
uv run ruff check app/
uv run ruff format app/
```

## Contributing

1. Read `CLAUDE.md` for detailed development guidelines
2. Follow TDD workflow (write tests first)
3. Run quality checks before committing
4. Work on feature branches (never commit to main)

---

**Built with** [FastAPI](https://fastapi.tiangolo.com/) + [Mangum](https://mangum.fastapiexpert.com/) | **Powered by** [LangGraph](https://langchain-ai.github.io/langgraph/)
