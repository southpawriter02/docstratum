# v0.6.3 — Code Cleanup

> **Task:** Final code cleanup, docstrings, and formatting.
> 

---

## Task Overview

---

## Cleanup Checklist

### Code Quality

- [ ]  All functions have docstrings
- [ ]  Type hints on all function signatures
- [ ]  No unused imports
- [ ]  No commented-out code
- [ ]  No hardcoded secrets
- [ ]  Consistent naming conventions

### Formatting

```bash
# Install formatters
pip install black isort

# Format all Python files
black .
isort .
```

### Linting

```bash
# Install linter
pip install ruff

# Check for issues
ruff check .

# Auto-fix where possible
ruff check --fix .
```

---

## File-by-File Review

### `schemas/llms_[schema.py](http://schema.py)`

- [ ]  Module docstring
- [ ]  Class docstrings
- [ ]  Field descriptions

### `core/[loader.py](http://loader.py)`

- [ ]  Function docstrings
- [ ]  Error handling
- [ ]  Logging statements

### `core/[context.py](http://context.py)`

- [ ]  Function docstrings
- [ ]  Token estimation documented
- [ ]  Section builders documented

### `core/[agents.py](http://agents.py)`

- [ ]  Class docstring
- [ ]  Method docstrings
- [ ]  API key handling documented

### `core/[testing.py](http://testing.py)`

- [ ]  Dataclass docstrings
- [ ]  Test harness documented
- [ ]  Result format documented

### `demo/[app.py](http://app.py)`

- [ ]  Module docstring
- [ ]  UI sections commented
- [ ]  Session state documented

---

## Security Check

- [ ]  `.env` in `.gitignore`
- [ ]  No API keys in code
- [ ]  `.env.example` has placeholder values
- [ ]  No sensitive URLs in examples

```bash
# Search for potential secrets
grep -r "sk-" . --include="*.py"
grep -r "api_key" . --include="*.py"
```

---

## Test Coverage

```bash
# Run tests with coverage
pytest --cov=core --cov=schemas --cov-report=html

# Open report
open htmlcov/index.html
```

**Target:** >70% coverage

---

## Acceptance Criteria

- [ ]  `black .` runs with no changes
- [ ]  `ruff check .` returns no errors
- [ ]  All public functions have docstrings
- [ ]  No secrets in codebase
- [ ]  Tests pass: `pytest`