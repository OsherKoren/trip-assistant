# API Service - Development Tasks

> **Note**: This file tracks development progress and is kept in version control
> as a reference for project workflow. It is NOT part of the production API code.
> Each service in the monorepo has its own TASKS.md for independent tracking.

## Overview

Building a FastAPI backend that exposes the LangGraph agent via HTTP endpoints, with AWS Lambda deployment support.

**Architecture**: `API Gateway → Lambda → FastAPI (Mangum) → Agent`

---

## Phase 1: Project Setup & Schemas ✅

Define project structure, dependencies, and Pydantic schemas.

- [x] Create `pyproject.toml`
  - [x] Package name: `trip-assistant-api`
  - [x] Build system: hatchling
  - [x] Core dependencies:
    - `fastapi >= 0.115`
    - `mangum >= 0.18` (AWS Lambda adapter)
    - `pydantic >= 2.0`
    - `loguru >= 0.7` (structured logging)
    - `trip-assistant-agent` (installed separately)
  - [x] Dev dependencies:
    - `pytest >= 8.0`
    - `pytest-cov >= 4.1`
    - `pytest-mock >= 3.12`
    - `httpx >= 0.27` (for TestClient)
    - `ruff >= 0.8`
    - `mypy >= 1.8`
    - `pre-commit`
  - [x] Ruff config (match agent pattern)
  - [x] Mypy config (match agent pattern)
  - [x] Pytest config with markers: `integration`, `unit`
- [x] Create `app/__init__.py` (empty)
- [x] Create `app/logger.py`
  - [x] Import loguru logger
  - [x] Configure console handler with custom format (match agent pattern)
  - [x] Set INFO level by default
  - [x] Export logger for use across app
- [x] Create `app/schemas.py`
  - [x] `MessageRequest(BaseModel)` with `question: str` (min_length=1)
  - [x] `MessageResponse(BaseModel)` with `answer`, `category`, `confidence`, `source`
  - [x] `HealthResponse(BaseModel)` with `status`, `service`, `version`
  - [x] `ErrorResponse(BaseModel)` with `detail`
- [x] Create `tests/__init__.py` (empty)
- [x] Create `tests/test_schemas.py`
  - [x] Test MessageRequest instantiation and validation
  - [x] Test empty/whitespace question rejected (parametrized)
  - [x] Test MessageResponse serialization round-trip
  - [x] Test source=None handling in MessageResponse
  - [x] Test HealthResponse structure
  - [x] Test ErrorResponse structure
- [x] Run `pytest tests/test_schemas.py -v` (must pass)
- [x] Run `pre-commit run --all-files` (must pass)

**Actual**: 11 tests passing (parametrized tests create additional test cases)

---

## Phase 2: Dependencies & Agent Initialization ✅

Create dependency injection layer for the agent graph.

- [x] Create `app/dependencies.py`
  - [x] Import logger from `app.logger`
  - [x] Implement `get_graph()` function
    - [x] Import and return compiled agent graph
    - [x] Handle import errors gracefully (raise HTTPException 500)
    - [x] Log errors and successful initialization
    - [x] Add type hints for return type
  - [x] Add docstrings explaining dependency injection pattern
- [x] Create `tests/test_dependencies.py`
  - [x] Test `get_graph()` returns callable with invoke method
  - [x] Test dependency override mechanism works (for testing)
  - [x] Test handles agent import error gracefully
  - [x] Test graph can be invoked with sample state
- [x] Run `pytest tests/test_dependencies.py -v` (must pass)
- [x] Run `pre-commit run --all-files` (must pass)
- [x] Commit changes: `git add app/dependencies.py tests/test_dependencies.py && git commit`

**Actual**: 4 tests passing

**Design Note**: Using dependency injection (`Depends(get_graph)`) allows easy mocking in tests via `app.dependency_overrides`.

---

## Phase 3: API Routes ✅

Build FastAPI routers for messages and health endpoints.

