---
name: review-fastapi
description: |
  Review FastAPI code for best practices and suggest refactorings.
  Use when: (1) After implementing new endpoints or dependencies, (2) Before creating
  a PR, (3) User requests code review, (4) Debugging API behavior, (5) Checking
  compliance with FastAPI patterns, (6) Optimizing API performance.
  Reviews recent changes by default, or specific files if requested.
---

# FastAPI Code Review Skill

Automated code review for FastAPI backend implementations with refactoring suggestions.

## What This Skill Does

1. **Analyzes recent changes** - Reviews git diff or specified files
2. **Checks FastAPI patterns** - Validates dependency injection, schemas, error handling, async/await
3. **References best practices** - Compares against FastAPI and Pydantic patterns
4. **Suggests refactorings** - Provides specific code improvements
5. **Validates tests** - Ensures TDD compliance and test coverage

---

## Review Workflow

### 1. Identify Scope

By default, review recent uncommitted changes:
```bash
git diff HEAD
git status --short
```

If user specifies files, review those instead:
```bash
# User: "Review app/main.py"
# → Read that file specifically
```

### 2. Run Checklist

Check each file against the [FastAPI Best Practices Checklist](references/checklist.md).

### 3. Reference Documentation

For each issue found, reference:
- Official FastAPI docs
- Project CLAUDE.md conventions
- References in `.claude/skills/references/`

### 4. Provide Specific Fixes

Don't just say "fix this" - provide actual code examples:

**Bad:**
```
❌ The endpoint should use dependency injection
```

**Good:**
```
❌ Endpoint doesn't use dependency injection

Current code (app/main.py:15):
    from src.graph import graph  # Direct import!
    result = graph.invoke(...)

Refactor to:
    from app.dependencies import get_graph

    @app.post("/api/messages")
    async def create_message(
        request: MessageRequest,
        agent = Depends(get_graph)  # Dependency injection
    ):
        result = agent.invoke(...)
```

### 5. Suggest Refactorings

Look for opportunities to improve code quality:
- Better error handling
- Proper async/await usage
- Type hints and validation
- Test coverage gaps

---

## FastAPI Best Practices Checklist

### Application Structure

