# v0.4.2 — Scoring Calibration & Testing

> **Version:** v0.4.2
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.4.x-quality-scoring.md](RR-SCOPE-v0.4.x-quality-scoring.md)
> **Depends On:** v0.4.0 (dimension scorers), v0.4.1 (composite pipeline), v0.3.5d (calibration specimens)
> **Consumed By:** v0.5.x (CLI), v0.6.x (remediation), v0.8.x (reports) — all consume `QualityScore` validated by these tests

---

## 1. Purpose

v0.4.2 is the **confidence sub-version** — it proves the scoring engine works correctly before downstream phases depend on it. It does not add production logic; it validates the logic built in v0.4.0 and v0.4.1.

### 1.1 What v0.4.2 Provides

| Before v0.4.2                       | After v0.4.2                                               |
| ----------------------------------- | ---------------------------------------------------------- |
| Scoring code exists but is untested | ≥90% coverage, all 30 criteria individually verified       |
| No confidence in grade boundaries   | Every threshold (29/30, 49/50, 69/70, 89/90) tested        |
| No gold standard validation         | 6 calibration specimens scored with ±3 tolerance baselines |
| No regression protection            | JSON fixture baselines for CI enforcement                  |

### 1.2 Data Flow

```
v0.4.2a ──► Test v0.4.0b/c/d dimension scorers in isolation
              │
v0.4.2b ──► Test v0.4.1a–d composite pipeline in isolation
              │
v0.4.2c ──► End-to-end: validate_file() → score_file() on 6 specimens
              │
v0.4.2d ──► Boundary cases + record JSON regression baselines
              │
              ▼
         CI passes: pytest --cov=docstratum.scoring --cov-fail-under=90
```

### 1.3 User Stories

| ID     | As a...             | I want to...                                             | So that...                              |
| ------ | ------------------- | -------------------------------------------------------- | --------------------------------------- |
| US-420 | developer           | know that each criterion scores correctly in isolation   | I can trust per-criterion results       |
| US-421 | developer           | see that gating, grading, and detail population all work | the composite pipeline is reliable      |
| US-422 | QA engineer         | validate scores against 6 real-world files               | the engine produces correct assessments |
| US-423 | CI/CD pipeline      | enforce ≥90% coverage and regression baselines           | regressions are caught automatically    |
| US-424 | downstream consumer | trust that `QualityScore` output is correct and stable   | v0.5.x+ can safely depend on it         |

---

## 2. Architecture

### 2.1 Test Module Structure

```
tests/scoring/
├── conftest.py                    # Shared fixtures for scoring tests
├── test_registry.py               # v0.4.0a — Registry unit tests (11 tests)
├── test_structural.py             # v0.4.2a — Structural scorer tests
├── test_content.py                # v0.4.2a — Content scorer tests
├── test_anti_pattern.py           # v0.4.2a — Anti-pattern scorer tests
├── test_composite.py              # v0.4.2b — Composite pipeline tests
├── test_calibration_scoring.py    # v0.4.2c — Calibration specimen scoring
├── test_boundary_regression.py    # v0.4.2d — Boundary & regression tests
└── fixtures/
    ├── expected_scores/           # JSON regression baselines
    │   ├── ds-cs-001-svelte.json
    │   ├── ds-cs-002-pydantic.json
    │   ├── ds-cs-003-vercel-ai-sdk.json
    │   ├── ds-cs-004-shadcn-ui.json
    │   ├── ds-cs-005-cursor.json
    │   └── ds-cs-006-nvidia.json
    └── mock_results/              # Synthetic ValidationResult fixtures
        ├── perfect_result.json
        ├── zero_result.json
        ├── l0_failure_result.json
        └── gated_result.json
```

### 2.2 Design Decision: Separate Test Files per Sub-Part

| Approach                                         | Chosen? | Rationale                                                    |
| ------------------------------------------------ | ------- | ------------------------------------------------------------ |
| **Separate test files per scoring module**       | **Yes** | Matches source module structure; easy to run in isolation    |
| Single monolithic test file                      | No      | Too large; hard to navigate; harder to parallelize           |
| Test files grouped by test type (boundary, etc.) | No      | Doesn't match source module organization; harder to maintain |

