# v0.3.3c — Code Examples & Language

> **Version:** v0.3.3c
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.3-l3-best-practices.md](RR-SPEC-v0.3.3-l3-best-practices.md)
> **Depends On:** v0.2.0b (section extraction), v0.2.1a (metadata extraction)

---

## 1. Purpose

v0.3.3c checks two related aspects of code quality in the documentation:

1. **Presence** — Does the file contain at least one fenced code block? (W004)
2. **Language specifiers** — Do all fenced code blocks include a language identifier? (W005)

Code examples are the **strongest single quality predictor** (r ≈ 0.65) identified in the v0.0.2c analysis of 450+ projects. Files without any code examples rarely score above 60; files with multiple, well-chosen examples routinely score above 85.

### 1.1 User Story

> As a documentation author, I want to know if my file lacks code examples or has code blocks without language tags, so that I can add examples with proper specifiers for better AI comprehension.

---

## 2. Diagnostic Codes

### W004 — NO_CODE_EXAMPLES

| Field                 | Value                                            |
| --------------------- | ------------------------------------------------ |
| **Code**              | W004                                             |
| **Severity**          | WARNING                                          |
| **Emitted**           | Once per file (if zero fenced code blocks found) |
| **Criterion**         | DS-VC-CON-010 (5 pts / 50 content)               |
| **Anti-Pattern Feed** | AP-CONT-006 (Example Void)                       |

### W005 — CODE_NO_LANGUAGE

| Field                 | Value                                            |
| --------------------- | ------------------------------------------------ |
| **Code**              | W005                                             |
| **Severity**          | WARNING                                          |
| **Emitted**           | Once per code block lacking a language specifier |
| **Criterion**         | DS-VC-CON-011 (3 pts / 50 content)               |
| **Anti-Pattern Feed** | None                                             |

---

## 3. Check Logic

### 3.1 Code Fence Detection

Fenced code blocks are identified by the triple-backtick pattern in `ParsedLlmsTxt.raw_content`. The check scans the entire file (not per-section) because code examples can appear in any section, including blockquotes.

````python
"""Implements v0.3.3c — Code Examples & Language check."""

import re

from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.validation import (
    Severity,
    ValidationDiagnostic,
    ValidationLevel,
)

# Matches opening code fence: ``` optionally followed by a language identifier
CODE_FENCE_PATTERN = re.compile(
    r"^(`{3,})(\s*)(\S+)?",
    re.MULTILINE,
)


def check_code_examples(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:
    """Check for code examples and language specifiers.

    Implements DS-VC-CON-010 (code presence) and DS-VC-CON-011
    (language specifiers). Emits W004 if no fenced code blocks
    found; W005 per code block lacking a language identifier.
    """
    diagnostics: list[ValidationDiagnostic] = []
    lines = parsed.raw_content.splitlines()

    code_blocks: list[dict] = []
    in_code_block = False
    fence_char_count = 0

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        if not in_code_block:
            match = CODE_FENCE_PATTERN.match(stripped)
            if match:
                fence_char_count = len(match.group(1))
                language = match.group(3)  # None if no lang
                code_blocks.append({
                    "line_number": i,
                    "language": language,
                })
                in_code_block = True
        else:
            # Check for closing fence (same or more backticks)
            if stripped.startswith("`" * fence_char_count) and stripped.rstrip("`") == "":
                in_code_block = False

    # W004: No code examples at all
    if len(code_blocks) == 0:
        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.W004_NO_CODE_EXAMPLES,
                severity=Severity.WARNING,
                message="No fenced code blocks found in the file.",
                level=ValidationLevel.L3_BEST_PRACTICES,
                check_id="CON-010",
                line_number=1,
                context={"code_block_count": 0},
                remediation=(
                    "Add at least one fenced code block (```) with a "
                    "language specifier. Code examples are the strongest "
                    "quality predictor (r ≈ 0.65)."
                ),
            )
        )
        return diagnostics  # W005 is moot if no code blocks exist

    # W005: Code blocks without language specifiers
    for block in code_blocks:
        if block["language"] is None:
            diagnostics.append(
                ValidationDiagnostic(
                    code=DiagnosticCode.W005_CODE_NO_LANGUAGE,
                    severity=Severity.WARNING,
                    message=(
                        f"Code block at line {block['line_number']} "
                        "has no language specifier."
                    ),
                    level=ValidationLevel.L3_BEST_PRACTICES,
                    check_id="CON-011",
                    line_number=block["line_number"],
                    context={
                        "line": block["line_number"],
                    },
                    remediation=(
                        "Add a language identifier after the opening "
                        "backticks: ```python, ```bash, ```json, etc."
                    ),
                )
            )

    return diagnostics
