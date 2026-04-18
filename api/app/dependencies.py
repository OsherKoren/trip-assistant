"""Dependency injection for the agent graph.

Provides a build_graph() factory called once at startup and a get_graph()
stub that lifespan overrides via app.dependency_overrides.
Also provides streaming equivalents: build_stream_graph() and get_stream_graph().
"""

import json
from collections.abc import AsyncGenerator
from dataclasses import dataclass
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


# ---------------------------------------------------------------------------
# Streaming graph
# ---------------------------------------------------------------------------


@dataclass
class StreamDone:
    """Sentinel yielded as the last item from a stream graph, carrying the final agent state."""

    state: dict[str, Any]


class StreamGraphProtocol(Protocol):
    """Protocol for a streaming agent: yields text chunks then a StreamDone sentinel."""

    def astream(self, state: dict[str, Any]) -> AsyncGenerator[str | StreamDone, None]: ...


_NON_STREAMING_NODES: frozenset[str] = frozenset(
    {"classifier", "language_guard", "inject_documents"}
)


class LocalStreamGraph:
    """Streams tokens from the local LangGraph agent via astream_events.

    LLM token streaming produces tiny chunks (sometimes single characters).
    Without buffering, each token becomes a separate SSE event, causing
    character-by-character delivery to clients (e.g., "D", "a", "y", "4").
    This class buffers tokens before yielding to the client, dramatically
    reducing SSE event overhead and improving perceived latency.

    Uses ``astream_events(version="v2")`` and filters to specialist nodes only,
    skipping classifier/language_guard nodes whose LLM calls produce structured
    JSON tokens (not user-facing text).

    Yields text chunks then a StreamDone sentinel with the accumulated final
    state (category, confidence, answer, source).

    Reference: LangGraph astream_events v2 format and on_chat_model_stream events
    """

    def __init__(self, buffer_size: int = 100) -> None:
        """Initialize with configurable buffer size in characters."""
        self.buffer_size = buffer_size

    async def astream(self, state: dict[str, Any]) -> AsyncGenerator[str | StreamDone, None]:
        from src.graph import graph  # deferred to avoid import at startup

        captured: dict[str, Any] = {}
        # astream_events fires on_chat_model_stream at multiple chain levels for the
        # same LLM call, producing two separate run_ids with identical content.
        # Lock onto the first specialist run_id and skip all others.
        specialist_run_id: str | None = None
        buffer: list[str] = []

        async for event in graph.astream_events(state, version="v2"):
            kind = event.get("event", "")

            if kind == "on_chat_model_stream":
                node = event.get("metadata", {}).get("langgraph_node", "")
                if node in _NON_STREAMING_NODES:
                    continue
                run_id = event.get("run_id", "")
                if specialist_run_id is None:
                    specialist_run_id = run_id
                elif run_id != specialist_run_id:
                    continue  # skip duplicate stream from another chain level
                chunk = event["data"]["chunk"]
                if chunk.content:
                    buffer.append(chunk.content)
                    # Yield when buffer reaches configured size
                    if len("".join(buffer)) >= self.buffer_size:
                        yield "".join(buffer)
                        buffer = []

            elif kind == "on_chain_end":
                output = event["data"].get("output", {})
                if isinstance(output, dict):
                    captured.update(output)

        # Flush remaining buffer
        if buffer:
            yield "".join(buffer)

        yield StreamDone(captured)


class LambdaStreamGraph:
    """Lambda 'streaming': calls ainvoke normally and yields the full answer as a single chunk.

    Real token-by-token streaming across Lambda boundaries requires
    InvokeWithResponseStream (infra Phase 23). Until then, this collects
    the complete response first and emits it as one SSE event.
    """

    def __init__(self, proxy: AgentGraphProtocol) -> None:
        self._proxy = proxy

    async def astream(self, state: dict[str, Any]) -> AsyncGenerator[str | StreamDone, None]:
        result = await self._proxy.ainvoke(state)
        yield result.get("answer", "")
        yield StreamDone(result)


def build_stream_graph(
    agent_mode: str,
    graph: AgentGraphProtocol,
    buffer_size: int = 100,
) -> StreamGraphProtocol:
    """Build the streaming graph wrapper (called once at startup).

    Args:
        agent_mode: "local" for astream_events, "lambda" for single-chunk via ainvoke.
        graph: The already-built agent graph or Lambda proxy.
        buffer_size: Characters to buffer before yielding SSE chunks (default 100).

    Returns:
        StreamGraphProtocol implementation appropriate for the mode.
    """
    if agent_mode == "lambda":
        logger.info("Stream graph: Lambda proxy (single-chunk mode)")
        return LambdaStreamGraph(graph)

    logger.info("Stream graph: local astream_events", buffer_size=buffer_size)
    return LocalStreamGraph(buffer_size=buffer_size)


def get_stream_graph() -> StreamGraphProtocol:
    """Dependency stub — overridden by lifespan at startup."""
    raise RuntimeError("get_stream_graph() called before lifespan wired the dependency")
