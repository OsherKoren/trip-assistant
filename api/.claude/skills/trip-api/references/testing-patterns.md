# Testing Patterns

## Table of Contents
- [TDD Workflow](#tdd-workflow)
- [Test Fixtures](#test-fixtures)
- [Testing Endpoints](#testing-endpoints)
- [Testing Validation](#testing-validation)
- [Testing Dependencies](#testing-dependencies)
- [Integration Tests](#integration-tests)

---

## TDD Workflow

1. Write failing test
2. Run `pytest tests/ -v` - confirm it fails
3. Implement minimal code to pass
4. Run `pytest tests/ -v` - confirm it passes
5. Refactor if needed
6. Run `pre-commit run --all-files` before committing

---

## Test Fixtures

### Shared Fixtures (`tests/conftest.py`)

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.dependencies import get_graph

@pytest.fixture
def mock_graph():
    """Mock agent graph for testing."""
    graph = MagicMock()
    graph.invoke.return_value = {
        "answer": "Test answer",
        "category": "flight",
        "confidence": 0.95,
        "source": "flight.txt"
    }
    return graph

@pytest.fixture
def mock_graph_result():
    """Sample agent result for testing."""
    return {
        "answer": "Your flight departs at 3:00 PM",
        "category": "flight",
        "confidence": 0.95,
        "source": "flight.txt"
    }

@pytest.fixture
def client(mock_graph):
    """TestClient with overridden agent dependency."""
    app.dependency_overrides[get_graph] = lambda: mock_graph
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Parametrized Fixtures

```python
@pytest.fixture(params=["flight", "car_rental", "routes", "aosta", "chamonix", "annecy_geneva", "general"])
def category(request):
    """All valid categories for parametrized tests."""
    return request.param
```

---

## Testing Endpoints

### POST Endpoint Success

```python
# tests/test_main.py
def test_create_message_success(client, mock_graph):
    response = client.post(
        "/api/messages",
        json={"question": "What time is my flight?"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Test answer"
    assert data["category"] == "flight"
    assert data["confidence"] == 0.95
    assert data["source"] == "flight.txt"

    # Verify agent was called
    mock_graph.invoke.assert_called_once_with(
        {"question": "What time is my flight?"}
    )
```

### GET Endpoint

```python
def test_health_check(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "trip-assistant-api"
```

### Testing All Categories (Parametrized)

```python
@pytest.mark.parametrize("category", [
    "flight", "car_rental", "routes", "aosta", "chamonix", "annecy_geneva", "general"
])
def test_handles_all_categories(client, mock_graph, category):
    mock_graph.invoke.return_value = {
        "answer": f"Answer for {category}",
        "category": category,
        "confidence": 0.9,
        "source": f"{category}.txt"
    }

    response = client.post(
        "/api/messages",
        json={"question": f"Question about {category}"}
    )

    assert response.status_code == 200
    assert response.json()["category"] == category
```

---

## Testing Validation

### Empty String Validation

```python
def test_empty_question_rejected(client):
    response = client.post(
        "/api/messages",
        json={"question": ""}
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("question" in str(error).lower() for error in detail)
```

### Missing Field Validation

```python
def test_missing_question_rejected(client):
    response = client.post(
        "/api/messages",
        json={}
    )

    assert response.status_code == 422
```

### Whitespace Validation

```python
@pytest.mark.parametrize("question", ["   ", "\t", "\n", "  \n  "])
def test_whitespace_question_rejected(client, question):
    response = client.post(
        "/api/messages",
        json={"question": question}
    )

    assert response.status_code == 422
```

---

## Testing Dependencies

### Dependency Override

```python
def test_dependency_override_works():
    mock = MagicMock()
    mock.invoke.return_value = {"answer": "Override works"}

    app.dependency_overrides[get_graph] = lambda: mock
    client = TestClient(app)

    response = client.post(
        "/api/messages",
        json={"question": "Test"}
    )

    assert response.json()["answer"] == "Override works"
    app.dependency_overrides.clear()
```

### Agent Import Error

```python
def test_agent_import_error():
    def failing_dependency():
        raise ImportError("Agent not found")

    app.dependency_overrides[get_graph] = failing_dependency
    client = TestClient(app)

    response = client.post(
        "/api/messages",
        json={"question": "Test"}
    )

    assert response.status_code == 500
    app.dependency_overrides.clear()
```

---

## Integration Tests

### Real Agent (No Mocks)

```python
# tests/integration/conftest.py
import pytest
import os

@pytest.fixture(scope="session", autouse=True)
def skip_if_no_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set", allow_module_level=True)

@pytest.fixture
def integration_client():
    """TestClient with real agent (no mocks)."""
    # Don't override dependencies - use real agent
    return TestClient(app)
```

### End-to-End Test

```python
# tests/integration/test_api_integration.py
import pytest

@pytest.mark.integration
def test_real_flight_question(integration_client):
    response = integration_client.post(
        "/api/messages",
        json={"question": "What time is our flight?"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["answer"]) > 0
    assert data["category"] in ["flight", "general"]
    assert 0.0 <= data["confidence"] <= 1.0
```

### Testing Multiple Categories

```python
@pytest.mark.integration
@pytest.mark.parametrize("question,expected_category", [
    ("What time is our flight?", "flight"),
    ("Where do we pick up the car?", "car_rental"),
    ("How do we get to Aosta?", "routes"),
])
def test_real_classification(integration_client, question, expected_category):
    response = integration_client.post(
        "/api/messages",
        json={"question": question}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == expected_category
    assert len(data["answer"]) > 10  # Meaningful answer
    assert data["confidence"] > 0.5   # Reasonable confidence
```

---

## Testing Lambda Handler

### API Gateway Event

```python
# tests/test_handler.py
from app.handler import handler

def test_handler_with_api_gateway_event():
    event = {
        "version": "2.0",
        "routeKey": "POST /api/messages",
        "rawPath": "/api/messages",
        "requestContext": {
            "http": {
                "method": "POST",
                "path": "/api/messages"
            }
        },
        "headers": {
            "content-type": "application/json"
        },
        "body": '{"question": "Test question"}',
        "isBase64Encoded": False
    }

    response = handler(event, {})

    assert response["statusCode"] == 200
    assert "body" in response
```

---

## Running Tests

```bash
# All unit tests (fast, mocked)
pytest tests/ -v -m "not integration"

# Integration tests only (requires OPENAI_API_KEY)
pytest tests/ -v -m integration

# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Specific test
pytest tests/test_main.py::test_create_message_success -v
```
