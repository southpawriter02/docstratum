# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## [0.2.0d] - 2026-02-11

**Token Estimation -- Parser pipeline stage 4 (final).**

### Added

- `_estimate_section_tokens(doc)` -- sets `estimated_tokens = len(raw_content) // 4` on every `ParsedSection` (chars / 4 heuristic)
- Integrated as Phase 6 at end of `populate()` in `populator.py`
- 6 new tests in `test_parser_populator.py` (empty, short, 1000-char, floor rounding, doc >= section sum, all-sections check)

### Notes

- **Verification:** `black --check` (zero reformatting), `ruff check` (zero violations), 32 tests passing (26 v0.2.0c + 6 v0.2.0d).
- **Parser pipeline complete:** v0.2.0a-d all implemented.

---

## [0.2.0c] - 2026-02-11

**Model Population — Parser pipeline stage 3.**

### Added

#### Populator (`src/docstratum/parser/populator.py`)

- `populate(tokens, *, raw_content, source_filename) -> ParsedLlmsTxt` — 5-phase sequential walker: H1 extraction, blockquote collection, body consumption, section/link building (with code fence state tracking), and final assembly (v0.2.0c)
- `_parse_link_entry(token) -> ParsedLink | None` — Regex-based link parser extracting title, URL, and optional description from `- [title](url): desc` format
- `_is_syntactically_valid_url(url) -> bool` — Scheme+netloc or relative-path check (syntactic only, reachability is v0.3.2b)
- `LINK_PATTERN` — Compiled regex: `r'^- \[([^\]]*)\]\(([^)]*)\)(?::\s*(.*))?$'`

#### Parser Package (`src/docstratum/parser/__init__.py`)

- Added re-export for `populate`

#### Tests

- `tests/test_parser_populator.py` — 26 tests covering empty/minimal streams, blockquote extraction (multiline, bare, missing, raw preservation), section building (single/multiple/empty), link parsing (with/without description, empty URL/title, malformed), URL validation (absolute/relative/dotrelative/invalid/empty), code fence suppression, and assembly (source_filename, raw_content, parsed_at)

### Notes

- **Verification:** `black --check` (zero reformatting), `ruff check` (zero violations), 26 tests passing, `populator.py` at 95% coverage.
- **Spec reference:** Traces to v0.0.1a §Reference Parser Phases 1-5 and §Edge Cases A1-C10.

---

## [0.2.0b] - 2026-02-11

**Markdown Tokenization — Parser pipeline stage 2.**

### Added

#### Token Definitions (`src/docstratum/parser/tokens.py`)

- `TokenType(StrEnum)` — 8 structural token types: `H1`, `H2`, `H3_PLUS`, `BLOCKQUOTE`, `LINK_ENTRY`, `CODE_FENCE`, `BLANK`, `TEXT` (v0.2.0b)
- `Token(BaseModel)` — 3-field Pydantic model: `token_type`, `line_number` (1-indexed, ge=1), `raw_text` (v0.2.0b)

#### Tokenizer (`src/docstratum/parser/tokenizer.py`)

- `tokenize(content: str) -> list[Token]` — Line-by-line Markdown tokenizer with code fence state machine, priority-ordered prefix matching (code fence > H3+ > H2 > H1 > blockquote > link entry > blank > text), 1-indexed line numbers, and raw text preservation (v0.2.0b)

#### Parser Package (`src/docstratum/parser/__init__.py`)

- Added re-exports for `Token`, `TokenType`, and `tokenize`

#### Tests

- `tests/test_parser_tokenizer.py` — 23 tests covering all 8 token types, code fence state toggling/suppression/unclosed fences, classification priority ordering, tab-indented headings, empty content, line number tracking, full document tokenization, and raw text preservation

### Notes

- **Verification:** `black --check` (zero reformatting), `ruff check` (zero violations), 23 tests passing, `tokenizer.py` and `tokens.py` both at 100% coverage.
- **Spec reference:** Traces to v0.0.1a §ABNF Grammar (lines 74-127) and v0.0.1a §Reference Parser Design Phases 1-4.

## [0.2.0a] - 2026-02-11

**File I/O & Encoding Detection — Parser pipeline stage 1.**

### Added

#### Parser I/O Module (`src/docstratum/parser/io.py`)

