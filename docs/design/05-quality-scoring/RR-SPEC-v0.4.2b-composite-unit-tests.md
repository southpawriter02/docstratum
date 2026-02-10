# v0.4.2b — Composite & Gating Unit Tests

> **Version:** v0.4.2b
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.2-calibration-testing.md](RR-SPEC-v0.4.2-calibration-testing.md)
> **Depends On:** v0.4.1a–d (composite pipeline), v0.4.2a (dimension tests for fixture patterns)

---

## 1. Purpose

v0.4.2b defines the **unit test suite for the composite scoring pipeline** — the integration layer from v0.4.1. It tests composite calculation, gating rule enforcement, grade assignment, and detail enrichment in isolation using mock `DimensionScore` inputs.

### 1.1 User Story

> As a developer, I want the composite pipeline tested at every integration seam — sum, gate, grade, enrich — so that I can verify each stage independently and pinpoint regressions to a specific pipeline step.

### 1.2 Coverage Target

```
pytest tests/scoring/test_composite.py \
    --cov=docstratum.scoring.composite \
    --cov-fail-under=90
```

---

## 2. Fixture Factory

```python
"""Tests for the Composite Scoring Pipeline (v0.4.1a–d).

Uses mock DimensionScore instances to isolate composite logic
from dimension scorers.

Implements v0.4.2b.
"""

import pytest
from docstratum.schema.quality import (
    DimensionScore,
    QualityDimension,
    QualityGrade,
    QualityScore,
)
from docstratum.schema.validation import ValidationResult, ValidationLevel
from docstratum.schema.constants import AntiPatternID
from docstratum.scoring.composite import (
    compute_composite,
    apply_gating,
    assign_grade,
    enrich_details,
    score_file,
)


def make_dimension_score(
    dimension: QualityDimension,
    points: float,
    max_points: float | None = None,
    is_gated: bool = False,
    details: list[dict] | None = None,
) -> DimensionScore:
    """Create a DimensionScore with minimal boilerplate."""
    if max_points is None:
        max_points = {
            QualityDimension.STRUCTURAL: 30.0,
            QualityDimension.CONTENT: 50.0,
            QualityDimension.ANTI_PATTERN: 20.0,
        }[dimension]
    return DimensionScore(
        dimension=dimension,
        points=points,
        max_points=max_points,
        checks_passed=int(points > 0),
        checks_failed=int(points == 0),
        checks_total=1,
        details=details or [],
        is_gated=is_gated,
    )


# --- Standard score combinations ---

PERFECT_DIMENSIONS = {
    QualityDimension.STRUCTURAL: make_dimension_score(
        QualityDimension.STRUCTURAL, 30.0
    ),
    QualityDimension.CONTENT: make_dimension_score(
        QualityDimension.CONTENT, 50.0
    ),
    QualityDimension.ANTI_PATTERN: make_dimension_score(
        QualityDimension.ANTI_PATTERN, 20.0
    ),
}

ZERO_DIMENSIONS = {
    QualityDimension.STRUCTURAL: make_dimension_score(
        QualityDimension.STRUCTURAL, 0.0
    ),
    QualityDimension.CONTENT: make_dimension_score(
        QualityDimension.CONTENT, 0.0
    ),
    QualityDimension.ANTI_PATTERN: make_dimension_score(
        QualityDimension.ANTI_PATTERN, 0.0
    ),
}
```

---

## 3. Composite Calculation Tests (v0.4.1a)

| #   | Test Name                                  | Dimensions              | Expected Composite |
| --- | ------------------------------------------ | ----------------------- | ------------------ |
| 1   | `test_composite_perfect`                   | 30 + 50 + 20            | 100.0              |
| 2   | `test_composite_zero`                      | 0 + 0 + 0               | 0.0                |
| 3   | `test_composite_mid_range`                 | 20 + 30 + 10            | 60.0               |
| 4   | `test_composite_fractional`                | 28.5 + 47.25 + 18.0     | 93.75              |
| 5   | `test_composite_single_dimension_zero`     | 0 + 50 + 20             | 70.0               |
| 6   | `test_composite_l4_ceiling`                | 30 + 50 + 9             | 89.0               |
| 7   | `test_composite_preserves_float_precision` | 10.333 + 20.666 + 5.001 | 36.0               |

