# v0.4.2d — Boundary & Regression Tests

> **Version:** v0.4.2d
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.2-calibration-testing.md](RR-SPEC-v0.4.2-calibration-testing.md)
> **Depends On:** v0.4.1 (complete scoring pipeline), v0.4.2c (calibration scoring)

---

## 1. Purpose

v0.4.2d defines **targeted edge-case tests** and the **JSON regression baseline** system. It verifies extreme scoring scenarios that calibration specimens do not cover (perfect score, zero score, exact boundary behavior) and records stable snapshots for CI enforcement.

### 1.1 User Stories

> As a developer, I want edge-case tests for extreme scoring scenarios (perfect file, empty file, gating at ≤29 boundary) so that boundary conditions don't silently regress.

> As a CI pipeline, I want JSON fixture baselines for all 6 calibration specimens so that any score drift ≥4 points fails the build automatically.

---

## 2. Boundary Tests

### 2.1 Extreme Scenarios (8 tests)

| #   | Test Name                      | Setup                                                          | Expected                               |
| --- | ------------------------------ | -------------------------------------------------------------- | -------------------------------------- |
| 1   | `test_perfect_score`           | Mock ValidationResult with zero diagnostics, all levels passed | ~89 at v0.4.x (L4 ceiling, not 100)    |
| 2   | `test_perfect_score_grade`     | Same as above                                                  | STRONG (L4 ceiling prevents EXEMPLARY) |
| 3   | `test_zero_score`              | Mock with all possible diagnostics triggered                   | Near-0 points, CRITICAL                |
| 4   | `test_zero_score_grade`        | Same as above                                                  | CRITICAL                               |
| 5   | `test_empty_validation_result` | Empty diagnostics[], all levels passed                         | High score (binary criteria pass)      |
| 6   | `test_l0_only_failure`         | L0 failed, no higher levels evaluated                          | Near-0 points, CRITICAL                |
| 7   | `test_single_dimension_zero`   | Structural=0, Content=50, APD=9                                | Composite=59, ADEQUATE                 |
| 8   | `test_all_graduated_halfway`   | Every graduated criterion at 50% compliance                    | ~50 points, ADEQUATE                   |

### 2.2 Implementation

```python
"""Boundary & Regression Tests (v0.4.2d).

Tests extreme scoring scenarios not covered by calibration specimens.
Records JSON baselines for CI regression enforcement.

Implements v0.4.2d.
"""

import json
import pytest
from pathlib import Path

from docstratum.scoring.composite import score_file
from docstratum.schema.quality import QualityGrade, QualityDimension


class TestBoundaryScenarios:
    """Edge-case scoring scenarios.

    These tests use synthetic ValidationResults to exercise extreme
    conditions that no real-world calibration specimen covers.

    Implements v0.4.2d (boundary portion).
    """

    def test_perfect_score_with_l4_ceiling(
        self, clean_validation_result
    ):
        """A perfect file still hits the L4 ceiling at v0.4.x.

        All binary criteria pass, but APD-001–003 and APD-008 score 0
        because L4 checks are inactive. Maximum composite ≈ 89.
        """
        qs = score_file(clean_validation_result)

        # Should be near-max but not 100 (L4 ceiling)
        assert 85.0 <= qs.total_score <= 91.0
        assert qs.grade == QualityGrade.STRONG

        # Structural and Content should be maxed
        assert qs.dimensions[QualityDimension.STRUCTURAL].points == 30.0
        assert qs.dimensions[QualityDimension.CONTENT].points == 50.0

        # APD should be at L4 ceiling (≤9)
        apd = qs.dimensions[QualityDimension.ANTI_PATTERN]
        assert apd.points <= 9.0

    def test_zero_score(self, all_failures_validation_result):
        """All criteria fail → near-0 score, CRITICAL grade."""
        qs = score_file(all_failures_validation_result)

        assert qs.total_score < 5.0
        assert qs.grade == QualityGrade.CRITICAL

    def test_l0_failure_scores_near_zero(self, l0_failure_result):
        """L0 failure gates all higher levels → near-zero score."""
        qs = score_file(l0_failure_result)

        assert qs.total_score < 10.0
        assert qs.grade == QualityGrade.CRITICAL

        # All dimensions should be near-zero
        for dim in qs.dimensions.values():
            assert dim.points <= 5.0

    def test_single_dimension_failure(self):
        """One dimension scores 0, others score max."""
        # Construct a result where structural checks fail but
        # content and APD checks pass.
        # (Specific setup depends on diagnostic construction)
        ...
```

