"""Data schemas for the Trip Assistant agent.

This module contains all data structure definitions including:
- Type aliases (TopicCategory)
- Pydantic models (TopicClassification)
- TypedDicts (State and partial state updates)
"""

from typing import Literal, TypedDict

from pydantic import BaseModel, Field

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


class TopicClassification(BaseModel):
    """Structured output model for LLM question classification.

    Used with ChatOpenAI.with_structured_output() to ensure
    the classifier returns properly typed results.
    """

    category: TopicCategory = Field(
        description="The topic category of the question",
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0",
        ge=0.0,
        le=1.0,
    )


class ClassifierOutput(TypedDict):
    """Return type for classifier node (partial state update)."""

    category: TopicCategory
    confidence: float
    current_context: str


class SpecialistOutput(TypedDict):
    """Return type for specialist nodes (partial state update)."""

    answer: str
    source: str | None


class TripAssistantState(TypedDict):
    """Complete state for the Trip Assistant LangGraph agent.

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
