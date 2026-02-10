# v0.3.3a — Canonical Section Names

> **Version:** v0.3.3a
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.3-l3-best-practices.md](RR-SPEC-v0.3.3-l3-best-practices.md)
> **Depends On:** v0.2.1c (canonical name resolution — populates `ParsedSection.canonical_name`)

---

## 1. Purpose

v0.3.3a checks whether H2 section names align with the 11 canonical names or 32 recognized aliases defined by DECISION-012. Canonical naming is the strongest structural signal of a well-organized `llms.txt` file; projects with ≥70% canonical alignment achieve ~75% LLM task success versus ~15% for files with all custom names.

### 1.1 Why This Is L3 (Not L1)

v0.3.1b validates section structure and detects non-canonical names, but at L1 the focus is _structural completeness_ — whether sections parse correctly. At L3, the concern is _naming best practice_: are your sections named in ways that maximize AI navigability? Many valid files use custom section names (e.g., project-specific categories), so non-canonical naming is a quality advisory, not a structural failure.

### 1.2 User Story

> As a documentation author, I want to know which of my sections use non-canonical names so that I can rename them for better AI and human navigability.

---

## 2. Diagnostic Code

### W002 — NON_CANONICAL_SECTION_NAME

| Field                 | Value                                                 |
| --------------------- | ----------------------------------------------------- |
| **Code**              | W002                                                  |
| **Severity**          | WARNING                                               |
| **Emitted**           | Once per H2 section with `canonical_name is None`     |
| **Criterion**         | DS-VC-CON-008 (5 pts / 50 content)                    |
| **Anti-Pattern Feed** | AP-STRUCT-005 (Naming Nebula) when ≥50% non-canonical |

**Payload fields:**

```python
ValidationDiagnostic(
    code=DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME,
    severity=Severity.WARNING,
    message=f"Section '{section.name}' is not a canonical section name.",
    level=ValidationLevel.L3_BEST_PRACTICES,
    check_id="CON-008",
    line_number=section.heading_line,
    context={
        "section_name": section.name,
        "canonical_names": CANONICAL_SECTION_NAMES_LIST,
    },
    remediation="Use one of the 11 canonical names or 32 aliases. "
                f"See DECISION-012 for the full list.",
)
```

---

## 3. Check Logic

### 3.1 Algorithm

```python
"""Implements v0.3.3a — Canonical Section Names check."""

from docstratum.schema.constants import CANONICAL_SECTION_NAMES_LIST
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.validation import (
    Severity,
    ValidationDiagnostic,
    ValidationLevel,
)


def check_canonical_names(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:
    """Check section names against canonical names + aliases.

    Implements DS-VC-CON-008. Emits W002 per non-canonical section.
    Vacuous pass: if the file has zero H2 sections.
    """
    diagnostics: list[ValidationDiagnostic] = []

    for section in parsed.sections:
        if section.canonical_name is None:
            diagnostics.append(
                ValidationDiagnostic(
                    code=DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME,
                    severity=Severity.WARNING,
                    message=f"Section '{section.name}' is not a canonical section name.",
                    level=ValidationLevel.L3_BEST_PRACTICES,
                    check_id="CON-008",
                    line_number=section.heading_line,
                    context={
                        "section_name": section.name,
                        "canonical_names": CANONICAL_SECTION_NAMES_LIST,
                    },
                    remediation=(
                        "Use one of the 11 canonical names or 32 aliases. "
                        "See DECISION-012 for the full list."
                    ),
                )
            )

    return diagnostics
```

### 3.2 Decision Tree

```
For each ParsedSection:
  │
  ├── section.canonical_name is not None
  │     └── PASS — section matches a canonical name or alias
  │
  └── section.canonical_name is None
        └── EMIT W002 with section.name and line_number
```

### 3.3 Edge Cases

| Case                                              | Behavior                                   | Rationale                       |
| ------------------------------------------------- | ------------------------------------------ | ------------------------------- |
| Zero H2 sections                                  | Empty diagnostics list (vacuous pass)      | No sections to evaluate         |
| All sections canonical                            | Empty diagnostics list                     | File fully compliant            |
| All sections non-canonical                        | N × W002 (one per section)                 | File has 0% canonical alignment |
| Non-canonical name that resembles a canonical one | W002 emitted; no fuzzy matching            | Future enhancement              |
| Section with alias name                           | Pass (canonical_name populated by v0.2.1c) | Aliases map to canonical names  |

---

## 4. Criterion: DS-VC-CON-008

CON-008 defines a **70% threshold**: the criterion passes when ≥70% of H2 sections use canonical or alias names. However, the _diagnostic_ (W002) fires per non-canonical section regardless of the ratio. The 70% threshold is a _criterion-level_ pass condition used by the scorer (v0.5.x), not by the check function itself.

> [!IMPORTANT]
> The check function emits W002 per section. The 70% ratio evaluation belongs to the scorer, not to this check.

---

## 5. Deliverables

| File                                                     | Description  |
| -------------------------------------------------------- | ------------ |
| `src/docstratum/validation/checks/l3_canonical_names.py` | Check module |
| `tests/validation/checks/test_l3_canonical_names.py`     | Unit tests   |

---

## 6. Test Plan (10 tests)

| #   | Test Name                                   | Input                               | Expected                                                                |
| --- | ------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------- |
| 1   | `test_all_canonical_names_pass`             | File with 5 sections, all canonical | 0 diagnostics                                                           |
| 2   | `test_all_alias_names_pass`                 | File with 3 alias-named sections    | 0 diagnostics                                                           |
| 3   | `test_single_non_canonical`                 | 4 canonical + 1 custom ("My Notes") | 1 × W002 for "My Notes"                                                 |
| 4   | `test_all_non_canonical`                    | 3 sections, all custom names        | 3 × W002                                                                |
| 5   | `test_zero_sections`                        | File with no H2 sections            | 0 diagnostics (vacuous pass)                                            |
| 6   | `test_mixed_canonical_and_custom`           | 2 canonical + 2 custom              | 2 × W002                                                                |
| 7   | `test_case_insensitive`                     | Section "GETTING STARTED"           | 0 diagnostics (alias resolution is case-insensitive)                    |
| 8   | `test_w002_line_number`                     | Section at line 15                  | W002 with `line_number=15`                                              |
| 9   | `test_w002_context_includes_canonical_list` | Any non-canonical                   | `context["canonical_names"]` populated                                  |
| 10  | `test_diagnostic_fields_complete`           | Non-canonical section               | Check all fields: code, severity, message, level, check_id, remediation |