- `FileMetadata(BaseModel)` — 7-field Pydantic model for file-level encoding metadata: `byte_count`, `encoding`, `has_bom`, `has_null_bytes`, `line_ending_style`, `line_count`, `decoding_error` (v0.2.0a)
- `read_file(path: str) -> tuple[str, FileMetadata]` — Read file from disk with encoding detection, BOM handling, and line ending normalization
- `read_string(content: str) -> tuple[str, FileMetadata]` — Wrap raw string with metadata for pipeline compatibility
- `read_bytes(data: bytes) -> tuple[str, FileMetadata]` — Full encoding detection pipeline: UTF-8 BOM, null byte scan, UTF-8→Latin-1 fallback, line ending detection and normalization

#### Parser Package (`src/docstratum/parser/__init__.py`)

- New `parser` subpackage with re-exports for `FileMetadata`, `read_file`, `read_string`, `read_bytes`

#### Tests

- `tests/test_parser_io.py` — 19 tests covering UTF-8, UTF-8+BOM, Latin-1 fallback, null byte detection, all 4 line ending styles (LF/CRLF/CR/mixed), line ending normalization, empty files, whitespace-only files, FileNotFoundError, line count, and FileMetadata model constraints

### Notes

- **Verification:** `black --check` (zero reformatting), `ruff check` (zero violations), 19 tests passing, `parser/io.py` at 100% coverage.
- **Spec reference:** Traces to v0.0.1a §Edge Cases Category D (D1-D5) and v0.0.4a §4 (File Format Requirements).

---

## [0.1.5] - 2026-02-09

**Test Infrastructure — Test suite, fixtures, and CI enforcement.**

### Added

- `tests/test_enrichment.py` — 52 tests covering all 6 enrichment models, field constraints, pattern validation, and public API importability (v0.1.5a)
- `tests/test_pipeline.py` — Stage contract tests and helper function tests for all 5 pipeline stages (v0.1.5b)
- `tests/test_pipeline_integration.py` — End-to-end pipeline integration tests on 8 ecosystem fixtures (v0.1.5c)
- `tests/fixtures/` — 8 synthetic ecosystem fixture directories for multi-file validation testing

### Notes

- **Verification:** 324 tests passing, 93.58% coverage (≥80% floor enforced), all schema modules at 100%.

---

## [0.1.4] - 2026-02-09

**Ecosystem Pipeline Infrastructure — 5-stage ecosystem pipeline with orchestration.**

### Added

#### Pipeline Contracts (`src/docstratum/pipeline/stages.py`, `__init__.py`)

- `PipelineStage` protocol — standard interface for pipeline stages (v0.1.4a)
- `PipelineContext` — stage-shared state container with `SingleFileValidator` protocol
- `StageResult` — per-stage output with timing, diagnostics, and artifacts
- `StageTimer` — context manager for stage execution timing

#### Discovery Stage (`src/docstratum/pipeline/discovery.py`)

- `DiscoveryStage` — Stage 1: filesystem traversal, `classify_filename()`, E009/I010 emission (v0.1.4b)

#### Relationship Stage (`src/docstratum/pipeline/relationship.py`)

- `RelationshipStage` — Stage 3: link extraction and relationship classification (v0.1.4c)

#### Ecosystem Validator (`src/docstratum/pipeline/ecosystem_validator.py`)

- `EcosystemValidationStage` — Stage 4: 6 ecosystem anti-patterns, W012–W018 emission (v0.1.4d)

#### Ecosystem Scorer (`src/docstratum/pipeline/ecosystem_scorer.py`)

- `ScoringStage` — Stage 5: Completeness + Coverage dimension scoring (v0.1.4e)

#### Pipeline Orchestrator (`src/docstratum/pipeline/orchestrator.py`)

- `EcosystemPipeline.run()` — stoppable 5-stage execution with single-file backward compatibility (v0.1.4f)

---

## [0.1.3] - 2026-02-09

**Output & Governance Specifications — Design specifications for output, remediation, profiles, and scoring calibration.**

> These are _specification documents_ (design contracts), not code implementations.
> The code for these features arrives in later versions (v0.5.x–v0.8.x).

### Added

#### Specification Documents (`docs/design/02-foundation/`)

