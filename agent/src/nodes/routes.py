"""Routes specialist node."""

from langchain_openai import ChatOpenAI

from src.prompts import SPECIALIST_PROMPT_TEMPLATE, TOPICS
from src.schemas import SpecialistOutput, TripAssistantState


def handle_routes(state: TripAssistantState) -> SpecialistOutput:
    """Answer route questions using current_context.

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
        topic=TOPICS["routes"],
        context=context,
        question=question,
    )

    # Generate answer
    response = llm.invoke(prompt)
    assert isinstance(response.content, str), "Expected string response from LLM"
    answer = response.content

    return {
        "answer": answer,
        "source": "routes_to_aosta.txt",
    }
