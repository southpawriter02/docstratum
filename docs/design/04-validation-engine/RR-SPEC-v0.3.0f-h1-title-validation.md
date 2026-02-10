# v0.3.0f — H1 Title Validation

> **Version:** v0.3.0f
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.0-l0-parseable-gate.md](RR-SPEC-v0.3.0-l0-parseable-gate.md)
> **Grounding:** v0.0.4a §STR-001, v0.0.1a §ABNF Grammar (`title = "#" SP title-text CRLF`), DiagnosticCode.E001_NO_H1_TITLE, DiagnosticCode.E002_MULTIPLE_H1
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.title`, `ParsedLlmsTxt.title_line`, `ParsedLlmsTxt.raw_content`)
> **Module:** `src/docstratum/validation/checks/l0_h1_title.py`
> **Tests:** `tests/test_validation_l0_h1_title.py`

---

## 1. Purpose

Verify that exactly one H1 title exists in the document. The H1 title is the document's identity — without it, section extraction, canonical name matching, and ecosystem identification all become ambiguous. The ABNF grammar (`v0.0.1a`) defines `title` as a required production.

This check emits two mutually exclusive codes:

| Code | Severity | Condition                      |
| ---- | -------- | ------------------------------ |
| E001 | ERROR    | No H1 heading found            |
| E002 | ERROR    | More than one H1 heading found |

---

## 2. Diagnostic Codes

| Code | Severity | Message                                                               | Remediation                                             |
| ---- | -------- | --------------------------------------------------------------------- | ------------------------------------------------------- |
| E001 | ERROR    | No H1 title found. Every `llms.txt` file must begin with a `# Title`. | Add a `# ProjectName` heading as the first line.        |
| E002 | ERROR    | Multiple H1 headings found. Only one `# Title` is allowed per file.   | Remove duplicate `# ` headings. Use `## ` for sections. |

---

## 3. Check Logic

````python
"""L0 H1 title validation check.

Verifies that exactly one H1 heading (# Title) exists. E001 fires for
zero H1s; E002 fires for multiple. These are mutually exclusive.

Implements v0.3.0f.
"""


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check for exactly one H1 title.

    Detection of multiple H1s requires scanning raw_content or
    the token stream, since ParsedLlmsTxt only stores the first H1.

    Args:
        parsed: The parsed file model.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        Empty list if exactly one H1, or [E001] or [E002].
    """
    diagnostics: list[ValidationDiagnostic] = []

    if parsed.title is None:
        # No H1 found at all
        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.E001_NO_H1_TITLE,
                severity=Severity.ERROR,
                message=DiagnosticCode.E001_NO_H1_TITLE.message,
                remediation=DiagnosticCode.E001_NO_H1_TITLE.remediation,
                level=ValidationLevel.L0_PARSEABLE,
                check_id="STR-001",
                line_number=1,
                context="Expected '# Title' as the first heading.",
            )
        )
    else:
        # H1 exists — check for duplicates
        h1_lines = _find_h1_lines(parsed.raw_content)
        if len(h1_lines) > 1:
            second_h1_line = h1_lines[1]
            diagnostics.append(
                ValidationDiagnostic(
                    code=DiagnosticCode.E002_MULTIPLE_H1,
                    severity=Severity.ERROR,
                    message=DiagnosticCode.E002_MULTIPLE_H1.message,
                    remediation=DiagnosticCode.E002_MULTIPLE_H1.remediation,
                    level=ValidationLevel.L0_PARSEABLE,
                    check_id="STR-001",
                    line_number=second_h1_line,
                    context=(
                        f"First H1 at line {parsed.title_line}, "
                        f"second H1 at line {second_h1_line}."
                    ),
                )
            )

    return diagnostics


def _find_h1_lines(raw_content: str) -> list[int]:
    """Find all line numbers containing H1 headings.

    Scans raw_content for lines starting with '# ' (H1 marker).
    Excludes lines inside fenced code blocks.

    Args:
        raw_content: The full raw text of the file.

    Returns:
        List of 1-indexed line numbers where H1 headings appear.
    """
    h1_lines: list[int] = []
    in_code_block = False

    for line_num, line in enumerate(raw_content.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block and stripped.startswith("# "):
            h1_lines.append(line_num)

    return h1_lines
````

### 3.1 Mutual Exclusion

E001 and E002 can never both fire for the same file:

| State          | `parsed.title` | H1 count | Result |
| -------------- | -------------- | -------- | ------ |
| No H1          | `None`         | 0        | E001   |
| Exactly one H1 | Set            | 1        | Pass   |
| Multiple H1s   | Set (first)    | ≥ 2      | E002   |

### 3.2 Code Fence Awareness

The `_find_h1_lines()` helper skips lines inside fenced code blocks (` ``` `). Without this, a code example containing `# Example Title` would be falsely detected as a second H1.

### 3.3 Why H1 Is at L0

Every downstream check assumes the document has an identity (the H1 title). Without it:

- Canonical section matching cannot contextualize section names
- Ecosystem file identification breaks (`project_name` extraction relies on H1)
- The ABNF grammar treats `title` as a **required production**, not optional

This makes H1 absence a structural prerequisite failure, not merely a best-practice issue.

---

## 4. Acceptance Criteria

- [ ] `check()` returns empty list for files with exactly one H1.
- [ ] `check()` returns E001 for files with no H1.
- [ ] `check()` returns E002 for files with 2+ H1s.
- [ ] E001 and E002 never fire simultaneously.
- [ ] E002 includes `line_number` of the second H1.
- [ ] E002 includes `context` showing both H1 positions.
- [ ] H1s inside code fences are not counted.

---

## 5. Test Plan

### `tests/test_validation_l0_h1_title.py`

| Test                            | Input                                        | Expected                           |
| ------------------------------- | -------------------------------------------- | ---------------------------------- |
| `test_single_h1_passes`         | `"# Title\n## Section\n"`                    | `[]`                               |
| `test_no_h1_fails`              | `"## Section Only\n"`                        | `[E001]`                           |
| `test_multiple_h1_fails`        | `"# First\n## Mid\n# Second\n"`              | `[E002]`                           |
| `test_h1_in_code_fence_ignored` | `"# Title\n\`\`\`\n# Not a title\n\`\`\`\n"` | `[]`                               |
| `test_e001_line_number`         | `"No heading here\n"`                        | E001 with `line_number=1`          |
| `test_e002_line_number`         | `"# First\n\n# Second\n"`                    | E002 with `line_number=3`          |
| `test_mutual_exclusion`         | (multiple fixtures)                          | Never both E001 and E002 in result |
