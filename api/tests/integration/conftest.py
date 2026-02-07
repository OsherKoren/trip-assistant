"""Fixtures and configuration for integration tests with real OpenAI API.

Integration tests make actual API calls to OpenAI and require:
OPENAI_API_KEY set in the OS environment.

These tests use the real agent graph (not mocks) via TestClient.
"""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


def pytest_configure(config: pytest.Config) -> None:
    """Register integration marker.

    Args:
        config: Pytest configuration object.
    """
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires OpenAI API key)"
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:  # noqa: ARG001
    """Skip integration tests unless OPENAI_API_KEY is set.

    Args:
        config: Pytest configuration object.
        items: List of collected test items.
    """
    skip_integration = pytest.mark.skip(
        reason="OPENAI_API_KEY environment variable not set - skipping integration tests"
    )

    for item in items:
        if "integration" in item.keywords and not os.getenv("OPENAI_API_KEY"):
            item.add_marker(skip_integration)


@pytest.fixture
def integration_client() -> Generator[TestClient, None, None]:
    """Test client with real agent dependency for integration tests.

    This fixture:
    1. Forces ENVIRONMENT=dev to use local agent import
    2. Does NOT override get_graph dependency (uses real agent)
    3. Requires OPENAI_API_KEY in environment
    4. Makes actual OpenAI API calls

    Yields:
        TestClient instance with real agent graph.
    """
    # Force dev environment to ensure local agent import
    original_env = os.getenv("ENVIRONMENT")
    os.environ["ENVIRONMENT"] = "dev"

    try:
        # Create test client WITHOUT dependency overrides (uses real agent)
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Restore original environment setting
        if original_env is not None:
            os.environ["ENVIRONMENT"] = original_env
        else:
            os.environ.pop("ENVIRONMENT", None)

        # Ensure no dependency overrides leak to other tests
        app.dependency_overrides.clear()
