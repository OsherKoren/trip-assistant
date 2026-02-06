# Trip Assistant Agent

A LangGraph-powered conversational agent for answering questions about a family trip to the French/Italian Alps. The agent uses topic-based classification and routing to provide accurate, context-aware responses.

## Features

- 🎯 **Topic Classification** - Automatically identifies query topics (flights, car rental, routes, activities)
- 🧭 **Smart Routing** - Routes questions to specialized nodes based on classified topic
- 🛡️ **Error Resilience** - Graceful degradation with user-friendly error messages on API failures
- 🏭 **Factory Pattern** - Consistent specialist node generation reducing code duplication by 57%
- 🧪 **Comprehensive Testing** - 61 unit tests + 15 integration tests with full error coverage
- 📝 **Type Safety** - Full type hints with mypy validation

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (for LLM calls)

### Installation

1. **Clone and navigate to the agent directory:**
   ```bash
   cd agent/
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

### Basic Usage

```python
from src.graph import graph
from src.documents import load_documents

# Initialize state with question and documents
state = {
    "question": "What time is our flight?",
    "category": "general",
    "confidence": 0.0,
    "documents": load_documents(),
    "current_context": "",
    "answer": "",
    "source": None,
}

# Run the agent
result = graph.invoke(state)

print(f"Category: {result['category']}")
print(f"Answer: {result['answer']}")
print(f"Source: {result['source']}")
```

## Architecture

### Graph Flow

```
START → Classifier → Router → [Specialist] → END
```

1. **Classifier** - Uses GPT-4o-mini to classify the question into a topic category
2. **Router** - Routes to the appropriate specialist based on category
3. **Specialist** - Generates answer using relevant document context

### Specialist Topics

| Topic | Source Document | Example Questions |
|-------|----------------|-------------------|
| **flight** | flight.txt | "What time is our flight?", "Which airline?" |
| **car_rental** | car_rental.txt | "Where do we pick up the car?" |
| **routes** | routes_to_aosta.txt | "How do we get to Aosta?" |
| **aosta** | aosta_valley.txt | "What's planned for July 9?" |
| **chamonix** | chamonix.txt | "Tell me about Lac Blanc hike" |
| **annecy_geneva** | annecy_geneva.txt | "Paragliding information?" |
| **general** | All documents | Unclear or broad questions |

### Factory Pattern

All specialist nodes are generated using the factory pattern:

```python
# From src/nodes/__init__.py
from src.nodes.specialist_factory import create_specialist

handle_flight = create_specialist("flight", "flight.txt")
handle_car_rental = create_specialist("car_rental", "car_rental.txt")
# ... other specialists
```

**Benefits:**
- Consistent error handling across all specialists
- Reduced code duplication (57% less code)
- Easy to add new specialists (just one line!)

## Testing

### Run All Tests

```bash
# Unit tests only (fast, no API calls)
pytest tests/ -v -m "not integration"

# Integration tests (requires OPENAI_API_KEY)
pytest tests/integration/ -v

# All tests
pytest tests/ -v
```

### Test Coverage

- **61 unit tests** - Mocked LLM responses, no API costs
- **15 integration tests** - Real OpenAI API calls (~$0.01-0.10 per run)
- **12 error handling tests** - Comprehensive failure scenario coverage

### Test Organization

```
tests/
├── conftest.py                    # Shared fixtures
├── test_error_handling.py         # Error handling tests
├── test_graph.py                  # Graph assembly tests
├── test_documents.py              # Document loading tests
├── test_state.py                  # State schema tests
├── nodes/
│   ├── test_classifier.py         # Classifier tests
│   └── test_specialists.py        # Specialist tests
└── integration/
    ├── test_classifier_integration.py
    └── test_graph_integration.py
```

## Error Handling

The agent includes comprehensive error handling for production reliability:

### Classifier Errors
- Falls back to `"general"` category with 0.0 confidence
- Logs error with context for debugging
- User sees general specialist response

### Specialist Errors
- Returns user-friendly error message
- Preserves source field for tracking
- Logs error without exposing internals

### Routing Errors
- Falls back to general specialist if category is `None`
- Logs warning when fallback occurs

**Example error message:**
```
"Sorry, I couldn't retrieve flight information right now. Please try again."
```

## Development

### Code Quality

```bash
# Run all quality checks
pre-commit run --all-files

