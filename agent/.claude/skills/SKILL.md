---
name: trip-agent
description: |
  Build and modify the Trip Assistant LangGraph agent with topic-based routing.
  Use when: (1) Adding or modifying classifier/specialist nodes, (2) Updating 
  TripAssistantState schema, (3) Changing graph routing logic, (4) Adding new 
  trip topics/specialists, (5) Working with document loading, (6) Writing or 
  debugging tests for nodes or graph, (7) Any task involving the agent/ folder.
---

# Trip Assistant Agent Development

## Architecture

```
START → Classifier → Router → [Specialist Nodes] → END
```

The classifier analyzes user queries and routes to topic-specific specialist nodes.

## Core Patterns

### State Schema (`src/state.py`)
```python
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class TripAssistantState(TypedDict):
    messages: Annotated[list, add_messages]
    topic: Literal["flights", "hotels", "activities", ...] | None
    # Add fields as needed for routing context
```

### Graph Structure (`src/graph.py`)
```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(TripAssistantState)
graph.add_node("classifier", classify_query)
graph.add_node("flights_specialist", handle_flights)
graph.add_node("hotels_specialist", handle_hotels)
# ... other specialists

graph.add_edge(START, "classifier")
graph.add_conditional_edges("classifier", route_by_topic, {
    "flights": "flights_specialist",
    "hotels": "hotels_specialist",
    # ... other routes
})
graph.add_edge("flights_specialist", END)
# ... other edges to END

app = graph.compile()
```

### Routing Function
```python
def route_by_topic(state: TripAssistantState) -> str:
    return state["topic"]  # Returns node name based on classified topic
```

## Adding a New Specialist

1. Create node function in `src/nodes/<topic>_specialist.py`
2. Add topic to `TripAssistantState.topic` Literal type
3. Register node in `graph.py`: `graph.add_node("<topic>_specialist", handler)`
4. Add routing edge: `"<topic>": "<topic>_specialist"`
5. Add edge to END: `graph.add_edge("<topic>_specialist", END)`
6. Write tests first (TDD)

## Document Loading (`src/documents.py`)

Trip data lives in `data/*.txt`. Load documents for RAG context:
```python
from pathlib import Path

def load_trip_docs() -> list[str]:
    data_dir = Path(__file__).parent.parent / "data"
    return [f.read_text() for f in data_dir.glob("*.txt")]
```

## Testing (TDD Required)

Always write tests first:
```python
# tests/test_<node_name>.py
def test_classifier_routes_flight_query():
    state = {"messages": [HumanMessage(content="What time is my flight?")]}
    result = classify_query(state)
    assert result["topic"] == "flights"
```

Run: `pytest tests/ -v`

## References

- **Node patterns**: See [references/node-patterns.md](references/node-patterns.md) for classifier and specialist implementation details
- **Testing patterns**: See [references/testing-patterns.md](references/testing-patterns.md) for TDD patterns and fixtures

## Quality Checks

Before committing:
```bash
pre-commit run --all-files
mypy src/
pytest tests/ -v
```