- [x] Create `app/routers/` directory
- [x] Create `app/routers/__init__.py` (empty)
- [x] Create `app/routers/messages.py`
  - [x] Define `router = APIRouter(tags=["messages"])`
  - [x] Implement `POST /messages` endpoint
    - [x] Accept `MessageRequest`
    - [x] Use `Depends(get_graph)` to get agent
    - [x] Log incoming request (question preview)
    - [x] Invoke agent with `{"question": request.question}`
    - [x] Return `MessageResponse` with answer, category, confidence, source
    - [x] Handle errors → 500 with `ErrorResponse` and log errors
- [x] Create `app/routers/health.py`
  - [x] Define `router = APIRouter(tags=["health"])`
  - [x] Implement `GET /health` endpoint
    - [x] Return `HealthResponse` with status="healthy", service, version
    - [x] Lightweight check (no agent dependency)
- [x] Tests remain unchanged (routes tested via app.include_router)
- [x] Run `pytest tests/ -v` (all tests must pass)
- [x] Run `pre-commit run --all-files` (must pass)
- [x] Commit changes: `git add app/routers/ && git commit`

**Actual**: All tests passing (31 tests)

**Design Note**: Router prefix `/api` is set in main.py via `app.include_router(messages.router, prefix="/api")` (DRY - defined once).

---

## Phase 4: FastAPI App & Middleware ✅

Wire up the FastAPI application with CORS, middleware, and routers.

- [x] Create `app/middleware.py`
  - [x] Move request ID tracing middleware from main.py
  - [x] Export `add_request_id_header()` as standalone function
- [x] Simplify `app/main.py`
  - [x] Import logger from `app.logger`
  - [x] Initialize FastAPI app with title, version, description
  - [x] Add CORS middleware
    - [x] Configure origins for frontend (localhost:3000, deployed URLs)
    - [x] Allow credentials, all methods, all headers
  - [x] Register middleware: `app.middleware("http")(add_request_id_header)`
  - [x] Include routers with `/api` prefix
- [x] Create `tests/conftest.py`
  - [x] `mock_graph` fixture - returns MagicMock with invoke method
  - [x] `mock_graph_result` fixture - sample agent state dict
  - [x] `client` fixture - TestClient with overridden get_graph dependency
- [x] Create `tests/test_main.py`
  - [x] Test POST /api/messages success returns MessageResponse
  - [x] Test POST /api/messages validation rejects empty question
  - [x] Test POST /api/messages handles agent errors → 500
  - [x] Test POST /api/messages processes all 7 categories (parametrized)
  - [x] Test GET /api/health returns healthy status
  - [x] Test GET /api/health includes version
  - [x] Test CORS headers present in responses
  - [x] Test CORS preflight OPTIONS request
  - [x] Test request ID header present in responses
- [x] Run `pytest tests/test_main.py -v` (must pass)
- [x] Run `pytest tests/ -v` (all tests must pass)
- [x] Run `pre-commit run --all-files` (must pass)
- [x] Commit changes: `git add app/main.py app/middleware.py tests/conftest.py tests/test_main.py && git commit`

**Actual**: All tests passing (31 tests)

**CORS Note**: Configured early to avoid debugging CORS issues during frontend integration.

**Agent Import Path**: Agent uses `packages = ["src"]`, so import is `from src.graph import graph` after `pip install -e ../agent`.

---

## Phase 5: Lambda Handler ✅

Create AWS Lambda handler using Mangum adapter.

- [x] Create `app/handler.py`
  - [x] Import app from `app.main`
  - [x] Create handler: `handler = Mangum(app)`
  - [x] Add docstring explaining Lambda invocation
- [x] Create `tests/test_handler.py`
  - [x] Test handler is Mangum instance
  - [x] Test handler callable with mock API Gateway V2 event
  - [x] Test health endpoint via Lambda event
  - [x] Test messages endpoint via Lambda event
  - [x] Test invalid request handling via Lambda event
  - [x] Test agent error handling via Lambda event (added)
- [x] Run `pytest tests/test_handler.py -v` (must pass)
- [x] Run `pytest tests/ -v` (all tests must pass)
- [x] Run `pre-commit run --all-files` (must pass)
- [x] Commit changes: `git add app/handler.py tests/test_handler.py && git commit`

