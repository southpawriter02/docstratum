# v0.3.1a — Blockquote Presence

> **Version:** v0.3.1a
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.1-l1-structural.md](RR-SPEC-v0.3.1-l1-structural.md)
> **Grounding:** v0.0.4a §STR-002 (blockquote presence), v0.0.2 enrichment (55% real-world compliance), DiagnosticCode.W001_MISSING_BLOCKQUOTE
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.blockquote`)
> **Module:** `src/docstratum/validation/checks/l1_blockquote.py`
> **Tests:** `tests/test_validation_l1_blockquote.py`

---

## 1. Purpose

Detect files missing the blockquote description immediately after the H1 title. The `llms.txt` specification defines the blockquote as a one-line summary of the project — the `> description` element in the ABNF grammar.

### Why WARNING, Not ERROR

The v0.0.2 enrichment survey found only **55% adoption** of the blockquote convention across 450+ real-world `llms.txt` files. Making this an ERROR would fail nearly half of all existing files. The blockquote is a quality signal, not a structural requirement.

---

## 2. Diagnostic Code

| Code | Severity | Message                                             | Remediation                                                      |
| ---- | -------- | --------------------------------------------------- | ---------------------------------------------------------------- |
| W001 | WARNING  | No blockquote description found after the H1 title. | Add a `> description` blockquote immediately after the H1 title. |

---

## 3. Check Logic

```python
"""L1 blockquote presence check.

Detects files missing the blockquote description after the H1 title.
The ABNF grammar defines this as 'description = ">" SP desc-text CRLF'.

Implements v0.3.1a.
"""


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check whether a blockquote description exists after the H1.

    The parser (v0.2.0c) stores the blockquote text in
    ``parsed.blockquote``. If it's None or empty, the blockquote
    is missing.

    Args:
        parsed: The parsed file model.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        Empty list if blockquote exists, or [W001] if missing.
    """
    diagnostics: list[ValidationDiagnostic] = []

    if not parsed.blockquote:
        # Determine expected line: blockquote should be on line 2
        # (immediately after the H1 on line 1). Use title_line + 1
        # if available.
        expected_line = (parsed.title_line or 1) + 1

        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.W001_MISSING_BLOCKQUOTE,
                severity=Severity.WARNING,
                message=DiagnosticCode.W001_MISSING_BLOCKQUOTE.message,
                remediation=DiagnosticCode.W001_MISSING_BLOCKQUOTE.remediation,
                level=ValidationLevel.L1_STRUCTURAL,
                check_id="STR-002",
                line_number=expected_line,
                context=(
                    "Expected a blockquote (> description) on line "
                    f"{expected_line}, immediately after the H1 title."
                ),
            )
        )

    return diagnostics
```

### 3.1 Decision: `None` vs Empty String

| `parsed.blockquote`            | W001?             | Rationale                                                 |
| ------------------------------ | ----------------- | --------------------------------------------------------- |
| `None`                         | Yes               | No blockquote element found at all                        |
| `""` (empty string)            | Yes               | Blockquote markup exists but empty — functionally missing |
| `"> FastAPI docs"` (non-empty) | No                | Valid blockquote with content                             |
| `"> "` (whitespace only)       | Yes (after strip) | Whitespace-only is empty                                  |

The check uses `not parsed.blockquote` which is truthy for `None`, `""`, and whitespace-only after considering that the parser normalizes these.

### 3.2 Decision: `line_number` Placement

Since this is the _absence_ of an element, there is no specific source line to point to. We point to the line _where it should be_ — `title_line + 1` — to guide the author to the right insertion point.

---

## 4. Acceptance Criteria

- [ ] `check()` returns empty list for files with non-empty blockquote.
- [ ] `check()` returns W001 for `parsed.blockquote = None`.
- [ ] `check()` returns W001 for `parsed.blockquote = ""`.
- [ ] W001 uses `severity=WARNING`, `level=L1_STRUCTURAL`, `check_id="STR-002"`.
- [ ] W001 `line_number` is `title_line + 1`.

---

## 5. Test Plan

### `tests/test_validation_l1_blockquote.py`

| Test                             | Input                                   | Expected                  |
| -------------------------------- | --------------------------------------- | ------------------------- |
| `test_blockquote_present_passes` | `blockquote="> FastAPI framework docs"` | `[]`                      |
| `test_blockquote_none_fails`     | `blockquote=None`                       | `[W001]`                  |
| `test_blockquote_empty_fails`    | `blockquote=""`                         | `[W001]`                  |
| `test_w001_line_number`          | `title_line=1, blockquote=None`         | W001 with `line_number=2` |
