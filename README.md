# Trip Assistant

<!-- CI/CD Status -->
[![Agent Service CI](https://github.com/OsherKoren/trip-assistant/actions/workflows/agent-ci.yml/badge.svg)](https://github.com/OsherKoren/trip-assistant/actions/workflows/agent-ci.yml)
[![API Service CI](https://github.com/OsherKoren/trip-assistant/actions/workflows/api-ci.yml/badge.svg)](https://github.com/OsherKoren/trip-assistant/actions/workflows/api-ci.yml)
[![Frontend CI](https://github.com/OsherKoren/trip-assistant/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/OsherKoren/trip-assistant/actions/workflows/frontend-ci.yml)
[![Infrastructure CI](https://github.com/OsherKoren/trip-assistant/actions/workflows/infra-ci.yml/badge.svg)](https://github.com/OsherKoren/trip-assistant/actions/workflows/infra-ci.yml)
[![Deploy to AWS Lambda](https://github.com/OsherKoren/trip-assistant/actions/workflows/deploy.yml/badge.svg)](https://github.com/OsherKoren/trip-assistant/actions/workflows/deploy.yml)
[![Deploy Frontend](https://github.com/OsherKoren/trip-assistant/actions/workflows/frontend-deploy.yml/badge.svg)](https://github.com/OsherKoren/trip-assistant/actions/workflows/frontend-deploy.yml)

<!-- Test Coverage -->
[![Agent Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OsherKoren/trip-assistant/main/badges/agent-coverage.json)](https://github.com/OsherKoren/trip-assistant/actions/workflows/agent-ci.yml)
[![API Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OsherKoren/trip-assistant/main/badges/api-coverage.json)](https://github.com/OsherKoren/trip-assistant/actions/workflows/api-ci.yml)
[![Frontend Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OsherKoren/trip-assistant/main/badges/frontend-coverage.json)](https://github.com/OsherKoren/trip-assistant/actions/workflows/frontend-ci.yml)

<!-- Code Quality -->
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/type%20checker-mypy-blue.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

<!-- Tech Stack -->
[![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.x-1C3C3C.svg?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900.svg?logo=awslambda&logoColor=white)](https://aws.amazon.com/lambda/)
[![Terraform](https://img.shields.io/badge/Terraform-1.x-7B42BC.svg?logo=terraform&logoColor=white)](https://www.terraform.io/)

A LangGraph-powered Q&A assistant for family travel planning. Built as a monorepo with 3 application services and cloud infrastructure for flexible deployment.

## Overview

Trip Assistant helps families plan trips by answering questions about flights, accommodations, routes, and destinations. The agent uses topic-based routing to specialized nodes for accurate, context-aware responses.

**Trip Context:** France & Italy Alps, July 7-20, 2026, 5 family members

## Architecture

```
┌─────────────┐
│   Frontend  │  React chat interface
└──────┬──────┘
       │
       v
┌─────────────┐
│     API     │  FastAPI backend
└──────┬──────┘
       │
       v
┌─────────────┐
│    Agent    │  LangGraph state machine
└──────┬──────┘
       │
       v
  Classifier → Router → Specialists
  (flights, hotels, routes, destinations)
```

## Application Services

| Service | Path | Description | Status |
|---------|------|-------------|--------|
| **Agent** | [`./agent/`](./agent/README.md) | LangGraph agent with topic routing | ✅ Complete |
| **API** | [`./api/`](./api/CHANGELOG.md) | FastAPI backend serving the agent | ✅ Complete |
| **Frontend** | [`./frontend/`](./frontend/) | React chat interface | ✅ Complete |

## Infrastructure

| Component | Path | Description | Status |
|-----------|------|-------------|--------|
| **Infra** | [`./infra/`](./infra/) | AWS Lambda deployment (Terraform, Docker, ECR) | ✅ Complete |

## Quick Start

### Agent Service (Core)

```bash
cd agent
uv pip install -e .
cp .env.example .env  # Add your OPENAI_API_KEY
uv run pytest tests/ -v
```

### API Service

```bash
cd api
uv pip install -e ".[dev]"
cp .env.example .env  # Add your OPENAI_API_KEY, set ENVIRONMENT=dev

# Run tests
uv run pytest tests/ -v

# Local development server
fastapi dev app/main.py
```

### Run All Tests

```bash
# From repository root
uv run pytest agent/tests/ api/tests/ -v
```

### Quality Checks

```bash
# Run pre-commit hooks across all services
uv run pre-commit run --all-files
```

## Documentation

- [`docs/architecture.md`](./docs/architecture.md) - System design and data flow
- [`docs/data-model.md`](./docs/data-model.md) - State schema and document structure
- [`CLAUDE.md`](./CLAUDE.md) - Development guide and conventions

## Tech Stack

- **Agent**: LangGraph 1.x, LangChain, OpenAI GPT-4
- **API**: FastAPI, Python 3.11+
- **Frontend**: React, TypeScript, Tailwind CSS
- **Infra**: AWS Lambda, Terraform, Docker

## Development

This is a monorepo with separate application services and infrastructure:

**Application Services** (agent, api, frontend):
- `README.md` - Service-specific documentation
- `pyproject.toml` or `package.json` - Dependencies
- `tests/` - Service-specific tests

**Infrastructure** (infra):
- Terraform configuration for AWS resources
- Dockerfiles and deployment scripts
- No independent tests (validated via service deployments)

**Git Workflow:**
- Work on feature branches (e.g., `feature/agent`)
- Never commit directly to `main`
- All changes to `main` via pull requests
- CI/CD runs tests and deploys automatically

## Project Status

**Current Phase:** Feature refinement and polish

**Completed:**
- Agent service (LangGraph classifier → router → specialists)
- API service (FastAPI + Mangum Lambda handler + feedback endpoint)
- Frontend (React chat with markdown rendering, confidence scores, user feedback)
- Terraform modules (ECR, Lambda, API Gateway, Cognito, DynamoDB, SES, S3/CloudFront)
- CI/CD pipelines (deploy.yml with OIDC auth, smoke tests, auto-rollback)

## Contributing

1. Check service-specific `CLAUDE.md` files for development guidelines
2. Follow TDD: write tests before implementation
3. Run `pre-commit run --all-files` before committing
4. Keep changes focused and atomic

## License

Private project for family use.
