# SOLID Principles — Python Quick Reference

> SOLID originated in OOP, but the underlying ideas apply equally to functions, modules, and closures. Each section below covers **both paradigms**.

## Single Responsibility Principle (SRP)

> A class **or function** should have only one reason to change.

### Checklist
- [ ] Each class has one clear responsibility
- [ ] Each function does one thing (single level of abstraction)
- [ ] Class name describes its single purpose (no "Manager", "Handler", "Utils" grab-bags)
- [ ] Function name is a specific verb (not `process_data`, `handle_stuff`)
- [ ] Methods in a class all relate to the same concern
- [ ] Changes to one feature don't require modifying unrelated classes or functions
- [ ] Modules (files) are focused on one domain area

### OOP Smell
```python
# Bad — handles parsing, validation, AND persistence
class ReportProcessor:
    def parse(self, raw: str) -> dict: ...
    def validate(self, data: dict) -> bool: ...
    def save_to_db(self, data: dict) -> None: ...
    def send_email(self, report: dict) -> None: ...
```

### OOP Fix
```python
# Good — each class has one job
class ReportParser:
    def parse(self, raw: str) -> dict: ...

class ReportValidator:
    def validate(self, data: dict) -> bool: ...

class ReportRepository:
    def save(self, data: dict) -> None: ...

class ReportNotifier:
    def send(self, report: dict) -> None: ...
```

### Functional Smell
```python
# Bad — one function doing three unrelated things
def process_order(order: dict) -> None:
    # Validate
    if not order.get("items"):
        raise ValueError("Empty order")
    # Calculate
    total = sum(item["price"] * item["qty"] for item in order["items"])
    tax = total * 0.08
    # Persist
    db.execute("INSERT INTO orders ...", order)
    # Notify
    send_email(order["email"], f"Total: {total + tax}")
```

### Functional Fix
```python
# Good — each function has one job, composed at a higher level
def validate_order(order: dict) -> None:
    if not order.get("items"):
        raise ValueError("Empty order")

def calculate_total(items: list[dict]) -> float:
    return sum(item["price"] * item["qty"] for item in items)

def persist_order(order: dict) -> None:
    db.execute("INSERT INTO orders ...", order)

def notify_customer(email: str, total: float) -> None:
    send_email(email, f"Total: {total}")

# Compose
def handle_order(order: dict) -> None:
    validate_order(order)
    total = calculate_total(order["items"])
    persist_order(order)
    notify_customer(order["email"], total)
```

---

## Open/Closed Principle (OCP)

> Open for extension, closed for modification.

### Checklist
- [ ] New behavior can be added without changing existing code
- [ ] Uses polymorphism, composition, or higher-order functions instead of if/elif chains on type
- [ ] Strategy or plugin patterns used where behavior varies
- [ ] Decorators used to extend function behavior without modifying the original
- [ ] No need to edit a function every time a new variant is added

### OOP Smell
```python
# Bad — must modify this function for every new format
def export(data: dict, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(data)
    elif fmt == "csv":
        return to_csv(data)
    elif fmt == "xml":
        return to_xml(data)
    # Every new format = edit this function
```

### OOP Fix
```python
# Good — extend by adding new classes, not editing existing code
from abc import ABC, abstractmethod

class Exporter(ABC):
    @abstractmethod
    def export(self, data: dict) -> str: ...

class JsonExporter(Exporter):
    def export(self, data: dict) -> str:
        return json.dumps(data)

class CsvExporter(Exporter):
    def export(self, data: dict) -> str:
        return to_csv(data)

# Adding XML = new class, zero changes to existing code
```

### Functional Smell
```python
# Bad — same if/elif problem, but with bare functions
def notify(user: User, channel: str) -> None:
    if channel == "email":
        send_email(user.email, "Hello")
    elif channel == "sms":
        send_sms(user.phone, "Hello")
    elif channel == "slack":
        post_slack(user.slack_id, "Hello")
    # Every new channel = edit this function
```

### Functional Fix
```python
# Good — registry of callables, extend by registering new functions
from typing import Callable

Notifier = Callable[[User, str], None]

NOTIFIERS: dict[str, Notifier] = {}

def register_notifier(channel: str, fn: Notifier) -> None:
    NOTIFIERS[channel] = fn

def notify(user: User, channel: str, message: str) -> None:
    NOTIFIERS[channel](user, message)  # No if/elif, just dispatch

register_notifier("email", lambda u, msg: send_email(u.email, msg))
register_notifier("sms", lambda u, msg: send_sms(u.phone, msg))
# Adding Slack = one register call, zero changes to notify()
```

**Also: decorators are OCP in action** — they extend behavior without modifying the original function:
```python
@retry(max_attempts=3)
@log_execution_time
def fetch_data(url: str) -> dict: ...
```

---

## Liskov Substitution Principle (LSP)

> Subtypes must be substitutable for their base types.
> **Functional equivalent**: Callables with the same signature must honor the same contract.

### Checklist
- [ ] Subclasses don't raise unexpected exceptions
- [ ] Subclasses don't strengthen preconditions (narrower input)
- [ ] Subclasses don't weaken postconditions (broader/missing output)
- [ ] Overridden methods maintain the same contract
- [ ] No `isinstance` checks to handle subclass-specific behavior
- [ ] Callback/strategy functions honor the expected signature and return type
- [ ] Functions passed to `map`, `filter`, `sorted(key=)` return the expected type

### OOP Smell
```python
class Bird:
    def fly(self) -> str:
        return "flying"

class Penguin(Bird):
    def fly(self) -> str:
        raise NotImplementedError("Penguins can't fly")  # Breaks contract
```

### OOP Fix
```python
# Good — separate capabilities properly
class Bird:
    def move(self) -> str: ...

class FlyingBird(Bird):
    def move(self) -> str:
        return "flying"

class Penguin(Bird):
    def move(self) -> str:
        return "swimming"
```

