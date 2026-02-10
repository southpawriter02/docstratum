# v0.3.2c — Section Content Quality

> **Version:** v0.3.2c
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.2-l2-content-quality.md](RR-SPEC-v0.3.2-l2-content-quality.md)
> **Grounding:** DS-VC-CON-004 (Non-empty Sections, 4 pts SOFT), DS-VC-CON-005 (No Duplicate Sections, 3 pts SOFT), DS-VC-CON-007 (No Formulaic Descriptions, 3 pts SOFT)
> **Depends On:** v0.2.0 (`ParsedSection`, `ParsedLink`), v0.2.1a (`DocumentClassification.document_type`)
> **Module:** `src/docstratum/validation/checks/l2_section_content.py`
> **Tests:** `tests/test_validation_l2_section_content.py`

---

## 1. Purpose

Verify that sections contain meaningful content and are not empty shells, duplicates, or filled with formulaic copy-paste descriptions. This check is the "content audit" of L2 — it answers: does the structural skeleton (validated at L1) actually contain substance?

This check combines three criteria and two informational observations into a single module:

| Check                           | Criterion     | Code | Severity |
| ------------------------------- | ------------- | ---- | -------- |
| Empty section detection         | DS-VC-CON-004 | W011 | WARNING  |
| Formulaic description detection | DS-VC-CON-007 | W006 | WARNING  |
| Relative URL observation        | —             | I004 | INFO     |
| Type 2 Full observation         | —             | I005 | INFO     |

### 1.1 Why DS-VC-CON-005 (No Duplicate Sections) Is Not a Standalone Check Here

CON-005 (No Duplicate Sections) checks for identical H2 heading names. Its official spec notes that it "does not emit a standalone diagnostic code" — duplicates are covered by anti-pattern **AP-STRUCT-003 (Duplicate Identity)**, which runs in the anti-pattern detection pipeline (v0.3.4b). v0.3.2c does **not** implement duplicate section detection directly.

---

## 2. Diagnostic Codes

| Code | Severity | Criterion     | Message                                                                 | Remediation                                                              |
| ---- | -------- | ------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| W011 | WARNING  | DS-VC-CON-004 | One or more sections contain no meaningful content.                     | Add content or remove empty sections. Placeholder sections waste tokens. |
| W006 | WARNING  | DS-VC-CON-007 | Multiple sections use identical or near-identical description patterns. | Write unique, specific descriptions for each section.                    |
| I004 | INFO     | —             | Relative URLs found in link entries.                                    | Convert relative URLs to absolute or document the base URL.              |
| I005 | INFO     | —             | File classified as Type 2 Full (>250 KB).                               | — (informational only)                                                   |

---

## 3. Check Logic

```python
"""L2 section content quality check.

Verifies that sections contain meaningful content, detects formulaic
descriptions, and emits informational observations about relative
URLs and Type 2 Full classification.

Implements v0.3.2c. Criteria: DS-VC-CON-004, CON-005 (deferred),
CON-007.
"""

import re
from itertools import combinations


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check section content quality.

    Four independent sub-checks:
    1. W011: Empty sections (no links, no prose, only header)
    2. W006: Formulaic descriptions (>80% avg similarity across ≥5 descriptions)
    3. I004: Relative URLs detected (once per file)
    4. I005: Type 2 Full classification (once per file)

    Args:
        parsed: The parsed file model with sections.
        classification: Used for Type 2 Full detection (I005).
        file_meta: Not used by this check.

    Returns:
        List of W011, W006, I004, and/or I005 diagnostics.
    """
    diagnostics: list[ValidationDiagnostic] = []

    # --- Sub-check 1: Empty sections (W011) ---
    diagnostics.extend(_check_empty_sections(parsed))

    # --- Sub-check 2: Formulaic descriptions (W006) ---
    diagnostics.extend(_check_formulaic_descriptions(parsed))

    # --- Sub-check 3: Relative URLs (I004) ---
    diagnostics.extend(_check_relative_urls(parsed))

    # --- Sub-check 4: Type 2 Full (I005) ---
    diagnostics.extend(_check_type_2_full(classification, parsed))

    return diagnostics
```

### 3.1 Empty Section Detection (W011)

