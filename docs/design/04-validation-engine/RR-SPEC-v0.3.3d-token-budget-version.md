# v0.3.3d — Token Budget & Version Metadata

> **Version:** v0.3.3d
> **Document Type:** Sub-Part Design Specification
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.3-l3-best-practices.md](RR-SPEC-v0.3.3-l3-best-practices.md)
> **Depends On:** v0.2.1b (`DocumentClassification.size_tier`), v0.2.1d (`Metadata` — schema_version, last_updated)

---

## 1. Purpose

v0.3.3d combines two related checks about documentation _currency and conciseness_:

1. **Token Budget** (W010) — Does the file exceed the recommended token limit for its size tier?
2. **Version Metadata** (W007) — Does the file contain any version or date indicator?

Both address the question: _Is this documentation appropriately scoped and timestamped?_

### 1.1 Token Budget vs. E008

E008 (L0) is the **hard size limit** (>100K tokens → pipeline stops). W010 (L3) is the **tier-appropriate budget advisory** (e.g., a Standard-tier file exceeding 4,500 tokens). They are distinct concerns at different severity levels.

| Check | Level | Severity | Threshold        | Effect         |
| ----- | ----- | -------- | ---------------- | -------------- |
| E008  | L0    | ERROR    | >100K tokens     | Pipeline stops |
| W010  | L3    | WARNING  | Exceeds tier max | Advisory       |

### 1.2 User Stories

> As a documentation author, I want to know if my file exceeds its token budget tier so that I can trim content or reclassify the document.

> As a documentation author, I want to know if version metadata is missing so that readers can assess content currency.

---

## 2. Diagnostic Codes

### W010 — TOKEN_BUDGET_EXCEEDED

| Field                 | Value                                                   |
| --------------------- | ------------------------------------------------------- |
| **Code**              | W010                                                    |
| **Severity**          | WARNING                                                 |
| **Emitted**           | Once per file (if token count exceeds tier max)         |
| **Criterion**         | DS-VC-CON-012 (4 pts / 50 content)                      |
| **Anti-Pattern Feed** | AP-STRAT-002 (Monolith Monster) when combined with E008 |

### W007 — MISSING_VERSION_METADATA

| Field                 | Value                                             |
| --------------------- | ------------------------------------------------- |
| **Code**              | W007                                              |
| **Severity**          | WARNING                                           |
| **Emitted**           | Once per file (if no version/date metadata found) |
| **Criterion**         | DS-VC-CON-013 (3 pts / 50 content)                |
| **Anti-Pattern Feed** | AP-CONT-009 (Versionless Drift)                   |

---

## 3. Check Logic

### 3.1 Token Budget Check

