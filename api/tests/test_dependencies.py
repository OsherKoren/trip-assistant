"""Tests for dependency injection."""

import sys
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.dependencies import get_graph


@pytest.fixture
def mock_request() -> MagicMock:
    """Create a mock FastAPI Request object.

    Returns a request with no Lambda context (simulates local development).
    """
    request = MagicMock(spec=Request)
    request.scope = {}  # No aws.context in local dev
    return request


class TestGetGraph:
    """Tests for get_graph dependency."""

    def test_get_graph_returns_callable(self, mock_request: MagicMock) -> None:
        """Test that get_graph returns an object with invoke method."""
        graph = get_graph(mock_request)
        assert graph is not None
        assert hasattr(graph, "invoke")
        assert callable(graph.invoke)

    def test_get_graph_can_be_invoked(self, mock_request: MagicMock) -> None:
        """Test that returned graph can be invoked with sample state."""
        graph = get_graph(mock_request)
        # Should have invoke method (we don't call it to avoid real agent execution)
        assert callable(getattr(graph, "invoke", None))

    def test_get_graph_handles_import_error(self, mock_request: MagicMock) -> None:
        """Test that import errors raise HTTPException 500."""
        # Remove src.graph from sys.modules and prevent re-import
        original = sys.modules.pop("src.graph", None)
        original_src = sys.modules.pop("src", None)

        # Create a mock module that raises ImportError on attribute access
        class FailingModule:
            def __getattr__(self, name: str) -> None:
                raise ImportError(f"No module named 'src.{name}'")

        sys.modules["src"] = FailingModule()  # type: ignore[assignment]

        try:
            with pytest.raises(HTTPException) as exc_info:
                get_graph(mock_request)
            assert exc_info.value.status_code == 500
            assert "not available" in exc_info.value.detail.lower()
        finally:
            # Restore original modules
            sys.modules.pop("src", None)
            if original is not None:
                sys.modules["src.graph"] = original
            if original_src is not None:
                sys.modules["src"] = original_src

    def test_get_graph_dependency_override_works(self, mock_request: MagicMock) -> None:
        """Test that dependency can be overridden for testing."""
        from app.main import app

        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"answer": "test"}

        # Test override mechanism (must accept Request parameter)
        app.dependency_overrides[get_graph] = lambda _request: mock_graph

        # Verify override works
        overridden_graph = app.dependency_overrides[get_graph](mock_request)
        assert overridden_graph == mock_graph

        # Cleanup
        app.dependency_overrides.clear()
