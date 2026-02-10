# v0.4.0 — Dimension Scoring

> **Version:** v0.4.0
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.4.x-quality-scoring.md](../RR-SCOPE-v0.4.x-quality-scoring.md)
> **Depends On:** v0.3.x (`ValidationResult`, `ValidationDiagnostic`), v0.1.2b (`QualityScore`, `DimensionScore`, `QualityGrade`, `QualityDimension`), v0.1.2a (`DiagnosticCode`, `Severity`), `constants.py` (`AntiPatternID`, `AntiPatternCategory`)
> **Consumed By:** v0.4.1 (Composite Scoring & Grading), v0.5.x (CLI), v0.6.x (Remediation), v0.8.x (Reports)

---

## 1. Purpose

v0.4.0 implements the **three independent dimension scorers** — the components that read a `ValidationResult` from v0.3.x, evaluate their assigned validation criteria, and produce `DimensionScore` instances. The three dimensions operate independently; no dimension depends on another's result.

### 1.1 What v0.4.0 Adds

| Before v0.4.0                           | After v0.4.0                                                              |
| --------------------------------------- | ------------------------------------------------------------------------- |
| `ValidationResult` with raw diagnostics | 3 × `DimensionScore` with points, compliance rates, per-criterion details |
| "W003 emitted 15 times"                 | STR/CON/APD dimension points with graduated scoring                       |
| No numeric assessment                   | 0–100 point scale (30 + 50 + 20) with float precision                     |

### 1.2 Dimension Summary

| Dimension                        | Criteria         | Max Points | Weight   | Role                                           |
| -------------------------------- | ---------------- | ---------- | -------- | ---------------------------------------------- |
| **Structural** (DS-QS-DIM-STR)   | 9 (STR-001–009)  | 30         | 30%      | Gating — necessary but not sufficient          |
| **Content** (DS-QS-DIM-CON)      | 13 (CON-001–013) | 50         | 50%      | Primary driver — strongest quality predictor   |
| **Anti-Pattern** (DS-QS-DIM-APD) | 8 (APD-001–008)  | 20         | 20%      | Differentiator — path from STRONG to EXEMPLARY |
| **Total**                        | **30**           | **100**    | **100%** |                                                |

### 1.3 L4 Ceiling

Until v0.9.0 activates L4 checks, the APD dimension's effective maximum is **9 points** (APD-004: 3 + APD-005: 2 + APD-006: 2 + APD-007: 2). APD-001, APD-002, APD-003, and APD-008 score 0. This yields a composite ceiling of ~89 points — **EXEMPLARY (≥90) is not achievable until v0.9.0.** Highest attainable grade at v0.4.x is **STRONG**.

### 1.4 User Stories

| ID       | As a...            | I want to...                                          | So that...                                          |
| -------- | ------------------ | ----------------------------------------------------- | --------------------------------------------------- |
| US-040-1 | Scorer             | Evaluate 30 criteria from diagnostics                 | I can produce a numeric quality assessment          |
| US-040-2 | CLI user           | See per-dimension points                              | I know where my file is strong vs weak              |
| US-040-3 | Remediation engine | Read per-criterion details with compliance rates      | I can compute score-impact projections              |
| US-040-4 | Developer          | Add L4 diagnostic codes without changing scorer logic | The APD scorer auto-activates L4-dependent criteria |

---

## 2. Architecture

### 2.1 Module Structure

```
src/docstratum/scoring/
├── __init__.py              # Public API (deferred to v0.4.1)
├── registry.py              # v0.4.0a — Criteria-to-diagnostic mapping
├── structural.py            # v0.4.0b — Structural dimension scorer
├── content.py               # v0.4.0c — Content dimension scorer
├── anti_pattern.py          # v0.4.0d — Anti-pattern dimension scorer
└── ...
```

### 2.2 Data Flow

```
ValidationResult (from v0.3.x)
  │
  ├── registry.py ← CRITERIA_REGISTRY (static mapping)
  │      │
  │      ├── structural.py → DimensionScore(STRUCTURAL, max=30)
  │      ├── content.py    → DimensionScore(CONTENT, max=50)
  │      └── anti_pattern.py → DimensionScore(ANTI_PATTERN, max=20)
  │
  └── → v0.4.1 (Composite Scoring & Grading)
```

### 2.3 Scoring Modes

| Mode          | Formula                               | Used By                                                                                                    |
| ------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **BINARY**    | Pass = full points, Fail = 0          | STR-001, STR-002, STR-003, CON-005, CON-006, CON-007, CON-009, CON-010, CON-012, CON-013, STR-007, STR-008 |
| **GRADUATED** | `compliance_rate × max_points`        | STR-004, STR-005, STR-006, STR-009, CON-001, CON-002, CON-003, CON-004, CON-008, CON-011, APD-004, APD-005 |
| **THRESHOLD** | `≥ threshold → full, < threshold → 0` | Special case of GRADUATED with binary output                                                               |

---

## 3. Sub-Part Breakdown

