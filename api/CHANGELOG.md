# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Dual-mode dependencies: local agent import (dev) and Lambda proxy (prod)
- `AgentLambdaProxy` class for async Lambda invocation via aioboto3
- AWS SAM template and configuration for local Lambda testing
- SAM test events for health and messages endpoints
- Integration tests with real OpenAI API (11 tests)
- GitHub Actions CI/CD pipeline with 6 jobs
- CHANGELOG.md for release documentation
- `.env.example` with documented configuration options
- Production Dockerfile with multi-stage build
- `.dockerignore` for optimized Docker builds
- Router package exports (`health_router`, `messages_router`) in `routers/__init__.py`

### Changed
- Switched from `graph.invoke()` to `await graph.ainvoke()` for non-blocking I/O
- `get_graph()` dependency now checks `ENVIRONMENT` variable for mode selection
- Move schemas into `routers/` package (co-located with route handlers)
- Use relative imports in routers for schemas

### Fixed
- Use correct Lambda context attribute `aws_request_id` (was `request_id`)

## [0.1.0] - 2026-02-12

### Added
- Initial release of Trip Assistant API
- FastAPI backend exposing LangGraph agent via HTTP
- Pydantic request/response schemas with validation
  - `MessageRequest` with question field (min_length=1)
  - `MessageResponse` with answer, category, confidence, source
  - `HealthResponse` with status, service, version
  - `ErrorResponse` for error handling
- POST `/api/messages` endpoint for agent invocation
- GET `/api/health` endpoint for Lambda warm-up
- Dependency injection with `Depends(get_graph)` for testability
- HTTP middleware for request ID tracing (Lambda context)
- CORS middleware for frontend integration
- Lambda handler via Mangum adapter
- Structured logging with loguru
- Comprehensive unit test suite (44 tests):
  - Schema validation tests (11 tests)
  - Dependency injection tests (4 tests)
  - Route and middleware tests (15 tests)
  - Lambda handler tests (6 tests)
  - Lambda proxy tests (8 tests)
- Pre-commit hooks for code quality (ruff, mypy, pytest)

### Technical Details
- **Python**: 3.11+ required
- **Framework**: FastAPI >= 0.115
- **Lambda**: Mangum >= 0.18 adapter
- **Type Safety**: Full Pydantic v2 and mypy strict mode
- **Testing**: pytest with mocked agent dependencies
- **Code Quality**: ruff linter/formatter, mypy type checker

### Architecture
- **Pattern**: API Gateway → Lambda → FastAPI (Mangum) → Agent
- **Dependencies**: Injected via FastAPI `Depends()` for easy mocking
- **Error Handling**: Generic client errors, detailed server logs
- **Request Tracing**: Lambda request ID in response headers

[unreleased]: https://github.com/OsherKoren/trip-assistant/compare/api-v0.1.0...HEAD
[0.1.0]: https://github.com/OsherKoren/trip-assistant/releases/tag/api-v0.1.0
