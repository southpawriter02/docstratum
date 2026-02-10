# v0.3.5b — Diagnostic Aggregation

> **Version:** v0.3.5b
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.5-pipeline-assembly.md](RR-SPEC-v0.3.5-pipeline-assembly.md)
> **Depends On:** v0.1.2c (`ValidationResult`), v0.3.5a (pipeline)

---

## 1. Purpose

v0.3.5b implements the **aggregator** — the function that collects all diagnostics from the pipeline, determines `level_achieved`, and produces a fully populated `ValidationResult`.

### 1.1 What This Module Does NOT Do

| Responsibility                  | Owner  |
| ------------------------------- | ------ |
| Compute `QualityScore`          | v0.4.x |
| Format output (JSON, CLI table) | v0.8.x |
| Generate remediation plan       | v0.6.x |

### 1.2 User Story

> As a scorer, I want a `ValidationResult` with `level_achieved` and all diagnostics aggregated so that I can compute quality scores accurately.

---

## 2. `level_achieved` Logic

### 2.1 Decision Table

| L0 Pass | L1 Pass | L2 Pass | L3 Pass | `level_achieved`                                 |
| ------- | ------- | ------- | ------- | ------------------------------------------------ |
| ✗       | —       | —       | —       | `L0_PARSEABLE` (but `levels_passed[L0] = False`) |
| ✓       | ✗       | —       | —       | `L0_PARSEABLE`                                   |
| ✓       | ✓       | ✗       | —       | `L1_STRUCTURAL`                                  |
| ✓       | ✓       | ✓       | ✗       | `L2_CONTENT`                                     |
| ✓       | ✓       | ✓       | ✓       | `L3_BEST_PRACTICES`                              |

> **Important nuance:** When L0 fails, `level_achieved` is `L0_PARSEABLE` with `levels_passed[L0] = False`. This means the file was _tested at_ L0 but did not pass. The `is_valid` property returns `False` in this case.

### 2.2 Why Not L4?

L4 (`DOCSTRATUM_EXTENDED`) is out of scope for v0.3.x. It is never set by this pipeline. `levels_passed[L4]` defaults to `False` and is not modified.

---

## 3. Implementation

```python
"""Implements v0.3.5b — Diagnostic Aggregation."""

from datetime import datetime
from typing import Optional

from docstratum.schema.validation import (
    ValidationDiagnostic,
    ValidationLevel,
    ValidationResult,
)
from docstratum.validation.anti_patterns.detector import AntiPatternDetection


def aggregate_result(
    diagnostics: list[ValidationDiagnostic],
    levels_passed: dict[ValidationLevel, bool],
    anti_patterns: list[AntiPatternDetection],
    source_filename: str,
    validated_at: Optional[datetime] = None,
) -> ValidationResult:
    """Aggregate pipeline results into a ValidationResult.

    Determines level_achieved from levels_passed, attaches
    anti-pattern metadata, and populates all result fields.

    Args:
        diagnostics: All diagnostics from L0–L3 checks.
        levels_passed: Map of level → pass/fail from pipeline.
        anti_patterns: Detection results from v0.3.4.
        source_filename: Path of the validated file.
        validated_at: Timestamp (defaults to now).

    Returns:
        Fully populated ValidationResult.

    Implements v0.3.5b. Grounding: v0.1.2c (ValidationResult model).
    """
    level_achieved = _determine_level_achieved(levels_passed)

    # Ensure all levels are represented in levels_passed
    full_levels_passed = {level: False for level in ValidationLevel}
    full_levels_passed.update(levels_passed)

    # Attach anti-pattern metadata to relevant diagnostics
    _annotate_anti_pattern_diagnostics(diagnostics, anti_patterns)

    # Determine if any critical anti-pattern was detected
    critical_detected = any(
        ap.detected and ap.category.name == "CRITICAL"
        for ap in anti_patterns
    )

    return ValidationResult(
        level_achieved=level_achieved,
        diagnostics=diagnostics,
        levels_passed=full_levels_passed,
        source_filename=source_filename,
        validated_at=validated_at or datetime.now(),
    )


def _determine_level_achieved(
    levels_passed: dict[ValidationLevel, bool],
) -> ValidationLevel:
    """Determine the highest level where all checks passed.

    Walks the level hierarchy from L3 down to L0. Returns the
    highest level that passed. If L0 failed, returns L0 (with
    levels_passed[L0] = False indicating failure).
    """
    # Walk from highest to lowest
    ordered_levels = [
        ValidationLevel.L3_BEST_PRACTICES,
        ValidationLevel.L2_CONTENT,
        ValidationLevel.L1_STRUCTURAL,
        ValidationLevel.L0_PARSEABLE,
    ]

    for level in ordered_levels:
        if levels_passed.get(level, False):
            return level

    # Nothing passed — return L0 (with levels_passed[L0] = False)
    return ValidationLevel.L0_PARSEABLE


def _annotate_anti_pattern_diagnostics(
    diagnostics: list[ValidationDiagnostic],
    anti_patterns: list[AntiPatternDetection],
) -> None:
    """Annotate diagnostics with anti-pattern IDs where applicable.

    For each detected anti-pattern, find its constituent diagnostics
    and add anti_pattern_id to their context.
    """
    for ap in anti_patterns:
        if not ap.detected:
            continue

        for diag in diagnostics:
            if diag.code in ap.constituent_diagnostics:
                if "anti_patterns" not in diag.context:
                    diag.context["anti_patterns"] = []
                diag.context["anti_patterns"].append(str(ap.pattern_id))
```

