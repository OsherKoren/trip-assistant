"""Flight specialist node."""

from langchain_openai import ChatOpenAI

from src.prompts import SPECIALIST_PROMPT_TEMPLATE, TOPICS
from src.state import TripAssistantState


def handle_flight(state: TripAssistantState) -> dict:
    """Answer flight-related questions using current_context.

    Args:
        state: Current agent state with question and current_context

    Returns:
        Updated state dict with answer and source
    """
    question = state["question"]
    context = state["current_context"]

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create prompt from template
    prompt = SPECIALIST_PROMPT_TEMPLATE.format(
        topic=TOPICS["flight"],
        context=context,
        question=question,
    )

    # Generate answer
    response = llm.invoke(prompt)
    answer = response.content

    return {
        "answer": answer,
        "source": "flight.txt",
    }
