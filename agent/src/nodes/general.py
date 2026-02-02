"""General specialist node for unclear questions."""

from langchain_openai import ChatOpenAI

from src.state import TripAssistantState


def handle_general(state: TripAssistantState) -> dict:
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

    # Create prompt with all documents
    prompt = f"""Answer the following question about a family trip to the French/Italian Alps.

Available information:
{all_context}

Question: {question}

Provide a helpful answer based on the available information. If the question is unclear or you need more details, ask for clarification."""

    # Generate answer
    response = llm.invoke(prompt)
    answer = response.content

    return {
        "answer": answer,
        "source": None,
    }
