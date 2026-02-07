# LangGraph Refactoring Patterns

Common refactorings for improving LangGraph agent code quality.

---

## Pattern 1: Extract Specialist Factory

**When**: Multiple specialist nodes with identical structure

### Before
```python
# src/nodes/flights_specialist.py
def handle_flights(state: TripAssistantState) -> dict:
    llm = ChatOpenAI(model="gpt-4o")
    docs = load_docs_for_topic("flights")
    context = "\n\n".join(docs)

    messages = [
        SystemMessage(content=FLIGHTS_PROMPT.format(context=context)),
        *state["messages"]
    ]

    try:
        response = llm.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        logger.error(f"Flights specialist failed: {e}")
        return {"messages": [AIMessage(content="Error retrieving flight info")]}

# src/nodes/hotels_specialist.py
def handle_hotels(state: TripAssistantState) -> dict:
    llm = ChatOpenAI(model="gpt-4o")
    docs = load_docs_for_topic("hotels")
    context = "\n\n".join(docs)

    # ... exact same pattern
```

### After
```python
# src/nodes/specialist_factory.py
from typing import Callable
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from ..state import TripAssistantState
from ..documents import load_docs_for_topic
from ..logger import logger

def create_specialist(
    topic: str,
    prompt_template: str,
    model: str = "gpt-4o"
) -> Callable[[TripAssistantState], dict]:
    """
    Factory function to create specialist nodes with consistent behavior.

    Args:
        topic: Topic name for document loading
        prompt_template: Prompt template with {context} placeholder
        model: OpenAI model to use

    Returns:
        Specialist node function
    """
    def specialist_node(state: TripAssistantState) -> dict:
        llm = ChatOpenAI(model=model, temperature=0)
        docs = load_docs_for_topic(topic)
        context = "\n\n".join(docs)

        messages = [
            SystemMessage(content=prompt_template.format(context=context)),
            *state["messages"]
        ]

        try:
            response = llm.invoke(messages)
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"{topic.title()} specialist failed: {e}")
            return {
                "messages": [
                    AIMessage(content=f"Sorry, I couldn't retrieve {topic} information.")
                ]
            }

    specialist_node.__name__ = f"handle_{topic}"
    return specialist_node

# Usage in src/nodes/__init__.py
from .specialist_factory import create_specialist
from .prompts import FLIGHTS_PROMPT, HOTELS_PROMPT, ACTIVITIES_PROMPT

handle_flights = create_specialist("flights", FLIGHTS_PROMPT)
handle_hotels = create_specialist("hotels", HOTELS_PROMPT)
handle_activities = create_specialist("activities", ACTIVITIES_PROMPT)
```

