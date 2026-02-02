# Agent Service - Development Tasks

> **Note**: This file tracks development progress and is kept in version control
> as a reference for project workflow. It is NOT part of the production agent code.
> Each service in the monorepo has its own TASKS.md for independent tracking.

## Overview

Building a LangGraph 1.x agent with topic classification and specialist routing for trip Q&A.

**Graph Flow**: `START → classifier → router → [specialist] → END`

---

## Phase 1: State Schema ✅

Define the agent's state structure using TypedDict.

- [x] Create `src/state.py` with TripAssistantState TypedDict
  - [x] Define TopicCategory Literal type with all 7 categories
  - [x] Define TripAssistantState with all required fields:
    - `question: str`
    - `category: TopicCategory`
    - `confidence: float`
    - `documents: dict[str, str]`
    - `current_context: str`
    - `answer: str`
    - `source: str | None`
- [x] Create `tests/test_state.py`
  - [x] Test TripAssistantState can be instantiated
  - [x] Test TopicCategory only accepts valid values (parametrized)
- [x] Run `pytest tests/test_state.py -v` (must pass)
- [x] Run `pre-commit run --all-files` (must pass)

**Topic Categories**: flight | car_rental | routes | aosta | chamonix | annecy_geneva | general

---

## Phase 2: Document Loader ✅

Load trip data files from the `data/` directory.

- [x] Create `src/documents.py`
  - [x] Implement `load_documents(data_dir: Path | None = None) -> dict[str, str]`
  - [x] Load all 6 .txt files from data directory
  - [x] Return dict mapping filename (without .txt) to content
    - Example: `{"flight": "...", "car_rental": "...", ...}`
- [x] Create `tests/test_documents.py`
  - [x] Test loads all 6 txt files
  - [x] Test returns dict with correct keys (parametrized)
  - [x] Test handles missing directory gracefully
  - [x] Test custom data directory
  - [x] Test empty directory
- [x] Run `pytest tests/test_documents.py -v` (must pass)
- [x] Run `pre-commit run --all-files` (must pass)

**Data Files**:
- `flight.txt` - El Al LY345, times
- `car_rental.txt` - Sixt pickup, location
- `routes_to_aosta.txt` - 3 driving route options
- `aosta_valley.txt` - July 8-11 itinerary
- `chamonix.txt` - July 12-16 itinerary
- `annecy_geneva.txt` - July 16-20 itinerary

---

## Phase 3: Classifier Node ✅

Classify user questions by topic using LLM with structured output.

- [x] Create `src/nodes/` directory
- [x] Create `src/nodes/classifier.py`
  - [x] Define TopicClassification Pydantic model
    - `category: TopicCategory`
    - `confidence: float` (0.0 - 1.0)
  - [x] Implement `classify_question(state: TripAssistantState) -> dict`
    - [x] Use GPT-4o-mini with structured output to classify question
    - [x] Set category and confidence in returned state
    - [x] Set current_context to relevant document content
- [x] Create `tests/nodes/test_classifier.py`
  - [x] Test classifies all 6 category types correctly (parametrized)
  - [x] Test returns confidence score
  - [x] Test sets current_context from documents
  - [x] Test general category handling
- [x] Add pytest-mock to dev dependencies
- [x] Create conftest.py with reusable mock_classifier_llm fixture
- [x] Run `pytest tests/nodes/test_classifier.py -v` (must pass)
- [x] Run `pre-commit run --all-files` (must pass)

**Topic Mapping**:
| Category | Document | Example Questions |
|----------|----------|-------------------|
| flight | flight.txt | "What time is our flight?" |
| car_rental | car_rental.txt | "Where do we pick up the car?" |
| routes | routes_to_aosta.txt | "How do we get to Aosta?" |
| aosta | aosta_valley.txt | "What's planned for July 9?" |
| chamonix | chamonix.txt | "Lac Blanc hike details?" |
| annecy_geneva | annecy_geneva.txt | "Paragliding info?" |
| general | (all docs) | Unclear questions |

---

## Phase 4: Specialist Nodes ✅

Create specialist nodes that answer questions using document context.

- [x] Create specialist node files in `src/nodes/`:
  - [x] `flight.py` - Implement `handle_flight(state: TripAssistantState) -> dict`
  - [x] `car_rental.py` - Implement `handle_car_rental(state: TripAssistantState) -> dict`
  - [x] `routes.py` - Implement `handle_routes(state: TripAssistantState) -> dict`
  - [x] `aosta.py` - Implement `handle_aosta(state: TripAssistantState) -> dict`
  - [x] `chamonix.py` - Implement `handle_chamonix(state: TripAssistantState) -> dict`
  - [x] `annecy_geneva.py` - Implement `handle_annecy_geneva(state: TripAssistantState) -> dict`
  - [x] `general.py` - Implement `handle_general(state: TripAssistantState) -> dict`
    - Uses all documents as context OR asks for clarification

