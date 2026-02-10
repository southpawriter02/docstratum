# v0.4.1a — Composite Score Calculation

> **Version:** v0.4.1a
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.1-composite-scoring.md](RR-SPEC-v0.4.1-composite-scoring.md)
> **Depends On:** v0.4.0b (`score_structural()`), v0.4.0c (`score_content()`), v0.4.0d (`score_anti_pattern()`)

---

## 1. Purpose

v0.4.1a computes the **raw composite score** by summing the three dimension scores. This is the first stage of the composite pipeline — it produces the pre-gating, pre-grade total.

### 1.1 Why Simple Addition

The 30-50-20 weighting from DECISION-014 is already embedded in the dimension `max_points` (30, 50, 20). No additional multiplier is needed:

```
total_score = structural.points + content.points + anti_pattern.points
```

Because `max_points` sum to 100 (30 + 50 + 20), the composite is inherently on a 0–100 scale.

### 1.2 User Story

> As the composite pipeline, I want to sum three dimension scores into a single numeric value so that the gating rule and grade assignment have a unified input.

### 1.3 Design Decision: Skipped-Level Criteria (Finalized)

When gate-on-failure prevents higher validation levels from running, unevaluated criteria **score 0**. This decision was recommended in the scope doc (§2.5) and is finalized here:

| Approach                               | Chosen? | Rationale                                                                 |
| -------------------------------------- | ------- | ------------------------------------------------------------------------- |
| Score 0 for unevaluated criteria       | **Yes** | Simple, penalizing; L0 failure = fundamentally broken file = near-0 score |
| Exclude from denominator (dynamic max) | No      | Risks inflating scores; complicates the scoring model                     |

**Impact:** A file that fails L0 receives 0 from all L1–L3 criteria because they were never evaluated. The composite for such a file is near-0, and DS-QS-GATE additionally caps it at 29 (CRITICAL).

---

## 2. Composite Calculation Logic

### 2.1 Formula

```python
def compute_composite(
    structural: DimensionScore,
    content: DimensionScore,
    anti_pattern: DimensionScore,
) -> float:
    """Sum three dimension scores into a raw composite (0–100).

    No additional weighting is applied because the dimension
    max_points already encode the 30/50/20 weight split (DECISION-014).

    Args:
        structural: DimensionScore(STRUCTURAL) from v0.4.0b (0–30).
        content: DimensionScore(CONTENT) from v0.4.0c (0–50).
        anti_pattern: DimensionScore(ANTI_PATTERN) from v0.4.0d (0–20).

    Returns:
        Raw composite score as float (0.0–100.0).

    Implements v0.4.1a. Grounding: DECISION-014 (30-50-20 weight model).
    """
    return structural.points + content.points + anti_pattern.points
```

### 2.2 Decision Tree

```
Input: 3 × DimensionScore instances
    │
    ├── Validate all three dimensions present
    │     ├── STRUCTURAL dimension present?
    │     │     └── No → raise ScoringError("Missing STRUCTURAL dimension")
    │     ├── CONTENT dimension present?
    │     │     └── No → raise ScoringError("Missing CONTENT dimension")
    │     └── ANTI_PATTERN dimension present?
    │           └── No → raise ScoringError("Missing ANTI_PATTERN dimension")
    │
    ├── Sum points
    │     total = structural.points + content.points + anti_pattern.points
    │
    ├── Assert invariant: 0.0 ≤ total ≤ 100.0
    │     └── Violation → log warning (should not happen if dimension scorers are correct)
    │
    └── Return total as float
```

### 2.3 Boundary Behavior

