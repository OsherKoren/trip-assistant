"""LangGraph state graph for Trip Assistant agent."""

from typing import cast

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.nodes.annecy_geneva import handle_annecy_geneva
from src.nodes.aosta import handle_aosta
from src.nodes.car_rental import handle_car_rental
from src.nodes.chamonix import handle_chamonix
from src.nodes.classifier import classify_question
from src.nodes.flight import handle_flight
from src.nodes.general import handle_general
from src.nodes.routes import handle_routes
from src.schemas import TripAssistantState


def route_by_category(state: TripAssistantState) -> str:
    """Route to specialist node based on classified category.

    Args:
        state: Current agent state with category set by classifier

    Returns:
        Node name to route to (matches category)
    """
    return state["category"]


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
    workflow.add_node("flight", handle_flight)
    workflow.add_node("car_rental", handle_car_rental)
    workflow.add_node("routes", handle_routes)
    workflow.add_node("aosta", handle_aosta)
    workflow.add_node("chamonix", handle_chamonix)
    workflow.add_node("annecy_geneva", handle_annecy_geneva)
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


# Export compiled graph instance
graph = create_graph()
