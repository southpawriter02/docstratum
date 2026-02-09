# DocStratum Validator — Version Roadmap

> **Scope:** v0.0.1 through v1.0.0
> **Document Type:** High-Level Version Roadmap
> **Status:** DRAFT
> **Created:** 2026-02-09
> **Last Updated:** 2026-02-09
> **Governed By:** RR-SPEC-v0.1.0 (Project Foundation), DS-MANIFEST v1.0.0 (ASoT Standards)

---

## Purpose

This document aggregates all existing design specifications, functional requirements, and architectural decisions into a single, linear version roadmap for the DocStratum validation engine. Each major version (v0.X.0) represents a milestone with a cohesive deliverable. Minor versions (v0.X.Y) represent incremental capability additions within that milestone. Sub-parts (v0.X.Ya, v0.X.Yb, etc.) represent individually implementable work units.

The roadmap is organized by **what the validator can do at each version**, not by internal module boundaries. Each version builds on the previous, and the validator is usable (at progressively richer capability levels) at each major version boundary.

---

## Versioning Conventions

| Level | Pattern | Meaning | Example |
|-------|---------|---------|---------|
| **Major** | `v0.X.0` | Milestone with cohesive deliverable | `v0.3.0` = Content Validation & Scoring |
| **Minor** | `v0.X.Y` | Incremental capability within milestone | `v0.3.2` = Anti-Pattern Detection |
| **Sub-part** | `v0.X.Ya` | Individually implementable work unit | `v0.3.2a` = Structural Anti-Pattern Checks |
| **Release** | `v1.0.0` | General Availability — stable public API | `v1.0.0` = GA |

**Versioning Rules:**

- Sub-parts within a minor version MAY be implemented in parallel if no dependency exists.
- Sub-parts within a minor version MUST be implemented in order if a dependency chain is noted.
- Minor versions within a major version SHOULD be implemented sequentially.
- Major versions MUST be implemented sequentially (each depends on the previous).

---

## Roadmap Overview

```
v0.0.x  Research & Standards Definition     [COMPLETE]
v0.1.x  Foundation — Schema & Pipeline      [COMPLETE]
v0.2.x  Parser — Markdown → Parsed Model    [NOT STARTED]
v0.3.x  Validation Engine — L0–L3 Checks    [NOT STARTED]
v0.4.x  Quality Scoring — 100-Point System   [NOT STARTED]
v0.5.x  CLI & Profiles                      [NOT STARTED]
v0.6.x  Remediation Framework               [NOT STARTED]
v0.7.x  Ecosystem Integration               [NOT STARTED]
v0.8.x  Report Generation & Output Tiers    [NOT STARTED]
v0.9.x  Extended Validation & Polish         [NOT STARTED]
v1.0.0  General Availability                 [NOT STARTED]
```

---

## Phase 0: Research & Standards (v0.0.x) — COMPLETE

> **Status:** All deliverables complete. 27 research documents, 149 ASoT standard files ratified.

This phase produced the intellectual foundation upon which the validator is built. It is not part of the implementation roadmap but is referenced extensively by all subsequent versions.

### v0.0.1 — Specification Deep Dive

| Sub-part | Title | Deliverable | Status |
|----------|-------|-------------|--------|
| v0.0.1a | Formal Grammar & Parsing Rules | ABNF grammar, 26 error codes, parser pseudocode | COMPLETE |
| v0.0.1b | Specification Gap Analysis | 5 critical gaps (concepts, few-shot, metadata, etc.) | COMPLETE |
| v0.0.1c | Processing Methods Survey | Parser strategies, AST approaches | COMPLETE |
| v0.0.1d | Standards Interplay | Markdown/YAML/JSON compatibility analysis | COMPLETE |

### v0.0.2 — Content Audit

| Sub-part | Title | Deliverable | Status |
|----------|-------|-------------|--------|
| v0.0.2a | Source Discovery & Collection | 24-site catalog across 6 categories | COMPLETE |
| v0.0.2b | Individual Site Audits | Per-site conformance analysis | COMPLETE |
| v0.0.2c | Frequency & Pattern Analysis | Section name frequencies, structural patterns | COMPLETE |
| v0.0.2d | Synthesis & Recommendations | Gold standards, 15 best practices, 7 anti-patterns | COMPLETE |

### v0.0.3 — Ecosystem Survey

| Sub-part | Title | Deliverable | Status |
|----------|-------|-------------|--------|
| v0.0.3a | Tools & Libraries Inventory | 75+ tools, feature matrices, 12 critical gaps | COMPLETE |
| v0.0.3b | Key Players Analysis | Market positioning, adoption trends | COMPLETE |
| v0.0.3c | Related Standards | Markdown spec variants, YAML compatibility | COMPLETE |
| v0.0.3d | Gap Analysis & Positioning | DocStratum's unique value proposition | COMPLETE |

### v0.0.4 — Quality Standards

| Sub-part | Title | Deliverable | Status |
|----------|-------|-------------|--------|
| v0.0.4a | Structural Best Practices | 20 structural checks, canonical ordering, token budgets | COMPLETE |
| v0.0.4b | Content Best Practices | 15 content checks, scoring rubric, quality predictors | COMPLETE |
| v0.0.4c | Anti-Pattern Catalog | 22 anti-patterns across 4 categories | COMPLETE |
| v0.0.4d | Design Decisions | 16 architectural decisions (DECISION-001 through DECISION-016) | COMPLETE |

### v0.0.5 — Requirements Definition

| Sub-part | Title | Deliverable | Status |
|----------|-------|-------------|--------|
| v0.0.5a | Functional Requirements | FR-001 through FR-084 | COMPLETE |
| v0.0.5b | Non-Functional Requirements | NFR-001 through NFR-010 | COMPLETE |

### v0.0.6 — Platinum Standard

| Sub-part | Title | Deliverable | Status |
|----------|-------|-------------|--------|
| v0.0.6 | Platinum Standard Definition | 30 validation criteria, 5 levels, scoring framework | COMPLETE |

### v0.0.7 — Ecosystem Pivot

| Sub-part | Title | Deliverable | Status |
|----------|-------|-------------|--------|
| v0.0.7 | Ecosystem Strategy | Multi-file validation architecture, 6-stage pipeline, 5 health dimensions | COMPLETE |

**Research Outputs Feeding Implementation:**

- 38 diagnostic codes (DS-DC-E001–E010, W001–W018, I001–I010)
- 30 validation criteria (DS-VC-STR-001–009, DS-VC-CON-001–013, DS-VC-APD-001–008)
- 28 anti-patterns (DS-AP-CRIT-001–004, STRUCT-001–005, CONT-001–009, STRAT-001–004, ECO-001–006)
- 5 validation levels (DS-VL-L0–L4)
- 5 scoring specifications (DS-QS-DIM-STR, DIM-CON, DIM-APD, GRADE, GATE)
- 6 calibration specimens (DS-CS-001–006: Svelte 92, Pydantic 90, Vercel 90, Shadcn 89, Cursor 42, NVIDIA 24)
- 16+ design decisions (DECISION-001 through DECISION-016 from research; additional decisions DECISION-024, -025, -029, -030, -031, -036 from ecosystem pivot and subsequent phases)

