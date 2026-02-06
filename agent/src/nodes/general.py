"""General specialist node for unclear questions."""

from langchain_openai import ChatOpenAI

from src.logger import logger
from src.prompts import GENERAL_PROMPT_TEMPLATE
from src.schemas import SpecialistOutput, TripAssistantState


def handle_general(state: TripAssistantState) -> SpecialistOutput:
    """Answer general questions or ask for clarification.

    For general questions, uses all available documents or asks for clarification
    if the question is too vague.

    Args:
        state: Current agent state with question and documents

    Returns:
        Updated state dict with answer and source
    """
    question = state["question"]
    documents = state["documents"]

    # Combine all documents for context
    all_context = "\n\n".join([f"=== {name} ===\n{content}" for name, content in documents.items()])

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create prompt from template
    prompt = GENERAL_PROMPT_TEMPLATE.format(
        context=all_context,
        question=question,
    )

    # Generate answer with error handling
    try:
        response = llm.invoke(prompt)
        assert isinstance(response.content, str), "Expected string response from LLM"
        answer = response.content
    except Exception as e:
        logger.error(f"General specialist failed: {e}")
        answer = (
            "Sorry, I couldn't process your question right now. "
            "Please try rephrasing or asking something more specific."
        )

    return {
        "answer": answer,
        "source": None,
    }
