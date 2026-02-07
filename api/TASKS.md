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

## Phase 2: Dependencies & Agent Initialization

Create dependency injection layer for the agent graph.

- [ ] Create `app/dependencies.py`
  - [ ] Import logger from `app.logger`
  - [ ] Implement `get_graph()` function
    - [ ] Import and return compiled agent graph
    - [ ] Handle import errors gracefully (raise HTTPException 500)
    - [ ] Log errors and successful initialization
    - [ ] Add type hints for return type
  - [ ] Add docstrings explaining dependency injection pattern
- [ ] Create `tests/test_dependencies.py`
  - [ ] Test `get_graph()` returns callable with invoke method
  - [ ] Test dependency override mechanism works (for testing)
  - [ ] Test handles agent import error gracefully
  - [ ] Test graph can be invoked with sample state
- [ ] Run `pytest tests/test_dependencies.py -v` (must pass)
- [ ] Run `pre-commit run --all-files` (must pass)
- [ ] Commit changes: `git add app/dependencies.py tests/test_dependencies.py && git commit`

**Expected**: ~4 tests passing

**Design Note**: Using dependency injection (`Depends(get_graph)`) allows easy mocking in tests via `app.dependency_overrides`.

---

## Phase 3: FastAPI App & Routes

Build the FastAPI application with CORS support and endpoints.

- [ ] Create `app/main.py`
  - [ ] Import logger from `app.logger`
  - [ ] Initialize FastAPI app with title, version, description
  - [ ] Add CORS middleware
    - [ ] Configure origins for frontend (localhost:3000, deployed URLs)
    - [ ] Allow credentials, all methods, all headers
  - [ ] Implement `POST /api/messages`
    - [ ] Accept `MessageRequest`
    - [ ] Use `Depends(get_graph)` to get agent
    - [ ] Log incoming request (question preview)
    - [ ] Invoke agent with `{"question": request.question}`
    - [ ] Return `MessageResponse` with answer, category, confidence, source
    - [ ] Handle errors → 500 with `ErrorResponse` and log errors
  - [ ] Implement `GET /api/health`
    - [ ] Return `HealthResponse` with status="healthy", service="trip-assistant-api", version from package
    - [ ] Lightweight check (no agent dependency)
- [ ] Create `tests/conftest.py`
  - [ ] `mock_graph` fixture - returns MagicMock with invoke method
  - [ ] `mock_graph_result` fixture - sample agent state dict
  - [ ] `client` fixture - TestClient with overridden get_graph dependency
- [ ] Create `tests/test_main.py`
  - [ ] Test POST /api/messages success returns MessageResponse
  - [ ] Test POST /api/messages validation rejects empty question
  - [ ] Test POST /api/messages handles agent errors → 500
  - [ ] Test POST /api/messages processes all 7 categories (parametrized)
  - [ ] Test GET /api/health returns healthy status
  - [ ] Test GET /api/health includes version
  - [ ] Test CORS headers present in responses
  - [ ] Test CORS preflight OPTIONS request
- [ ] Run `pytest tests/test_main.py -v` (must pass)
- [ ] Run `pytest tests/ -v` (all ~15 tests must pass)
- [ ] Run `pre-commit run --all-files` (must pass)
- [ ] Commit changes: `git add app/main.py tests/conftest.py tests/test_main.py && git commit`

**Expected**: ~15 tests passing

**CORS Note**: Configured early to avoid debugging CORS issues during frontend integration.

**Agent Import Path**: Agent uses `packages = ["src"]`, so import is `from src.graph import graph` after `pip install -e ../agent`.

---

## Phase 4: Lambda Handler

Create AWS Lambda handler using Mangum adapter.

- [ ] Create `app/handler.py`
  - [ ] Import app from `app.main`
  - [ ] Create handler: `handler = Mangum(app)`
  - [ ] Add docstring explaining Lambda invocation
- [ ] Create `tests/test_handler.py`
  - [ ] Test handler is Mangum instance
  - [ ] Test handler callable with mock API Gateway V2 event
  - [ ] Test health endpoint via Lambda event
  - [ ] Test messages endpoint via Lambda event
  - [ ] Test invalid request handling via Lambda event
- [ ] Run `pytest tests/test_handler.py -v` (must pass)
- [ ] Run `pytest tests/ -v` (all ~20 tests must pass)
- [ ] Run `pre-commit run --all-files` (must pass)
- [ ] Commit changes: `git add app/handler.py tests/test_handler.py && git commit`

