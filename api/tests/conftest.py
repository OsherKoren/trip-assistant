"""Shared test fixtures for API tests."""

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_graph
from app.main import app


class MockGraph:
    """Simple stub for agent graph in tests.

    Attributes:
        return_value: The result to return from invoke().
        invoke_calls: List of state dicts passed to invoke() for assertion.
    """

    def __init__(self, return_value: dict[str, Any]) -> None:
        """Initialize mock graph with return value.

        Args:
            return_value: The result to return from invoke().
        """
        self.return_value = return_value
        self.invoke_calls: list[dict[str, Any]] = []

    def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
        """Mock invoke method that records calls and returns preset value.

        Args:
            state: Input state (typically contains "question" key).

        Returns:
            The preset return_value.
        """
        self.invoke_calls.append(state)
        return self.return_value

    async def ainvoke(self, state: dict[str, Any]) -> dict[str, Any]:
        """Mock async invoke method that records calls and returns preset value.

        Args:
            state: Input state (typically contains "question" key).

        Returns:
            The preset return_value.
        """
        self.invoke_calls.append(state)
        return self.return_value


@pytest.fixture
def mock_graph_result() -> dict[str, Any]:
    """Sample agent graph invocation result.

    Returns:
        Dictionary matching the agent's output state schema.
    """
    return {
        "answer": "Your flight departs at 3:00 PM from Terminal 3.",
        "category": "flight",
        "confidence": 0.95,
        "source": "flight.txt",
    }


@pytest.fixture
def mock_graph(mock_graph_result: dict[str, Any]) -> MockGraph:
    """Mock agent graph for testing without calling real agent.

    Args:
        mock_graph_result: Sample result to return from invoke().

    Returns:
        MockGraph instance with invoke() method that returns mock_graph_result.
    """
    return MockGraph(return_value=mock_graph_result)


@pytest.fixture
def client(mock_graph: MockGraph) -> Generator[TestClient, None, None]:
    """Test client with mocked agent dependency.

    This fixture overrides the get_graph dependency to return a mock graph
    instead of importing the real agent. This allows fast unit tests without
    requiring OpenAI API keys.

    Args:
        mock_graph: Mocked agent graph.

    Yields:
        TestClient instance with overridden dependency.
    """

    # Create test client first (lifespan wires the real graph),
    # then override with mock so tests don't call the real agent.
    with TestClient(app) as test_client:
        app.dependency_overrides[get_graph] = lambda: mock_graph
        yield test_client

    app.dependency_overrides.clear()
