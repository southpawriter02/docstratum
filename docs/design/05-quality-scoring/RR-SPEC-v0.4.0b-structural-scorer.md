# v0.4.0b — Structural Dimension Scorer

> **Version:** v0.4.0b
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.0-dimension-scoring.md](RR-SPEC-v0.4.0-dimension-scoring.md)
> **Depends On:** v0.4.0a (criteria registry), v0.3.x (`ValidationResult`)

---

## 1. Purpose

v0.4.0b implements the **Structural Dimension Scorer** — evaluates 9 criteria (DS-VC-STR-001 through STR-009) and produces a `DimensionScore(STRUCTURAL)` with 0–30 points.

### 1.1 What This Scorer Reads

| Input                            | Source           | Usage                                    |
| -------------------------------- | ---------------- | ---------------------------------------- |
| `ValidationResult.diagnostics[]` | v0.3.x pipeline  | Filter by structural diagnostic codes    |
| `STRUCTURAL_CRITERIA`            | v0.4.0a registry | Criteria definitions, scoring modes      |
| Anti-pattern metadata            | v0.3.4 detector  | STR-008 (critical), STR-009 (structural) |

### 1.2 What This Scorer Produces

```python
DimensionScore(
    dimension=QualityDimension.STRUCTURAL,
    points=28.5,       # 0–30 float
    max_points=30.0,
    checks_passed=7,
    checks_failed=2,
    checks_total=9,
    details=[
        {"check_id": "DS-VC-STR-001", "passed": True, "weight": 5.0, "points": 5.0,
         "compliance_rate": 1.0, "diagnostic_count": 0, "level": "L1"},
        ...
    ],
    is_gated=False,  # Set at composite level (v0.4.1b), not here
)
```

### 1.3 User Story

> As a scorer, I want to evaluate the 9 structural criteria against a `ValidationResult` and produce a dimension score so that the file's structural quality is quantified.

---

## 2. Criteria Evaluation Logic

### 2.1 Scoring Decision Table

| Criterion                      | Points | Mode      | Pass Condition                     | Graduated Formula                     |
| ------------------------------ | ------ | --------- | ---------------------------------- | ------------------------------------- |
| **STR-001** H1 Title Present   | 5      | BINARY    | E001 NOT in diagnostics            | —                                     |
| **STR-002** Single H1          | 3      | BINARY    | E002 NOT in diagnostics            | —                                     |
| **STR-003** Blockquote Present | 3      | BINARY    | W001 NOT in diagnostics            | —                                     |
| **STR-004** Valid Markdown     | 4      | GRADUATED | No E005 diagnostics                | `(1 - violations/total_elements) × 4` |
| **STR-005** Link Syntax        | 4      | GRADUATED | No E006 (syntactic)                | `(valid_links / total_links) × 4`     |
| **STR-006** Heading Hierarchy  | 3      | GRADUATED | No heading nesting violations      | `(1 - violations/total_headings) × 3` |
| **STR-007** Section Order      | 3      | BINARY    | W008 NOT in diagnostics            | —                                     |
| **STR-008** No Critical APs    | 3      | BINARY    | None of AP-CRIT-001–004 detected   | —                                     |
| **STR-009** No Structural APs  | 2      | GRADUATED | None of AP-STRUCT-001–005 detected | `(absent/5) × 2`                      |

### 2.2 Decision Tree

```
For each STR criterion in STRUCTURAL_CRITERIA:
    │
    ├── Look up diagnostic_codes and anti_pattern_ids from registry
    │
    ├── Count matching diagnostics in ValidationResult
    │     └── relevant_count = sum(1 for d in diagnostics if d.code in criterion.diagnostic_codes)
    │
    ├── For anti_pattern_ids (STR-008, STR-009):
    │     └── detected_count = count of detected patterns from anti-pattern metadata
    │
    ├── Apply scoring mode:
    │     ├── BINARY:
    │     │     ├── relevant_count == 0 AND detected_count == 0 → full points
    │     │     └── else → 0 points
    │     │
    │     └── GRADUATED:
    │           ├── Compute compliance_rate (varies by criterion)
    │           └── points = compliance_rate × max_points
    │
    └── Record in details[]: {check_id, passed, weight, points, compliance_rate}
```

---

## 3. Implementation

