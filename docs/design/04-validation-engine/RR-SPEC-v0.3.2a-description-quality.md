# v0.3.2a — Description Quality

> **Version:** v0.3.2a
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.2-l2-content-quality.md](RR-SPEC-v0.3.2-l2-content-quality.md)
> **Grounding:** DS-VC-CON-001 (Non-empty Descriptions, 5 pts SOFT), DS-VC-CON-003 (No Placeholder Content, 3 pts SOFT), v0.0.4b §CNT-004
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.sections`, `ParsedLink.description`), v0.3.1 (L1 pass)
> **Module:** `src/docstratum/validation/checks/l2_description_quality.py`
> **Tests:** `tests/test_validation_l2_description_quality.py`

---

## 1. Purpose

Verify that links include meaningful descriptions — not bare URLs with no context. The `llms.txt` format defines links as `- [title](url): description`, where the description component is critical for AI agent comprehension and human readability. Files with link descriptions score 23% higher overall (v0.0.2c audit, r ≈ 0.45 correlation).

This check combines two criteria:

1. **CON-001 (Non-empty Descriptions):** Are descriptions present and non-empty?
2. **CON-003 (No Placeholder Content):** Are descriptions substantive (not "TBD", "TODO", "Lorem ipsum")?

Both map to a single diagnostic code (W003) because placeholder descriptions are a special case of "missing description" — the description slot exists but conveys no useful information.

### 1.1 Why W003 Covers Both CON-001 and CON-003

CON-003's official spec notes that placeholder detection "does not emit a standalone diagnostic code" — it feeds anti-pattern AP-CONT-002 (Blank Canvas). However, placeholder text _in link descriptions specifically_ is most naturally diagnosed as a quality-of-description issue, not a separate class of problem. W003 fires with different `context` strings to distinguish the sub-issue:

| Scenario                          | W003 Context                                       |
| --------------------------------- | -------------------------------------------------- |
| Description is `None`             | "Link has no description text."                    |
| Description is `""` or whitespace | "Link description is empty."                       |
| Description matches placeholder   | "Link description is placeholder text: '{match}'." |

---

## 2. Diagnostic Code

| Code | Severity | Criterion              | Message                                             | Remediation                                                                  |
| ---- | -------- | ---------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------- |
| W003 | WARNING  | DS-VC-CON-001, CON-003 | Link entry has no description text (bare URL only). | Add a description after the link: `- [Title](url): Description of the page`. |

---

## 3. Placeholder Patterns

The placeholder patterns must be defined as a constant in `constants.py`, not hardcoded in the check:

```python
# constants.py — add to existing constants module

PLACEHOLDER_PATTERNS: tuple[str, ...] = (
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bXXX\b",
    r"\bTBD\b",
    r"Lorem ipsum",
    r"\[INSERT.*?\]",
    r"\[PLACEHOLDER\]",
    r"<your.*?here>",
    r"Description here",
    r"placeholder",
    r"coming soon",
    r"documentation for \w+",  # formulaic "Documentation for {thing}"
)
"""Regex patterns for detecting placeholder content in descriptions.

Each pattern is compiled case-insensitively. A description matching any
pattern is considered placeholder text and triggers W003.

These patterns are used by v0.3.2a (description quality) and may be reused
by v0.3.2c (section content) for section-level placeholder detection.
"""
```

> [!NOTE]
> The pattern `documentation for \w+` catches the most common formulaic pattern from auto-generated files (Mintlify, etc.). However, a legitimate description like "Documentation for the REST API" would also match. The pattern should be refined after calibration against the 11 empirical specimens.

---

## 4. Check Logic

```python
"""L2 description quality check.

Verifies that link descriptions are present and substantive (not
placeholder text). Combines DS-VC-CON-001 (existence) and
DS-VC-CON-003 (placeholder detection) into a single check.

Implements v0.3.2a.
"""

import re

