# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Markdown rendering for assistant messages (react-markdown + Tailwind Typography)
- User feedback system with thumbs up/down and optional comments (DynamoDB + SES email)
- Confidence percentage pill on assistant messages (blue gradient, accessible single-hue design)
- User avatar dropdown menu in header (initials circle, email display, theme toggle, sign out)
- Cognito machine client for authenticated CI/CD smoke tests
- `AGENT_MODE` environment variable to control execution mode (`local` or `lambda`)
- pydantic-settings for validated configuration at startup (`api/app/settings.py`)
- FastAPI lifespan to wire agent graph dependency once at startup
- Python code review skill with testing and logging checklists (`.claude/skills/review-python/`)

### Changed
- Separate execution mode (`AGENT_MODE`) from environment name (`ENVIRONMENT`)
- Agent graph dependency wired once at startup via lifespan instead of per-request

### Fixed
- Google sign-in race condition on mobile OAuth redirect (wait for Hub event before clearing loading state)
- Cognito domain config for Amplify v6 (build full domain from prefix automatically)
- Message bubbles too narrow on mobile (use 85vw instead of fixed max-width)
- API Lambda using dev mode instead of Lambda proxy when `ENVIRONMENT=dev` was set by Terraform
- CORS preflight for JWT-protected API Gateway (explicit POST route instead of $default catch-all)