# Individual checks
mypy src/                # Type checking
ruff check src/          # Linting
ruff format src/         # Formatting
```

### Adding a New Specialist

1. Add document to `data/new_topic.txt`
2. Add topic to `TopicCategory` in `src/schemas.py`
3. Add topic name to `TOPICS` dict in `src/prompts.py`
4. Create specialist in `src/nodes/__init__.py`:
   ```python
   handle_new_topic = create_specialist("new_topic", "new_topic.txt")
   ```
5. Add node to graph in `src/graph.py`
6. Write tests in `tests/nodes/test_specialists.py`

### Project Structure

```
agent/
├── src/
│   ├── state.py              # TripAssistantState TypedDict
│   ├── schemas.py            # Pydantic models and types
│   ├── documents.py          # Document loading
│   ├── prompts.py            # LLM prompt templates
│   ├── graph.py              # Main graph definition
│   ├── logger.py             # Logging configuration
│   └── nodes/
│       ├── classifier.py           # Topic classification
│       ├── general.py              # General specialist
│       └── specialist_factory.py   # Specialist factory
├── data/                     # Trip documents (6 txt files)
├── tests/                    # Test suite
├── .env.example              # Environment template
├── pyproject.toml            # Dependencies and config
├── CLAUDE.md                 # Detailed developer docs
├── CHANGELOG.md              # Version history
└── README.md                 # This file
```

## Dependencies

### Core
- **langgraph** >= 1.0 - Graph orchestration framework
- **langchain-openai** - OpenAI LLM integration
- **pydantic** - Data validation

### Development
- **pytest** - Testing framework
- **mypy** - Type checking
- **ruff** - Linting and formatting
- **pre-commit** - Git hooks for quality checks

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM calls |

## Performance

- **Classification**: ~1-2 seconds (GPT-4o-mini)
- **Answer generation**: ~2-4 seconds (GPT-4o-mini)
- **Total query time**: ~3-6 seconds end-to-end
- **Cost per query**: ~$0.001-0.003 (using gpt-4o-mini)

## Configuration

### Model Selection

Change models in `src/nodes/classifier.py` and `src/nodes/specialist_factory.py`:

```python
# Classifier (fast classification)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Specialist factory (quality answers)
def create_specialist(..., model: str = "gpt-4o-mini"):
    llm = ChatOpenAI(model=model, temperature=0)
```

**Model options:**
- `gpt-4o-mini` - Fast, cheap, good quality (recommended)
- `gpt-4o` - Best quality, slower, more expensive
- `gpt-3.5-turbo` - Fastest, cheapest, lower quality

## Troubleshooting

### "Module not found" errors
```bash
pip install -e .  # Install in editable mode
```

### "OPENAI_API_KEY not set"
```bash
# Add to .env file
echo "OPENAI_API_KEY=sk-..." > .env
```

### Integration tests skipped
```bash
# Set API key in environment
export OPENAI_API_KEY=sk-...
pytest tests/integration/ -v
```

### Type errors with mypy
```bash
# Some LangGraph types use type: ignore comments
# This is normal for dynamically generated functions
mypy src/  # Should pass with type: ignore annotations
```

## Contributing

1. Read `CLAUDE.md` for detailed development guidelines
2. Follow TDD workflow (write tests first)
3. Run quality checks before committing
4. Update `CHANGELOG.md` for notable changes
5. Work on feature branches (never commit to main)

## Documentation

- **README.md** (this file) - Quick start and overview
- **CLAUDE.md** - Detailed developer documentation
- **CHANGELOG.md** - Version history and changes
- **docs/** - Architecture and data model docs (in root)

## License

[Your License Here]

## Support

For questions or issues:
- Check `CLAUDE.md` for detailed documentation
- Review test files for usage examples
- See `CHANGELOG.md` for recent changes

---

**Built with** [LangGraph](https://langchain-ai.github.io/langgraph/) • **Powered by** OpenAI GPT-4o-mini
