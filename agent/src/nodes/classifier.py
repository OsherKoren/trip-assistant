"""Classifier node for topic-based question routing."""

from typing import cast

from langchain_openai import ChatOpenAI

from src.logger import logger
from src.schemas import (
    ClassifierOutput,
    TopicCategory,
    TopicClassification,
    TripAssistantState,
)

# Document key mapping for categories
CATEGORY_TO_DOCUMENT_KEY: dict[TopicCategory, str] = {
    "flight": "flight",
    "car_rental": "car_rental",
    "routes": "routes_to_aosta",
    "aosta": "aosta_valley",
    "chamonix": "chamonix",
    "annecy_geneva": "annecy_geneva",
    "general": "",  # General uses all documents or none
}


def classify_question(state: TripAssistantState) -> ClassifierOutput:
    """Classify question and set category + current_context.

    Uses GPT-4o-mini with structured output to classify the question
    into one of the predefined topic categories.

    Args:
        state: Current agent state with question and documents

    Returns:
        Updated state dict with category, confidence, and current_context set
    """
    question = state["question"]
    documents = state["documents"]

    # Initialize LLM with structured output
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(TopicClassification)

    # Classification prompt
    prompt = f"""Classify the following question about a family trip to the French/Italian Alps.

Available categories:
- flight: Questions about flight details (times, airline, etc.)
- car_rental: Questions about car rental pickup, location, details
- routes: Questions about driving routes to destinations
- aosta: Questions about Aosta Valley itinerary (July 8-11)
- chamonix: Questions about Chamonix itinerary (July 12-16)
- annecy_geneva: Questions about Annecy/Geneva itinerary (July 16-20)
- general: Unclear questions or general trip questions

Question: {question}

Classify this question and provide a confidence score (0.0-1.0)."""

    # Get classification from LLM with error handling
    try:
        classification = cast(TopicClassification, structured_llm.invoke(prompt))
    except Exception as e:
        logger.error(f"Classifier failed: {e}")
        # Fallback to general category with zero confidence
        classification = TopicClassification(category="general", confidence=0.0)

    # Get the relevant document content based on category
    doc_key = CATEGORY_TO_DOCUMENT_KEY[classification.category]
    current_context = documents.get(doc_key, "") if doc_key else ""

    # Return updated state
    return {
        "category": classification.category,
        "confidence": classification.confidence,
        "current_context": current_context,
    }
