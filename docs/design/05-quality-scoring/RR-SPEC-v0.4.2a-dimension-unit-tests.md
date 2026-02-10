# v0.4.2a — Dimension Scorer Unit Tests

> **Version:** v0.4.2a
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.2-calibration-testing.md](RR-SPEC-v0.4.2-calibration-testing.md)
> **Depends On:** v0.4.0a (registry), v0.4.0b (structural scorer), v0.4.0c (content scorer), v0.4.0d (anti-pattern scorer)

---

## 1. Purpose

v0.4.2a defines the **per-criterion unit test suite** for the three dimension scorers. Each of the 30 criteria receives at least one dedicated test verifying correct point calculation, graduated compliance fractions, and boundary conditions.

### 1.1 User Story

> As a developer, I want every scoring criterion individually tested — for pass, fail, and partial compliance — so that I can diagnose scoring bugs at the criterion level rather than debugging the composite pipeline.

### 1.2 Coverage Target

```
pytest tests/scoring/test_structural.py tests/scoring/test_content.py tests/scoring/test_anti_pattern.py \
    --cov=docstratum.scoring.structural \
    --cov=docstratum.scoring.content \
    --cov=docstratum.scoring.anti_pattern \
    --cov-fail-under=90
```

---

## 2. Structural Scorer Tests (`test_structural.py`)

### 2.1 Fixture Factory

```python
"""Tests for the Structural Dimension Scorer (v0.4.0b).

Each test constructs a synthetic ValidationResult with specific
diagnostics and verifies the DimensionScore output.

Implements v0.4.2a (structural portion).
"""

import pytest
from docstratum.scoring.structural import score_structural
from docstratum.scoring.registry import CRITERIA_REGISTRY
from docstratum.schema.validation import (
    ValidationResult, ValidationDiagnostic, ValidationLevel,
)
from docstratum.schema.diagnostics import DiagnosticCode, Severity
from docstratum.schema.quality import QualityDimension


def make_structural_result(
    diagnostics: list[ValidationDiagnostic] | None = None,
    level_achieved: ValidationLevel = ValidationLevel.L3_BEST_PRACTICES,
) -> ValidationResult:
    """Create a ValidationResult tailored for structural scoring tests."""
    return ValidationResult(
        source_filename="test.txt",
        diagnostics=diagnostics or [],
        level_achieved=level_achieved,
        levels_passed={
            ValidationLevel.L0_PARSEABLE: True,
            ValidationLevel.L1_STRUCTURAL: True,
            ValidationLevel.L2_CONTENT: True,
            ValidationLevel.L3_BEST_PRACTICES: True,
        },
    )
```

### 2.2 Per-Criterion Tests (9 criteria × ~2 tests = ~18 tests)

| #   | Test Name                                | Criterion     | Setup                          | Expected                          |
| --- | ---------------------------------------- | ------------- | ------------------------------ | --------------------------------- |
| 1   | `test_str001_h1_present_pass`            | DS-VC-STR-001 | No E001 diagnostic             | 5.0 points, passed=True           |
| 2   | `test_str001_h1_missing_fail`            | DS-VC-STR-001 | E001 diagnostic present        | 0.0 points, passed=False          |
| 3   | `test_str002_blockquote_present_pass`    | DS-VC-STR-002 | No E004 diagnostic             | 4.0 points, passed=True           |
| 4   | `test_str002_blockquote_missing_fail`    | DS-VC-STR-002 | E004 diagnostic present        | 0.0 points, passed=False          |
| 5   | `test_str003_sections_graduated_full`    | DS-VC-STR-003 | No W001 diagnostics            | 4.0 points, compliance_rate=1.0   |
| 6   | `test_str003_sections_graduated_partial` | DS-VC-STR-003 | 3 of 12 sections fail W001     | ~3.0 points, compliance_rate=0.75 |
| 7   | `test_str003_sections_graduated_zero`    | DS-VC-STR-003 | All sections fail W001         | 0.0 points, compliance_rate=0.0   |
| 8   | `test_str004_canonical_naming_graduated` | DS-VC-STR-004 | 50% non-canonical sections     | ~1.5 points, compliance_rate=0.5  |
| 9   | `test_str005_links_h2_pass`              | DS-VC-STR-005 | No E005 diagnostic             | 3.0 points, passed=True           |
| 10  | `test_str006_no_structure_chaos_pass`    | DS-VC-STR-006 | No AP-CRIT-002 detected        | 3.0 points, passed=True           |
| 11  | `test_str006_structure_chaos_fail`       | DS-VC-STR-006 | AP-CRIT-002 detected           | 0.0 points, passed=False          |
| 12  | `test_str007_encoding_pass`              | DS-VC-STR-007 | No E003 diagnostic             | 2.0 points, passed=True           |
| 13  | `test_str008_not_empty_pass`             | DS-VC-STR-008 | No E007 diagnostic             | 3.0 points, passed=True           |
| 14  | `test_str009_reasonable_size_pass`       | DS-VC-STR-009 | No E008 diagnostic             | 3.0 points, passed=True           |
| 15  | `test_str009_oversized_fail`             | DS-VC-STR-009 | E008 diagnostic (>100K tokens) | 0.0 points, passed=False          |

