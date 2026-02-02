"""Routes specialist node."""

from langchain_openai import ChatOpenAI

from src.state import TripAssistantState


def handle_routes(state: TripAssistantState) -> dict:
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

    # Create prompt with context
    prompt = f"""Answer the following question about driving routes using only the provided context.

Context:
{context}

Question: {question}

Provide a clear, concise answer based on the context. If the context doesn't contain the information, say so."""

    # Generate answer
    response = llm.invoke(prompt)
    answer = response.content

    return {
        "answer": answer,
        "source": "routes_to_aosta.txt",
    }