```python
"""Implements v0.3.3d — Token Budget & Version Metadata checks."""

import re
from typing import Optional

from docstratum.schema.classification import SizeTier
from docstratum.schema.constants import TOKEN_BUDGET_TIERS
from docstratum.schema.diagnostics import DiagnosticCode
from docstratum.schema.validation import (
    Severity,
    ValidationDiagnostic,
    ValidationLevel,
)

# Version detection patterns (deliberately permissive)
VERSION_PATTERNS: list[re.Pattern] = [
    re.compile(r"v\d+\.\d+", re.IGNORECASE),
    re.compile(r"version\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"\d{4}-\d{2}-\d{2}"),  # ISO date
    re.compile(r"last.?updated", re.IGNORECASE),
    re.compile(r"changelog", re.IGNORECASE),
]


def check_token_budget_and_version(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:
    """Check token budget compliance and version metadata presence.

    Implements DS-VC-CON-012 (token budget) and DS-VC-CON-013
    (version metadata). Emits W010 if token count exceeds tier
    budget; emits W007 if no version/date metadata found.
    """
    diagnostics: list[ValidationDiagnostic] = []

    # ── W010: Token Budget ──────────────────────────────────
    diagnostics.extend(_check_token_budget(parsed, classification))

    # ── W007: Version Metadata ──────────────────────────────
    diagnostics.extend(_check_version_metadata(parsed, file_meta))

    return diagnostics


def _check_token_budget(
    parsed: ParsedLlmsTxt,
    classification: DocumentClassification,
) -> list[ValidationDiagnostic]:
    """Emit W010 if estimated_tokens exceeds tier budget.

    Tier handling:
    - MINIMAL (<1,500 tokens): W010 not applicable (skip).
    - STANDARD (1,500–4,500):  Check against 4,500 max.
    - COMPREHENSIVE (4,500–12,000): Check against 12,000 max.
    - FULL (12,000–50,000):    Check against 50,000 max.
    - OVERSIZED (>50,000):     Check against FULL max (50,000).
    """
    tier = classification.size_tier
    tokens = parsed.estimated_tokens

    # MINIMAL files are below the smallest tier — skip
    if tier == SizeTier.MINIMAL:
        return []

    # Determine the tier max
    if tier == SizeTier.OVERSIZED:
        tier_name = "Full"
        tier_max = TOKEN_BUDGET_TIERS["full"]
    else:
        tier_name = tier.name.capitalize()
        tier_key = tier.name.lower()
        tier_max = TOKEN_BUDGET_TIERS.get(tier_key)
        if tier_max is None:
            return []  # Unknown tier — skip

    if tokens > tier_max:
        return [
            ValidationDiagnostic(
                code=DiagnosticCode.W010_TOKEN_BUDGET_EXCEEDED,
                severity=Severity.WARNING,
                message=(
                    f"File has ~{tokens:,} tokens, exceeding the "
                    f"{tier_name} tier budget of {tier_max:,}."
                ),
                level=ValidationLevel.L3_BEST_PRACTICES,
                check_id="CON-012",
                line_number=1,
                context={
                    "estimated_tokens": tokens,
                    "tier": tier_name,
                    "tier_max": tier_max,
                },
                remediation=(
                    f"Trim content to stay within {tier_max:,} tokens, "
                    "or reclassify to a higher tier if the content scope "
                    "justifies it."
                ),
            )
        ]

    return []


def _check_version_metadata(
    parsed: ParsedLlmsTxt,
    file_meta: FileMetadata,
) -> list[ValidationDiagnostic]:
    """Emit W007 if no version or date metadata found.

    Two-phase detection:
    1. Structured: Check Metadata for schema_version or last_updated.
    2. Pattern-based: Scan raw_content for version/date patterns.
    """
    # Phase 1: Structured metadata
    metadata: Optional[object] = getattr(parsed, "metadata", None)
    if metadata is not None:
        if getattr(metadata, "schema_version", None) is not None:
            return []
        if getattr(metadata, "last_updated", None) is not None:
            return []

    # Phase 2: Pattern matching on raw content
    for pattern in VERSION_PATTERNS:
        if pattern.search(parsed.raw_content):
            return []

    # No version metadata found
    return [
        ValidationDiagnostic(
            code=DiagnosticCode.W007_MISSING_VERSION_METADATA,
            severity=Severity.WARNING,
            message="No version or last-updated metadata found.",
            level=ValidationLevel.L3_BEST_PRACTICES,
            check_id="CON-013",
            line_number=1,
            context={
                "checked_structured": metadata is not None,
                "patterns_searched": len(VERSION_PATTERNS),
            },
            remediation=(
                "Add version information: 'version: 1.0', 'v2.3.1', "
                "'Last updated: 2026-02-10', or a changelog link."
            ),
        )
    ]
```

### 3.2 Decision Trees

#### Token Budget (W010)

```
classification.size_tier
  │
  ├── MINIMAL → SKIP (not applicable)
  │
  ├── STANDARD / COMPREHENSIVE / FULL
  │     └── estimated_tokens > tier_max?
  │           ├── Yes → EMIT W010
  │           └── No → PASS
  │
  └── OVERSIZED
        └── estimated_tokens > FULL max (50,000)?
              ├── Yes → EMIT W010 (against FULL tier)
              └── No → PASS (theoretically impossible for OVERSIZED)
```

