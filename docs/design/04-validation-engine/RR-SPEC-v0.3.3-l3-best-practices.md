# v0.3.3 — L3 Validation (Best Practices)

> **Version:** v0.3.3
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.3.x-validation-engine.md](../RR-SCOPE-v0.3.x-validation-engine.md)
> **Depends On:** v0.3.2 (L2 Content Quality — must pass before L3 runs), v0.2.0 (`ParsedLlmsTxt`), v0.2.1 (`DocumentClassification`, `Metadata`)
> **Consumed By:** v0.3.4 (Anti-Pattern Detection), v0.3.5 (Pipeline Assembly)

---

## 1. Purpose

v0.3.3 implements the **L3 Best Practices** level — the fourth and final tier of the standard validation pipeline. L3 verifies that the documentation follows recommended patterns derived from the v0.0.2c–v0.0.4c research phase. While L0–L2 ensure a file is parseable, structurally sound, and content-rich, L3 asks: does it follow the proven conventions that maximize LLM agent comprehension and human navigability?

### 1.1 Key Property: All WARNINGs

L3 emits **only WARNING-severity diagnostics**. No L3 check can block pipeline progression. This is by design — best practices are advisory, not structural requirements.

| Severity    | Codes                                    | Gate Impact                |
| ----------- | ---------------------------------------- | -------------------------- |
| **WARNING** | W002, W004, W005, W007, W008, W009, W010 | Does NOT block progression |

> **L3 gate behavior:** L3 always passes. All L3 diagnostics are WARNING severity, which by definition cannot block. A file that passes L2 will always also "pass" L3 — the diagnostics are quality observations that feed the scoring engine.

### 1.2 Relationship to Anti-Pattern Detection (v0.3.4)

L3 checks produce individual diagnostics. The anti-pattern detection pipeline (v0.3.4) aggregates these diagnostics into named patterns:

| L3 Diagnostic   | Downstream Anti-Pattern                               |
| --------------- | ----------------------------------------------------- |
| W002 (multiple) | AP-STRUCT-005 (Naming Nebula) when ≥50% non-canonical |
| W004            | AP-CONT-006 (Example Void)                            |
| W007            | AP-CONT-009 (Versionless Drift)                       |
| W008            | AP-STRUCT-004 (Section Shuffle)                       |

L3 checks are the _inputs_; anti-patterns are the _aggregated observations_.

### 1.3 User Stories

| ID       | As a...              | I want to...                                                       | So that...                                         |
| -------- | -------------------- | ------------------------------------------------------------------ | -------------------------------------------------- |
| US-033-1 | Documentation author | Know which sections use non-canonical names                        | I can rename them for better AI/human navigability |
| US-033-2 | Documentation author | Know if my file lacks a Master Index                               | I can add one (87% vs 31% LLM task success rate)   |
| US-033-3 | Documentation author | Know if code examples are missing or lack language tags            | I can add examples with proper specifiers          |
| US-033-4 | Documentation author | Know if my file exceeds its token budget tier                      | I can trim content or reclassify the document      |
| US-033-5 | Documentation author | Know if version metadata is missing                                | I can add temporal context for currency assessment |
| US-033-6 | Documentation author | Know if sections are out of canonical order                        | I can reorder for consistency and navigability     |
| US-033-7 | Scorer               | Read all L3 diagnostics to compute structural + content dimensions | I can score best-practice compliance accurately    |
| US-033-8 | CI pipeline          | See best-practice warnings without blocking the build              | I can progressively improve documentation quality  |

---

## 2. Architecture

### 2.1 Module Structure

```
src/docstratum/validation/checks/
├── l0_*.py                     # v0.3.0 (7 checks)
├── l1_*.py                     # v0.3.1 (4 checks)
├── l2_*.py                     # v0.3.2 (4 checks)
├── l3_canonical_names.py       # v0.3.3a — NEW
├── l3_master_index.py          # v0.3.3b — NEW
├── l3_code_examples.py         # v0.3.3c — NEW
├── l3_token_budget_version.py  # v0.3.3d — NEW
└── l3_structural_practices.py  # v0.3.3e — NEW
```

### 2.2 Check Interface

All L3 checks follow the uniform 3-argument interface:

```python
def check(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:
```

