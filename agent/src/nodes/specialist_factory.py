"""Factory for creating specialist nodes with consistent behavior."""

from collections.abc import Callable
from typing import Any

from langchain_openai import ChatOpenAI

from src.logger import logger
from src.prompts import SPECIALIST_PROMPT_TEMPLATE, TOPICS
from src.schemas import TopicCategory, TripAssistantState


def create_specialist(
    category: TopicCategory,
    source_file: str,
    model: str = "gpt-4o-mini",
) -> Callable[[TripAssistantState], dict[str, Any]]:
    """Factory function to create specialist nodes with consistent behavior.

    All specialists follow the same pattern:
    1. Extract question and context from state
    2. Format prompt using template
    3. Call LLM with error handling
    4. Return answer and source

    Args:
        category: Topic category for this specialist (e.g., "flight", "car_rental")
        source_file: Source document filename (e.g., "flight.txt")
        model: OpenAI model to use (default: gpt-4o-mini)

    Returns:
        Specialist node function with proper error handling
    """

    def specialist_node(state: TripAssistantState) -> dict[str, Any]:
        """Answer questions using current_context.

        Args:
            state: Current agent state with question and current_context

        Returns:
            Updated state dict with answer and source
        """
        question = state["question"]
        context = state["current_context"]

        llm = ChatOpenAI(model=model, temperature=0)

        prompt = SPECIALIST_PROMPT_TEMPLATE.format(
            topic=TOPICS[category],
            context=context,
            question=question,
        )

        try:
            response = llm.invoke(prompt)
            assert isinstance(response.content, str), "Expected string response from LLM"
            answer = response.content
        except Exception as e:
            logger.error(f"{category.title()} specialist failed: {e}")
            answer = (
                f"Sorry, I couldn't retrieve {TOPICS[category]} information right now. "
                "Please try again."
            )

        return {
            "answer": answer,
            "source": source_file,
        }

    # Set function metadata for debugging and introspection
    specialist_node.__name__ = f"handle_{category}"
    specialist_node.__doc__ = f"""Answer {TOPICS[category]} questions using current_context."""

    return specialist_node
