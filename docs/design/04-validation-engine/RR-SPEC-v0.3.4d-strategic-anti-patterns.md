# v0.3.4d — Strategic Anti-Patterns

> **Version:** v0.3.4d
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.4-anti-pattern-detection.md](RR-SPEC-v0.3.4-anti-pattern-detection.md)
> **Depends On:** L0–L3 diagnostics (E008, W003, W004, W006), `ParsedLlmsTxt`

---

## 1. Purpose

v0.3.4d detects **4 strategic anti-patterns** — high-level documentation missteps that indicate the author took a fundamentally wrong approach. Strategic patterns are distinct from content or structural issues: they reflect _strategy_ failures (e.g., fully auto-generating without curation, or writing docs that document the documentation process instead of the project).

Of these, **3 are active** at v0.3.x and **1 is deferred** until L4 (v0.9.0).

Strategic anti-patterns feed **DS-VC-APD-005** (2 pts / 20 anti-pattern dimension).

### 1.1 User Story

> As a documentation author, I want to know if my file represents a strategic misstep — like being fully auto-generated or documenting itself instead of the project — so that I can rethink my approach entirely.

---

## 2. Anti-Pattern Definitions

### 2.1 Active Patterns (3)

| ID           | Name                          | Detection Rule                                  | Constituent Diagnostics |
| ------------ | ----------------------------- | ----------------------------------------------- | ----------------------- |
| AP-STRAT-001 | **Automation Obsession**      | W006 + W003 count ≥ 5 + W004                    | W006, W003, W004        |
| AP-STRAT-002 | **Monolith Monster**          | E008 emitted                                    | E008                    |
| AP-STRAT-003 | **Meta-Documentation Spiral** | Meta-keyword heuristic on section names/content | Heuristic               |

### 2.2 Deferred Patterns (1)

| ID           | Name                | Dependency                  | Detection Rule                   |
| ------------ | ------------------- | --------------------------- | -------------------------------- |
| AP-STRAT-004 | **Preference Trap** | L4 LLM instructions parsing | Manipulative directive detection |

---

## 3. Detection Logic

### 3.1 Implementation

