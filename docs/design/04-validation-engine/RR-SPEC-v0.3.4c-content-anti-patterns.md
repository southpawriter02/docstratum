# v0.3.4c — Content Anti-Patterns

> **Version:** v0.3.4c
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.4-anti-pattern-detection.md](RR-SPEC-v0.3.4-anti-pattern-detection.md)
> **Depends On:** L2–L3 diagnostics (W003, W004, W006, W007, W011), `ParsedLlmsTxt`

---

## 1. Purpose

v0.3.4c detects **9 content anti-patterns** — patterns indicating degraded content quality that impairs LLM comprehension. Of these, **7 are active** at v0.3.x and **2 are deferred** until L4 diagnostic codes are available (v0.9.0).

Content anti-patterns feed **DS-VC-APD-004** (3 pts / 20 anti-pattern dimension).

### 1.1 User Story

> As a documentation author, I want to know if my file's content exhibits patterns like duplicated text, missing examples, or bare URL lists, so that I can address the root cause rather than fix symptoms one by one.

---

## 2. Anti-Pattern Definitions

### 2.1 Active Patterns (7)

| ID          | Name                      | Detection Rule                               | Constituent Diagnostics     |
| ----------- | ------------------------- | -------------------------------------------- | --------------------------- |
| AP-CONT-001 | **Copy-Paste Plague**     | ≥3 sections with >90% text similarity        | Heuristic (text comparison) |
| AP-CONT-002 | **Blank Canvas**          | ≥2 sections with W011 + placeholder patterns | W011                        |
| AP-CONT-004 | **Link Desert**           | W003 count / total links > 60%               | W003                        |
| AP-CONT-005 | **Outdated Oracle**       | Deprecated API pattern heuristic             | Heuristic                   |
| AP-CONT-006 | **Example Void**          | W004 emitted                                 | W004                        |
| AP-CONT-007 | **Formulaic Description** | W006 emitted                                 | W006                        |
| AP-CONT-009 | **Versionless Drift**     | W007 emitted                                 | W007                        |

### 2.2 Deferred Patterns (2)

| ID          | Name              | Dependency                 | Detection Rule |
| ----------- | ----------------- | -------------------------- | -------------- |
| AP-CONT-003 | **Jargon Jungle** | I007 (L4 readability)      | I007 ≥5 times  |
| AP-CONT-008 | **Silent Agent**  | I001 (L4 LLM instructions) | I001 emitted   |

---

## 3. Detection Logic

### 3.1 Implementation

