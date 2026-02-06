# v0.1.2 — Schema Definition: Validation Engine Models (Parent Overview)

> **Phase:** Foundation (v0.1.x)
> **Status:** DRAFT — Realigned to validation-engine pivot (2026-02-06)
> **Parent:** [v0.1.0 — Project Foundation](RR-SPEC-v0.1.0-project-foundation.md)
> **Goal:** Define the complete Pydantic v2 model hierarchy for the DocStratum validation engine — parsed document models, validation result models, quality scoring models, document type classification, error code registry, enrichment schema, and constants.
> **Traces to:** FR-001, FR-002, FR-003, FR-004, FR-007, FR-008 (v0.0.5a); DECISION-001, -002, -003, -004, -005, -006, -012, -013, -015, -016 (v0.0.4d)

---

## What Changed from the Original v0.1.2

The original v0.1.2 defined four Pydantic models (`LlmsTxt`, `CanonicalPage`, `Concept`, `FewShotExample`) that treated llms.txt as a YAML-based data format for generation output. This was the "generation trap" — modeling what a generated file *should* contain rather than what an existing file *actually* contains.

The realigned v0.1.2 defines **seven schema files** across three model categories:

| Category | Purpose | Files | Models |
|----------|---------|-------|--------|
| **Core (what exists)** | Represent a parsed Markdown llms.txt file | `parsed.py`, `classification.py` | `ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`, `ParsedBlockquote`, `DocumentType`, `DocumentClassification`, `SizeTier` |
| **Validation (what the engine reports)** | Represent validation results, diagnostics, and quality scores | `validation.py`, `quality.py`, `diagnostics.py` | `ValidationLevel`, `ValidationDiagnostic`, `ValidationResult`, `QualityDimension`, `QualityGrade`, `QualityScore`, `DimensionScore`, `DiagnosticCode`, `Severity` |
| **Extended (DocStratum enrichment)** | Represent semantic enrichment that DocStratum adds | `enrichment.py`, `constants.py` | `Metadata`, `Concept`, `ConceptRelationship`, `RelationshipType`, `FewShotExample`, `LLMInstruction`, `CanonicalSectionName`, `AntiPatternID`, `AntiPatternCategory` |

**Why this matters:** The validation engine ingests *Markdown*, not YAML. It produces *diagnostics*, not enriched files. The schema must model the entire validation pipeline from input (parsed Markdown) through processing (validation levels, quality scoring) to output (structured results with error codes).

---

## Model Architecture

```
                        ┌─────────────────────┐
                        │   Raw Markdown File  │
                        │   (llms.txt input)   │
                        └──────────┬──────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   classification.py       │
                    │   DocumentClassification  │
                    │   (Type 1 Index or        │
                    │    Type 2 Full?)           │
                    └──────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────────┐
                    │   parsed.py               │
                    │   ParsedLlmsTxt           │
                    │   ├── ParsedSection[]     │
                    │   │   └── ParsedLink[]    │
                    │   └── ParsedBlockquote    │
                    └──────────┬───────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ validation.py │ │  quality.py   │ │ enrichment.py │
    │ L0→L4 levels  │ │ 0-100 score   │ │ Concepts,     │
    │ Diagnostics   │ │ Grades        │ │ Few-shot,     │
    │ Error codes   │ │ Dimensions    │ │ Instructions  │
    └───────┬───────┘ └───────┬───────┘ └───────────────┘
            │                 │
            ▼                 ▼
    ┌─────────────────────────────────┐
    │   diagnostics.py                │
    │   DiagnosticCode enum           │
    │   (8 errors, 11 warnings,       │
    │    7 informational codes)        │
    └─────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────┐
    │   constants.py                  │
    │   Canonical section names (11)  │
    │   Token budget tiers (3)        │
    │   Anti-pattern registry (22)    │
    └─────────────────────────────────┘
```

---

## Sub-Parts

This specification was split into four sub-parts for maintainability. Each sub-part is a self-contained document with its own header, traces, code blocks, design decisions, and exit criteria.

| Sub-Part | Title | Scope | Files |
|----------|-------|-------|-------|
| [v0.1.2a](RR-SPEC-v0.1.2a-diagnostic-infrastructure.md) | Diagnostic Infrastructure | Shared vocabulary: error codes + constants + cross-reference mapping | `diagnostics.py`, `constants.py` |
| [v0.1.2b](RR-SPEC-v0.1.2b-document-models.md) | Document Models | Input-side: what a parsed file IS | `classification.py`, `parsed.py` |
| [v0.1.2c](RR-SPEC-v0.1.2c-validation-quality-models.md) | Validation & Quality Models | Output-side: how the engine judges a file | `validation.py`, `quality.py` |
| [v0.1.2d](RR-SPEC-v0.1.2d-enrichment-models.md) | Enrichment Models | Extension: what DocStratum adds | `enrichment.py` |

**Dependency order:** v0.1.2a (constants, diagnostics) → v0.1.2b (classification, parsed) → v0.1.2c (validation, quality) → v0.1.2d (enrichment). The dependency root is `diagnostics.py` and `constants.py` — every other schema file may import from these two, but neither imports from any other schema file.

---

## Design Decisions Applied

| ID | Decision | How Applied in v0.1.2 |
|----|----------|----------------------|
| DECISION-001 | Markdown over JSON/YAML | `ParsedLlmsTxt` models parsed Markdown, not YAML structures |
| DECISION-002 | 3-Layer Architecture | Enrichment models map to Layer 2 (Concept) and Layer 3 (Few-Shot) |
| DECISION-004 | Concept ID Format | `Concept.id` uses `^[a-z0-9-]+$` pattern |
| DECISION-005 | Typed Directed Relationships | `ConceptRelationship` with 5 `RelationshipType` values |
| DECISION-006 | Pydantic for Validation | All models use Pydantic v2 `BaseModel` with `Field` constraints |
| DECISION-012 | Canonical Section Names | `CanonicalSectionName` enum with 11 names + alias mapping |
| DECISION-013 | Token Budget Tiers | `TOKEN_BUDGET_TIERS` dict with 3 tiers + anti-pattern thresholds |
| DECISION-014 | Content Weight 50% | `QualityDimension` weights: structural 30, content 50, anti-pattern 20 |
| DECISION-016 | 4-Category Anti-Patterns | `AntiPatternCategory` enum with critical/structural/content/strategic |

---

## Exit Criteria

- [ ] All 7 schema files created and importable
- [ ] `from docstratum.schema import ParsedLlmsTxt, ValidationResult, QualityScore` works
- [ ] All 26 diagnostic codes (8E/11W/7I) defined in `DiagnosticCode` enum
- [ ] All 11 canonical section names defined in `CanonicalSectionName` enum
- [ ] All 22 anti-patterns defined in `ANTI_PATTERN_REGISTRY`
- [ ] `DiagnosticCode.severity` property returns correct `Severity` for all codes
- [ ] `QualityGrade.from_score()` returns correct grades at all thresholds
- [ ] `black --check src/docstratum/schema/` passes
- [ ] `ruff check src/docstratum/schema/` passes
- [ ] `mypy src/docstratum/schema/` passes (or has only expected Pydantic edge cases)