### 2.3 Gating Boundary Tests (4 tests)

| #   | Test Name                        | Pre-Gate Score | Gated? | Expected Post-Gate |
| --- | -------------------------------- | -------------- | ------ | ------------------ |
| 9   | `test_gating_at_exactly_30`      | 30.0           | Yes    | 29.0               |
| 10  | `test_gating_at_exactly_29`      | 29.0           | Yes    | 29.0 (no change)   |
| 11  | `test_gating_from_91`            | 91.0           | Yes    | 29.0               |
| 12  | `test_gating_preserves_below_29` | 15.0           | Yes    | 15.0 (no change)   |

### 2.4 Decision Tree

```
For each boundary scenario:
    │
    ├── Construct synthetic ValidationResult
    │     with precisely controlled diagnostics
    │
    ├── Run score_file(result) → QualityScore
    │
    ├── Assert total_score matches expected range
    │
    ├── Assert grade matches expected
    │
    └── Assert per-dimension scores are plausible
```

---

## 3. Float Rounding at All Grade Boundaries (4 tests)

These complement v0.4.2b's rounding tests by using the full pipeline rather than `assign_grade()` alone.

| #   | Test Name                               | Composite Target | Expected Grade |
| --- | --------------------------------------- | ---------------- | -------------- |
| 13  | `test_pipeline_rounding_at_90_boundary` | ~89.5            | EXEMPLARY      |
| 14  | `test_pipeline_rounding_at_70_boundary` | ~69.5            | STRONG         |
| 15  | `test_pipeline_rounding_at_50_boundary` | ~49.5            | ADEQUATE       |
| 16  | `test_pipeline_rounding_at_30_boundary` | ~29.5            | NEEDS_WORK     |

> **Note:** These tests construct ValidationResults that produce specific composite scores at boundary points. They are integration-level complements to the unit-level rounding tests in v0.4.2b.

---

## 4. JSON Regression Baselines

### 4.1 Purpose

Record the **exact `QualityScore` output** for each calibration specimen as a JSON fixture. Future scoring engine changes must produce results within ±3 of these baselines or the CI build fails.

### 4.2 Baseline Schema

```json
{
  "specimen_id": "DS-CS-001",
  "specimen_file": "ds-cs-001-svelte.txt",
  "captured_at": "2026-02-10T23:42:00Z",
  "scorer_version": "0.4.2d",
  "total_score": 81.25,
  "grade": "STRONG",
  "tolerance": 3,
  "dimensions": {
    "structural": {
      "points": 29.5,
      "max_points": 30.0,
      "checks_passed": 8,
      "checks_failed": 1,
      "checks_total": 9,
      "is_gated": false
    },
    "content": {
      "points": 45.75,
      "max_points": 50.0,
      "checks_passed": 11,
      "checks_failed": 2,
      "checks_total": 13,
      "is_gated": false
    },
    "anti_pattern": {
      "points": 6.0,
      "max_points": 20.0,
      "checks_passed": 3,
      "checks_failed": 5,
      "checks_total": 8,
      "is_gated": false
    }
  },
  "detail_count": 30
}
```

### 4.3 Baseline Storage

```
tests/scoring/fixtures/expected_scores/
├── ds-cs-001-svelte.json
├── ds-cs-002-pydantic.json
├── ds-cs-003-vercel-ai-sdk.json
├── ds-cs-004-shadcn-ui.json
├── ds-cs-005-cursor.json
└── ds-cs-006-nvidia.json
```

### 4.4 Regression Test Implementation

