# v0.3.5a — Level Sequencing & Gating

> **Version:** v0.3.5a
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.5-pipeline-assembly.md](RR-SPEC-v0.3.5-pipeline-assembly.md)
> **Depends On:** All check modules (v0.3.0–v0.3.3), anti-pattern detector (v0.3.4)

---

## 1. Purpose

v0.3.5a implements the **pipeline orchestrator** — the `validate_file()` function that sequences L0→L1→L2→L3 checks with gate-on-failure semantics, runs anti-pattern detection, and delegates to the aggregator (v0.3.5b) for result assembly.

### 1.1 Gate-on-Failure Semantics

The core invariant: **if any check at level N emits an ERROR-severity diagnostic, levels N+1 through L3 are skipped.** WARNING and INFO diagnostics do not block.

```
Level N checks complete
    │
    ├── ANY diagnostic with severity == ERROR?
    │     ├── Yes → levels_passed[N] = False
    │     │         SKIP levels N+1 ... L3
    │     │         PROCEED to anti-pattern detection
    │     │
    │     └── No  → levels_passed[N] = True
    │               PROCEED to level N+1
    │
    └── (After all applicable levels)
          → Run anti-pattern detection
          → Aggregate and return ValidationResult
```

### 1.2 User Story

> As a CLI user, I want to call `validate_file("llms.txt")` and get a complete `ValidationResult` without needing to orchestrate individual checks manually.

---

## 2. Public API

### 2.1 `validate_file()`

```python
"""Implements v0.3.5a — Validation Pipeline Orchestrator."""

from pathlib import Path
from typing import Union

from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.classification import DocumentClassification
from docstratum.schema.validation import (
    Severity,
    ValidationDiagnostic,
    ValidationLevel,
    ValidationResult,
)
from docstratum.validation.aggregator import aggregate_result
from docstratum.validation.anti_patterns.detector import AntiPatternDetector


# Type alias for check functions
CheckFunction = Callable[
    [ParsedLlmsTxt, DocumentClassification, FileMetadata],
    list[ValidationDiagnostic],
]


# Check registry: maps levels to their check functions
CHECK_REGISTRY: dict[ValidationLevel, list[CheckFunction]] = {
    # ... populated with all check functions from v0.3.0–v0.3.3
}

# Levels in pipeline order (L4 excluded from v0.3.x)
PIPELINE_LEVELS: list[ValidationLevel] = [
    ValidationLevel.L0_PARSEABLE,
    ValidationLevel.L1_STRUCTURAL,
    ValidationLevel.L2_CONTENT,
    ValidationLevel.L3_BEST_PRACTICES,
]


def validate_file(
    path: Union[str, Path],
    *,
    check_urls: bool = False,
    url_timeout: float = 5.0,
) -> ValidationResult:
    """Validate an llms.txt file through the L0–L3 pipeline.

    Executes all validation levels sequentially with gate-on-failure
    semantics. After level checks, runs anti-pattern detection on
    accumulated diagnostics.

    Args:
        path: Path to the llms.txt file to validate.
        check_urls: If True, enable URL reachability checking (L2).
            Default False (opt-in).
        url_timeout: Timeout in seconds for URL checks. Only used
            when check_urls=True. Default 5.0.

    Returns:
        ValidationResult with all diagnostics, level_achieved,
        and levels_passed map.

    Implements v0.3.5a. Grounding: DS-VL-L0 through DS-VL-L3.
    """
    # 1. Parse the file
    parsed, classification, file_meta = _load_and_parse(path)

    # 2. Run level checks with gating
    all_diagnostics: list[ValidationDiagnostic] = []
    levels_passed: dict[ValidationLevel, bool] = {}

    for level in PIPELINE_LEVELS:
        checks = CHECK_REGISTRY.get(level, [])
        level_diagnostics = _run_level(
            level, checks, parsed, classification, file_meta,
            check_urls=check_urls,
            url_timeout=url_timeout,
        )
        all_diagnostics.extend(level_diagnostics)

        # Gate: check for ERROR-severity diagnostics at this level
        has_errors = any(
            d.severity == Severity.ERROR for d in level_diagnostics
        )
        levels_passed[level] = not has_errors

        if has_errors:
            # Mark remaining levels as not passed, skip execution
            for remaining in PIPELINE_LEVELS[
                PIPELINE_LEVELS.index(level) + 1 :
            ]:
                levels_passed[remaining] = False
            break

    # 3. Anti-pattern detection (always runs)
    detector = AntiPatternDetector()
    anti_patterns = detector.detect_all(all_diagnostics, parsed)

    # 4. Aggregate
    return aggregate_result(
        diagnostics=all_diagnostics,
        levels_passed=levels_passed,
        anti_patterns=anti_patterns,
        source_filename=str(path),
    )


def _run_level(
    level: ValidationLevel,
    checks: list[CheckFunction],
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
    *,
    check_urls: bool = False,
    url_timeout: float = 5.0,
) -> list[ValidationDiagnostic]:
    """Execute all checks for a single level.

    Handles the special case of L2 checks that accept check_urls
    and url_timeout parameters (v0.3.2b).
    """
    diagnostics: list[ValidationDiagnostic] = []

    for check_fn in checks:
        # v0.3.2b check_url_validation accepts extra kwargs
        if _accepts_url_params(check_fn):
            result = check_fn(
                parsed, classification, file_meta,
                check_urls=check_urls,
                url_timeout=url_timeout,
            )
        else:
            result = check_fn(parsed, classification, file_meta)

        diagnostics.extend(result)

    return diagnostics


def _accepts_url_params(check_fn: CheckFunction) -> bool:
    """Check if a function accepts check_urls parameter."""
    import inspect
    sig = inspect.signature(check_fn)
    return "check_urls" in sig.parameters


def _load_and_parse(path: Union[str, Path]):
    """Load and parse the file. Returns (parsed, classification, file_meta)."""
    from docstratum.parser import parse_file
    return parse_file(Path(path))
```