### 2.3 Aggregate Tests (3 tests)

| #   | Test Name                                 | Setup             | Expected                              |
| --- | ----------------------------------------- | ----------------- | ------------------------------------- |
| 16  | `test_structural_perfect_score`           | No diagnostics    | points=30.0, max_points=30.0          |
| 17  | `test_structural_zero_score`              | All criteria fail | points=0.0, checks_failed=9           |
| 18  | `test_structural_dimension_is_structural` | Any result        | dimension=QualityDimension.STRUCTURAL |

### 2.4 Decision Tree

```
For each structural criterion (STR-001 through STR-009):
    │
    ├── Construct ValidationResult with targeted diagnostics
    │
    ├── Call score_structural(result, registry)
    │
    ├── Find criterion in dimension_score.details[]
    │     ├── Binary: assert points == weight (pass) or points == 0 (fail)
    │     └── Graduated: assert points ≈ weight × compliance_rate
    │
    └── Assert aggregate stats (checks_passed, checks_failed, checks_total=9)
```

---

## 3. Content Scorer Tests (`test_content.py`)

### 3.1 Per-Criterion Tests (13 criteria × ~2 tests = ~20 tests)

| #   | Test Name                                    | Criterion     | Setup                           | Expected                           |
| --- | -------------------------------------------- | ------------- | ------------------------------- | ---------------------------------- |
| 1   | `test_con001_link_descriptions_full`         | DS-VC-CON-001 | No W003 diagnostics             | 5.0 points, compliance_rate=1.0    |
| 2   | `test_con001_link_descriptions_partial`      | DS-VC-CON-001 | 5 of 20 links undescribed       | 3.75 points, compliance_rate=0.75  |
| 3   | `test_con001_link_descriptions_zero`         | DS-VC-CON-001 | All links undescribed           | 0.0 points, compliance_rate=0.0    |
| 4   | `test_con002_brief_present_pass`             | DS-VC-CON-002 | No W005 diagnostic              | 5.0 points, passed=True            |
| 5   | `test_con002_brief_missing_fail`             | DS-VC-CON-002 | W005 diagnostic present         | 0.0 points, passed=False           |
| 6   | `test_con003_section_descriptions_graduated` | DS-VC-CON-003 | 80% of sections described       | ~4.0 points, compliance_rate=0.8   |
| 7   | `test_con004_titles_not_urls_pass`           | DS-VC-CON-004 | No W006 diagnostics             | 4.0 points, passed=True            |
| 8   | `test_con005_consistent_formatting_pass`     | DS-VC-CON-005 | No W007 diagnostics             | 3.0 points, passed=True            |
| 9   | `test_con006_hierarchical_structure_pass`    | DS-VC-CON-006 | No W008 diagnostics             | 3.0 points, passed=True            |
| 10  | `test_con007_alt_text_graduated`             | DS-VC-CON-007 | 60% of images have alt text     | ~1.8 points, compliance_rate=0.6   |
| 11  | `test_con008_token_threshold_above`          | DS-VC-CON-008 | 95% of sections above threshold | 5.0 points (threshold met)         |
| 12  | `test_con008_token_threshold_below`          | DS-VC-CON-008 | 30% of sections above threshold | ~1.5 points (threshold graduated)  |
| 13  | `test_con009_code_examples_pass`             | DS-VC-CON-009 | No W004 diagnostics             | 4.0 points, passed=True            |
| 14  | `test_con009_code_examples_fail`             | DS-VC-CON-009 | W004 diagnostic present         | 0.0 points, passed=False           |
| 15  | `test_con010_canonical_url_graduated`        | DS-VC-CON-010 | 85% of URLs canonical           | ~2.55 points, compliance_rate=0.85 |
| 16  | `test_con011_no_broken_links_pass`           | DS-VC-CON-011 | No E006 diagnostics             | 3.0 points, passed=True            |
| 17  | `test_con012_reasonable_depth_pass`          | DS-VC-CON-012 | No W009 diagnostics             | 3.0 points, passed=True            |
| 18  | `test_con013_relative_paths_graduated`       | DS-VC-CON-013 | 70% of URLs absolute            | ~2.1 points, compliance_rate=0.7   |