### 2.3 Fixture Strategy

Tests use **two fixture types**:

1. **Mock `ValidationResult` instances** — constructed programmatically with specific diagnostic combinations. Used for unit tests (v0.4.2a, v0.4.2b) to isolate scoring logic from the validation pipeline.
2. **Real calibration specimens** — the 6 files from `tests/fixtures/calibration/` (captured in v0.3.5d). Used for integration tests (v0.4.2c) that run the full `validate_file() → score_file()` pipeline.

```python
# conftest.py — Shared scoring fixtures

import pytest
from docstratum.schema.validation import (
    ValidationResult,
    ValidationDiagnostic,
    ValidationLevel,
)
from docstratum.schema.diagnostics import DiagnosticCode, Severity


@pytest.fixture
def clean_validation_result() -> ValidationResult:
    """A ValidationResult with zero diagnostics (perfect file)."""
    return ValidationResult(
        level_achieved=ValidationLevel.L3_BEST_PRACTICES,
        diagnostics=[],
        levels_passed={
            ValidationLevel.L0_PARSEABLE: True,
            ValidationLevel.L1_STRUCTURAL: True,
            ValidationLevel.L2_CONTENT: True,
            ValidationLevel.L3_BEST_PRACTICES: True,
            ValidationLevel.L4_DOCSTRATUM_EXTENDED: False,
        },
        source_filename="test.txt",
    )


@pytest.fixture
def l0_failure_result() -> ValidationResult:
    """A ValidationResult where L0 failed (gate-on-failure)."""
    return ValidationResult(
        level_achieved=ValidationLevel.L0_PARSEABLE,
        diagnostics=[
            ValidationDiagnostic(
                code=DiagnosticCode.E007_EMPTY_FILE,
                severity=Severity.ERROR,
                message="File is empty.",
                level=ValidationLevel.L0_PARSEABLE,
            ),
        ],
        levels_passed={
            ValidationLevel.L0_PARSEABLE: False,
            ValidationLevel.L1_STRUCTURAL: False,
            ValidationLevel.L2_CONTENT: False,
            ValidationLevel.L3_BEST_PRACTICES: False,
            ValidationLevel.L4_DOCSTRATUM_EXTENDED: False,
        },
        source_filename="empty.txt",
    )


def make_diagnostic(
    code: DiagnosticCode,
    severity: Severity | None = None,
    level: ValidationLevel = ValidationLevel.L1_STRUCTURAL,
    check_id: str | None = None,
) -> ValidationDiagnostic:
    """Helper to create a ValidationDiagnostic with minimal boilerplate."""
    if severity is None:
        severity = (
            Severity.ERROR if code.value.startswith("E")
            else Severity.WARNING if code.value.startswith("W")
            else Severity.INFO
        )
    return ValidationDiagnostic(
        code=code,
        severity=severity,
        message=f"Test diagnostic: {code.value}",
        level=level,
        check_id=check_id,
    )
```

---

## 3. Sub-Part Breakdown

| Sub-Part                                           | Title                    | Test Count | Primary Scope               |
| -------------------------------------------------- | ------------------------ | ---------- | --------------------------- |
| [v0.4.2a](RR-SPEC-v0.4.2a-dimension-unit-tests.md) | Dimension Scorer Tests   | ~50        | v0.4.0b/c/d per-criterion   |
| [v0.4.2b](RR-SPEC-v0.4.2b-composite-unit-tests.md) | Composite Pipeline Tests | ~30        | v0.4.1a–d integration       |
| [v0.4.2c](RR-SPEC-v0.4.2c-calibration-scoring.md)  | Calibration Scoring      | ~18        | 6 specimens × 3 assertions  |
| [v0.4.2d](RR-SPEC-v0.4.2d-boundary-regression.md)  | Boundary & Regression    | ~16        | Edge cases + JSON baselines |