**Actual**: 6 tests passing (37 unit tests total)

**Lambda Event Format**: API Gateway HTTP API (v2.0) event structure.

### Post-Phase 5 Enhancement: Async Agent Invocation

- [x] Switch from `graph.invoke()` to `await graph.ainvoke()` in routes
  - [x] Update `app/routers/messages.py` to use async invocation
  - [x] Update `MockGraph` in `tests/conftest.py` to support `ainvoke()`
  - [x] Update error mocks in `tests/test_main.py` and `tests/test_handler.py`
  - [x] Update `tests/test_dependencies.py` to verify `ainvoke()` method
  - [x] Update docstrings in `app/dependencies.py`
- [x] Run `pytest tests/ -v` (all 37 tests must pass)
- [x] Run `pre-commit run --all-files` (must pass)
- [x] Commit changes: `git add app/ tests/ && git commit`

**Rationale**: Using async `ainvoke()` provides non-blocking I/O for OpenAI API calls, following FastAPI best practices. Prepares for Phase 6 async boto3 Lambda proxy.

---

## Phase 6: Docker & Deployment Configuration

Configure dual-mode dependencies and Docker containers for local/production environments.

### Dual-Mode Dependencies

- [x] Update `app/dependencies.py`
  - [x] Add `AgentLambdaProxy` class
    - [x] Wrap aioboto3 Lambda client (async)
    - [x] Implement `async def ainvoke(state)` method matching agent graph interface
    - [x] Parse Lambda JSON response to state dict
    - [x] Add type hints and error handling
  - [x] Update `get_graph()` function
    - [x] Check `os.getenv("ENVIRONMENT") == "dev"`
    - [x] Dev mode: Import `from src.graph import graph` (local agent)
    - [x] Production mode: Return `AgentLambdaProxy(function_name)`
    - [x] Log which mode is active
  - [x] Add docstring explaining dual-mode pattern
- [x] Add `aioboto3 >= 13.0` to `pyproject.toml` dependencies (async boto3)
- [x] Create `tests/test_dependencies_lambda.py`
  - [x] Test `AgentLambdaProxy.ainvoke()` with mocked aioboto3 client
  - [x] Test `get_graph()` returns local agent when `ENVIRONMENT=dev`
  - [x] Test `get_graph()` returns proxy when `ENVIRONMENT=prod`
  - [x] Test Lambda invocation error handling (timeout, payload errors)
  - [x] Test JSON serialization/deserialization of state

### Docker Configuration

- [x] Create `Dockerfile` (production Lambda)
  - [x] Multi-stage build: builder + runtime (match agent pattern)
  - [x] Base image: `python:3.11-slim`
  - [x] Builder: Install uv, copy only API code, no agent
  - [x] Runtime: Copy built artifacts, set CMD for Lambda
  - [x] Add labels: version from pyproject.toml, service name
- [x] Create `.dockerignore`
  - [x] Exclude `.venv`, `__pycache__`, `*.pyc`
  - [x] Exclude `tests/`, `.env`, `.git`
  - [x] Exclude `.pytest_cache`, `.ruff_cache`, `.mypy_cache`
- [x] Create `.env.example`
  - [x] Document `ENVIRONMENT=dev` for local (SAM CLI)
  - [x] Document `OPENAI_API_KEY` requirement
  - [x] Document `AWS_REGION`, `AGENT_LAMBDA_FUNCTION_NAME` for production
  - [x] Add to version control (safe template)
- [x] Ensure `.env` is in `.gitignore`

### Validation

- [x] Run `pytest tests/ -v` (all tests must pass, ~45 total)
- [x] Run `pre-commit run --all-files` (must pass)
- [x] Commit changes: `git add app/dependencies.py Dockerfile .env.example .dockerignore tests/test_dependencies_lambda.py pyproject.toml && git commit`

**Note**: Docker image build is validated in GitHub CI, not locally.