### 3.1 Decision Tree

```
compute_composite(dimensions):
    │
    ├── Sum all dimension.points values
    │
    ├── Assert result is float (not int)
    │
    └── Assert sum matches expected exactly
```

---

## 4. Gating Rule Tests (v0.4.1b)

### 4.1 Individual Critical Anti-Pattern Triggers (4 tests)

Each of the 4 critical anti-patterns must independently trigger the cap at 29.

| #   | Test Name                                   | Anti-Pattern | Pre-Gate Score | Expected Post-Gate |
| --- | ------------------------------------------- | ------------ | -------------- | ------------------ |
| 8   | `test_gating_ap_crit_001_ghost_file`        | AP-CRIT-001  | 85.0           | 29.0               |
| 9   | `test_gating_ap_crit_002_structure_chaos`   | AP-CRIT-002  | 85.0           | 29.0               |
| 10  | `test_gating_ap_crit_003_encoding_disaster` | AP-CRIT-003  | 85.0           | 29.0               |
| 11  | `test_gating_ap_crit_004_link_void`         | AP-CRIT-004  | 85.0           | 29.0               |

### 4.2 Gating Boundary Behavior (4 tests)

| #   | Test Name                              | Setup                         | Expected                          |
| --- | -------------------------------------- | ----------------------------- | --------------------------------- |
| 12  | `test_gating_no_critical_leaves_score` | No AP-CRIT detected, score=85 | 85.0 (unchanged)                  |
| 13  | `test_gating_score_already_below_29`   | AP-CRIT detected, score=15    | 15.0 (cap not applied — below 29) |
| 14  | `test_gating_score_exactly_29`         | AP-CRIT detected, score=29    | 29.0 (cap = current, unchanged)   |
| 15  | `test_gating_score_exactly_30`         | AP-CRIT detected, score=30    | 29.0 (capped)                     |

### 4.3 Gating Flag Tests (2 tests)

| #   | Test Name                            | Setup               | Expected                       |
| --- | ------------------------------------ | ------------------- | ------------------------------ |
| 16  | `test_gating_sets_is_gated_flag`     | AP-CRIT detected    | `structural.is_gated == True`  |
| 17  | `test_gating_no_flag_when_not_gated` | No AP-CRIT detected | `structural.is_gated == False` |

### 4.4 Multiple Critical Patterns (1 test)

| #   | Test Name                                | Setup                     | Expected                |
| --- | ---------------------------------------- | ------------------------- | ----------------------- |
| 18  | `test_gating_multiple_critical_same_cap` | AP-CRIT-001 + AP-CRIT-003 | 29.0 (non-proportional) |

### 4.5 Implementation

```python
class TestGatingRule:
    """Verify DS-QS-GATE enforcement.

    The gating rule caps the composite score at 29.0 when any critical
    anti-pattern (AP-CRIT-001–004) is detected. Gating is binary —
    one critical pattern has the same effect as four.

    Implements v0.4.2b (gating portion).
    """

    @pytest.mark.parametrize(
        "anti_pattern_id",
        [
            AntiPatternID.AP_CRIT_001,
            AntiPatternID.AP_CRIT_002,
            AntiPatternID.AP_CRIT_003,
            AntiPatternID.AP_CRIT_004,
        ],
    )
    def test_each_critical_triggers_gate(self, anti_pattern_id):
        """Each critical anti-pattern independently caps score at 29."""
        result = make_result_with_anti_pattern(anti_pattern_id)
        composite = 85.0
        gated_score = apply_gating(composite, result)
        assert gated_score == 29.0

    def test_non_critical_does_not_gate(self):
        """Non-critical anti-patterns do not trigger the cap."""
        result = make_result_with_anti_pattern(AntiPatternID.AP_CONT_001)
        composite = 85.0
        gated_score = apply_gating(composite, result)
        assert gated_score == 85.0
```

### 4.6 Decision Tree

