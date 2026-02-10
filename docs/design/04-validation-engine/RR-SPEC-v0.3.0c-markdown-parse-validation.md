# v0.3.0c — Markdown Parse Validation

> **Version:** v0.3.0c
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.0-l0-parseable-gate.md](RR-SPEC-v0.3.0-l0-parseable-gate.md)
> **Grounding:** v0.0.4a §4 (MD-001: valid Markdown syntax), DiagnosticCode.E005_INVALID_MARKDOWN
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.title`, `ParsedLlmsTxt.sections`, `ParsedLlmsTxt.raw_content`)
> **Module:** `src/docstratum/validation/checks/l0_markdown_parse.py`
> **Tests:** `tests/test_validation_l0_markdown_parse.py`

---

## 1. Purpose

Detect files that contain content but cannot be parsed into any recognized `llms.txt` Markdown structure. This catches files that are valid text (not empty, not binary) but structurally unsuitable — JSON files, CSV files, prose with no headings, raw HTML, etc.

---

## 2. Diagnostic Code

| Code | Severity | Message                                                                        | Remediation                                                                                       |
| ---- | -------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| E005 | ERROR    | Markdown syntax prevents meaningful parsing. No `llms.txt` structure detected. | Ensure the file follows `llms.txt` format: H1 title, optional blockquote, H2 sections with links. |

---

## 3. Check Logic

```python
"""L0 Markdown parse validation check.

Detects files with content that cannot be parsed into llms.txt structure.
Complements E007 (empty file) — E005 catches non-empty, non-parseable files.

Implements v0.3.0c.
"""


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check whether the file has any parseable llms.txt structure.

    E005 fires when:
    - title is None (no H1 found) AND
    - sections is empty (no H2 sections) AND
    - raw_content is non-empty (file has content)

    E005 does NOT fire when:
    - File is empty → E007 has precedence (caught in l0_empty_file.py)
    - File has an H1 but no sections → partially parsed (H1 check handles it)
    - File has no H1 but has sections → anomalous but partially parsed

    Args:
        parsed: The parsed file model.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        Empty list if parseable, or [E005] if unparseable with content.
    """
    diagnostics: list[ValidationDiagnostic] = []

    has_content = len(parsed.raw_content.strip()) > 0
    has_no_structure = parsed.title is None and len(parsed.sections) == 0

    if has_content and has_no_structure:
        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.E005_INVALID_MARKDOWN,
                severity=Severity.ERROR,
                message=DiagnosticCode.E005_INVALID_MARKDOWN.message,
                remediation=DiagnosticCode.E005_INVALID_MARKDOWN.remediation,
                level=ValidationLevel.L0_PARSEABLE,
                check_id="MD-001",
                line_number=1,
                context=f"File has {len(parsed.raw_content)} bytes but no H1 or H2 structure.",
            )
        )

    return diagnostics
```

### 3.1 Precedence: E007 > E005

| File State                         | E007 (Empty)   | E005 (Invalid Markdown) |
| ---------------------------------- | -------------- | ----------------------- |
| Empty / whitespace-only            | ✅ Emitted     | ❌ Not emitted          |
| Has content, no Markdown structure | ❌ Not emitted | ✅ Emitted              |
| Has content, has H1 or H2          | ❌ Not emitted | ❌ Not emitted          |

This precedence is inherent in the check logic — E005 only fires when `raw_content` is non-empty, which means E007 (which fires when `raw_content` is empty) naturally does not overlap.

### 3.2 Decision: Partial Structure

A file with an H1 but no sections (`title="Something"`, `sections=[]`) does NOT trigger E005. It has parseable structure — the H1 was found. The _absence_ of sections is a content-quality issue caught at L1/L2, not a parseability failure.

Conversely, a file with H2 sections but no H1 (`title=None`, `sections=[...]`) does NOT trigger E005 either. There is parseable Markdown structure — just no title. E001 (no H1) catches that specific issue.

E005 is the catch-all for files where the parser found **nothing at all**.

---

## 4. Acceptance Criteria

- [ ] `check()` returns empty list for files with H1 title.
- [ ] `check()` returns empty list for files with sections but no H1 (E001 handles that).
- [ ] `check()` returns empty list for empty files (E007 handles that).
- [ ] `check()` returns E005 for JSON content.
- [ ] `check()` returns E005 for plain prose with no headings.
- [ ] `check()` returns E005 for CSV content.
- [ ] E005 diagnostic has `line_number=1` and `context` showing byte count.

---

## 5. Test Plan

### `tests/test_validation_l0_markdown_parse.py`

| Test                         | Input                                                                    | Expected |
| ---------------------------- | ------------------------------------------------------------------------ | -------- |
| `test_valid_markdown_passes` | `ParsedLlmsTxt(title="Title", sections=[...])`                           | `[]`     |
| `test_h1_only_passes`        | `ParsedLlmsTxt(title="Title", sections=[])`                              | `[]`     |
| `test_sections_only_no_e005` | `ParsedLlmsTxt(title=None, sections=[Section])`                          | `[]`     |
| `test_empty_file_no_e005`    | `ParsedLlmsTxt(title=None, sections=[], raw_content="")`                 | `[]`     |
| `test_json_content_fails`    | `ParsedLlmsTxt(title=None, sections=[], raw_content='{"key": "value"}')` | `[E005]` |
| `test_prose_content_fails`   | `ParsedLlmsTxt(title=None, sections=[], raw_content="Just some text.")`  | `[E005]` |