### Functional Smell
```python
# Bad — callbacks violate expected contract
Transformer = Callable[[str], str]  # Expected: str in, str out

def shout(text: str) -> str:
    return text.upper()

def broken_transform(text: str) -> str:
    if not text:
        return None  # Violates return type contract!
    return text.upper()

# Any function used as Transformer must always return str, never None
```

### Functional Fix
```python
# Good — all callables honor the Transformer contract
def shout(text: str) -> str:
    return text.upper()

def whisper(text: str) -> str:
    return text.lower()

def identity(text: str) -> str:
    return text  # Empty string is fine — still a str
```

---

## Interface Segregation Principle (ISP)

> Clients should not be forced to depend on interfaces they don't use.
> **Functional equivalent**: Functions should accept only the parameters they need.

### Checklist
- [ ] ABCs/Protocols are small and focused (3-5 methods max)
- [ ] No classes forced to implement methods they don't need
- [ ] Uses `Protocol` for structural (duck) typing where appropriate
- [ ] Large interfaces split into smaller role-based ones
- [ ] Functions don't require callers to pass unused parameters
- [ ] No god-functions taking 8+ parameters (sign of bundled responsibilities)

### OOP Smell
```python
# Bad — forces all workers to implement every method
class Worker(ABC):
    @abstractmethod
    def code(self) -> None: ...
    @abstractmethod
    def test(self) -> None: ...
    @abstractmethod
    def deploy(self) -> None: ...
    @abstractmethod
    def write_docs(self) -> None: ...
```

### OOP Fix
```python
# Good — compose small, focused protocols
from typing import Protocol

class Coder(Protocol):
    def code(self) -> None: ...

class Tester(Protocol):
    def test(self) -> None: ...

class Deployer(Protocol):
    def deploy(self) -> None: ...

# A developer only needs to satisfy the protocols they actually use
```

### Functional Smell
```python
# Bad — caller forced to provide config they don't use
def send_notification(
    user: User,
    message: str,
    email_config: EmailConfig,     # Not needed for SMS
    sms_config: SmsConfig,         # Not needed for email
    slack_config: SlackConfig,     # Not needed for either
    channel: str,
) -> None: ...
```

### Functional Fix
```python
# Good — each function takes only what it needs
def send_email(user: User, message: str, config: EmailConfig) -> None: ...
def send_sms(user: User, message: str, config: SmsConfig) -> None: ...
def send_slack(user: User, message: str, config: SlackConfig) -> None: ...
```

---

## Dependency Inversion Principle (DIP)

> Depend on abstractions, not concretions.
> **Functional equivalent**: Pass dependencies as function parameters instead of hardcoding them.

### Checklist
- [ ] High-level modules don't import low-level modules directly
- [ ] Dependencies are injected (constructor, function parameter, or framework DI)
- [ ] Uses `Protocol` or `ABC` to define contracts between layers
- [ ] Easy to swap implementations (e.g., real DB vs. in-memory for tests)
- [ ] No hardcoded instantiation of dependencies inside business logic
- [ ] Functions accept callables as parameters for swappable behavior
- [ ] Module-level singletons are avoided in favor of explicit passing

### OOP Smell
```python
# Bad — business logic tightly coupled to a specific database
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hardcoded dependency

    def place_order(self, order: Order) -> None:
        self.db.insert("orders", order.to_dict())
```

### OOP Fix
```python
# Good — depend on abstraction, inject implementation
from typing import Protocol

class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...

class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo  # Injected

    def place_order(self, order: Order) -> None:
        self.repo.save(order)

# Production
service = OrderService(PostgresOrderRepo(conn))
# Tests
service = OrderService(InMemoryOrderRepo())
```

### Functional Smell
```python
# Bad — hardcoded dependency inside function
import requests

def fetch_weather(city: str) -> dict:
    response = requests.get(f"https://api.weather.com/{city}")  # Hardcoded
    return response.json()

# Can't test without hitting the real API
```

### Functional Fix
```python
# Good — inject the HTTP call as a parameter
from typing import Callable

HttpGet = Callable[[str], dict]

def fetch_weather(city: str, get: HttpGet) -> dict:
    return get(f"https://api.weather.com/{city}")

# Production
fetch_weather("Paris", lambda url: requests.get(url).json())

# Tests — no network call
fetch_weather("Paris", lambda url: {"temp": 22, "city": "Paris"})
```

**Also: closures as lightweight DI:**
```python
def make_fetcher(get: HttpGet) -> Callable[[str], dict]:
    def fetch_weather(city: str) -> dict:
        return get(f"https://api.weather.com/{city}")
    return fetch_weather

# Wire once, use everywhere
fetcher = make_fetcher(lambda url: requests.get(url).json())
fetcher("Paris")
```

---

## Priority Levels

| Priority | What to Flag |
|----------|-------------|
| Critical | LSP violations (broken contracts), DIP violations in core logic (classes or functions) |
| Important | SRP violations (god classes or god functions), OCP violations (growing if/elif chains) |
| Nice to Have | ISP refinements, extracting protocols, narrowing function signatures |

## Python-Specific Notes

- **Prefer `Protocol` over `ABC`** for duck typing — more Pythonic, no inheritance required
- **Dataclasses and NamedTuples** naturally encourage SRP (data vs. behavior separation)
- **`functools` and closures** can replace simple strategy classes (OCP without class overhead)
- **Higher-order functions** are Python's native DIP — pass behavior as parameters
- **Decorators** are OCP in action — extend without modifying
- **Don't over-engineer** — SOLID is a guide, not dogma. A 20-line script doesn't need DIP. A pure function pipeline doesn't need Protocol abstractions.
