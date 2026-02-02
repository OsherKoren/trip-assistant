"""State definitions for the Trip Assistant agent."""

from typing import Literal, TypedDict

# Topic categories for question classification
TopicCategory = Literal[
    "flight",
    "car_rental",
    "routes",
    "aosta",
    "chamonix",
    "annecy_geneva",
    "general",
]


class TripAssistantState(TypedDict):
    """State for the Trip Assistant LangGraph agent.

    Attributes:
        question: User's question about the trip
        category: Classified topic category
        confidence: Classification confidence score (0.0 - 1.0)
        documents: All loaded trip documents
        current_context: Relevant document content for the current question
        answer: Generated answer to the question
        source: Source document filename (e.g., "flight.txt") or None
    """

    question: str
    category: TopicCategory
    confidence: float
    documents: dict[str, str]
    current_context: str
    answer: str
    source: str | None
