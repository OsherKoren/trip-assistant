"""Shared fixtures and configuration for integration tests."""

import os

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: Integration tests requiring OPENAI_API_KEY")


def pytest_collection_modifyitems(config, items):  # noqa: ARG001
    """Skip integration tests if OPENAI_API_KEY is not set."""
    skip_integration = pytest.mark.skip(
        reason="OPENAI_API_KEY environment variable not set - skipping integration tests"
    )

    for item in items:
        if "integration" in item.keywords and not os.getenv("OPENAI_API_KEY"):
            item.add_marker(skip_integration)


@pytest.fixture
def real_documents():
    """Load real trip documents for integration tests."""
    from src.documents import load_documents

    return load_documents()


@pytest.fixture
def integration_state(real_documents):
    """Create initial state for integration tests with real documents."""
    from src.schemas import TripAssistantState

    state: TripAssistantState = {
        "question": "",
        "category": "general",
        "confidence": 0.0,
        "documents": real_documents,
        "current_context": "",
        "answer": "",
        "source": None,
    }
    return state
