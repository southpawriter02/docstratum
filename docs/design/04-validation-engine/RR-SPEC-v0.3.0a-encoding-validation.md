# v0.3.0a — Encoding Validation

> **Version:** v0.3.0a
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.0-l0-parseable-gate.md](RR-SPEC-v0.3.0-l0-parseable-gate.md)
> **Grounding:** v0.0.4a §4 (ENC-001: UTF-8 encoding), DiagnosticCode.E003_INVALID_ENCODING
> **Depends On:** v0.2.0a (`FileMetadata.encoding`)
> **Module:** `src/docstratum/validation/checks/l0_encoding.py`
> **Tests:** `tests/test_validation_l0_encoding.py`

---

## 1. Purpose

Verify that the file is valid UTF-8. Non-UTF-8 files cannot be reliably parsed as Markdown and produce unpredictable results when consumed by LLMs. This is the first and simplest validation gate — if the encoding is wrong, nothing else matters.

---

## 2. Diagnostic Code

| Code | Severity | Message                                | Remediation                                                                 |
| ---- | -------- | -------------------------------------- | --------------------------------------------------------------------------- |
| E003 | ERROR    | Invalid file encoding. Expected UTF-8. | Re-save the file as UTF-8. Check for binary content or encoding mismatches. |

---

## 3. Check Logic

```python
"""L0 encoding validation check.

Verifies that the file is encoded as UTF-8. Non-UTF-8 files cannot be
reliably parsed and are rejected at the L0 gate.

Implements v0.3.0a.
"""

from docstratum.schema.diagnostics import DiagnosticCode, Severity
from docstratum.schema.validation import ValidationDiagnostic, ValidationLevel


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check whether the file encoding is valid UTF-8.

    Args:
        parsed: The parsed file model (not directly used by this check).
        classification: The document classification (not directly used).
        file_meta: File-level metadata containing detected encoding.

    Returns:
        Empty list if UTF-8, or a list with one E003 diagnostic.
    """
    diagnostics: list[ValidationDiagnostic] = []

    if file_meta.encoding.lower() != "utf-8":
        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.E003_INVALID_ENCODING,
                severity=Severity.ERROR,
                message=DiagnosticCode.E003_INVALID_ENCODING.message,
                remediation=DiagnosticCode.E003_INVALID_ENCODING.remediation,
                level=ValidationLevel.L0_PARSEABLE,
                check_id="ENC-001",
                context=f"Detected encoding: {file_meta.encoding}",
            )
        )

    return diagnostics
```

### 3.1 Decision: BOM Handling

A UTF-8 BOM (`\xEF\xBB\xBF`) does NOT trigger E003. The file IS UTF-8 — it just has a BOM prefix.

| Scenario                    | Encoding Detected         | E003 Emitted?                   |
| --------------------------- | ------------------------- | ------------------------------- |
| Valid UTF-8, no BOM         | `utf-8`                   | No                              |
| Valid UTF-8 with BOM        | `utf-8-sig` or `utf-8`    | No (BOM is metadata only)       |
| Latin-1 fallback            | `latin-1`                 | Yes                             |
| Binary content / null bytes | `utf-8` (may still parse) | No (E005 or E007 catches these) |

> **Key Decision:** If v0.2.0a reports encoding as `utf-8-sig` (Python's name for UTF-8 with BOM), the check normalizes this to UTF-8 and does not emit E003. The BOM presence is recorded in `FileMetadata.has_bom` for informational purposes but is not a validation failure.

---

## 4. Acceptance Criteria

- [ ] `check()` returns empty list for UTF-8 files.
- [ ] `check()` returns empty list for UTF-8 with BOM (`utf-8-sig`).
- [ ] `check()` returns E003 for Latin-1 encoded files.
- [ ] E003 diagnostic includes `context` showing what encoding was detected.
- [ ] All diagnostic fields populated: `code`, `severity`, `message`, `remediation`, `level`, `check_id`.
- [ ] `line_number` is `None` (encoding is a file-level issue; no specific line).

---

## 5. Test Plan

### `tests/test_validation_l0_encoding.py`

| Test                          | Input                                   | Expected                                                                                          |
| ----------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `test_utf8_passes`            | `FileMetadata(encoding="utf-8")`        | `[]` (no diagnostics)                                                                             |
| `test_utf8_bom_passes`        | `FileMetadata(encoding="utf-8-sig")`    | `[]`                                                                                              |
| `test_latin1_fails`           | `FileMetadata(encoding="latin-1")`      | `[E003]`                                                                                          |
| `test_ascii_passes`           | `FileMetadata(encoding="ascii")`        | `[]` (ASCII is a subset of UTF-8)                                                                 |
| `test_e003_diagnostic_fields` | `FileMetadata(encoding="windows-1252")` | E003 with `severity=ERROR`, `level=L0`, `check_id="ENC-001"`, `context` contains `"windows-1252"` |