**Total tests: ~114** (across all test files).

### 3.1 Dependency Chain

```
v0.4.2a (dimension tests) ──► Tests v0.4.0b/c/d in isolation
    │                          Uses mock ValidationResult fixtures
    │                          Can develop alongside v0.4.0
    │
v0.4.2b (composite tests) ──► Tests v0.4.1a–d in isolation
    │                          Uses mock DimensionScore fixtures
    │                          Can develop alongside v0.4.1
    │
v0.4.2c (calibration)     ──► Requires v0.4.1 complete
    │                          Requires v0.3.x operational
    │                          Uses real calibration specimens
    │
v0.4.2d (regression)       ──► Requires v0.4.1 complete
                               Records JSON baselines for CI
```

> **Parallelization:** v0.4.2a can be written alongside v0.4.0 (after each dimension scorer is done, its tests can be written). v0.4.2b can be written alongside v0.4.1. v0.4.2c and v0.4.2d require the complete pipeline and must be written last.

---

## 4. Exit Criteria

### 4.1 Functional

- [ ] Each of the 30 scoring criteria has at least 1 dedicated test verifying correct point calculation.
- [ ] All 3 scoring modes (BINARY, GRADUATED, THRESHOLD) are tested.
- [ ] Graduated scoring float precision is verified (fractional points, not rounded to int).
- [ ] L4-dependent criteria (APD-001–003, APD-008) verified to score 0 when L4 codes absent.
- [ ] Composite calculation verified: sum of dimension points = total_score.
- [ ] Gating tested: each of the 4 AP-CRIT triggers independently caps at 29.
- [ ] Grade boundaries tested: exact thresholds at 29/30, 49/50, 69/70, 89/90.
- [ ] Float rounding at grade boundaries verified (89.5 → EXEMPLARY via `round()`).
- [ ] 6 calibration specimens produce scores within L4-adjusted ±3 tolerance.
- [ ] Quality ordering: Svelte ≥ Pydantic ≥ Vercel ≥ Shadcn > Cursor > NVIDIA.
- [ ] NVIDIA triggers gating; Cursor does not.
- [ ] JSON regression baselines recorded for all 6 specimens.

### 4.2 Non-Functional

- [ ] `pytest --cov=docstratum.scoring --cov-fail-under=90` passes.
- [ ] `black --check` and `ruff check` pass on all test files.
- [ ] No test depends on network access (calibration specimens are local fixtures).
- [ ] All tests execute in <5 seconds total (pure computation, no I/O).
- [ ] Tests are idempotent — running twice produces identical results.

### 4.3 CI Integration

- [ ] The `--cov-fail-under=90` threshold is enforced in CI.
- [ ] Regression baselines can be updated with a `--update-baselines` flag.
- [ ] Test failures produce clear diagnostic messages identifying which criterion or specimen failed.

---

## 5. Dependencies

| Module                        | What v0.4.2 Uses                                                                              |
| ----------------------------- | --------------------------------------------------------------------------------------------- |
| `scoring/registry.py`         | `CRITERIA_REGISTRY`, `get_criteria_by_dimension()`                                            |
| `scoring/structural.py`       | `score_structural()` — tested in v0.4.2a                                                      |
| `scoring/content.py`          | `score_content()` — tested in v0.4.2a                                                         |
| `scoring/anti_pattern.py`     | `score_anti_pattern()` — tested in v0.4.2a                                                    |
| `scoring/composite.py`        | `score_file()`, `compute_composite()`, `apply_gating()`, `assign_grade()`, `enrich_details()` |
| `schema/validation.py`        | `ValidationResult`, `ValidationDiagnostic`, `ValidationLevel`                                 |
| `schema/quality.py`           | `QualityScore`, `QualityGrade`, `DimensionScore`, `QualityDimension`                          |
| `schema/diagnostics.py`       | `DiagnosticCode`, `Severity`                                                                  |
| `schema/constants.py`         | `AntiPatternID`, `AntiPatternCategory`                                                        |
| `schema/parsed.py`            | `ParsedLlmsTxt` (for APD-006 token distribution tests)                                        |
| `tests/fixtures/calibration/` | 6 specimen files from v0.3.5d                                                                 |

