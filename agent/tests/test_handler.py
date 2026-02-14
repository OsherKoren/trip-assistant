"""Tests for the Lambda handler entry point."""

import json
import sys

import pytest


@pytest.fixture(autouse=True)
def _reset_graph_cache():
    """Reset the cached graph between tests."""
    import handler

    handler._graph = None
    yield
    handler._graph = None


@pytest.fixture()
def mock_graph(mocker):
    """Mock _get_graph to return a mock graph object."""
    mock = mocker.MagicMock()
    mock.invoke.return_value = {
        "answer": "Take a flight from TLV to GVA.",
        "category": "flight",
        "confidence": 0.95,
        "source": "flight.txt",
    }
    mocker.patch("handler._get_graph", return_value=mock)
    return mock


class TestHandler:
    """Tests for the Lambda handler function."""

    def test_direct_invocation(self, mock_graph):
        """Handler processes direct Lambda invocation with question field."""
        from handler import handler

        event = {"question": "How do I get to Geneva?"}
        result = handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["answer"] == "Take a flight from TLV to GVA."
        assert body["category"] == "flight"
        assert body["confidence"] == 0.95
        assert body["source"] == "flight.txt"
        mock_graph.invoke.assert_called_once_with({"question": "How do I get to Geneva?"})

    def test_api_gateway_proxy_event(self, mock_graph):
        """Handler processes API Gateway proxy event with JSON body."""
        from handler import handler

        event = {"body": json.dumps({"question": "What about car rental?"})}
        result = handler(event, None)

        assert result["statusCode"] == 200
        mock_graph.invoke.assert_called_once_with({"question": "What about car rental?"})

    def test_missing_question_returns_400(self, mock_graph):
        """Handler returns 400 when question is missing."""
        from handler import handler

        event = {"body": json.dumps({})}
        result = handler(event, None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "error" in body
        mock_graph.invoke.assert_not_called()

    def test_empty_question_returns_400(self, mock_graph):  # noqa: ARG002
        """Handler returns 400 when question is empty string."""
        from handler import handler

        event = {"question": ""}
        result = handler(event, None)

        assert result["statusCode"] == 400


class TestGetGraph:
    """Tests for lazy graph initialization."""

    def test_fetches_api_key_from_ssm(self, monkeypatch, mocker):
        """_get_graph fetches API key from SSM when not in env."""
        import handler

        monkeypatch.setenv("SSM_PARAMETER_NAME", "/test/openai-api-key")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        handler._graph = None

        mock_ssm = mocker.MagicMock()
        mock_ssm.get_parameter.return_value = {"Parameter": {"Value": "sk-test-key-123"}}
        mocker.patch("boto3.client", return_value=mock_ssm)

        mock_graph_obj = mocker.MagicMock()
        mock_module = mocker.MagicMock()
        mock_module.graph = mock_graph_obj
        monkeypatch.setitem(sys.modules, "src.graph", mock_module)

        result = handler._get_graph()

        assert result is mock_graph_obj
        mock_ssm.get_parameter.assert_called_once_with(
            Name="/test/openai-api-key", WithDecryption=True
        )

    def test_skips_ssm_when_api_key_exists(self, monkeypatch, mocker):
        """_get_graph skips SSM when OPENAI_API_KEY is already set."""
        import handler

        monkeypatch.setenv("SSM_PARAMETER_NAME", "/test/openai-api-key")
        monkeypatch.setenv("OPENAI_API_KEY", "existing-key")
        handler._graph = None

        mock_boto = mocker.patch("boto3.client")

        mock_graph_obj = mocker.MagicMock()
        mock_module = mocker.MagicMock()
        mock_module.graph = mock_graph_obj
        monkeypatch.setitem(sys.modules, "src.graph", mock_module)

        result = handler._get_graph()

        assert result is mock_graph_obj
        mock_boto.assert_not_called()

    def test_caches_graph_instance(self, mocker):
        """_get_graph returns cached graph on subsequent calls."""
        import handler

        cached = mocker.MagicMock()
        handler._graph = cached
        assert handler._get_graph() is cached
