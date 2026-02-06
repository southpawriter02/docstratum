# v0.1.1 — Environment Setup

> **Phase:** Foundation (v0.1.x)
> **Status:** DRAFT — Realigned to validation-engine pivot (2026-02-06)
> **Parent:** [v0.1.0 — Project Foundation](RR-SPEC-v0.1.0-project-foundation.md)
> **Goal:** Establish the development environment with foundation-only dependencies for the validation engine. No agent, demo, or LLM dependencies at this stage.
> **Traces to:** CONST-003 (fixed tech stack), NFR-011 (code style compliance), NFR-014 (Python 3.9+ compatibility)

---

## What Changed from the Original v0.1.1

The original v0.1.1 installed the entire project dependency stack upfront — LangChain, OpenAI, Streamlit, Neo4j — creating coupling between the foundation phase and downstream modules that don't exist yet. The research phase established a clear module hierarchy (v0.0.5a) with distinct dependency boundaries per phase.

The realigned v0.1.1 installs **only what the validation engine foundation needs**: Pydantic for schema validation, a Markdown parser for ingesting llms.txt files, and the testing/linting toolchain mandated by NFR-010 and NFR-011. Everything else arrives in the phase that actually needs it.

**Why this matters:** CONST-006 (40–60 hour time budget) demands that each phase be self-contained and testable in isolation. Installing LangChain in the foundation phase creates untested import chains and increases the virtual environment size by ~200 MB — overhead that provides zero value until v0.3.x.

---

## Prerequisites

- Python 3.11+ installed (NFR-014 specifies 3.9+; we target 3.11+ for `StrEnum`, `tomllib`, and modern typing features)
- `pip` ≥ 23.0 (DECISION: pip with `requirements.txt`, not Poetry — simpler for portfolio review)
- Git initialized in the project root

---

## Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Verify   │───▶│ 2. Create   │───▶│ 3. Create   │───▶│ 4. Install  │
│   Python    │    │   Project   │    │    venv     │    │    deps     │
└─────────────┘    └──────┬──────┘    └─────────────┘    └──────┬──────┘
                          │                                     │
                          ▼                                     ▼
                   Directory layout                     Foundation-only
                   from §Project                        packages from
                   Structure                            requirements.txt
                                                              │
                          ┌─────────────┐    ┌────────────────┘
                          │ 5. Config   │───▶│ 6. Verify  │
                          │   files     │    │   setup    │
                          └─────────────┘    └────────────┘
```

---

## Project Structure

```
docstratum/
├── pyproject.toml                  # Project metadata + tool configuration
├── requirements.txt                # Foundation-phase runtime dependencies
├── requirements-dev.txt            # Development/testing dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Standard Python gitignore
├── README.md                       # Project README (updated per phase)
│
├── src/
│   └── docstratum/
│       ├── __init__.py             # Package init with version
│       ├── schema/                 # v0.1.2 — Schema Definition
│       │   ├── __init__.py         # Public API re-exports
│       │   ├── parsed.py           # Parsed document models (Markdown AST)
│       │   ├── validation.py       # Validation result models (diagnostics, levels)
│       │   ├── quality.py          # Quality scoring models (composite score, grades)
│       │   ├── classification.py   # Document type classification models
│       │   ├── enrichment.py       # Extended schema models (concepts, few-shot, instructions)
│       │   ├── diagnostics.py      # Error code registry (DiagnosticCode enum)
│       │   └── constants.py        # Canonical section names, token budget tiers
│       └── logging_config.py       # Structured logging
│
├── tests/                          # v0.1.3 — Test infrastructure (flat layout)
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures + model factories [v0.1.3b]
│   ├── test_diagnostics.py         # Tests for DiagnosticCode enum (26 codes)
│   ├── test_constants.py           # Tests for canonical names, tiers, anti-patterns
│   ├── test_classification.py      # Tests for document type + size tier classification
│   ├── test_parsed.py              # Tests for ParsedLlmsTxt model hierarchy
│   ├── test_validation.py          # Tests for ValidationResult + ValidationDiagnostic
│   ├── test_quality.py             # Tests for QualityScore + DimensionScore + grades
│   ├── test_enrichment.py          # Tests for Concept, FewShotExample, LLMInstruction
│   └── fixtures/                   # v0.1.3a — Synthetic test fixtures
│       ├── gold_standard.md        # ~95 score, Exemplary, L4 (Svelte/Pydantic archetype)
│       ├── partial_conformance.md  # ~72 score, Strong, L2 (Anthropic/Stripe archetype)
│       ├── minimal_valid.md        # ~35 score, Needs Work, L0 only (stub archetype)
│       ├── non_conformant.md       # ~18 score, Critical, fails L1 (Cursor/NVIDIA archetype)
│       └── type_2_full_excerpt.md  # Type 2 Full document excerpt (Vercel AI SDK archetype)
│
└── docs/
    └── design/                     # Design documents (v0.0.x research + v0.1.x foundation)
        ├── 01-research/            # v0.0.x research phase (27 documents)
        └── 02-foundation/          # v0.1.x foundation phase
            ├── RR-SPEC-v0.1.0-project-foundation.md
            ├── RR-SPEC-v0.1.1-environment-setup.md
            ├── RR-SPEC-v0.1.2-schema-definition.md        (parent overview)
            ├── RR-SPEC-v0.1.2a-diagnostic-infrastructure.md
            ├── RR-SPEC-v0.1.2b-document-models.md
            ├── RR-SPEC-v0.1.2c-validation-quality-models.md
            ├── RR-SPEC-v0.1.2d-enrichment-models.md
            ├── RR-SPEC-v0.1.3-sample-data.md               (parent overview)
            ├── RR-SPEC-v0.1.3a-fixture-suite.md
            └── RR-SPEC-v0.1.3b-test-infrastructure.md
