"""LangGraph state graph for Trip Assistant agent."""

from typing import cast

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

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
        START → classifier → router → [specialist] → END

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph with state schema
    workflow = StateGraph(TripAssistantState)

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
    workflow.add_edge(START, "classifier")

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
