---
name: trip-api
description: |
  Build and modify the Trip Assistant FastAPI backend that exposes the agent via HTTP.
  Use when: (1) Adding or modifying API endpoints, (2) Working with Pydantic schemas,
  (3) Implementing dependency injection, (4) Testing API routes, (5) Configuring CORS
  or middleware, (6) Working with Lambda/Mangum handler, (7) Any task involving the api/ folder.
---

# Trip Assistant API Development

This is a shortcut skill that loads the full trip-api skill.

For complete documentation, see:
- [trip-api/SKILL.md](trip-api/SKILL.md) - FastAPI development patterns
- [review-fastapi/SKILL.md](review-fastapi/SKILL.md) - Code review for FastAPI

## Quick Reference

### Architecture
```
API Gateway → Lambda → FastAPI (Mangum) → Agent
```

### Key Files
- `app/main.py` - FastAPI app and routes
- `app/schemas.py` - Pydantic request/response models
- `app/dependencies.py` - Dependency injection (agent)
- `app/handler.py` - Lambda handler (Mangum adapter)

### Development
```bash
# Run locally
fastapi dev app/main.py

# Run tests
pytest tests/ -v

# Run integration tests (requires OPENAI_API_KEY)
pytest tests/ -v -m integration
```

### Common Tasks
- **Add endpoint**: Define schema → Add route → Write tests
- **Test endpoint**: Use TestClient with mocked dependencies
- **Review code**: Use `/review-fastapi` skill
- **Fix failing tests**: Check dependency overrides in conftest.py