**Actual**: 7 new tests (44 total - 37 existing + 7 Lambda proxy tests)

**Design Note**: Route handlers remain unchanged - they call `await graph.ainvoke()` whether it's the local agent or Lambda proxy.

---

## Phase 7: Local Development & SAM Configuration ✅

Configure local development workflow and AWS SAM for optional Lambda testing.

### SAM Template (Optional - requires Docker)

- [x] Create `template.yaml`
  - [x] `AWS::Serverless::Function` resource
    - [x] Runtime: python3.11
    - [x] Handler: app.handler.handler
    - [x] Memory: 512MB, Timeout: 30s
    - [x] Environment variables: `ENVIRONMENT`, `AGENT_LAMBDA_FUNCTION_NAME`, `AWS_REGION`
    - [x] Events: `HttpApi` with API Gateway v2 routes
      - [x] `POST /api/messages`
      - [x] `GET /api/health`
  - [x] `AWS::Serverless::HttpApi` resource (API Gateway v2)
  - [x] Outputs: API endpoint URL, Lambda function ARN
- [x] Create `samconfig.toml`
  - [x] `[default.local_invoke.parameters]`
    - [x] `env_vars`: Path to `.env` file
    - [x] `docker_network`: Host network for agent Lambda access
  - [x] `[default.local_start_api.parameters]`
    - [x] `env_vars`: Path to `.env` file
    - [x] `port`: 3001 (avoid conflict with frontend 3000)

### SAM Test Events (Optional)

- [x] Create `tests/events/` directory
- [x] Create `tests/events/messages-post.json`
  - [x] API Gateway v2 event for POST /api/messages
  - [x] Sample question in body
- [x] Create `tests/events/health-get.json`
  - [x] API Gateway v2 event for GET /api/health

### Documentation

- [x] Update `CLAUDE.md` with SAM section
  - [x] Installation: `brew install aws-sam-cli` (Mac) or pip
  - [x] Local invoke: `sam local invoke -e tests/events/messages-post.json`
  - [x] Local API: `sam local start-api --warm-containers EAGER`
  - [x] Direct FastAPI testing: `fastapi dev app/main.py`
  - [x] Testing: `curl http://localhost:8000/api/health`
  - [x] Troubleshooting: Docker daemon, .env file, network issues

### Validation (Direct FastAPI - No Docker Required)

- [x] Create `.env` file with `ENVIRONMENT=dev` and `OPENAI_API_KEY`
- [x] Run `fastapi dev app/main.py` (starts on port 8000)
- [x] Test health endpoint: `curl http://localhost:8000/api/health`
- [x] Test messages endpoint: `curl -X POST http://localhost:8000/api/messages -H "Content-Type: application/json" -d '{"question":"What car did we rent?"}'`
- [x] Verify existing tests pass: `uv run pytest tests/ -v -m "not integration"` (44 tests)
- [x] Commit changes: `git add template.yaml samconfig.toml tests/events/ CLAUDE.md && git commit`

### Optional SAM Validation (Requires Docker Desktop)

**Note**: SAM CLI is optional for daily development. Only use if you have Docker Desktop installed and want to test Lambda packaging.

- [ ] Install Docker Desktop and start daemon
- [ ] Run `sam validate` (template must be valid)
- [ ] Run `sam local invoke -e tests/events/health-get.json` (succeeds)
- [ ] Run `sam local start-api` (starts on port 3001)
- [ ] Test via SAM: `curl http://localhost:3001/api/health`

**Expected**: No new tests (infrastructure config)

**Design Notes**:
- **Primary workflow**: Use `fastapi dev` for daily development (no Docker needed)
- **SAM is optional**: Only needed for pre-deployment Lambda testing
- **Existing tests**: `tests/test_handler.py` already validates Lambda events
- SAM provides production-identical Lambda environment, but FastAPI + pytest covers 99% of use cases

---

## Phase 8: Integration Tests

Add end-to-end tests with real OpenAI API.

### Integration Test Framework

