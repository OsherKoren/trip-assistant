# Testing Patterns

## Table of Contents
- [TDD Workflow](#tdd-workflow)
- [Node Unit Tests](#node-unit-tests)
- [Graph Integration Tests](#graph-integration-tests)
- [Fixtures](#fixtures)
- [Mocking LLM Calls](#mocking-llm-calls)

---

## TDD Workflow

1. Write failing test
2. Run `pytest tests/ -v` - confirm it fails
3. Implement minimal code to pass
4. Run `pytest tests/ -v` - confirm it passes
5. Refactor if needed
6. Run `pre-commit run --all-files` before committing

---

## Node Unit Tests

### Testing Classifier

```python
# tests/test_classifier.py
import pytest
from langchain_core.messages import HumanMessage
from src.nodes.classifier import classify_query

@pytest.mark.parametrize("query,expected_topic", [
    ("What time is my flight?", "flights"),
    ("Where is my hotel?", "hotels"),
    ("What activities are planned?", "activities"),
    ("Best restaurants nearby?", "restaurants"),
])
def test_classifier_routes_correctly(query, expected_topic):
    state = {"messages": [HumanMessage(content=query)], "topic": None}
    result = classify_query(state)
    assert result["topic"] == expected_topic
```

### Testing Specialist Node

```python
# tests/test_flights_specialist.py
import pytest
from langchain_core.messages import HumanMessage, AIMessage
from src.nodes.flights_specialist import handle_flights

def test_flights_specialist_returns_message():
    state = {
        "messages": [HumanMessage(content="What time is my flight?")],
        "topic": "flights"
    }
    result = handle_flights(state)
    
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
```

---

## Graph Integration Tests

### Full Graph Execution

```python
# tests/test_graph.py
import pytest
from langchain_core.messages import HumanMessage
from src.graph import app

def test_graph_handles_flight_query():
    result = app.invoke({
        "messages": [HumanMessage(content="What time is my flight to Paris?")],
        "topic": None
    })
    
    assert result["topic"] == "flights"
    assert len(result["messages"]) >= 2  # Input + response

def test_graph_handles_hotel_query():
    result = app.invoke({
        "messages": [HumanMessage(content="What's my hotel address?")],
        "topic": None
    })
    
    assert result["topic"] == "hotels"
```

### Testing Routing

```python
# tests/test_routing.py
from src.graph import route_by_topic

def test_route_by_topic_returns_correct_node():
    state = {"topic": "flights", "messages": []}
    assert route_by_topic(state) == "flights"
    
    state = {"topic": "hotels", "messages": []}
    assert route_by_topic(state) == "hotels"
```

---

## Fixtures

```python
# tests/conftest.py
import pytest
from langchain_core.messages import HumanMessage

@pytest.fixture
def empty_state():
    return {"messages": [], "topic": None}

@pytest.fixture
def flight_query_state():
    return {
        "messages": [HumanMessage(content="What time is my flight?")],
        "topic": None
    }

@pytest.fixture
def classified_state():
    return {
        "messages": [HumanMessage(content="What time is my flight?")],
        "topic": "flights"
    }
```

Usage:
```python
def test_with_fixture(flight_query_state):
    result = classify_query(flight_query_state)
    assert result["topic"] == "flights"
```

---

## Mocking LLM Calls

### Using unittest.mock

```python
# tests/test_classifier_mocked.py
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from src.nodes.classifier import classify_query

@patch("src.nodes.classifier.ChatOpenAI")
def test_classifier_with_mocked_llm(mock_llm_class):
    # Setup mock
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="flights")
    mock_llm_class.return_value = mock_llm
    
    state = {"messages": [HumanMessage(content="Flight info?")], "topic": None}
    result = classify_query(state)
    
    assert result["topic"] == "flights"
    mock_llm.invoke.assert_called_once()
```

### Using pytest-mock

```python
def test_specialist_with_mocker(mocker):
    mock_llm = mocker.patch("src.nodes.flights_specialist.ChatOpenAI")
    mock_llm.return_value.invoke.return_value = AIMessage(
        content="Your flight departs at 3:00 PM."
    )
    
    state = {"messages": [HumanMessage(content="Flight time?")], "topic": "flights"}
    result = handle_flights(state)
    
    assert "3:00 PM" in result["messages"][0].content
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_classifier.py -v

# Specific test
pytest tests/test_classifier.py::test_classifier_routes_correctly -v

# With coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```