---

## Phase 1: Foundation (v0.1.x) — COMPLETE

> **Status:** All schema models implemented and tested. Ecosystem pipeline operational.
> **Implementation:** 5,737 source LOC, 4,111 test LOC, ≥80% coverage enforced.
> **Traces To:** FR-001, FR-003, FR-004, FR-007, FR-008, FR-011, FR-067–FR-084

### v0.1.0 — Project Foundation

**Deliverable:** Development environment, project structure, strategic pivot from generator to validator.

| Sub-part | Title | Key Outputs | Spec Reference | Status |
|----------|-------|-------------|----------------|--------|
| v0.1.0 | Project Foundation | pyproject.toml, src/docstratum structure, DECISION-001–016 inherited | RR-SPEC-v0.1.0 | COMPLETE |

### v0.1.1 — Environment Setup

**Deliverable:** Python 3.11+ environment with foundation-only dependencies.

| Sub-part | Title | Key Outputs | Spec Reference | Status |
|----------|-------|-------------|----------------|--------|
| v0.1.1 | Environment Setup | Virtual env, Pydantic 2.x, pytest, black, ruff, mypy | RR-SPEC-v0.1.1 | COMPLETE |

### v0.1.2 — Schema Definition

**Deliverable:** Complete Pydantic model layer for all validation concepts.

| Sub-part | Title | Key Outputs | Spec Reference | Status |
|----------|-------|-------------|----------------|--------|
| v0.1.2a | Diagnostic Infrastructure | `DiagnosticCode` (38 codes), `Severity`, `constants.py` (11 sections, 3 token tiers, 28 anti-patterns) | RR-SPEC-v0.1.2a | COMPLETE |
| v0.1.2b | Document Models | `DocumentType`, `SizeTier`, `DocumentClassification`, `ParsedLlmsTxt`, `ParsedSection`, `ParsedLink` | RR-SPEC-v0.1.2b | COMPLETE |
| v0.1.2c | Validation & Quality Models | `ValidationLevel` (L0–L4), `ValidationResult`, `QualityScore`, `QualityGrade`, `DimensionScore` | RR-SPEC-v0.1.2c | COMPLETE |
| v0.1.2d | Enrichment Models | `Concept`, `FewShotExample`, `LLMInstruction`, `Metadata`, `RelationshipType` | RR-SPEC-v0.1.2d | COMPLETE |

### v0.1.3 — Output & Governance Specifications

**Deliverable:** Design specifications for output tiers, remediation, profiles, and ecosystem scoring. These are *specifications* (documents), not implementations — the code comes in later versions.

| Sub-part | Title | Key Outputs | Spec Reference | Status |
|----------|-------|-------------|----------------|--------|
| v0.1.3a | Output Tier Specification | 4-tier output model (Pass/Fail, Diagnostic, Playbook, Adapted), format-tier matrix | RR-SPEC-v0.1.3-output-tier-specification | COMPLETE |
| v0.1.3b | Remediation Framework | Priority model, grouping strategy, YAML templates, dependency graph, `RemediationAction` model | RR-SPEC-v0.1.3-remediation-framework | COMPLETE |
| v0.1.3c | Validation Profiles | `ValidationProfile` model, 4 built-in profiles (lint/ci/full/enterprise), tag buffet composition | RR-SPEC-v0.1.3-validation-profiles | COMPLETE |
| v0.1.3d | Ecosystem Scoring Calibration | 5 health dimensions, 4 synthetic specimens, grade boundaries, sensitivity analysis | RR-SPEC-v0.1.3-ecosystem-scoring-calibration | COMPLETE |

### v0.1.4 — Ecosystem Pipeline Infrastructure

**Deliverable:** 5-stage ecosystem pipeline with orchestration, ready for single-file validator plug-in.

| Sub-part | Title | Key Outputs | Spec Reference | Status |
|----------|-------|-------------|----------------|--------|
| v0.1.4a | Pipeline Contracts | `PipelineStage` protocol, `PipelineContext`, `StageResult`, `StageTimer`, `SingleFileValidator` protocol | v0.0.7 §7 | COMPLETE |
| v0.1.4b | Discovery Stage | Stage 1: `DiscoveryStage`, `classify_filename()`, E009/I010 emission | v0.0.7 §7.1 (FR-074, FR-075) | COMPLETE |
| v0.1.4c | Relationship Stage | Stage 3: `RelationshipStage`, link extraction, relationship classification | v0.0.7 §7.3 (FR-076, FR-077) | COMPLETE |
| v0.1.4d | Ecosystem Validator | Stage 4: `EcosystemValidationStage`, 6 ecosystem anti-patterns, W012–W018 emission | v0.0.7 §7.4 (FR-079) | COMPLETE |
| v0.1.4e | Ecosystem Scorer | Stage 5: `ScoringStage`, Completeness + Coverage dimensions | v0.0.7 §7.5 (FR-081, FR-082) | COMPLETE |
| v0.1.4f | Pipeline Orchestrator | `EcosystemPipeline.run()`, stoppable execution, single-file backward compat | v0.0.7 §7, §10 (FR-083, FR-084) | COMPLETE |

### v0.1.5 — Test Infrastructure

**Deliverable:** Test suite, fixtures, and CI enforcement.

| Sub-part | Title | Key Outputs | Spec Reference | Status |
|----------|-------|-------------|----------------|--------|
| v0.1.5a | Schema Unit Tests | 8 test modules for all schema classes | RR-META-testing-standards | COMPLETE |
| v0.1.5b | Pipeline Unit Tests | Stage contract tests, helper function tests | RR-META-testing-standards | COMPLETE |
| v0.1.5c | Integration Tests | End-to-end pipeline on 8 ecosystem fixtures | RR-META-testing-standards | COMPLETE |

---

## Phase 2: Parser (v0.2.x) — NOT STARTED

> **Goal:** Parse raw Markdown `llms.txt` files into the `ParsedLlmsTxt` model.
> **At This Version:** User can feed a file and get a parsed representation with structural metadata.
> **Traces To:** FR-001, FR-011; DECISION-001, DECISION-003; v0.0.1a (ABNF grammar)
> **Depends On:** v0.1.x (schema models, `ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`)

### v0.2.0 — Core Parser

**Deliverable:** Markdown parser that transforms raw `llms.txt` content into a populated `ParsedLlmsTxt` model.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.2.0a | File I/O & Encoding Detection | Read files from disk or URL. Detect UTF-8/UTF-16/ASCII encoding, handle BOM. Validate line endings (LF vs CRLF). | `read_file()`, `detect_encoding()`, encoding validation |
| v0.2.0b | Markdown Tokenization | Use mistletoe (DECISION-003) to tokenize raw Markdown into an AST. Extract H1, H2, blockquotes, links, code blocks. | `tokenize_markdown()`, AST traversal |
| v0.2.0c | Model Population | Walk the AST and populate `ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`, `ParsedBlockquote`. Apply "permissive input, strict output" principle (v0.0.1a). | `parse_llms_txt()` → `ParsedLlmsTxt` |
| v0.2.0d | Token Estimation | Calculate estimated token counts per section and total. Apply the `bytes / 4` heuristic (DECISION-013). | `estimated_tokens` property population |