- [ ] Create `tests/integration/` directory
- [ ] Create `tests/integration/__init__.py`
- [ ] Create `tests/integration/conftest.py`
  - [ ] Add `pytest_configure` hook to skip if `OPENAI_API_KEY` not set
  - [ ] Add `integration_client` fixture (TestClient with real agent, no mocks)
  - [ ] Override `get_graph` dependency to use real agent (force `ENVIRONMENT=dev`)
  - [ ] Add docstring explaining integration test setup

### Integration Tests

- [ ] Create `tests/integration/test_api_integration.py`
  - [ ] Test POST /api/messages with real flight question
    - [ ] Verify answer not empty
    - [ ] Verify category is "flights"
    - [ ] Verify confidence > 0.5
  - [ ] Test POST /api/messages for all 7 categories (parametrized)
    - [ ] Questions: flights, lodging, transportation, activities, food, general, budget
    - [ ] Verify category matches expected
    - [ ] Verify answer relevance
  - [ ] Test GET /api/health returns healthy
  - [ ] Test general question handling (confidence check)
  - [ ] Test request ID header present
  - [ ] Mark all tests with `@pytest.mark.integration`

### Validation

- [ ] Update `pyproject.toml` (verify pytest markers configured)
- [ ] Run `pytest tests/ -v -m "not integration"` (unit tests pass, ~45 tests)
- [ ] Run `pytest tests/ -v -m integration` (skip without API key, ~11 skipped)
- [ ] Set `OPENAI_API_KEY` and run integration tests (~11 passed)
- [ ] Run `pre-commit run --all-files` (must pass)
- [ ] Commit changes: `git add tests/integration/ && git commit`

**Expected**: ~11 integration tests (~56 total tests)

**Test Organization**:
```
tests/
├── test_schemas.py                # Unit (~11 tests)
├── test_dependencies.py           # Unit (~4 tests)
├── test_dependencies_lambda.py    # Unit (~8 tests, Phase 6)
├── test_main.py                   # Unit (~15 tests, mocked agent)
├── test_handler.py                # Unit (~6 tests)
├── conftest.py                    # Shared unit test fixtures
└── integration/                   # Real API tests
    ├── __init__.py
    ├── conftest.py                # Integration fixtures
    └── test_api_integration.py    # End-to-end (~11 tests)
```

**Pytest Markers**:
- Unit tests (default): Fast, mocked agent, no API key needed
- `@pytest.mark.integration`: Real OpenAI API, requires `OPENAI_API_KEY`

**Running Tests**:
```bash
# Unit tests only (fast, no API key)
pytest tests/ -v -m "not integration"

# Integration tests only (requires API key)
pytest tests/ -v -m integration

# All tests
pytest tests/ -v
```

---

## Phase 9: CI/CD Pipeline

Add GitHub Actions workflow for automated testing, building, and deployment.

### CI/CD Configuration

- [ ] Create `.github/workflows/api-ci.yml`
  - [ ] **Job 1: unit-tests**
    - [ ] Matrix: Python 3.11, 3.12, 3.13
    - [ ] Checkout code
    - [ ] Install uv
    - [ ] Install API dependencies: `cd api && uv sync`
    - [ ] Install agent for imports: `uv pip install --system -e "../agent"`
    - [ ] Set `ENVIRONMENT=dev` (force local agent import)
    - [ ] Run: `uv run pytest tests/ -v -m "not integration"`
  - [ ] **Job 2: integration-tests**
    - [ ] Condition: Only on push to main (save OpenAI API costs)
    - [ ] Python 3.11 only
    - [ ] Install dependencies (same as unit-tests)
    - [ ] Set `ENVIRONMENT=dev` and `OPENAI_API_KEY` from secrets
    - [ ] Run: `uv run pytest tests/ -v -m integration`
    - [ ] Note: Uses TestClient (NOT SAM CLI or Lambda invoke)
  - [ ] **Job 3: quality-checks**
    - [ ] Python 3.11
    - [ ] Install uv and pre-commit
    - [ ] Run: `pre-commit run --all-files`
  - [ ] **Job 4: build-docker**
    - [ ] Depends on: unit-tests, quality-checks
    - [ ] Set up Docker Buildx
    - [ ] Build production `Dockerfile` (API code only, no agent)
    - [ ] Tag with commit SHA for verification
    - [ ] No push (push happens in next job)
  - [ ] **Job 5: push-to-ecr**
    - [ ] Condition: Only on push to main
    - [ ] Depends on: build-docker
    - [ ] Configure AWS credentials (OIDC or access keys)
    - [ ] Login to ECR
    - [ ] Extract version: `python -c "import tomllib; print(tomllib.load(open('api/pyproject.toml', 'rb'))['project']['version'])"`
    - [ ] Build and tag with 3 tags:
      - [ ] `<ecr-repo>:<git-sha-short>`
      - [ ] `<ecr-repo>:v<version>`
      - [ ] `<ecr-repo>:latest`
    - [ ] Push all tags to ECR
  - [ ] **Job 6: create-release**
    - [ ] Condition: Only on push to main
    - [ ] Depends on: push-to-ecr, integration-tests
    - [ ] Extract version from `pyproject.toml`
    - [ ] Create git tag: `api-v<version>` (prefixed to avoid agent collision)
    - [ ] Create GitHub release with CHANGELOG excerpt
    - [ ] Attach release notes from `CHANGELOG.md`

