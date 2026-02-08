# DS-VC-CON-009: Master Index Present

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-009 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L3-02 |
| **Dimension** | Content (50%) |
| **Level** | L3 — Best Practices |
| **Weight** | 5 / 50 content points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4a CHECK-STR-009; v0.0.2d finding: Master Index presence correlates with 87% vs 31% LLM task success rate; strong empirical signal for file utility |

## Description

This criterion ensures that the llms.txt file contains a section functioning as a master index—typically named "Master Index", "Table of Contents", "Index", "Documentation", or similar—usually positioned as the first H2 section. A master index serves as the organizational hub of the document, providing high-level navigation to key resources, sections, and topics without requiring the reader to skim the entire file.

The presence of a master index is one of the strongest single predictors of file utility and LLM task success. In v0.0.2d empirical testing, files with a Master Index section achieved 87% task success rate, compared to 31% for files without one. This dramatic difference reflects the fact that a well-formed index helps both human readers and AI agents quickly locate relevant information, reducing cognitive load and improving task completion rates.

Master index sections need not be exhaustive; even a simple list of key links or section pointers substantially improves navigability.

## Pass Condition

The file contains a section recognizable as a master index:

```python
h2_sections = extract_h2_headings(file_content)
first_h2 = h2_sections[0] if h2_sections else None

master_index_names = {
    'master index', 'table of contents', 'toc', 'index',
    'docs', 'documentation', 'guide', 'overview'
}

has_master_index = (
    (first_h2 and first_h2.name.lower() in master_index_names)
    or any(s.name.lower() in master_index_names for s in h2_sections)
)

assert has_master_index
```

The primary check is name-based. The section may contain links (link density > 0), but the criterion succeeds on name alone. The Master Index is ideally the first H2 section, though the criterion accepts it anywhere in the file for robustness.

## Fail Condition

No H2 section with a master-index-like name is found anywhere in the file. Failing scenarios include:

- File contains sections named "Getting Started", "API Reference", "Examples", but nothing called "Master Index", "Table of Contents", "Index", "Documentation", etc.
- First H2 section has a different name (e.g., "Getting Started") with no other index-like section elsewhere
- File has only H3+ headings with no H2 Master Index section

W009 fires once per file when no Master Index section is detected.

## Emitted Diagnostics

- **DS-DC-W009** (WARNING): No Master Index found in the file; ideally the first H2 section

## Related Anti-Patterns

- **DS-AP-STRUCT-001** (Sitemap Dump): A master index degenerates into a flat URL dump without meaningful organization, categorization, or explanatory text. This anti-pattern detects when an index exists but lacks utility.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): "Master Index" is one of the 11 canonical section names. Files that pass CON-008 are more likely to include a Master Index.
- **DS-VC-STR-007** (Canonical Section Ordering): Master Index should occupy the first H2 section position per canonical ordering conventions.

## Calibration Notes

v0.0.2d empirical finding: files with a Master Index section achieved 87% LLM task success rate vs 31% without. This is one of the strongest single predictors of file utility. Both Svelte and Pydantic specimens include Master Index sections. The criterion name-matches against 8 recognized variations to accommodate natural naming choices while maintaining high specificity.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
