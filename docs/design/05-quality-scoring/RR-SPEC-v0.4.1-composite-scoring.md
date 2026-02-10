# v0.4.1 — Composite Scoring & Grading

> **Version:** v0.4.1
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.4.x-quality-scoring.md](RR-SCOPE-v0.4.x-quality-scoring.md)
> **Depends On:** v0.4.0 (three dimension scorers), v0.3.4a (anti-pattern detection), `schema/quality.py` (output models)
> **Consumed By:** v0.4.2 (calibration & testing), v0.5.x (CLI), v0.6.x (remediation), v0.8.x (reports)

---

## 1. Purpose

v0.4.1 is the **integration layer** of the scoring engine. It consumes the three `DimensionScore` instances produced by v0.4.0 and assembles a single `QualityScore` — the primary output of Phase 4.

### 1.1 What v0.4.1 Does

| Before v0.4.1                            | After v0.4.1                                                         |
| ---------------------------------------- | -------------------------------------------------------------------- |
| 3 independent `DimensionScore` instances | 1 composite `QualityScore` with `total_score`, `grade`, `dimensions` |
| No gating enforcement                    | DS-QS-GATE applied: critical AP → cap at 29                          |
| No grade label                           | EXEMPLARY through CRITICAL assigned                                  |
| Dimension details populated individually | All 30 criteria unified in `DimensionScore.details[]`                |

### 1.2 Data Flow

```
DimensionScore(STRUCTURAL)  ─┐
  (from v0.4.0b, 0–30 pts)   │
                              │
DimensionScore(CONTENT)     ──┼── v0.4.1a ──► raw composite (0–100)
  (from v0.4.0c, 0–50 pts)   │                    │
                              │                    ▼
DimensionScore(ANTI_PATTERN)──┘              v0.4.1b ──► gated composite (0–100, or ≤29)
  (from v0.4.0d, 0–20 pts)                        │
                                                   ▼
ValidationResult ────────────────────────► v0.4.1b (reads AP-CRIT flags)
  (from v0.3.x)                                    │
                                                   ▼
                                             v0.4.1c ──► QualityGrade
                                                   │
                                                   ▼
                                             v0.4.1d ──► details[] enrichment
                                                   │
                                                   ▼
                                              QualityScore (final output)
```

### 1.3 Transformation Summary

| Stage       | Input                                       | Output                               | Mutates Score? |
| ----------- | ------------------------------------------- | ------------------------------------ | -------------- |
| **v0.4.1a** | 3 × `DimensionScore`                        | `total_score: float`                 | Creates it     |
| **v0.4.1b** | `total_score` + `ValidationResult` AP flags | `total_score` (possibly capped)      | May cap        |
| **v0.4.1c** | `total_score` (final)                       | `QualityGrade`                       | No             |
| **v0.4.1d** | 3 × `DimensionScore.details[]`              | Enriched `details[]` with extra keys | Enriches       |

### 1.4 User Stories

| ID     | As a...            | I want to...                                             | So that...                                              |
| ------ | ------------------ | -------------------------------------------------------- | ------------------------------------------------------- |
| US-401 | file maintainer    | see a single 0–100 score for my llms.txt                 | I can quickly assess overall quality                    |
| US-402 | CI/CD pipeline     | get a grade (EXEMPLARY–CRITICAL) from the scoring engine | I can enforce quality gates on PRs                      |
| US-403 | file maintainer    | see that a critical anti-pattern capped my score at 29   | I understand why my score is low despite good content   |
| US-404 | remediation engine | read per-criterion details with points and compliance    | I can prioritize fixes by potential score impact        |
| US-405 | report generator   | receive a fully populated `QualityScore` model           | I can render per-dimension and per-criterion breakdowns |

---

## 2. Architecture

### 2.1 Module Structure

```
src/docstratum/scoring/
├── registry.py              # v0.4.0a — Criteria-to-diagnostic mapping
├── structural.py            # v0.4.0b — Structural dimension scorer
├── content.py               # v0.4.0c — Content dimension scorer
├── anti_pattern.py          # v0.4.0d — Anti-pattern dimension scorer
├── composite.py             # v0.4.1a–d — Composite scoring pipeline  ← NEW
└── __init__.py              # Public API exports
```

