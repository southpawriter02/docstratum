# DS-VC-CON-008: Canonical Section Names

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-008 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Platinum ID** | L3-01 |
| **Dimension** | Content (50%) |
| **Level** | L3 — Best Practices |
| **Weight** | 5 / 50 content points |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | DECISION-012: 11 canonical names derived from frequency analysis of 450+ projects in v0.0.2c; v0.0.4a CHECK-STR-006; v0.0.6 calibration confirms strong correlation with quality scores |

## Description

This criterion ensures that section headings use one of 11 canonical names (or a recognized alias from the 32-alias mapping) rather than arbitrary or idiosyncratic section titles. Canonical section names emerge from frequency analysis of real-world llms.txt files and represent the most common organizational patterns that aid both human comprehension and LLM navigation.

The 11 canonical names are: **Master Index**, **LLM Instructions**, **Getting Started**, **Core Concepts**, **API Reference**, **Examples**, **Configuration**, **Advanced Topics**, **Troubleshooting**, **FAQ**, and **Optional**. Additionally, a curated set of 32 recognized aliases (e.g., "Documentation" as an alias for "Master Index", "Installation" as an alias for "Getting Started") extends coverage to natural variations without penalizing reasonable naming choices.

Files that consistently use canonical names are easier for both human readers and LLM agents to navigate, as the section names signal the likely content type and purpose. Conversely, files with highly custom or vague section names (e.g., "Random Notes", "Stuff", "Miscellaneous") force readers to infer structure from content alone, degrading utility.

## Pass Condition

At least 70% of H2 section names match a canonical name or recognized alias:

```python
canonical_names = set(CanonicalSectionName) | set(SECTION_NAME_ALIASES.keys())
# Canonical names:
# {'master index', 'llm instructions', 'getting started', 'core concepts',
#  'api reference', 'examples', 'configuration', 'advanced topics',
#  'troubleshooting', 'faq', 'optional'}
# Plus 32 aliases (see constants.py SECTION_NAME_ALIASES)

h2_sections = extract_h2_headings(file_content)
canonical_count = sum(1 for s in h2_sections if s.name.lower() in canonical_names)
canonical_ratio = canonical_count / len(h2_sections) if h2_sections else 1.0
assert canonical_ratio >= 0.70  #
```

Files with zero H2 sections are considered as having no violations (the criterion is not applicable). Files with 70% or higher canonical alignment pass.

## Fail Condition

More than 30% of H2 sections use non-canonical, non-alias names. Examples of failing scenarios:

- A file with 10 H2 sections where 4 or more use custom names (e.g., "Random Notes", "Implementation Details Nobody Asked For", "My Thoughts")
- A file where all sections are custom (0% canonical alignment)
- Files with idiosyncratic naming patterns that do not appear in the 32-alias set

W002 fires once per non-canonical section. Files where fewer than 70% of sections align with canonical names fail the criterion overall.

## Emitted Diagnostics

- **DS-DC-W002** (WARNING): Emitted once per H2 section that does not match a canonical name or recognized alias

## Related Anti-Patterns

- **DS-AP-STRUCT-005** (Naming Nebula): Vague, inconsistent, or non-standard section names that force readers to infer structure from content, reducing navigability and LLM comprehension.

## Related Criteria

- **DS-VC-STR-007** (Canonical Section Ordering): Sections must use canonical names before they can be evaluated for proper ordering. This criterion is a prerequisite for ordering validation.
- **DS-VC-CON-009** (Master Index Present): "Master Index" is one of the 11 canonical names and a key organizational hub in well-structured files.

## Calibration Notes

v0.0.2c frequency analysis of 450+ projects identified 11 section names appearing across the vast majority of high-quality implementations. Top-scoring specimens (Svelte, Pydantic) use ≥80% canonical names. The 70% threshold allows up to approximately 3 custom section names in a 10-section file, providing flexibility while maintaining navigability. Files with all custom section names score significantly lower on utility and LLM task success rate (≈15% vs ≈75% for canonical-aligned files).

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
