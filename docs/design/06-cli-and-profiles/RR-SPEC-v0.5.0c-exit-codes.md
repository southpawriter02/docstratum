# v0.5.0c — Exit Codes

> **Version:** v0.5.0c
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.5.0-cli-foundation.md](RR-SPEC-v0.5.0-cli-foundation.md)
> **Grounding:** RR-SPEC-v0.1.3-output-tier-specification.md §2.1.1 (Process exit codes), RR-SCOPE-v0.5.x §4.3
> **Depends On:** v0.5.0b (`CliArgs.strict`, `CliArgs.pass_threshold`), v0.3.x (`ValidationResult`), v0.4.x (`QualityScore`)
> **Module:** `src/docstratum/cli_exit_codes.py`
> **Tests:** `tests/test_cli_exit_codes.py`

---

## 1. Purpose

Map pipeline results to process exit codes. This module is the bridge between DocStratum's internal result models (`ValidationResult`, `QualityScore`) and the OS-level exit code that CI pipelines and shell scripts depend on.

### 1.1 User Story

> As a CI pipeline operator, I want `docstratum validate` to exit with code 0 when the file passes and a specific non-zero code when it fails, so that I can write conditional logic like `if docstratum validate llms.txt; then deploy; fi`.

> As a developer, I want distinct exit codes for different failure categories (structural vs. content vs. score threshold) so that I can diagnose issues without reading the full output.

---

## 2. Exit Code Table

| Code | Name | Condition | Severity | Precedence |
|------|------|-----------|----------|------------|
| **0** | `PASS` | No errors AND (no threshold OR score ≥ threshold) | — | Lowest |
| **1** | `STRUCTURAL_ERRORS` | `total_errors > 0` at L0 or L1 | ERROR | 1st (highest) |
| **2** | `CONTENT_ERRORS` | `total_errors > 0` at L2 or L3 | ERROR | 2nd |
| **3** | `WARNINGS_STRICT` | `total_warnings > 0` AND `--strict` | WARNING (promoted) | 3rd |
| **4** | `ECOSYSTEM_ERRORS` | Ecosystem-level failures (v0.7.x) | ERROR | 4th |
| **5** | `SCORE_BELOW_THRESHOLD` | `score.total_score < pass_threshold` | — | 5th |
| **10** | `PIPELINE_ERROR` | Unhandled exception, file-not-found, invalid input | FATAL | Override |

> **Grounding:** These codes are defined in RR-SPEC-v0.1.3-output-tier-specification.md §2.1.1. The enumeration here is authoritative for the CLI implementation.

### 2.1 Precedence Rules

Exit codes are evaluated in precedence order (highest first). The **first matching** condition determines the exit code:

```
1. PIPELINE_ERROR (10)  — always overrides (exception handler)
2. STRUCTURAL_ERRORS (1) — L0/L1 errors found
3. CONTENT_ERRORS (2)    — L2/L3 errors found
4. WARNINGS_STRICT (3)   — warnings exist + --strict
5. ECOSYSTEM_ERRORS (4)  — reserved for v0.7.x
6. SCORE_BELOW_THRESHOLD (5) — score < threshold
7. PASS (0)               — everything else
```

**Key insight:** A file can simultaneously have structural errors, content errors, warnings, AND a low score. The exit code represents the **most severe** condition.

---

## 3. Implementation