```
apply_gating(composite, validation_result):
    │
    ├── Extract anti_pattern_ids from ValidationResult.diagnostics
    │
    ├── Check intersection with {AP-CRIT-001, -002, -003, -004}
    │     │
    │     ├── Any found AND composite > 29.0 → return 29.0
    │     ├── Any found AND composite ≤ 29.0 → return composite (unchanged)
    │     └── None found → return composite (unchanged)
    │
    └── Assert is_gated flag set on structural DimensionScore
```

---

## 5. Grade Assignment Tests (v0.4.1c)

### 5.1 Exact Threshold Tests (10 tests)

| #   | Test Name        | Composite | Expected Grade |
| --- | ---------------- | --------- | -------------- |
| 19  | `test_grade_100` | 100.0     | EXEMPLARY      |
| 20  | `test_grade_90`  | 90.0      | EXEMPLARY      |
| 21  | `test_grade_89`  | 89.0      | STRONG         |
| 22  | `test_grade_70`  | 70.0      | STRONG         |
| 23  | `test_grade_69`  | 69.0      | ADEQUATE       |
| 24  | `test_grade_50`  | 50.0      | ADEQUATE       |
| 25  | `test_grade_49`  | 49.0      | NEEDS_WORK     |
| 26  | `test_grade_30`  | 30.0      | NEEDS_WORK     |
| 27  | `test_grade_29`  | 29.0      | CRITICAL       |
| 28  | `test_grade_0`   | 0.0       | CRITICAL       |

### 5.2 Float Rounding at Boundaries (4 tests)

| #   | Test Name                              | Composite | round() | Expected Grade |
| --- | -------------------------------------- | --------- | ------- | -------------- |
| 29  | `test_grade_89_5_rounds_to_exemplary`  | 89.5      | 90      | EXEMPLARY      |
| 30  | `test_grade_89_4_stays_strong`         | 89.4      | 89      | STRONG         |
| 31  | `test_grade_69_5_rounds_to_strong`     | 69.5      | 70      | STRONG         |
| 32  | `test_grade_29_5_rounds_to_needs_work` | 29.5      | 30      | NEEDS_WORK     |

### 5.3 Banker's Rounding Verification (2 tests)

| #   | Test Name                                       | Composite | round() | Expected Grade |
| --- | ----------------------------------------------- | --------- | ------- | -------------- |
| 33  | `test_bankers_rounding_0_5_rounds_to_even_low`  | 70.5      | 70      | STRONG         |
| 34  | `test_bankers_rounding_0_5_rounds_to_even_high` | 69.5      | 70      | STRONG         |

> **Note:** Python's `round()` uses banker's rounding — 0.5 rounds to the nearest even integer. This means 70.5 → 70 (already even) and 69.5 → 70 (rounds up to even). Both produce the same result in this case.

### 5.4 Implementation

```python
class TestGradeAssignment:
    """Verify DS-QS-GRADE threshold mapping.

    The composite score (float) is rounded with `round()` (banker's
    rounding) before being passed to `QualityGrade.from_score()`.

    Implements v0.4.2b (grade assignment portion).
    """

    @pytest.mark.parametrize(
        "composite, expected_grade",
        [
            (100.0, QualityGrade.EXEMPLARY),
            (90.0, QualityGrade.EXEMPLARY),
            (89.0, QualityGrade.STRONG),
            (70.0, QualityGrade.STRONG),
            (69.0, QualityGrade.ADEQUATE),
            (50.0, QualityGrade.ADEQUATE),
            (49.0, QualityGrade.NEEDS_WORK),
            (30.0, QualityGrade.NEEDS_WORK),
            (29.0, QualityGrade.CRITICAL),
            (0.0, QualityGrade.CRITICAL),
        ],
    )
    def test_exact_threshold(self, composite: float, expected_grade: QualityGrade):
        """Grade assignment at exact thresholds."""
        grade = assign_grade(composite)
        assert grade == expected_grade

    @pytest.mark.parametrize(
        "composite, expected_grade",
        [
            (89.5, QualityGrade.EXEMPLARY),   # round(89.5) = 90
            (89.4, QualityGrade.STRONG),      # round(89.4) = 89
            (69.5, QualityGrade.STRONG),      # round(69.5) = 70
            (29.5, QualityGrade.NEEDS_WORK),  # round(29.5) = 30
        ],
    )
    def test_float_rounding(self, composite: float, expected_grade: QualityGrade):
        """Float rounding at grade boundaries (banker's rounding)."""
        grade = assign_grade(composite)
        assert grade == expected_grade
```

