# Logging Practices — Quick Reference

> Log at the point of failure, use structured key-value pairs, and choose levels deliberately.

## Log Before Raising

### Checklist
- [ ] Every `raise` in application code is preceded by a `logger.error()` or `logger.warning()`
- [ ] Log includes context: what failed, relevant identifiers, input that caused the failure
- [ ] Exception is NOT logged if the caller is expected to log it (avoid double-logging)
- [ ] `logger.exception()` used in `except` blocks to capture the traceback automatically

### Examples

```python
# Bad — raises without logging (caller may swallow or re-raise, losing context)
def build_graph(agent_mode: str, function_name: str) -> Graph:
    if agent_mode == "lambda" and not function_name:
        raise RuntimeError("AGENT_LAMBDA_FUNCTION_NAME must be set")

# Good — log then raise
def build_graph(agent_mode: str, function_name: str) -> Graph:
    if agent_mode == "lambda" and not function_name:
        logger.error("Missing function name for Lambda mode", agent_mode=agent_mode)
        raise RuntimeError("AGENT_LAMBDA_FUNCTION_NAME must be set")
```

```python
# Bad — logs but doesn't include context
except ConnectionError:
    logger.error("Connection failed")
    raise

# Good — includes what was being attempted and the error
except ConnectionError as e:
    logger.error("Failed to connect to agent Lambda", function_name=self.function_name, error=str(e))
    raise HTTPException(status_code=500, detail="Agent unavailable") from e
```

### When NOT to log before raising

- **Validation errors in Pydantic models** — framework handles these
- **Re-raising in middleware** — the original handler already logged
- **Pure utility functions** — let the caller decide (e.g., a `parse_date()` raising `ValueError`)

---

## Structured Logging

### Checklist
- [ ] Uses key-value pairs, not f-strings or `%` formatting in log messages
- [ ] Log message is a static string (searchable), context is in kwargs
- [ ] Sensitive data (API keys, tokens, PII) never logged
- [ ] Preview-only for user input: `question=text[:50]` not full content

### Examples

```python
# Bad — dynamic string, hard to search/filter
logger.info(f"Processing request for user {user_id} with question: {question}")

# Good — static message, structured context
logger.info("Processing request", user_id=user_id, question_preview=question[:50])
```

```python
# Bad — logs secrets
logger.debug(f"Connecting with key={api_key}")

# Good — logs identifiers, not secrets
logger.debug("Connecting to API", endpoint=url, key_prefix=api_key[:8])
```

---

## Log Levels

### Checklist
- [ ] `DEBUG` — detailed diagnostic info (state contents, counts, intermediate values)
- [ ] `INFO` — significant events in normal flow (startup, request received, task completed)
- [ ] `WARNING` — unexpected but recoverable situations (missing optional config, fallback used)
- [ ] `ERROR` — failures that need attention (API call failed, invalid data, raised exceptions)
- [ ] `exception()` — same as ERROR but auto-captures traceback (use only inside `except` blocks)
- [ ] No `print()` statements in production code — always use logger

### Examples

```python
# Good — appropriate levels
logger.info("Starting up", environment=settings.environment, agent_mode=settings.agent_mode)
logger.debug("Loaded documents", count=len(docs), topic=topic)
logger.warning("No documents found for topic", topic=topic)
logger.error("Agent invocation failed", error=str(e), question_preview=question[:50])
```

---

## Entry and Exit Points

### Checklist
- [ ] `INFO` log at entry of significant operations (node invocation, request handling, startup)
- [ ] `INFO` or `DEBUG` log at successful completion with result summary
- [ ] `ERROR` log on failure with context before raising
- [ ] No excessive logging in tight loops or hot paths

### Examples

```python
# Good — entry + exit + error
def handle_flights(state: TripAssistantState) -> dict:
    logger.info("Flights specialist invoked")

    try:
        docs = load_docs_for_topic("flights")
        logger.debug("Loaded documents", count=len(docs))

        response = llm.invoke(messages)
        logger.info("Response generated", preview=response.content[:50])
        return {"messages": [response]}

    except Exception as e:
        logger.error("Flights specialist failed", error=str(e))
        raise
```

---

## Avoid Double-Logging

### Checklist
- [ ] If a function logs and raises, callers should NOT log the same error again
- [ ] If a function logs and returns a fallback, no need to log at the caller
- [ ] In exception chains (`raise ... from e`), log at the point closest to the root cause

### Examples

```python
# Bad — double-logged
def get_data() -> dict:
    try:
        return fetch_from_api()
    except APIError as e:
        logger.error("API fetch failed", error=str(e))  # Logged here
        raise

def process() -> None:
    try:
        data = get_data()
    except APIError as e:
        logger.error("Failed to get data", error=str(e))  # Logged AGAIN
        raise HTTPException(status_code=500, detail="Processing failed") from e

# Good — log once at the boundary
def get_data() -> dict:
    return fetch_from_api()  # Let it propagate

def process() -> None:
    try:
        data = get_data()
    except APIError as e:
        logger.error("Failed to get data from API", error=str(e))
        raise HTTPException(status_code=500, detail="Processing failed") from e
```

---

## Priority Levels

| Priority | What to Flag |
|----------|-------------|
| Critical | `raise` without logging in application code, `print()` in production, secrets in logs |
| Important | f-strings in log messages (not structured), missing context in error logs, double-logging |
| Nice to Have | Log level appropriateness, entry/exit logging, preview-only for user input |