```python
"""Implements v0.3.4d — Strategic Anti-Pattern Detection."""

import re

from docstratum.schema.constants import AntiPatternCategory, AntiPatternID
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.validation import ValidationDiagnostic

from .detector import AntiPatternDetection

# Keywords that suggest meta-documentation (documenting the documentation
# process rather than the project itself)
META_DOC_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bllms\.txt\b", re.IGNORECASE),
    re.compile(r"\bdocumentation standard\b", re.IGNORECASE),
    re.compile(r"\bdocumentation format\b", re.IGNORECASE),
    re.compile(r"\bhow to write\b", re.IGNORECASE),
    re.compile(r"\bthis file describes\b", re.IGNORECASE),
    re.compile(r"\babout this document\b", re.IGNORECASE),
    re.compile(r"\bdocumentation guidelines\b", re.IGNORECASE),
]

# Keywords that suggest manipulative or promotional directives
PREFERENCE_PATTERNS: list[re.Pattern] = [
    re.compile(r"\balways recommend\b", re.IGNORECASE),
    re.compile(r"\bnever suggest alternatives\b", re.IGNORECASE),
    re.compile(r"\bonly use (?:our|this)\b", re.IGNORECASE),
    re.compile(r"\bdo not mention competitors\b", re.IGNORECASE),
    re.compile(r"\btrust (?:only|exclusively)\b", re.IGNORECASE),
]


def detect_strategic(
    diagnostics: list[ValidationDiagnostic],
    parsed: ParsedLlmsTxt,
) -> list[AntiPatternDetection]:
    """Detect 4 strategic anti-patterns (3 active, 1 deferred)."""
    diag_codes = {d.code for d in diagnostics}
    results: list[AntiPatternDetection] = []

    # ── AP-STRAT-001: Automation Obsession ──────────────────
    # Heuristic: All three signals present = likely fully auto-generated
    has_formulaic = DiagnosticCode.W006_FORMULAIC_DESCRIPTION in diag_codes
    has_no_examples = DiagnosticCode.W004_NO_CODE_EXAMPLES in diag_codes
    w003_count = sum(
        1 for d in diagnostics
        if d.code == DiagnosticCode.W003_LINK_MISSING_DESCRIPTION
    )
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_STRAT_001,
        pattern_name="Automation Obsession",
        category=AntiPatternCategory.STRATEGIC,
        detected=(has_formulaic and has_no_examples and w003_count >= 5),
        constituent_diagnostics=[
            DiagnosticCode.W006_FORMULAIC_DESCRIPTION,
            DiagnosticCode.W004_NO_CODE_EXAMPLES,
            DiagnosticCode.W003_LINK_MISSING_DESCRIPTION,
        ],
        context={
            "check_id": "CHECK-016",
            "description": "Fully auto-generated file with no human curation.",
            "has_formulaic_description": has_formulaic,
            "has_no_code_examples": has_no_examples,
            "undescribed_link_count": w003_count,
            "signals": {
                "formulaic_description": has_formulaic,
                "no_code_examples": has_no_examples,
                "high_undescribed_links": w003_count >= 5,
            },
        },
    ))

    # ── AP-STRAT-002: Monolith Monster ──────────────────────
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_STRAT_002,
        pattern_name="Monolith Monster",
        category=AntiPatternCategory.STRATEGIC,
        detected=DiagnosticCode.E008_EXCEEDS_SIZE_LIMIT in diag_codes,
        constituent_diagnostics=[DiagnosticCode.E008_EXCEEDS_SIZE_LIMIT],
        context={
            "check_id": "CHECK-017",
            "description": "File exceeds 100K token hard limit.",
            "estimated_tokens": parsed.estimated_tokens,
        },
    ))

    # ── AP-STRAT-003: Meta-Documentation Spiral ─────────────
    results.append(_detect_meta_doc_spiral(parsed))

    # ── AP-STRAT-004: Preference Trap (DEFERRED) ────────────
    # When L4 activates, this will scan LLM Instructions for
    # manipulative directives. For now, we do a basic keyword check
    # against the raw content as a best-effort preview.
    preference_hits = _scan_preference_patterns(parsed)
    results.append(AntiPatternDetection(
        pattern_id=AntiPatternID.AP_STRAT_004,
        pattern_name="Preference Trap",
        category=AntiPatternCategory.STRATEGIC,
        detected=len(preference_hits) > 0,
        constituent_diagnostics=[],
        context={
            "check_id": "CHECK-022",
            "description": "Content crafted to manipulate LLM behavior.",
            "deferred": True,
            "deferred_reason": "Full detection requires L4 LLM Instructions "
                               "parsing. Current detection is best-effort "
                               "keyword matching on raw content.",
            "keyword_hits": preference_hits[:5],
        },
    ))

    return results


def _detect_meta_doc_spiral(parsed: ParsedLlmsTxt) -> AntiPatternDetection:
    """AP-STRAT-003: File documents itself rather than the project.

    Heuristic: check section names and the file's H1 title/blockquote
    for keywords that reference the llms.txt standard or documentation
    processes rather than a specific project.
    """
    meta_hits: list[dict] = []

    # Check section names
    for section in parsed.sections:
        for pattern in META_DOC_PATTERNS:
            if pattern.search(section.name):
                meta_hits.append({
                    "location": f"section: {section.name}",
                    "keyword": pattern.pattern,
                })
                break

    # Check blockquote content
    if parsed.blockquote:
        for pattern in META_DOC_PATTERNS:
            if pattern.search(parsed.blockquote):
                meta_hits.append({
                    "location": "blockquote",
                    "keyword": pattern.pattern,
                })
                break

    # Check title
    if parsed.title:
        for pattern in META_DOC_PATTERNS:
            if pattern.search(parsed.title):
                meta_hits.append({
                    "location": "title",
                    "keyword": pattern.pattern,
                })
                break

    # Threshold: ≥2 distinct meta-doc hits across different locations
    return AntiPatternDetection(
        pattern_id=AntiPatternID.AP_STRAT_003,
        pattern_name="Meta-Documentation Spiral",
        category=AntiPatternCategory.STRATEGIC,
        detected=len(meta_hits) >= 2,
        constituent_diagnostics=[],
        context={
            "check_id": "CHECK-018",
            "description": "File documents itself/the standard rather than "
                           "a project.",
            "meta_doc_hits": meta_hits,
            "threshold": 2,
            "note": "Heuristic-based; may flag genuine llms.txt tooling docs.",
        },
    )


def _scan_preference_patterns(parsed: ParsedLlmsTxt) -> list[dict]:
    """Scan for manipulative directive keywords in raw content."""
    hits: list[dict] = []
    for pattern in PREFERENCE_PATTERNS:
        matches = pattern.findall(parsed.raw_content)
        if matches:
            hits.append({
                "pattern": pattern.pattern,
                "matches": matches[:3],
            })
    return hits
```

