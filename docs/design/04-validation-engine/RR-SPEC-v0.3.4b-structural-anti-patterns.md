# v0.3.4b — Structural Anti-Patterns

> **Version:** v0.3.4b
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.4-anti-pattern-detection.md](RR-SPEC-v0.3.4-anti-pattern-detection.md)
> **Depends On:** L1–L3 diagnostics (W001, W002, W008, W011), `ParsedLlmsTxt`

---

## 1. Purpose

v0.3.4b detects **5 structural anti-patterns** — organizational weaknesses that reduce document navigability and structural quality. Unlike critical patterns, structural patterns do not cap the score; they reduce the structural dimension score (DS-QS-DIM-STR), feeding DS-VC-STR-009.

### 1.1 User Story

> As a documentation author, I want to know if my file's overall structure matches a known poor pattern so that I can reorganize it for better navigability.

---

## 2. Anti-Pattern Definitions

| ID            | Name                   | Detection Rule                                                       | Constituent Diagnostics  | CHECK     |
| ------------- | ---------------------- | -------------------------------------------------------------------- | ------------------------ | --------- |
| AP-STRUCT-001 | **Sitemap Dump**       | All sections links-only (no prose, no code) AND W001 (no blockquote) | W001, heuristic          | CHECK-005 |
| AP-STRUCT-002 | **Orphaned Sections**  | ≥3 sections with W011 (empty)                                        | W011 (multiple)          | CHECK-006 |
| AP-STRUCT-003 | **Duplicate Identity** | ≥2 sections with same `canonical_name`                               | canonical_name collision | CHECK-007 |
| AP-STRUCT-004 | **Section Shuffle**    | W008 emitted (out-of-order)                                          | W008                     | CHECK-008 |
| AP-STRUCT-005 | **Naming Nebula**      | ≥50% sections have `canonical_name is None`                          | W002 ratio               | CHECK-009 |

---

## 3. Detection Logic

### 3.1 Implementation

```python
"""Implements v0.3.4b — Structural Anti-Pattern Detection."""

from collections import Counter

from docstratum.schema.constants import AntiPatternCategory, AntiPatternID
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.validation import ValidationDiagnostic

from .detector import AntiPatternDetection


def detect_structural(
    diagnostics: list[ValidationDiagnostic],
    parsed: ParsedLlmsTxt,
) -> list[AntiPatternDetection]:
    """Detect 5 structural anti-patterns from L1–L3 diagnostics."""
    diag_codes = {d.code for d in diagnostics}
    results: list[AntiPatternDetection] = []

    # ── AP-STRUCT-001: Sitemap Dump ─────────────────────────
    # Heuristic: every section has links but no prose and no code,
    # AND the blockquote is missing (W001).
    has_no_blockquote = DiagnosticCode.W001_MISSING_BLOCKQUOTE in diag_codes
    all_sections_links_only = (
        len(parsed.sections) > 0
        and all(_is_links_only(s) for s in parsed.sections)
    )
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_STRUCT_001,
        pattern_name="Sitemap Dump",
        category=AntiPatternCategory.STRUCTURAL,
        detected=has_no_blockquote and all_sections_links_only,
        constituent_diagnostics=[DiagnosticCode.W001_MISSING_BLOCKQUOTE],
        context={
            "check_id": "CHECK-005",
            "description": "All sections are link-only with no prose or code; "
                           "file is a flat URL dump.",
            "section_count": len(parsed.sections),
            "has_blockquote": not has_no_blockquote,
        },
    ))

    # ── AP-STRUCT-002: Orphaned Sections ────────────────────
    w011_count = sum(
        1 for d in diagnostics
        if d.code == DiagnosticCode.W011_EMPTY_SECTIONS
    )
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_STRUCT_002,
        pattern_name="Orphaned Sections",
        category=AntiPatternCategory.STRUCTURAL,
        detected=w011_count >= 3,
        constituent_diagnostics=[DiagnosticCode.W011_EMPTY_SECTIONS],
        context={
            "check_id": "CHECK-006",
            "description": "≥3 sections are empty.",
            "empty_section_count": w011_count,
            "threshold": 3,
        },
    ))

    # ── AP-STRUCT-003: Duplicate Identity ───────────────────
    canonical_names = [
        s.canonical_name for s in parsed.sections
        if s.canonical_name is not None
    ]
    name_counts = Counter(canonical_names)
    duplicates = {name: count for name, count in name_counts.items() if count >= 2}
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_STRUCT_003,
        pattern_name="Duplicate Identity",
        category=AntiPatternCategory.STRUCTURAL,
        detected=len(duplicates) > 0,
        constituent_diagnostics=[],
        context={
            "check_id": "CHECK-007",
            "description": "≥2 sections map to the same canonical name.",
            "duplicate_canonical_names": {
                str(k): v for k, v in duplicates.items()
            },
        },
    ))

    # ── AP-STRUCT-004: Section Shuffle ──────────────────────
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_STRUCT_004,
        pattern_name="Section Shuffle",
        category=AntiPatternCategory.STRUCTURAL,
        detected=(
            DiagnosticCode.W008_SECTION_ORDER_NON_CANONICAL in diag_codes
        ),
        constituent_diagnostics=[
            DiagnosticCode.W008_SECTION_ORDER_NON_CANONICAL,
        ],
        context={
            "check_id": "CHECK-008",
            "description": "Canonical sections are out of order.",
        },
    ))

    # ── AP-STRUCT-005: Naming Nebula ────────────────────────
    total_sections = len(parsed.sections)
    non_canonical_count = sum(
        1 for s in parsed.sections if s.canonical_name is None
    )
    non_canonical_ratio = (
        (non_canonical_count / total_sections) if total_sections > 0 else 0.0
    )
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_STRUCT_005,
        pattern_name="Naming Nebula",
        category=AntiPatternCategory.STRUCTURAL,
        detected=total_sections > 0 and non_canonical_ratio >= 0.50,
        constituent_diagnostics=[
            DiagnosticCode.W002_NON_CANONICAL_SECTION_NAME,
        ],
        context={
            "check_id": "CHECK-009",
            "description": "≥50% of sections use non-canonical names.",
            "total_sections": total_sections,
            "non_canonical_count": non_canonical_count,
            "ratio": round(non_canonical_ratio, 3),
            "threshold": 0.50,
        },
    ))

    return results


def _is_links_only(section) -> bool:
    """Check if a section contains only links (no prose, no code).

    A section is links-only if:
    - It has ≥1 link
    - Its raw_content, stripped of link markdown and whitespace,
      contains no other substantive text.
    """
    if len(section.links) == 0:
        return False

    content = section.raw_content
    # Remove link patterns
    import re
    content = re.sub(r"-\s*\[.*?\]\(.*?\)(?::.*)?", "", content)
    # Remove headings
    content = re.sub(r"^#+\s+.*$", "", content, flags=re.MULTILINE)
    # Check remaining content
    remaining = content.strip()
    return len(remaining) < 20  # allow minor whitespace artifacts
```

