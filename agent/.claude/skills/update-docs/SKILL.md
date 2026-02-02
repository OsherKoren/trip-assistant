---
name: update-docs
description: |
  Update project documentation (README, CHANGELOG) based on recent changes.
  Use when: (1) After implementing new features or significant changes,
  (2) Before creating a pull request or release, (3) User explicitly requests
  documentation updates, (4) After completing a development phase/milestone.
  DO NOT use automatically on every commit.
---

# Documentation Update Skill

Update README.md, CHANGELOG.md, and other documentation based on recent code changes.

## Workflow

1. **Analyze changes** - Use `git diff` or `git log` to understand what changed
2. **Identify impact** - Determine which docs need updates
3. **Update systematically** - README → CHANGELOG → other docs
4. **Preserve style** - Match existing documentation tone and format

---

## README.md Updates

### When to Update README

- New features added (update Features section)
- Installation steps changed (update Installation section)
- New dependencies added (update Dependencies/Requirements)
- API changes (update Usage/Examples section)
- Configuration options changed

### README Structure (maintain consistency)

```markdown
# Project Name

Brief description

## Features
- List key features

## Installation
Step-by-step setup

## Usage
Examples and basic usage

## Development
How to contribute/develop

## Dependencies
Key dependencies
```

### Update Pattern

1. Read existing README.md
2. Identify which section(s) need updates
3. Preserve existing style and tone
4. Add new information in the appropriate section
5. Keep it concise - README is overview, not detailed docs

---

## CHANGELOG.md Updates

### Format: Keep a Changelog

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Vulnerability fixes

## [1.0.0] - 2026-01-15

### Added
- Initial release
```

### Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

### Update Pattern

1. Add changes under `## [Unreleased]`
2. Use appropriate category (Added, Changed, etc.)
3. Write from user perspective, not implementation details
4. Be specific but concise
5. Link to issues/PRs if relevant

### Examples

**Good:**
```markdown
### Added
- Classifier node with topic-based routing for flight, hotel, and activity queries
- Support for structured LLM output using Pydantic models
```

**Bad:**
```markdown
### Added
- Added some stuff to classifier.py
- Fixed things
```

---

## Other Documentation

### API Documentation
- Update docstrings in code (don't duplicate in README)
- Keep high-level API overview in README

### Architecture Docs
- Update `docs/architecture.md` if structure changes
- Update diagrams if routing/flow changes

### Task Specs
- Keep `tasks/*.md` files up to date with implementation status
- Mark completed phases

---

## Process

### 1. Analyze Changes

```bash
# See what changed since last commit
git diff HEAD

# See recent commits
git log --oneline -10

# See changed files
git status
```

### 2. Ask User

Before making changes, ask:
- "Which documentation files should I update?"
- "Is this a feature, fix, or change?"
- "Should this go in CHANGELOG under Unreleased?"

### 3. Update Files

Update in this order:
1. CHANGELOG.md (always update for notable changes)
2. README.md (if user-facing changes)
3. Other docs (architecture, API docs, etc.)

### 4. Show Preview

Show the user what you changed before they commit.

---

## Best Practices

### DO:
- ✓ Write from user perspective
- ✓ Be specific and concise
- ✓ Maintain existing style/tone
- ✓ Group related changes together
- ✓ Use present tense ("Add feature" not "Added feature")

### DON'T:
- ✗ Auto-generate verbose boilerplate
- ✗ Include implementation details in CHANGELOG
- ✗ Duplicate information across docs
- ✗ Update docs for trivial changes
- ✗ Break existing formatting

---

## Examples

### Scenario: Added Classifier Node

**CHANGELOG.md:**
```markdown
## [Unreleased]

### Added
- Classifier node for routing queries by topic (flights, hotels, activities)
- LangGraph StateGraph with conditional routing
```

**README.md (Architecture section):**
```markdown
## Architecture

The agent uses a classifier-router pattern:
1. Classifier analyzes user query and determines topic
2. Router sends to appropriate specialist node
3. Specialist responds with relevant trip information
```

### Scenario: Fixed Bug in Document Loading

**CHANGELOG.md:**
```markdown
## [Unreleased]

### Fixed
- Document loading now handles missing files gracefully
```

**README.md:**
No update needed (internal fix, not user-facing)

---

## When NOT to Update Docs

- Trivial code refactoring (no user impact)
- Internal test changes
- Code formatting
- Comment updates
- Minor variable renames

Only update docs for **notable changes** that affect users or developers.