```python
BASELINE_DIR = Path(__file__).parent / "fixtures" / "expected_scores"


class TestRegressionBaselines:
    """Compare current scoring output against recorded JSON baselines.

    Baselines are recorded once per scoring engine version and committed
    to the repository. Score drift ≥4 points (outside ±3 tolerance)
    fails the build.

    Implements v0.4.2d (regression portion).
    """

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
    def test_regression_total_score(self, specimen_file: str):
        """Current total score within ±tolerance of recorded baseline."""
        baseline_path = BASELINE_DIR / specimen_file.replace(".txt", ".json")
        with open(baseline_path) as f:
            baseline = json.load(f)

        path = CALIBRATION_DIR / specimen_file
        vr = validate_file(path)
        qs = score_file(vr)

        tolerance = baseline["tolerance"]
        expected = baseline["total_score"]
        assert abs(qs.total_score - expected) <= tolerance, (
            f"{specimen_file}: baseline={expected}, current={qs.total_score:.1f}, "
            f"drift={abs(qs.total_score - expected):.1f} (tolerance={tolerance})"
        )

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
    def test_regression_grade(self, specimen_file: str):
        """Current grade matches recorded baseline."""
        baseline_path = BASELINE_DIR / specimen_file.replace(".txt", ".json")
        with open(baseline_path) as f:
            baseline = json.load(f)

        path = CALIBRATION_DIR / specimen_file
        vr = validate_file(path)
        qs = score_file(vr)

        assert qs.grade.value == baseline["grade"], (
            f"{specimen_file}: expected {baseline['grade']}, "
            f"got {qs.grade.value}"
        )

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
    def test_regression_detail_count(self, specimen_file: str):
        """Detail count matches baseline (always 30)."""
        baseline_path = BASELINE_DIR / specimen_file.replace(".txt", ".json")
        with open(baseline_path) as f:
            baseline = json.load(f)

        path = CALIBRATION_DIR / specimen_file
        vr = validate_file(path)
        qs = score_file(vr)

        total_details = sum(
            len(dim.details) for dim in qs.dimensions.values()
        )
        assert total_details == baseline["detail_count"]
```

### 4.5 Baseline Update Mechanism

Baselines are updated when the scoring engine intentionally changes (e.g., new criteria, adjusted weights). The update is a manual process:

```python
# Run once to generate/update baselines:
# pytest tests/scoring/test_boundary_regression.py --update-baselines

@pytest.fixture
def update_baselines(request):
    """conftest fixture to enable baseline updates."""
    return request.config.getoption("--update-baselines", default=False)


def pytest_addoption(parser):
    """Add --update-baselines CLI option."""
    parser.addoption(
        "--update-baselines",
        action="store_true",
        default=False,
        help="Update JSON regression baselines with current scores.",
    )
```

When `--update-baselines` is passed:

```python
    def _update_baseline(self, specimen_file: str, qs: QualityScore):
        """Write current QualityScore as the new baseline."""
        baseline_path = BASELINE_DIR / specimen_file.replace(".txt", ".json")
        baseline = {
            "specimen_id": f"DS-CS-{specimen_file.split('-')[2]}",
            "specimen_file": specimen_file,
            "captured_at": datetime.utcnow().isoformat() + "Z",
            "scorer_version": "0.4.2d",
            "total_score": round(qs.total_score, 2),
            "grade": qs.grade.value,
            "tolerance": 3,
            "dimensions": {
                dim.value: {
                    "points": round(score.points, 2),
                    "max_points": score.max_points,
                    "checks_passed": score.checks_passed,
                    "checks_failed": score.checks_failed,
                    "checks_total": score.checks_total,
                    "is_gated": score.is_gated,
                }
                for dim, score in qs.dimensions.items()
            },
            "detail_count": sum(
                len(dim.details) for dim in qs.dimensions.values()
            ),
        }
        with open(baseline_path, "w") as f:
            json.dump(baseline, f, indent=2)
```

### 4.6 Decision Tree

```
--update-baselines mode:
    │
    ├── For each specimen:
    │     ├── Run full pipeline → QualityScore
    │     ├── Serialize to JSON with metadata
    │     └── Write to fixtures/expected_scores/
    │
    └── Commit updated baselines to repository

Normal test mode:
    │
    ├── For each specimen:
    │     ├── Load JSON baseline
    │     ├── Run full pipeline → QualityScore
    │     ├── Compare total_score within ±tolerance
    │     ├── Compare grade matches
    │     └── Compare detail_count matches
    │
    └── Fail if any drift exceeds tolerance
```