### 3.2 Decision Trees

#### AP-STRUCT-001: Sitemap Dump

```
W001 (missing blockquote) emitted?
  │
  ├── No  → detected = False
  └── Yes → All sections are links-only?
              ├── Yes → detected = True
              └── No  → detected = False
```

#### AP-STRUCT-002: Orphaned Sections

```
Count of W011 diagnostics ≥ 3?
  ├── Yes → detected = True
  └── No  → detected = False
```

#### AP-STRUCT-003: Duplicate Identity

```
Any canonical_name appears ≥2 times?
  ├── Yes → detected = True (with duplicate details)
  └── No  → detected = False
```

#### AP-STRUCT-004: Section Shuffle

```
W008 emitted?
  ├── Yes → detected = True
  └── No  → detected = False
```

#### AP-STRUCT-005: Naming Nebula

```
total_sections > 0?
  │
  ├── No  → detected = False
  └── Yes → non_canonical / total ≥ 50%?
              ├── Yes → detected = True
              └── No  → detected = False
```

---

## 4. Deliverables

| File                                                    | Description      |
| ------------------------------------------------------- | ---------------- |
| `src/docstratum/validation/anti_patterns/structural.py` | Detection module |
| `tests/validation/anti_patterns/test_structural.py`     | Unit tests       |

---

## 5. Test Plan (14 tests)

| #   | Test Name                            | Input                                         | Expected                       |
| --- | ------------------------------------ | --------------------------------------------- | ------------------------------ |
| 1   | `test_sitemap_dump_detected`         | W001 + all links-only sections                | STRUCT-001 detected            |
| 2   | `test_sitemap_dump_has_blockquote`   | No W001 + links-only                          | STRUCT-001 not detected        |
| 3   | `test_sitemap_dump_has_prose`        | W001 + sections with prose                    | STRUCT-001 not detected        |
| 4   | `test_orphaned_sections_3_empty`     | 3 × W011                                      | STRUCT-002 detected            |
| 5   | `test_orphaned_sections_2_empty`     | 2 × W011                                      | STRUCT-002 not detected        |
| 6   | `test_duplicate_identity_detected`   | 2 sections with canonical_name "MASTER_INDEX" | STRUCT-003 detected            |
| 7   | `test_duplicate_identity_all_unique` | All sections unique canonical                 | STRUCT-003 not detected        |
| 8   | `test_section_shuffle_detected`      | W008 in diagnostics                           | STRUCT-004 detected            |
| 9   | `test_section_shuffle_not_detected`  | No W008                                       | STRUCT-004 not detected        |
| 10  | `test_naming_nebula_above_threshold` | 6/10 sections non-canonical (60%)             | STRUCT-005 detected            |
| 11  | `test_naming_nebula_below_threshold` | 4/10 sections non-canonical (40%)             | STRUCT-005 not detected        |
| 12  | `test_naming_nebula_zero_sections`   | No sections                                   | STRUCT-005 not detected        |
| 13  | `test_all_five_returned`             | Any input                                     | Exactly 5 detections           |
| 14  | `test_struct_context_fields`         | STRUCT-005 detected                           | Context includes ratio, counts |