### Release Documentation

- [ ] Create `CHANGELOG.md`
  - [ ] Format: Keep a Changelog (https://keepachangelog.com)
  - [ ] Sections: Added, Changed, Fixed, Removed
  - [ ] Version v0.1.0: Document Phases 1-5 (FastAPI routes, Lambda handler, 37 unit tests)
  - [ ] Unreleased section: Phases 6-9 (dual-mode deps, SAM config, integration tests, CI/CD)

### Validation

- [ ] Push to feature branch and verify workflow runs
- [ ] Verify unit tests pass on Python 3.11, 3.12, 3.13
- [ ] Verify quality checks pass (ruff, mypy, pre-commit)
- [ ] Verify Docker build succeeds
- [ ] Verify integration tests are skipped on feature branch (only run on main)
- [ ] Verify ECR push and release jobs are skipped on feature branch
- [ ] Commit changes: `git add .github/workflows/api-ci.yml CHANGELOG.md && git commit`

**Expected**: No new tests (CI/CD infrastructure)

**Design Notes**:
- Matches `agent-ci.yml` pattern for consistency
- Integration tests use TestClient (direct FastAPI testing), NOT Lambda invoke
- SAM CLI is for local development only, not CI/CD
- `ENVIRONMENT=dev` forces local agent import in CI (simpler than boto3 mocking)
- Integration tests only on main to control OpenAI API costs
- 3-tag strategy enables version rollback and latest tracking

---

## Completion Criteria

- [x] Phase 1 completed (Project setup & schemas)
- [x] Phase 2 completed (Dependencies & agent initialization)
- [x] Phase 3 completed (API routes)
- [x] Phase 4 completed (FastAPI app & middleware)
- [x] Phase 5 completed (Lambda handler)
- [x] Phase 6 completed (Docker & deployment configuration)
- [x] Phase 7 completed (Local development & SAM configuration)
- [ ] Phase 8 completed (Integration tests)
- [ ] Phase 9 completed (CI/CD pipeline)
- [x] All unit tests passing (44 tests, mocked agent)
- [ ] Integration tests ready (~11 tests, skip without API key)
- [x] All quality checks passing (ruff, mypy, pre-commit)
- [x] Dual-mode dependencies work (dev imports local, prod calls Lambda)
- [x] Production Dockerfile builds successfully
- [x] Direct FastAPI development works (`fastapi dev app/main.py`)
- [x] SAM template valid for deployment (Docker optional for local testing)
- [ ] Integration tests validated with real OpenAI API
- [ ] CI/CD pipeline runs all jobs successfully
- [ ] Version tagging works (api-v prefix, 3-tag strategy)
- [x] Ready for frontend integration (via direct FastAPI or SAM)
- [x] Ready for AWS Lambda deployment (via infra/)
