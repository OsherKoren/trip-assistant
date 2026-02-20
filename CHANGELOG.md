# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `AGENT_MODE` environment variable to control execution mode (`local` or `lambda`)
- pydantic-settings for validated configuration at startup (`api/app/settings.py`)
- FastAPI lifespan to wire agent graph dependency once at startup
- Python code review skill with testing and logging checklists (`.claude/skills/review-python/`)

### Changed
- Separate execution mode (`AGENT_MODE`) from environment name (`ENVIRONMENT`)
- Agent graph dependency wired once at startup via lifespan instead of per-request

### Fixed
- API Lambda using dev mode instead of Lambda proxy when `ENVIRONMENT=dev` was set by Terraform
