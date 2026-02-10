# v0.4.1c — Grade Assignment

> **Version:** v0.4.1c
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.1-composite-scoring.md](RR-SPEC-v0.4.1-composite-scoring.md)
> **Depends On:** v0.4.1b (gated composite score), `schema/quality.py` (`QualityGrade.from_score()`)
> **Grounding:** DS-QS-GRADE (full specification)

---

## 1. Purpose

v0.4.1c maps the final composite score (post-gating) to a `QualityGrade` enum value using the DS-QS-GRADE threshold table.

### 1.1 User Story

> As a CI/CD pipeline, I want a single grade label (EXEMPLARY–CRITICAL) derived from the numeric score so that I can enforce pass/fail gates using human-readable categories.

---

## 2. Grade Thresholds (DS-QS-GRADE)

| Grade      | Score Range | Validation Level Alignment | Semantic Meaning                         |
| ---------- | ----------- | -------------------------- | ---------------------------------------- |
| EXEMPLARY  | ≥ 90        | L4 (DocStratum Extended)   | Best-in-class, all enrichment present    |
| STRONG     | 70–89       | L3 (Best Practices)        | Follows best practices, minor gaps       |
| ADEQUATE   | 50–69       | L2 (Content Quality)       | Functional content, room for improvement |
| NEEDS_WORK | 30–49       | L1 (Structural)            | Structure present, content weak          |
| CRITICAL   | 0–29        | L0 (Parseable Only)        | Fundamentally broken or minimal          |

### 2.1 L4 Ceiling at v0.4.x

Maximum achievable composite is ~89 (30 + 50 + 9). **EXEMPLARY is unreachable** until v0.9.0 activates L4 checks.

---

## 3. The Float-to-Int Problem

### 3.1 The Issue

`QualityGrade.from_score()` accepts `int`, but graduated scoring produces `float` composites (e.g., 89.5, 69.7).

### 3.2 Design Decision: Round Before Calling

| Approach                              | Chosen? | Rationale                                                         |
| ------------------------------------- | ------- | ----------------------------------------------------------------- |
| **`round()` before calling**          | **Yes** | Non-breaking; standard banker's rounding; clear boundary behavior |
| Update `from_score()` to accept float | No      | Requires model change; scope says no model changes                |
| Truncate (`int()`)                    | No      | Biased downward; 89.9 → 89 → STRONG feels wrong                   |
| Ceiling (`math.ceil`)                 | No      | Biased upward; 29.1 → 30 → NEEDS_WORK too generous                |

### 3.3 Rounding Behavior at Boundaries

| Float Score | `round()` | Grade      | Notes                              |
| ----------- | --------- | ---------- | ---------------------------------- |
| 89.5        | 90        | EXEMPLARY  | Banker's rounding: .5 on even → up |
| 89.49       | 89        | STRONG     | Rounds down                        |
| 69.5        | 70        | STRONG     | Banker's rounding: .5 on even → up |
| 29.5        | 30        | NEEDS_WORK | Rounds up — escapes CRITICAL       |
| 29.49       | 29        | CRITICAL   | Rounds down — stays gated range    |

---

## 4. Implementation

```python
"""Implements v0.4.1c — Grade Assignment."""

import logging
from docstratum.schema.quality import QualityGrade

logger = logging.getLogger(__name__)


def assign_grade(total_score: float) -> QualityGrade:
    """Assign a quality grade from the composite score.

    Rounds the float composite to the nearest integer using
    Python's default banker's rounding, then maps to a grade.

    Args:
        total_score: The (possibly gated) composite score (0.0–100.0).

    Returns:
        QualityGrade enum value.

    Implements v0.4.1c. Grounding: DS-QS-GRADE.
    """
    rounded = max(0, min(100, round(total_score)))
    grade = QualityGrade.from_score(rounded)

    logger.info(
        "Grade assigned: %s (score=%.2f, rounded=%d).",
        grade.value, total_score, rounded,
    )
    return grade
```

---

## 5. Boundary Scenarios

| Score | Rounded | Grade      | Reason               |
| ----- | ------- | ---------- | -------------------- |
| 100.0 | 100     | EXEMPLARY  | Perfect score        |
| 90.0  | 90      | EXEMPLARY  | At threshold         |
| 89.5  | 90      | EXEMPLARY  | Banker's rounding up |
| 89.0  | 89      | STRONG     | Below threshold      |
| 70.0  | 70      | STRONG     | At threshold         |
| 50.0  | 50      | ADEQUATE   | At threshold         |
| 30.0  | 30      | NEEDS_WORK | At threshold         |
| 29.5  | 30      | NEEDS_WORK | Banker's rounding up |
| 29.0  | 29      | CRITICAL   | Gating cap value     |
| 0.0   | 0       | CRITICAL   | Minimum score        |

---

## 6. Edge Cases

| Case                   | Behavior                   | Rationale                  |
| ---------------------- | -------------------------- | -------------------------- |
| Score = 0.0            | CRITICAL                   | Minimum valid score        |
| Score = 100.0          | EXEMPLARY                  | Maximum valid score        |
| Score > 100.0          | Clamped to 100, EXEMPLARY  | Defensive clamp            |
| Score < 0.0            | Clamped to 0, CRITICAL     | Defensive clamp            |
| Score = 89.5 (L4 ceil) | EXEMPLARY (rounds to 90)   | Unlikely at v0.4.x         |
| Gated score = 29.0     | CRITICAL (29 rounds to 29) | Gating always produces int |

---

## 7. Test Plan (12 tests)

| #   | Test Name                     | Input | Expected                  |
| --- | ----------------------------- | ----- | ------------------------- |
| 1   | `test_grade_exemplary_at_90`  | 90.0  | EXEMPLARY                 |
| 2   | `test_grade_exemplary_at_100` | 100.0 | EXEMPLARY                 |
| 3   | `test_grade_strong_at_89`     | 89.0  | STRONG                    |
| 4   | `test_grade_strong_at_70`     | 70.0  | STRONG                    |
| 5   | `test_grade_adequate_at_69`   | 69.0  | ADEQUATE                  |
| 6   | `test_grade_adequate_at_50`   | 50.0  | ADEQUATE                  |
| 7   | `test_grade_needs_work_at_49` | 49.0  | NEEDS_WORK                |
| 8   | `test_grade_needs_work_at_30` | 30.0  | NEEDS_WORK                |
| 9   | `test_grade_critical_at_29`   | 29.0  | CRITICAL                  |
| 10  | `test_grade_critical_at_0`    | 0.0   | CRITICAL                  |
| 11  | `test_grade_rounding_89_5`    | 89.5  | EXEMPLARY (rounds to 90)  |
| 12  | `test_grade_rounding_29_5`    | 29.5  | NEEDS_WORK (rounds to 30) |

---

## 8. Deliverables

| File                                  | Description                                     |
| ------------------------------------- | ----------------------------------------------- |
| `src/docstratum/scoring/composite.py` | `assign_grade()` function (in composite module) |
| `tests/scoring/test_composite.py`     | Grade assignment tests (v0.4.1c portion)        |
