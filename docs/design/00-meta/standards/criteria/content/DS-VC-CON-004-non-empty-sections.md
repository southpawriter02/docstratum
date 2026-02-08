# DS-VC-CON-004: Non-empty Sections

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-004 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L2-04 |
| **Dimension** | Content (50%) |
| **Level** | L2 — Content Quality |
| **Weight** | 4 / 50 content points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4c AP-STRUCT-002 (Orphaned Sections); v0.0.2c audit data |

## Description

This criterion requires that every H2 section heading is followed by substantive content. Section headers without accompanying content (sometimes called "orphaned sections") are a structural anti-pattern that suggests incomplete documentation or auto-generated structure without meaningful body text.

An H2 section should contain at least one meaningful element: a link, a paragraph, a code block, or a list. Section headers standing alone (followed only by whitespace or sub-headings) create a misleading table of contents and signal incomplete work.

The criterion is fully measurable by analyzing the structure of the Markdown tree — it requires no heuristics or external information.

## Pass Condition

Every H2 section contains at least one substantive content element:

```python
h2_sections = extract_all_h2_sections(content)
for section in h2_sections:
    content_children = [
        child for child in section.children
        if child.type in ('link', 'paragraph', 'code_block', 'list')
    ]
    assert len(content_children) > 0
```

A section containing only whitespace, or only sub-headings (H3+) with no actual content, fails the criterion.

## Fail Condition

Any H2 section is empty — the header is present but no content elements exist between it and the next H2 (or end of file).

- **W011** fires per empty section, enabling visibility into which sections lack content.
- A section containing only an H3 sub-heading (with no paragraph or link under the H3) is considered empty.

Examples:
- ❌ `## References` followed immediately by `## Next Steps` (nothing between)
- ❌ `## Installation` with only `### Prerequisites` and no text under Prerequisites
- ✓ `## Installation` followed by at least one paragraph, code block, link, or list

## Emitted Diagnostics

- **DS-DC-W011** (WARNING): Sections contain no meaningful content. Fires per empty section.

## Related Anti-Patterns

- **DS-AP-STRUCT-002** (Orphaned Sections): Sections with headers but no links, paragraphs, or substantive content — exactly what this criterion detects.

## Related Criteria

- **DS-VC-STR-004** (H2 Section Structure): Checks that the H2 section structure exists and is well-formed; DS-VC-CON-004 checks that sections have content.
- **DS-VC-CON-003** (No Placeholder Content): A section containing only placeholder text (e.g., `## TODO: Write this section`) is technically non-empty but semantically empty. This criterion focuses on structural emptiness; CON-003 addresses semantic emptiness (placeholder).

## Calibration Notes

Orphaned sections are moderately common in auto-generated files, particularly those created by documentation generators that produce boilerplate structure without populating content. Mid-range files (quality scores 40–60) typically have 1–2 empty sections.

The v0.0.2c audit data should be mined for orphaned section frequency across the 6 calibration specimens. This will help calibrate the severity weight and determine whether the criterion should distinguish between "1–2 empty sections" (minor) and "widespread empty sections" (severe).

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
