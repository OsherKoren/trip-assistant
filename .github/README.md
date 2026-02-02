# CI/CD Pipeline Documentation

## GitHub Actions Workflows

### Agent Service CI/CD (`agent-ci.yml`)

Automated testing and deployment pipeline for the agent service.

**Triggers:**
- Push to `main`, `develop`, or `feature/agent` branches (only if `agent/` files changed)
- Pull requests affecting `agent/` files

**Jobs:**

1. **Unit Tests** (Always runs)
   - Fast, mocked tests
   - No API key required
   - Runs on all branches and PRs
   - Uploads coverage to Codecov

2. **Integration Tests** (Main branch only)
   - Real OpenAI API calls
   - Requires `OPENAI_API_KEY` secret
   - Only runs on `main` branch to save costs
   - ~$0.01-0.10 per run

3. **Code Quality** (Always runs)
   - Ruff linter and formatter
   - MyPy type checker
   - Runs in parallel with unit tests

4. **Docker Build** (Main branch only)
   - Builds Docker image for agent
   - Tests image can import graph
   - Caches layers for faster builds
   - Does not push (requires ECR setup)

5. **Push to ECR** (Commented out - requires AWS)
   - Pushes to AWS ECR
   - Tags with git SHA and `latest`
   - Requires AWS credentials

---

## Required GitHub Secrets

Configure these in: **Settings → Secrets and variables → Actions**

### For Integration Tests
- `OPENAI_API_KEY` - Your OpenAI API key
  - Get from: https://platform.openai.com/api-keys
  - Used for: Integration tests in CI

### For AWS Deployment (Optional - Phase 8)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- Used for: Pushing to ECR and deploying to Lambda

---

## How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:
   - Name: `OPENAI_API_KEY`
   - Value: `sk-proj-your-actual-key-here`
5. Save

---

## Pipeline Flow

```
┌─────────────────┐
│   Push/PR       │
└────────┬────────┘
         │
         v
    ┌────────────────────────────┐
    │  Trigger Workflow          │
    │  (if agent/ files changed) │
    └────────┬───────────────────┘
             │
             v
    ┌────────────────────────────────────┐
    │  Run Jobs in Parallel:             │
    │  - Unit Tests                      │
    │  - Code Quality Checks             │
    └────────┬───────────────────────────┘
             │
             v (main branch only)
    ┌────────────────────────────┐
    │  Integration Tests         │
    │  (Real API)                │
    └────────┬───────────────────┘
             │
             v (main branch only)
    ┌────────────────────────────┐
    │  Build Docker Image        │
    └────────┬───────────────────┘
             │
             v (commented - Phase 8)
    ┌────────────────────────────┐
    │  Push to ECR               │
    │  Deploy to Lambda          │
    └────────────────────────────┘
```

---

## Cost Management

**Unit Tests:** Free (mocked, no API calls)

**Integration Tests:**
- Only run on `main` branch
- ~15 tests × $0.001 per test = ~$0.02 per run
- ~$1-2 per month with frequent commits

**Docker Builds:**
- Free on GitHub Actions (2000 minutes/month)
- Uses layer caching for speed

---

## Local Testing

Before pushing, test the Docker build locally:

```bash
# Build image
cd agent
docker build -t trip-assistant-agent:local .

# Test image
docker run --rm trip-assistant-agent:local python -c "from src.graph import graph; print('OK')"

# Run with environment variables
docker run --rm -e OPENAI_API_KEY=your-key trip-assistant-agent:local
```

---

## Troubleshooting

**Unit tests failing:**
- Check Python version (requires 3.11+)
- Check dependencies in `pyproject.toml`
- Run locally: `pytest tests/ -v -m "not integration"`

**Integration tests skipped:**
- Add `OPENAI_API_KEY` to GitHub Secrets
- Check it's running on `main` branch

**Docker build failing:**
- Check `Dockerfile` syntax
- Verify `.dockerignore` excludes unnecessary files
- Test build locally first

**Quality checks failing:**
- Run `pre-commit run --all-files` locally
- Fix ruff/mypy errors before pushing