```

### Directory Layout Rationale

The `src/docstratum/schema/` package uses a **one-file-per-concern** layout rather than a monolithic `schema.py` for three reasons:

1. **Test isolation** — Each concern (parsed models, validation models, quality models) has its own test file, matching NFR-010's ≥80% coverage target on the schema module.
2. **Import clarity** — Downstream modules import only what they need: `from docstratum.schema.validation import ValidationResult` avoids pulling in enrichment models when only validation is needed.
3. **Merge safety** — Parallel development on validation vs. enrichment models won't cause merge conflicts in a monolithic file. (Relevant even for a solo developer switching between branches.)

The public API is re-exported from `src/docstratum/schema/__init__.py`, so consumers can still do `from docstratum.schema import ParsedLlmsTxt, ValidationResult` for convenience.

---

## Step-by-Step Instructions

### Step 1: Verify Python Installation

```bash
# Check Python version (must be 3.11+)
python --version
# or
python3 --version
```

**If Python is not installed:**

- **macOS:** `brew install python@3.11`
- **Windows:** Download from [python.org](https://python.org)
- **Linux:** `sudo apt install python3.11 python3.11-venv`

### Step 2: Create Project Directory

```bash
# If starting fresh (skip if repo already exists)
mkdir docstratum
cd docstratum
git init
```

### Step 3: Create Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Verify activation
which python  # Should point to .venv/bin/python
```

### Step 4: Create requirements.txt

```
# DocStratum v0.1.x — Foundation Phase Runtime Dependencies
# ──────────────────────────────────────────────────────────
# Validation engine core dependencies ONLY.
# Agent/demo/LLM dependencies are deferred to their respective phases.
# See v0.1.0 §Tech Stack for the full dependency plan.

# Schema validation (DECISION-006: Pydantic for Schema Validation)
pydantic>=2.0.0,<3.0.0

# YAML frontmatter parsing (some llms.txt files include YAML frontmatter)
PyYAML>=6.0,<7.0

# Markdown parsing — CommonMark compliant (DECISION-003: GFM as standard)
# mistletoe: lightweight, extensible, pure Python, CommonMark-compliant.
# Alternative considered: markdown-it-py (heavier but better GFM table support).
# DECISION: mistletoe for foundation; can swap if GFM table support needed in v0.3.x.
mistletoe>=1.3.0,<2.0.0

# Environment variable loading (minimal now; API keys added in v0.5.x)
python-dotenv>=1.0.0,<2.0.0
```

### Step 5: Create requirements-dev.txt

```
# DocStratum v0.1.x — Development Dependencies
# ──────────────────────────────────────────────
# Testing, linting, and code quality tools.
# Mandated by NFR-010 (≥80% coverage) and NFR-011 (100% Black + Ruff).

# Include runtime dependencies
-r requirements.txt

# Testing framework (NFR-010: ≥80% test coverage on core modules)
pytest>=8.0.0,<9.0.0
pytest-cov>=4.0.0,<6.0.0

# Code formatting (NFR-011: 100% Black compliance)
black>=24.0.0

# Linting (NFR-011: 100% Ruff compliance)
ruff>=0.5.0

# Type checking (recommended for Pydantic v2 models — catches schema errors at dev time)
mypy>=1.8.0
```

### Step 6: Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### Step 7: Create Configuration Files

#### pyproject.toml

