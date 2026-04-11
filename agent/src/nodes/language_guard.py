"""Language guard node — rejects non-English input."""

import re

from src.logger import logger
from src.schemas import TripAssistantState

HEBREW_PATTERN = re.compile(r"[\u0590-\u05FF]")

UNSUPPORTED_LANGUAGE_MSG = (
    "I only answer questions in English. Please rephrase your question in English."
)


async def language_guard(state: TripAssistantState) -> dict[str, object]:
    """Detect Hebrew input and block with a fixed response.

    If the question contains Hebrew characters, sets `answer` immediately
    so the graph short-circuits to END without calling the classifier.

    Args:
        state: Current agent state with the user's question

    Returns:
        Partial state with `answer` set (blocked) or empty dict (pass-through)
    """
    question = state["question"]

    if HEBREW_PATTERN.search(question):
        logger.info("Language guard: rejected non-English (Hebrew) input")
        return {
            "answer": UNSUPPORTED_LANGUAGE_MSG,
            "category": "general",
            "confidence": 0.0,
        }

    return {}
