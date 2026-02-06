# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Specialist factory pattern for creating specialist nodes with consistent behavior
- Comprehensive error handling tests covering all node failure scenarios (12 tests)
- Graceful degradation for LLM API failures across all nodes
- Fallback routing to general specialist when classifier fails or category is missing
- Root test fixtures in `tests/conftest.py` for shared test data
- Error logging with context for debugging classifier and specialist failures
- README.md with quick start guide, architecture overview, and usage examples

### Changed
- Refactored 6 specialist nodes (flight, car_rental, routes, aosta, chamonix, annecy_geneva) into single factory pattern
- Reduced specialist code by 57% (240 lines → 120 lines) while maintaining functionality
- Improved routing function with None-safety and fallback behavior
- Updated test mocking to work with factory-generated specialists
- Consolidated duplicate node implementations into `specialist_factory.create_specialist()`

### Fixed
- Missing error handling in classifier node - now falls back to general category on API failure
- Missing error handling in all specialist nodes - now return user-friendly error messages
- Missing error handling in general specialist - now handles API failures gracefully
- Routing crashes when category is None or missing - now routes to general specialist
- Unhandled LLM exceptions that could crash the graph during API failures

### Security
- Added proper error handling to prevent exception information leakage to end users
- Error messages now user-friendly without exposing internal implementation details

## [0.1.0] - 2026-02-06

### Added
- Initial release of Trip Assistant Agent
- LangGraph 1.x StateGraph implementation with topic-based routing
- Classifier node using GPT-4o-mini for question categorization
- Six specialist nodes for different trip topics:
  - Flight specialist for flight-related queries
  - Car rental specialist for vehicle pickup/return information
  - Routes specialist for driving directions to destinations
  - Aosta Valley specialist for July 8-11 itinerary
  - Chamonix specialist for July 12-16 itinerary
  - Annecy/Geneva specialist for July 16-20 itinerary
- General specialist for unclear or broad questions
- Document loading system for trip information from text files
- Structured output using Pydantic models for type safety
- Comprehensive test suite:
  - 49 unit tests with mocked LLM responses
  - 15 integration tests with real OpenAI API calls
  - Pytest configuration with integration test markers
- Type hints throughout codebase with mypy validation
- Pre-commit hooks for code quality (ruff, mypy, pytest)
- Environment variable configuration via .env file
- Logging infrastructure using loguru
- Development documentation in CLAUDE.md
- Docker support for containerized deployment

### Technical Details
- **Python**: 3.11+ required
- **Framework**: LangGraph >= 1.0
- **LLM**: OpenAI GPT-4o-mini for classification and answer generation
- **Type Safety**: Full Pydantic and TypedDict annotations
- **Testing**: pytest with asyncio support
- **Code Quality**: ruff linter, mypy type checker, pre-commit hooks

### Architecture
- **Pattern**: Classifier → Router → Specialist → Response
- **State Management**: Immutable state updates using TypedDict
- **Error Handling**: Try/except blocks in critical paths
- **Document Context**: Relevant documents loaded per specialist

### Performance
- Classification: ~1-2 seconds (gpt-4o-mini)
- Answer generation: ~2-4 seconds (gpt-4o-mini)
- Cost per query: ~$0.001-0.003 using gpt-4o-mini

[unreleased]: https://github.com/yourusername/trip-assistant/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/trip-assistant/releases/tag/v0.1.0