No L3 check introduces extended parameters (unlike v0.3.2b's `check_urls` flag).

### 2.3 Gate Behavior

```
L2 checks (v0.3.2a–d)
    │
    ├── ANY L2 ERROR? ──── Yes ──→ STOP. L2 failed. Skip L3.
    │                                     levels_passed[L2] = False
    └── No ──→ L2 passed. Run L3 checks.
                  │
                  ├── v0.3.3a: canonical names     → 0..N W002
                  ├── v0.3.3b: master index         → 0..1 W009
                  ├── v0.3.3c: code examples        → 0..1 W004, 0..N W005
                  ├── v0.3.3d: token/version        → 0..1 W010, 0..1 W007
                  ├── v0.3.3e: structural practices → 0..1 W008
                  │
                  └── ANY L3 ERROR? ──── No. (L3 has zero ERROR-severity codes.)
                                         levels_passed[L3] = True (always)
```

### 2.4 Data Flow

```
ParsedSection.canonical_name (all sections) ────── v0.3.3a ── 0..N W002
ParsedSection.canonical_name (match index) ──────── v0.3.3b ── 0..1 W009
ParsedSection.raw_content (code fence scan) ──────── v0.3.3c ── 0..1 W004, 0..N W005
ParsedLlmsTxt.estimated_tokens + SizeTier ─────── v0.3.3d ── 0..1 W010
Metadata.schema_version / raw_content patterns ── v0.3.3d ── 0..1 W007
ParsedSection.canonical_name (ordering) ─────────── v0.3.3e ── 0..1 W008
```

---

## 3. Sub-Part Breakdown

| Sub-Part                                              | Title                     | Code(s)     | Severity | Criteria                        | Planned Tests |
| ----------------------------------------------------- | ------------------------- | ----------- | -------- | ------------------------------- | ------------- |
| [v0.3.3a](RR-SPEC-v0.3.3a-canonical-section-names.md) | Canonical Section Names   | W002        | WARNING  | DS-VC-CON-008                   | 10            |
| [v0.3.3b](RR-SPEC-v0.3.3b-master-index-presence.md)   | Master Index Presence     | W009        | WARNING  | DS-VC-CON-009                   | 8             |
| [v0.3.3c](RR-SPEC-v0.3.3c-code-examples.md)           | Code Examples & Language  | W004, W005  | WARNING  | DS-VC-CON-010, CON-011          | 12            |
| [v0.3.3d](RR-SPEC-v0.3.3d-token-budget-version.md)    | Token Budget & Version    | W010, W007  | WARNING  | DS-VC-CON-012, CON-013          | 14            |
| [v0.3.3e](RR-SPEC-v0.3.3e-structural-practices.md)    | Structural Best Practices | W008        | WARNING  | DS-VC-STR-007, STR-008, STR-009 | 10            |
| **Total**                                             |                           | **7 codes** |          |                                 | **54**        |

### 3.1 Diagnostic Code Inventory

| Code | Name                        | Severity | Level | Sub-Part | Criterion | Status   |
| ---- | --------------------------- | -------- | ----- | -------- | --------- | -------- |
| W002 | NON_CANONICAL_SECTION_NAME  | WARNING  | L3    | v0.3.3a  | CON-008   | Existing |
| W009 | NO_MASTER_INDEX             | WARNING  | L3    | v0.3.3b  | CON-009   | Existing |
| W004 | NO_CODE_EXAMPLES            | WARNING  | L3    | v0.3.3c  | CON-010   | Existing |
| W005 | CODE_NO_LANGUAGE            | WARNING  | L3    | v0.3.3c  | CON-011   | Existing |
| W010 | TOKEN_BUDGET_EXCEEDED       | WARNING  | L3    | v0.3.3d  | CON-012   | Existing |
| W007 | MISSING_VERSION_METADATA    | WARNING  | L3    | v0.3.3d  | CON-013   | Existing |
| W008 | SECTION_ORDER_NON_CANONICAL | WARNING  | L3    | v0.3.3e  | STR-007   | Existing |

> All 7 diagnostic codes already exist in `diagnostics.py`. No new codes are introduced by v0.3.3.

### 3.2 Scope Doc §3.4 Reconciliation

The scope doc (§3.4) defines 6 sub-parts (v0.3.3a–f) with a different grouping than the roadmap's 5 sub-parts. This spec follows the **roadmap structure** as the canonical source:

| Scope Doc Sub-Part                      | Roadmap Sub-Part                               | Resolution                                                 |
| --------------------------------------- | ---------------------------------------------- | ---------------------------------------------------------- |
| v0.3.3a — Canonical Names (W002)        | v0.3.3a — Canonical Section Names              | ✓ Aligned                                                  |
| v0.3.3b — Code Examples (W004, W005)    | v0.3.3c — Code Examples & Language             | Reordered (roadmap inserts Master Index at b)              |
| v0.3.3c — Formulaic Descriptions (W006) | **N/A — moved to v0.3.2c**                     | Formulaic detection is an L2 content quality check, not L3 |
| v0.3.3d — Version Metadata (W007)       | v0.3.3d — Token Budget & Version (merged)      | Roadmap groups W007 + W010                                 |
| v0.3.3e — Section Ordering (W008)       | v0.3.3e — Structural Best Practices (expanded) | Roadmap adds STR-008/009 aggregation                       |
| v0.3.3f — Token Budget (W010)           | v0.3.3d — Token Budget & Version (merged)      | Roadmap merges with version                                |
| **N/A**                                 | v0.3.3b — Master Index Presence (W009)         | **Scope doc omission** — roadmap adds this                 |

> [!NOTE]
> The scope doc's v0.3.3c (Formulaic Description Detection / W006) has been **superseded** by v0.3.2c, which already handles formulaic description detection at L2. The roadmap correctly excludes it from L3. This spec reflects the roadmap's cleaner separation.

---

## 4. Acceptance Criteria

### 4.1 Functional

- [ ] All five check modules exist in `src/docstratum/validation/checks/`.
- [ ] W002 emitted per section with non-canonical name.
- [ ] W009 emitted once when no Master Index-like section exists.
- [ ] W004 emitted once when no fenced code blocks found.
- [ ] W005 emitted per code block lacking a language specifier.
- [ ] W010 emitted once when token count exceeds tier budget.
- [ ] W007 emitted once when no version/date metadata found.
- [ ] W008 emitted once when canonical sections are out of order.
- [ ] L3 checks only run when L2 has passed.
- [ ] L3 always passes (zero ERROR codes).
- [ ] All diagnostics include `code`, `severity`, `message`, `remediation`, `level`, `check_id`.

### 4.2 Non-Functional

- [ ] `pytest --cov=docstratum.validation --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass.
- [ ] Google-style docstrings; modules reference "Implements v0.3.3x."

### 4.3 CHANGELOG Entry Template

```markdown
## [0.3.3] - YYYY-MM-DD

**L3 Validation — Best practice checks for section naming, Master Index, code examples, token budgets, version metadata, and structural ordering.**

### Added

#### L3 Checks (`src/docstratum/validation/checks/`)

- W002 canonical names: warns per section using non-canonical name (v0.3.3a)
- W009 Master Index: warns when no Master Index section found (v0.3.3b)
- W004 code examples: warns when no fenced code blocks found (v0.3.3c)
- W005 code language: warns per code block without language specifier (v0.3.3c)
- W010 token budget: warns when file exceeds tier token limit (v0.3.3d)
- W007 version metadata: warns when no version/date metadata found (v0.3.3d)
- W008 section ordering: warns when canonical sections are out of order (v0.3.3e)
```

---

## 5. Dependencies

| Module                     | What v0.3.3 Uses                                                                                              |
| -------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `schema/parsed.py`         | `ParsedLlmsTxt.sections`, `.estimated_tokens`, `.raw_content`, `ParsedSection.canonical_name`, `.raw_content` |
| `schema/diagnostics.py`    | W002, W004, W005, W007, W008, W009, W010                                                                      |
| `schema/validation.py`     | `ValidationDiagnostic`, `ValidationLevel.L3_BEST_PRACTICES`                                                   |
| `schema/classification.py` | `DocumentClassification.size_tier`, `SizeTier`                                                                |
| `schema/constants.py`      | `CANONICAL_SECTION_ORDER`, `SECTION_NAME_ALIASES`, `TOKEN_BUDGET_TIERS`, `VERSION_PATTERNS`                   |
| `schema/enrichment.py`     | `Metadata.schema_version`, `Metadata.last_updated` (v0.2.1d)                                                  |

### 5.1 Limitations

| Limitation                               | Reason                                                                    | When Addressed                               |
| ---------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------- |
| No fuzzy section name matching           | Exact + alias matching only; no Levenshtein suggestions                   | Future: could suggest closest canonical name |
| Version detection is pattern-based       | May miss non-standard versioning schemes                                  | By design (permissive patterns)              |
| Token count is an estimate               | `estimated_tokens` uses word-count heuristic, not `cl100k_base` tokenizer | v0.5.x (precision tokenization)              |
| STR-008/009 criteria are composite gates | v0.3.3e only checks ordering (W008); full anti-pattern gates are v0.3.4   | v0.3.4a–d                                    |

---

## 6. Design Decisions

| Decision                                 | Choice | Rationale                                                                                                                          |
| ---------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| All WARNING severity                     | Yes    | Best practices are advisory. Blocking would reject 40%+ of real-world files on section naming alone.                               |
| L3 always passes (no gate)               | Yes    | L3 produces quality observations for scoring; it does not gate progression.                                                        |
| Formulaic detection at L2 (not L3)       | Yes    | Formulaic descriptions are a content quality issue (CON-007), not a best practice pattern. Roadmap correctly places it at v0.3.2c. |
| Master Index at L3 (not L1)              | Yes    | Master Index is a best practice (87% vs 31% LLM success), not a structural requirement. Many valid files lack one.                 |
| Token budget separate from E008          | Yes    | E008 (L0) = hard 100K cap. W010 (L3) = tier-appropriate budget advisory. Different concerns, different severities.                 |
| Version metadata patterns are permissive | Yes    | Any recognizable version/date string suffices. The criterion detects _absence_, not correctness.                                   |
| No new diagnostic codes                  | Yes    | All 7 L3 codes already exist in `diagnostics.py`. L3 is purely consuming existing codes.                                           |

---

## 7. Sub-Part Specifications

- [v0.3.3a — Canonical Section Names](RR-SPEC-v0.3.3a-canonical-section-names.md)
- [v0.3.3b — Master Index Presence](RR-SPEC-v0.3.3b-master-index-presence.md)
- [v0.3.3c — Code Examples & Language](RR-SPEC-v0.3.3c-code-examples.md)
- [v0.3.3d — Token Budget & Version](RR-SPEC-v0.3.3d-token-budget-version.md)
- [v0.3.3e — Structural Best Practices](RR-SPEC-v0.3.3e-structural-practices.md)