```python
"""Implements v0.3.4c — Content Anti-Pattern Detection."""

import re
from difflib import SequenceMatcher
from typing import Optional

from docstratum.schema.constants import AntiPatternCategory, AntiPatternID
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.parsed import ParsedLlmsTxt, ParsedSection
from docstratum.schema.validation import ValidationDiagnostic

from .detector import AntiPatternDetection

# Patterns that indicate deprecated/outdated API usage
DEPRECATED_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bdeprecated\b", re.IGNORECASE),
    re.compile(r"\blegacy\b", re.IGNORECASE),
    re.compile(r"\bobsolete\b", re.IGNORECASE),
    re.compile(r"\bend[- ]?of[- ]?life\b", re.IGNORECASE),
    re.compile(r"\bno longer (?:supported|maintained)\b", re.IGNORECASE),
]

# Common placeholder pattern fragments
PLACEHOLDER_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b"),
    re.compile(r"\bLorem ipsum\b", re.IGNORECASE),
    re.compile(r"\bcoming soon\b", re.IGNORECASE),
    re.compile(r"\bunder construction\b", re.IGNORECASE),
]


def detect_content(
    diagnostics: list[ValidationDiagnostic],
    parsed: ParsedLlmsTxt,
) -> list[AntiPatternDetection]:
    """Detect 9 content anti-patterns (7 active, 2 deferred)."""
    diag_codes = {d.code for d in diagnostics}
    results: list[AntiPatternDetection] = []

    # ── AP-CONT-001: Copy-Paste Plague ──────────────────────
    results.append(_detect_copy_paste(parsed))

    # ── AP-CONT-002: Blank Canvas ───────────────────────────
    results.append(_detect_blank_canvas(diagnostics, parsed))

    # ── AP-CONT-003: Jargon Jungle (DEFERRED) ──────────────
    i007_count = sum(
        1 for d in diagnostics
        if d.code == DiagnosticCode.I007_READABILITY_CONCERN
    ) if hasattr(DiagnosticCode, "I007_READABILITY_CONCERN") else 0
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CONT_003,
        pattern_name="Jargon Jungle",
        category=AntiPatternCategory.CONTENT,
        detected=i007_count >= 5,
        constituent_diagnostics=[],
        context={
            "check_id": "CHECK-012",
            "description": "Heavy jargon without definitions.",
            "deferred": True,
            "deferred_reason": "Requires I007 (L4 readability). "
                               "Active when v0.9.0 emits L4 codes.",
            "i007_count": i007_count,
            "threshold": 5,
        },
    ))

    # ── AP-CONT-004: Link Desert ────────────────────────────
    total_links = sum(len(s.links) for s in parsed.sections)
    w003_count = sum(
        1 for d in diagnostics
        if d.code == DiagnosticCode.W003_LINK_MISSING_DESCRIPTION
    )
    link_desert_ratio = (w003_count / total_links) if total_links > 0 else 0.0
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CONT_004,
        pattern_name="Link Desert",
        category=AntiPatternCategory.CONTENT,
        detected=total_links > 0 and link_desert_ratio > 0.60,
        constituent_diagnostics=[
            DiagnosticCode.W003_LINK_MISSING_DESCRIPTION,
        ],
        context={
            "check_id": "CHECK-013",
            "description": ">60% of links lack descriptions.",
            "total_links": total_links,
            "undescribed_links": w003_count,
            "ratio": round(link_desert_ratio, 3),
            "threshold": 0.60,
        },
    ))

    # ── AP-CONT-005: Outdated Oracle ────────────────────────
    results.append(_detect_outdated_oracle(parsed))

    # ── AP-CONT-006: Example Void ───────────────────────────
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CONT_006,
        pattern_name="Example Void",
        category=AntiPatternCategory.CONTENT,
        detected=DiagnosticCode.W004_NO_CODE_EXAMPLES in diag_codes,
        constituent_diagnostics=[DiagnosticCode.W004_NO_CODE_EXAMPLES],
        context={
            "check_id": "CHECK-015",
            "description": "No code examples found.",
        },
    ))

    # ── AP-CONT-007: Formulaic Description ──────────────────
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CONT_007,
        pattern_name="Formulaic Description",
        category=AntiPatternCategory.CONTENT,
        detected=DiagnosticCode.W006_FORMULAIC_DESCRIPTION in diag_codes,
        constituent_diagnostics=[DiagnosticCode.W006_FORMULAIC_DESCRIPTION],
        context={
            "check_id": "CHECK-019",
            "description": "Auto-generated description patterns detected.",
        },
    ))

    # ── AP-CONT-008: Silent Agent (DEFERRED) ────────────────
    i001_emitted = (
        DiagnosticCode.I001_NO_LLM_INSTRUCTIONS in diag_codes
        if hasattr(DiagnosticCode, "I001_NO_LLM_INSTRUCTIONS")
        else False
    )
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CONT_008,
        pattern_name="Silent Agent",
        category=AntiPatternCategory.CONTENT,
        detected=i001_emitted,
        constituent_diagnostics=[],
        context={
            "check_id": "CHECK-020",
            "description": "No LLM-facing guidance.",
            "deferred": True,
            "deferred_reason": "Requires I001 (L4 LLM instructions). "
                               "Active when v0.9.0 emits L4 codes.",
        },
    ))

    # ── AP-CONT-009: Versionless Drift ──────────────────────
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CONT_009,
        pattern_name="Versionless Drift",
        category=AntiPatternCategory.CONTENT,
        detected=(
            DiagnosticCode.W007_MISSING_VERSION_METADATA in diag_codes
        ),
        constituent_diagnostics=[
            DiagnosticCode.W007_MISSING_VERSION_METADATA,
        ],
        context={
            "check_id": "CHECK-021",
            "description": "No version/date metadata found.",
        },
    ))

    return results


def _detect_copy_paste(parsed: ParsedLlmsTxt) -> AntiPatternDetection:
    """AP-CONT-001: ≥3 sections with >90% text similarity."""
    sections = parsed.sections
    similar_pairs: list[tuple[str, str, float]] = []

    for i in range(len(sections)):
        for j in range(i + 1, len(sections)):
            text_a = sections[i].raw_content.strip()
            text_b = sections[j].raw_content.strip()

            # Skip very short sections (< 50 chars)
            if len(text_a) < 50 or len(text_b) < 50:
                continue

            ratio = SequenceMatcher(None, text_a, text_b).ratio()
            if ratio > 0.90:
                similar_pairs.append((
                    sections[i].name, sections[j].name, round(ratio, 3)
                ))

    return AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CONT_001,
        pattern_name="Copy-Paste Plague",
        category=AntiPatternCategory.CONTENT,
        detected=len(similar_pairs) >= 3,
        constituent_diagnostics=[],
        context={
            "check_id": "CHECK-010",
            "description": "≥3 section pairs with >90% text similarity.",
            "similar_pairs_count": len(similar_pairs),
            "similar_pairs": [
                {"a": a, "b": b, "ratio": r} for a, b, r in similar_pairs[:5]
            ],
            "threshold_pairs": 3,
            "similarity_threshold": 0.90,
        },
    )


def _detect_blank_canvas(
    diagnostics: list[ValidationDiagnostic],
    parsed: ParsedLlmsTxt,
) -> AntiPatternDetection:
    """AP-CONT-002: ≥2 sections with W011 AND placeholder patterns."""
    w011_sections: list[str] = []
    for d in diagnostics:
        if d.code == DiagnosticCode.W011_EMPTY_SECTIONS:
            section_name = d.context.get("section_name", "unknown")
            w011_sections.append(section_name)

    # Also check for placeholder patterns in section content
    placeholder_sections: list[str] = []
    for section in parsed.sections:
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(section.raw_content):
                placeholder_sections.append(section.name)
                break

    # Combine: sections that are either empty (W011) or contain placeholders
    affected_sections = set(w011_sections) | set(placeholder_sections)

    return AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CONT_002,
        pattern_name="Blank Canvas",
        category=AntiPatternCategory.CONTENT,
        detected=len(affected_sections) >= 2,
        constituent_diagnostics=[DiagnosticCode.W011_EMPTY_SECTIONS],
        context={
            "check_id": "CHECK-011",
            "description": "≥2 sections are empty or contain placeholders.",
            "empty_sections": w011_sections,
            "placeholder_sections": placeholder_sections,
            "total_affected": len(affected_sections),
            "threshold": 2,
        },
    )


def _detect_outdated_oracle(parsed: ParsedLlmsTxt) -> AntiPatternDetection:
    """AP-CONT-005: Deprecated/outdated API pattern heuristic."""
    deprecated_hits: list[dict] = []

    for section in parsed.sections:
        for pattern in DEPRECATED_PATTERNS:
            matches = pattern.findall(section.raw_content)
            if matches:
                deprecated_hits.append({
                    "section": section.name,
                    "keyword": matches[0],
                    "count": len(matches),
                })

    # Threshold: ≥3 distinct sections contain deprecated keywords
    sections_with_hits = len({h["section"] for h in deprecated_hits})

    return AntiPatternDetection(
        pattern_id=AntiPatternID.AP_CONT_005,
        pattern_name="Outdated Oracle",
        category=AntiPatternCategory.CONTENT,
        detected=sections_with_hits >= 3,
        constituent_diagnostics=[],
        context={
            "check_id": "CHECK-014",
            "description": "≥3 sections contain deprecated/outdated indicators.",
            "sections_with_deprecated_keywords": sections_with_hits,
            "hits": deprecated_hits[:10],
            "threshold": 3,
            "note": "Heuristic-based detection; may produce false positives.",
        },
    )
```