```toml
[project]
name = "docstratum"
version = "0.1.0"
description = "Validation engine and semantic enrichment layer for llms.txt"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
authors = [
    {name = "Ryan"},
]
keywords = ["llms-txt", "validation", "schema", "ai", "documentation"]
classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Text Processing :: Markup :: Markdown",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.setuptools.packages.find]
where = ["src"]

# --- Tool Configuration ---

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort (import sorting)
    "N",    # pep8-naming
    "W",    # pycodestyle warnings
    "UP",   # pyupgrade (modernize Python syntax)
    "B",    # flake8-bugbear (common bugs)
    "SIM",  # flake8-simplify
    "RUF",  # ruff-specific rules
]
ignore = [
    "E501", # line too long (handled by Black)
]

[tool.ruff.lint.isort]
known-first-party = ["docstratum"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = [
    "--cov=docstratum",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
    "-v",
]

[tool.mypy]
python_version = "3.11"
plugins = ["pydantic.mypy"]
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

#### .env.example

```bash
# DocStratum v0.1.x — Environment Variables
# ──────────────────────────────────────────
# Foundation phase requires NO external API keys.
# All variables below are placeholders for downstream phases.

# --- v0.1.x: Foundation (no external services) ---
DOCSTRATUM_LOG_LEVEL=INFO

# --- v0.5.x: Agent Integration (future) ---
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# --- v0.6.0: Demo Layer (future) ---
# STREAMLIT_SERVER_PORT=8501
```

#### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
*.egg

# Virtual environment
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment (never commit secrets)
.env

# Testing
.coverage
htmlcov/
.pytest_cache/

# OS
.DS_Store
Thumbs.db

# Tool caches
.ruff_cache/
.mypy_cache/
```

---

## Package Initialization

### src/docstratum/__init__.py

```python
"""DocStratum — Validation engine and semantic enrichment layer for llms.txt.

DocStratum validates, scores, and enriches llms.txt files. It is NOT a generator.
The llms.txt ecosystem has 75+ generation tools but zero formal validators.
DocStratum fills that governance vacuum.

Modules:
    schema      Pydantic models for parsed documents, validation results,
                quality scores, and the extended enrichment schema.

Architecture:
    Input:      Existing llms.txt Markdown files (from any of 75+ generators)
    Process:    Parse → Classify → Validate → Score → Enrich
    Output:     Validation diagnostics, quality scores, enriched content for MCP

Design Decisions:
    See docs/design/02-foundation/RR-SPEC-v0.1.0-project-foundation.md
    for the full design decision registry (DECISION-001 through DECISION-016).
"""

__version__ = "0.1.0"
__author__ = "Ryan"
```

### src/docstratum/schema/__init__.py

```python
"""DocStratum Schema Module — Public API.

Re-exports all public Pydantic models for the validation engine.
Import from this module rather than from submodules directly.

Example:
    from docstratum.schema import (
        ParsedLlmsTxt,         # Parsed Markdown document
        ValidationResult,       # Validation pipeline output
        QualityScore,           # Composite quality score
        DocumentClassification, # Type 1 Index vs. Type 2 Full
        DiagnosticCode,         # Error code registry
    )

Model Categories:
    Parsed models       What an existing llms.txt file contains (Markdown AST)
    Validation models   What the validator reports (diagnostics, levels)
    Quality models      How good the file is (composite score, grades)
    Classification      What type of document it is (Type 1 vs. Type 2)
    Enrichment models   DocStratum-extended schema (concepts, few-shot, instructions)
    Constants           Canonical section names, token budget tiers, check IDs
"""

# --- Parsed document models (what the file contains) ---
from docstratum.schema.parsed import (
    ParsedBlockquote,
    ParsedLink,
    ParsedLlmsTxt,
    ParsedSection,
)

# --- Validation result models (what the validator reports) ---
from docstratum.schema.validation import (
    ValidationDiagnostic,
    ValidationLevel,
    ValidationResult,
)

# --- Quality scoring models (how good the file is) ---
from docstratum.schema.quality import (
    DimensionScore,
    QualityDimension,
    QualityGrade,
    QualityScore,
)

# --- Document type classification ---
from docstratum.schema.classification import (
    DocumentClassification,
    DocumentType,
    SizeTier,
)

# --- Error code registry ---
from docstratum.schema.diagnostics import DiagnosticCode, Severity

# --- Extended schema models (DocStratum enrichment) ---
from docstratum.schema.enrichment import (
    Concept,
    ConceptRelationship,
    FewShotExample,
    LLMInstruction,
    Metadata,
    RelationshipType,
)

# --- Constants ---
from docstratum.schema.constants import (
    ANTI_PATTERN_REGISTRY,
    CANONICAL_SECTION_NAMES,
    TOKEN_BUDGET_TIERS,
    AntiPatternCategory,
    AntiPatternID,
    CanonicalSectionName,
)

__all__ = [
    # Parsed
    "ParsedLlmsTxt",
    "ParsedSection",
    "ParsedLink",
    "ParsedBlockquote",
    # Validation
    "ValidationLevel",
    "ValidationDiagnostic",
    "ValidationResult",
    # Quality
    "QualityDimension",
    "QualityGrade",
    "QualityScore",
    "DimensionScore",
    # Classification
    "DocumentType",
    "DocumentClassification",
    "SizeTier",
    # Diagnostics
    "DiagnosticCode",
    "Severity",
    # Enrichment
    "Metadata",
    "Concept",
    "ConceptRelationship",
    "RelationshipType",
    "FewShotExample",
    "LLMInstruction",
    # Constants
    "CanonicalSectionName",
    "CANONICAL_SECTION_NAMES",
    "TOKEN_BUDGET_TIERS",
    "AntiPatternID",
    "AntiPatternCategory",
    "ANTI_PATTERN_REGISTRY",
]
```

