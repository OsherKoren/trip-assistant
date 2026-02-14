---
name: review-langgraph
description: |
  Review LangGraph agent code for best practices and suggest refactorings.
  Use when: (1) After implementing new nodes or graph changes, (2) Before creating
  a PR, (3) User requests code review, (4) Debugging graph behavior, (5) Checking
  compliance with LangGraph 1.x patterns, (6) Optimizing graph performance.
  Reviews recent changes by default, or specific files if requested.
---

# LangGraph Code Review Skill

Automated code review for LangGraph 1.x agent implementations with refactoring suggestions.

## What This Skill Does

1. **Analyzes recent changes** - Reviews git diff or specified files
2. **Checks LangGraph patterns** - Validates StateGraph, node signatures, state immutability
3. **References official docs** - Compares against LangGraph 1.x best practices
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
# User: "Review src/nodes/classifier.py"
# → Read that file specifically
```

### 2. Run Checklist

Check each file against the [LangGraph Best Practices Checklist](references/checklist.md).

### 3. Reference Documentation

For each issue found, reference:
- Official LangGraph docs (use WebFetch if needed)
- Project CLAUDE.md conventions
- References in `.claude/skills/references/`

### 4. Provide Specific Fixes

Don't just say "fix this" - provide actual code examples:

**Bad:**
```
❌ The node should not mutate state
```

**Good:**
```
❌ Node mutates state in place

Current code (src/nodes/classifier.py:15):
    state["topic"] = "flights"  # Mutates state!
    return state

Refactor to:
    return {"topic": "flights"}  # Returns new dict
```

### 5. Suggest Refactorings

Look for opportunities to improve code quality:
- Extract repeated patterns
- Use structured outputs instead of string parsing
- Simplify complex conditionals
- Improve type safety

---

## LangGraph 1.x Best Practices Checklist

### State Management

- [ ] **StateGraph imported from langgraph.graph** (not MessageGraph)
- [ ] **State is TypedDict** with all fields typed
- [ ] **Nodes return new dicts** (no in-place mutations)
- [ ] **messages field uses add_messages reducer** from langgraph.graph.message
- [ ] **Literal types for routing** (e.g., `topic: Literal["flights", "hotels"] | None`)

### Graph Structure

- [ ] **Nodes added with graph.add_node()** before edges
- [ ] **START and END imported** from langgraph.graph
- [ ] **Edges connect START → first node** and last nodes → END
- [ ] **Conditional edges have routing function** that returns node names
- [ ] **Routing function typed with state parameter**
- [ ] **app = graph.compile()** at end

### Node Functions

- [ ] **All nodes typed with state parameter** (e.g., `state: TripAssistantState`)
- [ ] **Nodes return dict[str, Any]** matching state fields
- [ ] **Error handling wraps LLM calls** with try/except
- [ ] **System prompts defined as module constants**
- [ ] **LLM model specified explicitly** (not default)

### Modern Patterns

- [ ] **Use with_structured_output()** instead of parsing strings
- [ ] **Pydantic models for structured output** with proper types
- [ ] **ChatOpenAI from langchain_openai** (not legacy imports)
- [ ] **No deprecated LangChain patterns** (chains, agents, etc.)

### Testing

- [ ] **Each node has unit test** in tests/test_<node>.py
- [ ] **Graph has integration test** in tests/integration/
- [ ] **Tests use markers** (@pytest.mark.integration for API tests)
- [ ] **Mocked LLM responses** for unit tests (no API calls)
- [ ] **Type hints in test functions**

---

## Common Anti-Patterns to Catch

### ❌ Using MessageGraph (Legacy)

```python
# WRONG - Legacy pattern
from langgraph.graph import MessageGraph
graph = MessageGraph()
```

**Fix:**
```python
# CORRECT - LangGraph 1.x
from langgraph.graph import StateGraph
from src.state import TripAssistantState

graph = StateGraph(TripAssistantState)
```

---

### ❌ Mutating State In Place

```python
# WRONG - Mutates state
def classify_node(state: TripAssistantState) -> TripAssistantState:
    state["topic"] = "flights"  # Mutation!
    return state
```

**Fix:**
```python
# CORRECT - Returns new dict
def classify_node(state: TripAssistantState) -> dict:
    return {"topic": "flights"}
```

---

### ❌ String Parsing Instead of Structured Output

```python
# WRONG - Brittle string parsing
response = llm.invoke(messages)
topic = response.content.strip().lower()
```

**Fix:**
```python
# CORRECT - Structured output with Pydantic
from pydantic import BaseModel
from typing import Literal

class Classification(BaseModel):
    topic: Literal["flights", "hotels", "activities"]

structured_llm = llm.with_structured_output(Classification)
response = structured_llm.invoke(messages)
topic = response.topic  # Type-safe!
```

---

### ❌ Untyped Routing Functions

```python
# WRONG - No types
def route_by_topic(state):
    return state["topic"]
```

**Fix:**
```python
# CORRECT - Fully typed
def route_by_topic(state: TripAssistantState) -> str:
    """Route to specialist node based on classified topic."""
    return state["topic"]
```

---

### ❌ Missing Error Handling

```python
# WRONG - No error handling
def handle_flights(state: TripAssistantState) -> dict:
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke(messages)  # What if this fails?
    return {"messages": [response]}
```

**Fix:**
```python
# CORRECT - Graceful failure
from langchain_core.messages import AIMessage

def handle_flights(state: TripAssistantState) -> dict:
    try:
        llm = ChatOpenAI(model="gpt-4o")
        response = llm.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        logger.error(f"Flight specialist failed: {e}")
        error_msg = AIMessage(
            content="Sorry, I couldn't retrieve flight information. Please try again."
        )
        return {"messages": [error_msg]}