from docstratum.schema.constants import PLACEHOLDER_PATTERNS


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check that all links have substantive descriptions.

    For each ParsedLink:
    - If description is None → W003 ("no description text")
    - If description is empty/whitespace → W003 ("description is empty")
    - If description matches a placeholder pattern → W003 ("placeholder text")

    Args:
        parsed: The parsed file model with sections and links.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        List of W003 diagnostics, one per offending link.
    """
    diagnostics: list[ValidationDiagnostic] = []

    compiled_patterns = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in PLACEHOLDER_PATTERNS
    ]

    for section in parsed.sections:
        for link in section.links:
            diagnostic = _check_single_link(link, compiled_patterns)
            if diagnostic is not None:
                diagnostics.append(diagnostic)

    return diagnostics


def _check_single_link(
    link: "ParsedLink",
    patterns: list[re.Pattern],
) -> "ValidationDiagnostic | None":
    """Check a single link's description quality.

    Args:
        link: The parsed link to check.
        patterns: Compiled placeholder regex patterns.

    Returns:
        A W003 diagnostic if the description is missing, empty, or
        placeholder text. None if the description is substantive.
    """
    # Case 1: No description at all
    if link.description is None:
        return ValidationDiagnostic(
            code=DiagnosticCode.W003_LINK_MISSING_DESCRIPTION,
            severity=Severity.WARNING,
            message=DiagnosticCode.W003_LINK_MISSING_DESCRIPTION.message,
            remediation=DiagnosticCode.W003_LINK_MISSING_DESCRIPTION.remediation,
            level=ValidationLevel.L2_CONTENT,
            check_id="CNT-001",
            line_number=link.line_number,
            context=f"Link [{link.title}]({link.url}) has no description text.",
        )

    # Case 2: Empty or whitespace-only description
    stripped = link.description.strip()
    if not stripped:
        return ValidationDiagnostic(
            code=DiagnosticCode.W003_LINK_MISSING_DESCRIPTION,
            severity=Severity.WARNING,
            message=DiagnosticCode.W003_LINK_MISSING_DESCRIPTION.message,
            remediation=DiagnosticCode.W003_LINK_MISSING_DESCRIPTION.remediation,
            level=ValidationLevel.L2_CONTENT,
            check_id="CNT-001",
            line_number=link.line_number,
            context=f"Link [{link.title}]({link.url}) description is empty.",
        )

    # Case 3: Placeholder text
    for pattern in patterns:
        match = pattern.search(stripped)
        if match:
            return ValidationDiagnostic(
                code=DiagnosticCode.W003_LINK_MISSING_DESCRIPTION,
                severity=Severity.WARNING,
                message=DiagnosticCode.W003_LINK_MISSING_DESCRIPTION.message,
                remediation=DiagnosticCode.W003_LINK_MISSING_DESCRIPTION.remediation,
                level=ValidationLevel.L2_CONTENT,
                check_id="CNT-003",
                line_number=link.line_number,
                context=(
                    f"Link [{link.title}]({link.url}) description is "
                    f"placeholder text: '{match.group()}'."
                ),
            )

    return None  # Description is substantive
```

### 4.1 Decision: Per-Link Granularity

W003 fires per link, not per section or per file. This provides maximum diagnostic granularity — the user sees exactly which links need attention.

CON-001 defines a "ratio" pass condition (≥50% of links must have descriptions). However, at the **diagnostic emission** level, we report per-link. The ratio-based scoring will be handled by the scoring engine (v0.4.x), not by the diagnostic check. The check's job is to _identify_ issues; the scorer's job is to _weight_ them.

### 4.2 Decision: check_id for Context Variation

| Context                   | check_id  |
| ------------------------- | --------- |
| Missing/empty description | `CNT-001` |
| Placeholder description   | `CNT-003` |

The `check_id` field differentiates which criterion triggered the diagnostic. All three scenarios use the same W003 code but carry different `check_id` values.

---

## 5. Acceptance Criteria

- [ ] `check()` returns W003 for each link with `description is None`.
- [ ] `check()` returns W003 for each link with `description.strip() == ""`.
- [ ] `check()` returns W003 for each link matching a placeholder pattern.
- [ ] `check()` returns empty list when all links have substantive descriptions.
- [ ] Placeholder patterns are case-insensitive.
- [ ] Placeholder patterns are defined as a constant, not hardcoded in the check.
- [ ] `check_id="CNT-001"` for missing/empty, `check_id="CNT-003"` for placeholder.
- [ ] All W003s use `severity=WARNING`, `level=L2_CONTENT`.
- [ ] Files with zero links produce zero diagnostics.
- [ ] Context includes the link title and URL for identification.

---

## 6. Test Plan

### `tests/test_validation_l2_description_quality.py`

| Test                                   | Input                                      | Expected                           |
| -------------------------------------- | ------------------------------------------ | ---------------------------------- |
| `test_all_descriptions_present_passes` | 3 links with descriptions                  | `[]`                               |
| `test_none_description_warns`          | 1 link with `description=None`             | `[W003]`                           |
| `test_empty_description_warns`         | 1 link with `description=""`               | `[W003]`                           |
| `test_whitespace_description_warns`    | 1 link with `description="   "`            | `[W003]`                           |
| `test_todo_placeholder_warns`          | Description = "TODO: add description"      | `[W003]` with `check_id="CNT-003"` |
| `test_lorem_ipsum_warns`               | Description = "Lorem ipsum dolor sit amet" | `[W003]`                           |
| `test_tbd_placeholder_warns`           | Description = "[TBD]"                      | `[W003]`                           |
| `test_multiple_missing`                | 3 links, 2 missing descriptions            | 2 × W003                           |
| `test_mixed_valid_invalid`             | 2 valid + 1 placeholder                    | 1 × W003                           |
| `test_no_links_passes`                 | Sections but no links                      | `[]`                               |
| `test_placeholder_case_insensitive`    | Description = "todo" (lowercase)           | `[W003]`                           |
| `test_context_includes_link_info`      | Link with missing desc                     | Context contains title and URL     |

---

## 7. Design Decisions

| Decision                              | Choice              | Rationale                                                                                      |
| ------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------- |
| W003 for both CON-001 and CON-003     | Yes                 | Placeholder is a special case of "no useful description." One code, differentiated by context. |
| Per-link granularity                  | Yes                 | Maximum diagnostic resolution. Scoring aggregation is the scorer's job.                        |
| Constant-defined placeholder patterns | Yes                 | Extensible without modifying check logic. Reusable by v0.3.2c.                                 |
| No code-block-aware filtering         | Deferred            | Placeholder patterns inside code blocks are edge cases. Future improvement.                    |
| No ratio threshold                    | Deferred to scoring | The check identifies; the scorer weights. Ratio-based pass/fail is a scoring concern.          |
