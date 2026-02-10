# v0.4.0d — Anti-Pattern Dimension Scorer

> **Version:** v0.4.0d
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.4.0-dimension-scoring.md](RR-SPEC-v0.4.0-dimension-scoring.md)
> **Depends On:** v0.4.0a (criteria registry), v0.3.4 (anti-pattern detection), v0.3.x (`ValidationResult`), `schema/parsed.py` (`ParsedLlmsTxt`)

---

## 1. Purpose

v0.4.0d implements the **Anti-Pattern Dimension Scorer** — evaluates 8 criteria (DS-VC-APD-001 through APD-008) and produces a `DimensionScore(ANTI_PATTERN)` with 0–20 points.

This is the **differentiator** dimension — it separates STRONG files from EXEMPLARY. It is also the dimension most affected by the L4 ceiling: 4 of 8 criteria depend on L4 diagnostic codes not yet active, reducing the effective maximum from 20 to **9 points** until v0.9.0.

### 1.1 L4 Ceiling Impact

| At v0.4.x                                                                 | At v0.9.0+                   |
| ------------------------------------------------------------------------- | ---------------------------- |
| Effective APD max: **9** (APD-004: 3, APD-005: 2, APD-006: 2, APD-007: 2) | Full APD max: **20**         |
| Composite ceiling: **~89**                                                | Composite ceiling: **100**   |
| Highest grade: **STRONG**                                                 | Highest grade: **EXEMPLARY** |

### 1.2 Design Decision: APD-006 Model Access

DS-VC-APD-006 (Balanced Token Distribution) checks whether any section exceeds 40% of total tokens. This information is **not** in `ValidationResult` — it requires reading `ParsedLlmsTxt.sections[].estimated_tokens`.

**Decision:** The APD scorer accepts `ParsedLlmsTxt` as an additional input alongside `ValidationResult` (scope doc option a). This is simpler than adding a new diagnostic code, and it is the single documented exception to the "scorer reads only `ValidationResult`" rule.

### 1.3 User Story

> As a scorer, I want to evaluate anti-pattern criteria including L4-dependent ones (gracefully scoring 0 when L4 is inactive) so that the scoring framework is extensible without code changes when L4 arrives.

---

## 2. Criteria Evaluation Logic

### 2.1 Scoring Decision Table

| Criterion                       | Pts | L4 Dep.? | Mode      | Pass Condition                   |
| ------------------------------- | --- | -------- | --------- | -------------------------------- |
| **APD-001** LLM Instructions    | 3   | **Yes**  | BINARY    | I001 NOT in diagnostics          |
| **APD-002** Concept Definitions | 3   | **Yes**  | BINARY    | I002 NOT in diagnostics          |
| **APD-003** Few-Shot Examples   | 3   | **Yes**  | BINARY    | I003 NOT in diagnostics          |
| **APD-004** No Content APs      | 3   | Partial  | GRADUATED | `(absent / evaluable) × 3`       |
| **APD-005** No Strategic APs    | 2   | Partial  | GRADUATED | `(absent / evaluable) × 2`       |
| **APD-006** Token Distribution  | 2   | No       | BINARY    | No section > 40% of total tokens |
| **APD-007** Absolute URLs       | 2   | No       | THRESHOLD | ≥90% URLs absolute → 2, else 0   |
| **APD-008** Jargon Defined      | 2   | **Yes**  | BINARY    | I007 NOT in diagnostics          |

### 2.2 L4-Dependent Criteria Logic (APD-001, APD-002, APD-003, APD-008)

```
Is the corresponding L4 diagnostic code present in DiagnosticCode enum?
    │
    ├── Yes (v0.9.0+): Check if the code appears in ValidationResult.diagnostics[]
    │     ├── Code absent (feature present): score full points
    │     └── Code present (feature missing): score 0 points
    │
    └── No (pre-v0.9.0): L4 checks were never run
          │
          └── Score 0 points
              Rationale: absence of a check ≠ presence of the feature.
              The file gets no credit for something that was never verified.
```

The scorer does **not** hardcode L4 availability. Instead, it checks whether the relevant diagnostic codes appear in the `ValidationResult`. If L4 checks weren't run, those codes never appear — the criteria naturally score 0. When v0.9.0 activates L4, the codes start appearing, and the scorer auto-evaluates.

### 2.3 APD-004 / APD-005 Graduated Scoring (Partial L4)

```python
# APD-004: Content anti-patterns (AP-CONT-001 through AP-CONT-009)
# 2 patterns (AP-CONT-003, AP-CONT-008) depend on L4 → excluded from denominator

evaluable_patterns = [ap for ap in AP_CONT_ALL if not ap.l4_dependent]
# At v0.4.x: evaluable = 7 of 9
# At v0.9.0+: evaluable = 9 of 9

detected_count = sum(1 for ap in evaluable_patterns if ap.detected)
absent_count = len(evaluable_patterns) - detected_count

points = (absent_count / len(evaluable_patterns)) * 3.0
```

