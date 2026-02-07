# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added

- Schema definition with Pydantic models for llms.txt validation (v0.1.2 — in progress)

---

## [0.1.2b] - 2026-02-06

**Document Models — Input-side Pydantic models for parsed llms.txt files.**

### Added

#### Classification Models (`src/docstratum/schema/classification.py`)

- `DocumentType(StrEnum)` — 3-value enum for document type classification (TYPE_1_INDEX, TYPE_2_FULL, UNKNOWN), based on bimodal distribution research (v0.0.1a Finding 4)
- `SizeTier(StrEnum)` — 5-value enum for token budget tiers (MINIMAL, STANDARD, COMPREHENSIVE, FULL, OVERSIZED), per DECISION-013
- `DocumentClassification(BaseModel)` — classification result model with 6 fields (document_type, size_bytes, estimated_tokens, size_tier, filename, classified_at) and class constant `TYPE_BOUNDARY_BYTES = 256_000`

#### Parsed Document Models (`src/docstratum/schema/parsed.py`)

- `ParsedBlockquote(BaseModel)` — blockquote description model (3 fields: text, line_number, raw), mapping to ABNF `description` rule
- `ParsedLink(BaseModel)` — link entry model (5 fields: title, url, description, line_number, is_valid_url), mapping to ABNF `entry` rule
- `ParsedSection(BaseModel)` — H2 section model (6 fields + 2 computed properties: link_count, has_code_examples), mapping to ABNF `section` rule
- `ParsedLlmsTxt(BaseModel)` — root document model (7 fields + 5 computed properties: section_count, total_links, estimated_tokens, has_blockquote, section_names), representing the complete parsed llms.txt structure per FR-001

#### Schema Exports

- Updated `src/docstratum/schema/__init__.py` with 7 new public exports (DocumentType, SizeTier, DocumentClassification, ParsedBlockquote, ParsedLink, ParsedSection, ParsedLlmsTxt)

#### Tests

- `tests/test_classification.py` — 10 tests covering enum values, model construction, field constraints (ge=0, ge=1), defaults, and public API importability
- `tests/test_parsed.py` — 20 tests covering all 4 parsed models, computed properties, field constraints, and public API importability

### Notes

- **Spec deviation:** `TYPE_BOUNDARY_BYTES` declared as `ClassVar[int]` instead of bare `int` annotation to prevent Pydantic v2 from treating it as a model field. Exit criterion (`== 256_000`) still satisfied.
- **Modernized syntax:** `Optional[X]` replaced with `X | None` throughout to satisfy ruff UP007 rule (project targets Python 3.11+).
- **Pre-existing fix:** Sorted `__all__` in `schema/__init__.py` to resolve pre-existing RUF022 violation from v0.1.2a.
- **Verification:** `black --check` (zero reformatting), `ruff check` (zero violations), 48 tests passing, 94% coverage (classification.py and parsed.py both at 100%).

---

## [0.1.2a] - 2026-02-06

**Diagnostic Infrastructure — Shared vocabulary for the validation engine.**

### Added

#### Diagnostic Codes (`src/docstratum/schema/diagnostics.py`)

- `Severity(StrEnum)` — 3-level severity enum (ERROR, WARNING, INFO)
- `DiagnosticCode(StrEnum)` — 26 diagnostic codes (8 errors E001–E008, 11 warnings W001–W011, 7 informational I001–I007) with docstring-driven message and remediation properties, per FR-004 and NFR-006

#### Constants (`src/docstratum/schema/constants.py`)

- `CanonicalSectionName(StrEnum)` — 11 standard section names from 450+ project frequency analysis (DECISION-012)
- `SECTION_NAME_ALIASES` — 32 alias mappings to canonical names
- `CANONICAL_SECTION_ORDER` — 10-step ordering sequence (v0.0.4a §6)
- `TokenBudgetTier(NamedTuple)` — tier definition with 5 fields (name, min_tokens, max_tokens, use_case, file_strategy)
- `TOKEN_BUDGET_TIERS` — 3 tiers (standard, comprehensive, full), per DECISION-013
- `TOKEN_ZONE_*` — 4 threshold constants (OPTIMAL=20K, GOOD=50K, DEGRADATION=100K, ANTI_PATTERN=500K)
- `AntiPatternCategory(StrEnum)` — 4 severity categories (CRITICAL, STRUCTURAL, CONTENT, STRATEGIC), per DECISION-016
- `AntiPatternID(StrEnum)` — 22 anti-pattern identifiers across 4 categories
- `AntiPatternEntry(NamedTuple)` — registry entry with CHECK-NNN cross-references
- `ANTI_PATTERN_REGISTRY` — 22-entry registry with full v0.0.4c traceability

#### Schema Exports

