"""Dependency injection for the agent graph.

Provides a build_graph() factory called once at startup and a get_graph()
stub that lifespan overrides via app.dependency_overrides.
"""

import json
from typing import Any, Protocol, cast

import aioboto3
from fastapi import HTTPException

from app.logger import logger


class AgentGraphProtocol(Protocol):
    """Protocol defining the agent graph interface."""

    async def ainvoke(self, state: dict[str, Any]) -> dict[str, Any]: ...


class AgentLambdaProxy:
    """Proxy for invoking the agent Lambda function asynchronously."""

    def __init__(self, function_name: str, region: str = "us-east-2") -> None:
        self.function_name = function_name
        self.region = region

    async def ainvoke(self, state: dict[str, Any]) -> dict[str, Any]:
        """Invoke the agent Lambda function asynchronously."""
        try:
            session = aioboto3.Session()
            async with session.client("lambda", region_name=self.region) as lambda_client:
                response = await lambda_client.invoke(
                    FunctionName=self.function_name,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(state).encode("utf-8"),
                )

                payload_bytes = await response["Payload"].read()
                lambda_response: dict[str, Any] = json.loads(payload_bytes.decode("utf-8"))

                if "body" in lambda_response:
                    result: dict[str, Any] = json.loads(lambda_response["body"])
                else:
                    result = lambda_response

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
                question_preview=state.get("question", "")[:50],
            )
            raise HTTPException(
                status_code=500,
                detail="Agent processing failed. Please try again later.",
            ) from e


def build_graph(
    agent_mode: str,
    function_name: str = "",
    region: str = "us-east-2",
) -> AgentGraphProtocol:
    """Build the agent graph or Lambda proxy (called once at startup).

    Args:
        agent_mode: "local" for direct import, "lambda" for Lambda proxy.
        function_name: Lambda function name (required when agent_mode="lambda").
        region: AWS region for Lambda invocation.

    Returns:
        Agent graph or proxy with ainvoke() method.

    Raises:
        RuntimeError: If agent cannot be initialized.
    """
    if agent_mode == "lambda":
        if not function_name:
            logger.error("Missing function name for Lambda mode", agent_mode=agent_mode)
            raise RuntimeError("AGENT_LAMBDA_FUNCTION_NAME must be set when AGENT_MODE=lambda")
        logger.info(
            "Agent graph: Lambda proxy",
            function_name=function_name,
            region=region,
        )
        return AgentLambdaProxy(function_name=function_name, region=region)

    # local mode
    try:
        from src.graph import graph

        logger.info("Agent graph: local import")
        return cast(AgentGraphProtocol, graph)
    except ImportError as e:
        logger.error("Failed to import local agent graph", error=str(e))
        raise RuntimeError("Agent graph not available. Ensure agent package is installed.") from e


def get_graph() -> AgentGraphProtocol:
    """Dependency stub — overridden by lifespan at startup."""
    raise RuntimeError("get_graph() called before lifespan wired the dependency")
