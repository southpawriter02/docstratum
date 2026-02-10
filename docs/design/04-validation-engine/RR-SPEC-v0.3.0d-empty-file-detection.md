# v0.3.0d — Empty File Detection

> **Version:** v0.3.0d
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.0-l0-parseable-gate.md](RR-SPEC-v0.3.0-l0-parseable-gate.md)
> **Grounding:** v0.0.4c §CHECK-001 (Ghost File anti-pattern), DiagnosticCode.E007_EMPTY_FILE
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.raw_content`)
> **Module:** `src/docstratum/validation/checks/l0_empty_file.py`
> **Tests:** `tests/test_validation_l0_empty_file.py`

---

## 1. Purpose

Detect files that are empty or contain only whitespace. An empty `llms.txt` file is the most severe documentation failure — the "Ghost File" anti-pattern (AP-CRIT-001). Detection at L0 ensures these files fail fast.

---

## 2. Diagnostic Code

| Code | Severity | Message                                    | Remediation                                                                |
| ---- | -------- | ------------------------------------------ | -------------------------------------------------------------------------- |
| E007 | ERROR    | File is empty or contains only whitespace. | Add content to the file. At minimum: H1 title, blockquote, one H2 section. |

---

## 3. Check Logic

```python
"""L0 empty file detection check.

Detects files that are empty (0 bytes) or contain only whitespace.
Maps to the Ghost File critical anti-pattern (AP-CRIT-001).

Implements v0.3.0d.
"""


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check whether the file is empty or whitespace-only.

    Args:
        parsed: The parsed file model.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        Empty list if file has content, or [E007] if empty.
    """
    diagnostics: list[ValidationDiagnostic] = []

    if len(parsed.raw_content.strip()) == 0:
        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.E007_EMPTY_FILE,
                severity=Severity.ERROR,
                message=DiagnosticCode.E007_EMPTY_FILE.message,
                remediation=DiagnosticCode.E007_EMPTY_FILE.remediation,
                level=ValidationLevel.L0_PARSEABLE,
                check_id="CHECK-001",
                context=f"File size: {file_meta.byte_count} bytes (all whitespace or empty).",
            )
        )

    return diagnostics
```

### 3.1 "Empty" Definition

| Content                                 | E007? | Rationale                                  |
| --------------------------------------- | ----- | ------------------------------------------ |
| 0 bytes                                 | Yes   | True empty file                            |
| `"   "` (spaces only)                   | Yes   | Whitespace-only is functionally empty      |
| `"\n\n\n"` (newlines only)              | Yes   | Same                                       |
| `"\t  \n  "` (mixed whitespace)         | Yes   | Same                                       |
| `"a"` (any non-whitespace char)         | No    | File has content (may still fail E005)     |
| YAML frontmatter only (`---\n...\n---`) | No    | Has content (characters beyond whitespace) |

---

## 4. Acceptance Criteria

- [ ] `check()` returns E007 for 0-byte files.
- [ ] `check()` returns E007 for whitespace-only files.
- [ ] `check()` returns empty list for files with any non-whitespace content.
- [ ] E007 diagnostic includes byte count in `context`.

---

## 5. Test Plan

### `tests/test_validation_l0_empty_file.py`

| Test                   | Input                       | Expected |
| ---------------------- | --------------------------- | -------- |
| `test_empty_string`    | `raw_content=""`            | `[E007]` |
| `test_whitespace_only` | `raw_content="   \n\t\n  "` | `[E007]` |
| `test_single_char`     | `raw_content="a"`           | `[]`     |
| `test_real_content`    | `raw_content="# Title\n"`   | `[]`     |