### 3.2 Decision Trees

#### AP-CONT-001: Copy-Paste Plague

```
For each pair of sections (i, j):
  │
  ├── Both sections ≥50 chars?
  │     ├── No  → Skip pair
  │     └── Yes → SequenceMatcher ratio > 0.90?
  │                 ├── Yes → Add to similar_pairs
  │                 └── No  → Skip pair
  │
  └── len(similar_pairs) ≥ 3?
        ├── Yes → detected = True
        └── No  → detected = False
```

#### AP-CONT-002: Blank Canvas

```
Count sections that are either:
  - W011 (empty section diagnostic)
  - OR contain placeholder patterns (TODO, TBD, Lorem ipsum, etc.)
  │
  └── affected_count ≥ 2?
        ├── Yes → detected = True
        └── No  → detected = False
```

#### AP-CONT-004: Link Desert

```
total_links > 0?
  │
  ├── No  → detected = False
  └── Yes → W003 count / total_links > 60%?
              ├── Yes → detected = True
              └── No  → detected = False
```

#### AP-CONT-005: Outdated Oracle

```
For each section:
  │
  └── Contains "deprecated", "legacy", "obsolete", etc.?
        └── Count sections with hits
              │
              └── sections_with_hits ≥ 3?
                    ├── Yes → detected = True
                    └── No  → detected = False
```