```python
"""Exit code mapping for the DocStratum CLI.

Maps ValidationResult and QualityScore to process exit codes (0–10)
following the precedence rules in RR-SPEC-v0.1.3-output-tier-specification.md §2.1.1.

Implements v0.5.0c.
"""

from enum import IntEnum
from typing import Optional

from docstratum.schema.validation import (
    ValidationDiagnostic,
    ValidationLevel,
    ValidationResult,
)
from docstratum.schema.diagnostics import Severity
from docstratum.schema.quality import QualityScore


class ExitCode(IntEnum):
    """Process exit codes for `docstratum validate`.

    Codes are ordered by precedence (lower value = higher precedence
    for error categories). PIPELINE_ERROR (10) always overrides.

    Grounding: RR-SPEC-v0.1.3-output-tier-specification.md §2.1.1.
    Implements v0.5.0c.
    """

    PASS = 0
    STRUCTURAL_ERRORS = 1
    CONTENT_ERRORS = 2
    WARNINGS_STRICT = 3
    ECOSYSTEM_ERRORS = 4
    SCORE_BELOW_THRESHOLD = 5
    PIPELINE_ERROR = 10


def compute_exit_code(
    result: ValidationResult,
    score: Optional[QualityScore] = None,
    *,
    strict: bool = False,
    pass_threshold: Optional[int] = None,
) -> ExitCode:
    """Compute the process exit code from pipeline results.

    Evaluates conditions in precedence order and returns the
    first matching exit code.

    Args:
        result: Validation pipeline result with diagnostics.
        score: Quality score (may be None if scoring was skipped).
        strict: If True, treat warnings as errors (exit code 3).
        pass_threshold: Minimum score to pass (0–100). If set and
            score is below threshold, exit code is 5.

    Returns:
        ExitCode enum member.

    Implements v0.5.0c.
    Grounding: precedence table in §2 of this spec.
    """
    # Check 1: Structural errors (L0/L1)
    if _has_errors_at_levels(result, {ValidationLevel.L0_PARSEABLE, ValidationLevel.L1_STRUCTURAL}):
        return ExitCode.STRUCTURAL_ERRORS

    # Check 2: Content errors (L2/L3)
    if _has_errors_at_levels(result, {ValidationLevel.L2_CONTENT, ValidationLevel.L3_BEST_PRACTICES}):
        return ExitCode.CONTENT_ERRORS

    # Check 3: Warnings in strict mode
    if strict and _has_warnings(result):
        return ExitCode.WARNINGS_STRICT

    # Check 4: Ecosystem errors (reserved for v0.7.x)
    # Not evaluated at v0.5.0 — no ecosystem pipeline exists

    # Check 5: Score below threshold
    if (
        pass_threshold is not None
        and score is not None
        and score.total_score < pass_threshold
    ):
        return ExitCode.SCORE_BELOW_THRESHOLD

    return ExitCode.PASS


def _has_errors_at_levels(
    result: ValidationResult,
    levels: set[ValidationLevel],
) -> bool:
    """Check if any ERROR-severity diagnostics exist at the given levels.

    Args:
        result: Validation result containing diagnostics.
        levels: Set of validation levels to check.

    Returns:
        True if at least one ERROR diagnostic matches.
    """
    return any(
        d.severity == Severity.ERROR and d.level in levels
        for d in result.diagnostics
    )


def _has_warnings(result: ValidationResult) -> bool:
    """Check if any WARNING-severity diagnostics exist.

    Args:
        result: Validation result containing diagnostics.

    Returns:
        True if at least one WARNING diagnostic exists.
    """
    return any(
        d.severity == Severity.WARNING
        for d in result.diagnostics
    )
```

---

## 4. Decision Tree

```
Pipeline completes (result + score available)
│
├── Any exception during pipeline?
│     └── YES → PIPELINE_ERROR (10) — caught at top level in cli.py
│
├── Any ERROR diagnostics at L0 or L1?
│     └── YES → STRUCTURAL_ERRORS (1)
│                Example: E001_MISSING_H1, E003_INVALID_ENCODING
│
├── Any ERROR diagnostics at L2 or L3?
│     └── YES → CONTENT_ERRORS (2)
│                Example: E010_EMPTY_DESCRIPTION, E006_BROKEN_LINK
│
├── --strict AND any WARNING diagnostics?
│     └── YES → WARNINGS_STRICT (3)
│                Example: W001_MISSING_BLOCKQUOTE, W008_SECTION_ORDER
│
├── Ecosystem errors? (v0.7.x only)
│     └── Not evaluated at v0.5.0
│
├── --pass-threshold set AND score < threshold?
│     └── YES → SCORE_BELOW_THRESHOLD (5)
│                Example: score=42, threshold=50
│
└── None of the above?
      └── PASS (0)
```

---

## 5. Edge Cases

| Scenario | Exit Code | Rationale |
|----------|-----------|-----------|
| L0 errors AND L2 errors | 1 (STRUCTURAL) | Structural > content in precedence |
| L2 errors AND warnings (strict) | 2 (CONTENT) | Content errors > strict warnings |
| Warnings only (not strict) | 0 (PASS) | Warnings are advisory without --strict |
| Score below threshold AND L0 errors | 1 (STRUCTURAL) | Errors always outrank threshold |
| Score below threshold, no errors | 5 (THRESHOLD) | Threshold is the only failing condition |
| No score available + threshold set | 0 (PASS) | Can't fail a threshold check without a score |
| Empty diagnostics list | 0 (PASS) | Clean file |
| All diagnostics are INFO severity | 0 (PASS) | INFO never affects exit code |
| Anti-pattern diagnostics (ERROR) at L3 | 2 (CONTENT) | L3 = content quality level |

---

## 6. Acceptance Criteria

- [ ] `ExitCode` enum defines all 7 codes (0, 1, 2, 3, 4, 5, 10)
- [ ] `compute_exit_code()` returns `STRUCTURAL_ERRORS` when L0/L1 errors exist
- [ ] `compute_exit_code()` returns `CONTENT_ERRORS` when L2/L3 errors exist (no L0/L1 errors)
- [ ] `compute_exit_code()` returns `WARNINGS_STRICT` when `strict=True` and warnings exist (no errors)
- [ ] `compute_exit_code()` returns `SCORE_BELOW_THRESHOLD` when score < threshold (no errors/warnings)
- [ ] `compute_exit_code()` returns `PASS` when no errors, no warnings (or not strict), and score above threshold
- [ ] Precedence is enforced: structural > content > warnings > ecosystem > threshold > pass
- [ ] `score=None` does not cause an exception when threshold is set
- [ ] Module docstring cites v0.5.0c and grounding spec

---

