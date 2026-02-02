# Agent Service - Development Tasks

> **Note**: This file tracks development progress and is kept in version control
> as a reference for project workflow. It is NOT part of the production agent code.
> Each service in the monorepo has its own TASKS.md for independent tracking.

## Overview

Building a LangGraph 1.x agent with topic classification and specialist routing for trip Q&A.

**Graph Flow**: `START → classifier → router → [specialist] → END`

---

## Phase 1: State Schema

Define the agent's state structure using TypedDict.

- [ ] Create `src/state.py` with TripAssistantState TypedDict
  - [ ] Define TopicCategory Literal type with all 7 categories
  - [ ] Define TripAssistantState with all required fields:
    - `question: str`
    - `category: TopicCategory`
    - `confidence: float`
    - `documents: dict[str, str]`
    - `current_context: str`
    - `answer: str`
    - `source: str | None`
- [ ] Create `tests/test_state.py`
  - [ ] Test TripAssistantState can be instantiated
  - [ ] Test TopicCategory only accepts valid values
- [ ] Run `pytest tests/test_state.py -v` (must pass)
- [ ] Run `pre-commit run --all-files` (must pass)

**Topic Categories**: flight | car_rental | routes | aosta | chamonix | annecy_geneva | general

---

## Phase 2: Document Loader

Load trip data files from the `data/` directory.

- [ ] Create `src/documents.py`
  - [ ] Implement `load_documents(data_dir: Path | None = None) -> dict[str, str]`
  - [ ] Load all 6 .txt files from data directory
  - [ ] Return dict mapping filename (without .txt) to content
    - Example: `{"flight": "...", "car_rental": "...", ...}`
- [ ] Create `tests/test_documents.py`
  - [ ] Test loads all 6 txt files
  - [ ] Test returns dict with correct keys
  - [ ] Test handles missing directory gracefully
- [ ] Run `pytest tests/test_documents.py -v` (must pass)
- [ ] Run `pre-commit run --all-files` (must pass)

**Data Files**:
- `flight.txt` - El Al LY345, times
- `car_rental.txt` - Sixt pickup, location
- `routes_to_aosta.txt` - 3 driving route options
- `aosta_valley.txt` - July 8-11 itinerary
- `chamonix.txt` - July 12-16 itinerary
- `annecy_geneva.txt` - July 16-20 itinerary

---

## Phase 3: Classifier Node

Classify user questions by topic using LLM with structured output.

- [ ] Create `src/nodes/` directory
- [ ] Create `src/nodes/classifier.py`
  - [ ] Define TopicClassification Pydantic model
    - `category: TopicCategory`
    - `confidence: float` (0.0 - 1.0)
  - [ ] Implement `classify_question(state: TripAssistantState) -> dict`
    - [ ] Use LLM with structured output to classify question
    - [ ] Set category and confidence in returned state
    - [ ] Set current_context to relevant document content
- [ ] Create `tests/nodes/test_classifier.py`
  - [ ] Test classifies flight questions correctly
  - [ ] Test classifies car rental questions correctly
  - [ ] Test returns confidence score
  - [ ] Test sets current_context from documents
- [ ] Run `pytest tests/nodes/test_classifier.py -v` (must pass)
- [ ] Run `pre-commit run --all-files` (must pass)

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

## Phase 4: Specialist Nodes

Create specialist nodes that answer questions using document context.

- [ ] Create specialist node files in `src/nodes/`:
  - [ ] `flight.py` - Implement `handle_flight(state: TripAssistantState) -> dict`
  - [ ] `car_rental.py` - Implement `handle_car_rental(state: TripAssistantState) -> dict`
  - [ ] `routes.py` - Implement `handle_routes(state: TripAssistantState) -> dict`
  - [ ] `aosta.py` - Implement `handle_aosta(state: TripAssistantState) -> dict`
  - [ ] `chamonix.py` - Implement `handle_chamonix(state: TripAssistantState) -> dict`
  - [ ] `annecy_geneva.py` - Implement `handle_annecy_geneva(state: TripAssistantState) -> dict`
  - [ ] `general.py` - Implement `handle_general(state: TripAssistantState) -> dict`
    - Uses all documents as context OR asks for clarification

**Common Pattern for Each Specialist**:
```python
def handle_<topic>(state: TripAssistantState) -> dict:
    """Answer question using current_context.

    Returns:
        {"answer": str, "source": "<topic>.txt"}
    """
    context = state["current_context"]
    question = state["question"]

    # Use LLM to generate answer from context
    # Return answer and source
```

- [ ] Create test files in `tests/nodes/`:
  - [ ] `test_flight.py`
  - [ ] `test_car_rental.py`
  - [ ] `test_routes.py`
  - [ ] `test_aosta.py`
  - [ ] `test_chamonix.py`
  - [ ] `test_annecy_geneva.py`
  - [ ] `test_general.py`

**Test Coverage for Each Specialist**:
- Test generates answer from context
- Test returns correct source
- Test handles missing context gracefully

- [ ] Run `pytest tests/nodes/ -v` (all must pass)
- [ ] Run `pre-commit run --all-files` (must pass)

---

## Phase 5: Graph Assembly

Wire all nodes together using LangGraph StateGraph.

- [ ] Create `src/graph.py`
  - [ ] Import all specialist handlers
  - [ ] Implement `route_by_category(state: TripAssistantState) -> str`
    - Returns node name based on state["category"]
  - [ ] Implement `create_graph()`:
    - [ ] Create StateGraph(TripAssistantState)
    - [ ] Add classifier node
    - [ ] Add all 7 specialist nodes
    - [ ] Add edge: START → classifier
    - [ ] Add conditional edges: classifier → route_by_category
    - [ ] Add edges: each specialist → END
    - [ ] Compile and return graph
  - [ ] Export compiled graph instance

**Graph Structure**:
```
START → classifier → router → [flight|car_rental|routes|aosta|chamonix|annecy_geneva|general] → END
```

- [ ] Create `tests/test_graph.py`
  - [ ] Test flight question routes to flight node
  - [ ] Test car question routes to car_rental node
  - [ ] Test end-to-end returns answer with source
  - [ ] Test unknown question routes to general
- [ ] Run `pytest tests/test_graph.py -v` (must pass)
- [ ] Manual test: `python -c "from src.graph import graph; print(graph.invoke({'question': 'What time is our flight?'}))"`
- [ ] Run `pytest tests/ -v` (all tests must pass)
- [ ] Run `pre-commit run --all-files` (must pass)

---

## Completion Criteria

- [ ] All phases completed
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] All quality checks passing (`pre-commit run --all-files`)
- [ ] Graph can be imported and invoked successfully
- [ ] Ready for API integration
