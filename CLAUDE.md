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
uv run pytest agent/tests/ api/tests/ -v

# Quality checks across all services
uv run pre-commit run --all-files

# Service-specific commands: see ./[service]/CLAUDE.md
```

## Package Management

**Python services (agent, api) use `uv` - NEVER use `pip` directly**

- Install packages: `uv pip install <package>`
- Install editable: `uv pip install -e .`
- Run commands: `uv run <command>` (uses project environment automatically)
- Sync dependencies: `uv sync` (creates/updates uv.lock)

## Common Pitfalls

- **Don't use pip directly** - Always use `uv pip` or `uv run` commands
- **Don't use legacy LangGraph patterns** - Use StateGraph (not MessageGraph)
- **Don't skip tests** - TDD is mandatory; tests must pass before task completion
- **Don't create files unnecessarily** - Prefer editing existing files
- **Don't mutate state** - LangGraph nodes should return new state dicts

## Git Workflow

- **NEVER commit directly to main** - Always work on feature branches (e.g., `feature/agent`)
- **NEVER checkout or switch to main** - Stay on feature branches for all development work
- **Pull requests only** - All changes to main must go through PR review and CI/CD
- **Branch naming** - Use descriptive names like `feature/agent`, `fix/integration-tests`

### Commit Messages

- **Keep it short** - 1-2 sentence summary (under 72 chars for title)
- **Be specific** - "Add schemas for API requests" not "Update files"
- **Focus on what, not how** - The diff shows how, commit explains what/why
- **Always include co-author** - End with `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`

### Pull Request Descriptions

- **Title: Short and specific** - Under 60 chars, imperative mood
- **Body: Brief summary** - 2-3 bullet points max, focus on user impact
- **No verbose details** - Code changes are visible in the diff

## Working on a Service

Each service has its own `CLAUDE.md` with detailed specs. Navigate to the service directory for focused context.

## Docs

- `docs/architecture.md` - System design and data flow
- `docs/data-model.md` - State schema and document structure