### 3.2 Aggregate Tests (2 tests)

| #   | Test Name                           | Setup          | Expected                           |
| --- | ----------------------------------- | -------------- | ---------------------------------- |
| 19  | `test_content_perfect_score`        | No diagnostics | points=50.0, max_points=50.0       |
| 20  | `test_content_dimension_is_content` | Any result     | dimension=QualityDimension.CONTENT |

### 3.3 Decision Tree

```
For each content criterion (CON-001 through CON-013):
    │
    ├── Construct ValidationResult with targeted diagnostics
    │
    ├── Call score_content(result, registry)
    │
    ├── Find criterion in dimension_score.details[]
    │     ├── Binary: assert points == weight (pass) or points == 0 (fail)
    │     └── Graduated: assert points ≈ weight × compliance_rate (tolerance ±0.01)
    │     └── Threshold: assert threshold logic applied
    │
    └── Assert aggregate stats (checks_passed, checks_failed, checks_total=13)
```

---

## 4. Anti-Pattern Scorer Tests (`test_anti_pattern.py`)

### 4.1 Per-Criterion Tests (8 criteria × ~2 tests = ~12 tests)

| #   | Test Name                                   | Criterion     | Setup                              | Expected                          |
| --- | ------------------------------------------- | ------------- | ---------------------------------- | --------------------------------- |
| 1   | `test_apd001_l4_absent_scores_zero`         | DS-VC-APD-001 | No I001 diagnostic (L4 inactive)   | 0.0 points (L4-dependent)         |
| 2   | `test_apd001_l4_present_scores_full`        | DS-VC-APD-001 | No I001 diagnostic (L4 active)     | 3.0 points                        |
| 3   | `test_apd002_l4_absent_scores_zero`         | DS-VC-APD-002 | No I002 diagnostic (L4 inactive)   | 0.0 points (L4-dependent)         |
| 4   | `test_apd003_l4_absent_scores_zero`         | DS-VC-APD-003 | No I003 diagnostic (L4 inactive)   | 0.0 points (L4-dependent)         |
| 5   | `test_apd004_no_content_anti_patterns_full` | DS-VC-APD-004 | No AP-CONT patterns detected       | 3.0 points (full compliance)      |
| 6   | `test_apd004_some_content_anti_patterns`    | DS-VC-APD-004 | 3 of 7 evaluable patterns detected | ~1.71 points (4/7 × 3)            |
| 7   | `test_apd005_no_strategic_anti_patterns`    | DS-VC-APD-005 | No AP-STRAT patterns detected      | 2.0 points                        |
| 8   | `test_apd005_some_strategic_anti_patterns`  | DS-VC-APD-005 | 1 of 3 evaluable patterns detected | ~1.33 points (2/3 × 2)            |
| 9   | `test_apd006_balanced_distribution`         | DS-VC-APD-006 | No section >40% of tokens          | 2.0 points                        |
| 10  | `test_apd006_imbalanced_distribution`       | DS-VC-APD-006 | 1 section = 50% of tokens          | 0.0 points                        |
| 11  | `test_apd007_absolute_urls_graduated`       | DS-VC-APD-007 | 85% absolute URLs                  | ~1.7 points (below 90% threshold) |
| 12  | `test_apd008_l4_absent_scores_zero`         | DS-VC-APD-008 | No I007 diagnostic (L4 inactive)   | 0.0 points (L4-dependent)         |

