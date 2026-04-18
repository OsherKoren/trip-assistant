# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Server-side message storage in DynamoDB with UUID (messages table)
- Feedback links to messages by ID with preview (replaces storing full message content)
- Markdown rendering for assistant messages (react-markdown + Tailwind Typography)
- User feedback system with thumbs up/down and optional comments (DynamoDB + SES email)
- Confidence percentage pill on assistant messages (blue gradient, accessible single-hue design)
- User avatar dropdown menu in header (initials circle, email display, theme toggle, sign out)
- Cognito machine client for authenticated CI/CD smoke tests
- `AGENT_MODE` environment variable to control execution mode (`local` or `lambda`)
- pydantic-settings for validated configuration at startup (`api/app/settings.py`)
- FastAPI lifespan to wire agent graph dependency once at startup
- Python code review skill with testing and logging checklists (`.claude/skills/review-python/`)
- Language guard node rejects non-English (Hebrew) input before classification — zero LLM cost, fixed English-only reply
- Streaming endpoint `POST /api/messages/stream` — Server-Sent Events (SSE) for token-by-token delivery
- `[DONE] <json>` SSE event carries message ID, category, and confidence after the last token
- `[ERROR] <message>` SSE event on agent failure, closes stream cleanly
- Frontend SSE client parses streaming responses and assembles full message progressively
- REST API Gateway (replaces HTTP API) with Cognito JWT authorizer and catch-all `{proxy+}` proxy

### Changed
- Move storage functions to `api/app/db/` package (feedback.py + messages.py)
- Feedback uses `message_id` as DynamoDB partition key (1:1 with messages, no separate feedback UUID)
- Feedback request uses `message_id` instead of `message_content`/`category`/`confidence`
- Assistant messages use server-generated UUID instead of client-generated IDs
- Separate execution mode (`AGENT_MODE`) from environment name (`ENVIRONMENT`)
- Agent graph dependency wired once at startup via lifespan instead of per-request
- API Lambda timeout increased from 30s to 60s to accommodate streaming responses
- Smoke test uses REST API URL and adds `POST /api/messages/stream` stream endpoint check

### Fixed
- Google sign-in race condition on mobile OAuth redirect (wait for Hub event before clearing loading state)
- Cognito domain config for Amplify v6 (build full domain from prefix automatically)
- Message bubbles too narrow on mobile (use 85vw instead of fixed max-width)
- API Lambda using dev mode instead of Lambda proxy when `ENVIRONMENT=dev` was set by Terraform
- CORS preflight for JWT-protected API Gateway (explicit POST route instead of $default catch-all)
- `POST /api/messages/stream` was unreachable in HTTP API (no explicit route) — fixed by REST API catch-all proxy