---

## Dependencies NOT Installed (Deferred)

| Package | Purpose | Phase | Why Not Now |
|---------|---------|-------|-------------|
| `langchain` | Agent framework + chain composition | v0.3.x–v0.5.x | Not needed for schema definition or validation |
| `openai` | OpenAI API SDK | v0.5.x | Agent responses require API keys and LLM calls |
| `anthropic` | Anthropic API SDK | v0.5.x | Agent responses require API keys and LLM calls |
| `litellm` | Multi-provider LLM abstraction | v0.5.x | Abstraction layer for agent integration |
| `streamlit` | Demo UI framework | v0.6.0 | Demo layer is the final implementation phase |
| `neo4j` | Graph database | Post-MVP (OOS-G1) | Concept graph visualization is out of scope |
| `httpx` / `requests` | HTTP client for URL validation | v0.2.x | URL resolution is a v0.2.x validation concern |

---

## Verification Script

After completing all steps, run this verification:

```bash
# 1. Verify Python version
python --version
# Expected: Python 3.11.x or 3.12.x

# 2. Verify core dependencies (no LangChain/OpenAI/Streamlit!)
python -c "
import pydantic; print(f'  pydantic {pydantic.__version__}')
import yaml; print(f'  PyYAML OK')
import mistletoe; print(f'  mistletoe OK')
import dotenv; print(f'  python-dotenv OK')
print('Runtime dependencies OK')
"

# 3. Verify dev dependencies
python -c "
import pytest; print(f'  pytest {pytest.__version__}')
print('Dev dependencies OK')
"

# 4. Verify NO prohibited dependencies are installed
python -c "
prohibited = ['langchain', 'openai', 'anthropic', 'streamlit', 'neo4j']
for pkg in prohibited:
    try:
        __import__(pkg)
        print(f'  FAIL: {pkg} should not be installed in foundation phase')
        exit(1)
    except ImportError:
        print(f'  OK: {pkg} not installed (correct)')
print('Dependency boundary check passed')
"

# 5. Verify schema imports (after v0.1.2 is implemented)
python -c "from docstratum.schema import ParsedLlmsTxt, ValidationResult, QualityScore; print('Schema imports OK')"

# 6. Run linting (NFR-011)
black --check src/ tests/
ruff check src/ tests/

# 7. Run tests with coverage (NFR-010)
pytest
# Expected: All tests pass, coverage ≥80% on docstratum.schema
```

---

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `python: command not found` | Python not in PATH | Use `python3` or add to PATH |
| `No module named 'pydantic'` | Virtual environment not activated | Run `source .venv/bin/activate` |
| `pip install` fails on `mistletoe` | Outdated pip | Run `pip install --upgrade pip` |
| `black --check` shows reformatting | Code not formatted | Run `black src/ tests/` to fix |
| `ruff check` shows violations | Lint issues | Run `ruff check --fix src/ tests/` to auto-fix |
| `pytest` can't find `docstratum` | Missing `pythonpath` in pyproject.toml | Verify `[tool.pytest.ini_options]` includes `pythonpath = ["src"]` |
| Coverage below 80% | Untested code paths | Add tests for uncovered branches |

---

## Exit Criteria

- [ ] `python --version` returns 3.11+
- [ ] `.venv` directory exists and is activated
- [ ] `pip install -r requirements-dev.txt` completes without errors
- [ ] Verification script steps 1–4 all pass (correct deps installed, no prohibited deps)
- [ ] `pyproject.toml` exists with Black, Ruff, pytest, and mypy configuration
- [ ] `.env.example` contains NO real API keys or secrets
- [ ] `.gitignore` excludes `.venv`, `.env`, `__pycache__`, and tool caches
- [ ] Project directory structure matches §Project Structure above
- [ ] `black --check src/ tests/` passes with zero reformatting needed
- [ ] `ruff check src/ tests/` passes with zero violations