### v0.2.1 — Classification & Metadata

**Deliverable:** Automatic document type classification and metadata extraction.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.2.1a | Document Type Classification | Classify as TYPE_1_INDEX, TYPE_2_FULL, TYPE_3_CONTENT_PAGE, or TYPE_4_INSTRUCTIONS based on filename, size, and content heuristics. | `classify_document()` → `DocumentClassification` |
| v0.2.1b | Size Tier Assignment | Assign MINIMAL/STANDARD/COMPREHENSIVE/FULL/OVERSIZED based on token count thresholds (DECISION-013). | `SizeTier` assignment |
| v0.2.1c | Canonical Section Matching | Match parsed section names against the 11 canonical names + 32 aliases (DECISION-012). | `ParsedSection.canonical_name` population |
| v0.2.1d | Metadata Extraction | Extract YAML frontmatter if present. Populate `Metadata` model fields (schema_version, site_name, site_url, last_updated, generator). | `extract_metadata()` → `Metadata` |

### v0.2.2 — Parser Testing & Calibration

**Deliverable:** Parser validated against real-world specimens and synthetic fixtures.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.2.2a | Synthetic Test Fixtures | Create 5 synthetic `llms.txt` files at each conformance level (L0 fail, L1, L2, L3, L4). | 5 test fixture files |
| v0.2.2b | Real-World Specimen Parsing | Parse the 6 calibration specimens (Svelte, Pydantic, Vercel, Shadcn, Cursor, NVIDIA) and verify parsed output matches expected structure. | Calibration validation tests |
| v0.2.2c | Edge Case Coverage | Test all 25+ edge cases from v0.0.1a: missing H1, multiple H1, no blockquote, malformed links, mixed line endings, BOM handling, empty file, oversized file. | Edge case test suite |
| v0.2.2d | SingleFileValidator Integration | Implement the `SingleFileValidator` protocol so the parser plugs into the ecosystem pipeline's Stage 2 (`PerFileStage`). | `SingleFileValidator` implementation, Stage 2 integration tests |

---

## Phase 3: Validation Engine (v0.3.x) — NOT STARTED

> **Goal:** Implement the L0–L3 single-file validation pipeline that emits diagnostics.
> **At This Version:** User gets a diagnostic report listing every issue found in their file, with severity, line numbers, and remediation hints.
> **Traces To:** FR-003, FR-004, FR-006, FR-008; DS-VL-L0–L3; DS-VC-STR-001–009, DS-VC-CON-001–013
> **Depends On:** v0.2.x (parser produces `ParsedLlmsTxt`)

### v0.3.0 — L0 Validation (Parseable Gate)

**Deliverable:** Binary gate — can this file be read and parsed as Markdown at all?

| Sub-part | Title | Description | Diagnostic Codes Emitted |
|----------|-------|-------------|--------------------------|
| v0.3.0a | Encoding Validation | Verify UTF-8 encoding (DECISION-003). Reject non-UTF-8 files. | E003 (INVALID_ENCODING) |
| v0.3.0b | Line Ending Validation | Verify consistent LF line endings. Flag CRLF or mixed. | E004 (INVALID_LINE_ENDINGS) |
| v0.3.0c | Markdown Parse Validation | Verify file parses as valid CommonMark 0.30 + GFM. | E005 (INVALID_MARKDOWN) |
| v0.3.0d | Empty File Detection | Reject zero-byte or whitespace-only files. | E007 (EMPTY_FILE) |
| v0.3.0e | Size Limit Enforcement | Reject files exceeding 100K tokens (anti-pattern threshold). | E008 (EXCEEDS_SIZE_LIMIT) |

**L0 Gate Behavior:** If ANY L0 check fails, the pipeline STOPS. No further validation is meaningful on an unparseable file. The composite quality score is capped at 29 (CRITICAL grade) per DS-QS-GATE.

### v0.3.1 — L1 Validation (Structural)

**Deliverable:** Structural checks verifying the file follows the `llms.txt` specification format.

| Sub-part | Title | Description | Criteria | Diagnostic Codes |
|----------|-------|-------------|----------|------------------|
| v0.3.1a | H1 Title Checks | Verify exactly one H1 heading exists. | DS-VC-STR-001 (5 pts), DS-VC-STR-002 (5 pts) | E001 (NO_H1_TITLE), E002 (MULTIPLE_H1) |
| v0.3.1b | Blockquote Check | Verify description blockquote exists after H1. | DS-VC-STR-003 (4 pts) | W001 (MISSING_BLOCKQUOTE) |
| v0.3.1c | Section Structure | Verify H2-delimited sections exist. No H3+ used as section headers. | DS-VC-STR-004 (4 pts), DS-VC-STR-006 (5 pts) | (implicit structural diagnostics) |
| v0.3.1d | Link Format Compliance | Verify links use `[text](url)` format per ABNF grammar. | DS-VC-STR-005 (4 pts) | E006 (BROKEN_LINKS) — format aspect |

**L1 Structural Points:** 22 / 30 structural points available at this level.

### v0.3.2 — L2 Validation (Content Quality)

**Deliverable:** Content quality checks verifying the documentation is meaningful and useful.

| Sub-part | Title | Description | Criteria | Diagnostic Codes |
|----------|-------|-------------|----------|------------------|
| v0.3.2a | Description Quality | Verify link descriptions are non-empty and substantive. Detect placeholder text ("TBD", "TODO", "Lorem ipsum"). | DS-VC-CON-001 (3 pts), DS-VC-CON-003 (3 pts) | W003 (LINK_MISSING_DESCRIPTION) |
| v0.3.2b | URL Validation | Syntax validation of all URLs. Optionally resolve URLs via HTTP (DNS + status check). | DS-VC-CON-002 (4 pts) | E006 (BROKEN_LINKS) — resolution aspect |
| v0.3.2c | Section Content Quality | Detect empty sections, duplicate sections, and formulaic/auto-generated descriptions. | DS-VC-CON-004 (4 pts), DS-VC-CON-005 (4 pts), DS-VC-CON-007 (3 pts) | W011 (EMPTY_SECTIONS), W006 (FORMULAIC_DESCRIPTIONS) |
| v0.3.2d | Blockquote Quality | Verify blockquote is substantive (not just a project name or single word). | DS-VC-CON-006 (4 pts) | (enhanced W001 context) |

**L2 Content Points:** 25 / 50 content points available at this level.

### v0.3.3 — L3 Validation (Best Practices)

**Deliverable:** Best practice checks verifying the documentation follows recommended patterns from the research phase.