```python
def _check_empty_sections(
    parsed: "ParsedLlmsTxt",
) -> list[ValidationDiagnostic]:
    """Detect sections with no meaningful content.

    A section is "empty" if:
    - It has zero links AND
    - Its raw_content, stripped of the H2 header line and whitespace,
      is empty.

    A section containing only H3+ sub-headings (with no content under
    them) is also considered empty.

    Returns:
        List of W011 diagnostics, one per empty section.
    """
    diagnostics: list[ValidationDiagnostic] = []

    for section in parsed.sections:
        if len(section.links) > 0:
            continue  # Has links → not empty

        # Strip the H2 header line from raw_content
        content = _strip_header_line(section.raw_content)
        stripped = content.strip()

        # Also strip any H3+ sub-headings (they don't count as content)
        stripped = re.sub(r"^#{3,}\s+.*$", "", stripped, flags=re.MULTILINE).strip()

        if not stripped:
            diagnostics.append(
                ValidationDiagnostic(
                    code=DiagnosticCode.W011_EMPTY_SECTIONS,
                    severity=Severity.WARNING,
                    message=DiagnosticCode.W011_EMPTY_SECTIONS.message,
                    remediation=DiagnosticCode.W011_EMPTY_SECTIONS.remediation,
                    level=ValidationLevel.L2_CONTENT,
                    check_id="CNT-004",
                    line_number=section.start_line,
                    context=(
                        f"Section '## {section.name}' contains no links, "
                        f"paragraphs, or code blocks."
                    ),
                )
            )

    return diagnostics
```

### 3.2 Formulaic Description Detection (W006)

```python
def _check_formulaic_descriptions(
    parsed: "ParsedLlmsTxt",
) -> list[ValidationDiagnostic]:
    """Detect when descriptions follow identical boilerplate patterns.

    Uses pairwise string similarity (SequenceMatcher ratio) across
    all link descriptions. Fires W006 if average similarity exceeds
    80% across 5+ descriptions.

    Why SequenceMatcher: It's in the stdlib (no dependency), provides
    a 0–1 ratio, and is sufficient for detecting near-identical strings.
    Levenshtein/Jaro-Winkler would be faster but requires a dependency.

    Returns:
        List containing 0 or 1 W006 diagnostic.
    """
    # Collect all non-empty descriptions across all sections
    descriptions: list[str] = []
    for section in parsed.sections:
        for link in section.links:
            if link.description and link.description.strip():
                descriptions.append(link.description.strip())

    # Need ≥5 descriptions for statistical reliability
    if len(descriptions) < 5:
        return []

    # Compute pairwise similarity
    from difflib import SequenceMatcher

    similarities: list[float] = []
    for a, b in combinations(descriptions, 2):
        ratio = SequenceMatcher(None, a.lower(), b.lower()).ratio()
        similarities.append(ratio)

    avg_similarity = sum(similarities) / len(similarities)

    if avg_similarity > 0.80:
        return [
            ValidationDiagnostic(
                code=DiagnosticCode.W006_FORMULAIC_DESCRIPTIONS,
                severity=Severity.WARNING,
                message=DiagnosticCode.W006_FORMULAIC_DESCRIPTIONS.message,
                remediation=DiagnosticCode.W006_FORMULAIC_DESCRIPTIONS.remediation,
                level=ValidationLevel.L2_CONTENT,
                check_id="CNT-007",
                line_number=1,  # File-level observation
                context=(
                    f"Average pairwise description similarity is "
                    f"{avg_similarity:.1%} across {len(descriptions)} "
                    f"descriptions (threshold: 80%)."
                ),
            )
        ]

    return []
```

### 3.3 Relative URL Observation (I004)

```python
def _check_relative_urls(
    parsed: "ParsedLlmsTxt",
) -> list[ValidationDiagnostic]:
    """Detect relative URLs in link entries.

    Emits I004 once per file (not per link) if any link uses a
    relative URL (starts with './', '../', or lacks '://').

    Returns:
        List containing 0 or 1 I004 diagnostic.
    """
    for section in parsed.sections:
        for link in section.links:
            if not link.url:
                continue
            if (
                link.url.startswith("./")
                or link.url.startswith("../")
                or "://" not in link.url
            ):
                return [
                    ValidationDiagnostic(
                        code=DiagnosticCode.I004_RELATIVE_URLS_DETECTED,
                        severity=Severity.INFO,
                        message=DiagnosticCode.I004_RELATIVE_URLS_DETECTED.message,
                        remediation=DiagnosticCode.I004_RELATIVE_URLS_DETECTED.remediation,
                        level=ValidationLevel.L2_CONTENT,
                        check_id="LNK-003",
                        line_number=link.line_number,
                        context=(
                            f"Relative URL detected: '{link.url}'. "
                            f"Consider using absolute URLs for portability."
                        ),
                    )
                ]

    return []
```

### 3.4 Type 2 Full Observation (I005)