---

## 6. Design Decisions

| Decision                                                        | Choice | Rationale                                                         |
| --------------------------------------------------------------- | ------ | ----------------------------------------------------------------- |
| Separate test files per scoring module                          | Yes    | Mirrors source structure; easy selective execution                |
| Mock ValidationResults for unit tests (not fixture files)       | Yes    | Deterministic; no file parsing overhead; exact diagnostic control |
| Real specimens only for calibration integration tests (v0.4.2c) | Yes    | Full pipeline validation requires real files                      |
| ±3 tolerance on calibration scores (with L4 adjustment)         | Yes    | Scope doc specification; accounts for minor scoring drift         |
| JSON regression baselines (not hardcoded assertions)            | Yes    | Diffable, versionable, updatable without code changes             |
| Shared conftest.py with helper factories                        | Yes    | Reduces boilerplate across 6 test files                           |
| L4-adjusted expected ranges (not raw reference values)          | Yes    | Honest: L4 ceiling means top scores are ~11 pts lower at v0.4.x   |

---

## 7. L4 Ceiling Adjustment for Calibration

### 7.1 The Problem

The scope doc's expected calibration scores (Svelte: 92, Pydantic: 90, etc.) were calibrated **assuming all 30 criteria are evaluable**. At v0.4.x, 4 L4-dependent APD criteria score 0:

| Criterion | Points Lost |
| --------- | ----------- |
| APD-001   | 3           |
| APD-002   | 3           |
| APD-003   | 3           |
| APD-008   | 2           |
| **Total** | **11**      |

### 7.2 Adjusted Expected Scores

The adjustment is **not** a flat −11 because some specimens may not have earned full APD points even if L4 were active. The adjustment per specimen:

| Specimen      | Ref Score | L4 Adjustment | v0.4.x Expected | v0.4.x Grade | Tolerance |
| ------------- | --------- | ------------- | --------------- | ------------ | --------- |
| Svelte        | 92        | −11           | 81              | STRONG       | ±3        |
| Pydantic      | 90        | −11           | 79              | STRONG       | ±3        |
| Vercel AI SDK | 90        | −11           | 79              | STRONG       | ±3        |
| Shadcn UI     | 89        | −11           | 78              | STRONG       | ±3        |
| Cursor        | 42        | −6 (partial)  | 36              | NEEDS_WORK   | ±3        |
| NVIDIA        | 24        | −2 (partial)  | 22              | CRITICAL     | ±3        |

> **Note:** Cursor and NVIDIA adjustments are smaller because they would not have earned max APD points even with L4 active (poor-quality files lack LLM instructions, concept definitions, etc.).

### 7.3 Grade Assertions at v0.4.x

| Specimen      | Expected Grade at v0.4.x | Notes                          |
| ------------- | ------------------------ | ------------------------------ |
| Svelte        | STRONG                   | Cannot reach EXEMPLARY         |
| Pydantic      | STRONG                   | Cannot reach EXEMPLARY         |
| Vercel AI SDK | STRONG                   | Cannot reach EXEMPLARY         |
| Shadcn UI     | STRONG                   | Cannot reach EXEMPLARY         |
| Cursor        | NEEDS_WORK               | Same grade as full calibration |
| NVIDIA        | CRITICAL                 | Gating triggered               |

---

## 8. Sub-Part Specifications

- [v0.4.2a — Dimension Scorer Unit Tests](RR-SPEC-v0.4.2a-dimension-unit-tests.md)
- [v0.4.2b — Composite & Gating Unit Tests](RR-SPEC-v0.4.2b-composite-unit-tests.md)
- [v0.4.2c — Calibration Specimen Scoring](RR-SPEC-v0.4.2c-calibration-scoring.md)
- [v0.4.2d — Boundary & Regression Tests](RR-SPEC-v0.4.2d-boundary-regression.md)
