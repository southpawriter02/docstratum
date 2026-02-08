# RR-META-ASoT: Implementation Strategy for the DocStratum Authoritative Source of Truth

> **Document Type:** Implementation Strategy & Execution Plan
> **Status:** DRAFT
> **Date Created:** 2026-02-08
> **Author:** Ryan + Claude Opus 4.6
> **Applies To:** DocStratum Validation Engine — ASoT Standards Library
> **Supersedes:** None (new document)
> **Blocks:** All validation pipeline implementation (v0.2.x+). No validation code shall be written until ASoT v1.0.0 is ratified.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Motivation](#2-problem-statement--motivation)
3. [Architecture Overview](#3-architecture-overview)
    - 3.1 [Design Principles](#31-design-principles)
    - 3.2 [Directory Hierarchy](#32-directory-hierarchy)
    - 3.3 [Naming Taxonomy](#33-naming-taxonomy)
    - 3.4 [Cross-Reference Strategy](#34-cross-reference-strategy)
    - 3.5 [The Manifest Concept](#35-the-manifest-concept)
    - 3.6 [File Template Architecture](#36-file-template-architecture)
4. [Phase A: Scaffolding](#4-phase-a-scaffolding)
5. [Phase B: Diagnostic Codes](#5-phase-b-diagnostic-codes)
6. [Phase C: Validation Criteria](#6-phase-c-validation-criteria)
7. [Phase D: Supporting Standards](#7-phase-d-supporting-standards)
8. [Phase E: Manifest Ratification](#8-phase-e-manifest-ratification)
9. [Self-Validation Loop](#9-self-validation-loop)
10. [Decision Log](#10-decision-log)
11. [Risk Register](#11-risk-register)
12. [Appendices](#12-appendices)
    - A. [Complete Inventory of Standard Elements](#appendix-a-complete-inventory-of-standard-elements)
    - B. [File Template Specifications](#appendix-b-file-template-specifications)
    - C. [Naming Taxonomy Quick Reference](#appendix-c-naming-taxonomy-quick-reference)
    - D. [Traceability Matrix](#appendix-d-traceability-matrix)

---

## 1. Executive Summary

### 1.1 What Is the ASoT?

The **Authoritative Source of Truth** (ASoT) is a modular, hierarchically organized standards library that serves as the single definitive reference for all validation logic in the DocStratum engine. It is not a single document but a structured collection of atomic standard files — each defining one criterion, one diagnostic code, one design decision, or one anti-pattern — organized into a navigable directory tree with a version-pinned manifest at its root.

### 1.2 Why Now?

The DocStratum project has accumulated a rich body of research across 27 documents (900+ KB) spanning the v0.0.x research phase. This research defines 30 validation criteria (v0.0.6 Platinum Standard), 38 diagnostic codes, 28 anti-patterns, 5 validation levels, 11 canonical section names, 3 token budget tiers, 16 design decisions, and 5 ecosystem health dimensions. However, this knowledge is **distributed across multiple documents with no explicit precedence rules, no ratification status, and no mechanism for validators to programmatically confirm their configuration matches the standard.**

The ASoT consolidates, ratifies, and structures this knowledge so that:

1. **Validators know what to check.** Each validation criterion has an unambiguous pass/fail definition in its own file.
2. **Validators can self-check.** The manifest declares integrity assertions that the pipeline verifies before running.
3. **Results are traceable.** Every validation output is stamped with the ASoT version that produced it.
4. **Changes are auditable.** Individual standard elements can be modified, deprecated, or added without touching unrelated elements.
5. **Context is manageable.** AI collaborators (and human reviewers) can load specific standard files without ingesting the entire corpus.

### 1.3 What This Document Covers

This document defines the **complete implementation strategy** for building the ASoT standards library, organized into five sequential phases:

| Phase | Name | Scope | Estimated Files |
|-------|------|-------|-----------------|
| **A** | Scaffolding | Directory tree, templates, manifest stub, README indexes | ~15 structural files |
| **B** | Diagnostic Codes | All 38 diagnostic code definitions (E001–E010, W001–W018, I001–I010) | 38 standard files + 3 index READMEs |
| **C** | Validation Criteria | All 30 Platinum Standard criteria (L0-01 through L4-08) | 30 standard files + 4 index READMEs |
| **D** | Supporting Standards | Design decisions, anti-patterns, calibration, canonical names, scoring, ecosystem, levels | ~80 standard files + 8 index READMEs |
| **E** | Manifest Ratification | Finalize manifest, integrity assertions, version stamp, declare ASoT v1.0.0 | 1 manifest + verification |

**Total estimated output:** ~170 files comprising the complete ASoT v1.0.0 standards library.

### 1.4 Blocking Constraint

> **CRITICAL:** No validation pipeline code (v0.2.x) shall be implemented until the ASoT v1.0.0 is ratified. The ASoT defines *what* the pipeline validates; building the pipeline before the standard is locked would risk implementing against a moving target. This is a docs-first project.

---

## 2. Problem Statement & Motivation

### 2.1 The Current State

DocStratum's validation requirements are currently defined across these sources:

| Source Document | What It Defines | Status | Location |
|----------------|-----------------|--------|----------|
| RR-SPEC-v0.0.6 (Platinum Standard) | 30 validation criteria across 5 levels | DRAFT | `docs/design/01-research/` |
| RR-SPEC-v0.0.7 (Ecosystem Pivot) | 12 ecosystem diagnostic codes, 6 anti-patterns, 5 ecosystem health dimensions | DRAFT | `docs/design/01-research/` |
| `diagnostics.py` | 38 diagnostic codes with severity, message, remediation | Implemented | `src/docstratum/schema/` |
| `constants.py` | 11 canonical names, 28 anti-patterns, 3 token budget tiers | Implemented | `src/docstratum/schema/` |
| `validation.py` | 5 validation levels, ValidationResult/Diagnostic models | Implemented | `src/docstratum/schema/` |
| `quality.py` | 3 quality dimensions, 5 grade thresholds, scoring weights | Implemented | `src/docstratum/schema/` |
| `classification.py` | 5 document types, 5 size tiers, classification boundary | Implemented | `src/docstratum/schema/` |
| `ecosystem.py` | 5 ecosystem health dimensions, ecosystem models | Implemented | `src/docstratum/schema/` |
| RR-SPEC-v0.1.0 (Foundation) | 16 design decisions (DECISION-001 through DECISION-016) | DRAFT | `docs/design/02-foundation/` |

### 2.2 Problems This Creates

**Problem 1: No single source of truth.** To reconstruct the full validation baseline, a developer (or AI collaborator) must cross-reference 9+ sources. There is no single place to look up "what does criterion L3-02 mean, exactly?"

**Problem 2: Research output ≠ ratified standard.** The v0.0.6 Platinum Standard sits in the `01-research/` folder and is labeled DRAFT. Research informs a standard, but research *is not* the standard. The act of ratification — saying "this is now authoritative" — has not occurred.

**Problem 3: No self-validation mechanism.** When the pipeline is built, there is no way for it to verify that its own configuration (which codes are active, what weights apply, what thresholds are used) matches what the standard prescribes. Configuration drift — where code evolves but documentation doesn't, or vice versa — is undetectable.

**Problem 4: Monolithic context problem.** Loading the full v0.0.6 document (400+ lines) into an AI context window when you only need the definition of one criterion wastes tokens and risks context pollution. The ASoT's modular structure solves this by making each element independently addressable and loadable.

**Problem 5: No change tracking for the standard itself.** If someone updates a diagnostic code's severity or tweaks a scoring weight, there is no mechanism to flag "the standard changed" and stamp prior validation results as potentially stale.

### 2.3 What Success Looks Like

The ASoT is successful when:

1. A developer can answer "what does DocStratum check for criterion X?" by reading exactly one file.
2. The validation pipeline can verify its own configuration against the manifest before running.
3. Every validation result includes an ASoT version stamp (e.g., "Validated against ASoT v1.0.0").
4. A criterion can be modified without touching any other criterion file.
5. The provenance chain from criterion → research document → empirical evidence is preserved in every file.

---

## 3. Architecture Overview

### 3.1 Design Principles

The ASoT architecture is governed by five principles, derived from the problems identified above:

| # | Principle | Rationale |
|---|-----------|-----------|
| **P1** | **Atomic granularity** | Each standard element (criterion, diagnostic code, anti-pattern, etc.) lives in its own file. This makes elements independently addressable, versionable, and loadable. |
| **P2** | **Identifier-based references** | Files reference each other using DS-prefixed identifiers (e.g., "See DS-DC-E001"), not file paths. This decouples logical identity from physical location, so files can be reorganized without breaking cross-references. |
| **P3** | **Manifest as registry** | A central manifest file declares every active standard element, its status, and its location. The pipeline reads this manifest at startup, not the individual files. Individual files are loaded on demand. |
| **P4** | **Provenance is mandatory** | Every standard element must trace back to its research origin. If a criterion cannot cite its source, it doesn't belong in the ASoT. |
| **P5** | **Status lifecycle** | Every element has an explicit status: `DRAFT` → `RATIFIED` → `DEPRECATED`. Only `RATIFIED` elements are enforced by the validation pipeline. `DRAFT` elements are visible but non-blocking. `DEPRECATED` elements remain in the tree (for historical reference) but are excluded from validation. |

### 3.2 Directory Hierarchy

The ASoT lives under the existing meta-documentation path and introduces a `standards/` subtree:

```
docs/design/00-meta/standards/
│
├── README.md                              ← Human-readable overview of the ASoT
├── DS-MANIFEST.md                         ← Version-pinned registry (the keystone)
│
├── criteria/                              ← Validation Criteria (30 from v0.0.6)
│   ├── README.md                          ← Criteria index with dimension/level mapping
│   ├── structural/                        ← Structural dimension (30% weight)
│   │   ├── DS-VC-STR-001-h1-title-present.md
│   │   ├── DS-VC-STR-002-single-h1-only.md
│   │   ├── DS-VC-STR-003-blockquote-present.md
│   │   ├── DS-VC-STR-004-h2-section-structure.md
│   │   ├── DS-VC-STR-005-link-format-compliance.md
│   │   ├── DS-VC-STR-006-no-heading-violations.md
│   │   ├── DS-VC-STR-007-canonical-section-ordering.md
│   │   ├── DS-VC-STR-008-no-critical-anti-patterns.md
│   │   └── DS-VC-STR-009-no-structural-anti-patterns.md
│   ├── content/                           ← Content dimension (50% weight)
│   │   ├── DS-VC-CON-001-non-empty-descriptions.md
│   │   ├── DS-VC-CON-002-url-resolvability.md
│   │   ├── DS-VC-CON-003-no-placeholder-content.md
│   │   ├── DS-VC-CON-004-non-empty-sections.md
│   │   ├── DS-VC-CON-005-no-duplicate-sections.md
│   │   ├── DS-VC-CON-006-substantive-blockquote.md
│   │   ├── DS-VC-CON-007-no-formulaic-descriptions.md
│   │   ├── DS-VC-CON-008-canonical-section-names.md
│   │   ├── DS-VC-CON-009-master-index-present.md
│   │   ├── DS-VC-CON-010-code-examples-present.md
│   │   ├── DS-VC-CON-011-code-language-specifiers.md
│   │   ├── DS-VC-CON-012-token-budget-respected.md
│   │   └── DS-VC-CON-013-version-metadata-present.md
│   └── anti-pattern/                      ← Anti-pattern dimension (20% weight)
│       ├── DS-VC-APD-001-llm-instructions-section.md
│       ├── DS-VC-APD-002-concept-definitions.md
│       ├── DS-VC-APD-003-few-shot-examples.md
│       ├── DS-VC-APD-004-no-content-anti-patterns.md
│       ├── DS-VC-APD-005-no-strategic-anti-patterns.md
│       ├── DS-VC-APD-006-token-optimized-structure.md
│       ├── DS-VC-APD-007-relative-url-minimization.md
│       └── DS-VC-APD-008-jargon-defined-or-linked.md
│
├── diagnostics/                           ← Diagnostic Codes (38 total)
│   ├── README.md                          ← Full index: code → severity → level → criterion
│   ├── errors/                            ← E-series (structural failures, 10 codes)
│   │   ├── DS-DC-E001-NO_H1_TITLE.md
│   │   ├── DS-DC-E002-MULTIPLE_H1.md
│   │   ├── DS-DC-E003-INVALID_ENCODING.md
│   │   ├── DS-DC-E004-INVALID_LINE_ENDINGS.md
│   │   ├── DS-DC-E005-INVALID_MARKDOWN.md
│   │   ├── DS-DC-E006-BROKEN_LINKS.md
│   │   ├── DS-DC-E007-EMPTY_FILE.md
│   │   ├── DS-DC-E008-EXCEEDS_SIZE_LIMIT.md
│   │   ├── DS-DC-E009-NO_INDEX_FILE.md
│   │   └── DS-DC-E010-ORPHANED_ECOSYSTEM_FILE.md
│   ├── warnings/                          ← W-series (quality deviations, 18 codes)
│   │   ├── DS-DC-W001-MISSING_BLOCKQUOTE.md
│   │   ├── DS-DC-W002-NON_CANONICAL_SECTION_NAME.md
│   │   ├── DS-DC-W003-LINK_MISSING_DESCRIPTION.md
│   │   ├── DS-DC-W004-NO_CODE_EXAMPLES.md
│   │   ├── DS-DC-W005-CODE_NO_LANGUAGE.md
│   │   ├── DS-DC-W006-FORMULAIC_DESCRIPTIONS.md
│   │   ├── DS-DC-W007-MISSING_VERSION_METADATA.md
│   │   ├── DS-DC-W008-SECTION_ORDER_NON_CANONICAL.md
│   │   ├── DS-DC-W009-NO_MASTER_INDEX.md
│   │   ├── DS-DC-W010-TOKEN_BUDGET_EXCEEDED.md
│   │   ├── DS-DC-W011-EMPTY_SECTIONS.md
│   │   ├── DS-DC-W012-BROKEN_CROSS_FILE_LINK.md
│   │   ├── DS-DC-W013-MISSING_AGGREGATE.md
│   │   ├── DS-DC-W014-AGGREGATE_INCOMPLETE.md
│   │   ├── DS-DC-W015-INCONSISTENT_PROJECT_NAME.md
│   │   ├── DS-DC-W016-INCONSISTENT_VERSIONING.md
│   │   ├── DS-DC-W017-REDUNDANT_CONTENT.md
│   │   └── DS-DC-W018-UNBALANCED_TOKEN_DISTRIBUTION.md
│   └── info/                              ← I-series (observations, 10 codes)
│       ├── DS-DC-I001-NO_LLM_INSTRUCTIONS.md
│       ├── DS-DC-I002-NO_CONCEPT_DEFINITIONS.md
│       ├── DS-DC-I003-NO_FEW_SHOT_EXAMPLES.md
│       ├── DS-DC-I004-RELATIVE_URLS_DETECTED.md
│       ├── DS-DC-I005-TYPE_2_FULL_DETECTED.md
│       ├── DS-DC-I006-OPTIONAL_SECTIONS_UNMARKED.md
│       ├── DS-DC-I007-JARGON_WITHOUT_DEFINITION.md
│       ├── DS-DC-I008-NO_INSTRUCTION_FILE.md
│       ├── DS-DC-I009-CONTENT_COVERAGE_GAP.md
│       └── DS-DC-I010-ECOSYSTEM_SINGLE_FILE.md
│
├── levels/                                ← Validation Levels (L0–L4)
│   ├── README.md                          ← Level hierarchy and cumulative model
│   ├── DS-VL-L0-PARSEABLE.md
│   ├── DS-VL-L1-STRUCTURAL.md
│   ├── DS-VL-L2-CONTENT_QUALITY.md
│   ├── DS-VL-L3-BEST_PRACTICES.md
│   └── DS-VL-L4-DOCSTRATUM_EXTENDED.md
│
├── scoring/                               ← Quality Scoring Framework
│   ├── README.md                          ← Scoring model overview
│   ├── DS-QS-DIM-STR-structural.md        ← Structural dimension (30%)
│   ├── DS-QS-DIM-CON-content.md           ← Content dimension (50%)
│   ├── DS-QS-DIM-APD-anti-pattern.md      ← Anti-pattern dimension (20%)
│   ├── DS-QS-GRADE-thresholds.md          ← Grade boundaries (0–29, 30–49, 50–69, 70–89, 90–100)
│   └── DS-QS-CAP-structural-gating.md     ← Structural gating rule (CRITICAL caps at 29)
│
├── calibration/                           ← Gold Standard Calibration Specimens
│   ├── README.md                          ← Calibration methodology and specimen list
│   ├── DS-CS-001-svelte-exemplary.md      ← Expected: 92, Grade: Exemplary
│   ├── DS-CS-002-pydantic-exemplary.md    ← Expected: 90, Grade: Exemplary
│   ├── DS-CS-003-vercel-sdk-exemplary.md  ← Expected: 90, Grade: Exemplary
│   ├── DS-CS-004-shadcn-strong.md         ← Expected: 89, Grade: Strong
│   ├── DS-CS-005-cursor-needs-work.md     ← Expected: 42, Grade: Needs Work
│   └── DS-CS-006-nvidia-critical.md       ← Expected: 24, Grade: Critical
│
├── decisions/                             ← Design Decisions (DECISION-001 through DECISION-016)
│   ├── README.md                          ← Decision index with status and impact
│   ├── DS-DD-001-markdown-over-json.md
│   ├── DS-DD-002-three-layer-architecture.md
│   ├── DS-DD-003-gfm-as-standard.md
│   ├── DS-DD-004-concept-id-format.md
│   ├── DS-DD-005-typed-directed-relationships.md
│   ├── DS-DD-006-pydantic-v2-for-schema.md
│   ├── DS-DD-007-document-type-classification.md
│   ├── DS-DD-008-permissive-parser.md
│   ├── DS-DD-009-three-tier-diagnostics.md
│   ├── DS-DD-010-master-index-as-navigation.md
│   ├── DS-DD-011-optional-section-reserved.md
│   ├── DS-DD-012-eleven-canonical-names.md
│   ├── DS-DD-013-token-budget-tiers.md
│   ├── DS-DD-014-content-quality-primary-weight.md
│   ├── DS-DD-015-mcp-as-target-consumer.md
│   └── DS-DD-016-four-category-anti-patterns.md
│
├── anti-patterns/                         ← Anti-Pattern Registry (28 patterns)
│   ├── README.md                          ← Full registry: ID → name → category → severity
│   ├── critical/                          ← Critical (4) — prevent LLM consumption entirely
│   │   ├── DS-AP-CRIT-001-ghost-file.md
│   │   ├── DS-AP-CRIT-002-structure-chaos.md
│   │   ├── DS-AP-CRIT-003-encoding-disaster.md
│   │   └── DS-AP-CRIT-004-link-void.md
│   ├── structural/                        ← Structural (5) — break navigation
│   │   ├── DS-AP-STRUCT-001-sitemap-dump.md
│   │   ├── DS-AP-STRUCT-002-orphaned-sections.md
│   │   ├── DS-AP-STRUCT-003-duplicate-identity.md
│   │   ├── DS-AP-STRUCT-004-section-shuffle.md
│   │   └── DS-AP-STRUCT-005-naming-nebula.md
│   ├── content/                           ← Content (9) — degrade quality
│   │   ├── DS-AP-CONT-001-copy-paste-plague.md
│   │   ├── DS-AP-CONT-002-blank-canvas.md
│   │   ├── DS-AP-CONT-003-jargon-jungle.md
│   │   ├── DS-AP-CONT-004-link-desert.md
│   │   ├── DS-AP-CONT-005-outdated-oracle.md
│   │   ├── DS-AP-CONT-006-example-void.md
│   │   ├── DS-AP-CONT-007-formulaic-description.md
│   │   ├── DS-AP-CONT-008-silent-agent.md
│   │   └── DS-AP-CONT-009-versionless-drift.md
│   ├── strategic/                         ← Strategic (4) — undermine long-term value
│   │   ├── DS-AP-STRAT-001-automation-obsession.md
│   │   ├── DS-AP-STRAT-002-monolith-monster.md
│   │   ├── DS-AP-STRAT-003-meta-documentation-spiral.md
│   │   └── DS-AP-STRAT-004-preference-trap.md
│   └── ecosystem/                         ← Ecosystem (6) — ecosystem-level structural problems
│       ├── DS-AP-ECO-001-index-island.md
│       ├── DS-AP-ECO-002-phantom-links.md
│       ├── DS-AP-ECO-003-shadow-aggregate.md
│       ├── DS-AP-ECO-004-duplicate-ecosystem.md
│       ├── DS-AP-ECO-005-token-black-hole.md
│       └── DS-AP-ECO-006-orphan-nursery.md
│
├── ecosystem/                             ← Ecosystem Health Dimensions (from v0.0.7)
│   ├── README.md                          ← Ecosystem validation model overview
│   ├── DS-EH-COV-coverage.md
│   ├── DS-EH-CON-consistency.md
│   ├── DS-EH-COM-completeness.md
│   ├── DS-EH-TOK-token-efficiency.md
│   └── DS-EH-FRE-freshness.md
│
└── canonical/                             ← Canonical Section Names (11 names, DECISION-012)
    ├── README.md                          ← All canonical names with match patterns/aliases
    ├── DS-CN-001-master-index.md
    ├── DS-CN-002-llm-instructions.md
    ├── DS-CN-003-getting-started.md
    ├── DS-CN-004-core-concepts.md
    ├── DS-CN-005-api-reference.md
    ├── DS-CN-006-examples.md
    ├── DS-CN-007-configuration.md
    ├── DS-CN-008-advanced-topics.md
    ├── DS-CN-009-troubleshooting.md
    ├── DS-CN-010-faq.md
    └── DS-CN-011-optional.md
```

**File count summary:**

| Directory | Standard Files | Index READMEs | Subtotal |
|-----------|---------------|---------------|----------|
| Root | 2 (README, MANIFEST) | — | 2 |
| criteria/ | 30 | 4 (root + 3 dimensions) | 34 |
| diagnostics/ | 38 | 4 (root + 3 severities) | 42 |
| levels/ | 5 | 1 | 6 |
| scoring/ | 5 | 1 | 6 |
| calibration/ | 6 | 1 | 7 |
| decisions/ | 16 | 1 | 17 |
| anti-patterns/ | 28 | 6 (root + 5 categories) | 34 |
| ecosystem/ | 5 | 1 | 6 |
| canonical/ | 11 | 1 | 12 |
| **Total** | **146** | **20** | **166** |

### 3.3 Naming Taxonomy

Every file in the standards tree follows a predictable naming pattern that encodes its type, category, and identity:

**Pattern:** `DS-{TypeCode}-{SubCategory}-{Sequence}-{slug}.md`

| Type Code | Meaning | Sub-Category | Example |
|-----------|---------|--------------|---------|
| **VC** | Validation Criterion | `STR` (Structural), `CON` (Content), `APD` (Anti-Pattern Detection) | `DS-VC-STR-001-h1-title-present.md` |
| **DC** | Diagnostic Code | None (severity is in the existing code: E/W/I) | `DS-DC-E001-NO_H1_TITLE.md` |
| **VL** | Validation Level | None (level number is self-descriptive) | `DS-VL-L0-PARSEABLE.md` |
| **DD** | Design Decision | None (sequential numbering) | `DS-DD-001-markdown-over-json.md` |
| **AP** | Anti-Pattern | `CRIT`, `STRUCT`, `CONT`, `STRAT`, `ECO` | `DS-AP-CONT-007-formulaic-description.md` |
| **EH** | Ecosystem Health | `COV`, `CON`, `COM`, `TOK`, `FRE` | `DS-EH-COV-coverage.md` |
| **QS** | Quality Scoring | `DIM` (Dimension), `GRADE`, `CAP` (Gating) | `DS-QS-DIM-STR-structural.md` |
| **CS** | Calibration Specimen | None (sequential numbering) | `DS-CS-001-svelte-exemplary.md` |
| **CN** | Canonical Name | None (sequential numbering) | `DS-CN-001-master-index.md` |

**Naming rules:**

1. The `DS-` prefix is mandatory on all standard files. It scopes all identifiers to the DocStratum namespace.
2. Slugs use lowercase kebab-case. Diagnostic code slugs use UPPER_SNAKE_CASE to match the existing `DiagnosticCode` enum values.
3. Sequence numbers are zero-padded to 3 digits (e.g., `001`, `012`) to ensure lexicographic sort order matches logical order.
4. The combination of `{TypeCode}-{SubCategory}-{Sequence}` forms the **DS Identifier** — the canonical reference used in cross-references (e.g., `DS-VC-STR-001`, `DS-DC-E007`, `DS-AP-CONT-003`).

### 3.4 Cross-Reference Strategy

Standard files frequently reference each other. A validation criterion file needs to list the diagnostic codes it emits; a diagnostic code file needs to identify which criteria trigger it; an anti-pattern file needs to cite the criteria it affects.

**Rules for cross-references:**

1. **Use DS identifiers, not file paths.** Write `DS-DC-E001` rather than `../diagnostics/errors/DS-DC-E001-NO_H1_TITLE.md`. Identifiers are stable across reorganizations; paths are not.

2. **Each README index maintains a lookup table.** The README in each directory maps DS identifiers to relative file paths, serving as the resolution layer. Example:

    ```markdown
    | DS Identifier | File | Status |
    |---------------|------|--------|
    | DS-DC-E001 | errors/DS-DC-E001-NO_H1_TITLE.md | RATIFIED |
    | DS-DC-E002 | errors/DS-DC-E002-MULTIPLE_H1.md | RATIFIED |
    ```

3. **The manifest is the authoritative resolver.** If a README index and the manifest disagree, the manifest wins. The manifest is the single source of truth *about* the source of truth.

4. **Bidirectional references are encouraged but not required.** If `DS-VC-STR-001` cites `DS-DC-E001`, ideally `DS-DC-E001` also cites `DS-VC-STR-001`. Maintaining bidirectionality is a Phase E integrity assertion (the manifest verifies it).

### 3.5 The Manifest Concept

`DS-MANIFEST.md` is the structural keystone of the entire ASoT. It is the only file that the validation pipeline *must* read at startup. It serves five roles:

**Role 1: Version Declaration**
```markdown
## ASoT Version
- **Current Version:** 1.0.0
- **Version Date:** 2026-02-XX
- **Semantic Versioning:** MAJOR.MINOR.PATCH
  - MAJOR: Breaking changes (criteria removed, scoring weights changed, levels redefined)
  - MINOR: Additive changes (new criteria added, new diagnostic codes)
  - PATCH: Corrections (typos, clarifications, provenance updates)
```

**Role 2: File Registry**

A complete table listing every standard file with its path, type, status, and last-modified date. This is what the pipeline reads to know its complete configuration.

```markdown
## File Registry

| DS Identifier | Type | Path | Status | Modified |
|---------------|------|------|--------|----------|
| DS-VC-STR-001 | Validation Criterion | criteria/structural/DS-VC-STR-001-h1-title-present.md | RATIFIED | 2026-02-XX |
| DS-DC-E001 | Diagnostic Code | diagnostics/errors/DS-DC-E001-NO_H1_TITLE.md | RATIFIED | 2026-02-XX |
| ... | ... | ... | ... | ... |
```

**Role 3: Integrity Assertions**

Self-check rules the pipeline verifies at startup:

```markdown
## Integrity Assertions

| ID | Assertion | Expected |
|----|-----------|----------|
| IA-001 | Count of RATIFIED VC files | 30 |
| IA-002 | Count of RATIFIED DC files | 38 |
| IA-003 | Count of RATIFIED AP files | 28 |
| IA-004 | Sum of structural VC weights | 30 points |
| IA-005 | Sum of content VC weights | 50 points |
| IA-006 | Sum of anti-pattern VC weights | 20 points |
| IA-007 | Every DC file referenced by ≥1 VC file | True |
| IA-008 | Every VC file references ≥1 DC file | True (except composite criteria) |
| IA-009 | Calibration specimen count | ≥5 |
| IA-010 | All calibration specimens have expected scores | True |
```

**Role 4: Provenance Map**

For each standard element, a pointer to the research document that originated the requirement:

```markdown
## Provenance Map

| DS Identifier | Primary Source | Secondary Sources |
|---------------|---------------|-------------------|
| DS-VC-STR-001 | Official llms.txt spec §1 | v0.0.1a ABNF grammar; v0.0.2c audit (24/24 compliance) |
| DS-VC-CON-010 | v0.0.4b CNT-007 | v0.0.2c (r ≈ 0.65 quality correlation) |
```

**Role 5: Change Log**

```markdown
## Change Log

| ASoT Version | Date | Change | Affected Identifiers |
|--------------|------|--------|---------------------|
| 1.0.0 | 2026-02-XX | Initial ratification | All (166 files) |
```

### 3.6 File Template Architecture

Each standard file type has a prescribed internal structure. This ensures consistency, machine-parseability, and human readability. The complete templates are in [Appendix B](#appendix-b-file-template-specifications), but here is the core principle:

Every standard file contains:

1. **Header block** — An H1 title with the DS identifier, followed by a metadata table (ID, status, ASoT version, provenance).
2. **Description** — What this element is and why it matters.
3. **Specification** — The precise, unambiguous definition (pass/fail conditions for criteria; message/remediation for diagnostic codes; detection rules for anti-patterns).
4. **Cross-references** — Links to related elements using DS identifiers.
5. **Change history** — Per-element version tracking.

---

## 4. Phase A: Scaffolding

### 4.1 Objectives

Create the complete directory tree, all README index stubs, the manifest template, and one populated example of each file type (to validate the template before scaling). No substantive standard content is authored in this phase — only structure.

### 4.2 Pre-Conditions

- The `docs/design/00-meta/` directory exists (confirmed).
- The naming taxonomy (Section 3.3) is agreed upon.
- The directory hierarchy (Section 3.2) is agreed upon.
- File templates (Appendix B) are reviewed and approved.

### 4.3 Steps

| Step | Action | Output | Dependencies |
|------|--------|--------|--------------|
| A.1 | Create `docs/design/00-meta/standards/` root directory | Empty directory | None |
| A.2 | Create all subdirectories per hierarchy in §3.2 | 10 directories + subdirectories | A.1 |
| A.3 | Create `README.md` at standards root | Overview document with links to each subdirectory | A.2 |
| A.4 | Create `DS-MANIFEST.md` stub with version 0.0.0-scaffold | Manifest template with empty registry table | A.2 |
| A.5 | Create README.md in each subdirectory (15 total) | Stub indexes with column headers, no data rows | A.2 |
| A.6 | Create one example file per type (9 examples) — see below | Fully populated examples validating each template | A.5 |
| A.7 | Peer-review the examples against Appendix B templates | Reviewed examples with feedback incorporated | A.6 |
| A.8 | Update all README indexes to include the example files | Index tables with one row each | A.7 |
| A.9 | Update manifest to include the 9 example files with status DRAFT | Manifest registry with 9 entries | A.8 |

**Step A.6 — Example file selections:**

These are chosen to represent the most common cross-reference patterns:

| Type | Selected Example | Rationale |
|------|-----------------|-----------|
| Validation Criterion | DS-VC-STR-001 (H1 Title Present) | Simplest criterion; maps cleanly to one diagnostic code (E001) |
| Diagnostic Code (Error) | DS-DC-E001 (NO_H1_TITLE) | Most fundamental error; referenced by the example criterion above |
| Diagnostic Code (Warning) | DS-DC-W001 (MISSING_BLOCKQUOTE) | Demonstrates the warning-vs-error distinction (55% compliance note) |
| Diagnostic Code (Info) | DS-DC-I001 (NO_LLM_INSTRUCTIONS) | Demonstrates the informational tier |
| Validation Level | DS-VL-L0 (PARSEABLE) | Foundation level; simplest exit criteria |
| Design Decision | DS-DD-014 (Content Quality Primary Weight) | Directly impacts scoring; demonstrates how decisions constrain implementation |
| Anti-Pattern | DS-AP-CRIT-001 (Ghost File) | Simplest anti-pattern; demonstrates the gating mechanism |
| Calibration Specimen | DS-CS-001 (Svelte Exemplary) | Highest-scoring specimen; demonstrates the calibration format |
| Canonical Name | DS-CN-001 (Master Index) | Most impactful canonical name; has the most aliases |

### 4.4 Deliverables

| Deliverable | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| Directory tree | All directories created per §3.2 | `find docs/design/00-meta/standards/ -type d` returns exactly the hierarchy in §3.2 |
| README indexes (16) | Stub files in every directory | Each README has an H1, a description paragraph, and a table with column headers |
| Manifest stub | `DS-MANIFEST.md` with version 0.0.0-scaffold | Contains all 5 roles (version, registry, assertions, provenance, changelog) as sections with placeholder content |
| Example files (9) | One fully populated file per type | Each file matches its Appendix B template; all cross-references use DS identifiers; all metadata fields populated |

### 4.5 Acceptance Criteria

Phase A is complete when:

1. **Structural completeness**: `find` returns all expected directories and files (exact count verified).
2. **Template validation**: Each example file can be parsed by a human reader and unambiguously identifies what standard element it defines.
3. **Cross-reference validation**: Every DS identifier referenced in an example file corresponds to another example file that exists.
4. **Manifest coherence**: The manifest registry lists exactly 9 entries matching the 9 example files, all with status DRAFT.

### 4.6 Workflow

```
┌─────────────────────────────────────────────────────┐
│ Phase A: Scaffolding                                  │
│                                                       │
│  A.1─A.2 ──► A.3─A.5 ──► A.6 ──► A.7 ──► A.8─A.9  │
│  (dirs)      (READMEs)   (examples) (review) (index) │
│                                                       │
│  Gate: A.7 must pass before A.8                       │
│  Rollback: If templates need changes, return to A.6   │
└─────────────────────────────────────────────────────┘
```

### 4.7 Decision Points

| Decision | Question | Options | Recommended | Rationale |
|----------|----------|---------|-------------|-----------|
| A-DEC-01 | Should the manifest be Markdown or YAML? | (a) Pure Markdown, (b) YAML with Markdown summary, (c) Both | (a) Pure Markdown | Keeps the standard self-contained in one format. The pipeline can parse Markdown tables. YAML introduces a second format that must be kept in sync. |
| A-DEC-02 | Should example files use DRAFT or RATIFIED status? | (a) DRAFT, (b) RATIFIED | (a) DRAFT | Examples are validated during Phase A but not ratified until Phase E when all content is complete. Premature ratification creates an inconsistency. |
| A-DEC-03 | Should README indexes include file descriptions? | (a) ID + path + status only, (b) ID + path + status + one-line description | (b) With descriptions | A one-line description makes the index scannable without opening each file. Marginal additional maintenance cost. |

---

## 5. Phase B: Diagnostic Codes

### 5.1 Objectives

Populate all 38 diagnostic code standard files. Diagnostic codes are the most self-contained element type (each code has a well-defined severity, message, remediation, and validation level mapping that is already fully specified in `diagnostics.py`). This makes them the lowest-risk, highest-value starting point — every other standard element *references* diagnostic codes.

### 5.2 Pre-Conditions

- Phase A completed and accepted.
- All 9 example files reviewed and approved.
- The diagnostic code template (Appendix B.2) is finalized.

### 5.3 Source Material

All diagnostic code content is extracted and ratified from these sources:

| Source | Codes Defined | What It Provides |
|--------|--------------|------------------|
| `src/docstratum/schema/diagnostics.py` | All 38 (E001–E010, W001–W018, I001–I010) | Code value, severity, message, remediation, v0.0.4 check ID mapping |
| RR-SPEC-v0.0.6 §4 (Criterion Registry) | E001–E008, W001–W011, I001–I007 (original 26) | Provenance pointers to specific research documents |
| RR-SPEC-v0.0.7 §5 (Ecosystem Diagnostics) | E009–E010, W012–W018, I008–I010 (12 new) | Ecosystem-level provenance, cross-file context description |

### 5.4 Steps

| Step | Action | Output | Dependencies |
|------|--------|--------|--------------|
| B.1 | Extract complete metadata for all 38 codes from `diagnostics.py` | Structured data: code, severity, message, remediation, check_id | Phase A |
| B.2 | Cross-reference each code with v0.0.6 criterion mapping (§6.1) | Provenance and criterion linkage for original 26 codes | B.1 |
| B.3 | Cross-reference each v0.0.7 code with ecosystem spec (§5) | Provenance and criterion linkage for 12 ecosystem codes | B.1 |
| B.4 | Author all 10 error code files (E001–E010) | 10 files in `diagnostics/errors/` | B.2, B.3 |
| B.5 | Author all 18 warning code files (W001–W018) | 18 files in `diagnostics/warnings/` | B.2, B.3 |
| B.6 | Author all 10 info code files (I001–I010) | 10 files in `diagnostics/info/` | B.2, B.3 |
| B.7 | Update diagnostics README index with all 38 entries | Complete index table | B.4–B.6 |
| B.8 | Update manifest registry with 38 new entries (status: DRAFT) | Manifest now has 47 entries (9 examples + 38 diagnostics) | B.7 |
| B.9 | Validation pass: verify every code in `diagnostics.py` has a corresponding file | Checklist output: 38/38 matched | B.8 |

### 5.5 Per-File Authoring Workflow

For each diagnostic code file, the authoring process follows this sequence:

```
┌──────────────────────────────────────────────────────────────────┐
│ Per-File Workflow (Diagnostic Code)                                │
│                                                                    │
│  1. Read code entry from diagnostics.py                           │
│     └─ Extract: value, severity, message, remediation, check_id   │
│                                                                    │
│  2. Look up provenance in v0.0.6 §4 or v0.0.7 §5                 │
│     └─ Extract: criterion ID, research source, empirical data     │
│                                                                    │
│  3. Identify related elements                                     │
│     └─ Which VC criterion(s) emit this code?                      │
│     └─ Which AP anti-pattern(s) trigger this code?                │
│     └─ Which VL level does this code belong to?                   │
│                                                                    │
│  4. Fill template (Appendix B.2)                                  │
│     └─ Populate all fields; leave nothing as "[TBD]"              │
│                                                                    │
│  5. Self-check                                                    │
│     └─ Does the message match diagnostics.py exactly?             │
│     └─ Does the remediation match diagnostics.py exactly?         │
│     └─ Are all DS identifier cross-references valid?              │
│     └─ Is provenance complete (no "origin unknown")?              │
│                                                                    │
│  6. Commit file                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 5.6 Deliverables

| Deliverable | Count | Acceptance Criteria |
|-------------|-------|---------------------|
| Error code files | 10 | Message and remediation match `diagnostics.py` exactly |
| Warning code files | 18 | Message and remediation match `diagnostics.py` exactly |
| Info code files | 10 | Message and remediation match `diagnostics.py` exactly |
| Updated README index | 1 | All 38 codes listed with severity, level, criterion mapping |
| Updated manifest | 1 | 38 new DRAFT entries; total count assertion passes |

### 5.7 Acceptance Criteria

Phase B is complete when:

1. **Coverage**: Every `DiagnosticCode` enum member in `diagnostics.py` has exactly one corresponding file in `diagnostics/`.
2. **Fidelity**: The `message` and `remediation` fields in each standard file are character-identical to the values returned by the `DiagnosticCode.message` and `DiagnosticCode.remediation` properties.
3. **Provenance**: Every file cites at least one research document as its origin.
4. **Cross-references**: Every file lists at least one related VC criterion (except I005 and I010, which are classification-level observations with no direct criterion mapping).
5. **Manifest**: The manifest registry contains 47 entries (9 Phase A + 38 Phase B), all with status DRAFT.

### 5.8 Decision Points

| Decision | Question | Options | Recommended | Rationale |
|----------|----------|---------|-------------|-----------|
| B-DEC-01 | Should message text in ASoT files be copied verbatim from `diagnostics.py` or paraphrased? | (a) Verbatim copy, (b) Paraphrased for readability | (a) Verbatim copy | The ASoT is the authority. If the `diagnostics.py` message needs improving, it should be updated in both places simultaneously. Verbatim ensures no drift. |
| B-DEC-02 | What happens when `diagnostics.py` has information the ASoT file doesn't (or vice versa)? | (a) ASoT wins, (b) Code wins, (c) Both must agree | (c) Both must agree | Integrity assertion IA-011: "Every DC file's message matches `DiagnosticCode.message` property." Disagreement is a configuration drift error, not a precedence question. |
| B-DEC-03 | Should ecosystem codes (E009–E010, W012–W018, I008–I010) be in separate subdirectories? | (a) Same directories as original codes, (b) Separate `ecosystem/` subdirectory | (a) Same directories | Severity-based grouping is more natural for navigation. Ecosystem provenance is captured in the file metadata, not the directory structure. |

---

## 6. Phase C: Validation Criteria

### 6.1 Objectives

Populate all 30 validation criterion files based on the Platinum Standard (v0.0.6). This is the most intellectually demanding phase because it requires translating research-quality descriptions into precise, unambiguous pass/fail definitions suitable for an automated validator.

### 6.2 Pre-Conditions

- Phase B completed and accepted (all 38 diagnostic code files exist).
- Diagnostic code files are available for cross-referencing.
- The validation criterion template (Appendix B.1) is finalized.

### 6.3 Source Material

| Source | Criteria | What It Provides |
|--------|----------|------------------|
| RR-SPEC-v0.0.6 §4.1 (L0 Parseable) | L0-01 through L0-05 | 5 criteria with descriptions, measurability, diagnostic codes, provenance |
| RR-SPEC-v0.0.6 §4.2 (L1 Structural) | L1-01 through L1-06 | 6 criteria |
| RR-SPEC-v0.0.6 §4.3 (L2 Content) | L2-01 through L2-07 | 7 criteria |
| RR-SPEC-v0.0.6 §4.4 (L3 Best Practices) | L3-01 through L3-10 | 10 criteria |
| RR-SPEC-v0.0.6 §4.5 (L4 Exemplary) | L4-01 through L4-08 | 8 criteria |

### 6.4 Criterion-to-File Mapping

The 30 Platinum Standard criteria map to the three quality dimensions as follows:

**Structural Dimension (DS-VC-STR-*) — 9 criteria:**

| DS Identifier | Platinum ID | Criterion | Level |
|---------------|-------------|-----------|-------|
| DS-VC-STR-001 | L0-01 through L0-05 | Parseable prerequisites (UTF-8, non-empty, valid Markdown, token limit, LF endings) | L0 |
| DS-VC-STR-002 | L1-01 | H1 title present | L1 |
| DS-VC-STR-003 | L1-02 | Single H1 only | L1 |
| DS-VC-STR-004 | L1-03 | Blockquote present | L1 |
| DS-VC-STR-005 | L1-04 | H2 section structure | L1 |
| DS-VC-STR-006 | L1-05 | Link format compliance | L1 |
| DS-VC-STR-007 | L1-06 | No heading level violations | L1 |
| DS-VC-STR-008 | L3-06 | Canonical section ordering | L3 |
| DS-VC-STR-009 | L3-09 + L3-10 | No critical/structural anti-patterns (composite) | L3 |

> **Note:** DS-VC-STR-001 is a compound criterion covering the 5 L0 checks. This is a deliberate consolidation — L0 checks are prerequisite gates, not quality assessments. They all share the same behavior: if any fail, no further validation is possible. Representing them as 5 separate files would add granularity without adding value.

**Content Dimension (DS-VC-CON-*) — 13 criteria:**

| DS Identifier | Platinum ID | Criterion | Level |
|---------------|-------------|-----------|-------|
| DS-VC-CON-001 | L2-01 | Non-empty descriptions | L2 |
| DS-VC-CON-002 | L2-02 | URL resolvability | L2 |
| DS-VC-CON-003 | L2-03 | No placeholder content | L2 |
| DS-VC-CON-004 | L2-04 | Non-empty sections | L2 |
| DS-VC-CON-005 | L2-05 | No duplicate sections | L2 |
| DS-VC-CON-006 | L2-06 | Substantive blockquote | L2 |
| DS-VC-CON-007 | L2-07 | No formulaic descriptions | L2 |
| DS-VC-CON-008 | L3-01 | Canonical section names | L3 |
| DS-VC-CON-009 | L3-02 | Master Index present | L3 |
| DS-VC-CON-010 | L3-03 | Code examples present | L3 |
| DS-VC-CON-011 | L3-04 | Code language specifiers | L3 |
| DS-VC-CON-012 | L3-05 | Token budget respected | L3 |
| DS-VC-CON-013 | L3-07 | Version metadata present | L3 |

**Anti-Pattern Detection Dimension (DS-VC-APD-*) — 8 criteria:**

| DS Identifier | Platinum ID | Criterion | Level |
|---------------|-------------|-----------|-------|
| DS-VC-APD-001 | L4-01 | LLM Instructions section | L4 |
| DS-VC-APD-002 | L4-02 | Concept definitions | L4 |
| DS-VC-APD-003 | L4-03 | Few-shot examples | L4 |
| DS-VC-APD-004 | L4-04 | No content anti-patterns | L4 |
| DS-VC-APD-005 | L4-05 | No strategic anti-patterns | L4 |
| DS-VC-APD-006 | L4-06 | Token-optimized structure | L4 |
| DS-VC-APD-007 | L4-07 | Relative URL minimization | L4 |
| DS-VC-APD-008 | L4-08 | Jargon defined or linked | L4 |

### 6.5 Steps

| Step | Action | Output | Dependencies |
|------|--------|--------|--------------|
| C.1 | Extract all 30 criteria from v0.0.6 §4.1–§4.5 | Structured data per criterion | Phase B |
| C.2 | Map each criterion to its quality dimension (STR/CON/APD) | Dimension assignment table (§6.4 above) | C.1 |
| C.3 | For each criterion, define precise pass/fail conditions | Unambiguous boolean logic for each check | C.2 |
| C.4 | For each criterion, identify all emitted diagnostic codes | DS-DC cross-references per criterion | C.3 |
| C.5 | For each criterion, identify related anti-patterns | DS-AP cross-references per criterion | C.3 |
| C.6 | Author all 9 structural criteria files | 9 files in `criteria/structural/` | C.3–C.5 |
| C.7 | Author all 13 content criteria files | 13 files in `criteria/content/` | C.3–C.5 |
| C.8 | Author all 8 anti-pattern detection criteria files | 8 files in `criteria/anti-pattern/` | C.3–C.5 |
| C.9 | Update criteria README indexes (root + 3 subdirectories) | 4 complete index files | C.6–C.8 |
| C.10 | Update manifest registry with 30 new entries | Manifest now has 77 entries | C.9 |
| C.11 | Cross-reference validation: verify every criterion cites ≥1 DC file | Checklist: 30/30 cross-refs valid | C.10 |
| C.12 | Backfill DC files: update each diagnostic code file's "Related Criteria" section | 38 files updated with VC cross-references | C.11 |

### 6.6 Authoring Workflow — Criteria-Specific Challenges

Validation criteria are harder to author than diagnostic codes because they require **precise pass/fail logic**. The Platinum Standard (v0.0.6) provides descriptions and measurability assessments, but not always unambiguous boolean conditions. Phase C must resolve ambiguities explicitly.

**Common ambiguity patterns and resolution strategy:**

| Ambiguity | Example | Resolution Strategy |
|-----------|---------|---------------------|
| Threshold values | L2-07: "pairwise similarity > 80% across 5+ descriptions" — is 80% the right threshold? | Document the threshold with a `[CALIBRATION-NEEDED]` tag. Use the threshold from v0.0.6 as the initial value. Flag for calibration against specimens in Phase D. |
| Composite checks | L3-09: "No critical anti-patterns" — pass means all 4 AP-CRIT patterns absent | Enumerate all constituent checks explicitly in the pass condition. The criterion file lists every AP it encompasses. |
| Heuristic checks | L4-02: "Concept definitions" — what counts as a "definition"? | Define the heuristic patterns explicitly (e.g., "X is...", "X refers to...", "## Glossary", "## Concepts"). Document edge cases. |
| "Should" vs "Must" | L1-03: "A blockquote should appear" — is it required or recommended? | Align with the existing diagnostic code severity. W001 is a WARNING, not an ERROR, so blockquote absence is recommended but not required. Document this in the pass condition with a "soft pass" concept. |

### 6.7 Deliverables

| Deliverable | Count | Acceptance Criteria |
|-------------|-------|---------------------|
| Structural criterion files | 9 | Each has unambiguous pass/fail conditions matching v0.0.6 |
| Content criterion files | 13 | Each has unambiguous pass/fail conditions matching v0.0.6 |
| Anti-pattern detection files | 8 | Each has unambiguous pass/fail conditions matching v0.0.6 |
| Updated README indexes | 4 | All 30 criteria listed with level, dimension, weight |
| Updated manifest | 1 | 30 new DRAFT entries; total = 77 |
| Updated DC files (backfill) | 38 | Each DC file now lists its related VC criteria |

### 6.8 Acceptance Criteria

Phase C is complete when:

1. **Coverage**: Every criterion in v0.0.6 §4 has exactly one corresponding file.
2. **Precision**: Every criterion file contains a pass condition that could be directly translated to a Python boolean expression without further interpretation.
3. **Bidirectional cross-references**: Every VC file lists its emitted DC codes, and every DC file (updated in C.12) lists the VC criteria that trigger it.
4. **Weight accounting**: The sum of all STR criterion weights = 30, CON = 50, APD = 20.
5. **No TBD fields**: Every field in every criterion file is populated (though `[CALIBRATION-NEEDED]` tags are acceptable for heuristic thresholds).

### 6.9 Decision Points

| Decision | Question | Options | Recommended | Rationale |
|----------|----------|---------|-------------|-----------|
| C-DEC-01 | Should L0 checks be one compound criterion (DS-VC-STR-001) or five separate files? | (a) One compound, (b) Five separate | (a) One compound | L0 checks are binary gates with identical behavior (fail → stop). Splitting them adds 4 files with no additional information value. The compound file lists all 5 checks individually. |
| C-DEC-02 | How should criterion weights be assigned within a dimension? | (a) Equal weights, (b) Variable weights from v0.0.6, (c) Defer to calibration | (b) Variable weights from v0.0.6 | v0.0.6 already assigns weights implicitly through the scoring rubric. Making them explicit ensures the ASoT is self-contained. |
| C-DEC-03 | Should "soft pass" criteria (warnings that don't block progression) be documented differently from "hard pass" criteria? | (a) Same template, (b) Add a `pass_type` field (HARD / SOFT) | (b) Add pass_type field | This distinction is architecturally significant. A HARD pass means failure blocks level progression. A SOFT pass means failure emits a warning but doesn't block. Making this explicit prevents implementation confusion. |
| C-DEC-04 | L3-08 ("Optional section used appropriately") is "partially measurable" — include or exclude? | (a) Include with heuristic, (b) Exclude from automated pipeline, (c) Include as INFO-only | (c) Include as INFO-only | The criterion adds value as a suggestion but cannot be reliably automated. Including it as INFO-only means it appears in results but doesn't affect scoring. |

---

## 7. Phase D: Supporting Standards

### 7.1 Objectives

Populate all remaining standard element types: design decisions (16), anti-patterns (28), calibration specimens (6), canonical names (11), validation levels (5), scoring definitions (5), and ecosystem health dimensions (5). These elements are the context and infrastructure that criteria and diagnostics reference.

### 7.2 Pre-Conditions

- Phase C completed and accepted.
- All 30 criteria and 38 diagnostic code files exist.
- Cross-references from Phases B and C are validated.

### 7.3 Sub-Phases

Phase D is internally ordered to respect dependencies between element types:

| Sub-Phase | Element Type | Count | Dependencies | Rationale for Order |
|-----------|-------------|-------|--------------|---------------------|
| **D.1** | Validation Levels (VL) | 5 | Phase C (criteria reference levels) | Levels define the framework that criteria operate within. They are referenced by every VC file but don't themselves reference VC files. |
| **D.2** | Anti-Patterns (AP) | 28 | Phase B (DC files), Phase C (VC files) | Anti-patterns are referenced by multiple criteria (L3-09, L3-10, L4-04, L4-05) and diagnostic codes. Populating them allows backfilling AP cross-references into existing files. |
| **D.3** | Design Decisions (DD) | 16 | None (standalone) | Design decisions constrain the implementation but don't have bidirectional references to other standard elements. They can be authored in parallel. |
| **D.4** | Canonical Names (CN) | 11 | Phase D.2 (anti-pattern AP-STRUCT-005 Naming Nebula references canonical names) | Canonical names are referenced by criterion DS-VC-CON-008 and diagnostic code DS-DC-W002. |
| **D.5** | Scoring Framework (QS) | 5 | Phase C (criteria define the things being scored) | Scoring definitions formalize the weights and thresholds that criteria contribute to. |
| **D.6** | Ecosystem Health (EH) | 5 | Phase B (ecosystem diagnostic codes), Phase D.2 (ecosystem anti-patterns) | Ecosystem health dimensions are the most recent addition (v0.0.7) and build on all other elements. |
| **D.7** | Calibration Specimens (CS) | 6 | Phase D.5 (scoring framework defines how scores are calculated) | Calibration specimens define *expected* scores, which requires the scoring framework to be finalized first. |

### 7.4 Steps (by Sub-Phase)

**D.1 — Validation Levels (5 files)**

| Step | Action | Output |
|------|--------|--------|
| D.1.1 | Extract level definitions from `validation.py` and v0.0.6 §3.2 | Structured data per level |
| D.1.2 | For each level, list the criteria that belong to it | Level → criteria mapping |
| D.1.3 | For each level, define exit criteria (from v0.0.6 level exit conditions) | Precise boolean exit conditions |
| D.1.4 | Author 5 level files | 5 files in `levels/` |
| D.1.5 | Update levels README index | Complete index |

**D.2 — Anti-Patterns (28 files)**

| Step | Action | Output |
|------|--------|--------|
| D.2.1 | Extract all 28 anti-patterns from `constants.py` ANTI_PATTERN_REGISTRY | ID, name, category, check_id, description |
| D.2.2 | Cross-reference with v0.0.4c (original 22) and v0.0.7 §6 (6 ecosystem) for extended descriptions | Detection logic, severity impact, examples |
| D.2.3 | For each anti-pattern, identify which criteria and diagnostic codes reference it | Cross-reference table |
| D.2.4 | Author 4 critical anti-pattern files | 4 files in `anti-patterns/critical/` |
| D.2.5 | Author 5 structural anti-pattern files | 5 files in `anti-patterns/structural/` |
| D.2.6 | Author 9 content anti-pattern files | 9 files in `anti-patterns/content/` |
| D.2.7 | Author 4 strategic anti-pattern files | 4 files in `anti-patterns/strategic/` |
| D.2.8 | Author 6 ecosystem anti-pattern files | 6 files in `anti-patterns/ecosystem/` |
| D.2.9 | Update anti-patterns README indexes (root + 5 subdirectories) | 6 complete index files |
| D.2.10 | Backfill VC and DC files with AP cross-references | Updated VC and DC files |

**D.3 — Design Decisions (16 files)**

| Step | Action | Output |
|------|--------|--------|
| D.3.1 | Extract all 16 decisions from v0.1.0 §DECISION-001 through DECISION-016 | Structured data per decision |
| D.3.2 | For each decision, identify impact on validation criteria and scoring | Impact mapping |
| D.3.3 | Author 16 decision files | 16 files in `decisions/` |
| D.3.4 | Update decisions README index | Complete index |

**D.4 — Canonical Names (11 files)**

| Step | Action | Output |
|------|--------|--------|
| D.4.1 | Extract all 11 names + 32 aliases from `constants.py` | Name, position, aliases |
| D.4.2 | Author 11 canonical name files | 11 files in `canonical/` |
| D.4.3 | Update canonical README index | Complete index |

**D.5 — Scoring Framework (5 files)**

| Step | Action | Output |
|------|--------|--------|
| D.5.1 | Extract dimension definitions from `quality.py` | Weight, max points, scoring logic |
| D.5.2 | Extract grade thresholds from `QualityGrade.from_score()` | Boundary values (0–29, 30–49, 50–69, 70–89, 90–100) |
| D.5.3 | Document structural gating rule (CRITICAL cap at 29) | Gating logic |
| D.5.4 | Author 5 scoring files | 5 files in `scoring/` |
| D.5.5 | Update scoring README index | Complete index |

**D.6 — Ecosystem Health (5 files)**

| Step | Action | Output |
|------|--------|--------|
| D.6.1 | Extract 5 dimensions from `ecosystem.py` EcosystemHealthDimension | Dimension definitions |
| D.6.2 | Cross-reference with v0.0.7 §4.3 for scoring methodology | Per-dimension scoring logic |
| D.6.3 | Author 5 ecosystem health files | 5 files in `ecosystem/` |
| D.6.4 | Update ecosystem README index | Complete index |

**D.7 — Calibration Specimens (6 files)**

| Step | Action | Output |
|------|--------|--------|
| D.7.1 | Extract gold standard scores from v0.0.6 §7 and `quality.py` header | Expected total score, grade, per-dimension scores |
| D.7.2 | For each specimen, document which criteria it passes/fails | Per-criterion pass/fail expectation |
| D.7.3 | Author 6 calibration specimen files | 6 files in `calibration/` |
| D.7.4 | Update calibration README index | Complete index |

### 7.5 Deliverables

| Deliverable | Count | Acceptance Criteria |
|-------------|-------|---------------------|
| Validation level files | 5 | Each lists its criteria, exit conditions, and level relationship |
| Anti-pattern files | 28 | Each matches `constants.py` registry; detection logic is unambiguous |
| Design decision files | 16 | Each matches v0.1.0; impact on validation is documented |
| Canonical name files | 11 | Each lists all aliases from `SECTION_NAME_ALIASES`; canonical position documented |
| Scoring files | 5 | Weights sum to 100; grade thresholds match `QualityGrade.from_score()` |
| Ecosystem health files | 5 | Each describes its measurement methodology |
| Calibration specimen files | 6 | Each has expected total score and per-dimension breakdown |
| Updated README indexes | 8 (new) + 4 (updated from Phase C) | All tables populated |
| Updated manifest | 1 | ~76 new entries; total = ~153 |

### 7.6 Acceptance Criteria

Phase D is complete when:

1. **Complete coverage**: Every anti-pattern in `ANTI_PATTERN_REGISTRY`, every `CanonicalSectionName`, every `QualityDimension`, every `EcosystemHealthDimension`, every DECISION-* from v0.1.0, every `ValidationLevel`, and every gold standard specimen has exactly one corresponding file.
2. **Internal consistency**: The sum of all scoring dimension weights in QS files equals 100. The grade thresholds in `DS-QS-GRADE-thresholds.md` match `QualityGrade.from_score()` exactly.
3. **Cross-reference completeness**: All backfill operations from D.2.10 are complete. No standard file has an empty "Related" section (except where genuinely no relationships exist).
4. **Calibration readiness**: Each specimen file could be used as a self-test input for the pipeline (expected scores are specific enough to validate against).

### 7.7 Decision Points

| Decision | Question | Options | Recommended | Rationale |
|----------|----------|---------|-------------|-----------|
| D-DEC-01 | Should anti-pattern files include inline examples of the pattern? | (a) Yes, with real-world excerpts, (b) Yes, with synthetic examples, (c) No examples | (b) Synthetic examples | Real-world excerpts may have copyright issues. Synthetic examples demonstrate the pattern without legal risk. |
| D-DEC-02 | Should calibration specimens include the actual llms.txt file content? | (a) Full content, (b) Summary only, (c) Link to external source | (c) Link to external source | Including full content bloats the ASoT. A link to the public URL plus the expected score is sufficient for calibration. |
| D-DEC-03 | The ecosystem health dimensions in `ecosystem.py` (COVERAGE, CONSISTENCY, COMPLETENESS, TOKEN_EFFICIENCY, FRESHNESS) differ slightly from v0.0.7 naming (Coverage, Coherence, Completeness, Consistency, Capability). Which naming wins? | (a) Code wins, (b) v0.0.7 wins, (c) Reconcile and pick best | (c) Reconcile | The code was implemented after v0.0.7, so it may have evolved the naming for good reasons. Document both names, pick the clearest, and update whichever source is wrong. |

---

## 8. Phase E: Manifest Ratification

### 8.1 Objectives

Finalize the manifest, run all integrity assertions, change all element statuses from DRAFT to RATIFIED, stamp the version as ASoT v1.0.0, and perform a comprehensive cross-reference validation pass.

### 8.2 Pre-Conditions

- Phases A through D completed and accepted.
- All ~166 standard files exist with status DRAFT.
- No unresolved `[TBD]` or `[CALIBRATION-NEEDED]` tags remain (or a conscious decision has been made to accept them).

### 8.3 Steps

| Step | Action | Output | Dependencies |
|------|--------|--------|--------------|
| E.1 | Complete the manifest file registry (all ~146 standard files + 20 READMEs) | Full registry table | Phase D |
| E.2 | Define and document all integrity assertions (IA-001 through IA-NNN) | Assertions section of manifest | E.1 |
| E.3 | Run all integrity assertions manually (or via script) | Assertion results: all PASS | E.2 |
| E.4 | Complete the provenance map (every file → research source) | Full provenance table | E.1 |
| E.5 | Cross-reference audit: verify every DS identifier referenced in any file exists in the registry | Audit report: 0 broken references | E.1 |
| E.6 | Bidirectional reference audit: for every A→B reference, verify B→A exists | Audit report (informational — not all references need to be bidirectional) | E.5 |
| E.7 | Change all file statuses from DRAFT to RATIFIED | All files updated | E.3, E.5 |
| E.8 | Set manifest version to 1.0.0 | Version field updated | E.7 |
| E.9 | Write initial change log entry | "v1.0.0 — Initial ratification" | E.8 |
| E.10 | Final review: read the top-level README, manifest, and 5 randomly selected standard files to verify consistency | Review notes | E.9 |

### 8.4 Integrity Assertion Catalog

These assertions are verified during E.3 and become permanent self-checks for the pipeline:

| ID | Assertion | Expected Value | Verification Method |
|----|-----------|---------------|---------------------|
| IA-001 | Total RATIFIED standard files | 146 | Count files matching `DS-*.md` |
| IA-002 | RATIFIED VC (criteria) files | 30 | Count files in `criteria/` |
| IA-003 | RATIFIED DC (diagnostic) files | 38 | Count files in `diagnostics/` |
| IA-004 | RATIFIED AP (anti-pattern) files | 28 | Count files in `anti-patterns/` |
| IA-005 | RATIFIED DD (decision) files | 16 | Count files in `decisions/` |
| IA-006 | RATIFIED CN (canonical name) files | 11 | Count files in `canonical/` |
| IA-007 | RATIFIED VL (level) files | 5 | Count files in `levels/` |
| IA-008 | RATIFIED QS (scoring) files | 5 | Count files in `scoring/` |
| IA-009 | RATIFIED EH (ecosystem) files | 5 | Count files in `ecosystem/` |
| IA-010 | RATIFIED CS (calibration) files | 6 | Count files in `calibration/` |
| IA-011 | Sum of STR dimension weights | 30 | Parse VC-STR files, sum weights |
| IA-012 | Sum of CON dimension weights | 50 | Parse VC-CON files, sum weights |
| IA-013 | Sum of APD dimension weights | 20 | Parse VC-APD files, sum weights |
| IA-014 | Every DC file referenced by ≥1 VC file | True | Cross-reference scan |
| IA-015 | Every VC file references ≥1 DC file | True (with documented exceptions) | Cross-reference scan |
| IA-016 | No broken DS identifier references | 0 broken | Full reference scan |
| IA-017 | Calibration specimen count ≥ 5 | ≥5 | Count CS files |
| IA-018 | All calibration scores within 0–100 | True | Parse CS files |
| IA-019 | Grade thresholds in QS file match code | True | Compare to `QualityGrade.from_score()` |
| IA-020 | No `[TBD]` tags in RATIFIED files | 0 occurrences | Text search |

### 8.5 Deliverables

| Deliverable | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| Finalized manifest | `DS-MANIFEST.md` version 1.0.0 | All 5 roles populated; all assertions pass |
| Ratified standard files | All ~146 files with status RATIFIED | No file remains in DRAFT status |
| Integrity assertion results | Report showing all IA-* assertions PASS | 0 failures |
| Cross-reference audit report | Report showing 0 broken DS identifier references | 0 broken references |

### 8.6 Acceptance Criteria

Phase E — and the entire ASoT implementation — is complete when:

1. **All integrity assertions pass** (IA-001 through IA-020, zero failures).
2. **All files are RATIFIED** (no DRAFT or DEPRECATED files remain in ASoT v1.0.0).
3. **The manifest version is 1.0.0** and includes a dated change log entry.
4. **The validation pipeline team has a clear contract**: "Read `DS-MANIFEST.md`, verify integrity assertions, then implement each VC criterion."

### 8.7 Post-Ratification Protocol

After ASoT v1.0.0 is declared:

1. **Any change to a standard file** requires a manifest version bump (MINOR for additions, MAJOR for removals or weight changes, PATCH for corrections).
2. **New criteria** are added as DRAFT files first, then ratified in a subsequent version bump.
3. **Deprecated criteria** remain in the tree with status DEPRECATED and a deprecation date. They are excluded from pipeline integrity assertions but preserved for historical reference.
4. **Pipeline validation results** must include the ASoT version they were run against (e.g., `"asot_version": "1.0.0"` in the `ValidationResult` output).

---

## 9. Self-Validation Loop

### 9.1 Concept

The self-validation loop is the mechanism by which the validation pipeline **checks itself** against the ASoT before validating external documents. This addresses the original insight that motivated the entire ASoT effort: "each time we run the validation, the validators should look to the ASoT to make sure its requirements and results align with expected baselines."

### 9.2 Three-Stage Self-Check

```
┌──────────────────────────────────────────────────────────────────┐
│ Pipeline Startup                                                   │
│                                                                    │
│  Stage 1: MANIFEST LOAD                                           │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │ Read DS-MANIFEST.md                                      │      │
│  │ Parse version, file registry, integrity assertions       │      │
│  │ IF version mismatch with pipeline config → HALT          │      │
│  └─────────────────────────────────────────────────────────┘      │
│                           │                                        │
│                           ▼                                        │
│  Stage 2: INTEGRITY VERIFICATION                                  │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │ Run all IA-* assertions from manifest                    │      │
│  │ Verify file counts, weight sums, cross-references        │      │
│  │ IF any assertion fails → HALT with drift error           │      │
│  └─────────────────────────────────────────────────────────┘      │
│                           │                                        │
│                           ▼                                        │
│  Stage 3: CALIBRATION SELF-TEST (optional, configurable)          │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │ Load calibration specimens from CS files                 │      │
│  │ Run pipeline against each specimen                       │      │
│  │ Compare actual scores to expected scores                 │      │
│  │ IF |actual - expected| > tolerance → WARN or HALT        │      │
│  └─────────────────────────────────────────────────────────┘      │
│                           │                                        │
│                           ▼                                        │
│  ✅ Pipeline configuration verified. Begin external validation.   │
└──────────────────────────────────────────────────────────────────┘
```

### 9.3 Stage 1: Manifest Load

The pipeline reads `DS-MANIFEST.md` and extracts:

- **ASoT version**: Compared against the pipeline's `EXPECTED_ASOT_VERSION` constant. If the pipeline expects v1.0.0 but the manifest says v1.1.0, the pipeline halts with a message: "Pipeline expects ASoT v1.0.0 but found v1.1.0. Update pipeline or downgrade ASoT."
- **File registry**: The list of all active standard files. The pipeline verifies it can locate every file listed in the registry.
- **Integrity assertions**: The complete list of IA-* assertions to run in Stage 2.

### 9.4 Stage 2: Integrity Verification

For each IA-* assertion, the pipeline evaluates the condition and compares to the expected value. Failures are reported with full context:

```
INTEGRITY CHECK FAILED: IA-011
  Expected: Sum of STR dimension weights = 30
  Actual:   Sum of STR dimension weights = 28
  Impact:   Structural dimension scoring will be incorrect
  Action:   Review DS-VC-STR-* files for weight discrepancies

Pipeline halted. Fix configuration drift before running external validation.
```

### 9.5 Stage 3: Calibration Self-Test

This is an optional but recommended stage where the pipeline validates its own output against known-good specimens. For each calibration specimen:

1. Load the specimen's expected score from its CS file.
2. Run the full validation pipeline against the specimen's llms.txt file.
3. Compare the actual total score, grade, and per-dimension scores against expectations.
4. If the difference exceeds a configurable tolerance (default: ±3 points), flag a warning or halt.

**Use case:** If a developer changes a scoring weight or adjusts a heuristic threshold, the calibration self-test immediately catches whether the change produces unexpected score drift. This is essentially a regression test for the validation standard itself.

### 9.6 Result Stamping

Every `ValidationResult` and `QualityScore` output includes:

```python
class ValidationResult(BaseModel):
    # ... existing fields ...
    asot_version: str = Field(
        description="ASoT version this result was validated against.",
    )
```

This enables retroactive analysis: "All results validated against ASoT v1.0.0 are potentially stale since v1.1.0 added criterion DS-VC-CON-014."

---

## 10. Decision Log

This section catalogs all decisions made during the ASoT implementation strategy design. Decisions are numbered with a `ASOT-DEC-` prefix to distinguish them from the inherited `DECISION-001` through `DECISION-016` from v0.1.0.

| ID | Decision | Chosen Option | Rationale | Phase |
|----|----------|--------------|-----------|-------|
| ASOT-DEC-001 | Modular file architecture vs single document | Modular (one file per element) | Context efficiency, independent versioning, scalability | Architecture |
| ASOT-DEC-002 | Naming convention | `DS-{Type}-{Sub}-{Seq}-{slug}.md` | Self-documenting, sortable, namespace-scoped | Architecture |
| ASOT-DEC-003 | Cross-reference method | DS identifiers (not file paths) | Stable across reorganizations | Architecture |
| ASOT-DEC-004 | Manifest format | Pure Markdown | Single-format consistency; pipeline can parse Markdown tables | A |
| ASOT-DEC-005 | Example file initial status | DRAFT (not RATIFIED) | Premature ratification creates inconsistency | A |
| ASOT-DEC-006 | README index detail level | ID + path + status + one-line description | Scannable without opening each file | A |
| ASOT-DEC-007 | DC message fidelity | Verbatim from `diagnostics.py` | Prevents drift between code and standard | B |
| ASOT-DEC-008 | Code-vs-ASoT precedence | Both must agree (disagreement = drift error) | Neither source is "more correct" — they must be synchronized | B |
| ASOT-DEC-009 | Ecosystem code directory placement | Same severity directories as original codes | Severity-based grouping is more natural for navigation | B |
| ASOT-DEC-010 | L0 check consolidation | One compound criterion (DS-VC-STR-001) | All L0 checks share identical gate behavior; splitting adds no value | C |
| ASOT-DEC-011 | Criterion weight source | Variable weights from v0.0.6 | Explicit weights ensure ASoT is self-contained | C |
| ASOT-DEC-012 | Soft vs hard pass distinction | Add `pass_type` field (HARD / SOFT) | Architecturally significant for pipeline implementation | C |
| ASOT-DEC-013 | Partially measurable criteria handling | Include as INFO-only (non-scoring) | Adds value as suggestion without compromising automated scoring | C |
| ASOT-DEC-014 | Anti-pattern examples | Synthetic examples (not real-world excerpts) | Avoids copyright concerns while demonstrating the pattern | D |
| ASOT-DEC-015 | Calibration specimen content | Link to external source + expected scores | Avoids bloating the ASoT with full file content | D |
| ASOT-DEC-016 | Ecosystem health dimension naming | Reconcile code and v0.0.7 naming | Document both, pick clearest, update whichever source is wrong | D |

---

## 11. Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-001 | Template changes mid-implementation require reworking completed files | Medium | High | Finalize templates completely in Phase A before scaling. Phase A example files serve as template validation. |
| R-002 | Cross-reference inconsistencies accumulate across phases | High | Medium | Run cross-reference validation at the end of each phase, not just Phase E. |
| R-003 | v0.0.6 Platinum Standard contains ambiguities that surface during criterion authoring | High | Medium | Document ambiguities as explicit decisions (C-DEC-*). Resolve before moving to next criterion. |
| R-004 | File count (~166) makes manual review impractical | Medium | Medium | Use automated scripts to verify structural properties (field presence, DS identifier format, weight sums). Manual review focuses on content quality, not structure. |
| R-005 | ASoT and `diagnostics.py` code drift apart post-ratification | Medium | High | Implement IA-011 as a CI check. Any PR that modifies `diagnostics.py` must also update the corresponding DS-DC file (and vice versa). |
| R-006 | Calibration specimens become stale as the underlying llms.txt files change | Low | Medium | Re-validate specimens quarterly. Document specimen URLs and capture dates. |
| R-007 | Naming taxonomy collisions (e.g., DS-AP-CON-* and DS-EH-CON-* share "CON") | Low | Low | Full type code resolves ambiguity: `AP` = anti-pattern, `EH` = ecosystem health. No collision in practice because the full prefix `DS-AP-CON-*` vs `DS-EH-CON-*` is always used. |

---

## 12. Appendices

### Appendix A: Complete Inventory of Standard Elements

**Validation Criteria (30):**

| DS ID | Platinum ID | Name | Dimension | Level |
|-------|-------------|------|-----------|-------|
| DS-VC-STR-001 | L0-01–L0-05 | Parseable Prerequisites | Structural | L0 |
| DS-VC-STR-002 | L1-01 | H1 Title Present | Structural | L1 |
| DS-VC-STR-003 | L1-02 | Single H1 Only | Structural | L1 |
| DS-VC-STR-004 | L1-03 | Blockquote Present | Structural | L1 |
| DS-VC-STR-005 | L1-04 | H2 Section Structure | Structural | L1 |
| DS-VC-STR-006 | L1-05 | Link Format Compliance | Structural | L1 |
| DS-VC-STR-007 | L1-06 | No Heading Level Violations | Structural | L1 |
| DS-VC-STR-008 | L3-06 | Canonical Section Ordering | Structural | L3 |
| DS-VC-STR-009 | L3-09+L3-10 | No Critical/Structural Anti-Patterns | Structural | L3 |
| DS-VC-CON-001 | L2-01 | Non-Empty Descriptions | Content | L2 |
| DS-VC-CON-002 | L2-02 | URL Resolvability | Content | L2 |
| DS-VC-CON-003 | L2-03 | No Placeholder Content | Content | L2 |
| DS-VC-CON-004 | L2-04 | Non-Empty Sections | Content | L2 |
| DS-VC-CON-005 | L2-05 | No Duplicate Sections | Content | L2 |
| DS-VC-CON-006 | L2-06 | Substantive Blockquote | Content | L2 |
| DS-VC-CON-007 | L2-07 | No Formulaic Descriptions | Content | L2 |
| DS-VC-CON-008 | L3-01 | Canonical Section Names | Content | L3 |
| DS-VC-CON-009 | L3-02 | Master Index Present | Content | L3 |
| DS-VC-CON-010 | L3-03 | Code Examples Present | Content | L3 |
| DS-VC-CON-011 | L3-04 | Code Language Specifiers | Content | L3 |
| DS-VC-CON-012 | L3-05 | Token Budget Respected | Content | L3 |
| DS-VC-CON-013 | L3-07 | Version Metadata Present | Content | L3 |
| DS-VC-APD-001 | L4-01 | LLM Instructions Section | Anti-Pattern | L4 |
| DS-VC-APD-002 | L4-02 | Concept Definitions | Anti-Pattern | L4 |
| DS-VC-APD-003 | L4-03 | Few-Shot Examples | Anti-Pattern | L4 |
| DS-VC-APD-004 | L4-04 | No Content Anti-Patterns | Anti-Pattern | L4 |
| DS-VC-APD-005 | L4-05 | No Strategic Anti-Patterns | Anti-Pattern | L4 |
| DS-VC-APD-006 | L4-06 | Token-Optimized Structure | Anti-Pattern | L4 |
| DS-VC-APD-007 | L4-07 | Relative URL Minimization | Anti-Pattern | L4 |
| DS-VC-APD-008 | L4-08 | Jargon Defined or Linked | Anti-Pattern | L4 |

**Diagnostic Codes (38):**

| DS ID | Code | Severity | Message (first line) |
|-------|------|----------|---------------------|
| DS-DC-E001 | E001 | ERROR | No H1 title found |
| DS-DC-E002 | E002 | ERROR | Multiple H1 titles found |
| DS-DC-E003 | E003 | ERROR | File is not valid UTF-8 encoding |
| DS-DC-E004 | E004 | ERROR | File uses non-LF line endings |
| DS-DC-E005 | E005 | ERROR | File contains invalid Markdown syntax |
| DS-DC-E006 | E006 | ERROR | Section contains links with empty or malformed URLs |
| DS-DC-E007 | E007 | ERROR | File is empty or contains only whitespace |
| DS-DC-E008 | E008 | ERROR | File exceeds the maximum recommended size |
| DS-DC-E009 | E009 | ERROR | Ecosystem has no llms.txt file |
| DS-DC-E010 | E010 | ERROR | A file in the ecosystem is not referenced by any other file |
| DS-DC-W001 | W001 | WARNING | No blockquote description found after the H1 title |
| DS-DC-W002 | W002 | WARNING | Section name does not match any of the 11 canonical names |
| DS-DC-W003 | W003 | WARNING | Link entry has no description text |
| DS-DC-W004 | W004 | WARNING | File contains no code examples |
| DS-DC-W005 | W005 | WARNING | Code block found without a language specifier |
| DS-DC-W006 | W006 | WARNING | Multiple sections use identical or near-identical description patterns |
| DS-DC-W007 | W007 | WARNING | No version or last-updated metadata found |
| DS-DC-W008 | W008 | WARNING | Sections do not follow the canonical 10-step ordering |
| DS-DC-W009 | W009 | WARNING | No Master Index found as the first H2 section |
| DS-DC-W010 | W010 | WARNING | File exceeds the recommended token budget for its tier |
| DS-DC-W011 | W011 | WARNING | One or more sections contain no meaningful content |
| DS-DC-W012 | W012 | WARNING | A link references another file that doesn't exist |
| DS-DC-W013 | W013 | WARNING | Index token count suggests a project large enough for llms-full.txt |
| DS-DC-W014 | W014 | WARNING | llms-full.txt does not contain content from all indexed files |
| DS-DC-W015 | W015 | WARNING | H1 title differs between files in the ecosystem |
| DS-DC-W016 | W016 | WARNING | Version metadata differs between files |
| DS-DC-W017 | W017 | WARNING | Significant content duplication between files |
| DS-DC-W018 | W018 | WARNING | One file consumes >70% of total ecosystem tokens |
| DS-DC-I001 | I001 | INFO | No LLM Instructions section found |
| DS-DC-I002 | I002 | INFO | No structured concept definitions found |
| DS-DC-I003 | I003 | INFO | No few-shot Q&A examples found |
| DS-DC-I004 | I004 | INFO | Relative URLs found in link entries |
| DS-DC-I005 | I005 | INFO | File classified as Type 2 Full |
| DS-DC-I006 | I006 | INFO | Optional sections not explicitly marked with token estimates |
| DS-DC-I007 | I007 | INFO | Domain-specific jargon used without inline definition |
| DS-DC-I008 | I008 | INFO | No llms-instructions.txt or LLM Instructions section exists |
| DS-DC-I009 | I009 | INFO | The index references categories for which no content page exists |
| DS-DC-I010 | I010 | INFO | The entire ecosystem consists of just llms.txt |

**Anti-Patterns (28):** See `constants.py` ANTI_PATTERN_REGISTRY for full listing.

**Design Decisions (16):** See v0.1.0 DECISION-001 through DECISION-016.

**Calibration Specimens (6):** Svelte (92), Pydantic (90), Vercel SDK (90), Shadcn UI (89), Cursor (42), NVIDIA (24).

**Canonical Names (11):** Master Index, LLM Instructions, Getting Started, Core Concepts, API Reference, Examples, Configuration, Advanced Topics, Troubleshooting, FAQ, Optional.

**Validation Levels (5):** L0 Parseable, L1 Structural, L2 Content Quality, L3 Best Practices, L4 DocStratum Extended.

**Quality Scoring (5):** Structural Dimension (30%), Content Dimension (50%), Anti-Pattern Dimension (20%), Grade Thresholds, Structural Gating.

**Ecosystem Health (5):** Coverage, Consistency, Completeness, Token Efficiency, Freshness.

### Appendix B: File Template Specifications

#### B.1 Validation Criterion Template

```markdown
# DS-VC-{DIM}-{SEQ}: {Criterion Name}

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-{DIM}-{SEQ} |
| **Status** | DRAFT / RATIFIED / DEPRECATED |
| **ASoT Version** | {version} |
| **Platinum ID** | {L0-01 through L4-08} |
| **Dimension** | {Structural (30%) / Content (50%) / Anti-Pattern Detection (20%)} |
| **Level** | {L0–L4} |
| **Weight** | {N} / {max} dimension points |
| **Pass Type** | {HARD / SOFT} |
| **Measurability** | {Fully measurable / Heuristic / Partially measurable} |
| **Provenance** | {Primary source; secondary sources} |

## Description

{What this criterion checks and why it matters for LLM consumption.}

## Pass Condition

{Precise, unambiguous definition of what "passing" means.
Should be translatable to a Python boolean expression.}

## Fail Condition

{What triggers a failure, including edge cases.}

## Emitted Diagnostics

- **DS-DC-{CODE}** ({SEVERITY}): Emitted when {condition}

## Related Anti-Patterns

- **DS-AP-{ID}**: {Name} — {brief relationship description}

## Related Criteria

- **DS-VC-{ID}**: {Name} — {how they relate}

## Calibration Notes

{How this criterion affects gold-standard specimen scores.
Which specimens pass/fail this criterion.}

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| {version} | {date} | Initial ratification |
```

#### B.2 Diagnostic Code Template

```markdown
# DS-DC-{CODE}: {ENUM_NAME}

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-{CODE} |
| **Status** | DRAFT / RATIFIED / DEPRECATED |
| **ASoT Version** | {version} |
| **Code** | {E/W/I}{NNN} |
| **Severity** | {ERROR / WARNING / INFO} |
| **Validation Level** | {L0–L4} |
| **Check ID** | {STR-001 / CNT-007 / CHECK-011 / etc.} |
| **Provenance** | {Research source} |

## Message

> {Exact message text from DiagnosticCode.message property}

## Remediation

> {Exact remediation text from DiagnosticCode.remediation property}

## Description

{Extended explanation of what this code means,
when it fires, and why it matters.}

## Triggering Criteria

- **DS-VC-{ID}**: Emitted when this criterion fails

## Related Anti-Patterns

- **DS-AP-{ID}**: {Name} — triggers this diagnostic

## Related Diagnostic Codes

- **DS-DC-{CODE}**: {How they relate}

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| {version} | {date} | Initial ratification |
```

#### B.3 Anti-Pattern Template

```markdown
# DS-AP-{CAT}-{SEQ}: {Pattern Name}

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-{CAT}-{SEQ} |
| **Status** | DRAFT / RATIFIED / DEPRECATED |
| **ASoT Version** | {version} |
| **Registry ID** | {AP-CRIT-001 / AP-STRUCT-001 / etc.} |
| **Category** | {Critical / Structural / Content / Strategic / Ecosystem} |
| **Check ID** | {CHECK-001 through CHECK-028} |
| **Severity Impact** | {Gate structural score at 29 / Reduce structural dimension /
                        Reduce content dimension / Deduction penalty / Ecosystem-level} |
| **Provenance** | {v0.0.4c / v0.0.7 §6} |

## Description

{What this anti-pattern looks like and why it's harmful.}

## Detection Logic

{How the validator detects this pattern.
Specific heuristics, thresholds, pattern matching rules.}

## Example (Synthetic)

{A constructed example demonstrating the anti-pattern.}

## Remediation

{How to fix the pattern.}

## Affected Criteria

- **DS-VC-{ID}**: This anti-pattern causes failure of this criterion

## Emitted Diagnostics

- **DS-DC-{CODE}**: Emitted when this pattern is detected

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| {version} | {date} | Initial ratification |
```

#### B.4 Additional Templates

Design decisions, calibration specimens, canonical names, validation levels, scoring definitions, and ecosystem health dimensions each have analogous templates. These follow the same structural principles (header block, metadata table, description, specification, cross-references, change history) adapted to their specific content. Full templates will be created during Phase A scaffolding (Step A.6) when the example files are authored.

### Appendix C: Naming Taxonomy Quick Reference

| Prefix | Type | Sub-Categories | Example |
|--------|------|----------------|---------|
| `DS-VC-` | Validation Criterion | `STR`, `CON`, `APD` | `DS-VC-STR-001` |
| `DS-DC-` | Diagnostic Code | (none — code prefix E/W/I) | `DS-DC-E001` |
| `DS-VL-` | Validation Level | (none — level number) | `DS-VL-L0` |
| `DS-DD-` | Design Decision | (none — sequential) | `DS-DD-014` |
| `DS-AP-` | Anti-Pattern | `CRIT`, `STRUCT`, `CONT`, `STRAT`, `ECO` | `DS-AP-CONT-007` |
| `DS-EH-` | Ecosystem Health | `COV`, `CON`, `COM`, `TOK`, `FRE` | `DS-EH-COV` |
| `DS-QS-` | Quality Scoring | `DIM`, `GRADE`, `CAP` | `DS-QS-DIM-STR` |
| `DS-CS-` | Calibration Specimen | (none — sequential) | `DS-CS-001` |
| `DS-CN-` | Canonical Name | (none — sequential) | `DS-CN-001` |

### Appendix D: Traceability Matrix

This matrix maps from Platinum Standard criteria (v0.0.6) to ASoT files, ensuring complete coverage:

| Platinum ID | ASoT Criterion | ASoT Diagnostic(s) | ASoT Anti-Pattern(s) | Level | Dimension |
|-------------|---------------|--------------------|--------------------|-------|-----------|
| L0-01 | DS-VC-STR-001 | DS-DC-E003 | DS-AP-CRIT-003 | L0 | Structural |
| L0-02 | DS-VC-STR-001 | DS-DC-E007 | DS-AP-CRIT-001 | L0 | Structural |
| L0-03 | DS-VC-STR-001 | DS-DC-E005 | — | L0 | Structural |
| L0-04 | DS-VC-STR-001 | DS-DC-E008 | DS-AP-STRAT-002 | L0 | Structural |
| L0-05 | DS-VC-STR-001 | DS-DC-E004 | DS-AP-CRIT-003 | L0 | Structural |
| L1-01 | DS-VC-STR-002 | DS-DC-E001 | DS-AP-CRIT-002 | L1 | Structural |
| L1-02 | DS-VC-STR-003 | DS-DC-E002 | — | L1 | Structural |
| L1-03 | DS-VC-STR-004 | DS-DC-W001 | — | L1 | Structural |
| L1-04 | DS-VC-STR-005 | — | DS-AP-STRUCT-002 | L1 | Structural |
| L1-05 | DS-VC-STR-006 | DS-DC-E006 | DS-AP-CRIT-004 | L1 | Structural |
| L1-06 | DS-VC-STR-007 | — | — | L1 | Structural |
| L2-01 | DS-VC-CON-001 | DS-DC-W003 | DS-AP-CONT-004 | L2 | Content |
| L2-02 | DS-VC-CON-002 | DS-DC-E006 | DS-AP-CRIT-004 | L2 | Content |
| L2-03 | DS-VC-CON-003 | — | DS-AP-CONT-002 | L2 | Content |
| L2-04 | DS-VC-CON-004 | DS-DC-W011 | DS-AP-STRUCT-002 | L2 | Content |
| L2-05 | DS-VC-CON-005 | — | DS-AP-STRUCT-003 | L2 | Content |
| L2-06 | DS-VC-CON-006 | — | — | L2 | Content |
| L2-07 | DS-VC-CON-007 | DS-DC-W006 | DS-AP-CONT-007 | L2 | Content |
| L3-01 | DS-VC-CON-008 | DS-DC-W002 | DS-AP-STRUCT-005 | L3 | Content |
| L3-02 | DS-VC-CON-009 | DS-DC-W009 | — | L3 | Content |
| L3-03 | DS-VC-CON-010 | DS-DC-W004 | DS-AP-CONT-006 | L3 | Content |
| L3-04 | DS-VC-CON-011 | DS-DC-W005 | — | L3 | Content |
| L3-05 | DS-VC-CON-012 | DS-DC-W010 | DS-AP-STRAT-002 | L3 | Content |
| L3-06 | DS-VC-STR-008 | DS-DC-W008 | DS-AP-STRUCT-004 | L3 | Structural |
| L3-07 | DS-VC-CON-013 | DS-DC-W007 | DS-AP-CONT-009 | L3 | Content |
| L3-08 | — (INFO-only, per ASOT-DEC-013) | — | — | L3 | — |
| L3-09 | DS-VC-STR-009 | — (composite) | DS-AP-CRIT-001–004 | L3 | Structural |
| L3-10 | DS-VC-STR-009 | — (composite) | DS-AP-STRUCT-001–005 | L3 | Structural |
| L4-01 | DS-VC-APD-001 | DS-DC-I001 | DS-AP-CONT-008 | L4 | Anti-Pattern |
| L4-02 | DS-VC-APD-002 | DS-DC-I002 | DS-AP-CONT-003 | L4 | Anti-Pattern |
| L4-03 | DS-VC-APD-003 | DS-DC-I003 | — | L4 | Anti-Pattern |
| L4-04 | DS-VC-APD-004 | — (composite) | DS-AP-CONT-001–009 | L4 | Anti-Pattern |
| L4-05 | DS-VC-APD-005 | — (composite) | DS-AP-STRAT-001–004 | L4 | Anti-Pattern |
| L4-06 | DS-VC-APD-006 | — | — | L4 | Anti-Pattern |
| L4-07 | DS-VC-APD-007 | DS-DC-I004 | — | L4 | Anti-Pattern |
| L4-08 | DS-VC-APD-008 | DS-DC-I007 | DS-AP-CONT-003 | L4 | Anti-Pattern |

---

## Revision History

| Date | Version | Change |
|------|---------|--------|
| 2026-02-08 | 0.1.0-draft | Initial draft — complete implementation strategy with 5 phases, templates, and appendices |

---

## Cross-References

| Document | Relevance |
|----------|-----------|
| RR-SPEC-v0.0.6 — Platinum Standard Definition | Primary source for 30 validation criteria |
| RR-SPEC-v0.0.7 — Ecosystem Pivot Specification | Source for ecosystem codes, anti-patterns, health dimensions |
| RR-SPEC-v0.1.0 — Project Foundation | Source for 16 design decisions |
| `src/docstratum/schema/diagnostics.py` | Authoritative code for 38 diagnostic codes |
| `src/docstratum/schema/constants.py` | Authoritative code for canonical names, anti-patterns, token tiers |
| `src/docstratum/schema/validation.py` | Authoritative code for validation levels and result models |
| `src/docstratum/schema/quality.py` | Authoritative code for scoring dimensions, grades, and weights |
| `src/docstratum/schema/ecosystem.py` | Authoritative code for ecosystem health dimensions |
| `src/docstratum/schema/classification.py` | Authoritative code for document types and size tiers |