| Evaluable   | Detected | Absent | Points             |
| ----------- | -------- | ------ | ------------------ |
| 7 (v0.4.x)  | 0        | 7      | 3.0 (full)         |
| 7 (v0.4.x)  | 3        | 4      | `(4/7) × 3 = 1.71` |
| 7 (v0.4.x)  | 7        | 0      | 0.0                |
| 9 (v0.9.0+) | 0        | 9      | 3.0 (full)         |
| 9 (v0.9.0+) | 2        | 7      | `(7/9) × 3 = 2.33` |

Same approach for APD-005 with strategic anti-patterns (3 of 4 evaluable at v0.4.x).

### 2.4 APD-006 Token Distribution Check

```python
def _check_token_distribution(parsed: ParsedLlmsTxt) -> bool:
    """Check that no section exceeds 40% of total tokens.

    This is the one case where the APD scorer reads ParsedLlmsTxt
    directly, per scope doc §3.1 option (a).

    Returns True if distribution is balanced (pass).
    """
    total_tokens = sum(s.estimated_tokens for s in parsed.sections)
    if total_tokens == 0:
        return True  # No tokens = vacuously balanced

    threshold = total_tokens * 0.40
    return all(s.estimated_tokens <= threshold for s in parsed.sections)
```

### 2.5 APD-007 Absolute URL Prevalence

```python
def _check_absolute_url_prevalence(result: ValidationResult) -> float:
    """Calculate the fraction of URLs that are absolute.

    Uses I004 diagnostic (if emitted for relative URLs) or
    infers from the parsed link data.

    Returns compliance rate (0.0–1.0).
    """
    # Count relative URL diagnostics (I005_UNOPTIMIZED_LINKS or similar)
    relative_count = sum(
        1 for d in result.diagnostics
        if d.code == DiagnosticCode.I005_UNOPTIMIZED_LINKS
    )
    total_urls = _count_total_urls(result)
    if total_urls == 0:
        return 1.0  # No URLs = vacuously all absolute

    absolute_rate = 1.0 - (relative_count / total_urls)
    return absolute_rate
```

THRESHOLD scoring: `≥ 0.90 → 2.0 points`, `< 0.90 → 0.0 points`.

### 2.6 Decision Tree

```
For each APD criterion:
    │
    ├── Is l4_dependent = True?
    │     ├── Yes: Check if L4 code appears in diagnostics
    │     │     ├── Code absent AND L4 checks not run → score 0
    │     │     ├── Code absent AND L4 checks ran → score full points
    │     │     └── Code present → score 0
    │     └── No: Evaluate normally
    │
    ├── APD-004 / APD-005 (graduated, anti-pattern count):
    │     ├── Filter to evaluable patterns (exclude L4-dependent)
    │     ├── Count detected vs absent
    │     └── points = (absent / evaluable) × max_points
    │
    ├── APD-006 (binary, token distribution):
    │     ├── Read ParsedLlmsTxt.sections[].estimated_tokens
    │     ├── Any section > 40% of total? → 0 points
    │     └── All sections ≤ 40% → 2 points
    │
    ├── APD-007 (threshold, absolute URLs):
    │     ├── Calculate absolute_rate from diagnostics
    │     ├── rate ≥ 0.90 → 2 points
    │     └── rate < 0.90 → 0 points
    │
    └── Record in details[]
```

---

## 3. Implementation

