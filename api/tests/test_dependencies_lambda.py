"""Tests for AgentLambdaProxy."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.dependencies import AgentLambdaProxy

# --- Fixtures ---


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
    mock_payload = MagicMock()
    mock_payload.read = AsyncMock(return_value=json.dumps(sample_response).encode("utf-8"))

    mock_lambda_client = MagicMock()
    mock_lambda_client.invoke = AsyncMock(return_value={"Payload": mock_payload})
    mock_lambda_client.__aenter__ = AsyncMock(return_value=mock_lambda_client)
    mock_lambda_client.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.client = MagicMock(return_value=mock_lambda_client)

    with patch("app.dependencies.aioboto3.Session", return_value=mock_session):
        proxy = AgentLambdaProxy(function_name="test-agent-lambda", region="us-east-2")
        result = await proxy.ainvoke(sample_state)

        assert result == sample_response
        assert result["answer"] == "A Renault Clio"
        assert result["category"] == "transportation"

        mock_lambda_client.invoke.assert_called_once_with(
            FunctionName="test-agent-lambda",
            InvocationType="RequestResponse",
            Payload=json.dumps(sample_state).encode("utf-8"),
        )


@pytest.mark.asyncio
async def test_agent_lambda_proxy_ainvoke_lambda_error(sample_state: dict[str, str]) -> None:
    """Test AgentLambdaProxy.ainvoke() handles Lambda invocation errors."""
    mock_lambda_client = MagicMock()
    mock_lambda_client.invoke = AsyncMock(side_effect=Exception("Lambda timeout"))
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


@pytest.mark.asyncio
async def test_agent_lambda_proxy_ainvoke_json_parsing_error(sample_state: dict[str, str]) -> None:
    """Test AgentLambdaProxy.ainvoke() handles invalid JSON responses."""
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
