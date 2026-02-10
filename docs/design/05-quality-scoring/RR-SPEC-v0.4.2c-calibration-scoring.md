# v0.4.2c — Calibration Specimen Scoring

> **Version:** v0.4.2c
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.2-calibration-testing.md](RR-SPEC-v0.4.2-calibration-testing.md)
> **Depends On:** v0.4.1 (complete scoring pipeline), v0.3.5d (calibration specimens), v0.3.x (validation pipeline)

---

## 1. Purpose

v0.4.2c runs the **complete end-to-end pipeline** (`validate_file() → score_file()`) against the 6 gold standard calibration specimens and verifies that scores fall within expected ranges. This is the integration test that proves the scoring engine produces correct assessments against real-world `llms.txt` files.

### 1.1 User Story

> As a QA engineer, I want automated tests that score 6 real-world files of known quality and verify the results match expected ranges, so that I can detect when changes to the scoring or validation engine produce incorrect assessments.

### 1.2 Relationship to v0.3.5d

v0.3.5d tests the **validation pipeline** output against calibration specimens (level_achieved, diagnostic counts). v0.4.2c tests the **scoring pipeline** output (composite score, grade, per-dimension breakdown). Same specimens, different pipeline stage.

| Concern         | v0.3.5d                | v0.4.2c                          |
| --------------- | ---------------------- | -------------------------------- |
| Pipeline tested | `validate_file()`      | `validate_file() → score_file()` |
| Output verified | `ValidationResult`     | `QualityScore`                   |
| Key assertions  | level_achieved, errors | total_score, grade, dimensions   |
| Tolerances      | Exact level match      | ±3 score tolerance               |

---

## 2. Adjusted Expected Scores

At v0.4.x, 4 L4-dependent APD criteria score 0, reducing maximum achievable scores. The expected values below account for this ceiling.

### 2.1 v0.4.x Expected Score Table

| Specimen      | ID        | Ref Score | L4 Adj | v0.4.x Score | v0.4.x Grade | Tolerance |
| ------------- | --------- | --------- | ------ | ------------ | ------------ | --------- |
| Svelte        | DS-CS-001 | 92        | −11    | 81           | STRONG       | ±3        |
| Pydantic      | DS-CS-002 | 90        | −11    | 79           | STRONG       | ±3        |
| Vercel AI SDK | DS-CS-003 | 90        | −11    | 79           | STRONG       | ±3        |
| Shadcn UI     | DS-CS-004 | 89        | −11    | 78           | STRONG       | ±3        |
| Cursor        | DS-CS-005 | 42        | −6     | 36           | NEEDS_WORK   | ±3        |
| NVIDIA        | DS-CS-006 | 24        | −2     | 22           | CRITICAL     | ±3        |

### 2.2 Per-Dimension Expected Ranges

Beyond total score, each dimension should fall within a plausible range.

| Specimen      | Structural (0–30) | Content (0–50) | Anti-Pattern (0–20) |
| ------------- | ----------------- | -------------- | ------------------- |
| Svelte        | 28–30             | 44–50          | 7–9 (L4 ceiling)    |
| Pydantic      | 27–30             | 42–48          | 7–9 (L4 ceiling)    |
| Vercel AI SDK | 27–30             | 42–48          | 7–9 (L4 ceiling)    |
| Shadcn UI     | 26–30             | 40–46          | 7–9 (L4 ceiling)    |
| Cursor        | 15–22             | 15–22          | 3–7                 |
| NVIDIA        | 5–12              | 8–15           | 0–5                 |

---

## 3. Implementation

### 3.1 Test File