```python
def _check_type_2_full(
    classification: "DocumentClassification",
    parsed: "ParsedLlmsTxt",
) -> list[ValidationDiagnostic]:
    """Emit I005 if file is classified as Type 2 Full.

    Type 2 Full files (>250 KB) receive different treatment in
    downstream validation — some criteria are less strictly applied
    because the file likely represents an inline documentation dump.

    Returns:
        List containing 0 or 1 I005 diagnostic.
    """
    if classification.document_type == DocumentType.TYPE_2_FULL:
        return [
            ValidationDiagnostic(
                code=DiagnosticCode.I005_TYPE_2_FULL_DETECTED,
                severity=Severity.INFO,
                message=DiagnosticCode.I005_TYPE_2_FULL_DETECTED.message,
                remediation=DiagnosticCode.I005_TYPE_2_FULL_DETECTED.remediation,
                level=ValidationLevel.L2_CONTENT,
                check_id="SIZ-002",
                line_number=1,
                context=(
                    f"File size: {parsed.raw_content_length:,} bytes. "
                    f"Type 2 Full threshold: 250,000 bytes."
                ),
            )
        ]

    return []
```

---

## 4. Decision: Formulaic Detection Parameters

| Parameter            | Value                        | Rationale                                                   |
| -------------------- | ---------------------------- | ----------------------------------------------------------- |
| Similarity function  | `SequenceMatcher.ratio()`    | Stdlib, no extra dependency, 0–1 scale                      |
| Similarity threshold | 80%                          | Provisional (CON-007 spec). Calibrate against 11 specimens. |
| Minimum descriptions | 5                            | ≥5 for statistical reliability (CON-007 spec).              |
| Comparison           | Case-insensitive             | Catches "Documentation for X" vs "documentation for Y"      |
| Scope                | File-wide (all descriptions) | Not per-section — formulaic patterns span the whole file    |
| Cardinality          | 0 or 1 W006 per file         | File-level observation, not per-pair                        |

---

## 5. Acceptance Criteria

- [ ] W011 emitted per empty section (no links, no prose, only header).
- [ ] W011 not emitted for sections with at least one link, paragraph, or code block.
- [ ] W011 handles sections with only H3+ sub-headings as empty.
- [ ] W006 emitted when ≥5 descriptions have >80% avg pairwise similarity.
- [ ] W006 not emitted when <5 descriptions exist.
- [ ] W006 not emitted when similarity ≤80%.
- [ ] I004 emitted once per file when relative URLs detected.
- [ ] I004 not emitted when all URLs are absolute.
- [ ] I005 emitted when `document_type == TYPE_2_FULL`.
- [ ] I005 not emitted for other document types.
- [ ] All diagnostics use `level=L2_CONTENT`.

---

## 6. Test Plan

### `tests/test_validation_l2_section_content.py`

| Test                                    | Input                             | Expected                      |
| --------------------------------------- | --------------------------------- | ----------------------------- |
| `test_all_sections_have_content_passes` | Sections with links and prose     | `[]` (no W011)                |
| `test_empty_section_warns`              | Section with only header          | `[W011]`                      |
| `test_section_with_only_h3_is_empty`    | Section with H3 sub-headings only | `[W011]`                      |
| `test_section_with_link_not_empty`      | Section with 1 link               | No W011                       |
| `test_multiple_empty_sections`          | 3 empty sections                  | 3 × W011                      |
| `test_formulaic_above_threshold`        | 6 descriptions, 90% similarity    | `[W006]`                      |
| `test_formulaic_below_threshold`        | 6 descriptions, 70% similarity    | No W006                       |
| `test_formulaic_below_min_count`        | 3 descriptions, 95% similarity    | No W006                       |
| `test_varied_descriptions_pass`         | 8 unique descriptions             | No W006                       |
| `test_relative_url_emits_i004`          | Link with `./docs/api.md`         | `[I004]`                      |
| `test_absolute_url_no_i004`             | Link with `https://example.com`   | No I004                       |
| `test_i004_fires_once`                  | 3 relative URLs                   | 1 × I004                      |
| `test_type_2_full_emits_i005`           | `document_type=TYPE_2_FULL`       | `[I005]`                      |
| `test_type_1_no_i005`                   | `document_type=TYPE_1_SHORT`      | No I005                       |
| `test_w011_context_shows_section_name`  | Empty "## References"             | Context contains "References" |
| `test_w006_context_shows_similarity`    | Formulaic descs                   | Context contains "%"          |

---

## 7. Design Decisions

| Decision                                | Choice | Rationale                                                                              |
| --------------------------------------- | ------ | -------------------------------------------------------------------------------------- |
| CON-005 deferred to v0.3.4b AP pipeline | Yes    | Duplicate sections are anti-pattern AP-STRUCT-003, not a per-section diagnostic.       |
| W006 is file-level (not per section)    | Yes    | Formulaic patterns span the whole file — it's a systemic observation.                  |
| I004 fires once per file                | Yes    | Relative URLs are an observation, not a per-link quality issue.                        |
| I005 fires once per file                | Yes    | Type 2 Full is a file classification, not a per-section issue.                         |
| SequenceMatcher for similarity          | Yes    | Stdlib, no dependency. Adequate for detecting near-identical strings.                  |
| H3+ only = empty                        | Yes    | A section with only sub-headings and no content under them is structurally misleading. |