| Sub-part | Title | Description | Criteria | Diagnostic Codes |
|----------|-------|-------------|----------|------------------|
| v0.3.3a | Canonical Section Names | Check section names against 11 canonical names + 32 aliases (DECISION-012). | DS-VC-CON-008 (4 pts) | W002 (NON_CANONICAL_SECTION_NAME) |
| v0.3.3b | Master Index Presence | Check for a Master Index / TOC section. Research evidence: 87% vs 31% LLM success rate (DECISION-010). | DS-VC-CON-009 (5 pts) | W009 (NO_MASTER_INDEX) |
| v0.3.3c | Code Examples & Language | Check for presence of fenced code blocks with language specifiers. Research evidence: strongest quality predictor (r ≈ 0.65). | DS-VC-CON-010 (5 pts), DS-VC-CON-011 (3 pts) | W004 (NO_CODE_EXAMPLES), W005 (CODE_NO_LANGUAGE) |
| v0.3.3d | Token Budget & Version | Check token count against budget tier thresholds. Check for version metadata. | DS-VC-CON-012 (4 pts), DS-VC-CON-013 (4 pts) | W010 (TOKEN_BUDGET_EXCEEDED), W007 (MISSING_VERSION_METADATA) |
| v0.3.3e | Structural Best Practices | Canonical section ordering. No critical or structural anti-patterns. | DS-VC-STR-007 (4 pts), DS-VC-STR-008 (2 pts), DS-VC-STR-009 (2 pts) | W008 (SECTION_ORDER_NON_CANONICAL) |

**L3 Points:** 8 structural + 25 content = 33 points available at this level.

### v0.3.4 — Single-File Anti-Pattern Detection

**Deliverable:** Detect the 22 single-file anti-patterns defined in the ASoT standards.

| Sub-part | Title | Description | Anti-Patterns Detected |
|----------|-------|-------------|----------------------|
| v0.3.4a | Critical Anti-Patterns | Hard gates: Ghost File, Structure Chaos, Encoding Disaster, Link Void. Detection triggers DS-QS-GATE (cap score at 29). | AP-CRIT-001 through AP-CRIT-004 |
| v0.3.4b | Structural Anti-Patterns | Sitemap Dump, Orphaned Sections, Duplicate Identity, Section Shuffle, Naming Nebula. | AP-STRUCT-001 through AP-STRUCT-005 |
| v0.3.4c | Content Anti-Patterns | Copy-Paste Plague, Blank Canvas, Jargon Jungle, Link Desert, Outdated Oracle, Example Void, Formulaic Description, Silent Agent, Versionless Drift. | AP-CONT-001 through AP-CONT-009 |
| v0.3.4d | Strategic Anti-Patterns | Automation Obsession, Monolith Monster, Meta-Documentation Spiral, Preference Trap. | AP-STRAT-001 through AP-STRAT-004 |

### v0.3.5 — Validation Pipeline Assembly

**Deliverable:** Compose L0–L3 checks into a sequential pipeline that produces a `ValidationResult`.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.3.5a | Level Sequencing | Wire L0 → L1 → L2 → L3 with gate-on-failure semantics. L0 failure stops everything. | `validate_file()` → `ValidationResult` |
| v0.3.5b | Diagnostic Aggregation | Collect all `ValidationDiagnostic` instances, determine `level_achieved`, populate `levels_passed` map. | `ValidationResult` fully populated |
| v0.3.5c | Validation Unit Tests | Test each level independently and in combination. Test gate behavior (L0 failure = no L1 checks). | ≥85% coverage on validation module |
| v0.3.5d | Calibration Specimen Validation | Run the 6 real-world specimens through the pipeline. Verify `level_achieved` matches expected (Svelte = L3+, NVIDIA = L0/L1). | Calibration regression tests |

---

## Phase 4: Quality Scoring (v0.4.x) — NOT STARTED

> **Goal:** Implement the 100-point composite quality scoring engine.
> **At This Version:** User gets a numeric score (0–100), a letter grade (EXEMPLARY → CRITICAL), and per-dimension breakdown for any `llms.txt` file.
> **Traces To:** FR-007; DECISION-014; DS-QS-DIM-STR, DS-QS-DIM-CON, DS-QS-DIM-APD, DS-QS-GRADE, DS-QS-GATE
> **Depends On:** v0.3.x (validation pipeline produces `ValidationResult` with diagnostics)

### v0.4.0 — Dimension Scoring

**Deliverable:** Calculate per-dimension scores from validation diagnostics.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.4.0a | Structural Dimension | Sum points from DS-VC-STR-001 through STR-009. 30 max points, 30% weight. | `DimensionScore(STRUCTURAL)` |
| v0.4.0b | Content Dimension | Sum points from DS-VC-CON-001 through CON-013. 50 max points, 50% weight. Research-backed weighting (DECISION-014). | `DimensionScore(CONTENT)` |
| v0.4.0c | Anti-Pattern Dimension | Deduction-based scoring from DS-VC-APD-001 through APD-008. 20 max points, 20% weight. Start at 20, subtract for detected patterns. | `DimensionScore(ANTI_PATTERN)` |

### v0.4.1 — Composite Scoring & Grading

**Deliverable:** Combine dimension scores into a composite 0–100 score and assign a grade.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.4.1a | Composite Calculation | Sum all three dimension scores. Apply DS-QS-GATE: if any AP-CRIT detected, cap at 29. | `QualityScore.total_score` |
| v0.4.1b | Grade Assignment | Map composite to grade: EXEMPLARY (≥90), STRONG (70–89), ADEQUATE (50–69), NEEDS_WORK (30–49), CRITICAL (<30). | `QualityScore.grade` |
| v0.4.1c | Per-Check Detail Population | Populate `DimensionScore.details` list with pass/fail status for each individual criterion. | Drill-down capability |

### v0.4.2 — Scoring Calibration

**Deliverable:** Validate scoring engine against the 6 gold standard calibration specimens.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.4.2a | Specimen Scoring | Score all 6 specimens: Svelte (expected 92), Pydantic (90), Vercel (90), Shadcn (89), Cursor (42), NVIDIA (24). | Calibration test suite |
| v0.4.2b | Tolerance Analysis | Verify scores within ±3 points of expected. Investigate any outliers. Adjust check point values if calibration fails. | Calibration report |
| v0.4.2c | Grade Boundary Testing | Test edge cases at grade boundaries (29/30, 49/50, 69/70, 89/90). Verify correct grade assignment. | Boundary tests |

---

## Phase 5: CLI & Profiles (v0.5.x) — NOT STARTED

> **Goal:** Provide a command-line interface and configurable validation profiles.
> **At This Version:** User can run `docstratum validate llms.txt` from the terminal and get structured output. Different profiles (lint, ci, full) customize what gets checked.
> **Traces To:** RR-SPEC-v0.1.3 (validation profiles), RR-SPEC-v0.1.3 (output tier spec)
> **Depends On:** v0.4.x (scoring engine produces `QualityScore`)

### v0.5.0 — CLI Foundation

**Deliverable:** Basic command-line interface for single-file validation.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.5.0a | CLI Entry Point | Define `console_scripts` entry point in pyproject.toml. Top-level `docstratum` command with `validate` subcommand. | `docstratum validate <path>` |
| v0.5.0b | Argument Parsing | Accept file path(s), `--profile`, `--max-level`, `--output-format`, `--output-tier`, `--threshold`. | argparse or click CLI |
| v0.5.0c | Exit Codes | Implement Tier 1 exit code convention: 0=pass, 1=structural, 2=content, 3=warnings, 4=ecosystem, 5=score below threshold, 10=pipeline error. | Process exit codes |
| v0.5.0d | Terminal Output | Basic terminal output: file name, score, grade, error/warning/info counts. Colorized severity indicators. | Terminal formatter |

