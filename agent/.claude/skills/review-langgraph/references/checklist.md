# LangGraph Code Review Checklist

Quick reference for reviewing LangGraph 1.x code. Check each item for compliance.

## State Management ✓

- [ ] StateGraph used (not MessageGraph)
- [ ] State is TypedDict with all fields typed
- [ ] Nodes return new dicts (no mutations like `state["key"] = value`)
- [ ] messages field uses `Annotated[list, add_messages]`
- [ ] Routing fields use Literal types (e.g., `Literal["flights", "hotels"]`)
- [ ] Optional fields typed as `Field | None`

## Graph Structure ✓

- [ ] Imports: `from langgraph.graph import StateGraph, START, END`
- [ ] Graph initialized: `graph = StateGraph(StateType)`
- [ ] Nodes added before edges
- [ ] START edge defined: `graph.add_edge(START, "first_node")`
- [ ] END edges defined for all terminal nodes
- [ ] Conditional edges have proper routing function
- [ ] Graph compiled: `app = graph.compile()`

## Node Functions ✓

- [ ] Type signature: `def node(state: StateType) -> dict:`
- [ ] Returns dict with partial state updates
- [ ] Does not mutate input state
- [ ] Has docstring explaining purpose
- [ ] Error handling for LLM/external calls
- [ ] Logging for debugging (using logger from logger-usage.md)

## LLM Integration ✓

- [ ] ChatOpenAI imported from langchain_openai
- [ ] Model specified explicitly (no defaults)
- [ ] Temperature set appropriately
- [ ] Uses `with_structured_output()` for structured responses
- [ ] Pydantic models defined for structured outputs
- [ ] System prompts defined as constants
- [ ] Error handling wraps LLM invocations

## Routing ✓

- [ ] Routing function typed: `def route(state: StateType) -> str:`
- [ ] Returns node name as string
- [ ] Handles None/missing values
- [ ] Has fallback for unexpected values
- [ ] Matches node names exactly (case-sensitive)

## Testing ✓

- [ ] Unit test exists: `tests/test_<module>.py`
- [ ] Integration test marked: `@pytest.mark.integration`
- [ ] Unit tests mock LLM calls (no API)
- [ ] Integration tests use real API (with OPENAI_API_KEY)
- [ ] Tests check return types
- [ ] Tests validate state updates
- [ ] Fixtures in conftest.py for common state

## Performance ✓

- [ ] Documents loaded once, not per query
- [ ] LLM instances reused when possible
- [ ] Appropriate model for task (gpt-4o-mini for simple, gpt-4o for complex)
- [ ] No unnecessary state fields
- [ ] Streaming enabled if needed

## Error Handling ✓

- [ ] try/except around LLM calls
- [ ] User-friendly error messages
- [ ] Fallback behavior defined
- [ ] Errors logged with context
- [ ] No silent failures

## Type Safety ✓

- [ ] All functions have type hints
- [ ] State fields properly typed in TypedDict
- [ ] No `Any` types (unless necessary)
- [ ] Pydantic models for structured data
- [ ] mypy passes with no errors

## Code Quality ✓

- [ ] No duplicate code across nodes
- [ ] Constants for prompts and configs
- [ ] Clear function/variable names
- [ ] Docstrings for public functions
- [ ] Follows project conventions (CLAUDE.md)
- [ ] pre-commit hooks pass

## Documentation ✓

- [ ] Docstrings explain node purpose
- [ ] Complex logic has comments
- [ ] TASKS.md updated if feature complete
- [ ] README updated if user-facing change

---

## Priority Levels

### 🔴 Critical (Must Fix)
- State mutations
- Missing error handling
- Type errors
- Test failures

### 🟡 Important (Should Fix)
- Missing structured output
- Untyped functions
- No integration tests
- Poor error messages

### 🟢 Nice to Have
- Code duplication
- Performance optimizations
- Better logging
- Documentation improvements
