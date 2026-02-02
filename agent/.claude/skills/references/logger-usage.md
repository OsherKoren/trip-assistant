# Logger Usage Examples

Using loguru for debugging the trip assistant agent.

## Import

```python
from src.logger import logger
```

## Basic Usage

### In Classifier Node

```python
# src/nodes/classifier.py
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from ..logger import logger
from ..state import TripAssistantState


def classify_query(state: TripAssistantState) -> dict:
    """Classify user query into topic categories."""
    logger.info("Classifier node invoked")

    user_message = state["messages"][-1].content
    logger.debug("User query: {query}", query=user_message)

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        messages = [
            SystemMessage(content="Classify the trip question."),
            *state["messages"]
        ]

        logger.debug("Sending {count} messages to LLM", count=len(messages))
        response = llm.invoke(messages)

        topic = response.content.strip().lower()
        logger.info("Classified topic: {topic}", topic=topic)

        return {"topic": topic}

    except Exception as e:
        logger.error("Classification failed: {error}", error=str(e))
        logger.exception("Full traceback:")
        return {"topic": "general"}
```

### In Specialist Node

```python
# src/nodes/flights_specialist.py
from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..documents import load_docs_for_topic
from ..logger import logger
from ..state import TripAssistantState


def handle_flights(state: TripAssistantState) -> dict:
    """Handle flight-related queries."""
    logger.info("Flights specialist invoked")

    try:
        # Load documents
        docs = load_docs_for_topic("flights")
        logger.debug("Loaded {count} flight documents", count=len(docs))

        if not docs:
            logger.warning("No flight documents found!")

        context = "\n\n".join(docs)
        logger.debug("Context length: {length} chars", length=len(context))

        # Call LLM
        llm = ChatOpenAI(model="gpt-4o")
        messages = [
            SystemMessage(content=f"Use this context:\n{context}"),
            *state["messages"]
        ]

        logger.debug("Calling LLM with {count} messages", count=len(messages))
        response = llm.invoke(messages)

        logger.info("Response generated: {preview}...",
                   preview=response.content[:50])

        return {"messages": [response]}

    except Exception as e:
        logger.error("Flights specialist error: {error}", error=str(e))
        logger.exception("Full traceback:")
        error_msg = AIMessage(content="Sorry, couldn't retrieve flight info.")
        return {"messages": [error_msg]}
```

### In Graph

```python
# src/graph.py
from langgraph.graph import END, START, StateGraph

from .logger import logger
from .nodes.classifier import classify_query
from .state import TripAssistantState


def route_by_topic(state: TripAssistantState) -> str:
    """Route to specialist based on topic."""
    topic = state["topic"]
    logger.info("Routing to: {topic}", topic=topic)
    return topic


# Build graph
logger.info("Building LangGraph...")
graph = StateGraph(TripAssistantState)

graph.add_node("classifier", classify_query)
# ... add other nodes

graph.add_edge(START, "classifier")
# ... add other edges

logger.info("Compiling graph...")
app = graph.compile()
logger.info("Graph ready!")
```

### In Documents Module

```python
# src/documents.py
from pathlib import Path

from .logger import logger

DATA_DIR = Path(__file__).parent.parent / "data"


def load_trip_docs() -> list[str]:
    """Load all trip documents."""
    logger.info("Loading trip documents from {path}", path=DATA_DIR)

    docs = []
    for file_path in DATA_DIR.glob("*.txt"):
        logger.debug("Reading {file}", file=file_path.name)
        try:
            content = file_path.read_text()
            docs.append(content)
            logger.debug("Loaded {file}: {size} bytes",
                        file=file_path.name,
                        size=len(content))
        except Exception as e:
            logger.error("Failed to read {file}: {error}",
                        file=file_path.name,
                        error=str(e))

    logger.info("Loaded {count} documents", count=len(docs))
    return docs


def load_docs_for_topic(topic: str) -> list[str]:
    """Load documents for a specific topic."""
    logger.debug("Loading documents for topic: {topic}", topic=topic)

    topic_files = {
        "flights": ["flight.txt"],
        "hotels": ["annecy_geneva.txt", "aosta_valley.txt"],
        "activities": ["chamonix.txt"],
    }

    files = topic_files.get(topic, [])
    logger.debug("Topic {topic} has {count} files", topic=topic, count=len(files))

    docs = []
    for filename in files:
        file_path = DATA_DIR / filename
        if file_path.exists():
            docs.append(file_path.read_text())
            logger.debug("Loaded {file}", file=filename)
        else:
            logger.warning("File not found: {file}", file=filename)

    return docs
```

## Log Levels

```python
# Different severity levels
logger.debug("Detailed info for debugging")      # Only in DEBUG mode
logger.info("General information")                # Default level
logger.warning("Warning - something unexpected")  # Warnings
logger.error("Error occurred")                    # Errors
logger.exception("Error with traceback")          # Auto-includes traceback
```

## Structured Logging

```python
# Good - structured with context
logger.info("Classified query", topic="flights", confidence=0.95)
logger.debug("State update", topic=topic, message_count=len(state["messages"]))

# Also good - using format strings
logger.info("Classified topic: {topic}", topic=topic)
logger.debug("Processing {count} messages", count=len(messages))
```

## Enable DEBUG Mode

To see more detailed logs, edit `src/logger.py` and uncomment the DEBUG section:

```python
# Change level from "INFO" to "DEBUG"
logger.add(
    sys.stderr,
    format=(...),
    level="DEBUG",  # Changed from "INFO"
    colorize=True,
)
```

## Console Output Example

```
2026-02-02 13:45:23 | INFO     | src.graph:build_graph:12 | Building LangGraph...
2026-02-02 13:45:23 | INFO     | src.graph:build_graph:20 | Compiling graph...
2026-02-02 13:45:23 | INFO     | src.graph:build_graph:22 | Graph ready!
2026-02-02 13:45:25 | INFO     | src.nodes.classifier:classify_query:15 | Classifier node invoked
2026-02-02 13:45:25 | DEBUG    | src.nodes.classifier:classify_query:18 | User query: What time is my flight?
2026-02-02 13:45:26 | INFO     | src.nodes.classifier:classify_query:28 | Classified topic: flights
2026-02-02 13:45:26 | INFO     | src.graph:route_by_topic:8 | Routing to: flights
2026-02-02 13:45:26 | INFO     | src.nodes.flights_specialist:handle_flights:12 | Flights specialist invoked
2026-02-02 13:45:26 | DEBUG    | src.nodes.flights_specialist:handle_flights:16 | Loaded 1 flight documents
```

## Tips

1. **Use structured logging** - Pass variables as keyword arguments
2. **Log at entry points** - Start of each node function
3. **Log important decisions** - Classification results, routing decisions
4. **Log errors with context** - Include relevant state information
5. **Use appropriate levels** - DEBUG for details, INFO for flow, ERROR for problems
6. **Don't log sensitive data** - Be careful with user messages containing PII
