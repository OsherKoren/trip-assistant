# Agent Service

LangGraph 1.x agent with topic-based routing for trip Q&A.

## Key Files

```
agent/
├── TASKS.md              # Development task tracking
├── src/
│   ├── state.py          # TripAssistantState TypedDict
│   ├── documents.py      # Load data/*.txt files
│   ├── graph.py          # Main graph definition
│   └── nodes/            # Classifier + specialist nodes
├── data/                 # Trip documents (6 txt files)
└── tests/
```

## Setup

- **Python**: 3.11+
- **Environment**: Requires `OPENAI_API_KEY` environment variable
- **Install**: `pip install -e .` from the agent directory
- **Dependencies**: langgraph >= 1.0, langchain-openai, pydantic

## Development Workflow (MUST FOLLOW)

1. Read `TASKS.md` - find next unchecked `[ ]` task
2. Write unit test first (TDD)
3. Implement the feature/fix
4. Run `pytest tests/ -v` (must pass)
5. Run `pre-commit run --all-files` (must pass)
6. Update `TASKS.md` - mark task `[x]` complete

**Rules:**
- Only implement tasks listed in `TASKS.md`
- Complex requests: use Plan Mode first, then add tasks to `TASKS.md`

## Commands

```bash
pytest tests/ -v              # Run tests
pre-commit run --all-files    # Quality checks
mypy src/                     # Type check
```

## Common Pitfalls

**LangGraph 1.x Specific:**
- Don't use `MessageGraph` (legacy) - use `StateGraph` from langgraph 1.x
- Don't mutate state in nodes - return new dicts, don't modify in place
- Don't forget to type all nodes with `TripAssistantState`
- Don't use `add_node` without proper type hints

**Testing:**
- Always run pytest before claiming a task is complete
- Don't skip pre-commit hooks - they catch issues early
- Test failures = implementation not complete

**File Operations:**
- Don't create new files unless absolutely necessary
- Prefer editing existing files over creating new ones

## Naming Conventions

- **Node functions**: `{action}_node` (e.g., `classify_node`, `route_node`)
- **Test files**: `test_{module}.py` matching source file names
- **Data files**: lowercase with underscores in `data/` directory
- **State fields**: snake_case matching TypedDict definition

## Dependencies

- langgraph >= 1.0
- langchain-openai
- pydantic
