# v0.3.5c — Validation Unit Tests

> **Version:** v0.3.5c
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.5-pipeline-assembly.md](RR-SPEC-v0.3.5-pipeline-assembly.md)
> **Depends On:** v0.3.0–v0.3.4 (all checks + anti-patterns), v0.3.5a–b (pipeline + aggregator)

---

## 1. Purpose

v0.3.5c defines the **comprehensive test suite** for the validation engine. While individual sub-parts (v0.3.0–v0.3.4) each define per-module tests, v0.3.5c adds **cross-cutting integration tests** that verify pipeline behavior across levels.

### 1.1 Coverage Target

```
pytest --cov=docstratum.validation --cov-fail-under=85
```

### 1.2 User Story

> As a QA engineer, I want comprehensive gate behavior, diagnostic completeness, and cross-check interaction tests so that I can trust the pipeline produces correct results.

---

## 2. Test Categories

### 2.1 Gate Behavior Tests (8 tests)

Verify that gate-on-failure semantics work correctly across levels.

| #   | Test Name                    | Setup                             | Assertion               |
| --- | ---------------------------- | --------------------------------- | ----------------------- |
| 1   | `test_l0_gate_prevents_l1`   | Mock L0 check to emit ERROR       | L1 checks never called  |
| 2   | `test_l0_gate_prevents_l2`   | Mock L0 to emit ERROR             | L2 checks never called  |
| 3   | `test_l0_gate_prevents_l3`   | Mock L0 to emit ERROR             | L3 checks never called  |
| 4   | `test_l1_gate_prevents_l2`   | L0 passes, mock L1 to emit ERROR  | L2 checks never called  |
| 5   | `test_l1_gate_prevents_l3`   | L0 passes, mock L1 to emit ERROR  | L3 checks never called  |
| 6   | `test_l2_gate_prevents_l3`   | L0–L1 pass, mock L2 to emit ERROR | L3 checks never called  |
| 7   | `test_warning_does_not_gate` | L1 emits WARNING only             | L2 and L3 still execute |
| 8   | `test_info_does_not_gate`    | L1 emits INFO only                | L2 and L3 still execute |

### 2.2 Cross-Check Interaction Tests (6 tests)

Verify correct behavior when multiple checks interact.

| #   | Test Name                                    | Setup                       | Assertion                                     |
| --- | -------------------------------------------- | --------------------------- | --------------------------------------------- |
| 9   | `test_e007_takes_precedence_over_e005`       | Empty file                  | E007 emitted; E005 not emitted (or secondary) |
| 10  | `test_e001_e002_mutually_exclusive`          | Both conditions             | Only one of E001/E002 emitted (never both)    |
| 11  | `test_w002_feeds_naming_nebula`              | ≥50% non-canonical sections | W002 diagnostics + AP-STRUCT-005 detected     |
| 12  | `test_w003_feeds_link_desert`                | >60% undescribed links      | W003 diagnostics + AP-CONT-004 detected       |
| 13  | `test_w004_feeds_example_void`               | No code examples            | W004 diagnostic + AP-CONT-006 detected        |
| 14  | `test_critical_anti_pattern_with_l0_failure` | E007 (empty file)           | AP-CRIT-001 detected despite L0 failure       |

### 2.3 Diagnostic Completeness Tests (4 tests)

Verify that every diagnostic includes all required fields.

| #   | Test Name                               | Setup                     | Assertion                                       |
| --- | --------------------------------------- | ------------------------- | ----------------------------------------------- |
| 15  | `test_all_diagnostics_have_code`        | Run pipeline on test file | Every diagnostic has `.code`                    |
| 16  | `test_all_diagnostics_have_severity`    | Same                      | Every diagnostic has `.severity`                |
| 17  | `test_all_diagnostics_have_message`     | Same                      | Every diagnostic has `.message` (non-empty)     |
| 18  | `test_all_diagnostics_have_remediation` | Same                      | Every diagnostic has `.remediation` (non-empty) |

### 2.4 End-to-End Pipeline Tests (4 tests)

| #   | Test Name                    | Setup                              | Assertion                             |
| --- | ---------------------------- | ---------------------------------- | ------------------------------------- |
| 19  | `test_clean_file_passes_all` | Exemplary fixture file             | `level_achieved=L3`, 0 errors         |
| 20  | `test_empty_file_fails_l0`   | Empty fixture                      | `level_achieved=L0`, `is_valid=False` |
| 21  | `test_structural_only_file`  | Valid markdown, no content quality | `level_achieved=L1` or `L2`           |
| 22  | `test_result_serializable`   | Any result                         | `result.model_dump_json()` succeeds   |

---

## 3. Fixture Strategy

### 3.1 Fixture Files

```
tests/validation/fixtures/
├── clean_file.txt          # Passes all L0–L3 checks
├── empty_file.txt          # Empty (triggers E007)
├── no_h1.txt               # Missing H1 (triggers E001)
├── multiple_h1.txt         # Two H1s (triggers E002)
├── encoding_error.txt      # Non-UTF-8 bytes (triggers E003)
├── large_file.txt          # >100K tokens (triggers E008)
├── warnings_only.txt       # L0–L2 pass, many WARNINGs
├── structural_only.txt     # Good structure, weak content
└── anti_pattern_target.txt # Triggers multiple anti-patterns
```

### 3.2 Mock Strategy

For gate behavior tests, **mock check functions** rather than creating fixture files:

```python
@pytest.fixture
def mock_l0_error():
    """Mock that makes L0 emit an ERROR."""
    def check(parsed, classification, file_meta):
        return [ValidationDiagnostic(
            code=DiagnosticCode.E007_EMPTY_FILE,
            severity=Severity.ERROR,
            ...
        )]
    return check
```

---

## 4. Deliverables

| File                                               | Description                       |
| -------------------------------------------------- | --------------------------------- |
| `tests/validation/test_gate_behavior.py`           | Gate behavior tests (8)           |
| `tests/validation/test_cross_check.py`             | Cross-check interaction tests (6) |
| `tests/validation/test_diagnostic_completeness.py` | Field completeness tests (4)      |
| `tests/validation/test_end_to_end.py`              | End-to-end pipeline tests (4)     |
| `tests/validation/fixtures/`                       | Test fixture files                |

---

## 5. Total Test Count

| Category                          | Tests    |
| --------------------------------- | -------- |
| Gate Behavior                     | 8        |
| Cross-Check Interaction           | 6        |
| Diagnostic Completeness           | 4        |
| End-to-End Pipeline               | 4        |
| **Total (v0.3.5c)**               | **22**   |
| Per-module tests (v0.3.0–v0.3.4)  | ~285     |
| Pipeline + Aggregator (v0.3.5a–b) | 20       |
| **Grand Total**                   | **~327** |
