# v0.3.3e — Structural Best Practices

> **Version:** v0.3.3e
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.3-l3-best-practices.md](RR-SPEC-v0.3.3-l3-best-practices.md)
> **Depends On:** v0.2.1c (canonical name resolution), v0.2.0b (section extraction)

---

## 1. Purpose

v0.3.3e checks whether **canonical sections appear in the recommended order**. The 11 canonical section names have a prescribed sequence (DECISION-012); when sections follow this order, both human readers and AI agents can navigate by position rather than scanning the entire document.

### 1.1 Scope of v0.3.3e

The roadmap lists **three criteria** under v0.3.3e: DS-VC-STR-007 (Canonical Section Ordering), DS-VC-STR-008 (No Critical Anti-Patterns), and DS-VC-STR-009 (No Structural Anti-Patterns).

However, STR-008 and STR-009 are **composite anti-pattern gates** — they aggregate detections from the anti-pattern pipeline (v0.3.4). This check implements only the **non-composite** criterion: **STR-007 (Section Ordering / W008)**.

> [!IMPORTANT]
> STR-008 and STR-009 are scored by the anti-pattern detection stage (v0.3.4a/b), not by this check module. This check only handles W008 (section ordering).

### 1.2 Canonical Section Order

Per `CANONICAL_SECTION_ORDER` in `constants.py`:

| Position | Section Name     |
| -------- | ---------------- |
| 1        | Master Index     |
| 2        | LLM Instructions |
| 3        | Getting Started  |
| 4        | Core Concepts    |
| 5        | API Reference    |
| 6        | Examples         |
| 7        | Configuration    |
| 8        | Advanced Topics  |
| 9        | Troubleshooting  |
| 10       | FAQ              |
| 11       | Optional         |

### 1.3 User Story

> As a documentation author, I want to know if my canonical sections are out of the recommended order so that I can reorder them for consistency and navigability.

---

## 2. Diagnostic Code

### W008 — SECTION_ORDER_NON_CANONICAL

| Field                 | Value                                                      |
| --------------------- | ---------------------------------------------------------- |
| **Code**              | W008                                                       |
| **Severity**          | WARNING                                                    |
| **Emitted**           | Once per file (if any canonical sections are out of order) |
| **Criterion**         | DS-VC-STR-007 (3 pts / 30 structural)                      |
| **Anti-Pattern Feed** | AP-STRUCT-004 (Section Shuffle)                            |

**Payload fields:**

```python
ValidationDiagnostic(
    code=DiagnosticCode.W008_SECTION_ORDER_NON_CANONICAL,
    severity=Severity.WARNING,
    message="Canonical sections are not in the recommended order.",
    level=ValidationLevel.L3_BEST_PRACTICES,
    check_id="STR-007",
    line_number=first_out_of_order_section_line,
    context={
        "found_order": found_canonical_names,
        "expected_order": expected_canonical_names,
        "first_violation": {
            "section": violating_section_name,
            "position": actual_position,
            "expected_after": preceding_canonical_name,
        },
    },
    remediation=(
        "Reorder sections to follow the canonical sequence: Master Index → "
        "LLM Instructions → Getting Started → ... → Optional."
    ),
)
```

---

## 3. Check Logic

### 3.1 Algorithm

```python
"""Implements v0.3.3e — Structural Best Practices (Section Ordering)."""

from docstratum.schema.constants import CANONICAL_SECTION_ORDER
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.validation import (
    Severity,
    ValidationDiagnostic,
    ValidationLevel,
)


def check_structural_practices(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:
    """Check canonical section ordering.

    Implements DS-VC-STR-007. Emits W008 if canonical sections
    appear out of the prescribed order. Non-canonical sections
    are ignored for ordering purposes.

    The check verifies the relative order of present canonical
    sections against CANONICAL_SECTION_ORDER. A file with only
    2 canonical sections (e.g., "Getting Started", "API Reference")
    passes if they are in that relative order, even though
    positions 1–2 (Master Index, LLM Instructions) and 5–11
    are missing.
    """
    # Extract canonical names in document order, ignoring None
    canonical_in_order: list[tuple[str, int]] = []
    for section in parsed.sections:
        if section.canonical_name is not None:
            canonical_in_order.append(
                (section.canonical_name.value, section.heading_line)
            )

    # 0 or 1 canonical sections → trivially ordered
    if len(canonical_in_order) <= 1:
        return []

    # Build the expected order indices
    name_to_index = {
        name: idx for idx, name in enumerate(CANONICAL_SECTION_ORDER)
    }

    indices = [
        name_to_index[name] for name, _ in canonical_in_order
        if name in name_to_index
    ]

    # Check monotonically increasing
    for i in range(1, len(indices)):
        if indices[i] < indices[i - 1]:
            # Found violation
            found_names = [name for name, _ in canonical_in_order]
            sorted_names = sorted(
                found_names,
                key=lambda n: name_to_index.get(n, 999),
            )

            violating_name = canonical_in_order[i][0]
            violating_line = canonical_in_order[i][1]
            preceding_name = canonical_in_order[i - 1][0]

            return [
                ValidationDiagnostic(
                    code=DiagnosticCode.W008_SECTION_ORDER_NON_CANONICAL,
                    severity=Severity.WARNING,
                    message=(
                        "Canonical sections are not in the recommended order."
                    ),
                    level=ValidationLevel.L3_BEST_PRACTICES,
                    check_id="STR-007",
                    line_number=violating_line,
                    context={
                        "found_order": found_names,
                        "expected_order": sorted_names,
                        "first_violation": {
                            "section": violating_name,
                            "appears_after": preceding_name,
                            "expected_before": preceding_name,
                        },
                    },
                    remediation=(
                        "Reorder sections to follow the canonical sequence: "
                        + " → ".join(sorted_names) + "."
                    ),
                )
            ]

    return []
```