### v0.5.1 — Validation Profiles

**Deliverable:** Named profile system controlling which rules execute and how output is formatted.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.5.1a | Profile Model Implementation | Implement `ValidationProfile` Pydantic model from v0.1.3c spec. Fields: `profile_name`, `max_validation_level`, `enabled_stages`, `rule_tags_include/exclude`, `severity_overrides`, `priority_overrides`, `pass_threshold`, `output_tier`, `output_format`, `grouping_mode`, `extends`. | `ValidationProfile` runtime model |
| v0.5.1b | Built-in Profiles | Implement 4 built-in profiles: `lint` (L0–L1, terminal, structural only), `ci` (L0–L3, JSON, threshold 50), `full` (L0–L4, markdown, all rules), `enterprise` (extends full, HTML, Tier 4). | 4 YAML profile files |
| v0.5.1c | Tag-Based Rule Filtering | Implement the "buffet" composition model. Rules tagged with categories. `rule_tags_include` uses OR semantics. `rule_tags_exclude` always wins. Level gating via `max_validation_level`. | Rule filtering engine |
| v0.5.1d | Profile Inheritance | Implement single-level `extends` field. Child profile overrides parent values for explicitly set fields. | Profile resolution logic |

### v0.5.2 — Profile Discovery & Configuration

**Deliverable:** Profile loading from multiple sources with precedence rules.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.5.2a | Profile Loading | Load profiles from YAML/JSON files. Validate against `ValidationProfile` schema. | `load_profile()` |
| v0.5.2b | Discovery Precedence | Implement precedence: CLI flag > project `.docstratum.yml` > user `~/.docstratum/profiles/` > built-in. | Profile resolution chain |
| v0.5.2c | CLI Override Integration | Allow `--max-level`, `--output-format`, etc. to override loaded profile fields. | CLI-to-profile merge |
| v0.5.2d | Legacy Format Migration | Auto-detect and convert legacy v0.2.4d configuration format to ValidationProfile. | Backward compatibility |

---

## Phase 6: Remediation Framework (v0.6.x) — NOT STARTED

> **Goal:** Transform raw diagnostics into actionable, prioritized remediation guidance.
> **At This Version:** User gets a "playbook" — not just "what's wrong" but "what to do, in what order, and why."
> **Traces To:** RR-SPEC-v0.1.3 (remediation framework), DECISION-024, DECISION-025
> **Depends On:** v0.5.x (CLI and profiles operational)

### v0.6.0 — Priority Model

**Deliverable:** Impact-based priority assignment that supersedes raw severity.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.6.0a | Priority Levels | Implement `RemediationPriority` enum: CRITICAL, HIGH, MEDIUM, LOW. Separate from `Severity` (ERROR/WARNING/INFO). | `RemediationPriority` enum |
| v0.6.0b | Default Priority Assignments | Assign priorities to all 38 diagnostic codes per DECISION-024. Notable overrides: W009 → HIGH (despite WARNING severity), I001 → HIGH (despite INFO severity), W005 → LOW. | Priority lookup table |
| v0.6.0c | Priority Assignment Rules | Implement 4-factor priority calculation: LLM Consumption Impact (research-backed r > 0.3), Gating Effect, Score Weight, Prevalence-Adjusted Effort. | `calculate_priority()` |

### v0.6.1 — Grouping & Effort Estimation

**Deliverable:** Consolidate related diagnostics into logical action items with effort estimates.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.6.1a | Same-Code Consolidation | Group diagnostics with same code in same file into one action item (e.g., 15× W003 → "Add descriptions to 15 links"). | Grouping rules engine |
| v0.6.1b | Anti-Pattern Aggregation | When grouped diagnostics trigger an anti-pattern threshold, attach anti-pattern metadata (e.g., 15× W003 → "Link Desert" AP-CONT-004). | Anti-pattern cross-reference |
| v0.6.1c | Effort Estimation | Assign QUICK_WIN / MODERATE / STRUCTURAL to each action item. Apply promotion rules: QUICK_WIN with N>10 instances → MODERATE, MODERATE with N>20 → STRUCTURAL. | `EffortEstimate` assignment |
| v0.6.1d | Score Impact Projection | Calculate estimated score increase if each action item is completed. Produce `ScoreProjection` (current → after_critical → after_high → after_all). | `score_impact` per action |

### v0.6.2 — Remediation Templates

**Deliverable:** YAML-stored expanded guidance for every diagnostic code.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.6.2a | Template Schema | Define YAML template schema per DECISION-025: `title`, `summary`, `guidance`, `example`, `why_it_matters`, `common_mistakes`, `related_codes`, `anti_pattern`, `effort`, `score_dimension`. | Template schema definition |
| v0.6.2b | Error Templates | Write templates for E001–E010 (10 error codes). | `remediation_templates_errors.yaml` |
| v0.6.2c | Warning Templates | Write templates for W001–W018 (18 warning codes). | `remediation_templates_warnings.yaml` |
| v0.6.2d | Info Templates | Write templates for I001–I010 (10 informational codes). | `remediation_templates_info.yaml` |

### v0.6.3 — Dependency Graph & Sequencing

**Deliverable:** Prerequisite ordering that tells users what to fix first.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.6.3a | Dependency Definitions | Implement the dependency graph from the remediation framework spec. Longest chain: E003 → E005 → E006 → W003 → W006 (5 steps). | Dependency graph data structure |
| v0.6.3b | Topological Sort | Sort action items respecting dependencies. Structural fixes before content. Quick wins before rework. | `sequence_actions()` |
| v0.6.3c | Remediation Playbook Assembly | Assemble `RemediationPlaybook` model: executive summary, score projection, ordered action items, grouping mode, anti-patterns detected. | `RemediationPlaybook` model population |

---

## Phase 7: Ecosystem Integration (v0.7.x) — NOT STARTED

> **Goal:** Wire the single-file validator into the ecosystem pipeline for multi-file analysis.
> **At This Version:** User can point the tool at a project directory and get validation across all `llms.txt` ecosystem files, with cross-file checks and aggregate scoring.
> **Traces To:** v0.0.7 (Ecosystem Pivot); FR-069–FR-084
> **Depends On:** v0.6.x (remediation framework for rich ecosystem reporting)

### v0.7.0 — SingleFileValidator Integration

**Deliverable:** Connect the v0.3.x/v0.4.x validation engine to the existing ecosystem pipeline.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.7.0a | Validator Adapter | Implement `SingleFileValidator` protocol using the v0.3.x validation pipeline + v0.4.x scoring engine. Stage 2 (`PerFileStage`) calls this for each discovered file. | `SingleFileValidatorImpl` |
| v0.7.0b | Per-File Result Storage | Store `ParsedLlmsTxt`, `ValidationResult`, and `QualityScore` on each `EcosystemFile` in `PipelineContext`. | `EcosystemFile` fully populated |
| v0.7.0c | End-to-End Pipeline Test | Run full 5-stage pipeline on the 8 existing ecosystem fixtures. Verify Stage 2 now produces real validation results (not just raw content). | Integration test updates |

