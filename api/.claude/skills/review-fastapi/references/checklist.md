# FastAPI Best Practices Checklist

Quick reference for reviewing FastAPI code.

## Application Structure

- [ ] FastAPI app has title, version, description
- [ ] CORS middleware configured with appropriate origins
- [ ] Routes use clear path prefixes (/api/*)
- [ ] No startup/shutdown events (Lambda incompatible)

## Pydantic Schemas

- [ ] Request schemas have Field constraints (min_length, max_length, etc.)
- [ ] Request schemas have field_validators for custom validation
- [ ] Response schemas defined for all endpoints (response_model)
- [ ] Optional fields use `field: str | None = None` pattern
- [ ] model_config includes examples for API docs
- [ ] No bare dict or list types (use typed models)

## Dependency Injection

- [ ] Dependencies defined in separate dependencies.py file
- [ ] Dependencies raise HTTPException on failure (not generic Exception)
- [ ] Routes use Depends() to inject dependencies
- [ ] Dependencies are overridable for testing
- [ ] No circular imports between dependencies and routes
- [ ] No direct imports of external services in routes

## Error Handling

- [ ] Validation errors return 422 (automatic via Pydantic)
- [ ] Application errors return appropriate status codes (400, 500, etc.)
- [ ] HTTPException used for all API errors
- [ ] Error messages are user-friendly (no stack traces)
- [ ] Sensitive information not exposed in errors
- [ ] Errors logged with appropriate level
- [ ] Try/except blocks around agent/external calls

## Async/Await

- [ ] All endpoints use `async def` (not `def`)
- [ ] No blocking calls in async routes
- [ ] Blocking operations use run_in_executor
- [ ] Dependencies are async-compatible
- [ ] No time.sleep() or requests.get() in async code

## Type Hints

- [ ] All function parameters typed
- [ ] Return types specified
- [ ] Pydantic models used instead of plain dicts
- [ ] TypedDict used for complex dict structures
- [ ] Type hints pass mypy checks

## Testing

- [ ] Each endpoint has unit test
- [ ] TestClient used for route testing
- [ ] Dependencies overridden in tests (app.dependency_overrides)
- [ ] Validation tests for invalid input (422 responses)
- [ ] Error handling tests for failures (500 responses)
- [ ] Integration tests marked with @pytest.mark.integration
- [ ] Unit tests mock external dependencies (agent)
- [ ] Tests clean up overrides after completion

## Lambda/Mangum

- [ ] Handler uses Mangum adapter
- [ ] Handler imported from app.main
- [ ] Handler tests use API Gateway v2 event format
- [ ] No long-running processes (Lambda timeout)
- [ ] No local file writes (use /tmp if needed)

## Security

- [ ] No secrets in code (use environment variables)
- [ ] CORS origins restricted (not "*")
- [ ] No eval() or exec()
- [ ] Input validation on all user input
- [ ] No SQL injection risks (if using DB)

## Documentation

- [ ] Docstrings on all public functions
- [ ] Complex logic has inline comments
- [ ] API examples in schema model_config
- [ ] README has endpoint documentation

## Code Quality

- [ ] No commented-out code
- [ ] No print() statements (use logging)
- [ ] No TODO comments without issue links
- [ ] Variables have descriptive names
- [ ] Functions are small and focused
- [ ] No code duplication (DRY principle)

## Common Issues to Flag

### High Priority (Must Fix)

- Direct imports instead of dependency injection
- Missing error handling
- Blocking calls in async routes
- Missing CORS configuration
- Integration tests without markers
- No request validation

### Medium Priority (Should Fix)

- Missing response models
- Unclear error messages
- Missing type hints
- No logging
- Test coverage gaps

### Low Priority (Nice to Have)

- Missing docstrings
- No usage examples
- Could use more validation
- Could improve variable names
