# Node Patterns

## Table of Contents
- [Classifier Node](#classifier-node)
- [Specialist Node Template](#specialist-node-template)
- [Error Handling](#error-handling)
- [Document Context Integration](#document-context-integration)

---

## Classifier Node

The classifier analyzes user intent and sets the `topic` field for routing.

```python
# src/nodes/classifier.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from ..state import TripAssistantState

CLASSIFIER_PROMPT = """Analyze the user's question about their trip.
Classify into one of: flights, hotels, activities, restaurants, transportation, general

Respond with only the topic name."""

def classify_query(state: TripAssistantState) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    messages = [
        SystemMessage(content=CLASSIFIER_PROMPT),
        *state["messages"]
    ]
    
    response = llm.invoke(messages)
    topic = response.content.strip().lower()
    
    return {"topic": topic}
```

### Classifier with Structured Output (Preferred)

```python
from pydantic import BaseModel
from typing import Literal

class Classification(BaseModel):
    topic: Literal["flights", "hotels", "activities", "restaurants", "transportation", "general"]
    confidence: float

def classify_query(state: TripAssistantState) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(Classification)
    
    response = structured_llm.invoke([
        SystemMessage(content="Classify the trip question."),
        *state["messages"]
    ])
    
    return {"topic": response.topic}
```

---

## Specialist Node Template

Each specialist handles one topic with relevant document context.

```python
# src/nodes/flights_specialist.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from ..state import TripAssistantState
from ..documents import load_trip_docs

FLIGHTS_PROMPT = """You are a flight information specialist.
Use the following trip documents to answer questions about flights:

{context}

Be specific with times, flight numbers, and terminals."""

def handle_flights(state: TripAssistantState) -> dict:
    llm = ChatOpenAI(model="gpt-4o")
    docs = load_trip_docs()  # Or filter for flight-specific docs
    
    context = "\n\n".join(docs)
    
    messages = [
        SystemMessage(content=FLIGHTS_PROMPT.format(context=context)),
        *state["messages"]
    ]
    
    response = llm.invoke(messages)
    
    return {"messages": [response]}
```

---

## Error Handling

Wrap LLM calls for graceful failures:

```python
from langchain_core.messages import AIMessage

def handle_flights(state: TripAssistantState) -> dict:
    try:
        # ... LLM call
        return {"messages": [response]}
    except Exception as e:
        error_msg = AIMessage(content=f"Sorry, I couldn't retrieve flight information. Please try again.")
        return {"messages": [error_msg]}
```

---

## Document Context Integration

### Filter Documents by Topic

```python
# src/documents.py
from pathlib import Path

TOPIC_FILES = {
    "flights": ["flight_itinerary.txt", "airport_info.txt"],
    "hotels": ["hotel_booking.txt"],
    "activities": ["activities.txt", "tours.txt"],
}

def load_docs_for_topic(topic: str) -> list[str]:
    data_dir = Path(__file__).parent.parent / "data"
    files = TOPIC_FILES.get(topic, [])
    return [
        (data_dir / f).read_text() 
        for f in files 
        if (data_dir / f).exists()
    ]
```

### Use in Specialist

```python
def handle_flights(state: TripAssistantState) -> dict:
    docs = load_docs_for_topic("flights")
    context = "\n\n".join(docs)
    # ... rest of implementation
```
