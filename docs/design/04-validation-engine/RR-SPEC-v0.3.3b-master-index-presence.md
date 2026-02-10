# v0.3.3b — Master Index Presence

> **Version:** v0.3.3b
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.3-l3-best-practices.md](RR-SPEC-v0.3.3-l3-best-practices.md)
> **Depends On:** v0.2.1c (canonical name resolution)

---

## 1. Purpose

v0.3.3b checks whether the file contains a section functioning as a **Master Index** — the organizational hub that provides high-level navigation to key resources. This is one of the strongest single predictors of file utility:

> **Research finding (v0.0.2d):** Files with a Master Index achieve **87% LLM task success rate** vs. **31%** for files without one.

### 1.1 Recognition Strategy

The check relies on `ParsedSection.canonical_name` from v0.2.1c. The canonical name resolver already maps sections named "Table of Contents", "TOC", "Index", "Documentation", "Guide", "Overview", "Docs", and "Master Index" to `CanonicalSectionName.MASTER_INDEX`. This check simply verifies that at least one section received that mapping.

### 1.2 User Story

> As a documentation author, I want to know if my file lacks a Master Index so that I can add one — improving LLM task success from 31% to 87%.

---

## 2. Diagnostic Code

### W009 — NO_MASTER_INDEX

| Field                 | Value                                                           |
| --------------------- | --------------------------------------------------------------- |
| **Code**              | W009                                                            |
| **Severity**          | WARNING                                                         |
| **Emitted**           | Once per file (if no Master Index section found)                |
| **Criterion**         | DS-VC-CON-009 (5 pts / 50 content)                              |
| **Anti-Pattern Feed** | None directly (but absence contributes to reduced navigability) |

**Payload fields:**

```python
ValidationDiagnostic(
    code=DiagnosticCode.W009_NO_MASTER_INDEX,
    severity=Severity.WARNING,
    message="No Master Index section found.",
    level=ValidationLevel.L3_BEST_PRACTICES,
    check_id="CON-009",
    line_number=1,  # file-level observation
    context={
        "recognized_names": [
            "Master Index", "Table of Contents", "TOC", "Index",
            "Documentation", "Guide", "Overview", "Docs",
        ],
    },
    remediation=(
        "Add a 'Master Index' or 'Table of Contents' section as the first H2. "
        "Research shows 87% vs 31% LLM task success rate with a Master Index."
    ),
)
```

---

## 3. Check Logic

### 3.1 Algorithm

```python
"""Implements v0.3.3b — Master Index Presence check."""

from docstratum.schema.constants import CanonicalSectionName
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.validation import (
    Severity,
    ValidationDiagnostic,
    ValidationLevel,
)

MASTER_INDEX_RECOGNIZED_NAMES = [
    "Master Index", "Table of Contents", "TOC", "Index",
    "Documentation", "Guide", "Overview", "Docs",
]


def check_master_index(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:
    """Check for a Master Index section.

    Implements DS-VC-CON-009. Emits W009 if no section has
    canonical_name == CanonicalSectionName.MASTER_INDEX.
    Vacuous pass: if the file has zero H2 sections.
    """
    has_master_index = any(
        section.canonical_name == CanonicalSectionName.MASTER_INDEX
        for section in parsed.sections
    )

    if has_master_index or len(parsed.sections) == 0:
        return []

    return [
        ValidationDiagnostic(
            code=DiagnosticCode.W009_NO_MASTER_INDEX,
            severity=Severity.WARNING,
            message="No Master Index section found.",
            level=ValidationLevel.L3_BEST_PRACTICES,
            check_id="CON-009",
            line_number=1,
            context={
                "recognized_names": MASTER_INDEX_RECOGNIZED_NAMES,
            },
            remediation=(
                "Add a 'Master Index' or 'Table of Contents' section as the "
                "first H2. Research shows 87% vs 31% LLM task success rate "
                "with a Master Index."
            ),
        )
    ]
```

### 3.2 Decision Tree

```
sections = parsed.sections
  │
  ├── len(sections) == 0
  │     └── PASS (vacuous — no sections to evaluate)
  │
  ├── any section.canonical_name == MASTER_INDEX
  │     └── PASS
  │
  └── no section.canonical_name == MASTER_INDEX
        └── EMIT W009 (once, file-level)
```

### 3.3 Edge Cases

| Case                              | Behavior                              | Rationale                                     |
| --------------------------------- | ------------------------------------- | --------------------------------------------- |
| Zero sections                     | 0 diagnostics (vacuous pass)          | Cannot have a Master Index without sections   |
| Master Index at position 1        | Pass                                  | Ideal placement                               |
| Master Index at position 5        | Pass                                  | Criterion accepts any position (CON-009 spec) |
| Section named "Documentation"     | Pass (alias resolves to MASTER_INDEX) | v0.2.1c alias mapping                         |
| Section named "Table of Contents" | Pass (alias resolves to MASTER_INDEX) | v0.2.1c alias mapping                         |
| Section named "Links"             | W009 (not a recognized alias)         | Not in the 8 recognized variations            |

---

## 4. Deliverables

| File                                                  | Description  |
| ----------------------------------------------------- | ------------ |
| `src/docstratum/validation/checks/l3_master_index.py` | Check module |
| `tests/validation/checks/test_l3_master_index.py`     | Unit tests   |

---

## 5. Test Plan (8 tests)

| #   | Test Name                                  | Input                                        | Expected                                |
| --- | ------------------------------------------ | -------------------------------------------- | --------------------------------------- |
| 1   | `test_master_index_present_pass`           | Section with canonical name MASTER_INDEX     | 0 diagnostics                           |
| 2   | `test_master_index_alias_documentation`    | Section named "Documentation"                | 0 diagnostics                           |
| 3   | `test_master_index_alias_toc`              | Section named "Table of Contents"            | 0 diagnostics                           |
| 4   | `test_no_master_index`                     | Sections: "Getting Started", "API Reference" | 1 × W009                                |
| 5   | `test_zero_sections`                       | File with no H2 sections                     | 0 diagnostics                           |
| 6   | `test_w009_line_number_is_1`               | No Master Index                              | W009 with `line_number=1`               |
| 7   | `test_w009_context_includes_names`         | No Master Index                              | `context["recognized_names"]` populated |
| 8   | `test_master_index_not_first_still_passes` | Master Index at position 3                   | 0 diagnostics                           |