### v0.7.1 — Ecosystem Scoring Enhancement

**Deliverable:** Activate the 3 reserved ecosystem health dimensions (Consistency, Token Efficiency, Freshness).

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.7.1a | Consistency Dimension | Detect project name inconsistency (W015), version inconsistency (W016), terminology drift. 20 max points, deduction-based. | `calculate_consistency()` |
| v0.7.1b | Token Efficiency Dimension | Calculate Gini coefficient for token distribution across files. 15 max points. Gini 0.0–0.2 = balanced (14–15 pts), Gini 0.8–1.0 = concentrated (0–3 pts). | `calculate_token_efficiency()` |
| v0.7.1c | Freshness Dimension | Check version metadata presence and consistency. 10 max points, deduction-based. Missing metadata: -2pts/file (cap -6). | `calculate_freshness()` |
| v0.7.1d | 5-Dimension Composite | Reweight ecosystem scoring: Completeness 30%, Coverage 25%, Consistency 20%, Token Efficiency 15%, Freshness 10%. Apply quality floor and bonus rules. | Updated `EcosystemScore` |

### v0.7.2 — Ecosystem Calibration

**Deliverable:** Validate ecosystem scoring against the 4 synthetic calibration specimens.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.7.2a | Specimen Scoring | Score specimens: ECO-CS-001 "Stripe-Like" (expected 96), ECO-CS-002 "Growing Startup" (71), ECO-CS-003 "Neglected Project" (39), ECO-CS-004 "Ghost Ecosystem" (17). | Calibration tests |
| v0.7.2b | Sensitivity Verification | Verify sensitivity scenarios: single broken link drops EXEMPLARY → STRONG, adding low-quality file causes regression, decomposition improves score by ~21 pts. | Sensitivity tests |
| v0.7.2c | CLI Ecosystem Mode | Add `docstratum validate <directory>` support. Auto-detect ecosystem vs. single-file based on input path. | CLI ecosystem support |

---

## Phase 8: Report Generation & Output Tiers (v0.8.x) — NOT STARTED

> **Goal:** Generate rich, formatted reports at all 4 output tiers in all supported formats.
> **At This Version:** User can get output ranging from a CI/CD-friendly JSON blob to a full HTML remediation playbook.
> **Traces To:** RR-SPEC-v0.1.3 (output tier specification); FR-004, NFR-006
> **Depends On:** v0.7.x (ecosystem integration for cross-file context)

### v0.8.0 — Tier 1 & Tier 2 Output

**Deliverable:** Machine-readable pass/fail (Tier 1) and human-readable diagnostic report (Tier 2).

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.8.0a | Tier 1 JSON Formatter | Produce JSON output: `passed`, `exit_code`, `level_achieved`, `total_score`, `grade`, `file_count`, `error_count`, `warning_count`. | JSON Tier 1 formatter |
| v0.8.0b | Tier 1 YAML Formatter | Same data as JSON, serialized as YAML. | YAML Tier 1 formatter |
| v0.8.0c | Tier 2 Terminal Formatter | Colorized terminal output: diagnostics grouped by file, sorted by severity → line number → code. Per-dimension score breakdown. | Terminal Tier 2 formatter |
| v0.8.0d | Tier 2 JSON/YAML Formatters | Full diagnostic data in machine-readable formats. All `ValidationDiagnostic` fields included. | JSON/YAML Tier 2 formatters |
| v0.8.0e | Tier 2 Markdown Formatter | Diagnostic report as Markdown with tables, code blocks for context snippets, and per-dimension breakdown. | Markdown Tier 2 formatter |
| v0.8.0f | Tier 2 HTML Formatter | Same as Markdown but rendered as a self-contained HTML document with inline CSS. | HTML Tier 2 formatter |

### v0.8.1 — Tier 3 Output (Remediation Playbook)

**Deliverable:** Prioritized, grouped, sequenced action plan with score projections.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.8.1a | Playbook Markdown Renderer | Render `RemediationPlaybook` as Markdown: executive summary, score projection chart, action items grouped by priority/level/file/effort. | Markdown Tier 3 renderer |
| v0.8.1b | Playbook JSON Renderer | Full playbook data in JSON for programmatic consumption. | JSON Tier 3 renderer |
| v0.8.1c | Playbook HTML Renderer | Rich HTML with collapsible sections, inline code examples, effort badges, score impact indicators. | HTML Tier 3 renderer |

### v0.8.2 — Tier 4 Output (Audience-Adapted)

**Deliverable:** Tier 3 plus contextual intelligence tailored to the consumer's domain and goals.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.8.2a | Context Profile Schema | Implement `ContextProfile` input: `industry`, `project_type`, `documentation_goals`, `target_audience`, `estimated_project_size`, `comparison_set`. | `ContextProfile` model |
| v0.8.2b | Comparative Analysis | Compare user's scores against calibration specimens and optional comparison set. | Comparative analysis engine |
| v0.8.2c | Domain Recommendations | Generate industry-specific guidance (e.g., fintech → prioritize LLM Instructions, developer tools → prioritize API Reference). | Domain recommendation engine |
| v0.8.2d | Maturity Assessment & Roadmap | Assess documentation maturity relative to benchmarks. Generate phased improvement plan (30/60/90 day). | Maturity model, phased roadmap |
| v0.8.2e | HTML Report Renderer | Comprehensive HTML report combining Tier 3 playbook with Tier 4 contextual intelligence. Primary Tier 4 format. | HTML Tier 4 renderer |

### v0.8.3 — Report Metadata & Traceability

**Deliverable:** Every output artifact includes metadata for audit trail.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.8.3a | Report Metadata Schema | Populate: `report_id` (UUID4), `asot_version`, `engine_version`, `profile_name`, `output_tier`, `output_format`, `validated_at`, `root_path`, `files_validated`, `stages_executed`, `total_duration_ms`, `pass_threshold`. | Metadata on all reports |
| v0.8.3b | Metadata Placement | JSON: top-level `"metadata"` key. Markdown: YAML frontmatter. YAML: top-level `metadata` key. HTML: `<meta>` tags + visible header. Terminal: first 3 lines. | Format-specific placement |

---

## Phase 9: Extended Validation & Polish (v0.9.x) — NOT STARTED

> **Goal:** L4 DocStratum Extended validation, CI/CD integration, performance, and API stabilization.
> **At This Version:** Full validation coverage including DocStratum-specific enrichment checks. Ready for production use in CI/CD pipelines.
> **Traces To:** DS-VL-L4; DS-VC-APD-001–008; v0.0.1b (specification gaps)
> **Depends On:** v0.8.x (report generation for full output capability)

### v0.9.0 — L4 Validation (DocStratum Extended)

**Deliverable:** Checks for DocStratum-specific enrichment features that go beyond baseline `llms.txt`.

