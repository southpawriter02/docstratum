# v0.3.4a — Critical Anti-Patterns

> **Version:** v0.3.4a
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.4-anti-pattern-detection.md](RR-SPEC-v0.3.4-anti-pattern-detection.md)
> **Depends On:** L0 diagnostics (E001–E008)

---

## 1. Purpose

v0.3.4a detects the **4 critical anti-patterns** — documentation failures so severe that the file is functionally useless for LLM consumption. Detection of any critical anti-pattern triggers **DS-QS-GATE**: the quality score is capped at 29 (CRITICAL grade).

### 1.1 User Story

> As a CI pipeline, I want to detect files that are structurally unsalvageable so that I can flag them for immediate human review before serving to AI agents.

---

## 2. Anti-Pattern Definitions

| ID          | Name                  | Detection Rule                          | Constituent Diagnostics | CHECK     |
| ----------- | --------------------- | --------------------------------------- | ----------------------- | --------- |
| AP-CRIT-001 | **Ghost File**        | E007 emitted                            | E007 (EMPTY_FILE)       | CHECK-001 |
| AP-CRIT-002 | **Structure Chaos**   | (E001 OR E002) AND `len(sections) == 0` | E001, E002, E005        | CHECK-002 |
| AP-CRIT-003 | **Encoding Disaster** | E003 emitted                            | E003 (INVALID_ENCODING) | CHECK-003 |
| AP-CRIT-004 | **Link Void**         | E006 count / total links > 80%          | E006 (multiple)         | CHECK-004 |

---

## 3. Detection Logic

### 3.1 Implementation

```python
"""Implements v0.3.4a — Critical Anti-Pattern Detection."""

from docstratum.schema.constants import AntiPatternCategory, AntiPatternID
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.validation import ValidationDiagnostic

from .detector import AntiPatternDetection


def detect_critical(
    diagnostics: list[ValidationDiagnostic],
    parsed: ParsedLlmsTxt,
) -> list[AntiPatternDetection]:
    """Detect 4 critical anti-patterns from L0 diagnostics.

    All 4 are fully detectable at v0.3.x. Detection of any
    activates DS-QS-GATE (score capped at 29).
    """
    diag_codes = {d.code for d in diagnostics}
    results: list[AntiPatternDetection] = []

    # ── AP-CRIT-001: Ghost File ─────────────────────────────
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CRIT_001,
        pattern_name="Ghost File",
        category=AntiPatternCategory.CRITICAL,
        detected=DiagnosticCode.E007_EMPTY_FILE in diag_codes,
        constituent_diagnostics=[DiagnosticCode.E007_EMPTY_FILE],
        context={
            "description": "Empty or whitespace-only file.",
            "check_id": "CHECK-001",
        },
    ))

    # ── AP-CRIT-002: Structure Chaos ────────────────────────
    has_h1_error = (
        DiagnosticCode.E001_NO_H1_TITLE in diag_codes
        or DiagnosticCode.E002_MULTIPLE_H1 in diag_codes
    )
    no_sections = len(parsed.sections) == 0
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CRIT_002,
        pattern_name="Structure Chaos",
        category=AntiPatternCategory.CRITICAL,
        detected=has_h1_error and no_sections,
        constituent_diagnostics=[
            DiagnosticCode.E001_NO_H1_TITLE,
            DiagnosticCode.E002_MULTIPLE_H1,
            DiagnosticCode.E005_INVALID_MARKDOWN,
        ],
        context={
            "description": "No recognizable structure — H1 error AND no sections.",
            "check_id": "CHECK-002",
            "has_h1_error": has_h1_error,
            "section_count": len(parsed.sections),
        },
    ))

    # ── AP-CRIT-003: Encoding Disaster ──────────────────────
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CRIT_003,
        pattern_name="Encoding Disaster",
        category=AntiPatternCategory.CRITICAL,
        detected=DiagnosticCode.E003_INVALID_ENCODING in diag_codes,
        constituent_diagnostics=[DiagnosticCode.E003_INVALID_ENCODING],
        context={
            "description": "Non-UTF-8 encoding prevents reliable parsing.",
            "check_id": "CHECK-003",
        },
    ))

    # ── AP-CRIT-004: Link Void ──────────────────────────────
    total_links = sum(len(s.links) for s in parsed.sections)
    e006_count = sum(
        1 for d in diagnostics
        if d.code == DiagnosticCode.E006_BROKEN_LINKS
    )
    link_void_ratio = (e006_count / total_links) if total_links > 0 else 0.0
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CRIT_004,
        pattern_name="Link Void",
        category=AntiPatternCategory.CRITICAL,
        detected=total_links > 0 and link_void_ratio > 0.80,
        constituent_diagnostics=[DiagnosticCode.E006_BROKEN_LINKS],
        context={
            "description": ">80% of links are broken or malformed.",
            "check_id": "CHECK-004",
            "total_links": total_links,
            "broken_links": e006_count,
            "ratio": round(link_void_ratio, 3),
        },
    ))

    return results
```