- [x] Create `test_specialists.py` with parametrized tests for all specialists
  - [x] Test generates answer from context (6 specialists parametrized)
  - [x] Test returns correct source (7 specialists parametrized)
  - [x] Test handles empty context gracefully
  - [x] Test general specialist uses all documents

**Test Coverage**:
- All specialists tested with GPT-4o-mini mocked responses
- Parametrized tests for common patterns
- Special test for general node using all documents

- [x] Run `pytest tests/nodes/ -v` (all must pass)
- [x] Run `pre-commit run --all-files` (must pass)

---

## Phase 5: Graph Assembly ✅

Wire all nodes together using LangGraph StateGraph.

- [x] Create `src/graph.py`
  - [x] Import all specialist handlers
  - [x] Implement `route_by_category(state: TripAssistantState) -> str`
    - Returns node name based on state["category"]
  - [x] Implement `create_graph()`:
    - [x] Create StateGraph(TripAssistantState)
    - [x] Add classifier node
    - [x] Add all 7 specialist nodes
    - [x] Add edge: START → classifier
    - [x] Add conditional edges: classifier → route_by_category
    - [x] Add edges: each specialist → END
    - [x] Compile and return graph
  - [x] Export compiled graph instance

**Graph Structure**:
```
START → classifier → router → [flight|car_rental|routes|aosta|chamonix|annecy_geneva|general] → END
```

- [x] Create `tests/test_graph.py`
  - [x] Test flight question routes to flight node (parametrized 4 categories)
  - [x] Test car question routes to car_rental node
  - [x] Test end-to-end returns answer with source
  - [x] Test unknown question routes to general
  - [x] Test documents preserved through flow
- [x] Run `pytest tests/test_graph.py -v` (must pass)
- [x] Run `pytest tests/ -v` (all 50 tests must pass)
- [x] Run `pre-commit run --all-files` (must pass)

---

## Phase 6: Integration Tests ✅

Add real API integration tests with OpenAI GPT-4o-mini.

- [x] Create `.env.example` template file
  - [x] Document OPENAI_API_KEY requirement
  - [x] Add to version control (safe template)
- [x] Ensure `.env` is in `.gitignore` (already done)
- [x] Create `tests/integration/` directory
- [x] Create `tests/integration/__init__.py`
- [x] Create `tests/integration/conftest.py`
  - [x] Add pytest hook to skip if OPENAI_API_KEY not set
  - [x] Add fixture to load real documents
  - [x] Add integration_state fixture
- [x] Create `tests/integration/test_classifier_integration.py`
  - [x] Test real classifier with actual OpenAI API (8 tests)
  - [x] Test multiple question types (6 categories parametrized)
  - [x] Verify confidence scores are reasonable
  - [x] Mark with `@pytest.mark.integration`
- [x] Create `tests/integration/test_graph_integration.py`
  - [x] Test end-to-end graph with real API (7 tests)
  - [x] Test complete flow: question → classification → specialist → answer
  - [x] Verify answer quality and sources
  - [x] Test multiple categories
  - [x] Mark with `@pytest.mark.integration` and `@pytest.mark.slow`
- [x] Update `pyproject.toml`
  - [x] Add pytest markers: `integration`, `unit`, and `slow`
  - [x] Document marker usage in configuration
- [x] Update `CLAUDE.md`
  - [x] Add environment setup section
  - [x] Add integration test commands section
  - [x] Document .env setup instructions
  - [x] Add cost warnings (~$0.01-0.10 per run)
- [x] Verify tests skip gracefully without API key (15 skipped)
- [x] Verify unit tests still pass with marker (49 passed)
- [x] All quality checks passing

**Test Organization**:
```
tests/
├── unit/                          # Fast, mocked tests (49 tests)
│   ├── test_state.py
│   ├── test_documents.py
│   └── nodes/
│       ├── test_classifier.py     # Mocked LLM
│       └── test_specialists.py    # Mocked LLM
├── integration/                   # Real API tests (new)
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_classifier_integration.py
│   └── test_graph_integration.py
└── test_graph.py                  # Integration test (mocked)
```

**Pytest Markers**:
- `@pytest.mark.unit` - Fast, mocked tests (default)
- `@pytest.mark.integration` - Real API tests (requires OPENAI_API_KEY)

**Running Tests**:
```bash
# All tests (unit + integration)
pytest tests/ -v

# Unit tests only (fast, no API key needed)
pytest tests/ -v -m "not integration"

# Integration tests only (requires API key)
pytest tests/ -v -m integration

# Specific integration test
pytest tests/integration/test_graph_integration.py -v
```

---

## Completion Criteria

- [x] Phase 1-5 completed (Core agent functionality)
- [x] Phase 6 completed (Integration tests)
- [x] All unit tests passing (49 tests, mocked)
- [x] Integration test framework ready (15 tests, skip without API key)
- [x] All quality checks passing (ruff, mypy, pytest)
- [x] Graph can be imported and invoked successfully
- [ ] Integration tests validated with real API (requires OPENAI_API_KEY)
- [ ] Ready for CI/CD pipeline setup (Phase 7)
- [ ] Ready for AWS deployment (Phase 8 in infra/)