## 7. Deliverables

| File | Description | Status |
|------|-------------|--------|
| `src/docstratum/cli_exit_codes.py` | Exit code enum and compute function | NEW |
| `tests/test_cli_exit_codes.py` | Unit tests (100% coverage target) | NEW |

---

## 8. Test Plan (12 tests)

| # | Test Name | Input | Expected |
|---|-----------|-------|----------|
| 1 | `test_clean_file_passes` | No diagnostics, no threshold | ExitCode.PASS (0) |
| 2 | `test_l0_error_structural` | E003 diagnostic at L0 | ExitCode.STRUCTURAL_ERRORS (1) |
| 3 | `test_l1_error_structural` | E001 diagnostic at L1 | ExitCode.STRUCTURAL_ERRORS (1) |
| 4 | `test_l2_error_content` | E010 diagnostic at L2 | ExitCode.CONTENT_ERRORS (2) |
| 5 | `test_l3_error_content` | E006 diagnostic at L3 | ExitCode.CONTENT_ERRORS (2) |
| 6 | `test_warnings_not_strict` | W001 diagnostic, strict=False | ExitCode.PASS (0) |
| 7 | `test_warnings_strict` | W001 diagnostic, strict=True | ExitCode.WARNINGS_STRICT (3) |
| 8 | `test_score_below_threshold` | score=42, threshold=50, no errors | ExitCode.SCORE_BELOW_THRESHOLD (5) |
| 9 | `test_score_above_threshold` | score=80, threshold=50, no errors | ExitCode.PASS (0) |
| 10 | `test_precedence_structural_over_content` | L0 error + L2 error | ExitCode.STRUCTURAL_ERRORS (1) |
| 11 | `test_precedence_content_over_threshold` | L2 error + score below threshold | ExitCode.CONTENT_ERRORS (2) |
| 12 | `test_no_score_with_threshold` | score=None, threshold=50 | ExitCode.PASS (0) |

```python
"""Tests for v0.5.0c — Exit Codes.

Full coverage of the compute_exit_code() function and the
ExitCode enum. Target: 100% coverage.

Implements v0.5.0c test plan.
"""

import pytest

from docstratum.cli_exit_codes import ExitCode, compute_exit_code
from docstratum.schema.diagnostics import DiagnosticCode, Severity
from docstratum.schema.validation import (
    ValidationDiagnostic,
    ValidationLevel,
    ValidationResult,
)
from docstratum.schema.quality import QualityScore


def _make_result(diagnostics: list[ValidationDiagnostic] | None = None) -> ValidationResult:
    """Create a minimal ValidationResult for testing."""
    return ValidationResult(
        diagnostics=diagnostics or [],
        level_achieved=ValidationLevel.L3_BEST_PRACTICES,
        levels_passed=[],
        total_errors=sum(1 for d in (diagnostics or []) if d.severity == Severity.ERROR),
        total_warnings=sum(1 for d in (diagnostics or []) if d.severity == Severity.WARNING),
    )


def _make_diagnostic(
    severity: Severity,
    level: ValidationLevel,
) -> ValidationDiagnostic:
    """Create a minimal ValidationDiagnostic for testing."""
    return ValidationDiagnostic(
        code=DiagnosticCode.E001_MISSING_H1,  # arbitrary code
        severity=severity,
        message="Test diagnostic",
        remediation="Fix it",
        level=level,
        check_id="TEST-001",
    )


def _make_score(total: float) -> QualityScore:
    """Create a minimal QualityScore for testing."""
    return QualityScore(total_score=total, grade="B", dimensions=[])


def test_clean_file_passes():
    result = _make_result([])
    assert compute_exit_code(result) == ExitCode.PASS


def test_l0_error_structural():
    diag = _make_diagnostic(Severity.ERROR, ValidationLevel.L0_PARSEABLE)
    result = _make_result([diag])
    assert compute_exit_code(result) == ExitCode.STRUCTURAL_ERRORS


def test_warnings_not_strict():
    diag = _make_diagnostic(Severity.WARNING, ValidationLevel.L1_STRUCTURAL)
    result = _make_result([diag])
    assert compute_exit_code(result, strict=False) == ExitCode.PASS


def test_warnings_strict():
    diag = _make_diagnostic(Severity.WARNING, ValidationLevel.L1_STRUCTURAL)
    result = _make_result([diag])
    assert compute_exit_code(result, strict=True) == ExitCode.WARNINGS_STRICT


def test_score_below_threshold():
    result = _make_result([])
    score = _make_score(42.0)
    assert compute_exit_code(result, score, pass_threshold=50) == ExitCode.SCORE_BELOW_THRESHOLD


def test_precedence_structural_over_content():
    d1 = _make_diagnostic(Severity.ERROR, ValidationLevel.L0_PARSEABLE)
    d2 = _make_diagnostic(Severity.ERROR, ValidationLevel.L2_CONTENT)
    result = _make_result([d1, d2])
    assert compute_exit_code(result) == ExitCode.STRUCTURAL_ERRORS
```