#### AP-CONT-006/007/009: Direct Diagnostic Mapping

```
Corresponding diagnostic code in diag_codes?
  ├── Yes → detected = True
  └── No  → detected = False
```

---

## 4. Edge Cases

| Case                                     | Behavior                      | Rationale                                      |
| ---------------------------------------- | ----------------------------- | ---------------------------------------------- |
| Zero sections                            | Most patterns = False         | No content to evaluate                         |
| Very short sections (< 50 chars)         | Skipped by Copy-Paste Plague  | Trivially similar due to length                |
| Placeholder in blockquote (not section)  | Not detected by Blank Canvas  | Only section content is checked                |
| "Deprecated" in changelog section        | May trigger Outdated Oracle   | Heuristic limitation — accepts false positives |
| I007 code not yet in DiagnosticCode enum | Jargon Jungle always False    | Graceful degradation via `hasattr` check       |
| Link Desert with W003 exactly at 60%     | Not detected (threshold is >) | Consistent with CON-008 threshold convention   |

---

## 5. Deliverables

| File                                                 | Description      |
| ---------------------------------------------------- | ---------------- |
| `src/docstratum/validation/anti_patterns/content.py` | Detection module |
| `tests/validation/anti_patterns/test_content.py`     | Unit tests       |

---

## 6. Test Plan (18 tests)

| #   | Test Name                                | Input                             | Expected                               |
| --- | ---------------------------------------- | --------------------------------- | -------------------------------------- |
| 1   | `test_copy_paste_plague_detected`        | 4 sections with identical content | CONT-001 detected                      |
| 2   | `test_copy_paste_plague_below_threshold` | 2 similar pairs                   | CONT-001 not detected                  |
| 3   | `test_copy_paste_short_sections_skipped` | 5 identical 10-char sections      | CONT-001 not detected                  |
| 4   | `test_blank_canvas_detected`             | 2 × W011 + placeholder sections   | CONT-002 detected                      |
| 5   | `test_blank_canvas_one_section`          | 1 × W011                          | CONT-002 not detected                  |
| 6   | `test_jargon_jungle_deferred`            | No I007 in enum                   | CONT-003 detected=False, deferred=True |
| 7   | `test_link_desert_above_threshold`       | 10 links, 7 × W003                | CONT-004 detected                      |
| 8   | `test_link_desert_no_links`              | 0 links                           | CONT-004 not detected                  |
| 9   | `test_outdated_oracle_detected`          | 3 sections with "deprecated"      | CONT-005 detected                      |
| 10  | `test_outdated_oracle_below_threshold`   | 2 sections with "legacy"          | CONT-005 not detected                  |
| 11  | `test_example_void_detected`             | W004 in diagnostics               | CONT-006 detected                      |
| 12  | `test_example_void_not_detected`         | No W004                           | CONT-006 not detected                  |
| 13  | `test_formulaic_description_detected`    | W006 in diagnostics               | CONT-007 detected                      |
| 14  | `test_silent_agent_deferred`             | No I001 in enum                   | CONT-008 detected=False, deferred=True |
| 15  | `test_versionless_drift_detected`        | W007 in diagnostics               | CONT-009 detected                      |
| 16  | `test_all_nine_returned`                 | Any input                         | Exactly 9 detections                   |
| 17  | `test_deferred_context_fields`           | CONT-003/008                      | Context includes deferred=True, reason |
| 18  | `test_link_desert_context`               | CONT-004 detected                 | Context includes ratio, counts         |