### 3.2 Decision Tree

```
sections = parsed.sections
  │
  ├── Extract canonical_name (non-None) in document order
  │
  ├── 0 or 1 canonical sections
  │     └── PASS (trivially ordered)
  │
  └── ≥2 canonical sections
        │
        ├── Index sequence is monotonically increasing
        │     └── PASS
        │
        └── Index sequence breaks monotonicity
              └── EMIT W008 (once, at first violation)
```

### 3.3 Key Design Decision: Non-Canonical Sections Are Invisible

Non-canonical sections (those with `canonical_name is None`) do **not** affect ordering. A file structured as:

```
## Master Index       (canonical pos 1)
## My Custom Section  (ignored)
## API Reference      (canonical pos 5)
```

Is considered correctly ordered because `[1, 5]` is monotonically increasing.

### 3.4 Edge Cases

| Case                                  | Behavior                          | Rationale                                                                                                          |
| ------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Zero canonical sections               | Pass                              | Nothing to order                                                                                                   |
| One canonical section                 | Pass                              | Trivially ordered                                                                                                  |
| Two canonical in correct order        | Pass                              | Monotonically increasing                                                                                           |
| Two canonical in wrong order          | W008                              | `[5, 3]` is not increasing                                                                                         |
| All 11 canonical in correct order     | Pass                              | Full compliance                                                                                                    |
| Non-canonical interspersed            | Ignored                           | Only canonical sections participate                                                                                |
| Repeated canonical names              | Duplicate violates monotonicity   | `[1, 5, 5]` → indices not strictly increasing — but duplicate canonical names are a separate issue (AP-STRUCT-003) |
| Custom sections between two canonical | Pass (if canonical order correct) | Non-canonical sections are transparent                                                                             |

---

## 4. STR-008 and STR-009 Deferral

| Criterion                                   | What It Does                                 | Where Implemented        |
| ------------------------------------------- | -------------------------------------------- | ------------------------ |
| DS-VC-STR-008 (No Critical Anti-Patterns)   | Composite gate, aggregates AP-CRIT-001–004   | v0.3.4a                  |
| DS-VC-STR-009 (No Structural Anti-Patterns) | Composite gate, aggregates AP-STRUCT-001–005 | v0.3.4b                  |
| DS-VC-STR-007 (Section Ordering)            | Single check: W008                           | **This check (v0.3.3e)** |

> STR-008 and STR-009 are composite criteria that depend on anti-pattern detection results. They cannot be evaluated until v0.3.4 has run. This check handles the non-composite structural best practice (ordering) and defers the composite gates.

---

## 5. Deliverables

| File                                                          | Description  |
| ------------------------------------------------------------- | ------------ |
| `src/docstratum/validation/checks/l3_structural_practices.py` | Check module |
| `tests/validation/checks/test_l3_structural_practices.py`     | Unit tests   |

---

## 6. Test Plan (10 tests)

| #   | Test Name                                   | Input                                   | Expected                                               |
| --- | ------------------------------------------- | --------------------------------------- | ------------------------------------------------------ |
| 1   | `test_correct_order_passes`                 | Master Index → API Reference → Examples | 0 diagnostics                                          |
| 2   | `test_reversed_order_emits_w008`            | Examples → API Reference                | 1 × W008                                               |
| 3   | `test_zero_canonical_sections_passes`       | All non-canonical sections              | 0 diagnostics                                          |
| 4   | `test_one_canonical_section_passes`         | Only "Getting Started"                  | 0 diagnostics                                          |
| 5   | `test_non_canonical_interspersed`           | Master Index → "Custom" → API Reference | 0 diagnostics                                          |
| 6   | `test_all_eleven_in_order`                  | Full canonical sequence                 | 0 diagnostics                                          |
| 7   | `test_all_eleven_reversed`                  | Full canonical sequence reversed        | 1 × W008                                               |
| 8   | `test_w008_line_number`                     | Violation at line 30                    | W008 with `line_number=30`                             |
| 9   | `test_w008_context_found_vs_expected`       | Out of order                            | `context["found_order"]` ≠ `context["expected_order"]` |
| 10  | `test_w008_remediation_shows_correct_order` | Out of order                            | Remediation contains "→" sequence                      |