### 3.2 Decision Trees

#### AP-CRIT-001: Ghost File

```
E007_EMPTY_FILE in diagnostics?
  ├── Yes → detected = True
  └── No  → detected = False
```

#### AP-CRIT-002: Structure Chaos

```
(E001 OR E002) in diagnostics?
  │
  ├── Yes → sections count == 0?
  │           ├── Yes → detected = True
  │           └── No  → detected = False (partial structure exists)
  │
  └── No  → detected = False
```

#### AP-CRIT-003: Encoding Disaster

```
E003_INVALID_ENCODING in diagnostics?
  ├── Yes → detected = True
  └── No  → detected = False
```

#### AP-CRIT-004: Link Void

```
total_links > 0?
  │
  ├── Yes → E006 count / total_links > 0.80?
  │           ├── Yes → detected = True
  │           └── No  → detected = False
  │
  └── No  → detected = False (no links to evaluate)
```

---

## 4. Deliverables

| File                                                  | Description      |
| ----------------------------------------------------- | ---------------- |
| `src/docstratum/validation/anti_patterns/critical.py` | Detection module |
| `tests/validation/anti_patterns/test_critical.py`     | Unit tests       |

---

## 5. Test Plan (12 tests)

| #   | Test Name                                 | Input               | Expected                               |
| --- | ----------------------------------------- | ------------------- | -------------------------------------- |
| 1   | `test_ghost_file_detected`                | E007 in diagnostics | CRIT-001 detected=True                 |
| 2   | `test_ghost_file_not_detected`            | No E007             | CRIT-001 detected=False                |
| 3   | `test_structure_chaos_e001_no_sections`   | E001 + 0 sections   | CRIT-002 detected=True                 |
| 4   | `test_structure_chaos_e002_no_sections`   | E002 + 0 sections   | CRIT-002 detected=True                 |
| 5   | `test_structure_chaos_e001_with_sections` | E001 + 3 sections   | CRIT-002 detected=False                |
| 6   | `test_encoding_disaster_detected`         | E003 in diagnostics | CRIT-003 detected=True                 |
| 7   | `test_encoding_disaster_not_detected`     | No E003             | CRIT-003 detected=False                |
| 8   | `test_link_void_above_threshold`          | 10 links, 9 E006    | CRIT-004 detected=True (90%)           |
| 9   | `test_link_void_at_threshold`             | 10 links, 8 E006    | CRIT-004 detected=False (80% = not >)  |
| 10  | `test_link_void_no_links`                 | 0 links             | CRIT-004 detected=False                |
| 11  | `test_all_four_returned`                  | Any input           | Exactly 4 AntiPatternDetection objects |
| 12  | `test_critical_context_fields`            | CRIT-004 detected   | Context includes ratio, counts         |