| Scenario                          | structural | content | anti_pattern | Composite | Notes                                      |
| --------------------------------- | ---------- | ------- | ------------ | --------- | ------------------------------------------ |
| **Perfect score**                 | 30.0       | 50.0    | 20.0         | 100.0     | All criteria pass with full compliance     |
| **Zero score**                    | 0.0        | 0.0     | 0.0          | 0.0       | All criteria fail                          |
| **L4 ceiling (v0.4.x)**           | 30.0       | 50.0    | 9.0          | 89.0      | APD-001–003, APD-008 score 0 (L4 deferred) |
| **Content-only failure**          | 30.0       | 0.0     | 20.0         | 50.0      | Strong structure, no content quality       |
| **Fractional points (graduated)** | 28.5       | 43.75   | 7.43         | 79.68     | Graduated scoring produces float           |
| **L0 failure (all skipped)**      | 0.0        | 0.0     | 0.0          | 0.0       | Gate-on-failure: unevaluated = 0           |
| **Only structural passes**        | 22.0       | 0.0     | 0.0          | 22.0      | L1 passes, L2+ gate failures               |

### 2.4 Precision

- **Type:** `float` — matches `DimensionScore.points` type.
- **Rounding:** Not applied at this stage. The raw composite preserves full float precision. Rounding (if any) occurs in v0.4.1c before grade assignment.
- **Arithmetic:** Standard Python float addition. No fixed-point arithmetic needed — maximum precision loss for 3 additions of values in [0, 50] is within machine epsilon.

---

## 3. Orchestrator Function

v0.4.1a also defines the top-level orchestration function that wires the entire scoring pipeline:

```python
from datetime import datetime

from docstratum.schema.constants import AntiPatternID
from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.quality import (
    DimensionScore,
    QualityDimension,
    QualityGrade,
    QualityScore,
)
from docstratum.schema.validation import ValidationResult
from docstratum.scoring.anti_pattern import score_anti_pattern
from docstratum.scoring.content import score_content
from docstratum.scoring.structural import score_structural


def score_file(
    result: ValidationResult,
    parsed: ParsedLlmsTxt,
    anti_pattern_results: dict | None = None,
) -> QualityScore:
    """Score a validated llms.txt file (full pipeline).

    Orchestrates the entire v0.4.x scoring pipeline:
      1. Score each dimension independently (v0.4.0b/c/d)
      2. Compute raw composite (v0.4.1a)
      3. Apply gating rule (v0.4.1b)
      4. Assign grade (v0.4.1c)
      5. Enrich details (v0.4.1d)

    Args:
        result: ValidationResult from v0.3.x pipeline.
        parsed: ParsedLlmsTxt model (needed for APD-006).
        anti_pattern_results: Anti-pattern detection results from v0.3.4.

    Returns:
        Fully populated QualityScore.

    Implements v0.4.1. Grounding: DS-QS-DIM-STR, DS-QS-DIM-CON,
    DS-QS-DIM-APD, DS-QS-GATE, DS-QS-GRADE.
    """
    # Step 1: Dimension scoring (v0.4.0b/c/d)
    str_score = score_structural(result, anti_pattern_results)
    con_score = score_content(result)
    apd_score = score_anti_pattern(result, parsed, anti_pattern_results)

    # Step 2: Composite calculation (v0.4.1a)
    raw_total = compute_composite(str_score, con_score, apd_score)

    # Step 3: Gating rule (v0.4.1b)
    total, is_gated = apply_gating(raw_total, result)
    if is_gated:
        str_score = str_score.model_copy(update={"is_gated": True})

    # Step 4: Grade assignment (v0.4.1c)
    grade = assign_grade(total)

    # Step 5: Detail enrichment (v0.4.1d)
    str_score = enrich_details(str_score)
    con_score = enrich_details(con_score)
    apd_score = enrich_details(apd_score)

    return QualityScore(
        total_score=total,
        grade=grade,
        dimensions={
            QualityDimension.STRUCTURAL: str_score,
            QualityDimension.CONTENT: con_score,
            QualityDimension.ANTI_PATTERN: apd_score,
        },
        scored_at=datetime.now(),
        source_filename=result.source_filename,
    )
```

---

