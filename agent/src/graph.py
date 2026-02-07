"""LangGraph state graph for Trip Assistant agent."""

from typing import cast

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.documents import load_documents
from src.logger import logger
from src.nodes import (
    classify_question,
    handle_annecy_geneva,
    handle_aosta,
    handle_car_rental,
    handle_chamonix,
    handle_flight,
    handle_general,
    handle_routes,
)
from src.schemas import TripAssistantState

# Load documents once at module level (cached for process lifetime)
_documents = load_documents()


def inject_documents(_state: TripAssistantState) -> dict[str, dict[str, str]]:
    """Inject cached documents into state.

    Documents are loaded once at module import and reused for every request.
    This decouples callers from document loading — they only need to pass
    {"question": "..."} to invoke the graph.

    Args:
        _state: Current agent state (unused, documents come from cache)

    Returns:
        Partial state update with cached documents
    """
    return {"documents": _documents}


def route_by_category(state: TripAssistantState) -> str:
    """Route to specialist node based on classified category.

    Args:
        state: Current agent state with category set by classifier

    Returns:
        Node name to route to (matches category, defaults to "general")
    """
    category = state.get("category")

    if category is None:
        logger.warning("No category set by classifier, routing to general")
        return "general"

    return category


def create_graph() -> CompiledStateGraph[
    TripAssistantState, None, TripAssistantState, TripAssistantState
]:
    """Create and compile the Trip Assistant graph.

    Graph flow:
        START → inject_documents → classifier → router → [specialist] → END

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph with state schema
    workflow = StateGraph(TripAssistantState)

    # Add entry node to inject cached documents
    workflow.add_node("inject_documents", inject_documents)  # type: ignore[call-overload]

    # Add classifier node
    workflow.add_node("classifier", classify_question)

    # Add all specialist nodes
    # Factory-generated specialists have dynamic types, so we need type: ignore
    workflow.add_node("flight", handle_flight)  # type: ignore[arg-type]
    workflow.add_node("car_rental", handle_car_rental)  # type: ignore[arg-type]
    workflow.add_node("routes", handle_routes)  # type: ignore[arg-type]
    workflow.add_node("aosta", handle_aosta)  # type: ignore[arg-type]
    workflow.add_node("chamonix", handle_chamonix)  # type: ignore[arg-type]
    workflow.add_node("annecy_geneva", handle_annecy_geneva)  # type: ignore[arg-type]
    workflow.add_node("general", handle_general)

    # Add edges
    workflow.add_edge(START, "inject_documents")
    workflow.add_edge("inject_documents", "classifier")

    # Conditional routing based on category
    workflow.add_conditional_edges("classifier", route_by_category)

    # All specialists go to END
    for node_name in [
        "flight",
        "car_rental",
        "routes",
        "aosta",
        "chamonix",
        "annecy_geneva",
        "general",
    ]:
        workflow.add_edge(node_name, END)

    return cast(
        CompiledStateGraph[TripAssistantState, None, TripAssistantState, TripAssistantState],
        workflow.compile(),
    )


graph = create_graph()
