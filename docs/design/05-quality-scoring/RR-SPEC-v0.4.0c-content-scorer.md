# v0.4.0c — Content Dimension Scorer

> **Version:** v0.4.0c
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.0-dimension-scoring.md](RR-SPEC-v0.4.0-dimension-scoring.md)
> **Depends On:** v0.4.0a (criteria registry), v0.3.x (`ValidationResult`)

---

## 1. Purpose

v0.4.0c implements the **Content Dimension Scorer** — evaluates 13 criteria (DS-VC-CON-001 through CON-013) and produces a `DimensionScore(CONTENT)` with 0–50 points.

The Content dimension is the **primary quality driver** (50% weight, DECISION-014). It contains the criteria with the highest point allocations: Code Examples (CON-010, 5 pts), Canonical Names (CON-008, 5 pts), Master Index (CON-009, 5 pts), and Link Descriptions (CON-001, 5 pts) — all empirically validated as the strongest quality predictors.

### 1.1 User Story

> As a scorer, I want to evaluate the 13 content criteria against diagnostics and produce a dimension score so that content quality — the strongest predictor of file usefulness — is quantified with graduated precision.

---

## 2. Criteria Evaluation Logic

### 2.1 Scoring Decision Table

| Criterion                          | Pts | Mode      | Pass Condition          | Graduated Formula                                       |
| ---------------------------------- | --- | --------- | ----------------------- | ------------------------------------------------------- |
| **CON-001** Link Descriptions      | 5   | GRADUATED | No W003                 | `(described_links / total_links) × 5`                   |
| **CON-002** URL Resolvability      | 4   | GRADUATED | No E006 (reachability)  | `(reachable_urls / checked_urls) × 4`                   |
| **CON-003** No Placeholder Text    | 3   | GRADUATED | No W011 (placeholder)   | `(clean_sections / total_sections) × 3`                 |
| **CON-004** Non-Empty Sections     | 4   | GRADUATED | No W011 (empty)         | `(non_empty / total_sections) × 4`                      |
| **CON-005** No Duplicate Names     | 3   | BINARY    | No W012                 | —                                                       |
| **CON-006** Substantive Blockquote | 3   | BINARY    | Blockquote >20 chars    | —                                                       |
| **CON-007** No Formulaic Desc.     | 3   | BINARY    | No W006                 | —                                                       |
| **CON-008** Canonical Names        | 5   | GRADUATED | ≥70% canonical sections | `min(compliance / 0.70, 1.0) × 5` (threshold-graduated) |
| **CON-009** Master Index           | 5   | BINARY    | No W009                 | —                                                       |
| **CON-010** Code Examples          | 5   | BINARY    | No W004                 | —                                                       |
| **CON-011** Code Lang Specifiers   | 3   | GRADUATED | No W005                 | `(with_lang / total_blocks) × 3`                        |
| **CON-012** Token Budget           | 4   | BINARY    | No W010                 | —                                                       |
| **CON-013** Version Metadata       | 3   | BINARY    | No W007                 | —                                                       |

### 2.2 CON-008 Threshold-Graduated Scoring

CON-008 (Canonical Section Names) uses a hybrid approach — it's graduated, but with a 70% compliance threshold for full points:

```
compliance = canonical_sections / total_sections
if compliance >= 0.70:
    points = 5.0  (full)
else:
    points = (compliance / 0.70) * 5.0  (proportional up to threshold)
```

| Compliance | Points                |
| ---------- | --------------------- |
| 100%       | 5.0                   |
| 85%        | 5.0 (above threshold) |
| 70%        | 5.0 (at threshold)    |
| 50%        | 3.57                  |
| 30%        | 2.14                  |
| 0%         | 0.0                   |

### 2.3 CON-002 URL Resolvability

This criterion only scores when `check_urls=True` was passed to `validate_file()`:

- **If `check_urls=True`:** Graduated scoring based on `(reachable / checked) × 4`.
- **If `check_urls=False`:** No E006-reachability diagnostics emitted → criterion scores full 4 points (absence of failure diagnostics = pass).

> **Design Decision:** URLs not checked = pass. This avoids penalizing offline validation. When URL checking is explicitly enabled, failures reduce the score.

### 2.4 Decision Tree

```
For each CON criterion:
    │
    ├── Look up diagnostic_codes from registry
    │
    ├── Count relevant diagnostics in ValidationResult
    │
    ├── For GRADUATED criteria:
    │     ├── Determine total_items (links, sections, code blocks, etc.)
    │     ├── violations = count of relevant diagnostics
    │     ├── compliance = 1.0 - (violations / total_items)
    │     ├── For CON-008: apply threshold formula (compliance / 0.70)
    │     └── points = compliance × max_points
    │
    ├── For BINARY criteria:
    │     ├── violations == 0 → full points
    │     └── violations > 0  → 0 points
    │
    └── Record in details[]
```

---

## 3. Implementation