### 3.1 Decision Tree

```
levels_passed dict received from pipeline
    │
    ├── Walk L3 → L2 → L1 → L0
    │     ├── L3 passed? → level_achieved = L3_BEST_PRACTICES
    │     ├── L2 passed? → level_achieved = L2_CONTENT
    │     ├── L1 passed? → level_achieved = L1_STRUCTURAL
    │     └── L0 passed? → level_achieved = L0_PARSEABLE
    │                       (levels_passed[L0] = True)
    │
    ├── Nothing passed? → level_achieved = L0_PARSEABLE
    │                      (levels_passed[L0] = False → is_valid = False)
    │
    ├── Attach anti-pattern annotations to diagnostics
    │
    └── Return ValidationResult
```

---

## 4. Edge Cases

| Case                                         | Behavior                                                         | Rationale                                            |
| -------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------- |
| L0 fails                                     | `level_achieved=L0`, `levels_passed[L0]=False`, `is_valid=False` | File cannot be parsed                                |
| All pass                                     | `level_achieved=L3`, all `True` except L4                        | Highest achievable in v0.3.x                         |
| L4                                           | Always `False`                                                   | Not implemented in v0.3.x                            |
| Empty diagnostics list                       | All levels pass                                                  | No errors means no failures                          |
| Anti-pattern with no constituent diagnostics | No annotations added                                             | Pattern detected via heuristic, not diagnostic codes |

---

## 5. Deliverables

| File                                      | Description        |
| ----------------------------------------- | ------------------ |
| `src/docstratum/validation/aggregator.py` | Aggregation module |
| `tests/validation/test_aggregator.py`     | Unit tests         |

---

## 6. Test Plan (10 tests)

| #   | Test Name                        | Input                    | Expected                                       |
| --- | -------------------------------- | ------------------------ | ---------------------------------------------- |
| 1   | `test_all_levels_pass`           | All True                 | `level_achieved=L3`                            |
| 2   | `test_l0_fails`                  | L0=False                 | `level_achieved=L0`, `is_valid=False`          |
| 3   | `test_l1_fails`                  | L0=True, L1=False        | `level_achieved=L0`                            |
| 4   | `test_l2_fails`                  | L0–L1=True, L2=False     | `level_achieved=L1`                            |
| 5   | `test_l3_fails`                  | L0–L2=True, L3=False     | `level_achieved=L2`                            |
| 6   | `test_l4_always_false`           | All True                 | `levels_passed[L4]=False`                      |
| 7   | `test_anti_pattern_annotations`  | CRIT-001 detected + E007 | E007 diagnostic has `anti_patterns` in context |
| 8   | `test_validated_at_populated`    | Any                      | `validated_at` is datetime                     |
| 9   | `test_source_filename_populated` | path="test.txt"          | `source_filename="test.txt"`                   |
| 10  | `test_empty_diagnostics`         | No diagnostics, all pass | `level_achieved=L3`, empty list                |
