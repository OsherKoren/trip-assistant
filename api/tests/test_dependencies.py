"""Tests for dependency injection (build_graph factory)."""

from unittest.mock import MagicMock

import pytest

from app.dependencies import AgentLambdaProxy, build_graph


class TestBuildGraph:
    """Tests for build_graph() factory."""

    def test_local_mode_returns_graph(self) -> None:
        """Test that local mode imports and returns the agent graph."""
        graph = build_graph("local")
        assert graph is not None
        assert hasattr(graph, "ainvoke")
        assert callable(graph.ainvoke)

    def test_lambda_mode_returns_proxy(self) -> None:
        """Test that lambda mode returns AgentLambdaProxy."""
        graph = build_graph("lambda", function_name="test-fn", region="us-west-2")
        assert isinstance(graph, AgentLambdaProxy)
        assert graph.function_name == "test-fn"
        assert graph.region == "us-west-2"

    def test_lambda_mode_missing_function_name_raises(self) -> None:
        """Test that lambda mode without function name raises RuntimeError."""
        with pytest.raises(RuntimeError, match="AGENT_LAMBDA_FUNCTION_NAME"):
            build_graph("lambda")

    def test_local_mode_import_error_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that local mode raises RuntimeError when agent is not installed."""
        import sys

        monkeypatch.delitem(sys.modules, "src.graph", raising=False)
        monkeypatch.delitem(sys.modules, "src", raising=False)
        monkeypatch.setitem(sys.modules, "src.graph", None)  # type: ignore[arg-type]

        with pytest.raises(RuntimeError, match="not available"):
            build_graph("local")

    def test_dependency_override_works(self) -> None:
        """Test that get_graph can be overridden via app.dependency_overrides."""
        from app.dependencies import get_graph
        from app.main import app

        mock_graph = MagicMock()
        app.dependency_overrides[get_graph] = lambda: mock_graph

        overridden = app.dependency_overrides[get_graph]()
        assert overridden is mock_graph

        app.dependency_overrides.clear()
