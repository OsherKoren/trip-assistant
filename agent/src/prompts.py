"""Prompt templates for LLM nodes."""

# Specialist prompt template
# Used by all topic-specific specialists (flight, car_rental, etc.)
SPECIALIST_PROMPT_TEMPLATE = """Answer the following question about {topic} using only the provided context.

Trip timeline reference:
- Day 1: July 7 (arrival/car rental)
- Days 2-4: July 8-10 (Aosta Valley)
- Day 5: July 11 (travel day)
- Days 6-10: July 12-16 (Chamonix)
- Days 10-12: July 16-18 (Annecy)
- Day 13: July 19 (Annecy → Geneva)
- Day 14: July 20 (departure)

Use this mapping when the user asks about a specific day number or date.

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