```python
"""Implements v0.4.0c — Content Dimension Scorer."""

from docstratum.schema.quality import DimensionScore, QualityDimension
from docstratum.schema.validation import ValidationResult
from docstratum.scoring.registry import (
    CriterionMapping,
    ScoringMode,
    get_criteria_by_dimension,
)


def score_content(result: ValidationResult) -> DimensionScore:
    """Score the content dimension (50 points max).

    Evaluates 13 content criteria (DS-VC-CON-001 through CON-013)
    against the diagnostics in a ValidationResult.

    Args:
        result: Validated file result from v0.3.x pipeline.

    Returns:
        DimensionScore with content points and per-criterion details.

    Implements v0.4.0c. Grounding: DS-QS-DIM-CON, DECISION-014.
    """
    criteria = get_criteria_by_dimension(QualityDimension.CONTENT)
    details: list[dict] = []
    total_points = 0.0
    passed = 0
    failed = 0

    for criterion in criteria:
        criterion_result = _evaluate_content_criterion(criterion, result)
        details.append(criterion_result)
        total_points += criterion_result["points"]
        if criterion_result["passed"]:
            passed += 1
        else:
            failed += 1

    return DimensionScore(
        dimension=QualityDimension.CONTENT,
        points=total_points,
        max_points=50.0,
        checks_passed=passed,
        checks_failed=failed,
        checks_total=len(criteria),
        details=details,
    )


def _evaluate_content_criterion(
    criterion: CriterionMapping,
    result: ValidationResult,
) -> dict:
    """Evaluate a single content criterion.

    Handles both BINARY and GRADUATED scoring modes,
    including the CON-008 threshold variant.
    """
    diag_count = sum(
        1 for d in result.diagnostics
        if d.code in criterion.diagnostic_codes
    )

    if criterion.scoring_mode == ScoringMode.BINARY:
        passed = diag_count == 0
        points = criterion.max_points if passed else 0.0
        compliance = 1.0 if passed else 0.0

    elif criterion.scoring_mode == ScoringMode.GRADUATED:
        total_items = _get_content_total_items(criterion, result)
        compliance = max(0.0, 1.0 - diag_count / max(total_items, 1))

        # CON-008: threshold-graduated variant
        if criterion.threshold > 0:
            if compliance >= criterion.threshold:
                points = criterion.max_points
            else:
                points = (compliance / criterion.threshold) * criterion.max_points
        else:
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


def _get_content_total_items(
    criterion: CriterionMapping,
    result: ValidationResult,
) -> int:
    """Get the denominator for graduated content scoring.

    Returns the total countable items relevant to each criterion.
    This information is derived from the ValidationResult context.
    """
    # The actual denominators will come from ValidationResult context
    # or from diagnostic metadata (e.g., total links, total sections).
    # Placeholder implementation — v0.4.0c design spec documents
    # the expected sources.
    return max(1, len(result.diagnostics))
```

---

## 4. Edge Cases

| Case                            | Behavior                                           | Rationale                           |
| ------------------------------- | -------------------------------------------------- | ----------------------------------- |
| L0/L1 fails → no L2 diagnostics | CON-001–007 score 0 (no data)                      | Unevaluated = 0                     |
| L2 fails → no L3 diagnostics    | CON-008–013 score 0 (no data)                      | Unevaluated = 0                     |
| `check_urls=False`              | CON-002 = 4.0 (full points)                        | No E006-reachability emitted = pass |
| File with no links              | CON-001 total_items = 0, compliance = 1.0          | Empty set = vacuously satisfied     |
| File with no code blocks        | CON-010 = 0 (W004 emitted), CON-011 compliance N/A | Binary W004 present = fail          |
| 100% canonical names            | CON-008 = 5.0 (above 70% threshold)                | Threshold-graduated formula         |
| 65% canonical names             | CON-008 = `(0.65/0.70) × 5 = 4.64`                 | Below threshold = proportional      |
| All sections empty              | CON-004 = 0.0, CON-003 potentially 0 too           | Multiple criteria can score 0       |

---

## 5. Deliverables

| File                                | Description           |
| ----------------------------------- | --------------------- |
| `src/docstratum/scoring/content.py` | Content scorer module |
| `tests/scoring/test_content.py`     | Unit tests            |

---

## 6. Test Plan (16 tests)

| #   | Test Name                            | Input                       | Expected                             |
| --- | ------------------------------------ | --------------------------- | ------------------------------------ |
| 1   | `test_perfect_content_score`         | No diagnostics              | 50.0 points, 13 passed               |
| 2   | `test_w003_graduates_con_001`        | 5 of 20 links undescribed   | `(15/20) × 5 = 3.75`                 |
| 3   | `test_con_002_urls_not_checked`      | No E006 reachability        | Full 4.0 points                      |
| 4   | `test_con_002_urls_partial`          | 3 of 10 unreachable         | `(7/10) × 4 = 2.8`                   |
| 5   | `test_con_003_placeholder_graduated` | 2 of 8 sections placeholder | `(6/8) × 3 = 2.25`                   |
| 6   | `test_con_004_empty_sections`        | 4 of 12 empty               | `(8/12) × 4 = 2.67`                  |
| 7   | `test_con_005_binary_pass`           | No W012                     | 3.0                                  |
| 8   | `test_con_005_binary_fail`           | W012 present                | 0.0                                  |
| 9   | `test_con_007_formulaic_fail`        | W006 present                | 0.0                                  |
| 10  | `test_con_008_above_threshold`       | 80% canonical               | 5.0 (full)                           |
| 11  | `test_con_008_below_threshold`       | 50% canonical               | `(0.50/0.70) × 5 ≈ 3.57`             |
| 12  | `test_con_009_binary_pass`           | No W009                     | 5.0                                  |
| 13  | `test_con_010_code_examples_fail`    | W004 present                | 0.0                                  |
| 14  | `test_l0_failure_zeroes_content`     | L0 failed                   | All criteria score 0                 |
| 15  | `test_details_all_populated`         | Any input                   | 13 entries with all fields           |
| 16  | `test_float_precision`               | Graduated criteria          | Points are float, not rounded to int |
