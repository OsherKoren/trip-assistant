# Data Model

## Agent State

```python
class TripAssistantState(TypedDict):
    question: str
    category: TopicCategory
    confidence: float
    documents: dict[str, str]
    current_context: str
    answer: str
    source: str | None
```

## Documents

```
agent/data/
├── flight.txt
├── car_rental.txt
├── routes_to_aosta.txt
├── aosta_valley.txt
├── chamonix.txt
├── annecy_geneva.txt
└── files/
    └── car_rental_voucher.pdf
```

## API

**POST /api/messages**

Request: `{"question": "..."}`

Response: `{"answer": "...", "category": "...", "confidence": 0.95, "source": "..."}`