```python
"""Calibration Specimen Scoring Tests (v0.4.2c).

Runs the complete validation + scoring pipeline on 6 gold standard
specimens and verifies scores fall within L4-adjusted expected ranges.

These are integration tests requiring real fixture files.

Implements v0.4.2c.
"""

import pytest
from pathlib import Path

from docstratum.validation import validate_file
from docstratum.scoring.composite import score_file
from docstratum.schema.quality import QualityGrade, QualityDimension

CALIBRATION_DIR = Path(__file__).parent.parent / "fixtures" / "calibration"


class TestCalibrationScoring:
    """Score 6 real-world specimens and verify against expected ranges.

    Expected scores are L4-adjusted (APD-001–003, APD-008 score 0).
    Tolerance of ±3 points accounts for minor scoring variations.

    Implements v0.4.2c.
    """

    @pytest.mark.parametrize(
        "specimen_file, expected_score, tolerance",
        [
            ("ds-cs-001-svelte.txt", 81, 3),
            ("ds-cs-002-pydantic.txt", 79, 3),
            ("ds-cs-003-vercel-ai-sdk.txt", 79, 3),
            ("ds-cs-004-shadcn-ui.txt", 78, 3),
            ("ds-cs-005-cursor.txt", 36, 3),
            ("ds-cs-006-nvidia.txt", 22, 3),
        ],
    )
    def test_specimen_total_score(
        self,
        specimen_file: str,
        expected_score: int,
        tolerance: int,
    ):
        """Total score falls within ±tolerance of expected."""
        path = CALIBRATION_DIR / specimen_file
        validation_result = validate_file(path)
        quality_score = score_file(validation_result)

        assert abs(quality_score.total_score - expected_score) <= tolerance, (
            f"{specimen_file}: expected {expected_score}±{tolerance}, "
            f"got {quality_score.total_score:.1f}"
        )

    @pytest.mark.parametrize(
        "specimen_file, expected_grade",
        [
            ("ds-cs-001-svelte.txt", QualityGrade.STRONG),
            ("ds-cs-002-pydantic.txt", QualityGrade.STRONG),
            ("ds-cs-003-vercel-ai-sdk.txt", QualityGrade.STRONG),
            ("ds-cs-004-shadcn-ui.txt", QualityGrade.STRONG),
            ("ds-cs-005-cursor.txt", QualityGrade.NEEDS_WORK),
            ("ds-cs-006-nvidia.txt", QualityGrade.CRITICAL),
        ],
    )
    def test_specimen_grade(
        self,
        specimen_file: str,
        expected_grade: QualityGrade,
    ):
        """Grade matches expected at v0.4.x (L4-adjusted)."""
        path = CALIBRATION_DIR / specimen_file
        validation_result = validate_file(path)
        quality_score = score_file(validation_result)

        assert quality_score.grade == expected_grade, (
            f"{specimen_file}: expected {expected_grade.name}, "
            f"got {quality_score.grade.name} (score={quality_score.total_score:.1f})"
        )
```

### 3.2 Quality Ordering Test

```python
    def test_quality_ordering(self):
        """Specimens maintain relative quality ordering by total score.

        Svelte ≥ Pydantic ≥ Vercel ≥ Shadcn > Cursor > NVIDIA
        """
        specimens = [
            "ds-cs-001-svelte.txt",
            "ds-cs-002-pydantic.txt",
            "ds-cs-003-vercel-ai-sdk.txt",
            "ds-cs-004-shadcn-ui.txt",
            "ds-cs-005-cursor.txt",
            "ds-cs-006-nvidia.txt",
        ]
        scores = []
        for s in specimens:
            path = CALIBRATION_DIR / s
            vr = validate_file(path)
            qs = score_file(vr)
            scores.append(qs.total_score)

        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], (
                f"{specimens[i]} ({scores[i]:.1f}) should score >= "
                f"{specimens[i+1]} ({scores[i+1]:.1f})"
            )
```

### 3.3 Per-Dimension Validation