- `RR-SPEC-v0.1.3-output-tier-specification.md` — 4-tier output model (Pass/Fail → Audience-Adapted), format-tier compatibility matrix, report metadata schema (v0.1.3a)
- `RR-SPEC-v0.1.3-remediation-framework.md` — Priority model, grouping strategy, effort estimation, dependency graph, remediation templates, Tier 3/4 boundary (v0.1.3b)
- `RR-SPEC-v0.1.3-validation-profiles.md` — `ValidationProfile` model, 4 built-in profiles (lint/ci/full/enterprise), tag-based rule composition, inheritance (v0.1.3c)
- `RR-SPEC-v0.1.3-ecosystem-scoring-calibration.md` — 5 health dimensions, weighting formulas, 4 synthetic calibration specimens (ECO-CS-001–004), grade boundaries (v0.1.3d)

---

## [0.1.2d] - 2026-02-10

**Enrichment Models — Semantic extension schema for concepts, few-shot examples, and LLM instructions.**

### Added

#### Enrichment Models (`src/docstratum/schema/enrichment.py`)

- `RelationshipType(StrEnum)` — 5 typed directed relationships for the Concept Graph (DECISION-005): `depends_on`, `relates_to`, `conflicts_with`, `specializes`, `supersedes`
- `ConceptRelationship(BaseModel)` — typed, directed edge with `target_id` (DECISION-004 pattern), `relationship_type`, optional `description` (max 200 chars)
- `Concept(BaseModel)` — Layer 2 semantic concept with 8 fields: `id` (DECISION-004), `name`, `definition` (10–500 chars), `aliases`, `relationships`, `related_page_urls`, `anti_patterns`, `domain`
- `FewShotExample(BaseModel)` — Layer 3 Q&A pair with 8 fields: `id`, `intent`, `question` (min 10), `ideal_answer` (min 50), `concept_ids`, `difficulty` (beginner/intermediate/advanced), `language`, `source_urls`
- `LLMInstruction(BaseModel)` — agent behavior directive with `directive_type` (positive/negative/conditional), `instruction`, `context`, `applies_to_concepts`, `priority` (0–100)
- `Metadata(BaseModel)` — file-level provenance with 7 fields: `schema_version` (semver pattern), `site_name`, `site_url`, `last_updated`, `generator`, `docstratum_version`, `token_budget_tier`

#### Public API

- All 6 enrichment types exported from `docstratum.schema` via `__init__.py`

### Notes

- **Convention:** Uses `X | None` union syntax instead of `Optional[X]` per ruff UP007 (matching v0.1.2b+).
- **Verification:** `black --check` (zero reformatting), `ruff check` (zero violations), 324 tests passing, `enrichment.py` at 100% coverage.

## [0.1.2c] - 2026-02-07

**Validation & Quality Models — Output-side Pydantic models for the validation engine.**

### Added

#### Validation Models (`src/docstratum/schema/validation.py`)

- `ValidationLevel(IntEnum)` — 5-level validation pipeline (L0_PARSEABLE through L4_DOCSTRATUM_EXTENDED), per v0.0.1b validation level definitions
- `ValidationDiagnostic(BaseModel)` — single validation finding with 9 fields (code, severity, message, remediation, line_number, column, context, level, check_id); depends on `DiagnosticCode` and `Severity` from v0.1.2a
- `ValidationResult(BaseModel)` — complete pipeline output with 6 computed properties (total_errors, total_warnings, total_info, is_valid, errors, warnings) and per-level pass/fail tracking

#### Quality Models (`src/docstratum/schema/quality.py`)

- `QualityDimension(StrEnum)` — 3-dimension composite scoring (STRUCTURAL 30pts, CONTENT 50pts, ANTI_PATTERN 20pts), per DECISION-014
- `QualityGrade(StrEnum)` — 5-grade classification (EXEMPLARY 90+, STRONG 70+, ADEQUATE 50+, NEEDS_WORK 30+, CRITICAL 0–29) with `from_score()` classmethod, calibrated against gold standards (v0.0.4b §11.3)
- `DimensionScore(BaseModel)` — per-dimension breakdown with 8 fields and `percentage` computed property (handles zero max_points)
- `QualityScore(BaseModel)` — composite 0–100 score with grade and dimension breakdown, primary output of `docstratum-score`

#### Public API

- All 7 new types exported from `docstratum.schema` via `__init__.py`

> **Style note:** Uses `X | None` union syntax instead of `Optional[X]` for ruff UP007 consistency with v0.1.2b.

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