| Sub-part | Title | Description | Criteria | Diagnostic Codes |
|----------|-------|-------------|----------|------------------|
| v0.9.0a | LLM Instructions Section | Detect presence and quality of LLM-facing instructions (Stripe pattern). 0% current adoption — strongest differentiator. | DS-VC-APD-001 (3 pts) | I001 (NO_LLM_INSTRUCTIONS) |
| v0.9.0b | Concept Definitions | Detect structured concept definitions with proper ID format (DECISION-004), relationships, aliases. | DS-VC-APD-002 (2 pts) | I002 (NO_CONCEPT_DEFINITIONS) |
| v0.9.0c | Few-Shot Examples | Detect question/answer pairs with intent, difficulty, concept linkage (DECISION-008). | DS-VC-APD-003 (3 pts) | I003 (NO_FEW_SHOT_EXAMPLES) |
| v0.9.0d | Extended Anti-Pattern Checks | Content and strategic anti-patterns at L4: AP-CONT-001–009, AP-STRAT-001–004. | DS-VC-APD-004 (3 pts), DS-VC-APD-005 (3 pts) | (anti-pattern diagnostics) |
| v0.9.0e | Optimization Checks | Token-optimized structure, relative URL minimization, jargon definitions. | DS-VC-APD-006 (2 pts), DS-VC-APD-007 (2 pts), DS-VC-APD-008 (2 pts) | I004 (RELATIVE_URLS_DETECTED), I007 (JARGON_WITHOUT_DEFINITION) |

**L4 Anti-Pattern Points:** 20 / 20 anti-pattern points available at this level.

### v0.9.1 — CI/CD Integration

**Deliverable:** Pre-built integrations for common CI/CD systems.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.9.1a | GitHub Actions Workflow | Reusable workflow template: validate on PR, block merge if score below threshold, post score as PR comment. | `.github/workflows/docstratum.yml` template |
| v0.9.1b | Pre-commit Hook | Pre-commit hook configuration for local validation on commit. | `.pre-commit-config.yaml` template |
| v0.9.1c | Configuration File Support | `.docstratum.yml` project-level config: default profile, custom thresholds, rule overrides. | Config file schema and loader |

### v0.9.2 — Performance & Stability

**Deliverable:** Performance optimization and API surface finalization.

| Sub-part | Title | Description | Key Outputs |
|----------|-------|-------------|-------------|
| v0.9.2a | URL Resolution Caching | Cache HTTP resolution results with TTL. Concurrent URL checking with configurable parallelism. | URL cache layer |
| v0.9.2b | Large File Handling | Lazy parsing for files >50K tokens. Streaming token estimation. Memory-bounded AST traversal. | Large file optimizations |
| v0.9.2c | Public API Stabilization | Define `__all__` exports. Deprecation warnings for any experimental APIs. Semantic versioning commitment. | Stable public API surface |
| v0.9.2d | Error Handling Hardening | Graceful handling of all failure modes: corrupt files, network errors, permission issues, disk full. Structured error responses. | Error handling audit |

---

## v1.0.0 — General Availability

> **Goal:** Stable, documented, production-ready release.
> **At This Version:** Complete validator with all 38 diagnostic codes, all 5 validation levels, all 4 output tiers, configurable profiles, ecosystem support, and CI/CD integration.
> **Depends On:** All of v0.1.x through v0.9.x

### v1.0.0 Release Checklist

| Category | Requirement | Traces To |
|----------|-------------|-----------|
| **Validation** | All 38 diagnostic codes emittable | DS-DC-E001–E010, W001–W018, I001–I010 |
| **Validation** | All 30 validation criteria evaluated | DS-VC-STR-001–009, CON-001–013, APD-001–008 |
| **Validation** | All 5 levels operational (L0–L4) | DS-VL-L0–L4 |
| **Validation** | All 28 anti-patterns detectable | DS-AP-CRIT through ECO |
| **Scoring** | 100-point composite scoring operational | DS-QS-DIM-STR, DIM-CON, DIM-APD |
| **Scoring** | Grade assignment operational | DS-QS-GRADE |
| **Scoring** | Critical gating operational | DS-QS-GATE |
| **Scoring** | Calibration within ±3 points for all 6 specimens | DS-CS-001–006 |
| **Ecosystem** | All 5 health dimensions operational | DS-EH-COV, CONS, COMP, TOK, FRESH |
| **Ecosystem** | All 6 ecosystem anti-patterns detectable | DS-AP-ECO-001–006 |
| **Ecosystem** | 4 synthetic specimens within ±5 points | ECO-CS-001–004 |
| **Output** | All 4 output tiers functional | Tier 1 (Pass/Fail), Tier 2 (Diagnostic), Tier 3 (Playbook), Tier 4 (Adapted) |
| **Output** | All 5 output formats functional | JSON, YAML, Markdown, HTML, Terminal |
| **Profiles** | All 4 built-in profiles functional | lint, ci, full, enterprise |
| **Profiles** | Custom profile loading and inheritance | ValidationProfile model |
| **Remediation** | All 38 remediation templates written | YAML templates per DECISION-025 |
| **Remediation** | Priority model, grouping, sequencing operational | DECISION-024, dependency graph |
| **CLI** | `docstratum validate` operational for files and directories | Console entry point |
| **CI/CD** | GitHub Actions template available | Workflow template |
| **CI/CD** | Pre-commit hook available | Hook configuration |
| **Testing** | ≥85% coverage on schema & validation modules | RR-META-testing-standards |
| **Testing** | ≥80% overall project coverage | pytest-cov enforcement |
| **Testing** | All 6 calibration specimens pass regression | DS-CS-001–006 |
| **Documentation** | README with installation, quick start, usage | RR-META-documentation-requirements |
| **Documentation** | ARCHITECTURE.md with system design | RR-META-documentation-requirements |
| **Documentation** | CHANGELOG.md with version history | Keep a Changelog format |
| **API** | Stable public API with `__all__` exports | Semantic versioning commitment |

---

## Dependency Graph

```
v0.1.x (Foundation) ─────────────────────────────────────────────┐
    │                                                              │
    ▼                                                              │
v0.2.x (Parser) ──► ParsedLlmsTxt populated                      │
    │                                                              │
    ▼                                                              │
v0.3.x (Validation) ──► ValidationResult populated                │
    │                                                              │
    ▼                                                              │
v0.4.x (Scoring) ──► QualityScore populated                       │
    │                                                              │
    ▼                                                              │
v0.5.x (CLI & Profiles) ──► User-facing tool operational          │
    │                                                              │
    ▼                                                              │
v0.6.x (Remediation) ──► RemediationPlaybook generated            │
    │                                                              │
    ▼                                                              │
v0.7.x (Ecosystem) ──► EcosystemPipeline + SingleFileValidator ◄──┘
    │                                                    (wires back to v0.1.4 infrastructure)
    ▼
v0.8.x (Reports) ──► All 4 tiers × 5 formats
    │
    ▼
v0.9.x (Extended & Polish) ──► L4 checks, CI/CD, performance
    │
    ▼
v1.0.0 (GA) ──► Stable release
```

---

