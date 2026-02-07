"""Tests for Lambda proxy mode in dependencies.

These tests verify dual-mode operation (dev vs prod), Lambda invocation,
and error handling for the AgentLambdaProxy class.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Request

from app.dependencies import AgentLambdaProxy, get_graph

# --- Fixtures ---


@pytest.fixture
def mock_request() -> Request:
    """Create a mock FastAPI request."""
    request = MagicMock(spec=Request)
    request.scope = {"aws.context": None}
    return request


@pytest.fixture
def sample_state() -> dict[str, str]:
    """Sample agent state for testing."""
    return {"question": "What car did we rent?"}


@pytest.fixture
def sample_response() -> dict[str, str | float]:
    """Sample agent response for testing."""
    return {
        "question": "What car did we rent?",
        "answer": "A Renault Clio",
        "category": "transportation",
        "confidence": 0.95,
    }


# --- AgentLambdaProxy Tests ---


@pytest.mark.asyncio
async def test_agent_lambda_proxy_ainvoke_success(
    sample_state: dict[str, str], sample_response: dict[str, str | float]
) -> None:
    """Test AgentLambdaProxy.ainvoke() with successful Lambda invocation."""
    # Mock aioboto3 session and Lambda client
    mock_payload = MagicMock()
    mock_payload.read = AsyncMock(return_value=json.dumps(sample_response).encode("utf-8"))

    mock_lambda_client = MagicMock()
    mock_lambda_client.invoke = AsyncMock(return_value={"Payload": mock_payload})
    mock_lambda_client.__aenter__ = AsyncMock(return_value=mock_lambda_client)
    mock_lambda_client.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.client = MagicMock(return_value=mock_lambda_client)

    # Patch aioboto3.Session
    with patch("app.dependencies.aioboto3.Session", return_value=mock_session):
        proxy = AgentLambdaProxy(function_name="test-agent-lambda", region="us-east-2")
        result = await proxy.ainvoke(sample_state)

        # Verify result matches expected response
        assert result == sample_response
        assert result["answer"] == "A Renault Clio"
        assert result["category"] == "transportation"

        # Verify Lambda client was called correctly
        mock_lambda_client.invoke.assert_called_once_with(
            FunctionName="test-agent-lambda",
            InvocationType="RequestResponse",
            Payload=json.dumps(sample_state).encode("utf-8"),
        )


@pytest.mark.asyncio
async def test_agent_lambda_proxy_ainvoke_lambda_error(sample_state: dict[str, str]) -> None:
    """Test AgentLambdaProxy.ainvoke() handles Lambda invocation errors."""
    # Mock Lambda client that raises an error
    mock_lambda_client = MagicMock()
    mock_lambda_client.invoke = AsyncMock(side_effect=Exception("Lambda timeout"))
    mock_lambda_client.__aenter__ = AsyncMock(return_value=mock_lambda_client)
    mock_lambda_client.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.client = MagicMock(return_value=mock_lambda_client)

    with patch("app.dependencies.aioboto3.Session", return_value=mock_session):
        proxy = AgentLambdaProxy(function_name="test-agent-lambda")

        # Verify HTTPException is raised
        with pytest.raises(HTTPException) as exc_info:
            await proxy.ainvoke(sample_state)

        assert exc_info.value.status_code == 500
        assert "Agent processing failed" in exc_info.value.detail


@pytest.mark.asyncio
async def test_agent_lambda_proxy_ainvoke_json_parsing_error(sample_state: dict[str, str]) -> None:
    """Test AgentLambdaProxy.ainvoke() handles invalid JSON responses."""
    # Mock Lambda response with invalid JSON
    mock_payload = MagicMock()
    mock_payload.read = AsyncMock(return_value=b"invalid json")

    mock_lambda_client = MagicMock()
    mock_lambda_client.invoke = AsyncMock(return_value={"Payload": mock_payload})
    mock_lambda_client.__aenter__ = AsyncMock(return_value=mock_lambda_client)
    mock_lambda_client.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.client = MagicMock(return_value=mock_lambda_client)

    with patch("app.dependencies.aioboto3.Session", return_value=mock_session):
        proxy = AgentLambdaProxy(function_name="test-agent-lambda")

        with pytest.raises(HTTPException) as exc_info:
            await proxy.ainvoke(sample_state)

        assert exc_info.value.status_code == 500
        assert "Agent processing failed" in exc_info.value.detail


# --- Dual-Mode Tests ---


def test_get_graph_dev_mode_returns_local_agent(mock_request: Request) -> None:
    """Test get_graph() returns local agent in dev mode."""
    with patch.dict("os.environ", {"ENVIRONMENT": "dev"}):
        # Mock the agent import
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock()

        with patch.dict("sys.modules", {"src.graph": MagicMock(graph=mock_graph)}):
            graph = get_graph(mock_request)

            # Verify local graph is returned
            assert graph is mock_graph


def test_get_graph_prod_mode_returns_lambda_proxy(mock_request: Request) -> None:
    """Test get_graph() returns Lambda proxy in production mode."""
    with patch.dict(
        "os.environ",
        {
            "ENVIRONMENT": "prod",
            "AGENT_LAMBDA_FUNCTION_NAME": "prod-agent-lambda",
            "AWS_REGION": "us-west-2",
        },
    ):
        graph = get_graph(mock_request)

        # Verify Lambda proxy is returned
        assert isinstance(graph, AgentLambdaProxy)
        assert graph.function_name == "prod-agent-lambda"
        assert graph.region == "us-west-2"


def test_get_graph_prod_mode_missing_function_name(mock_request: Request) -> None:
    """Test get_graph() raises error when AGENT_LAMBDA_FUNCTION_NAME not set."""
    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "prod"},
        clear=True,
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_graph(mock_request)

        assert exc_info.value.status_code == 500
        assert "Agent configuration error" in exc_info.value.detail


def test_get_graph_dev_mode_import_error(mock_request: Request) -> None:
    """Test get_graph() handles agent import errors in dev mode."""
    with (
        patch.dict("os.environ", {"ENVIRONMENT": "dev"}),
        patch("app.dependencies.logger"),
        patch.dict("sys.modules", {"src.graph": None}),
        pytest.raises(HTTPException) as exc_info,
    ):
        get_graph(mock_request)

    assert exc_info.value.status_code == 500
    assert "Agent graph not available" in exc_info.value.detail
