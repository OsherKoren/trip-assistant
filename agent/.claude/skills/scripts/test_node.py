#!/usr/bin/env python3
"""Quick test runner for trip-assistant agent nodes.

Usage:
    python .claude/skills/scripts/test_node.py classifier "What time is my flight?"
    python .claude/skills/scripts/test_node.py flights "Tell me about my flight"
    python .claude/skills/scripts/test_node.py graph "What's my hotel address?"
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from langchain_core.messages import HumanMessage


def test_classifier(query: str):
    """Test classifier node with a query."""
    from nodes.classifier import classify_query

    state = {"messages": [HumanMessage(content=query)], "topic": None}
    result = classify_query(state)
    print(f"Query: {query}")
    print(f"Classified topic: {result['topic']}")
    return result


def test_specialist(topic: str, query: str):
    """Test a specialist node directly."""
    # Dynamic import based on topic
    module = __import__(f"nodes.{topic}_specialist", fromlist=["handle_" + topic])
    handler = getattr(module, f"handle_{topic}")

    state = {"messages": [HumanMessage(content=query)], "topic": topic}
    result = handler(state)
    print(f"Query: {query}")
    print(f"Response: {result['messages'][-1].content}")
    return result


def test_full_graph(query: str):
    """Test the full graph end-to-end."""
    from graph import app

    result = app.invoke({"messages": [HumanMessage(content=query)], "topic": None})
    print(f"Query: {query}")
    print(f"Classified topic: {result['topic']}")
    print(f"Response: {result['messages'][-1].content}")
    return result


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    node_type = sys.argv[1]
    query = sys.argv[2]

    if node_type == "classifier":
        test_classifier(query)
    elif node_type == "graph":
        test_full_graph(query)
    elif node_type in [
        "flights",
        "hotels",
        "activities",
        "restaurants",
        "transportation",
        "general",
    ]:
        test_specialist(node_type, query)
    else:
        print(f"Unknown node type: {node_type}")
        print(
            "Valid options: classifier, graph, flights, hotels, activities, restaurants, transportation, general"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
