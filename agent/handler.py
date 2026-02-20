"""AWS Lambda handler for the Trip Assistant agent.

Fetches the OpenAI API key from SSM Parameter Store on first invocation
(cached per Lambda container), then delegates to the LangGraph graph.
"""

import json
import os
from typing import Any

import boto3

_graph = None
PING_SENTINEL = "__ping__"


def _get_graph():
    """Lazily initialize the graph (cold start only).

    Fetches the API key from SSM and imports the graph on first call.
    Subsequent calls return the cached graph instance.
    """
    global _graph  # noqa: PLW0603
    if _graph is not None:
        return _graph

    parameter_name = os.environ.get("SSM_PARAMETER_NAME", "")
    if parameter_name and "OPENAI_API_KEY" not in os.environ:
        ssm = boto3.client("ssm")
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        os.environ["OPENAI_API_KEY"] = response["Parameter"]["Value"]

    from src.graph import graph

    _graph = graph
    return _graph


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:  # noqa: ARG001
    """Lambda entry point for the agent.

    Args:
        event: Lambda event with "question" field
        context: Lambda context (unused)

    Returns:
        JSON response with answer and metadata
    """
    body = event if "question" in event else json.loads(event.get("body", "{}"))
    question = body.get("question", "")

    if not question:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'question' field"}),
        }

    if question == PING_SENTINEL:
        _get_graph()  # validate cold start (SSM + LangGraph init)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "answer": "pong",
                    "category": "ping",
                    "confidence": 1.0,
                    "source": None,
                }
            ),
        }

    graph = _get_graph()
    result = graph.invoke({"question": question})

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "answer": result.get("answer", ""),
                "category": result.get("category", ""),
                "confidence": result.get("confidence", 0.0),
                "source": result.get("source"),
            }
        ),
    }
