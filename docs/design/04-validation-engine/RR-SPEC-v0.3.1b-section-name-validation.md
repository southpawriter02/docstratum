# v0.3.1b — Section Name Validation

> **Version:** v0.3.1b
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.1-l1-structural.md](RR-SPEC-v0.3.1-l1-structural.md)
> **Grounding:** v0.0.4a §NAM-001 (canonical section name matching), v0.0.1a §ABNF Grammar (`section = "##" SP section-name CRLF`), DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.sections`, `ParsedSection.name`, `ParsedSection.canonical_name`), v0.2.1c (canonical section matching), v0.1.2a (`CanonicalSectionName`, `SECTION_NAME_ALIASES`)
> **Module:** `src/docstratum/validation/checks/l1_section_names.py`
> **Tests:** `tests/test_validation_l1_section_names.py`

---

## 1. Purpose

Detect H2 sections whose names do not match any of the 11 canonical section names defined in `CanonicalSectionName`. Non-canonical names are a quality signal — they suggest the author is using a project-specific section structure rather than the recommended standard.

v0.2.1c performs canonical name matching during parsing and stores the result in `ParsedSection.canonical_name`. This check reads that field — it does NOT re-run the matching logic.

---

## 2. Diagnostic Code

| Code | Severity | Message                                                    | Remediation                                                           |
| ---- | -------- | ---------------------------------------------------------- | --------------------------------------------------------------------- |
| W002 | WARNING  | Section name does not match any of the 11 canonical names. | Use canonical names where possible (see `CanonicalSectionName` enum). |

---

## 3. Check Logic

```python
"""L1 section name validation check.

Detects H2 sections with names that don't match any canonical name.
Reads the canonical_name field populated by v0.2.1c during parsing.

Implements v0.3.1b.
"""

from docstratum.schema.constants import CanonicalSectionName


CANONICAL_LIST = ", ".join(f'"{name.value}"' for name in CanonicalSectionName)
"""Preformatted string of all 11 canonical names for diagnostic context."""


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check whether each section uses a canonical name.

    Iterates over every ParsedSection and checks whether
    ``section.canonical_name`` is set. If it's None, the section
    name was not recognized by the canonical matcher (v0.2.1c).

    One W002 is emitted per non-canonical section.

    Args:
        parsed: The parsed file model with sections.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        List of W002 diagnostics, one per non-canonical section.
    """
    diagnostics: list[ValidationDiagnostic] = []

    for section in parsed.sections:
        if section.canonical_name is None:
            diagnostics.append(
                ValidationDiagnostic(
                    code=DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME,
                    severity=Severity.WARNING,
                    message=DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME.message,
                    remediation=(
                        DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME.remediation
                    ),
                    level=ValidationLevel.L1_STRUCTURAL,
                    check_id="NAM-001",
                    line_number=section.line_number,
                    context=(
                        f'Section "## {section.name}" does not match any '
                        f"canonical name. Canonical names: {CANONICAL_LIST}."
                    ),
                )
            )

    return diagnostics
```

### 3.1 The 11 Canonical Section Names

These are the recognized names from `CanonicalSectionName`:

| #   | Canonical Name   | Common Aliases (from `SECTION_NAME_ALIASES`)       |
| --- | ---------------- | -------------------------------------------------- |
| 1   | Master Index     | table of contents, toc, index, docs, documentation |
| 2   | LLM Instructions | instructions, agent instructions                   |
| 3   | Getting Started  | quickstart, quick start, installation, setup       |
| 4   | Core Concepts    | concepts, key concepts, fundamentals               |
| 5   | API Reference    | api, reference, endpoints                          |
| 6   | Examples         | usage, use cases, tutorials, recipes               |
| 7   | Configuration    | config, settings, options                          |
| 8   | Advanced Topics  | advanced, internals                                |
| 9   | Troubleshooting  | debugging, common issues, known issues             |
| 10  | FAQ              | frequently asked questions                         |
| 11  | Optional         | supplementary, appendix, extras                    |

A section using ANY alias (case-insensitive) maps to its canonical name via v0.2.1c. Only sections matching NONE of these trigger W002.

### 3.2 Decision: One W002 Per Section

Each non-canonical section produces its own W002 diagnostic with its own `line_number` and `context`. This allows:

- Per-section remediation (each W002 tells you which section to rename)
- Anti-pattern counting (v0.3.4b counts W002 frequency for AP-STRUCT detection)
- Quality scoring (v0.4.x deducts per-section points)

A file with 5 sections where 3 are non-canonical produces 3 × W002.

### 3.3 Decision: Including Canonical List in Context

The `context` field includes all 11 canonical names as a comma-separated string. This gives the author immediate guidance without requiring them to look up external documentation. The diagnostic message is slightly longer but significantly more actionable.

### 3.4 Decision: No Fuzzy Suggestion

The scope doc lists "fuzzy matching for nearest canonical suggestion" as NICE-TO-HAVE. For v0.3.1b, the check reports the non-match but does NOT suggest the closest canonical name. Implementation options for future consideration:

- Levenshtein distance to `CanonicalSectionName.values()` (threshold ≤ 3 edits)
- Embedding similarity between section name and canonical names
- Pattern matching (e.g., "Getting started" ≈ "Getting Started")

This is deferred to v0.5.x or later.

---

## 4. Acceptance Criteria

- [ ] `check()` returns empty list when all sections have `canonical_name` set.
- [ ] `check()` returns W002 per section with `canonical_name = None`.
- [ ] W002 includes the actual section name in `context`.
- [ ] W002 includes all 11 canonical names in `context`.
- [ ] W002 uses `severity=WARNING`, `level=L1_STRUCTURAL`, `check_id="NAM-001"`.
- [ ] `line_number` is `section.line_number` (the line where `## SectionName` appears).
- [ ] Multiple non-canonical sections produce multiple W002 diagnostics.
- [ ] Sections with aliases that resolved to canonical names do NOT trigger W002.
- [ ] File with zero sections produces zero diagnostics.

---

## 5. Test Plan

### `tests/test_validation_l1_section_names.py`

| Test                                 | Input                                                     | Expected                                 |
| ------------------------------------ | --------------------------------------------------------- | ---------------------------------------- |
| `test_all_canonical_passes`          | 3 sections, all `canonical_name` set                      | `[]`                                     |
| `test_single_non_canonical`          | 1 section `canonical_name=None`                           | `[W002]`                                 |
| `test_multiple_non_canonical`        | 3 sections, 2 `canonical_name=None`                       | 2 × W002                                 |
| `test_mixed_canonical_non_canonical` | 4 sections (2 canonical, 2 not)                           | 2 × W002                                 |
| `test_alias_resolved_passes`         | Section "quickstart" → `canonical_name="Getting Started"` | `[]`                                     |
| `test_w002_includes_section_name`    | Section `name="Custom Stuff"`                             | W002 `context` contains `"Custom Stuff"` |
| `test_w002_includes_canonical_list`  | Any non-canonical                                         | W002 `context` contains `"Master Index"` |
| `test_w002_line_number`              | Section at `line_number=15`                               | W002 with `line_number=15`               |
| `test_no_sections_passes`            | `parsed.sections = []`                                    | `[]`                                     |