## 4. Edge Cases

| Case                                  | Behavior                                            | Rationale                         |
| ------------------------------------- | --------------------------------------------------- | --------------------------------- |
| All dimensions produce 0.0            | Composite = 0.0                                     | Valid minimum                     |
| Anti-pattern at max (20.0) pre-v0.9.0 | Not possible — ceiling is 9.0                       | 4 L4-dependent criteria score 0   |
| Negative dimension points             | Not possible — `DimensionScore.points` has `ge=0`   | Pydantic constraint enforced      |
| Points exceed max_points              | Not possible — dimension scorers enforce ceiling    | By construction in v0.4.0b/c/d    |
| Sum exceeds 100.0                     | Log warning; should not occur (max is 30+50+20=100) | Defensive invariant check         |
| One dimension scorer not called       | `score_file()` always calls all three               | Orchestrator ensures completeness |

---

## 5. Deliverables

| File                                  | Description                      |
| ------------------------------------- | -------------------------------- |
| `src/docstratum/scoring/composite.py` | Composite scoring module         |
| `src/docstratum/scoring/__init__.py`  | Updated with `score_file` export |
| `tests/scoring/test_composite.py`     | Unit tests (v0.4.1a portion)     |

---

## 6. Test Plan (8 tests)

| #   | Test Name                                            | Input                                 | Expected                                         |
| --- | ---------------------------------------------------- | ------------------------------------- | ------------------------------------------------ |
| 1   | `test_composite_perfect_score`                       | 30.0 + 50.0 + 20.0                    | 100.0                                            |
| 2   | `test_composite_zero_score`                          | 0.0 + 0.0 + 0.0                       | 0.0                                              |
| 3   | `test_composite_l4_ceiling`                          | 30.0 + 50.0 + 9.0                     | 89.0                                             |
| 4   | `test_composite_fractional`                          | 28.5 + 43.75 + 7.43                   | 79.68                                            |
| 5   | `test_composite_single_dimension_zero`               | 30.0 + 0.0 + 20.0                     | 50.0                                             |
| 6   | `test_composite_returns_float`                       | Any valid inputs                      | `isinstance(result, float)`                      |
| 7   | `test_composite_preserves_precision`                 | 10.33 + 25.67 + 5.99                  | 41.99 (not 42)                                   |
| 8   | `test_score_file_orchestrator_returns_quality_score` | Mock ValidationResult + ParsedLlmsTxt | Returns `QualityScore` with all fields populated |

---

## 7. Changelog Requirements

```markdown
## [0.4.1a] - YYYY-MM-DD

**Composite Score Calculation — Raw composite from three dimension scores.**

### Added

#### Composite Scoring (`src/docstratum/scoring/composite.py`)

- `compute_composite()` — sums three `DimensionScore` instances into a 0–100 float (DECISION-014: 30+50+20 weight model)
- `score_file()` — top-level orchestrator wiring v0.4.0 dimension scorers through the v0.4.1 composite pipeline

#### Public API

- `score_file` exported from `docstratum.scoring`

### Notes

- **Design Decision:** Skipped-level criteria score 0 (not excluded from denominator). Scope doc §2.5 recommendation finalized.
- **Verification:** `black --check`, `ruff check`, ≥90% coverage on scoring module.
```

---

## 8. Limitations

| Limitation                          | Impact                                                   | Resolution Timeline   |
| ----------------------------------- | -------------------------------------------------------- | --------------------- |
| L4 ceiling (max ~89 points)         | EXEMPLARY grade unreachable at v0.4.x                    | v0.9.0 (L4 checks)    |
| No profile-based criteria filtering | All 30 criteria always scored                            | v0.5.x (profiles)     |
| No score caching                    | Rescoring same file recalculates everything              | v0.9.2 (perf)         |
| `from_score()` accepts `int` only   | Composite must be `round()`ed before grade (see v0.4.1c) | Optional model update |