### 2.2 Design Decision: Single Module vs. Four Modules

The four v0.4.1 sub-parts are implemented in a **single module** (`composite.py`) rather than four separate files because:

1. **Sequential coupling:** v0.4.1b depends on v0.4.1a's result; v0.4.1c depends on v0.4.1b's result. They form a tight pipeline.
2. **Small size:** Each sub-part is 10–30 LOC. Four files of ~20 LOC each would be over-fragmented.
3. **Single public API surface:** External consumers call `score_file()` or `compute_composite()` — they never invoke sub-parts individually.
4. **Consistent with scope:** The dimension scorers (v0.4.0b/c/d) are separate files because they are _independent_. The composite stages are _dependent_.

### 2.3 Scoring Modes Reference

The composite layer does not evaluate individual criteria — it aggregates results from the dimension scorers. For reference, the scoring modes defined in v0.4.0a:

| Mode          | Formula                               | Used By                                                                     |
| ------------- | ------------------------------------- | --------------------------------------------------------------------------- |
| **BINARY**    | Pass = full, fail = 0                 | STR-001–003, 007, 008; CON-005–007, 009–010, 012–013; APD-001–003, 006, 008 |
| **GRADUATED** | `compliance_rate × max_points`        | STR-004–006, 009; CON-001–004, 008, 011; APD-004–005                        |
| **THRESHOLD** | `≥ threshold → full, < threshold → 0` | APD-007                                                                     |

---

## 3. Sub-Part Breakdown

| Sub-Part                                            | Title                       | Primary Output                  |
| --------------------------------------------------- | --------------------------- | ------------------------------- |
| [v0.4.1a](RR-SPEC-v0.4.1a-composite-calculation.md) | Composite Score Calculation | `total_score: float` (0–100)    |
| [v0.4.1b](RR-SPEC-v0.4.1b-gating-rule.md)           | Gating Rule Application     | Gated `total_score`, `is_gated` |
| [v0.4.1c](RR-SPEC-v0.4.1c-grade-assignment.md)      | Grade Assignment            | `QualityGrade`                  |
| [v0.4.1d](RR-SPEC-v0.4.1d-detail-population.md)     | Per-Check Detail Population | Enriched `details[]`            |

### 3.1 Dependency Chain

```
v0.4.0b/c/d (dimension scores) ──► v0.4.1a (sum)
                                        │
v0.3.4a (AP-CRIT detection) ────────► v0.4.1b (gate)
                                        │
                                    v0.4.1c (grade)
                                        │
v0.4.0b/c/d (per-criterion data) ──► v0.4.1d (enrich details)
                                        │
                                    QualityScore (assembled)
```

> **Parallelization Note:** v0.4.1d reads from the dimension scorers (not from the composite), so it can be developed in parallel with v0.4.1b/c. However, the final assembly requires all four sub-parts.

---

## 4. Exit Criteria

### 4.1 Functional

- [ ] `total_score` = `structural.points + content.points + anti_pattern.points` (simple sum, DECISION-014).
- [ ] Gating rule: any AP-CRIT-001 through AP-CRIT-004 detected → `total_score = min(total_score, 29)`.
- [ ] Gating sets `DimensionScore(STRUCTURAL).is_gated = True` when triggered.
- [ ] Grade assigned using `QualityGrade.from_score()` thresholds (≥90 EXEMPLARY, ≥70 STRONG, ≥50 ADEQUATE, ≥30 NEEDS_WORK, <30 CRITICAL).
- [ ] `QualityGrade.from_score()` accepts `float` input (or composite is `round()`ed first — see v0.4.1c spec).
- [ ] All 30 criteria appear in `DimensionScore.details[]` with `check_id`, `passed`, `weight`, `points`.
- [ ] Details enriched with `compliance_rate`, `diagnostic_count`, `level` keys.
- [ ] `QualityScore.dimensions` dictionary populated with all three `DimensionScore` instances.
- [ ] `QualityScore.scored_at` and `source_filename` populated.
- [ ] Composite score precision: `float` (not rounded to `int`), matching dimension scorer outputs.

