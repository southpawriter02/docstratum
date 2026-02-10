# v0.3.5d — Calibration Specimen Validation

> **Version:** v0.3.5d
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.5-pipeline-assembly.md](RR-SPEC-v0.3.5-pipeline-assembly.md)
> **Depends On:** v0.3.5a–b (pipeline + aggregator), DS-CS-001 through DS-CS-006 (calibration specimens)

---

## 1. Purpose

v0.3.5d runs the complete validation pipeline against the **6 gold standard calibration specimens** — real-world `llms.txt` files that represent the quality spectrum from EXEMPLARY to CRITICAL. These serve as **regression tests** ensuring the pipeline correctly differentiates file quality.

### 1.1 Why Calibration Matters

Individual unit tests verify that specific checks emit correct diagnostics. Calibration tests verify that the **entire pipeline produces the right overall assessment** for real files. They are the end-to-end validation of the validation engine.

### 1.2 User Story

> As a developer, I want regression tests against known-quality files so that changes to individual checks don't silently degrade overall pipeline accuracy.

---

## 2. Calibration Specimens

| Specimen          | ID        | Source                        | Quality Tier | Expected Level     |
| ----------------- | --------- | ----------------------------- | ------------ | ------------------ |
| **Svelte**        | DS-CS-001 | svelte.dev/llms.txt           | EXEMPLARY    | L3+ (passes all)   |
| **Pydantic**      | DS-CS-002 | docs.pydantic.dev/llms.txt    | EXEMPLARY    | L3+ (passes all)   |
| **Vercel AI SDK** | DS-CS-003 | ai-sdk/llms.txt               | GOOD         | L3+ (passes all)   |
| **Shadcn UI**     | DS-CS-004 | ui.shadcn.com/llms.txt        | GOOD         | L3 (some warnings) |
| **Cursor**        | DS-CS-005 | cursor.com/llms.txt           | ACCEPTABLE   | L1–L2              |
| **NVIDIA**        | DS-CS-006 | developer.nvidia.com/llms.txt | CRITICAL     | L0–L1              |

### 2.1 Expected Diagnostic Profiles

#### DS-CS-001 (Svelte) — Expected: L3

| Level | Errors | Warnings | Notes                                     |
| ----- | ------ | -------- | ----------------------------------------- |
| L0    | 0      | 0        | Clean parse, valid encoding               |
| L1    | 0      | 0        | H1 present, blockquote, sections          |
| L2    | 0      | 0–2      | Strong content, possibly minor W003       |
| L3    | 0      | 0–3      | Canonical sections, code examples present |

#### DS-CS-006 (NVIDIA) — Expected: L0–L1

| Level | Errors | Warnings | Notes                                 |
| ----- | ------ | -------- | ------------------------------------- |
| L0    | 0–1    | 0        | May parse but minimal structure       |
| L1    | 1+     | 2+       | Missing sections or structural issues |
| L2    | —      | —        | Likely gated by L1 failure            |
| L3    | —      | —        | Likely gated                          |

---

## 3. Implementation

```python
"""Implements v0.3.5d — Calibration Specimen Validation."""

import pytest
from pathlib import Path

from docstratum.validation import validate_file
from docstratum.schema.validation import ValidationLevel

CALIBRATION_DIR = Path(__file__).parent.parent / "fixtures" / "calibration"


class TestCalibrationSpecimens:
    """Regression tests against 6 gold standard calibration specimens.

    These tests verify that the validation pipeline produces the
    expected level_achieved for known-quality files. Expected values
    are documented in DS-CS-001 through DS-CS-006.

    Implements v0.3.5d.
    """

    @pytest.mark.parametrize(
        "specimen_file, expected_min_level",
        [
            ("ds-cs-001-svelte.txt", ValidationLevel.L3_BEST_PRACTICES),
            ("ds-cs-002-pydantic.txt", ValidationLevel.L3_BEST_PRACTICES),
            ("ds-cs-003-vercel-ai-sdk.txt", ValidationLevel.L3_BEST_PRACTICES),
            ("ds-cs-004-shadcn-ui.txt", ValidationLevel.L2_CONTENT),
            ("ds-cs-005-cursor.txt", ValidationLevel.L1_STRUCTURAL),
            ("ds-cs-006-nvidia.txt", ValidationLevel.L0_PARSEABLE),
        ],
    )
    def test_specimen_level_achieved(
        self, specimen_file: str, expected_min_level: ValidationLevel
    ):
        """Verify that each specimen achieves at least its expected level."""
        path = CALIBRATION_DIR / specimen_file
        result = validate_file(path)
        assert result.level_achieved >= expected_min_level, (
            f"{specimen_file}: expected at least {expected_min_level.name}, "
            f"got {result.level_achieved.name}"
        )

    @pytest.mark.parametrize(
        "specimen_file",
        [
            "ds-cs-001-svelte.txt",
            "ds-cs-002-pydantic.txt",
            "ds-cs-003-vercel-ai-sdk.txt",
        ],
    )
    def test_exemplary_specimens_pass_l3(self, specimen_file: str):
        """Top-tier specimens should achieve L3 with no errors."""
        path = CALIBRATION_DIR / specimen_file
        result = validate_file(path)
        assert result.level_achieved == ValidationLevel.L3_BEST_PRACTICES
        assert result.total_errors == 0

    def test_nvidia_has_structural_issues(self):
        """NVIDIA specimen should exhibit structural deficiencies."""
        path = CALIBRATION_DIR / "ds-cs-006-nvidia.txt"
        result = validate_file(path)
        assert result.total_errors > 0 or result.total_warnings > 2

    def test_quality_ordering(self):
        """Specimens should maintain relative quality ordering.

        Svelte ≥ Pydantic ≥ Vercel ≥ Shadcn ≥ Cursor ≥ NVIDIA
        (by level_achieved, with warnings as tiebreaker).
        """
        specimens = [
            "ds-cs-001-svelte.txt",
            "ds-cs-002-pydantic.txt",
            "ds-cs-003-vercel-ai-sdk.txt",
            "ds-cs-004-shadcn-ui.txt",
            "ds-cs-005-cursor.txt",
            "ds-cs-006-nvidia.txt",
        ]
        results = [
            validate_file(CALIBRATION_DIR / s) for s in specimens
        ]

        # Level should be non-increasing (or equal)
        for i in range(len(results) - 1):
            assert results[i].level_achieved >= results[i + 1].level_achieved, (
                f"{specimens[i]} ({results[i].level_achieved.name}) should be "
                f">= {specimens[i+1]} ({results[i+1].level_achieved.name})"
            )
```

