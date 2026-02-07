# Agent Service

LangGraph 1.x agent with topic-based routing for trip Q&A.

## Key Files

```
agent/
├── TASKS.md              # Development task tracking
├── CHANGELOG.md          # Version history and changes
├── src/
│   ├── state.py          # TripAssistantState TypedDict
│   ├── documents.py      # Load data/*.txt files
│   ├── graph.py          # Main graph definition
│   └── nodes/
│       ├── classifier.py       # Topic classification node
│       ├── general.py          # General specialist node
│       └── specialist_factory.py  # Factory for specialist nodes
├── data/                 # Trip documents (6 txt files)
└── tests/
    ├── test_error_handling.py  # Error handling tests
    └── integration/            # Real API integration tests
```

## Setup

- **Python**: 3.11+
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- **Environment**: Requires `OPENAI_API_KEY` environment variable for integration tests
- **Install**: `uv pip install -e .` from the agent directory
- **Dependencies**: langgraph >= 1.0, langchain-openai, pydantic

## Environment Setup

1. **Copy `.env.example` to `.env`**:
   ```bash
   cp .env.example .env
   ```

2. **Add your OpenAI API key** to `.env`:
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

3. **Never commit `.env`** (already in .gitignore)

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

### Testing

```bash
# Run all unit tests (fast, mocked, no API key needed)
pytest tests/ -v -m "not integration"

# Run integration tests (real API, requires OPENAI_API_KEY)
pytest tests/integration/ -v

# Run ALL tests (unit + integration)
pytest tests/ -v

# Run specific integration test
pytest tests/integration/test_graph_integration.py -v

# List available test markers
pytest --markers
```

### Quality Checks

```bash
pre-commit run --all-files    # Linting, formatting, type checking
mypy src/                     # Type check only
ruff check src/               # Lint only
```

## Integration Tests

Integration tests make **real API calls** to OpenAI and incur small costs (~$0.01-0.10 per run).

**Setup:**
1. Set `OPENAI_API_KEY` in `.env` file
2. Tests are automatically skipped if the key is not set

**Cost Management:**
- Unit tests are **free** (mocked LLM responses)
- Integration tests cost ~$0.01-0.10 per full run
- Run integration tests only when needed (before commits, CI/CD)

**Test Organization:**
- `tests/` - Unit tests (mocked, fast, free)
- `tests/integration/` - Integration tests (real API, slower, costs money)

## Architecture Highlights

**Specialist Factory Pattern:**
- All specialist nodes (flight, car_rental, routes, aosta, chamonix, annecy_geneva) are created using `specialist_factory.create_specialist()`
- Ensures consistent error handling, logging, and behavior across all specialists
- Reduces code duplication by 57% while maintaining functionality
- To add new specialist: `handle_new = create_specialist("topic", "source.txt")`

**Error Handling:**
- All nodes include try/except blocks for graceful degradation
- Classifier falls back to "general" category on API failure
- Specialists return user-friendly error messages on failure
- Routing function handles missing categories with fallback to general
- Comprehensive test coverage for all error scenarios

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
- Use mocks from `tests/conftest.py` for consistent test data

**File Operations:**
- Don't create new files unless absolutely necessary
- Prefer editing existing files over creating new ones
- Don't create individual specialist files - use specialist factory

## Naming Conventions

- **Node functions**: `{action}_node` (e.g., `classify_node`, `route_node`)
- **Test files**: `test_{module}.py` matching source file names
- **Data files**: lowercase with underscores in `data/` directory
- **State fields**: snake_case matching TypedDict definition

## Dependencies

- langgraph >= 1.0
- langchain-openai
- pydantic