### 4.2 The L4-Dependent Criterion Pattern

All 4 L4-dependent criteria (APD-001, APD-002, APD-003, APD-008) follow the same test pattern:

```python
class TestL4DependentCriteria:
    """Verify L4-dependent criteria score 0 when L4 codes are absent.

    At v0.4.x, L4 checks are not active, so the corresponding
    diagnostic codes (I001, I002, I003, I007) never appear in
    the ValidationResult. The scorer must score 0 — not "pass by
    absence" — because the code was never evaluated.

    Implements v0.4.2a (L4 dependency tests).
    """

    @pytest.mark.parametrize(
        "check_id, expected_weight",
        [
            ("DS-VC-APD-001", 3.0),
            ("DS-VC-APD-002", 3.0),
            ("DS-VC-APD-003", 3.0),
            ("DS-VC-APD-008", 2.0),
        ],
    )
    def test_l4_absent_scores_zero(self, check_id: str, expected_weight: float):
        """L4-dependent criteria score 0 when L4 codes are not evaluated."""
        result = make_anti_pattern_result(diagnostics=[], l4_active=False)
        score = score_anti_pattern(result, CRITERIA_REGISTRY)

        detail = next(d for d in score.details if d["check_id"] == check_id)
        assert detail["points"] == 0.0
        assert detail["weight"] == expected_weight
        assert detail["passed"] is False

    @pytest.mark.parametrize(
        "check_id, expected_weight",
        [
            ("DS-VC-APD-001", 3.0),
            ("DS-VC-APD-002", 3.0),
            ("DS-VC-APD-003", 3.0),
            ("DS-VC-APD-008", 2.0),
        ],
    )
    def test_l4_present_and_passing_scores_full(
        self, check_id: str, expected_weight: float
    ):
        """L4-dependent criteria score full when L4 is active and passing."""
        result = make_anti_pattern_result(
            diagnostics=[],  # No violations
            l4_active=True,  # L4 codes were evaluated
        )
        score = score_anti_pattern(result, CRITERIA_REGISTRY)

        detail = next(d for d in score.details if d["check_id"] == check_id)
        assert detail["points"] == expected_weight
        assert detail["passed"] is True
```

### 4.3 Aggregate Tests (2 tests)

| #   | Test Name                                     | Setup       | Expected                                |
| --- | --------------------------------------------- | ----------- | --------------------------------------- |
| 13  | `test_anti_pattern_l4_ceiling`                | L4 inactive | points ≤ 9.0 (APD-4/5/6/7 only)         |
| 14  | `test_anti_pattern_dimension_is_anti_pattern` | Any result  | dimension=QualityDimension.ANTI_PATTERN |

---

## 5. Skipped-Level Tests (4 tests)

These cross-cutting tests verify that when higher validation levels were never evaluated (gate-on-failure), the dimension scorers handle the absence correctly.

| #   | Test Name                                     | Setup                          | Expected                  |
| --- | --------------------------------------------- | ------------------------------ | ------------------------- |
| 1   | `test_l0_failure_structural_scores_near_zero` | L0 failure, no L1+ diagnostics | Most STR criteria score 0 |
| 2   | `test_l0_failure_content_scores_zero`         | L0 failure, no L2 diagnostics  | All CON criteria score 0  |
| 3   | `test_l1_failure_content_scores_zero`         | L1 failure, L2 never evaluated | All CON criteria score 0  |
| 4   | `test_l2_failure_best_practices_scores_zero`  | L2 failure, L3 never evaluated | L3 criteria score 0       |

