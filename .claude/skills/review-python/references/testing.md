# Pythonic Testing — Quick Reference

> Prefer pytest-native tools over unittest.mock wherever possible.
> Reserve unittest.mock for cases pytest doesn't cover (async mocks, spec-based mocks).

## Fixtures & Setup

### Checklist
- [ ] Shared fixtures live in `conftest.py` (not duplicated across test files)
- [ ] Uses `@pytest.fixture` over manual setup/teardown
- [ ] Fixture scope matches lifecycle (`function` default, `session` for expensive resources)
- [ ] Factory fixtures used when tests need variants of the same object
- [ ] No fixture does real I/O unless explicitly needed (integration tests)

### Examples

```python
# Bad — repeated setup in every test
def test_user_create():
    user = User(name="Alice", age=30)
    assert user.name == "Alice"

def test_user_greeting():
    user = User(name="Alice", age=30)
    assert user.greeting() == "Hello, Alice!"

# Good — fixture in conftest.py
@pytest.fixture
def user() -> User:
    return User(name="Alice", age=30)

def test_user_create(user: User) -> None:
    assert user.name == "Alice"

def test_user_greeting(user: User) -> None:
    assert user.greeting() == "Hello, Alice!"
```

```python
# Good — factory fixture for variants
@pytest.fixture
def make_user() -> Callable[..., User]:
    def _make(name: str = "Alice", age: int = 30) -> User:
        return User(name=name, age=age)
    return _make

def test_minor(make_user: Callable[..., User]) -> None:
    user = make_user(age=16)
    assert not user.is_adult()
```

---

## Monkeypatch Over unittest.mock.patch

### Checklist
- [ ] Uses `monkeypatch.setenv()` / `monkeypatch.delenv()` for environment variables
- [ ] Uses `monkeypatch.setattr()` for replacing attributes/functions on modules or objects
- [ ] Uses `monkeypatch.setitem()` for dict mutations
- [ ] No `unittest.mock.patch` or `@patch` decorators for env vars or simple attribute swaps
- [ ] No `with patch.dict("os.environ", ...)` — use `monkeypatch.setenv` instead

### Examples

```python
# Bad — unittest.mock for env vars
from unittest.mock import patch

def test_reads_env():
    with patch.dict("os.environ", {"API_KEY": "test-key"}):
        settings = Settings()
        assert settings.api_key == "test-key"

# Good — monkeypatch (auto-reverted after test)
def test_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_KEY", "test-key")
    settings = Settings()
    assert settings.api_key == "test-key"
```

```python
# Bad — patch decorator for attribute swap
@patch("app.dependencies.some_module.create_client")
def test_uses_client(mock_create):
    mock_create.return_value = FakeClient()
    result = build_thing()
    assert result.ready

# Good — monkeypatch.setattr
def test_uses_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.dependencies.some_module.create_client", lambda: FakeClient())
    result = build_thing()
    assert result.ready
```

---

## pytest Built-in Fixtures Over unittest

### Checklist
- [ ] Uses `tmp_path` (not `tempfile.mkdtemp()`) for temporary directories
- [ ] Uses `capsys` (not mocking `sys.stdout`) for capturing print output
- [ ] Uses `caplog` (not mocking `logging`) for capturing log output
- [ ] Uses `monkeypatch` (not `@patch`) for env vars and attribute swaps
- [ ] Uses `request` fixture for parametrize access and test metadata

### Examples

```python
# Bad — manual tempdir
import tempfile, shutil

def test_writes_file():
    tmpdir = tempfile.mkdtemp()
    try:
        path = Path(tmpdir) / "out.txt"
        write_output(path)
        assert path.read_text() == "done"
    finally:
        shutil.rmtree(tmpdir)

# Good — tmp_path (auto-cleaned)
def test_writes_file(tmp_path: Path) -> None:
    path = tmp_path / "out.txt"
    write_output(path)
    assert path.read_text() == "done"
```

```python
# Bad — mock stdout
from unittest.mock import patch
from io import StringIO

def test_prints_greeting():
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
        greet("Alice")
        assert "Hello, Alice" in mock_out.getvalue()

# Good — capsys
def test_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    greet("Alice")
    assert "Hello, Alice" in capsys.readouterr().out
```

---

## When unittest.mock IS Appropriate

Keep `unittest.mock` for cases pytest doesn't replace:

- [ ] **AsyncMock** — `pytest` has no native async mock; use `unittest.mock.AsyncMock`
- [ ] **MagicMock with spec** — when you need auto-specced mocks that enforce interface
- [ ] **call assertions** — `assert_called_once_with`, `call_args_list` for verifying interactions
- [ ] **Side effects** — `side_effect=[val1, val2, Exception()]` for sequential returns
- [ ] **Complex patching** — `patch.object` for class instance methods in deeply nested code

### Examples

```python
# Good — AsyncMock for async interfaces
from unittest.mock import AsyncMock

@pytest.fixture
def mock_graph() -> AsyncMock:
    graph = AsyncMock()
    graph.ainvoke.return_value = {"answer": "test", "category": "general", "confidence": 0.9}
    return graph
```

```python
# Good — MagicMock with spec to catch interface drift
from unittest.mock import MagicMock

mock_client = MagicMock(spec=LambdaClient)
mock_client.invoke.return_value = {"Payload": ...}
# mock_client.nonexistent_method()  # Raises AttributeError — caught early
```

---

## Parametrize Over Copy-Paste

### Checklist
- [ ] Uses `@pytest.mark.parametrize` for testing multiple inputs with same logic
- [ ] Test IDs are readable (use `pytest.param(..., id="descriptive-name")` when needed)
- [ ] No duplicated test functions that differ only in input values
- [ ] Parametrized tests grouped logically (happy paths together, error cases together)

### Examples

```python
# Bad — duplicated tests
def test_classify_flight() -> None:
    assert classify("What time is my flight?") == "flight"

def test_classify_hotel() -> None:
    assert classify("Where is my hotel?") == "accommodation"

def test_classify_car() -> None:
    assert classify("Where do I pick up the car?") == "car_rental"

# Good — parametrized
@pytest.mark.parametrize("query, expected", [
    ("What time is my flight?", "flight"),
    ("Where is my hotel?", "accommodation"),
    ("Where do I pick up the car?", "car_rental"),
])
def test_classify(query: str, expected: str) -> None:
    assert classify(query) == expected
```

---

## Type Hints in Tests

### Checklist
- [ ] All test functions have return type `-> None`
- [ ] Fixture return types are annotated
- [ ] `pytest.MonkeyPatch`, `pytest.CaptureFixture[str]`, etc. used for built-in fixtures
- [ ] No `Any` as fixture type — use the actual type or protocol

---

## Test Organization

### Checklist
- [ ] Unit tests in `tests/` root, integration tests in `tests/integration/`
- [ ] Integration tests marked with `@pytest.mark.integration`
- [ ] Test file mirrors source file: `app/settings.py` → `tests/test_settings.py`
- [ ] Test classes group related tests: `class TestSettings:` (no need for `unittest.TestCase`)
- [ ] Fixtures scoped appropriately — `conftest.py` for shared, test file for local

---

## Priority Levels

| Priority | What to Flag |
|----------|-------------|
| Critical | `@patch` or `patch.dict` for env vars (use monkeypatch), duplicated test code that should be parametrized |
| Important | Missing type hints on tests, `tempfile` instead of `tmp_path`, mock stdout instead of `capsys` |
| Nice to Have | Factory fixtures, `pytest.param` with IDs, fixture scope optimization |