### 3.1 Decision Tree

```
For each calibration specimen:
    │
    ├── Load specimen from fixtures/calibration/
    │
    ├── Run validate_file(specimen)
    │
    └── Assert level_achieved ≥ expected_min_level
          │
          ├── Pass → Specimen correctly classified
          │
          └── Fail → Regression detected
                     → Investigate which check(s) changed
```

---

## 4. Fixture Management

### 4.1 Specimen Storage

```
tests/fixtures/calibration/
├── ds-cs-001-svelte.txt
├── ds-cs-002-pydantic.txt
├── ds-cs-003-vercel-ai-sdk.txt
├── ds-cs-004-shadcn-ui.txt
├── ds-cs-005-cursor.txt
└── ds-cs-006-nvidia.txt
```

### 4.2 Specimen Versioning

Specimens are **point-in-time snapshots** of real `llms.txt` files. They should be:

- Committed to the repository as test fixtures.
- **Never modified** after initial capture (to maintain regression stability).
- Documented with the capture date in a `SPECIMENS.md` file.

### 4.3 Adding New Specimens

When the v0.0.4c research identifies additional calibration files:

1. Capture the file to `tests/fixtures/calibration/`.
2. Run the pipeline and record `level_achieved` as the expected value.
3. Add a parametrized test case.
4. Document in `SPECIMENS.md`.

---

## 5. Edge Cases

| Case                               | Behavior                         | Rationale                                   |
| ---------------------------------- | -------------------------------- | ------------------------------------------- |
| Specimen updated upstream          | Test may fail                    | Specimens are snapshots; do not auto-update |
| New check changes expected level   | Update expected_min_level        | Documented regression                       |
| `check_urls=False` (default)       | E006 never emitted for specimens | URL checking is opt-in                      |
| Specimen has external dependencies | Test runs offline                | No network calls by default                 |

---

## 6. Deliverables

| File                                      | Description                  |
| ----------------------------------------- | ---------------------------- |
| `tests/validation/test_calibration.py`    | Calibration regression tests |
| `tests/fixtures/calibration/`             | 6 specimen files             |
| `tests/fixtures/calibration/SPECIMENS.md` | Specimen documentation       |

---

## 7. Test Plan (10 tests)

| #   | Test Name                                    | Assertion                     |
| --- | -------------------------------------------- | ----------------------------- |
| 1   | `test_specimen_level_achieved[svelte]`       | ≥ L3                          |
| 2   | `test_specimen_level_achieved[pydantic]`     | ≥ L3                          |
| 3   | `test_specimen_level_achieved[vercel]`       | ≥ L3                          |
| 4   | `test_specimen_level_achieved[shadcn]`       | ≥ L2                          |
| 5   | `test_specimen_level_achieved[cursor]`       | ≥ L1                          |
| 6   | `test_specimen_level_achieved[nvidia]`       | ≥ L0                          |
| 7   | `test_exemplary_specimens_pass_l3[svelte]`   | L3, 0 errors                  |
| 8   | `test_exemplary_specimens_pass_l3[pydantic]` | L3, 0 errors                  |
| 9   | `test_nvidia_has_structural_issues`          | errors > 0 OR warnings > 2    |
| 10  | `test_quality_ordering`                      | Non-increasing level sequence |
