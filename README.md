# Trip Assistant

A LangGraph-powered Q&A assistant for family travel planning. Built as a monorepo with 3 application services and cloud infrastructure for flexible deployment.

## Overview

Trip Assistant helps families plan trips by answering questions about flights, accommodations, routes, and destinations. The agent uses topic-based routing to specialized nodes for accurate, context-aware responses.

**Trip Context:** France/Italy Alps, July 7-20, 2026, 5 family members

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
| **API** | [`./api/`](./api/CHANGELOG.md) | FastAPI backend serving the agent | 🚧 In Progress |
| **Frontend** | [`./frontend/`](./frontend/) | React chat interface | 🚧 Planned |

## Infrastructure

| Component | Path | Description | Status |
|-----------|------|-------------|--------|
| **Infra** | [`./infra/`](./infra/) | AWS Lambda deployment (Terraform, Docker) | 🚧 Planned |

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
- **Frontend**: React, TypeScript
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

**Current Phase:** API service in progress (endpoints, Lambda handler, tests complete)

**Next Steps:**
1. Finalize API service and merge to main
2. Frontend development
3. Infrastructure setup and deployment

## Contributing

1. Check service-specific `CLAUDE.md` files for development guidelines
2. Follow TDD: write tests before implementation
3. Run `pre-commit run --all-files` before committing
4. Keep changes focused and atomic

## License

Private project for family use.