### 5.1 Decision Tree

```
For each skipped-level scenario:
    │
    ├── Construct ValidationResult with levels_passed={L0: False, ...}
    │
    ├── Call each dimension scorer
    │
    └── Assert: criteria at unevaluated levels score 0 (not pass by absence)
              │
              ├── STR criteria at L1+: 0 if L0 failed
              ├── CON criteria at L2+: 0 if L1 failed
              └── APD criteria at L4:  0 always (pre-v0.9.0)
```

---

## 6. Float Precision Tests (3 tests)

Verify that graduated scoring produces correct fractional points — not rounded integers.

| #   | Test Name                                    | Setup                            | Expected                            |
| --- | -------------------------------------------- | -------------------------------- | ----------------------------------- |
| 1   | `test_graduated_produces_float`              | 3/7 compliance on 5-pt criterion | 2.142857... (not 2.0 or 3.0)        |
| 2   | `test_graduated_sum_matches_aggregate`       | Multiple graduated criteria      | sum(details.points) == score.points |
| 3   | `test_graduated_compliance_rate_is_fraction` | 75% compliance                   | compliance_rate == 0.75 (not 75)    |

---

## 7. Edge Cases

| Case                                    | Behavior                                 | Test Coverage           |
| --------------------------------------- | ---------------------------------------- | ----------------------- |
| ValidationResult has zero diagnostics   | All binary criteria pass (`passed=True`) | `test_*_perfect_score`  |
| Multiple diagnostics for same criterion | Score based on worst case (graduated)    | `test_str003_*_partial` |
| Unknown diagnostic code                 | Ignored — does not affect scoring        | Not tested (defensive)  |
| Registry has criterion not in result    | Criterion treated as not evaluated = 0   | Skipped-level tests     |
| L4 codes appear unexpectedly            | Scored normally (forward-compatible)     | `test_l4_present_*`     |

---

## 8. Deliverables

| File                                 | Description                             | Test Count |
| ------------------------------------ | --------------------------------------- | ---------- |
| `tests/scoring/test_structural.py`   | Structural scorer tests (STR-001–009)   | ~18        |
| `tests/scoring/test_content.py`      | Content scorer tests (CON-001–013)      | ~20        |
| `tests/scoring/test_anti_pattern.py` | Anti-pattern scorer tests (APD-001–008) | ~14        |
| **Total v0.4.2a**                    |                                         | **~52**    |

---

## 9. Changelog Requirements

```markdown
## [0.4.2a] - YYYY-MM-DD

**Dimension Scorer Unit Tests — Per-criterion verification for all 30 criteria.**

### Added

#### Structural Scorer Tests (`tests/scoring/test_structural.py`)

- 15 per-criterion tests + 3 aggregate tests covering STR-001 through STR-009
- Graduated scoring precision tests for STR-003, STR-004

#### Content Scorer Tests (`tests/scoring/test_content.py`)

- 18 per-criterion tests + 2 aggregate tests covering CON-001 through CON-013
- Threshold-graduated tests for CON-008

#### Anti-Pattern Scorer Tests (`tests/scoring/test_anti_pattern.py`)

- 12 per-criterion tests + 2 aggregate tests covering APD-001 through APD-008
- L4 dependency verification (APD-001–003, APD-008 score 0 at v0.4.x)
- L4 ceiling test (max APD ≤ 9 at v0.4.x)

#### Cross-Cutting Tests

- 4 skipped-level tests (L0/L1/L2 failure cascades)
- 3 float precision tests

### Notes

- **Coverage:** Targets ≥90% on `scoring.structural`, `scoring.content`, `scoring.anti_pattern`.
- **Fixtures:** Uses synthetic `ValidationResult` instances (no file I/O).
```