---

## 5. CI Integration

### 5.1 pytest Configuration

```ini
# pyproject.toml

[tool.pytest.ini_options]
markers = [
    "scoring: marks scoring engine tests",
    "calibration: marks calibration specimen tests",
    "regression: marks regression baseline tests",
]
```

### 5.2 CI Command

```bash
# Full scoring test suite with coverage enforcement
pytest tests/scoring/ \
    --cov=docstratum.scoring \
    --cov-fail-under=90 \
    -v \
    --tb=short
```

### 5.3 Marker Usage

```bash
# Run only boundary tests
pytest tests/scoring/ -m "scoring and not calibration"

# Run only calibration tests
pytest tests/scoring/ -m calibration

# Run only regression baseline tests
pytest tests/scoring/ -m regression
```

---

## 6. Edge Cases

| Case                                          | Behavior                               | Test Coverage                  |
| --------------------------------------------- | -------------------------------------- | ------------------------------ |
| Baseline file missing                         | Test skipped with warning (not error)  | `skipIf` guard                 |
| Score drifts by exactly ±3 (within tolerance) | Test passes                            | Parametrized tolerance         |
| Score drifts by ±4 (outside tolerance)        | Test fails with diagnostic message     | Parametrized tolerance         |
| New criterion added (31 total)                | detail_count regression test fails     | `test_regression_detail_count` |
| All L4 checks become active (v0.9.0)          | Baselines must be regenerated          | `--update-baselines`           |
| Parallel test execution                       | No shared state — tests are idempotent | By design                      |
| Float precision in JSON serialization         | `round(score, 2)` before writing       | Baseline schema                |

---

## 7. Test Plan Summary

| Category                  | Test Count | File                          |
| ------------------------- | ---------- | ----------------------------- |
| Boundary scenarios        | 8          | `test_boundary_regression.py` |
| Gating boundary           | 4          | `test_boundary_regression.py` |
| Float rounding (pipeline) | 4          | `test_boundary_regression.py` |
| Regression: total_score   | 6          | `test_boundary_regression.py` |
| Regression: grade         | 6          | `test_boundary_regression.py` |
| Regression: detail_count  | 6          | `test_boundary_regression.py` |
| **Total v0.4.2d**         | **~34**    |                               |

---

## 8. Deliverables

| File                                            | Description                           |
| ----------------------------------------------- | ------------------------------------- |
| `tests/scoring/test_boundary_regression.py`     | Boundary & regression tests           |
| `tests/scoring/fixtures/expected_scores/*.json` | 6 JSON regression baseline files      |
| `tests/scoring/conftest.py` (additions)         | `--update-baselines` option, fixtures |

---

## 9. Changelog Requirements

```markdown
## [0.4.2d] - YYYY-MM-DD

**Boundary & Regression Tests — Edge cases and CI-enforced JSON baselines.**

### Added

#### Boundary Tests (`tests/scoring/test_boundary_regression.py`)

- 8 extreme scenario tests (perfect score, zero score, L0 failure, single-dimension failure)
- 4 gating boundary tests (exact threshold at 29/30)
- 4 pipeline-level float rounding tests at grade boundaries

#### Regression Baselines (`tests/scoring/fixtures/expected_scores/`)

- 6 JSON baseline files (one per calibration specimen)
- `--update-baselines` pytest option for baseline regeneration
- 18 regression comparison tests (score ±3, grade match, detail count)

#### CI Integration

- `pytest --cov=docstratum.scoring --cov-fail-under=90` enforced
- `scoring`, `calibration`, `regression` pytest markers registered
- Clear diagnostic messages on drift detection

### Notes

- **L4 ceiling:** Perfect score is ~89 at v0.4.x (not 100). Baselines reflect this.
- **Baseline updates:** Required when scoring logic intentionally changes.
  Run `pytest tests/scoring/ --update-baselines` to regenerate.
```
