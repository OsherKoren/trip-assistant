"""Tests for the Lambda handler module."""

import json
from typing import Any
from unittest.mock import MagicMock

from mangum import Mangum

from app.handler import handler
from app.main import app


def _mock_lambda_context() -> MagicMock:
    """Create a mock Lambda context for testing.

    Returns:
        Mock Lambda context with required attributes.
    """
    context = MagicMock()
    context.request_id = "test-request-id"
    context.function_name = "trip-assistant-api"
    context.function_version = "$LATEST"
    context.invoked_function_arn = (
        "arn:aws:lambda:us-east-1:123456789012:function:trip-assistant-api"
    )
    context.memory_limit_in_mb = 256
    context.log_group_name = "/aws/lambda/trip-assistant-api"
    context.log_stream_name = "2026/01/01/[$LATEST]test"
    return context


def test_handler_is_mangum_instance() -> None:
    """Verify handler is a Mangum instance wrapping the FastAPI app."""
    assert isinstance(handler, Mangum)


def test_handler_is_callable() -> None:
    """Verify handler can be called like a Lambda function."""
    assert callable(handler)


def test_health_endpoint_via_lambda_event(mock_graph: Any) -> None:
    """Test GET /api/health returns healthy status via Lambda event."""
    # Override dependency for testing
    from app.dependencies import get_graph

    app.dependency_overrides[get_graph] = lambda: mock_graph

    # API Gateway HTTP API (v2.0) event for GET /api/health
    event = {
        "version": "2.0",
        "routeKey": "GET /api/health",
        "rawPath": "/api/health",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test-api-id",
            "domainName": "test.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "test",
            "http": {
                "method": "GET",
                "path": "/api/health",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test-agent",
            },
            "requestId": "test-request-id-123",
            "stage": "$default",
            "time": "01/Jan/2026:00:00:00 +0000",
            "timeEpoch": 1704067200000,
        },
        "isBase64Encoded": False,
    }

    # Invoke handler
    response = handler(event, _mock_lambda_context())

    # Verify response structure
    assert response["statusCode"] == 200
    assert "body" in response

    # Parse response body
    body = json.loads(response["body"])
    assert body["status"] == "healthy"
    assert body["service"] == "trip-assistant-api"
    assert "version" in body

    # Cleanup
    app.dependency_overrides.clear()


def test_messages_endpoint_via_lambda_event(mock_graph: Any) -> None:
    """Test POST /api/messages processes message via Lambda event."""
    # Override dependency for testing
    from app.dependencies import get_graph

    app.dependency_overrides[get_graph] = lambda: mock_graph

    # API Gateway HTTP API (v2.0) event for POST /api/messages
    event = {
        "version": "2.0",
        "routeKey": "POST /api/messages",
        "rawPath": "/api/messages",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test-api-id",
            "domainName": "test.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "test",
            "http": {
                "method": "POST",
                "path": "/api/messages",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test-agent",
            },
            "requestId": "test-request-id-456",
            "stage": "$default",
            "time": "01/Jan/2026:00:00:00 +0000",
            "timeEpoch": 1704067200000,
        },
        "body": json.dumps({"question": "What car did we rent?"}),
        "isBase64Encoded": False,
    }

    # Invoke handler
    response = handler(event, _mock_lambda_context())

    # Verify response structure
    assert response["statusCode"] == 200
    assert "body" in response

    # Parse response body
    body = json.loads(response["body"])
    assert body["answer"] == "Your flight departs at 3:00 PM from Terminal 3."
    assert body["category"] == "flight"
    assert body["confidence"] == 0.95
    assert body["source"] == "flight.txt"

    # Verify agent was invoked
    assert len(mock_graph.invoke_calls) == 1
    assert mock_graph.invoke_calls[0]["question"] == "What car did we rent?"

    # Cleanup
    app.dependency_overrides.clear()


def test_invalid_request_handling_via_lambda_event(mock_graph: Any) -> None:
    """Test Lambda event with invalid request body returns 422."""
    # Override dependency for testing
    from app.dependencies import get_graph

    app.dependency_overrides[get_graph] = lambda: mock_graph

    # API Gateway HTTP API (v2.0) event with empty question
    event = {
        "version": "2.0",
        "routeKey": "POST /api/messages",
        "rawPath": "/api/messages",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test-api-id",
            "domainName": "test.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "test",
            "http": {
                "method": "POST",
                "path": "/api/messages",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test-agent",
            },
            "requestId": "test-request-id-789",
            "stage": "$default",
            "time": "01/Jan/2026:00:00:00 +0000",
            "timeEpoch": 1704067200000,
        },
        "body": json.dumps({"question": ""}),  # Invalid: empty question
        "isBase64Encoded": False,
    }

    # Invoke handler
    response = handler(event, _mock_lambda_context())

    # Verify error response
    assert response["statusCode"] == 422  # Validation error

    # Cleanup
    app.dependency_overrides.clear()


def test_agent_error_handling_via_lambda_event() -> None:
    """Test Lambda event handles agent invocation errors gracefully."""

    # Create a custom MockGraph that raises an error
    class ErrorMockGraph:
        def invoke(self, _state: dict[str, Any]) -> dict[str, Any]:
            raise RuntimeError("Agent processing failed")

        async def ainvoke(self, _state: dict[str, Any]) -> dict[str, Any]:
            raise RuntimeError("Agent processing failed")

    error_graph = ErrorMockGraph()

    # Override dependency for testing
    from app.dependencies import get_graph

    app.dependency_overrides[get_graph] = lambda: error_graph

    # API Gateway HTTP API (v2.0) event
    event = {
        "version": "2.0",
        "routeKey": "POST /api/messages",
        "rawPath": "/api/messages",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test-api-id",
            "domainName": "test.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "test",
            "http": {
                "method": "POST",
                "path": "/api/messages",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test-agent",
            },
            "requestId": "test-request-id-error",
            "stage": "$default",
            "time": "01/Jan/2026:00:00:00 +0000",
            "timeEpoch": 1704067200000,
        },
        "body": json.dumps({"question": "What car did we rent?"}),
        "isBase64Encoded": False,
    }

    # Invoke handler
    response = handler(event, _mock_lambda_context())

    # Verify error response
    assert response["statusCode"] == 500

    # Parse error response
    body = json.loads(response["body"])
    assert "detail" in body
    # Should not expose internal error details
    assert "Agent processing failed" not in body["detail"]

    # Cleanup
    app.dependency_overrides.clear()