- `src/docstratum/schema/__init__.py` — re-exports all public API from diagnostics and constants modules (32 names in `__all__`)

#### Tests

- `tests/test_diagnostics.py` — 7 tests covering code counts, severity property, code number extraction, message/remediation content, and value format
- `tests/test_constants.py` — 11 tests covering section names, aliases, ordering, token budget tiers, zone thresholds, and anti-pattern registry integrity

### Notes

- **Verification:** `black --check` (zero reformatting), `ruff check` (zero violations), 18 tests passing, coverage ≥80%.

---

## [0.1.1] - 2026-02-06

**Environment Setup — Foundation phase scaffolding with zero downstream dependencies.**

### Added

#### Project Configuration

- `pyproject.toml` with project metadata and tool configuration:
  - **Black** (line-length 88, Python 3.11 target)
  - **Ruff** (E/F/I/N/W/UP/B/SIM/RUF rule sets, isort with first-party detection)
  - **pytest** (`tests/` testpath, `src/` pythonpath, `--cov=docstratum` with 80% floor)
  - **mypy** (Python 3.11, Pydantic plugin, strict mode with `disallow_untyped_defs`)
- `requirements.txt` — foundation-only runtime dependencies:
  - `pydantic>=2.0.0,<3.0.0` (DECISION-006: Pydantic for schema validation)
  - `PyYAML>=6.0,<7.0` (YAML frontmatter parsing)
  - `mistletoe>=1.3.0,<2.0.0` (DECISION-003: CommonMark-compliant Markdown parsing)
  - `python-dotenv>=1.0.0,<2.0.0` (environment variable loading)
- `requirements-dev.txt` — development toolchain:
  - `pytest>=8.0.0`, `pytest-cov>=4.0.0` (NFR-010: ≥80% coverage)
  - `black>=24.0.0`, `ruff>=0.5.0` (NFR-011: 100% compliance)
  - `mypy>=1.8.0` (type checking with Pydantic v2 plugin)
- `.env.example` — environment variable template with `DOCSTRATUM_LOG_LEVEL=INFO` and commented-out future API key placeholders (no real secrets)
- `.gitignore` — comprehensive exclusions for Python bytecode, virtual environments, IDE files, testing artifacts, tool caches, and OS files

#### Source Package

- `src/docstratum/__init__.py` — package root with `__version__ = "0.1.0"`, `__author__`, and module-level docstring describing the validation engine architecture (parse → classify → validate → score → enrich pipeline)
- `src/docstratum/schema/__init__.py` — schema subpackage placeholder with docstring documenting model categories (parsed, validation, quality, classification, enrichment, constants); actual re-exports deferred to v0.1.2
- `src/docstratum/logging_config.py` — centralized logging configuration per RR-META-logging-standards:
  - `setup_logging(level: str | None = None) -> None` using `logging.basicConfig()`
  - Pipe-delimited format: `%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s`
  - Reads `DOCSTRATUM_LOG_LEVEL` environment variable, defaults to `INFO`
  - Suppresses noisy third-party loggers (`httpx`, `openai`, `langchain`) at WARNING level

#### Test Scaffold

- `tests/__init__.py` — test package init for pytest discovery
- `tests/fixtures/.gitkeep` — empty fixture directory placeholder (fixtures arrive in v0.1.3a)

### Notes

- **Dependency boundary enforced:** No agent/LLM/demo dependencies installed. Verified that `langchain`, `openai`, `anthropic`, `streamlit`, and `neo4j` are all absent from the environment.
- **Spec deviation:** The v0.1.1 spec defined `build-backend = "setuptools.backends._legacy:_Backend"` in `pyproject.toml`, which is not a valid setuptools backend. Corrected to `"setuptools.build_meta"` to enable `pip install -e .`.
- **Verification:** `black --check` (zero reformatting), `ruff check` (zero violations), and all import checks pass on Python 3.11.14.

---

## [0.1.0] - 2026-02-05

**Project Foundation — Research-to-implementation pivot defining the validation engine architecture.**

### Added

- Project foundation spec (RR-SPEC-v0.1.0) documenting the pivot from generation to validation
- Engineering standards:
  - RR-META-testing-standards (pytest, AAA pattern, ≥80% coverage targets)
  - RR-META-logging-standards (stdlib logging, pipe-delimited format, no `print()`)
  - RR-META-commenting-standards (Google docstrings, type hints, TODO format)
  - RR-META-development-workflow (spec-first methodology, version-prefixed commits)
  - RR-META-documentation-requirements (Keep a Changelog, ADR templates)
- Design decision registry (DECISION-001 through DECISION-016)
- Version roadmap: Foundation (v0.1.x) → Data Preparation (v0.2.x) → Logic Core (v0.3.x) → Demo (v0.4.x) → Testing (v0.5.x) → Release (v0.6.x)