**Expected**: ~5 tests passing (~20 unit total)

**Lambda Event Format**: API Gateway HTTP API (v2.0) event structure.

---

## Phase 5: Dockerfile

Create containerized deployment configuration.

- [ ] Create `Dockerfile`
  - [ ] Base image: `python:3.11-slim`
  - [ ] Set working directory: `/app`
  - [ ] Copy all files
  - [ ] Install api package: `pip install --no-cache-dir -e .`
  - [ ] Install agent package: `pip install --no-cache-dir -e ../agent`
  - [ ] CMD: `["fastapi", "run", "app/main.py", "--port", "8000"]`
  - [ ] Add comments for Lambda vs container deployment
- [ ] Create `.dockerignore`
  - [ ] Exclude `.venv`, `__pycache__`, `*.pyc`
  - [ ] Exclude `tests/`, `.env`, `.git`
  - [ ] Exclude `.pytest_cache`, `.ruff_cache`, `.mypy_cache`
- [ ] Run `pre-commit run --all-files` (must pass)
- [ ] Commit changes: `git add Dockerfile .dockerignore && git commit`

**Expected**: No new tests (infrastructure files)

**Note**: Dockerfile supports both local development and container deployment (ECS). Lambda uses handler directly.

---

## Phase 6: Integration Tests

Add end-to-end tests with real agent (requires OPENAI_API_KEY).

- [ ] Create `.env.example` template file
  - [ ] Document OPENAI_API_KEY requirement
  - [ ] Add to version control (safe template)
- [ ] Ensure `.env` is in `.gitignore`
- [ ] Create `tests/integration/` directory
- [ ] Create `tests/integration/__init__.py`
- [ ] Create `tests/integration/conftest.py`
  - [ ] Add pytest hook to skip if OPENAI_API_KEY not set
  - [ ] Add `integration_client` fixture (TestClient with real agent, no mocks)
- [ ] Create `tests/integration/test_api_integration.py`
  - [ ] Test POST /api/messages with flight question (real end-to-end)
  - [ ] Test POST /api/messages for 6 categories (parametrized)
    - [ ] Verify answer not empty
    - [ ] Verify category matches expected
    - [ ] Verify confidence > 0.5
  - [ ] Test GET /api/health returns healthy
  - [ ] Test general question handling
  - [ ] Mark all tests with `@pytest.mark.integration`
- [ ] Update `pyproject.toml`
  - [ ] Verify pytest markers configured
- [ ] Verify tests skip gracefully without API key (~8 skipped)
- [ ] Verify unit tests still pass with marker (~20 passed)
- [ ] All quality checks passing
- [ ] Commit changes: `git add .env.example tests/integration/ && git commit`

**Expected**: ~8 integration tests (skip without API key), ~28 total tests

**Test Organization**:
```
tests/
├── test_schemas.py           # Unit tests (~7 tests)
├── test_dependencies.py      # Unit tests (~4 tests)
├── test_main.py              # Unit tests (~15 tests, mocked agent)
├── test_handler.py           # Unit tests (~5 tests)
├── conftest.py               # Shared fixtures for unit tests
└── integration/              # Real API tests (new)
    ├── __init__.py
    ├── conftest.py           # Integration fixtures
    └── test_api_integration.py  # End-to-end tests (~8 tests)
```

**Pytest Markers**:
- `@pytest.mark.unit` - Fast, mocked tests (default)
- `@pytest.mark.integration` - Real API tests (requires OPENAI_API_KEY)

**Running Tests**:
```bash
# All unit tests (fast, no API key needed)
pytest tests/ -v -m "not integration"

# Integration tests only (requires API key)
pytest tests/ -v -m integration

# All tests
pytest tests/ -v
```

---

## Completion Criteria

- [ ] Phase 1-5 completed (Core API functionality)
- [ ] Phase 6 completed (Integration tests)
- [ ] All unit tests passing (~20 tests, mocked agent)
- [ ] Integration test framework ready (~8 tests, skip without API key)
- [ ] All quality checks passing (ruff, mypy, pytest)
- [ ] API can be started with `fastapi dev app/main.py`
- [ ] Lambda handler can process API Gateway events
- [ ] Dockerfile builds successfully
- [ ] Integration tests validated with real API (requires OPENAI_API_KEY)
- [ ] Ready for frontend integration
- [ ] Ready for AWS deployment (via infra/)