---

## 6. Detail Enrichment Tests (v0.4.1d)

| #   | Test Name                                     | Setup                         | Expected                       |
| --- | --------------------------------------------- | ----------------------------- | ------------------------------ |
| 35  | `test_enrichment_adds_name_from_registry`     | Detail without `name`         | `name` populated from registry |
| 36  | `test_enrichment_adds_scoring_mode`           | Detail without `scoring_mode` | `scoring_mode` = "BINARY" etc. |
| 37  | `test_enrichment_adds_dimension`              | Detail without `dimension`    | `dimension` from parent score  |
| 38  | `test_enrichment_calculates_impact_potential` | weight=5, points=3.75         | `impact_potential` = 1.25      |
| 39  | `test_enrichment_zero_impact`                 | weight=5, points=5.0          | `impact_potential` = 0.0       |
| 40  | `test_enrichment_preserves_existing_keys`     | Detail already has `name`     | Existing `name` preserved      |
| 41  | `test_enrichment_returns_model_copy`          | Any input                     | Original unchanged             |
| 42  | `test_enrichment_handles_empty_details`       | Empty details list            | Returns empty list             |

---

## 7. Orchestrator Tests (score_file)

End-to-end tests for the `score_file()` function that orchestrates the full pipeline.

| #   | Test Name                                    | Setup                  | Expected                             |
| --- | -------------------------------------------- | ---------------------- | ------------------------------------ |
| 43  | `test_score_file_returns_quality_score`      | Clean ValidationResult | Returns QualityScore instance        |
| 44  | `test_score_file_all_dimensions_present`     | Any result             | 3 dimensions in output               |
| 45  | `test_score_file_source_filename_propagated` | filename="test.txt"    | output.source_filename == "test.txt" |
| 46  | `test_score_file_scored_at_populated`        | Any result             | output.scored_at is recent           |

---

## 8. Edge Cases

| Case                            | Behavior                   | Test Coverage                           |
| ------------------------------- | -------------------------- | --------------------------------------- |
| All dimensions score max        | Composite = 100, EXEMPLARY | `test_composite_perfect`                |
| All dimensions score 0          | Composite = 0, CRITICAL    | `test_composite_zero`                   |
| Gated + below 29                | Score unchanged            | `test_gating_score_already_below_29`    |
| Float at exact 0.5 boundary     | Banker's rounding applies  | `test_bankers_rounding_*`               |
| No details to enrich            | Empty enriched list        | `test_enrichment_handles_empty_details` |
| Composite = 29.0001 with gating | Capped at 29.0             | Covered by parametrized tests           |

---

## 9. Deliverables

| File                              | Description              | Test Count |
| --------------------------------- | ------------------------ | ---------- |
| `tests/scoring/test_composite.py` | Composite pipeline tests | ~46        |

---

## 10. Changelog Requirements

```markdown
## [0.4.2b] - YYYY-MM-DD

**Composite Pipeline Unit Tests — Verifies composite calculation, gating, grading, and enrichment.**

### Added

#### Composite Tests (`tests/scoring/test_composite.py`)

- 7 composite calculation tests (sums, precision, L4 ceiling)
- 11 gating rule tests (4 AP-CRIT triggers, boundary, flag, multi-pattern)
- 16 grade assignment tests (10 threshold, 4 float rounding, 2 banker's rounding)
- 8 detail enrichment tests (registry metadata, impact_potential, immutability)
- 4 orchestrator tests (score_file() end-to-end)

### Notes

- **Coverage:** Targets ≥90% on `scoring.composite`.
- **Fixtures:** Uses mock `DimensionScore` instances (no dimension scorer execution).
- **Key verification:** Banker's rounding at grade boundaries (89.5 → EXEMPLARY).
```
