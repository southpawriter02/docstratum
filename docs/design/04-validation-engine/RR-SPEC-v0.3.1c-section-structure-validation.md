# v0.3.1c — Section Structure Validation

> **Version:** v0.3.1c
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.1-l1-structural.md](RR-SPEC-v0.3.1-l1-structural.md)
> **Grounding:** DS-VC-STR-004 (H2 Section Structure, 4 pts HARD), DS-VC-STR-006 (No Heading Violations, 3 pts SOFT), v0.0.1a ABNF grammar (`section = "##" SP section-name CRLF`)
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.sections`, `ParsedLlmsTxt.raw_content`)
> **Module:** `src/docstratum/validation/checks/l1_section_structure.py`
> **Tests:** `tests/test_validation_l1_section_structure.py`

---

## 1. Purpose

Verify two related structural properties of the document's heading hierarchy:

1. **H2 sections exist** (DS-VC-STR-004): At least one H2-delimited section is present. Without H2 sections, the file has no navigable structure for AI agents. This is a HARD criterion worth 4 structural points.

2. **No H3+ as section headers** (DS-VC-STR-006): H3, H4, H5, H6 headings are not used as top-level section dividers. H3+ may appear _within_ H2 sections as sub-structure, but should never appear at the document root level (between H2s or where an H2 is expected). This is a SOFT criterion worth 3 structural points.

These two checks are combined into a single sub-part because they are complementary: STR-004 ensures H2 structure exists, STR-006 ensures H3+ doesn't usurp it.

### 1.1 Diagnostic Code Gap

> [!IMPORTANT]
> Neither DS-VC-STR-004 nor DS-VC-STR-006 has a standalone diagnostic code in the current `diagnostics.py` registry. The L1-STRUCTURAL level definition (DS-VL-L1) notes: _"Their failures are captured as part of the structural validation pass/fail and reflected in the dimension score."_
>
> **Decision for v0.3.1c:** Introduce **two new WARNING codes** to make these checks explicit and diagnosable. These codes will follow the existing naming pattern and be added to `diagnostics.py` as part of v0.3.1c implementation:
>
> | New Code | Severity | Criterion     | Message                                                        |
> | -------- | -------- | ------------- | -------------------------------------------------------------- |
> | W019     | WARNING  | DS-VC-STR-004 | No H2 sections found. File has no navigable section structure. |
> | W020     | WARNING  | DS-VC-STR-006 | H3+ heading used as top-level section divider.                 |
>
> **Rationale:** Implicit structural scoring (without a code) is opaque — the user sees their score drop but doesn't know why. Explicit diagnostic codes provide actionable feedback consistent with all other validation checks.

---

## 2. Diagnostic Codes

| Code | Severity | Criterion     | Message                                                        | Remediation                                                                                           |
| ---- | -------- | ------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| W019 | WARNING  | DS-VC-STR-004 | No H2 sections found. File has no navigable section structure. | Add section headings using `## SectionName` syntax. Refer to the 11 canonical section names.          |
| W020 | WARNING  | DS-VC-STR-006 | H3+ heading used as top-level section divider. Expected H2.    | Convert `###` (or deeper) section headers to `##`. Use H3+ only for sub-structure within H2 sections. |

---

## 3. Check Logic

