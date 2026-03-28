"""General specialist node for unclear questions."""

from langchain_openai import ChatOpenAI

from src.logger import logger
from src.prompts import GENERAL_PROMPT_TEMPLATE, format_history
from src.schemas import SpecialistOutput, TripAssistantState

# Module-level LLM instance (created once per process/Lambda container)
_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


async def handle_general(state: TripAssistantState) -> SpecialistOutput:
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
    history = state.get("history", [])

    # Combine all documents for context
    all_context = "\n\n".join([f"=== {name} ===\n{content}" for name, content in documents.items()])

    # Create prompt from template
    prompt = GENERAL_PROMPT_TEMPLATE.format(
        context=all_context,
        history=format_history(history),
        question=question,
    )

    # Generate answer with error handling
    try:
        response = await _llm.ainvoke(prompt)
        if not isinstance(response.content, str):
            raise ValueError(f"Unexpected LLM response type: {type(response.content)}")
        answer = response.content
    except Exception as e:
        logger.exception("General specialist failed", error=str(e))
        answer = (
            "Sorry, I couldn't process your question right now. "
            "Please try rephrasing or asking something more specific."
        )

    return {
        "answer": answer,
        "source": None,
    }