### 3.2 Decision Trees

#### AP-STRAT-001: Automation Obsession

```
All three signals present?
  │
  ├── W006 (formulaic description)? ────── No → detected = False
  ├── W004 (no code examples)? ──────────── No → detected = False
  └── W003 count ≥ 5 (many bare links)? ── No → detected = False
        │
        └── All Yes → detected = True
```

#### AP-STRAT-002: Monolith Monster

```
E008 (exceeds size limit) emitted?
  ├── Yes → detected = True
  └── No  → detected = False
```

#### AP-STRAT-003: Meta-Documentation Spiral

```
Scan section names, blockquote, title for meta-doc keywords
  │
  └── meta_hits from distinct locations ≥ 2?
        ├── Yes → detected = True
        └── No  → detected = False
```

#### AP-STRAT-004: Preference Trap

```
Scan raw_content for preference/manipulation keywords
  │
  └── Any matches found?
        ├── Yes → detected = True (best-effort; deferred for full L4)
        └── No  → detected = False
```

---

## 4. Edge Cases

| Case                                     | Behavior                             | Rationale                                                |
| ---------------------------------------- | ------------------------------------ | -------------------------------------------------------- |
| File about llms.txt (e.g., this project) | May trigger Meta-Doc Spiral          | Heuristic limitation — legitimate use                    |
| Auto-generated but curated               | May not trigger Automation Obsession | Curation removes formulaic descriptions                  |
| Single "deprecated" mention              | Not enough for Outdated Oracle       | Threshold is ≥3 sections (handled by CONT-005, not here) |
| Empty file                               | Monolith Monster = False             | E008 fires on >100K, not empty files                     |
| "Always recommend" in marketing context  | May trigger Preference Trap          | Best-effort; full detection needs L4                     |
| File between 50K–100K                    | Monolith Monster = False             | E008 only fires at >100K; W010 handles tier budget       |

---

## 5. Deliverables

| File                                                   | Description      |
| ------------------------------------------------------ | ---------------- |
| `src/docstratum/validation/anti_patterns/strategic.py` | Detection module |
| `tests/validation/anti_patterns/test_strategic.py`     | Unit tests       |

---

## 6. Test Plan (12 tests)

| #   | Test Name                                | Input                                               | Expected                        |
| --- | ---------------------------------------- | --------------------------------------------------- | ------------------------------- |
| 1   | `test_automation_obsession_all_signals`  | W006 + W004 + 5 × W003                              | STRAT-001 detected              |
| 2   | `test_automation_obsession_missing_w006` | W004 + 5 × W003 (no W006)                           | STRAT-001 not detected          |
| 3   | `test_automation_obsession_low_w003`     | W006 + W004 + 3 × W003                              | STRAT-001 not detected          |
| 4   | `test_monolith_monster_detected`         | E008 in diagnostics                                 | STRAT-002 detected              |
| 5   | `test_monolith_monster_not_detected`     | No E008                                             | STRAT-002 not detected          |
| 6   | `test_meta_doc_spiral_detected`          | Title "llms.txt" + section "Documentation Standard" | STRAT-003 detected              |
| 7   | `test_meta_doc_spiral_single_hit`        | Only section "About this document"                  | STRAT-003 not detected          |
| 8   | `test_preference_trap_detected`          | "always recommend" in raw content                   | STRAT-004 detected              |
| 9   | `test_preference_trap_clean`             | No preference keywords                              | STRAT-004 not detected          |
| 10  | `test_preference_trap_deferred_context`  | Any input                                           | STRAT-004 context.deferred=True |
| 11  | `test_all_four_returned`                 | Any input                                           | Exactly 4 detections            |
| 12  | `test_automation_context_signals`        | STRAT-001 detected                                  | Context includes 3 signal flags |