````

### 3.2 Decision Tree

```
Scan raw_content for code fences
  │
  ├── 0 code blocks found
  │     └── EMIT W004 (once, file-level)
  │         └── RETURN (W005 check skipped — moot)
  │
  └── ≥1 code blocks found
        └── For each code block:
              ├── language is not None
              │     └── PASS
              └── language is None
                    └── EMIT W005 with line_number
```

### 3.3 Edge Cases

| Case                                        | Behavior                              | Rationale                                       |
| ------------------------------------------- | ------------------------------------- | ----------------------------------------------- |
| Zero code blocks                            | W004 emitted, no W005                 | W005 requires code blocks to exist first        |
| All blocks have language                    | 0 diagnostics                         | Fully compliant                                 |
| Mixed (some with, some without)             | Only W005 for blocks missing language | W004 not emitted since code blocks exist        |
| Inline code only (single backticks)         | W004 emitted                          | Inline code is not a fenced code block          |
| Code fence with 4+ backticks (``````)       | Detected                              | Regex matches 3+ backticks                      |
| Nested code fences (4 backticks wrapping 3) | Inner fence treated as text           | Correct: inner ``` inside ```` block is content |
| Language identifier with spaces after       | Matches (e.g., ` ```python `)         | Regex captures first non-whitespace token       |
| Empty file                                  | W004 emitted                          | No content means no code blocks                 |

---

## 4. Deliverables

| File                                                   | Description  |
| ------------------------------------------------------ | ------------ |
| `src/docstratum/validation/checks/l3_code_examples.py` | Check module |
| `tests/validation/checks/test_l3_code_examples.py`     | Unit tests   |

---

## 5. Test Plan (12 tests)

| #   | Test Name                                | Input                           | Expected                      |
| --- | ---------------------------------------- | ------------------------------- | ----------------------------- |
| 1   | `test_no_code_blocks_emits_w004`         | File with no code fences        | 1 × W004                      |
| 2   | `test_one_block_with_language_passes`    | `python ... `                   | 0 diagnostics                 |
| 3   | `test_multiple_blocks_all_with_language` | 3 blocks, all with lang         | 0 diagnostics                 |
| 4   | `test_one_block_no_language_emits_w005`  | ``` (bare)                      | 1 × W005                      |
| 5   | `test_mixed_blocks_language_and_bare`    | 2 with lang + 1 bare            | 1 × W005                      |
| 6   | `test_w005_not_emitted_when_w004`        | No code blocks                  | W004 only, no W005            |
| 7   | `test_inline_code_does_not_count`        | Only `inline` code              | 1 × W004                      |
| 8   | `test_four_backtick_fence_detected`      | `python ... `                   | 0 diagnostics                 |
| 9   | `test_w005_line_number_correct`          | Bare fence at line 20           | W005 with `line_number=20`    |
| 10  | `test_w004_remediation_message`          | No code blocks                  | Remediation mentions r ≈ 0.65 |
| 11  | `test_empty_language_treated_as_none`    | ``` followed by whitespace only | 1 × W005                      |
| 12  | `test_diagnostic_fields_complete`        | Bare code block                 | All fields present on W005    |