## Functional Requirements Traceability

> **Scope Note:** This table focuses on FRs directly relevant to the validation engine. The full project defines FR-001 through FR-084 (with FR-009 through FR-066 covering the original data preparation, content structure, context builder, agent, and demo layer modules from the pre-pivot design). Those FRs are out of scope for this validator-focused roadmap but remain valid for future product extensions.

| FR | Title | Target Version | Phase |
|----|-------|----------------|-------|
| FR-001 | Pydantic models for base structure | v0.1.2b | Foundation |
| FR-002 | Extended schema fields (enrichment) | v0.1.2d | Foundation |
| FR-003 | 5-level validation pipeline | v0.3.0–v0.3.3 + v0.9.0 | Validation + Extended |
| FR-004 | Error reporting with line numbers | v0.3.5 | Validation |
| FR-006 | Clear, actionable error messages | v0.6.2 | Remediation |
| FR-007 | Quality assessment framework (0–100) | v0.4.0–v0.4.1 | Scoring |
| FR-008 | Error code registry (38 codes) | v0.1.2a | Foundation |
| FR-011 | Round-trip serialization | v0.2.0c | Parser |
| FR-067 | Logging at INFO level | v0.1.4a | Foundation |
| FR-069 | DocumentEcosystem model | v0.1.4a | Foundation |
| FR-070 | EcosystemFile model | v0.1.4a | Foundation |
| FR-071 | FileRelationship model | v0.1.4a | Foundation |
| FR-072 | EcosystemScore model | v0.1.4e | Foundation |
| FR-073 | LinkRelationship enum + ParsedLink ext | v0.1.4c | Foundation |
| FR-074 | Directory-based ecosystem discovery | v0.1.4b | Foundation |
| FR-075 | File type classification | v0.1.4b | Foundation |
| FR-076 | Link extraction & relationship mapping | v0.1.4c | Foundation |
| FR-077 | Cross-file link resolution | v0.1.4c | Foundation |
| FR-078 | 12 new ecosystem diagnostic codes | v0.1.2a | Foundation |
| FR-079 | Ecosystem anti-pattern detection | v0.1.4d | Foundation |
| FR-080 | Per-file validation within ecosystem | v0.7.0a | Ecosystem |
| FR-081 | Ecosystem Completeness scoring | v0.1.4e | Foundation |
| FR-082 | Ecosystem Coverage scoring | v0.1.4e | Foundation |
| FR-083 | Backward-compatible single-file mode | v0.1.4f | Foundation |
| FR-084 | Pipeline orchestration (stoppable) | v0.1.4f | Foundation |

---

## Design Decisions Traceability

| Decision | Title | Implemented In | Phase |
|----------|-------|----------------|-------|
| DECISION-001 | Markdown over JSON/YAML | v0.2.0 (parser reads Markdown) | Parser |
| DECISION-003 | GFM as standard | v0.2.0b (mistletoe tokenizer) | Parser |
| DECISION-004 | Concept ID format | v0.9.0b (L4 concept validation) | Extended |
| DECISION-005 | Typed directed relationships | v0.1.2d, v0.1.4c | Foundation |
| DECISION-006 | Pydantic for schema | v0.1.2 (all models) | Foundation |
| DECISION-008 | Example IDs linked to concepts | v0.9.0c (L4 few-shot validation) | Extended |
| DECISION-010 | Master Index priority | v0.3.3b (L3 Master Index check) | Validation |
| DECISION-012 | 11 canonical section names | v0.2.1c, v0.3.3a | Parser, Validation |
| DECISION-013 | Token budget tiers | v0.2.0d, v0.3.3d | Parser, Validation |
| DECISION-014 | Content 50% weighting | v0.4.0b (content dimension) | Scoring |
| DECISION-015 | MCP as target consumer | v0.3.3d (token budgets for context windows) | Validation |
| DECISION-016 | Four-category anti-pattern severity | v0.3.4 (anti-pattern detection) | Validation |
| DECISION-024 | Impact-based priority | v0.6.0 (priority model) | Remediation |
| DECISION-025 | YAML remediation templates | v0.6.2 (template authoring) | Remediation |
| DECISION-029 | Profiles = buffet compositions | v0.5.1 (profile system) | CLI & Profiles |
| DECISION-030 | OR semantics for tags | v0.5.1c (tag filtering) | CLI & Profiles |
| DECISION-031 | Single-level inheritance | v0.5.1d (profile inheritance) | CLI & Profiles |
| DECISION-036 | Same grade thresholds (single + eco) | v0.7.2a (ecosystem calibration) | Ecosystem |

---

## Estimated Effort by Phase

| Phase | Version | Description | Estimated Sub-parts | Estimated Complexity |
|-------|---------|-------------|--------------------:|---------------------:|
| 0 | v0.0.x | Research & Standards | 20+ | COMPLETE |
| 1 | v0.1.x | Foundation | 17 | COMPLETE |
| 2 | v0.2.x | Parser | 12 | MODERATE |
| 3 | v0.3.x | Validation Engine | 18 | HIGH |
| 4 | v0.4.x | Quality Scoring | 9 | MODERATE |
| 5 | v0.5.x | CLI & Profiles | 12 | MODERATE |
| 6 | v0.6.x | Remediation Framework | 11 | HIGH |
| 7 | v0.7.x | Ecosystem Integration | 9 | MODERATE |
| 8 | v0.8.x | Report Generation | 12 | HIGH |
| 9 | v0.9.x | Extended & Polish | 10 | MODERATE |
| GA | v1.0.0 | General Availability | — | LOW (verification) |
| | | **TOTAL (remaining)** | **~93 sub-parts** | |

---

## Notes for Subsequent Detailed Planning

This roadmap is intentionally **high-level**. Each major version (v0.X.0) should receive its own detailed specification document before implementation begins. The sub-parts listed here are directional — during detailed planning, sub-parts may be split, merged, or reordered based on implementation discoveries.

**Key areas where detailed specs already exist:**

- v0.2.x Parser: v0.0.1a (ABNF grammar), v0.0.4a (structural checks)
- v0.3.x Validation: DS-VC-* (30 criteria), DS-VL-* (5 levels), DS-DC-* (38 codes)
- v0.4.x Scoring: DS-QS-* (5 scoring specs), DS-CS-* (6 calibration specimens)
- v0.5.x Profiles: RR-SPEC-v0.1.3-validation-profiles
- v0.6.x Remediation: RR-SPEC-v0.1.3-remediation-framework
- v0.7.x Ecosystem: v0.0.7, RR-SPEC-v0.1.3-ecosystem-scoring-calibration
- v0.8.x Reports: RR-SPEC-v0.1.3-output-tier-specification

**Key areas where detailed specs do NOT yet exist (will need creation before implementation):**

- v0.9.0 L4 validation: Concept definition validation rules, few-shot quality rubric, LLM Instructions scoring
- v0.9.1 CI/CD: GitHub Actions workflow details, pre-commit hook behavior
- v0.9.2 Performance: Benchmarking targets, caching strategy details
- v1.0.0 GA: Release process, documentation plan, migration guide (if breaking changes)
