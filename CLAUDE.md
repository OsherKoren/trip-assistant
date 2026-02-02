# Trip Assistant Agent

A LangGraph-powered Q&A assistant for family travel. Monorepo with 4 services.

## Services

| Service | Path | Description |
|---------|------|-------------|
| agent | `./agent/` | LangGraph agent (classifier → router → specialists) |
| api | `./api/` | FastAPI backend serving the agent |
| frontend | `./frontend/` | React chat interface |
| infra | `./infra/` | AWS Lambda deployment (cheap/free tier) |

## Quick Context

- **Trip**: France/Italy Alps, July 7-20, 2026, 5 family members
- **Pattern**: Topic classification → conditional routing → specialist nodes (no RAG)
- **Stack**: LangGraph 1.x, FastAPI, React, AWS Lambda

## Monorepo Commands

```bash
# Run all service tests
pytest agent/tests/ api/tests/ -v

# Quality checks across all services
pre-commit run --all-files

# Service-specific commands: see ./[service]/CLAUDE.md
```

## Common Pitfalls

- **Don't use legacy LangGraph patterns** - Use StateGraph (not MessageGraph)
- **Don't skip tests** - TDD is mandatory; tests must pass before task completion
- **Don't create files unnecessarily** - Prefer editing existing files
- **Don't mutate state** - LangGraph nodes should return new state dicts

## Working on a Service

Each service has its own `CLAUDE.md` with detailed specs. Navigate to the service directory for focused context.

## Docs

- `docs/architecture.md` - System design and data flow
- `docs/data-model.md` - State schema and document structure
