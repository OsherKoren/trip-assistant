"""LangGraph state graph for Trip Assistant agent."""

from collections.abc import AsyncGenerator

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
    language_guard,
)
from src.schemas import TopicCategory, TripAssistantState

# Load documents once at module level (cached for process lifetime)
_documents = load_documents()


def inject_documents(state: TripAssistantState) -> dict[str, object]:
    """Inject cached documents and default history into state.

    Documents are loaded once at module import and reused for every request.
    History defaults to empty list for backward compatibility.

    Args:
        state: Current agent state (history may or may not be set)

    Returns:
        Partial state update with cached documents and defaulted history
    """
    result: dict[str, object] = {"documents": _documents}
    if "history" not in state:
        result["history"] = []
    return result


def route_after_language_guard(state: TripAssistantState) -> str:
    """Route to END if language guard blocked the request, else to classifier.

    Args:
        state: Current agent state (answer is set if language was blocked)

    Returns:
        "blocked" if answer was set by language guard, "pass" otherwise
    """
    return "blocked" if state.get("answer") else "pass"


def route_by_category(state: TripAssistantState) -> TopicCategory:
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
        START → language_guard → inject_documents → classifier → router → [specialist] → END
        language_guard short-circuits to END for non-English (Hebrew) input

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph with state schema
    workflow: StateGraph[TripAssistantState, None, TripAssistantState, TripAssistantState] = (
        StateGraph(TripAssistantState)
    )

    # Add language guard node (rejects non-English input before any processing)
    workflow.add_node("language_guard", language_guard)

    # Add entry node to inject cached documents
    workflow.add_node("inject_documents", inject_documents)

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
    workflow.add_edge(START, "language_guard")
    workflow.add_conditional_edges(
        "language_guard",
        route_after_language_guard,
        {"blocked": END, "pass": "inject_documents"},
    )
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

    return workflow.compile()


graph = create_graph()


async def stream_agent(state: TripAssistantState) -> AsyncGenerator[str, None]:
    """Stream token chunks from the agent as they are generated.

    Args:
        state: Initial agent state (requires at minimum {"question": "..."})

    Yields:
        Text deltas from the LLM as they are produced
    """
    async for event in graph.astream_events(state, version="v2"):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content:
                yield chunk.content