#### Version Metadata (W007)

```
Metadata object exists?
  │
  ├── Yes → schema_version or last_updated present?
  │           ├── Yes → PASS
  │           └── No → Fall through to pattern scan
  │
  └── No → Fall through to pattern scan
               │
               └── Any VERSION_PATTERN matches raw_content?
                     ├── Yes → PASS
                     └── No → EMIT W007
```

### 3.3 Edge Cases

| Case                                 | Behavior                    | Rationale                                  |
| ------------------------------------ | --------------------------- | ------------------------------------------ |
| MINIMAL tier file                    | No W010 (skipped)           | Below smallest budget tier                 |
| OVERSIZED file at 60K tokens         | W010 against FULL max (50K) | OVERSIZED maps to FULL for budget purposes |
| Token count exactly at tier max      | Pass                        | Threshold is `>`, not `>=`                 |
| YAML frontmatter with `version: 1.0` | Pass (structured check)     | Metadata.schema_version populated          |
| Raw content with "v2.3" anywhere     | Pass (pattern match)        | Permissive pattern matching                |
| Raw content with "changelog" link    | Pass (pattern match)        | "changelog" signals version awareness      |
| File with "Last updated: Jan 2026"   | Pass (pattern match)        | "last updated" pattern matches             |
| File with no dates or versions       | W007                        | No temporal context available              |
| File with `2026-02-10` in body text  | Pass                        | ISO date pattern matches                   |

---

## 4. Deliverables

| File                                                          | Description  |
| ------------------------------------------------------------- | ------------ |
| `src/docstratum/validation/checks/l3_token_budget_version.py` | Check module |
| `tests/validation/checks/test_l3_token_budget_version.py`     | Unit tests   |

---

## 5. Test Plan (14 tests)

### Token Budget (W010)

| #   | Test Name                          | Input                        | Expected                                                |
| --- | ---------------------------------- | ---------------------------- | ------------------------------------------------------- |
| 1   | `test_standard_tier_within_budget` | 3,000 tokens, STANDARD       | 0 diagnostics                                           |
| 2   | `test_standard_tier_over_budget`   | 5,000 tokens, STANDARD       | 1 × W010                                                |
| 3   | `test_comprehensive_tier_over`     | 15,000 tokens, COMPREHENSIVE | 1 × W010                                                |
| 4   | `test_full_tier_within_budget`     | 40,000 tokens, FULL          | 0 diagnostics                                           |
| 5   | `test_minimal_tier_skipped`        | 500 tokens, MINIMAL          | 0 diagnostics                                           |
| 6   | `test_oversized_against_full_max`  | 60,000 tokens, OVERSIZED     | 1 × W010 (tier_max=50,000)                              |
| 7   | `test_exact_tier_max_passes`       | 4,500 tokens, STANDARD       | 0 diagnostics                                           |
| 8   | `test_w010_context_fields`         | Over budget                  | Context includes `estimated_tokens`, `tier`, `tier_max` |

### Version Metadata (W007)

| #   | Test Name                             | Input                        | Expected      |
| --- | ------------------------------------- | ---------------------------- | ------------- |
| 9   | `test_structured_version_passes`      | Metadata with schema_version | 0 diagnostics |
| 10  | `test_structured_last_updated_passes` | Metadata with last_updated   | 0 diagnostics |
| 11  | `test_pattern_version_string`         | Raw content "v2.3.1"         | 0 diagnostics |
| 12  | `test_pattern_iso_date`               | Raw content "2026-02-10"     | 0 diagnostics |
| 13  | `test_no_version_metadata`            | No metadata, no patterns     | 1 × W007      |
| 14  | `test_changelog_reference_passes`     | Raw content "See changelog"  | 0 diagnostics |