### 4.2 Non-Functional

- [ ] ≥90% test coverage on `composite.py`.
- [ ] `black --check` and `ruff check` pass.
- [ ] No new fields added to `quality.py` Pydantic models without documented amendment.
- [ ] Composite computation completes in <10ms for any `ValidationResult` (no I/O, pure arithmetic).

### 4.3 Integration

- [ ] `score_file()` orchestrator function wires v0.4.0 scorers + v0.4.1 pipeline into a single call.
- [ ] Output `QualityScore` is JSON-serializable (Pydantic `.model_dump()` works cleanly).
- [ ] The `QualityScore` produced by `score_file()` is accepted by v0.4.2 calibration tests.

---

## 5. Dependencies

| Module                    | What v0.4.1 Uses                                                     |
| ------------------------- | -------------------------------------------------------------------- |
| `schema/validation.py`    | `ValidationResult`, `ValidationDiagnostic` (reads AP-CRIT flags)     |
| `schema/quality.py`       | `QualityScore`, `QualityGrade`, `DimensionScore`, `QualityDimension` |
| `schema/constants.py`     | `AntiPatternID` (AP-CRIT-001–004 for gating)                         |
| `scoring/registry.py`     | `CRITERIA_REGISTRY` (for detail enrichment in v0.4.1d)               |
| `scoring/structural.py`   | `score_structural()` → `DimensionScore(STRUCTURAL)`                  |
| `scoring/content.py`      | `score_content()` → `DimensionScore(CONTENT)`                        |
| `scoring/anti_pattern.py` | `score_anti_pattern()` → `DimensionScore(ANTI_PATTERN)`              |

### 5.1 Known Model Constraints

| Constraint                                         | Impact                                       | Resolution                        |
| -------------------------------------------------- | -------------------------------------------- | --------------------------------- |
| `QualityGrade.from_score()` accepts `int`          | Graduated scoring produces `float` composite | v0.4.1c: `round()` before calling |
| `DimensionScore.details` is `list[dict]`           | No schema enforcement on dict keys           | v0.4.1d: document required keys   |
| `QualityScore.total_score` has `le=100` constraint | Must ensure sum does not exceed 100.0        | By construction (30+50+20 = 100)  |
| No `CompositeScore` class exists                   | DS-QS-GATE spec references it                | Use functions, not a class        |

---

## 6. Design Decisions

| Decision                                              | Choice          | Rationale                                                              |
| ----------------------------------------------------- | --------------- | ---------------------------------------------------------------------- |
| Single `composite.py` module for all 4 sub-parts      | Yes             | Sequential coupling; small LOC per sub-part; single public API surface |
| No additional weighting multiplier at composite level | Yes             | Weights already embedded in max_points (30+50+20 = 100)                |
| `round()` composite before grade assignment           | Yes             | `from_score()` accepts int; avoids float threshold ambiguity           |
| Gating modifies `is_gated` on STRUCTURAL dimension    | Yes             | Scope doc §3.2 specifies this; gating is triggered by structural APs   |
| Score 0 for unevaluated criteria (gate-on-failure)    | Yes (finalized) | Scope doc §2.5 recommendation; simpler and penalizing                  |
| Details enriched with extra keys beyond minimum 4     | Yes             | `compliance_rate`, `diagnostic_count`, `level` enable remediation      |

---

## 7. Sub-Part Specifications

- [v0.4.1a — Composite Score Calculation](RR-SPEC-v0.4.1a-composite-calculation.md)
- [v0.4.1b — Gating Rule Application](RR-SPEC-v0.4.1b-gating-rule.md)
- [v0.4.1c — Grade Assignment](RR-SPEC-v0.4.1c-grade-assignment.md)
- [v0.4.1d — Per-Check Detail Population](RR-SPEC-v0.4.1d-detail-population.md)