- [ ] **FastAPI app properly configured** with title, version, description
- [ ] **CORS middleware configured** for frontend origins
- [ ] **Dependency injection used** for agent access (not direct imports)
- [ ] **Routes organized** with clear path prefixes (/api/*)
- [ ] **Response models defined** for all endpoints

### Pydantic Schemas

- [ ] **Request schemas have validation** (Field constraints, validators)
- [ ] **Response schemas match return types** (response_model parameter)
- [ ] **Optional fields use None default** (field: str | None = None)
- [ ] **Examples provided** in model_config for documentation
- [ ] **Type hints are precise** (not just str, dict, etc.)

### Dependency Injection

- [ ] **Dependencies defined in dependencies.py** (not in routes)
- [ ] **Dependencies raise HTTPException on errors**
- [ ] **Routes use Depends()** to inject dependencies
- [ ] **Dependencies are testable** (can be overridden)
- [ ] **No circular imports** between dependencies and routes

### Error Handling

- [ ] **Validation errors return 422** (automatic via Pydantic)
- [ ] **Application errors return 500** with HTTPException
- [ ] **Error responses have meaningful messages**
- [ ] **Sensitive info not exposed** in error messages
- [ ] **Logging added for errors**

### Async/Await

- [ ] **Endpoints defined with async def** (not def)
- [ ] **Blocking operations use await** or run_in_executor
- [ ] **No blocking calls** in async routes (no requests.get, time.sleep)
- [ ] **Dependencies are async-compatible**

### Testing

- [ ] **Each endpoint has unit test** in tests/test_main.py
- [ ] **TestClient used** for testing routes
- [ ] **Dependencies overridden** in tests (app.dependency_overrides)
- [ ] **Validation tests** for invalid input
- [ ] **Integration tests marked** with @pytest.mark.integration
- [ ] **Mocked agent** for unit tests (no real API calls)

### Lambda/Mangum

- [ ] **Handler uses Mangum** adapter
- [ ] **Handler tests** with API Gateway events
- [ ] **No startup/shutdown** events (not supported in Lambda)

---

## Common Anti-Patterns to Catch

### ❌ Direct Imports Instead of Dependency Injection

```python
# WRONG - Direct import
from src.graph import graph

@app.post("/api/messages")
async def create_message(request: MessageRequest):
    result = graph.invoke(...)  # Hard to mock in tests!
```

**Fix:**
```python
# CORRECT - Dependency injection
from app.dependencies import get_graph

@app.post("/api/messages")
async def create_message(
    request: MessageRequest,
    agent = Depends(get_graph)  # Easy to override in tests
):
    result = agent.invoke(...)
```

---

### ❌ Missing Validation on Request Models

```python
# WRONG - No validation
class MessageRequest(BaseModel):
    question: str  # Empty strings allowed!
```

**Fix:**
```python
# CORRECT - With validation
from pydantic import Field, field_validator

class MessageRequest(BaseModel):
    question: str = Field(..., min_length=1)

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()
```

---

### ❌ Not Using Response Models

```python
# WRONG - No response model
@app.post("/api/messages")
async def create_message(request: MessageRequest):
    result = agent.invoke(...)
    return result  # Unvalidated dict!
```

**Fix:**
```python
# CORRECT - With response model
@app.post("/api/messages", response_model=MessageResponse)
async def create_message(request: MessageRequest):
    result = agent.invoke(...)
    return MessageResponse(**result)  # Validated!
```

---

### ❌ Poor Error Handling

```python
# WRONG - No error handling
@app.post("/api/messages")
async def create_message(request: MessageRequest, agent = Depends(get_graph)):
    result = agent.invoke({"question": request.question})  # What if this fails?
    return MessageResponse(**result)
```

**Fix:**
```python
# CORRECT - Graceful error handling
import logging

logger = logging.getLogger(__name__)

@app.post("/api/messages")
async def create_message(request: MessageRequest, agent = Depends(get_graph)):
    try:
        result = agent.invoke({"question": request.question})
        return MessageResponse(**result)
    except KeyError as e:
        logger.error(f"Invalid agent response: {e}")
        raise HTTPException(
            status_code=500,
            detail="Agent returned incomplete response"
        )
    except Exception as e:
        logger.error(f"Agent invocation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process request"
        )
```

---

### ❌ Sync Functions in Async Routes

```python
# WRONG - Mixing sync/async
@app.post("/api/messages")
async def create_message(request: MessageRequest):
    result = some_blocking_function()  # Blocks event loop!
    return result
```

**Fix:**
```python
# CORRECT - Proper async usage
@app.post("/api/messages")
async def create_message(request: MessageRequest):
    # Option 1: Make it async
    result = await some_async_function()

    # Option 2: Run blocking code in executor
    from asyncio import get_event_loop
    loop = get_event_loop()
    result = await loop.run_in_executor(None, some_blocking_function)

    return result
```

---

### ❌ Missing CORS Configuration

```python
# WRONG - No CORS (frontend requests will fail)
app = FastAPI()

@app.post("/api/messages")
async def create_message(...):
    ...
```

**Fix:**
```python
# CORRECT - CORS configured
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### ❌ Integration Tests Without Markers

```python
# WRONG - No marker, makes real API calls in unit tests
def test_with_real_agent():
    client = TestClient(app)  # Uses real agent!
    response = client.post("/api/messages", ...)
```

**Fix:**
```python
# CORRECT - Marked as integration test
import pytest

@pytest.mark.integration
def test_with_real_agent(integration_client):
    response = integration_client.post("/api/messages", ...)
```

---

## Review Output Format

Structure your review as:

### ✅ Good Practices Found

- List what the code does well
- Reference specific patterns from docs

### ❌ Issues Found

For each issue:
1. **Location**: file:line_number
2. **Problem**: What's wrong and why
3. **Impact**: How this affects functionality/maintainability
4. **Fix**: Specific code to replace it

### 🔧 Refactoring Opportunities

- Suggest improvements even if code works
- Focus on maintainability and type safety
- Provide before/after examples

### 📚 References

- Link to relevant FastAPI docs
- Reference project conventions from CLAUDE.md
- Cite specific patterns from skill references

---

## Example Review

```markdown
# Code Review: app/main.py

## ✅ Good Practices Found

- **Response models**: All endpoints use response_model parameter ✓
- **CORS configured**: Middleware properly set up ✓
- **Async endpoints**: All routes use async def ✓

## ❌ Issues Found

### 1. Missing Error Handling
**Location**: app/main.py:25
**Problem**: Agent invocation not wrapped in try/except
**Impact**: Unhandled exceptions will return 500 without meaningful message
**Fix**:
\`\`\`python
@app.post("/api/messages")
async def create_message(request: MessageRequest, agent = Depends(get_graph)):
    try:
        result = agent.invoke({"question": request.question})
        return MessageResponse(**result)
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process request")
\`\`\`

### 2. No Request Validation
**Location**: app/schemas.py:5
**Problem**: MessageRequest allows empty strings
**Impact**: Empty questions will be sent to agent, wasting tokens
**Fix**:
\`\`\`python
from pydantic import Field

class MessageRequest(BaseModel):
    question: str = Field(..., min_length=1)  # Add constraint
\`\`\`

## 🔧 Refactoring Opportunities

### Add Logging
Consider adding logging for request/response tracking:
\`\`\`python
import logging
logger = logging.getLogger(__name__)

@app.post("/api/messages")
async def create_message(...):
    logger.info(f"Processing question: {request.question[:50]}")
    # ... rest of code
\`\`\`

## 📚 References

- FastAPI dependency injection: https://fastapi.tiangolo.com/tutorial/dependencies/
- Error handling: .claude/skills/references/api-patterns.md#error-handling
- Testing: .claude/skills/references/testing-patterns.md
```

---

## Companion Skill

For general Python/OOP review (SOLID principles, Pythonic idioms), also invoke the **`review-python`** skill at the monorepo root.

## When NOT to Review

Don't run this skill for:
- Trivial changes (typos, comments)
- Changes outside api/ directory
- Non-code files (docs, configs)
- Changes that are already tested and passing CI/CD

---

## Process

1. **Determine scope**: Recent changes or specified files
2. **Read relevant files**: Use Read tool for each file in scope
3. **Check against patterns**: Review using checklist above
4. **Generate review**: Structured output with specific fixes
5. **Offer to apply fixes**: Ask if user wants Claude to refactor

---

## Quick Commands

After running the skill, offer:

```
Would you like me to:
1. Apply the suggested refactorings
2. Add missing tests
3. Review a different file/scope
4. Run tests to verify changes
```
