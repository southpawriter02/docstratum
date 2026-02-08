# DS-VC-STR-006: No Heading Violations

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-006 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L1-06 |
| **Dimension** | Structural (30%) |
| **Level** | L1 — Structurally Valid |
| **Weight** | 3 / 30 structural points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.1a grammar: sections are H2-delimited; v0.0.2c audit: 0% of valid implementations use H3 for sections |

## Description

This criterion ensures that H3, H4, H5, and H6 headings are not misused as primary section dividers. The llms.txt specification establishes a clear heading hierarchy: H1 for project title, H2 for primary sections, and H3+ exclusively for sub-structure within H2 sections.

When H3 or deeper headings appear at the top level (as primary section dividers between H2 sections), the file exhibits a hierarchical inconsistency. This violates the specification's structural contract and confuses parsers attempting to extract logical document divisions. While such violations are rare (0% in the v0.0.2 calibration audit), they represent a structural quality issue that warrants detection and correction.

This is a SOFT criterion: detection does not block L1 classification but reduces the structural dimension score. Heading level consistency is important for document quality and machine readability but not catastrophic if violated in isolated cases.

## Pass Condition

No H3+ headings are used as primary section dividers. H3/H4/H5/H6 are permitted only **within** H2 sections for sub-structure:

```python
# Extract all headings and their nesting context
headings = extract_headings(file_content)
h2_sections = [h for h in headings if h.level == 2]

# For each H2 section, check that no H3+ appears at the top level between sections
for i, h2 in enumerate(h2_sections):
    next_h2 = h2_sections[i + 1] if i + 1 < len(h2_sections) else None
    content_between = get_content_between(h2, next_h2)
    headings_between = extract_headings(content_between)
    # All headings within this section should be H3 or deeper
    assert all(h.level >= 3 for h in headings_between), "H3+ within H2 section is valid"

# Equivalently: No H3+ heading should be a top-level divider
assert not any(is_primary_section_divider(h) and h.level >= 3 for h in headings)
```

If no H2 sections exist in the file (a minimal llms.txt with only H1 + blockquote), this criterion passes vacuously.

## Fail Condition

An H3+ heading is used where an H2 would be expected:

- `### Getting Started` appearing as a top-level section (between other H2 sections)
- `#### Configuration` used as a primary section divider
- Mixed hierarchy within a single file: some sections use H2, others use H3
- File contains only H1 and H3+ headings with no H2s (non-canonical hierarchical structure)

## Emitted Diagnostics

- **No standalone diagnostic code:** This is a structural quality check without a dedicated diagnostic code. Violations are captured through holistic structural dimension scoring and related anti-pattern detection (e.g., DS-AP-STRUCT-005 Naming Nebula, which often correlates with heading inconsistencies).

## Related Anti-Patterns

- **DS-AP-STRUCT-005** (Naming Nebula): Vague or inconsistent naming often accompanies heading level violations. Both suggest poor document organization.

## Related Criteria

- **DS-VC-STR-004** (H2 Section Structure): The complementary check; STR-004 ensures sections use H2, STR-006 ensures H3+ is not misused.
- **DS-VC-STR-001** (H1 Title Present): H1 is the root of the hierarchy. Correct H2/H3 usage follows below it.
- **DS-VC-CON-008** (Canonical Section Names): Once structure is verified (correct heading levels), this checks section naming conventions.

## Calibration Notes

- **0% of valid implementations in the v0.0.2 audit use H3 for primary sections**
- Heading level consistency is a universally followed convention among professional llms.txt implementations
- All calibration specimens (Svelte, Pydantic, Cursor, FastAPI, Django, Flask) use canonical H1 → H2 → H3+ hierarchy
- Violations observed only in:
  - Auto-generated documents (rare)
  - Non-standard Markdown converters
  - Copy-pasted content from heterogeneous sources
- SOFT pass means violations reduce the structural score but do not prevent L1 classification

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