**Benefits**:
- DRY (Don't Repeat Yourself)
- Consistent error handling
- Easy to add new specialists
- Centralized changes

---

## Pattern 2: Replace String Parsing with Structured Output

**When**: Parsing LLM string responses manually

### Before
```python
def classify_query(state: TripAssistantState) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    messages = [
        SystemMessage(content="Classify the query. Respond with only: flights, hotels, or activities"),
        *state["messages"]
    ]

    response = llm.invoke(messages)
    topic = response.content.strip().lower()  # Brittle!

    # What if LLM returns "Flights" or "I think it's flights"?
    if topic not in ["flights", "hotels", "activities"]:
        topic = "general"

    return {"topic": topic}
```

### After
```python
from pydantic import BaseModel, Field
from typing import Literal

class TopicClassification(BaseModel):
    """Classification result with topic and confidence."""
    topic: Literal["flights", "hotels", "activities", "restaurants", "transportation", "general"]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    reasoning: str = Field(description="Brief explanation of classification")

def classify_query(state: TripAssistantState) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(TopicClassification)

    messages = [
        SystemMessage(content="Classify the user's trip question by topic."),
        *state["messages"]
    ]

    try:
        result = structured_llm.invoke(messages)

        # Optional: Log low confidence classifications
        if result.confidence < 0.7:
            logger.warning(f"Low confidence classification: {result.topic} ({result.confidence})")

        return {"topic": result.topic}
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return {"topic": "general"}  # Fallback
```

**Benefits**:
- Type-safe
- Guaranteed valid values (Literal type)
- Additional metadata (confidence, reasoning)
- Better error handling

---

## Pattern 3: Simplify Routing with Mapping

**When**: Long if/elif chains for routing

### Before
```python
def route_by_topic(state: TripAssistantState) -> str:
    topic = state.get("topic")

    if topic == "flights":
        return "flights_specialist"
    elif topic == "hotels":
        return "hotels_specialist"
    elif topic == "activities":
        return "activities_specialist"
    elif topic == "restaurants":
        return "restaurants_specialist"
    elif topic == "transportation":
        return "transportation_specialist"
    elif topic == "general":
        return "general_specialist"
    else:
        return "general_specialist"  # Fallback
```

### After
```python
# Module-level constant
TOPIC_ROUTING_MAP: dict[str, str] = {
    "flights": "flights_specialist",
    "hotels": "hotels_specialist",
    "activities": "activities_specialist",
    "restaurants": "restaurants_specialist",
    "transportation": "transportation_specialist",
    "general": "general_specialist",
}

def route_by_topic(state: TripAssistantState) -> str:
    """Route to specialist node based on classified topic."""
    topic = state.get("topic")
    return TOPIC_ROUTING_MAP.get(topic, "general_specialist")
```

**Benefits**:
- More readable
- Easy to add new routes
- Clear default fallback
- Can validate at startup that all Literal values have routes

---

## Pattern 4: Centralize Prompt Management

**When**: Prompts scattered across node files

### Before
```python
# src/nodes/flights_specialist.py
FLIGHTS_PROMPT = """You are a flight information specialist..."""

def handle_flights(state):
    # use FLIGHTS_PROMPT

# src/nodes/hotels_specialist.py
HOTELS_PROMPT = """You are a hotel information specialist..."""

def handle_hotels(state):
    # use HOTELS_PROMPT
```

### After
```python
# src/prompts.py
"""Centralized prompt templates for all agents and specialists."""

CLASSIFIER_SYSTEM_PROMPT = """Analyze the user's question about their trip.
Classify into one of the following topics:
- flights: Questions about flight times, airlines, airports
- hotels: Questions about accommodations, check-in/out
- activities: Questions about tours, attractions, things to do
- restaurants: Questions about dining, food recommendations
- transportation: Questions about getting around, car rentals, trains
- general: General trip questions or unclear intent
"""

FLIGHTS_SPECIALIST_PROMPT = """You are a flight information specialist for a family trip.

Trip Documents:
{context}

Provide specific information about:
- Flight times and airlines
- Airport terminals
- Check-in procedures
- Baggage allowances

Be concise and factual."""

HOTELS_SPECIALIST_PROMPT = """You are a hotel information specialist for a family trip.

Trip Documents:
{context}

Provide specific information about:
- Hotel names and addresses
- Check-in/out times
- Room details and amenities
- Special requests

Be concise and factual."""

# More prompts...
```

```python
# src/nodes/flights_specialist.py
from ..prompts import FLIGHTS_SPECIALIST_PROMPT

def handle_flights(state: TripAssistantState) -> dict:
    # use FLIGHTS_SPECIALIST_PROMPT
```

**Benefits**:
- Single source of truth for prompts
- Easy to A/B test prompt variations
- Better version control for prompt changes
- Easier to review prompt consistency

---

## Pattern 5: Add Confidence-Based Routing

**When**: Classifier should route to general for ambiguous queries

### Before
```python
def classify_query(state: TripAssistantState) -> dict:
    # ... classification logic
    return {"topic": result.topic}

# Graph always routes to specific specialist
graph.add_conditional_edges("classifier", route_by_topic, {
    "flights": "flights_specialist",
    "hotels": "hotels_specialist",
    # ...
})
```

### After
```python
# Enhanced state
class TripAssistantState(TypedDict):
    messages: Annotated[list, add_messages]
    topic: Literal["flights", "hotels", ...] | None
    classification_confidence: float | None  # NEW

# Enhanced classifier
def classify_query(state: TripAssistantState) -> dict:
    # ... classification logic
    result = structured_llm.invoke(messages)

    return {
        "topic": result.topic,
        "classification_confidence": result.confidence
    }

# Confidence-aware routing
def route_with_confidence(state: TripAssistantState) -> str:
    """Route based on topic and confidence."""
    topic = state.get("topic")
    confidence = state.get("classification_confidence", 1.0)

    # Low confidence → general specialist
    if confidence < 0.7:
        logger.info(f"Low confidence ({confidence}) for {topic}, routing to general")
        return "general_specialist"

    return TOPIC_ROUTING_MAP.get(topic, "general_specialist")

# Update graph
graph.add_conditional_edges("classifier", route_with_confidence, {
    "flights_specialist": "flights_specialist",
    "hotels_specialist": "hotels_specialist",
    "general_specialist": "general_specialist",
    # ...
})
```

**Benefits**:
- Handles ambiguous queries gracefully
- Better user experience (accurate answer > fast wrong answer)
- Observable via logging

---

## Pattern 6: Extract Common Test Fixtures

**When**: Test setup duplicated across test files

### Before
```python
# tests/test_classifier.py
def test_classifier_flights():
    state = {
        "messages": [HumanMessage(content="What time is my flight?")],
        "topic": None
    }
    # test logic

# tests/test_flights_specialist.py
def test_flights_specialist():
    state = {
        "messages": [HumanMessage(content="What time is my flight?")],
        "topic": "flights"
    }
    # test logic

# tests/test_graph.py
def test_graph_integration():
    state = {
        "messages": [HumanMessage(content="What time is my flight?")],
        "topic": None
    }
    # test logic
```

### After
```python
# tests/conftest.py
import pytest
from langchain_core.messages import HumanMessage
from src.state import TripAssistantState

@pytest.fixture
def empty_state() -> TripAssistantState:
    """Empty state with no messages."""
    return {"messages": [], "topic": None}

@pytest.fixture
def flight_query() -> str:
    """Sample flight query text."""
    return "What time is my flight to Paris?"

@pytest.fixture
def flight_query_state(flight_query) -> TripAssistantState:
    """State with flight query message."""
    return {
        "messages": [HumanMessage(content=flight_query)],
        "topic": None
    }

@pytest.fixture
def classified_flight_state(flight_query) -> TripAssistantState:
    """State with flight query already classified."""
    return {
        "messages": [HumanMessage(content=flight_query)],
        "topic": "flights"
    }

# tests/test_classifier.py
def test_classifier_flights(flight_query_state):
    result = classify_query(flight_query_state)
    assert result["topic"] == "flights"

# tests/test_flights_specialist.py
def test_flights_specialist(classified_flight_state):
    result = handle_flights(classified_flight_state)
    assert len(result["messages"]) == 1
```

**Benefits**:
- DRY tests
- Consistent test data
- Easy to update test cases
- Fixtures can be composed

---

## Pattern 7: Type-Safe Document Loading

**When**: Document loading has no validation

### Before
```python
def load_docs_for_topic(topic: str) -> list[str]:
    data_dir = Path(__file__).parent.parent / "data"
    files = TOPIC_FILES.get(topic, [])
    return [(data_dir / f).read_text() for f in files]  # No error handling!
```

### After
```python
from pathlib import Path
from typing import Literal

TopicType = Literal["flights", "hotels", "activities", "restaurants", "transportation"]

TOPIC_FILES: dict[TopicType, list[str]] = {
    "flights": ["flight_itinerary.txt", "airport_info.txt"],
    "hotels": ["hotel_booking.txt"],
    "activities": ["activities_plan.txt"],
    "restaurants": ["restaurant_recommendations.txt"],
    "transportation": ["car_rental.txt", "train_schedule.txt"],
}

def load_docs_for_topic(topic: TopicType) -> list[str]:
    """
    Load trip documents for a specific topic.

    Args:
        topic: Topic type (must be valid Literal value)

    Returns:
        List of document contents (empty list if files missing)

    Raises:
        ValueError: If topic not in TOPIC_FILES
    """
    if topic not in TOPIC_FILES:
        raise ValueError(f"Unknown topic: {topic}")

    data_dir = Path(__file__).parent.parent / "data"
    documents = []

    for filename in TOPIC_FILES[topic]:
        file_path = data_dir / filename

        if not file_path.exists():
            logger.warning(f"Document not found: {file_path}")
            continue

        try:
            documents.append(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")

    return documents
```

**Benefits**:
- Type-safe topic parameter
- Handles missing files gracefully
- Logging for debugging
- Clear error messages

---

## When to Refactor

### Immediate (Block PR)
- State mutations
- Missing error handling
- Type errors
- Test failures

### Before Next Release
- Duplicate specialist code
- String parsing (should use structured output)
- Poor type coverage
- Missing tests

### When Convenient
- Long if/elif chains
- Scattered prompts
- Duplicate test setup
- Missing docstrings

---

## Refactoring Workflow

Since this project follows TDD (tests written first per TASKS.md), tests already exist:

1. **Ensure existing tests pass** (`pytest tests/ -v`)
2. **Refactor code** (improve structure, no behavior change)
3. **Run tests to confirm behavior unchanged** (`pytest tests/ -v`)
4. **Run full test suite** (`pytest tests/ -v` - includes integration)
5. **Run quality checks** (`pre-commit run --all-files`)
6. **Commit with clear refactor message**

Note: If refactoring untested code, write characterization test first. But in this TDD workflow, tests already exist!
