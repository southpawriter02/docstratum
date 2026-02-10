# v0.3.0b — Line Ending Validation

> **Version:** v0.3.0b
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.0-l0-parseable-gate.md](RR-SPEC-v0.3.0-l0-parseable-gate.md)
> **Grounding:** v0.0.4a §4 (ENC-002: LF line endings only), DiagnosticCode.E004_INVALID_LINE_ENDINGS
> **Depends On:** v0.2.0a (`FileMetadata.line_ending_style`)
> **Module:** `src/docstratum/validation/checks/l0_line_endings.py`
> **Tests:** `tests/test_validation_l0_line_endings.py`

---

## 1. Purpose

Verify that the file uses LF (Unix-style) line endings exclusively. Mixed or non-LF line endings can cause tokenization inconsistencies, byte count mismatches, and parsing ambiguities.

---

## 2. Diagnostic Code

| Code | Severity | Message                                                  | Remediation                                                                             |
| ---- | -------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| E004 | ERROR    | Invalid line endings detected. Expected LF (Unix-style). | Convert line endings to LF. Most editors support this (`dos2unix`, or editor settings). |

---

## 3. Check Logic

```python
"""L0 line ending validation check.

Verifies that the file uses LF (Unix-style) line endings. CRLF, CR,
or mixed line endings are rejected at the L0 gate.

Implements v0.3.0b.
"""

from docstratum.schema.diagnostics import DiagnosticCode, Severity
from docstratum.schema.validation import ValidationDiagnostic, ValidationLevel


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check whether line endings are consistently LF.

    Args:
        parsed: The parsed file model (not directly used by this check).
        classification: The document classification (not directly used).
        file_meta: File-level metadata containing detected line ending style.

    Returns:
        Empty list if LF, or a list with one E004 diagnostic.
    """
    diagnostics: list[ValidationDiagnostic] = []

    if file_meta.line_ending_style.upper() != "LF":
        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.E004_INVALID_LINE_ENDINGS,
                severity=Severity.ERROR,
                message=DiagnosticCode.E004_INVALID_LINE_ENDINGS.message,
                remediation=DiagnosticCode.E004_INVALID_LINE_ENDINGS.remediation,
                level=ValidationLevel.L0_PARSEABLE,
                check_id="ENC-002",
                context=f"Detected line ending style: {file_meta.line_ending_style}",
            )
        )

    return diagnostics
```

### 3.1 Line Ending Style Values

The `FileMetadata.line_ending_style` field (from v0.2.0a) can be:

| Value     | Meaning                           | E004?                               |
| --------- | --------------------------------- | ----------------------------------- |
| `"LF"`    | Unix-style (`\n`)                 | No                                  |
| `"CRLF"`  | Windows-style (`\r\n`)            | Yes                                 |
| `"CR"`    | Legacy Mac (`\r`)                 | Yes                                 |
| `"MIXED"` | Multiple styles in same file      | Yes                                 |
| `"NONE"`  | Single-line file, no line endings | No (no line endings = trivially LF) |

---

## 4. Acceptance Criteria

- [ ] `check()` returns empty list for LF files.
- [ ] `check()` returns empty list for single-line files (`"NONE"`).
- [ ] `check()` returns E004 for CRLF files.
- [ ] `check()` returns E004 for CR files.
- [ ] `check()` returns E004 for MIXED line ending files.
- [ ] E004 diagnostic includes `context` showing what style was detected.

---

## 5. Test Plan

### `tests/test_validation_l0_line_endings.py`

| Test                          | Input                                     | Expected |
| ----------------------------- | ----------------------------------------- | -------- |
| `test_lf_passes`              | `FileMetadata(line_ending_style="LF")`    | `[]`     |
| `test_crlf_fails`             | `FileMetadata(line_ending_style="CRLF")`  | `[E004]` |
| `test_cr_fails`               | `FileMetadata(line_ending_style="CR")`    | `[E004]` |
| `test_mixed_fails`            | `FileMetadata(line_ending_style="MIXED")` | `[E004]` |
| `test_no_line_endings_passes` | `FileMetadata(line_ending_style="NONE")`  | `[]`     |
