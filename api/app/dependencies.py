"""Dependency injection for the agent graph.

This module provides FastAPI dependencies for initializing and accessing
the LangGraph agent. Using dependency injection allows easy mocking in tests
via app.dependency_overrides without modifying production code.

Dual-Mode Pattern:
- Dev mode (ENVIRONMENT=dev): Import local agent directly from src.graph
- Production mode (ENVIRONMENT=prod): Use AgentLambdaProxy to invoke agent via Lambda
"""

import json
import os
from typing import Any, Protocol, cast

import aioboto3
from fastapi import HTTPException, Request

from app.logger import logger


class AgentGraphProtocol(Protocol):
    """Protocol defining the agent graph interface.

    This protocol ensures both local agent and Lambda proxy provide
    the same ainvoke() method for consistent route handler usage.
    """

    async def ainvoke(self, state: dict[str, Any]) -> dict[str, Any]:
        """Invoke the agent asynchronously.

        Args:
            state: Agent state dictionary with at least {"question": str}.

        Returns:
            Agent state dictionary with answer, category, confidence, etc.
        """
        ...


class AgentLambdaProxy:
    """Proxy for invoking the agent Lambda function asynchronously.

    This class wraps aioboto3 Lambda client to provide the same ainvoke()
    interface as the local agent graph, enabling transparent dual-mode operation.
    """

    def __init__(self, function_name: str, region: str = "us-east-2") -> None:
        """Initialize the Lambda proxy.

        Args:
            function_name: Name of the agent Lambda function.
            region: AWS region where the Lambda is deployed.
        """
        self.function_name = function_name
        self.region = region

    async def ainvoke(self, state: dict[str, Any]) -> dict[str, Any]:
        """Invoke the agent Lambda function asynchronously.

        Args:
            state: Agent state dictionary with at least {"question": str}.

        Returns:
            Agent state dictionary with answer, category, confidence, etc.

        Raises:
            HTTPException: 500 error if Lambda invocation fails.
        """
        try:
            # Create aioboto3 session and Lambda client
            session = aioboto3.Session()
            async with session.client("lambda", region_name=self.region) as lambda_client:
                # Invoke Lambda function with JSON payload
                response = await lambda_client.invoke(
                    FunctionName=self.function_name,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(state).encode("utf-8"),
                )

                # Read and parse response payload
                payload_bytes = await response["Payload"].read()
                result: dict[str, Any] = json.loads(payload_bytes.decode("utf-8"))

                logger.debug(
                    "Agent Lambda invoked successfully",
                    function_name=self.function_name,
                    question=state.get("question", "")[:50],
                )
                return result

        except Exception as e:
            logger.error(
                "Agent Lambda invocation failed",
                function_name=self.function_name,
                error=str(e),
                state=state,
            )
            raise HTTPException(
                status_code=500,
                detail="Agent processing failed. Please try again later.",
            ) from e


def get_graph(request: Request) -> AgentGraphProtocol:
    """Get the agent graph (local or Lambda proxy based on ENVIRONMENT).

    This dependency returns either:
    - Dev mode (ENVIRONMENT=dev): Local agent graph imported from src.graph
    - Production mode (ENVIRONMENT=prod): AgentLambdaProxy for Lambda invocation

    Both provide the same ainvoke() interface for consistent route handler usage.

    Args:
        request: FastAPI request object (provides Lambda context in production).

    Returns:
        Agent graph or proxy with ainvoke() method.

    Raises:
        HTTPException: 500 error if agent cannot be initialized.

    Example:
        ```python
        @app.post("/api/messages")
        async def create_message(
            message: MessageRequest,
            graph = Depends(get_graph)
        ):
            result = await graph.ainvoke({"question": message.question})
            return MessageResponse(**result)
        ```
    """
    # Extract request ID for tracing (Lambda context available in production)
    lambda_context = request.scope.get("aws.context")
    request_id = lambda_context.aws_request_id if lambda_context else "local"

    # Check environment mode
    environment = os.getenv("ENVIRONMENT", "dev")

    if environment == "dev":
        # Dev mode: Import local agent graph
        try:
            from src.graph import graph

            logger.debug(
                "Agent graph initialized in dev mode (local import)",
                request_id=request_id,
            )
            # Cast needed because agent package has ignore_missing_imports=true
            return cast(AgentGraphProtocol, graph)
        except ImportError as e:
            logger.error(
                "Failed to import agent graph in dev mode",
                error=str(e),
                request_id=request_id,
            )
            raise HTTPException(
                status_code=500,
                detail="Agent graph not available. Ensure agent package is installed.",
            ) from e
    else:
        # Production mode: Use Lambda proxy
        function_name = os.getenv("AGENT_LAMBDA_FUNCTION_NAME")
        if not function_name:
            logger.error(
                "AGENT_LAMBDA_FUNCTION_NAME not set in production mode",
                request_id=request_id,
            )
            raise HTTPException(
                status_code=500,
                detail="Agent configuration error. Please contact support.",
            )

        region = os.getenv("AWS_REGION", "us-east-2")
        logger.debug(
            "Agent graph initialized in production mode (Lambda proxy)",
            function_name=function_name,
            region=region,
            request_id=request_id,
        )
        return AgentLambdaProxy(function_name=function_name, region=region)
