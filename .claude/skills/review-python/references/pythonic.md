# Pythonic Code — Quick Reference

## Built-in Usage

### Checklist
- [ ] Uses `dict.get(key, default)` instead of `if key in dict` + access
- [ ] Uses `enumerate()` instead of manual index tracking
- [ ] Uses `zip()` for parallel iteration
- [ ] Uses `any()` / `all()` instead of manual loop-and-flag
- [ ] Uses `collections` module where appropriate (defaultdict, Counter, namedtuple)
- [ ] Uses `itertools` for complex iteration patterns
- [ ] Uses `pathlib.Path` instead of `os.path` string manipulation

### Examples

```python
# Bad
found = False
for item in items:
    if item.is_valid():
        found = True
        break

# Good
found = any(item.is_valid() for item in items)
```

```python
# Bad
for i in range(len(items)):
    print(i, items[i])

# Good
for i, item in enumerate(items):
    print(i, item)
```

```python
# Bad
result = {}
for key in keys:
    if key not in result:
        result[key] = []
    result[key].append(value)

# Good
from collections import defaultdict
result = defaultdict(list)
for key in keys:
    result[key].append(value)
```

---

## Comprehensions & Generators

### Checklist
- [ ] Uses list/dict/set comprehensions for simple transforms
- [ ] Uses generator expressions for large sequences (memory efficiency)
- [ ] Comprehensions are readable — no more than one condition + one transform
- [ ] Complex logic extracted to a named function, not crammed into a comprehension

### Examples

```python
# Bad — too complex in comprehension
result = [transform(x) for x in data if x.is_valid() and x.category in allowed and x.score > threshold]

# Good — extract predicate
def is_eligible(x: Item) -> bool:
    return x.is_valid() and x.category in allowed and x.score > threshold

result = [transform(x) for x in data if is_eligible(x)]
```

```python
# Bad — builds full list just to iterate
total = sum([len(line) for line in lines])

# Good — generator expression, no intermediate list
total = sum(len(line) for line in lines)
```

---

## Unpacking & Assignment

### Checklist
- [ ] Uses tuple unpacking for multiple return values
- [ ] Uses `*rest` for capturing remaining items
- [ ] Uses `_` for deliberately ignored values
- [ ] Uses walrus operator `:=` where it improves readability (Python 3.8+)

### Examples

```python
# Bad
first = parts[0]
rest = parts[1:]

# Good
first, *rest = parts
```

```python
# Bad
match = pattern.search(text)
if match:
    process(match)

# Good
if match := pattern.search(text):
    process(match)
```

---

## String Handling

### Checklist
- [ ] Uses f-strings for formatting (not `.format()` or `%`)
- [ ] Uses `str.join()` for building strings from iterables
- [ ] Uses `str.removeprefix()` / `str.removesuffix()` (Python 3.9+)
- [ ] Uses `textwrap.dedent` for multi-line strings in code

### Examples

```python
# Bad
message = "Hello, " + name + "! You have " + str(count) + " items."

# Good
message = f"Hello, {name}! You have {count} items."
```

```python
# Bad
result = ""
for word in words:
    result += word + ", "
result = result[:-2]

# Good
result = ", ".join(words)
```

---

## Context Managers & Resources

### Checklist
- [ ] Uses `with` for file I/O, locks, DB connections
- [ ] Uses `contextlib.contextmanager` for simple custom context managers
- [ ] Uses `contextlib.suppress` instead of bare `try/except: pass`
- [ ] No manual `.close()` calls on resources that support `with`

### Examples

```python
# Bad
try:
    os.remove(path)
except FileNotFoundError:
    pass

# Good
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove(path)
```

---

## Data Classes & Typing

### Checklist
- [ ] Uses `dataclass` or `NamedTuple` for data containers (not bare dicts or tuples)
- [ ] Uses `TypedDict` for structured dict shapes (e.g., LangGraph state)
- [ ] Uses `Enum` for fixed sets of choices
- [ ] Uses `|` union syntax (Python 3.10+): `str | None` not `Optional[str]`
- [ ] Uses `Self` type (Python 3.11+) for methods returning own type

### Examples

```python
# Bad — "magic" tuple positions
def get_user():
    return ("Alice", 30, "alice@example.com")

name = get_user()[0]  # What is [0]?

# Good — self-documenting
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str

user = get_user()
print(user.name)
```

```python
# Bad
status = "active"  # Could be anything

# Good
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
```

---

## Exception Handling

### Checklist
- [ ] Catches specific exceptions, not bare `except:` or `except Exception:`
- [ ] Uses `raise ... from e` to preserve exception chains
- [ ] Custom exceptions inherit from appropriate built-in exceptions
- [ ] No silent swallowing of exceptions without logging
- [ ] Uses EAFP (try/except) over LBYL (if/check) for key lookups, attribute access

### Examples

```python
# Bad — LBYL (Look Before You Leap)
if hasattr(obj, "name") and obj.name is not None:
    process(obj.name)

# Good — EAFP (Easier to Ask Forgiveness than Permission)
try:
    process(obj.name)
except AttributeError:
    handle_missing()
```

```python
# Bad — loses original traceback
except ValueError as e:
    raise CustomError("bad value")

# Good — preserves chain
except ValueError as e:
    raise CustomError("bad value") from e
```

---

## Module & Import Patterns

### Checklist
- [ ] Uses `__all__` to define public API of modules
- [ ] Avoids circular imports (restructure or use local imports)
- [ ] Groups imports: stdlib → third-party → local (enforced by ruff/isort)
- [ ] Uses absolute imports over relative imports
- [ ] Avoids wildcard imports (`from module import *`)

---

## Performance Idioms

### Checklist
- [ ] Uses `set` for membership testing over `list` (O(1) vs O(n))
- [ ] Uses `dict` comprehension over `dict()` constructor with zip
- [ ] Avoids repeated attribute lookups in tight loops (assign to local)
- [ ] Uses `functools.lru_cache` for expensive pure function calls
- [ ] Uses `__slots__` on data-heavy classes when memory matters

### Examples

```python
# Bad — O(n) lookup on every iteration
allowed = ["a", "b", "c", "d", "e"]
filtered = [x for x in data if x in allowed]

# Good — O(1) lookup
allowed = {"a", "b", "c", "d", "e"}
filtered = [x for x in data if x in allowed]
```

---

## Priority Levels

| Priority | What to Flag |
|----------|-------------|
| Critical | Bare `except:`, mutable default args, silent exception swallowing |
| Important | Non-Pythonic loops, missing context managers, stringly-typed data |
| Nice to Have | Generator vs list comprehension, `pathlib` over `os.path`, `__slots__` |
