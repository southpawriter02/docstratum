# DS-VC-STR-004: H2 Section Structure

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-004 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L1-04 |
| **Dimension** | Structural (30%) |
| **Level** | L1 — Structurally Valid |
| **Weight** | 4 / 30 structural points [CALIBRATION-NEEDED] |
| **Pass Type** | HARD |
| **Measurability** | Fully measurable |
| **Provenance** | Official llms.txt spec: "H2-delimited sections"; v0.0.1a ABNF grammar defining section structure |

## Description

This criterion verifies that the llms.txt file uses H2 (`##`) headings to delimit primary content sections. The llms.txt specification defines the document structure as: H1 (project title) → optional blockquote → multiple H2 sections, each containing subsection content.

When a file deviates from this structure—for example, using H3 (`###`) as a top-level section divider or omitting section headers entirely—AI agents struggle to parse and navigate the document. The hierarchical heading structure is the backbone of machine-readable documentation; it enables automated extraction of logical document divisions and semantic understanding of content relationships.

In the v0.0.2 audit, all well-formed llms.txt specimens used H2 for primary sections beneath the H1 title. Files lacking H2 structure were invariably non-compliant or auto-generated. This criterion is a structural prerequisite without a standalone diagnostic code—failure is captured holistically through the overall structural scoring.

## Pass Condition

All primary content sections use H2 headings. Optionally, H3, H4, H5, or H6 headings may appear **within** H2 sections for sub-structure:

```python
primary_section_headings = [h for h in headings if h.level == 2 or is_primary_section_divider(h)]
assert all(h.level == 2 for h in primary_section_headings)

# Equivalently, no H3+ headings appear as top-level section dividers
assert not any(h.level >= 3 and is_primary_section_divider(h))
```

A minimal valid llms.txt could consist of H1 + blockquote + zero H2 sections (effectively a title-only document), which would vacuously pass this criterion. However, such minimal files would fail other content-based criteria (e.g., CON-007 Mandatory Sections).

## Fail Condition

Primary content sections use heading levels other than H2:

- An H3 heading appears where an H2 would be expected (e.g., "### Getting Started" as a top-level section between other H2 sections)
- An H4 or deeper heading is used to delimit primary sections
- File contains only H1 and H3+ headings with no H2s (indicating non-standard hierarchical structure)
- Section dividers are indicated by other Markdown elements (e.g., horizontal rules `---`, bold lines `**Section**`) rather than heading syntax

## Emitted Diagnostics

- **No standalone diagnostic code:** This is a structural prerequisite. Failure is captured through holistic structural dimension scoring. The absence of H2 structure contributes to overall structural degradation.

## Related Anti-Patterns

- **DS-AP-CRIT-002** (Structure Chaos): Complete lack of section structure (no H2s, no organized sections) is a subset of Structure Chaos.

## Related Criteria

- **DS-VC-STR-006** (No Heading Violations): Complementary check ensuring H3+ is not misused for primary sections.
- **DS-VC-STR-001** (H1 Title Present): H1 is the top-level heading; H2s are sections beneath it. Together they establish the hierarchical structure.
- **DS-VC-CON-007** (Mandatory Sections): Once H2 structure is verified, CON-007 checks that required sections (Master Index, LLM Instructions, Getting Started, etc.) are present.
- **DS-VC-CON-008** (Canonical Section Names): Verifies that H2 sections use canonical names from the official list.

## Calibration Notes

- All well-formed specimens in the v0.0.2 audit use H2 for sections
- Files lacking H2s entirely are extremely rare in published llms.txt files (~1%)
- When observed, H2 absence correlates with non-standard document formats (e.g., files intended for human reading but lacking machine-readable structure)
- Svelte, Pydantic, Cursor, FastAPI, Django, Flask: All use H2 section structure correctly
- H3+ as primary sections: Never observed in the calibration set, indicating this is a universally followed convention

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