| Sub-Part                                          | Title                                   | Primary Output                 |
| ------------------------------------------------- | --------------------------------------- | ------------------------------ |
| [v0.4.0a](RR-SPEC-v0.4.0a-criteria-registry.md)   | Criteria-to-Diagnostic Mapping Registry | `CRITERIA_REGISTRY`            |
| [v0.4.0b](RR-SPEC-v0.4.0b-structural-scorer.md)   | Structural Dimension Scorer             | `DimensionScore(STRUCTURAL)`   |
| [v0.4.0c](RR-SPEC-v0.4.0c-content-scorer.md)      | Content Dimension Scorer                | `DimensionScore(CONTENT)`      |
| [v0.4.0d](RR-SPEC-v0.4.0d-anti-pattern-scorer.md) | Anti-Pattern Dimension Scorer           | `DimensionScore(ANTI_PATTERN)` |

---

## 4. Acceptance Criteria

### 4.1 Functional

- [ ] Criteria registry maps all 30 criteria to diagnostic codes and scoring modes.
- [ ] Structural scorer evaluates 9 STR criteria → `DimensionScore(STRUCTURAL)`, 0–30 points.
- [ ] Content scorer evaluates 13 CON criteria → `DimensionScore(CONTENT)`, 0–50 points.
- [ ] APD scorer evaluates 8 APD criteria → `DimensionScore(ANTI_PATTERN)`, 0–20 points.
- [ ] Graduated scoring produces `float` points (e.g., 3.75 from 75% compliance on 5-point criterion).
- [ ] L4-dependent criteria (APD-001–003, APD-008) score 0 when L4 codes absent.
- [ ] Each `DimensionScore.details[]` populated with per-criterion `check_id`, `passed`, `weight`, `points`.
- [ ] `checks_passed`, `checks_failed`, `checks_total` correctly populated.

### 4.2 Non-Functional

- [ ] `pytest --cov=docstratum.scoring --cov-fail-under=90` passes.
- [ ] `black --check` and `ruff check` pass.
- [ ] Google-style docstrings; modules reference "Implements v0.4.0x."

### 4.3 CHANGELOG Entry Template

```markdown
## [0.4.0] - YYYY-MM-DD

**Dimension Scoring — three independent scorers evaluate 30 criteria across Structural, Content, and Anti-Pattern dimensions.**

### Added

#### Quality Scoring (`src/docstratum/scoring/`)

- Criteria-to-Diagnostic Registry: 30 criteria mapped to diagnostic codes with BINARY/GRADUATED scoring modes
- Structural Dimension Scorer: 9 criteria (STR-001–009), 0–30 points
- Content Dimension Scorer: 13 criteria (CON-001–013), 0–50 points
- Anti-Pattern Dimension Scorer: 8 criteria (APD-001–008), 0–20 points (9 effective until v0.9.0)
- Graduated scoring with float precision
- Per-criterion detail population for drill-down reporting
```

---

## 5. Dependencies

| Module                  | What v0.4.0 Uses                                                     |
| ----------------------- | -------------------------------------------------------------------- |
| `schema/validation.py`  | `ValidationResult`, `ValidationDiagnostic`, `ValidationLevel`        |
| `schema/quality.py`     | `QualityScore`, `QualityGrade`, `DimensionScore`, `QualityDimension` |
| `schema/diagnostics.py` | `DiagnosticCode`, `Severity`                                         |
| `schema/constants.py`   | `AntiPatternID`, `AntiPatternCategory`, `ANTI_PATTERN_REGISTRY`      |
| `schema/parsed.py`      | `ParsedLlmsTxt` (APD-006 only — token distribution)                  |

### 5.1 Limitations

| Limitation                                | Reason                                       | When Addressed                 |
| ----------------------------------------- | -------------------------------------------- | ------------------------------ |
| L4-dependent criteria score 0             | I001, I002, I003, I007 not emitted           | v0.9.0                         |
| EXEMPLARY grade unreachable               | APD ceiling at 9/20 = composite max ~89      | v0.9.0                         |
| APD-006 reads `ParsedLlmsTxt`             | Token distribution not in `ValidationResult` | By design (scope doc option a) |
| `QualityGrade.from_score()` accepts `int` | Graduated scoring produces `float`           | Design decision in v0.4.0      |

---

## 6. Design Decisions

| Decision                                                        | Choice         | Rationale                                                               |
| --------------------------------------------------------------- | -------------- | ----------------------------------------------------------------------- |
| Score 0 for unevaluated criteria (not exclude from denominator) | Yes            | Simpler, more penalizing for broken files, consistent with DS-QS-GATE   |
| `float` points throughout                                       | Yes            | Graduated scoring needs fractional precision                            |
| `round()` composite before grade assignment                     | Yes            | `QualityGrade.from_score()` accepts `int`; rounding is the simplest fix |
| APD-006 reads `ParsedLlmsTxt` directly                          | Yes (option a) | Simpler than adding a new diagnostic code; clean exception documented   |
| No weighting multipliers                                        | Correct        | Point allocations already embed 30/50/20 weighting                      |
| Registry is static (not dynamic)                                | Yes            | All 30 criteria known at compile time; no runtime discovery needed      |
| Separate scorer modules                                         | Yes            | Independent development and testing; clean separation                   |

---

## 7. Sub-Part Specifications

- [v0.4.0a — Criteria-to-Diagnostic Mapping Registry](RR-SPEC-v0.4.0a-criteria-registry.md)
- [v0.4.0b — Structural Dimension Scorer](RR-SPEC-v0.4.0b-structural-scorer.md)
- [v0.4.0c — Content Dimension Scorer](RR-SPEC-v0.4.0c-content-scorer.md)
- [v0.4.0d — Anti-Pattern Dimension Scorer](RR-SPEC-v0.4.0d-anti-pattern-scorer.md)
