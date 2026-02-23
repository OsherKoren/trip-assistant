"""Prompt templates for LLM nodes."""

# Specialist prompt template
# Used by all topic-specific specialists (flight, car_rental, etc.)
SPECIALIST_PROMPT_TEMPLATE = """Answer the following question about {topic} using only the provided context.

Context:
{context}

Question: {question}

Provide a clear, concise answer based on the context. If the context lists multiple options or alternatives, present ALL of them so the user can choose — do not pick one on their behalf. If the context doesn't contain the information, say so."""

# General prompt template
# Used by the general specialist for unclear/broad questions
GENERAL_PROMPT_TEMPLATE = """Answer the following question about a family trip to the French/Italian Alps.

Available information:
{context}

Question: {question}

Provide a helpful answer based on the available information. If the question is unclear or you need more details, ask for clarification."""

# Topic names for formatting specialist prompts
TOPICS = {
    "flight": "a flight",
    "car_rental": "car rental",
    "routes": "driving routes",
    "aosta": "the Aosta Valley itinerary",
    "chamonix": "the Chamonix itinerary",
    "annecy_geneva": "the Annecy and Geneva itinerary",
}
