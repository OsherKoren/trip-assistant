---
name: review-python
description: |
  Review Python code for Pythonic idioms and SOLID principles (OOP and functional).
  Use when: (1) After implementing new classes, functions, or modules, (2) Before creating
  a PR, (3) User requests code review, (4) Checking compliance with Python standards.
  Covers both OOP and functional/procedural code — not limited to classes.
  Reviews recent changes by default, or specific files if requested.
  Complements domain-specific skills (review-langgraph, review-fastapi).
---

# Python Code Review Skill

General-purpose code review for Python code quality, Pythonic idioms, and SOLID principles — for **both OOP and functional/procedural code**.

## What This Skill Does

1. **Analyzes recent changes** - Reviews git diff or specified files
2. **Checks Pythonic patterns** - Validates idiomatic Python usage (classes, functions, modules)
3. **Checks SOLID principles** - Validates design against SOLID (OOP: classes/protocols, Functional: functions/closures/higher-order functions)
4. **References checklists** - Compares against `references/pythonic.md` and `references/solid.md`
5. **Suggests refactorings** - Provides specific code improvements with before/after examples

---

## Review Workflow

### 1. Identify Scope

By default, review recent uncommitted changes:
```bash
git diff --name-only          # Changed files
git diff --staged --name-only # Staged files
```

Or review specific files if the user requests it.

### 2. Run Checklists

Apply both checklists from the `references/` directory:

1. **`references/pythonic.md`** - Pythonic idioms, built-in usage, code style
2. **`references/solid.md`** - SOLID principles for Python classes and modules

### 3. Provide Feedback

For each issue found, provide:
- **What**: The specific problem
- **Why**: Which principle or idiom it violates
- **Fix**: Concrete code suggestion (before/after)

### 4. Suggest Refactorings

Look for broader refactoring opportunities:
- Classes doing too much (SRP violation)
- Tight coupling between modules (DIP violation)
- Repeated logic that could be abstracted (DRY)
- Non-Pythonic patterns that have idiomatic alternatives

---

## Output Format

```markdown
## Python & OOP Review: `<file or scope>`

### Good Practices
- <what's already done well>

### Issues Found
- **[SOLID-SRP]** `class_name` handles both X and Y — split into two classes
- **[PYTHONIC]** Use `dict.get(key, default)` instead of `if key in dict`

### Refactoring Opportunities
- <broader improvement suggestions with before/after code>

### References
- See `references/solid.md` > Single Responsibility
- See `references/pythonic.md` > Built-in Usage
```

---

## When NOT to Review

- Changes to non-Python files (JSON, YAML, Markdown, configs)
- Trivial changes (typos, comment fixes, import reordering)
- Auto-generated code or lock files
- Changes already covered by domain-specific skills (LangGraph patterns, FastAPI patterns)

This skill focuses on **general Python quality** — delegate framework-specific concerns to `review-langgraph` or `review-fastapi`.