````python
"""L1 section structure validation check.

Verifies:
1. At least one H2 section exists (DS-VC-STR-004, W019)
2. No H3+ headings used as top-level section dividers (DS-VC-STR-006, W020)

Implements v0.3.1c.
"""


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check section heading structure.

    Two independent checks combined:
    - W019: No H2 sections at all (file has H1 but no sections)
    - W020: H3+ headings at the top level (between or instead of H2s)

    Args:
        parsed: The parsed file model.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        List of W019 and/or W020 diagnostics.
    """
    diagnostics: list[ValidationDiagnostic] = []

    # --- Check 1: H2 sections exist (DS-VC-STR-004) ---
    if len(parsed.sections) == 0:
        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.W019_NO_H2_SECTIONS,
                severity=Severity.WARNING,
                message=DiagnosticCode.W019_NO_H2_SECTIONS.message,
                remediation=DiagnosticCode.W019_NO_H2_SECTIONS.remediation,
                level=ValidationLevel.L1_STRUCTURAL,
                check_id="STR-004",
                line_number=1,
                context=(
                    "File contains an H1 title but no H2 sections. "
                    "At minimum, add one '## SectionName' heading."
                ),
            )
        )

    # --- Check 2: No H3+ as top-level dividers (DS-VC-STR-006) ---
    orphan_headings = _find_orphan_h3_plus(parsed.raw_content, parsed.sections)
    for heading_line, heading_text, heading_level in orphan_headings:
        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.W020_HEADING_LEVEL_VIOLATION,
                severity=Severity.WARNING,
                message=DiagnosticCode.W020_HEADING_LEVEL_VIOLATION.message,
                remediation=DiagnosticCode.W020_HEADING_LEVEL_VIOLATION.remediation,
                level=ValidationLevel.L1_STRUCTURAL,
                check_id="STR-006",
                line_number=heading_line,
                context=(
                    f"H{heading_level} heading '{heading_text}' appears at "
                    f"the top level. Expected '## {heading_text}' (H2)."
                ),
            )
        )

    return diagnostics


def _find_orphan_h3_plus(
    raw_content: str,
    sections: list,
) -> list[tuple[int, str, int]]:
    """Find H3+ headings that appear at the document root level.

    A heading is "orphan" if it:
    - Is H3 or deeper (###, ####, etc.)
    - Appears OUTSIDE any H2 section's content range
    - Is not inside a code fence

    Headings WITHIN H2 sections are valid sub-structure.

    Args:
        raw_content: The full raw text of the file.
        sections: The list of parsed H2 sections with line ranges.

    Returns:
        List of (line_number, heading_text, heading_level) tuples.
    """
    orphans: list[tuple[int, str, int]] = []
    in_code_block = False

    # Build set of line ranges covered by H2 sections
    h2_ranges = set()
    for section in sections:
        if hasattr(section, "start_line") and hasattr(section, "end_line"):
            for line in range(section.start_line, section.end_line + 1):
                h2_ranges.add(line)

    for line_num, line in enumerate(raw_content.splitlines(), start=1):
        stripped = line.strip()

        # Toggle code fence state
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Skip H1 and H2 (those are valid at root level)
        if stripped.startswith("# ") and not stripped.startswith("## "):
            continue
        if stripped.startswith("## ") and not stripped.startswith("### "):
            continue

        # Detect H3+ headings
        if stripped.startswith("### "):
            level = 3
        elif stripped.startswith("#### "):
            level = 4
        elif stripped.startswith("##### "):
            level = 5
        elif stripped.startswith("###### "):
            level = 6
        else:
            continue

        # Is this heading outside any H2 section range?
        if line_num not in h2_ranges:
            heading_text = stripped.lstrip("#").strip()
            orphans.append((line_num, heading_text, level))

    return orphans
````

### 3.1 Decision: W019 vs W020 Independence

W019 and W020 can fire simultaneously. A file with zero H2 sections AND H3 headings at the top level would emit both:

| File Structure                          | W019?       | W020?                       |
| --------------------------------------- | ----------- | --------------------------- |
| `# Title` + `## Sec1` + `## Sec2`       | No          | No                          |
| `# Title` only (no sections)            | Yes         | No                          |
| `# Title` + `### Sec1` + `### Sec2`     | Yes (no H2) | Yes (2×, one per orphan H3) |
| `# Title` + `## Sec1` + `### OrphanSec` | No          | Yes (1×)                    |

### 3.2 Decision: "Orphan" Definition

An H3+ heading is "orphan" only if it appears _outside_ any H2 section's line range. H3+ headings _within_ a section are valid sub-structure:

```markdown
# Project ← H1 (valid)

## Getting Started ← H2 section (valid)

### Installation ← H3 WITHIN section (valid, not orphan)

### Configuration ← H3 WITHIN section (valid, not orphan)

### Advanced Setup ← H3 between sections (ORPHAN → W020)

## API Reference ← H2 section (valid)
```

### 3.3 Decision: WARNING, Not ERROR

Both checks emit WARNINGs:

- **W019 (no H2 sections):** A title-only file is structurally minimal but not broken. The file passed L0 (has H1, has content). The lack of sections is a quality issue.
- **W020 (H3+ orphan):** 0% occurrence in the v0.0.2 calibration audit — this is extremely rare. When it occurs, it's a structural quality issue but doesn't prevent parsing.

---

## 4. Schema Changes Required

These two new codes must be added to `diagnostics.py`:

```python
# ── [v0.3.1c] Section structure diagnostics ──────────────────
W019_NO_H2_SECTIONS = (
    "W019",
    """No H2 sections found. File has no navigable section structure.
    Maps to: DS-VC-STR-004 (H2 Section Structure). Severity: WARNING.
    Note: A file with only H1 + blockquote and no sections is structurally minimal.
    Remediation: Add section headings using '## SectionName' syntax.""",
)

W020_HEADING_LEVEL_VIOLATION = (
    "W020",
    """H3+ heading used as top-level section divider. Expected H2.
    Maps to: DS-VC-STR-006 (No Heading Violations). Severity: WARNING.
    Note: 0% occurrence in v0.0.2 calibration audit. Extremely rare but detectable.
    Remediation: Convert H3+ section headers to H2. Use H3+ only within H2 sections.""",
)
```

> [!WARNING]
> This adds 2 new codes to the registry, expanding from 38 to 40 total codes. The CHANGELOG for v0.3.1c must note this expansion.

---

## 5. Acceptance Criteria

- [ ] `check()` returns W019 when `parsed.sections` is empty.
- [ ] `check()` returns W020 per orphan H3+ heading.
- [ ] `check()` returns empty list when H2 sections exist and no orphan H3+ headings.
- [ ] H3+ headings _within_ H2 sections do NOT trigger W020.
- [ ] H3+ headings inside code fences do NOT trigger W020.
- [ ] W019 and W020 can fire simultaneously.
- [ ] W019 uses `check_id="STR-004"`, W020 uses `check_id="STR-006"`.
- [ ] Both use `severity=WARNING`, `level=L1_STRUCTURAL`.
- [ ] `diagnostics.py` updated with W019 and W020 codes.

---

## 6. Test Plan

### `tests/test_validation_l1_section_structure.py`

| Test                                 | Input                         | Expected                   |
| ------------------------------------ | ----------------------------- | -------------------------- |
| `test_h2_sections_present_passes`    | 2 H2 sections, no orphan H3+  | `[]`                       |
| `test_no_h2_sections_warns`          | `sections=[]`                 | `[W019]`                   |
| `test_orphan_h3_warns`               | H2 + H3 outside section range | `[W020]`                   |
| `test_h3_within_section_passes`      | H2 + H3 inside section range  | `[]`                       |
| `test_h3_in_code_fence_ignored`      | H3 inside ``` block           | `[]`                       |
| `test_multiple_orphan_h3`            | 3 orphan H3s                  | 3 × W020                   |
| `test_no_h2_and_orphan_h3_both_fire` | `sections=[]` + 2 orphan H3s  | `[W019, W020, W020]`       |
| `test_w019_line_number`              | No sections                   | W019 with `line_number=1`  |
| `test_w020_line_number`              | Orphan H3 at line 10          | W020 with `line_number=10` |
