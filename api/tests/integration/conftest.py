"""Fixtures and configuration for integration tests with real OpenAI API.

Integration tests make actual API calls to OpenAI and require:
OPENAI_API_KEY set in the OS environment.

These tests use the real agent graph (not mocks) via TestClient.
"""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.dependencies import build_graph, get_graph
from app.main import app


def pytest_configure(config: pytest.Config) -> None:
    """Register integration marker."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires OpenAI API key)"
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:  # noqa: ARG001
    """Skip integration tests unless OPENAI_API_KEY is set."""
    skip_integration = pytest.mark.skip(
        reason="OPENAI_API_KEY environment variable not set - skipping integration tests"
    )

    for item in items:
        if "integration" in item.keywords and not os.getenv("OPENAI_API_KEY"):
            item.add_marker(skip_integration)


@pytest.fixture
def integration_client() -> Generator[TestClient, None, None]:
    """Test client with real agent dependency for integration tests.

    Uses AGENT_MODE=local to import the real agent graph directly.
    Requires OPENAI_API_KEY in environment.

    Yields:
        TestClient instance with real agent graph.
    """
    try:
        with TestClient(app) as test_client:
            graph = build_graph("local")
            app.dependency_overrides[get_graph] = lambda: graph
            yield test_client
    finally:
        app.dependency_overrides.clear()