### 2.2 Decision Tree

```
validate_file(path) called
    │
    ├── Parse file → parsed, classification, file_meta
    │
    ├── L0 checks (7 functions)
    │     ├── Any ERROR? → levels_passed = {L0: False, L1–L3: False}
    │     │                → SKIP to anti-pattern detection
    │     └── No ERROR  → levels_passed[L0] = True → Continue
    │
    ├── L1 checks (4 functions)
    │     ├── Any ERROR? → levels_passed = {L0: True, L1: False, L2–L3: False}
    │     │                → SKIP to anti-pattern detection
    │     └── No ERROR  → levels_passed[L1] = True → Continue
    │
    ├── L2 checks (4 functions, check_urls passed to v0.3.2b)
    │     ├── Any ERROR? → levels_passed = {L0–L1: True, L2: False, L3: False}
    │     │                → SKIP to anti-pattern detection
    │     └── No ERROR  → levels_passed[L2] = True → Continue
    │
    ├── L3 checks (5 functions)
    │     └── levels_passed[L3] = True (always — L3 has no ERRORs)
    │
    ├── Anti-pattern detection (4 detectors)
    │     └── anti_patterns = detect_all(all_diagnostics, parsed)
    │
    └── Aggregate → ValidationResult
```

---

## 3. Edge Cases

| Case                         | Behavior                   | Rationale                              |
| ---------------------------- | -------------------------- | -------------------------------------- |
| Empty file (E007)            | L0 fails, L1–L3 skipped    | E007 is ERROR severity                 |
| File with only warnings      | All levels pass            | WARNINGs don't block                   |
| `check_urls=False` (default) | L2 E006 never emitted      | URL check gated by parameter           |
| Parse failure                | Depends on parser behavior | Pipeline wraps parse errors gracefully |
| Non-existent file            | `FileNotFoundError` raised | Caller responsible for path validation |
| L3 always passes             | By design                  | L3 has zero ERROR-severity codes       |

---

## 4. Deliverables

| File                                    | Description                  |
| --------------------------------------- | ---------------------------- |
| `src/docstratum/validation/pipeline.py` | Pipeline orchestrator        |
| `src/docstratum/validation/__init__.py` | Public API (`validate_file`) |
| `tests/validation/test_pipeline.py`     | Unit tests                   |

---

## 5. Test Plan (10 tests)

| #   | Test Name                                 | Input                            | Expected                                    |
| --- | ----------------------------------------- | -------------------------------- | ------------------------------------------- |
| 1   | `test_l0_failure_skips_l1_l3`             | File with E007                   | Only L0 diagnostics; L1–L3 checks not run   |
| 2   | `test_l1_failure_skips_l2_l3`             | File that passes L0, fails L1    | L0+L1 diagnostics; L2–L3 not run            |
| 3   | `test_l2_failure_skips_l3`                | File that passes L0+L1, fails L2 | L0+L1+L2 diagnostics; L3 not run            |
| 4   | `test_all_levels_pass`                    | Clean file                       | All levels pass; L3 included                |
| 5   | `test_warnings_dont_block`                | File with only WARNINGs          | All levels pass                             |
| 6   | `test_anti_patterns_run_after_l0_failure` | Empty file                       | Anti-patterns include Ghost File (CRIT-001) |
| 7   | `test_anti_patterns_run_after_all_pass`   | Clean file                       | Anti-patterns all `detected=False`          |
| 8   | `test_check_urls_passed_through`          | `check_urls=True`                | L2 URL check executes                       |
| 9   | `test_check_urls_default_false`           | Default call                     | L2 URL check skipped                        |
| 10  | `test_validate_file_returns_result`       | Any file                         | Returns `ValidationResult` instance         |