```python
    @pytest.mark.parametrize(
        "specimen_file, dimension, expected_min, expected_max",
        [
            # Svelte: near-max structural/content, L4-ceiling on APD
            ("ds-cs-001-svelte.txt", QualityDimension.STRUCTURAL, 28, 30),
            ("ds-cs-001-svelte.txt", QualityDimension.CONTENT, 44, 50),
            ("ds-cs-001-svelte.txt", QualityDimension.ANTI_PATTERN, 7, 9),
            # NVIDIA: low across all dimensions
            ("ds-cs-006-nvidia.txt", QualityDimension.STRUCTURAL, 5, 12),
            ("ds-cs-006-nvidia.txt", QualityDimension.CONTENT, 8, 15),
            ("ds-cs-006-nvidia.txt", QualityDimension.ANTI_PATTERN, 0, 5),
        ],
    )
    def test_dimension_plausible_range(
        self,
        specimen_file: str,
        dimension: QualityDimension,
        expected_min: int,
        expected_max: int,
    ):
        """Per-dimension score falls within plausible range."""
        path = CALIBRATION_DIR / specimen_file
        vr = validate_file(path)
        qs = score_file(vr)

        dim_score = qs.dimensions[dimension]
        assert expected_min <= dim_score.points <= expected_max, (
            f"{specimen_file} {dimension.value}: expected "
            f"{expected_min}–{expected_max}, got {dim_score.points:.1f}"
        )
```

### 3.4 Gating Assertions

```python
class TestCalibrationGating:
    """Verify that gating is correctly applied to calibration specimens.

    NVIDIA should trigger gating (critical anti-patterns detected).
    Cursor should NOT trigger gating (problems, but not critical).

    Implements v0.4.2c (gating validation).
    """

    def test_nvidia_triggers_gating(self):
        """NVIDIA specimen has critical anti-patterns → score capped at 29."""
        path = CALIBRATION_DIR / "ds-cs-006-nvidia.txt"
        vr = validate_file(path)
        qs = score_file(vr)

        structural = qs.dimensions[QualityDimension.STRUCTURAL]
        assert structural.is_gated is True
        assert qs.total_score <= 29.0

    def test_cursor_does_not_trigger_gating(self):
        """Cursor has problems but no critical anti-patterns → no gating."""
        path = CALIBRATION_DIR / "ds-cs-005-cursor.txt"
        vr = validate_file(path)
        qs = score_file(vr)

        structural = qs.dimensions[QualityDimension.STRUCTURAL]
        assert structural.is_gated is False
        assert qs.total_score > 29.0

    @pytest.mark.parametrize(
        "specimen_file",
        [
            "ds-cs-001-svelte.txt",
            "ds-cs-002-pydantic.txt",
            "ds-cs-003-vercel-ai-sdk.txt",
            "ds-cs-004-shadcn-ui.txt",
        ],
    )
    def test_exemplary_specimens_not_gated(self, specimen_file: str):
        """High-quality specimens should never trigger gating."""
        path = CALIBRATION_DIR / specimen_file
        vr = validate_file(path)
        qs = score_file(vr)

        structural = qs.dimensions[QualityDimension.STRUCTURAL]
        assert structural.is_gated is False
```

---

## 4. Decision Tree

```
For each calibration specimen:
    │
    ├── Load from tests/fixtures/calibration/
    │
    ├── Run validate_file(specimen) → ValidationResult
    │
    ├── Run score_file(validation_result) → QualityScore
    │
    ├── Assert total_score within ±3 of L4-adjusted expected
    │     │
    │     ├── Pass → Specimen correctly scored
    │     │
    │     └── Fail → Score drift detected
    │            ├── Check per-dimension scores for root cause
    │            └── Investigate which criteria changed
    │
    ├── Assert grade matches expected (at v0.4.x, NOT ref grade)
    │
    ├── Assert per-dimension scores within plausible ranges
    │
    └── Assert gating behavior (NVIDIA gated, others not)
```

---

## 5. Detail Completeness Assertion

Every calibration specimen's `QualityScore` should have exactly 30 detail entries across all 3 dimensions:

```python
    @pytest.mark.parametrize(
        "specimen_file",
        [
            "ds-cs-001-svelte.txt",
            "ds-cs-002-pydantic.txt",
            "ds-cs-003-vercel-ai-sdk.txt",
            "ds-cs-004-shadcn-ui.txt",
            "ds-cs-005-cursor.txt",
            "ds-cs-006-nvidia.txt",
        ],
    )
    def test_specimen_has_30_detail_entries(self, specimen_file: str):
        """Every specimen should show all 30 criteria in details."""
        path = CALIBRATION_DIR / specimen_file
        vr = validate_file(path)
        qs = score_file(vr)

        total_details = sum(
            len(dim.details) for dim in qs.dimensions.values()
        )
        assert total_details == 30, (
            f"{specimen_file}: expected 30 detail entries, got {total_details}"
        )
```

---

## 6. Edge Cases

| Case                                              | Behavior                           | Test Coverage                |
| ------------------------------------------------- | ---------------------------------- | ---------------------------- |
| Specimen updated upstream                         | Tests compare against snapshot     | Specimens never auto-updated |
| Score drifts by ±4 (outside tolerance)            | Test fails; investigate root cause | Parametrized score test      |
| Grade changes (e.g., Pydantic drops below STRONG) | Test fails; critical regression    | Parametrized grade test      |
| NVIDIA score drops below 0                        | Should not happen                  | Assertions guarantee ≥0      |
| Specimen file missing                             | pytest collection error            | Clear error message          |

---

## 7. Test Plan (18 tests)

| #    | Test Name                                         | Assertion                               |
| ---- | ------------------------------------------------- | --------------------------------------- |
| 1–6  | `test_specimen_total_score[spec]` × 6             | Score within ±3 of L4-adjusted expected |
| 7–12 | `test_specimen_grade[spec]` × 6                   | Grade matches v0.4.x expected           |
| 13   | `test_quality_ordering`                           | Non-increasing score sequence           |
| 14   | `test_nvidia_triggers_gating`                     | `is_gated=True`, score ≤ 29             |
| 15   | `test_cursor_does_not_trigger_gating`             | `is_gated=False`, score > 29            |
| 16   | `test_dimension_plausible_range` (6 parametrized) | Per-dimension within min–max (sampled)  |
| 17   | `test_exemplary_specimens_not_gated` × 4          | Top-tier files not gated                |
| 18   | `test_specimen_has_30_detail_entries` × 6         | 30 detail entries across all dimensions |

> **Effective parametrized test count:** ~38 individual test invocations (6 + 6 + 1 + 1 + 1 + 6 + 4 + 6 + additional dimension range tests). Counted as **~18 logical tests** with parametrization expanding to ~38 at runtime.

---

## 8. Deliverables

| File                                        | Description                           |
| ------------------------------------------- | ------------------------------------- |
| `tests/scoring/test_calibration_scoring.py` | Calibration scoring integration tests |

---

## 9. Changelog Requirements

```markdown
## [0.4.2c] - YYYY-MM-DD

**Calibration Specimen Scoring — End-to-end scoring validation against 6 real-world files.**

### Added

#### Calibration Scoring Tests (`tests/scoring/test_calibration_scoring.py`)

- 6 specimen total score tests (±3 tolerance, L4-adjusted)
- 6 specimen grade tests (STRONG/NEEDS_WORK/CRITICAL at v0.4.x)
- Quality ordering test (Svelte ≥ Pydantic ≥ Vercel ≥ Shadcn > Cursor > NVIDIA)
- Per-dimension plausible range tests (sampled: Svelte structural, NVIDIA all)
- Gating assertion tests (NVIDIA gated, Cursor + top-4 not gated)
- Detail completeness test (30 entries per specimen)

### Notes

- **L4 ceiling:** Top scores reduced ~11 pts from reference values due to deferred L4 checks.
- **Tolerance:** ±3 points accommodates minor scoring variations.
- **Regression protection:** These tests form the baseline for CI regression detection.
```