```python
"""Implements v0.4.0d — Anti-Pattern Dimension Scorer."""

from docstratum.schema.constants import AntiPatternID
from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.quality import DimensionScore, QualityDimension
from docstratum.schema.validation import ValidationResult
from docstratum.scoring.registry import (
    CriterionMapping,
    ScoringMode,
    get_criteria_by_dimension,
)


# Anti-patterns with L4 dependencies (excluded from evaluable denominator)
L4_DEPENDENT_CONTENT_APS = {
    AntiPatternID.AP_CONT_003,  # Jargon Jungle
    AntiPatternID.AP_CONT_008,  # Meta-Documentation Spiral
}
L4_DEPENDENT_STRATEGIC_APS = {
    AntiPatternID.AP_STRAT_004,  # Preference Trap
}


def score_anti_pattern(
    result: ValidationResult,
    parsed: ParsedLlmsTxt,
    anti_pattern_results: dict | None = None,
) -> DimensionScore:
    """Score the anti-pattern dimension (20 points max).

    Evaluates 8 APD criteria (DS-VC-APD-001 through APD-008)
    against diagnostics and anti-pattern detection results.

    The parsed model is needed for APD-006 (token distribution),
    which is the single exception to the "read only ValidationResult" rule.

    Args:
        result: Validated file result from v0.3.x pipeline.
        parsed: Parsed llms.txt model (for APD-006 only).
        anti_pattern_results: Anti-pattern detection results from v0.3.4.

    Returns:
        DimensionScore with anti-pattern points and per-criterion details.

    Implements v0.4.0d. Grounding: DS-QS-DIM-APD, DECISION-016.
    """
    criteria = get_criteria_by_dimension(QualityDimension.ANTI_PATTERN)
    details: list[dict] = []
    total_points = 0.0
    passed = 0
    failed = 0

    for criterion in criteria:
        criterion_result = _evaluate_apd_criterion(
            criterion, result, parsed, anti_pattern_results or {}
        )
        details.append(criterion_result)
        total_points += criterion_result["points"]
        if criterion_result["passed"]:
            passed += 1
        else:
            failed += 1

    return DimensionScore(
        dimension=QualityDimension.ANTI_PATTERN,
        points=total_points,
        max_points=20.0,
        checks_passed=passed,
        checks_failed=failed,
        checks_total=len(criteria),
        details=details,
    )


def _evaluate_apd_criterion(
    criterion: CriterionMapping,
    result: ValidationResult,
    parsed: ParsedLlmsTxt,
    anti_pattern_results: dict,
) -> dict:
    """Evaluate a single APD criterion."""

    # L4-dependent criteria: score 0 if L4 codes not in diagnostics
    if criterion.l4_dependent:
        return _evaluate_l4_dependent(criterion, result)

    # APD-004 / APD-005: graduated anti-pattern count
    if criterion.anti_pattern_ids:
        return _evaluate_anti_pattern_count(
            criterion, anti_pattern_results
        )

    # APD-006: token distribution (reads ParsedLlmsTxt)
    if criterion.criterion_id == "DS-VC-APD-006":
        return _evaluate_token_distribution(criterion, parsed)

    # APD-007: absolute URL prevalence
    if criterion.criterion_id == "DS-VC-APD-007":
        return _evaluate_url_prevalence(criterion, result)

    # Default fallback
    return _default_detail(criterion)
```

---

## 4. Edge Cases

| Case                                  | Behavior                           | Rationale                                     |
| ------------------------------------- | ---------------------------------- | --------------------------------------------- |
| Pre-v0.9.0 (all L4 codes absent)      | APD-001–003, APD-008 score 0       | No credit for unverified features             |
| Post-v0.9.0 (L4 codes emitted)        | APD-001–003 auto-evaluate          | Code presence in diagnostics triggers scoring |
| File with 1 section (100% of tokens)  | APD-006 = 0 (single section > 40%) | Section dominance = fail                      |
| File with 0 sections                  | APD-006 = 2 (vacuously passes)     | No sections = no dominance                    |
| File with 0 URLs                      | APD-007 = 2 (vacuously passes)     | No URLs = vacuously all absolute              |
| All 7 evaluable content APs detected  | APD-004 = 0.0                      | `(0/7) × 3 = 0`                               |
| 3 of 7 evaluable content APs detected | APD-004 = `(4/7) × 3 = 1.71`       | Graduated proportional                        |
| Combined L4 ceiling                   | Maximum APD score = 9              | 11 points unavailable until v0.9.0            |

---

## 5. Deliverables

| File                                     | Description                |
| ---------------------------------------- | -------------------------- |
| `src/docstratum/scoring/anti_pattern.py` | Anti-pattern scorer module |
| `tests/scoring/test_anti_pattern.py`     | Unit tests                 |

---

## 6. Test Plan (14 tests)

| #   | Test Name                        | Input                                | Expected           |
| --- | -------------------------------- | ------------------------------------ | ------------------ |
| 1   | `test_maximum_score_with_l4`     | All L4 codes present, no APs         | 20.0 (full)        |
| 2   | `test_maximum_score_without_l4`  | Clean file, no L4 codes              | 9.0 (ceiling)      |
| 3   | `test_apd_001_scores_0_pre_l4`   | I001 not in diagnostics, L4 inactive | 0.0                |
| 4   | `test_apd_002_scores_0_pre_l4`   | I002 not in diagnostics              | 0.0                |
| 5   | `test_apd_003_scores_0_pre_l4`   | I003 not in diagnostics              | 0.0                |
| 6   | `test_apd_004_no_content_aps`    | 0 of 7 evaluable detected            | 3.0                |
| 7   | `test_apd_004_some_content_aps`  | 3 of 7 detected                      | `(4/7) × 3 ≈ 1.71` |
| 8   | `test_apd_005_no_strategic_aps`  | 0 of 3 evaluable detected            | 2.0                |
| 9   | `test_apd_005_all_strategic_aps` | 3 of 3 detected                      | 0.0                |
| 10  | `test_apd_006_balanced_tokens`   | No section > 40%                     | 2.0                |
| 11  | `test_apd_006_dominant_section`  | 1 section at 60% of total            | 0.0                |
| 12  | `test_apd_007_above_threshold`   | 95% absolute URLs                    | 2.0                |
| 13  | `test_apd_007_below_threshold`   | 80% absolute URLs                    | 0.0                |
| 14  | `test_apd_008_scores_0_pre_l4`   | I007 not in diagnostics, L4 inactive | 0.0                |