```python
"""Implements v0.4.0b — Structural Dimension Scorer."""

from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.quality import DimensionScore, QualityDimension
from docstratum.schema.validation import ValidationDiagnostic, ValidationResult
from docstratum.scoring.registry import (
    CriterionMapping,
    ScoringMode,
    STRUCTURAL_CRITERIA,
    get_criteria_by_dimension,
)


def score_structural(
    result: ValidationResult,
    anti_pattern_results: dict | None = None,
) -> DimensionScore:
    """Score the structural dimension (30 points max).

    Evaluates 9 structural criteria (DS-VC-STR-001 through STR-009)
    against the diagnostics in a ValidationResult.

    Args:
        result: Validated file result from v0.3.x pipeline.
        anti_pattern_results: Anti-pattern detection results from v0.3.4.

    Returns:
        DimensionScore with structural points and per-criterion details.

    Implements v0.4.0b. Grounding: DS-QS-DIM-STR.
    """
    criteria = get_criteria_by_dimension(QualityDimension.STRUCTURAL)
    details: list[dict] = []
    total_points = 0.0
    passed = 0
    failed = 0

    for criterion in criteria:
        criterion_result = _evaluate_criterion(
            criterion, result, anti_pattern_results or {}
        )
        details.append(criterion_result)
        total_points += criterion_result["points"]
        if criterion_result["passed"]:
            passed += 1
        else:
            failed += 1

    return DimensionScore(
        dimension=QualityDimension.STRUCTURAL,
        points=total_points,
        max_points=30.0,
        checks_passed=passed,
        checks_failed=failed,
        checks_total=len(criteria),
        details=details,
    )


def _evaluate_criterion(
    criterion: CriterionMapping,
    result: ValidationResult,
    anti_pattern_results: dict,
) -> dict:
    """Evaluate a single structural criterion."""
    # Count relevant diagnostics
    diag_count = sum(
        1 for d in result.diagnostics
        if d.code in criterion.diagnostic_codes
    )

    # Count detected anti-patterns
    ap_detected = sum(
        1 for ap_id in criterion.anti_pattern_ids
        if anti_pattern_results.get(str(ap_id), {}).get("detected", False)
    )

    if criterion.scoring_mode == ScoringMode.BINARY:
        passed = diag_count == 0 and ap_detected == 0
        points = criterion.max_points if passed else 0.0
        compliance = 1.0 if passed else 0.0
    elif criterion.scoring_mode == ScoringMode.GRADUATED:
        total_items = _get_total_items(criterion, result)
        violations = diag_count + ap_detected
        compliance = max(0.0, 1.0 - violations / max(total_items, 1))
        points = compliance * criterion.max_points
        passed = points == criterion.max_points
    else:
        compliance = 1.0
        points = criterion.max_points
        passed = True

    return {
        "check_id": criterion.criterion_id,
        "passed": passed,
        "weight": criterion.max_points,
        "points": round(points, 2),
        "compliance_rate": round(compliance, 2),
        "diagnostic_count": diag_count,
        "level": criterion.validation_level.name,
    }


def _get_total_items(
    criterion: CriterionMapping,
    result: ValidationResult,
) -> int:
    """Get the denominator for graduated scoring.

    Varies by criterion:
    - STR-004: total markdown elements parsed
    - STR-005: total links in document
    - STR-006: total headings
    - STR-009: 5 (structural anti-pattern count)
    """
    totals = {
        "DS-VC-STR-004": lambda r: max(len(r.diagnostics), 1),
        "DS-VC-STR-005": lambda r: max(len(r.diagnostics), 1),
        "DS-VC-STR-006": lambda r: max(len(r.diagnostics), 1),
        "DS-VC-STR-009": lambda r: 5,  # Fixed: 5 structural APs
    }
    fn = totals.get(criterion.criterion_id, lambda r: 1)
    return fn(result)
```

---

## 4. Edge Cases

| Case                                    | Behavior                                            | Rationale                                    |
| --------------------------------------- | --------------------------------------------------- | -------------------------------------------- |
| L0 fails → no L1/L3 diagnostics emitted | STR criteria that depend on L1+ codes score 0       | Unevaluated = 0 points (scope doc §2.5)      |
| All 4 critical APs detected             | STR-008 = 0 (also triggers gate at composite level) | Binary: any detected = fail                  |
| 3 of 5 structural APs detected          | STR-009 = `(2/5) × 2 = 0.8 points`                  | Graduated: (absent/5) × 2                    |
| No diagnostics at all                   | All STR criteria pass → 30 points                   | Clean file                                   |
| STR-006 with heuristic                  | Depends on parsed heading structure                 | No specific diagnostic code; needs heuristic |

---

## 5. Deliverables

| File                                   | Description              |
| -------------------------------------- | ------------------------ |
| `src/docstratum/scoring/structural.py` | Structural scorer module |
| `tests/scoring/test_structural.py`     | Unit tests               |

---

## 6. Test Plan (12 tests)

| #   | Test Name                               | Input                                 | Expected                                          |
| --- | --------------------------------------- | ------------------------------------- | ------------------------------------------------- |
| 1   | `test_perfect_structural_score`         | No diagnostics, no APs                | 30.0 points, 9 passed                             |
| 2   | `test_e001_fails_str_001`               | E001 diagnostic                       | STR-001 = 0, total ≤ 25                           |
| 3   | `test_e002_fails_str_002`               | E002 diagnostic                       | STR-002 = 0, total ≤ 27                           |
| 4   | `test_w001_fails_str_003`               | W001 diagnostic                       | STR-003 = 0, total ≤ 27                           |
| 5   | `test_str_004_graduated`                | 3 E005 diagnostics out of 10 elements | 70% compliance → 2.8 points                       |
| 6   | `test_str_005_graduated`                | 2 E006 syntactic out of 20 links      | 90% → 3.6 points                                  |
| 7   | `test_w008_fails_str_007`               | W008 diagnostic                       | STR-007 = 0                                       |
| 8   | `test_critical_aps_fail_str_008`        | AP-CRIT-001 detected                  | STR-008 = 0                                       |
| 9   | `test_structural_aps_graduated_str_009` | 2 of 5 detected                       | STR-009 = `(3/5) × 2 = 1.2`                       |
| 10  | `test_l0_failure_zeroes_l1_criteria`    | L0 failed, no L1+ diagnostics         | L1 criteria score 0                               |
| 11  | `test_details_populated`                | Any input                             | 9 entries in `details[]` with all required fields |
| 12  | `test_returns_dimension_score`          | Any input                             | Type is `DimensionScore`, dimension = STRUCTURAL  |