```

---

### ❌ Integration Tests Without Markers

```python
# WRONG - No marker, runs in unit test suite
def test_graph_with_real_api():
    result = app.invoke({"messages": [...]})  # Real API call!
```

**Fix:**
```python
# CORRECT - Marked as integration test
import pytest

@pytest.mark.integration
def test_graph_with_real_api():
    result = app.invoke({"messages": [...]})
```

---

## Refactoring Suggestions

### Extract Repeated Patterns

If you see multiple specialist nodes with similar structure:

```python
# Before: Repeated pattern in each specialist
def handle_flights(state):
    llm = ChatOpenAI(model="gpt-4o")
    docs = load_docs_for_topic("flights")
    context = "\n\n".join(docs)
    # ... repeated in every specialist

def handle_hotels(state):
    llm = ChatOpenAI(model="gpt-4o")
    docs = load_docs_for_topic("hotels")
    context = "\n\n".join(docs)
    # ... same pattern
```

**Suggest:**
```python
# After: Extracted helper
def create_specialist_node(topic: str, prompt_template: str):
    """Factory function for specialist nodes."""
    def specialist_node(state: TripAssistantState) -> dict:
        llm = ChatOpenAI(model="gpt-4o")
        docs = load_docs_for_topic(topic)
        context = "\n\n".join(docs)

        messages = [
            SystemMessage(content=prompt_template.format(context=context)),
            *state["messages"]
        ]

        response = llm.invoke(messages)
        return {"messages": [response]}

    return specialist_node

# Usage
handle_flights = create_specialist_node("flights", FLIGHTS_PROMPT)
handle_hotels = create_specialist_node("hotels", HOTELS_PROMPT)
```

---

### Improve Type Safety

```python
# Before: Loose typing
def route_by_topic(state: TripAssistantState) -> str:
    return state["topic"]  # Could be None!
```

**Suggest:**
```python
# After: Explicit handling
def route_by_topic(state: TripAssistantState) -> str:
    topic = state.get("topic")
    if topic is None:
        return "general"  # Fallback
    return topic
```

---

### Simplify Complex Conditionals

```python
# Before: Long if/elif chain
def route_by_topic(state: TripAssistantState) -> str:
    if state["topic"] == "flights":
        return "flights_specialist"
    elif state["topic"] == "hotels":
        return "hotels_specialist"
    elif state["topic"] == "activities":
        return "activities_specialist"
    # ... 10 more cases
```

**Suggest:**
```python
# After: Mapping approach
TOPIC_TO_NODE = {
    "flights": "flights_specialist",
    "hotels": "hotels_specialist",
    "activities": "activities_specialist",
    # ... etc
}

def route_by_topic(state: TripAssistantState) -> str:
    return TOPIC_TO_NODE.get(state["topic"], "general_specialist")
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

- Link to relevant LangGraph docs
- Reference project conventions from CLAUDE.md
- Cite specific patterns from skill references

---

## Example Review

```markdown
# Code Review: src/nodes/classifier.py

## ✅ Good Practices Found

- **Structured output**: Uses Pydantic + with_structured_output() ✓
- **Type hints**: Node function properly typed with TripAssistantState ✓
- **Constants**: Prompt defined as module constant ✓

## ❌ Issues Found

### 1. Missing Error Handling
**Location**: src/nodes/classifier.py:25
**Problem**: LLM call not wrapped in try/except
**Impact**: Unhandled exceptions will crash the graph
**Fix**:
\`\`\`python
def classify_query(state: TripAssistantState) -> dict:
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        # ... rest of code
        return {"topic": response.topic}
    except Exception as e:
        logger.error(f"Classifier failed: {e}")
        return {"topic": "general"}  # Fallback
\`\`\`

### 2. Integration Test Missing Marker
**Location**: tests/test_classifier.py:15
**Problem**: Test makes real API calls but has no @pytest.mark.integration
**Impact**: Expensive API calls run on every test, slow CI/CD
**Fix**:
\`\`\`python
import pytest

@pytest.mark.integration  # Add this marker
def test_classifier_with_real_api():
    # ... test code
\`\`\`

## 🔧 Refactoring Opportunities

### Improve Confidence Handling
Currently confidence score is calculated but not used. Consider:
- Adding confidence threshold for fallback to general specialist
- Logging low-confidence classifications for monitoring

## 📚 References

- LangGraph StateGraph: https://langchain-ai.github.io/langgraph/concepts/low_level/
- Error handling pattern: .claude/skills/references/node-patterns.md#error-handling
- Test markers: .claude/skills/references/testing-patterns.md#integration-tests
```

---

## Companion Skill

For general Python/OOP review (SOLID principles, Pythonic idioms), also invoke the **`review-python`** skill at the monorepo root.

## When NOT to Review

Don't run this skill for:
- Trivial changes (typos, comments)
- Changes outside agent/ directory
- Non-code files (docs, configs)
- Changes that are already tested and passing CI/CD

---

## Process

1. **Determine scope**: Recent changes or specified files
2. **Read relevant files**: Use Read tool for each file in scope
3. **Check against patterns**: Review using checklist above
4. **Fetch LangGraph docs if needed**: Use WebFetch for official docs
5. **Generate review**: Structured output with specific fixes
6. **Offer to apply fixes**: Ask if user wants Claude to refactor

---

## Quick Commands

After running the skill, offer:

```
Would you like me to:
1. Apply the suggested refactorings
2. Add missing tests
3. Fetch specific LangGraph documentation
4. Review a different file/scope
```
