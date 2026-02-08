# DS-VC-STR-003: Blockquote Present

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-003 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L1-03 |
| **Dimension** | Structural (30%) |
| **Level** | L1 — Structurally Valid |
| **Weight** | 3 / 30 structural points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | Official llms.txt spec: blockquote is "expected" section; v0.0.2c audit: 55% real-world compliance — low enough to warrant Warning, not Error |

## Description

This criterion checks that the llms.txt file includes at least one blockquote (`>`) element, conventionally placed immediately after the H1 title. The blockquote serves as a high-level summary or description of the project, providing context before detailed sections begin.

The official llms.txt specification lists blockquote as an "expected" element, though not strictly "required." In the v0.0.2 audit of 24 real-world implementations, approximately 55% included blockquotes. Top-scoring specimens (Svelte at 92, Pydantic at 90) consistently include them, suggesting a strong correlation between blockquote presence and overall document quality. Lower-scoring implementations often lack blockquotes entirely, typically in auto-generated or minimal documentation files.

Because blockquote absence is moderately common and does not represent a structural violation per se (it is "expected" but not "required"), this criterion is classified as SOFT. Failure emits a Warning, not an Error, and does not block progression to L1 — Structurally Valid.

## Pass Condition

At least one blockquote (`>`) element exists anywhere in the file, ideally immediately after the H1:

```python
blockquotes = [line for line in lines if line.startswith(">")]
assert len(blockquotes) >= 1
```

The blockquote should logically precede substantive content sections (H2 headings) and serve as the project summary. However, the criterion checks only for presence, not position or content quality (the latter is covered by DS-VC-CON-006 Substantive Blockquote).

## Fail Condition

No blockquote element found anywhere in the file:

- No lines start with `>` followed by content
- File has H1 and sections but no summary blockquote
- Common causes:
  - Minimal or quick-reference documentation (e.g., short API stubs)
  - Auto-generated files that skip descriptive sections
  - Markdown documents converted from non-Markdown sources without editor review
  - Documentation written to prioritize code examples over narrative description

## Emitted Diagnostics

- **DS-DC-W001** (WARNING): Emitted when no blockquote description is found in the file

## Related Anti-Patterns

- No direct anti-pattern, as blockquote absence is not categorized as an anti-pattern. However, files lacking blockquotes often show other structural weaknesses captured by DS-AP-STRUCT-002 (Orphaned Sections) or DS-AP-CONT-003 (Description Deficit).

## Related Criteria

- **DS-VC-STR-001** (H1 Title Present): The H1 title precedes the blockquote in conventional structure.
- **DS-VC-CON-006** (Substantive Blockquote): If a blockquote is present, this criterion verifies that it contains meaningful content (≥20 non-whitespace characters). STR-003 checks presence; CON-006 checks substance.
- **DS-VC-CON-003** (Non-empty File): Ensures the file has some content; blockquote presence adds to this requirement.

## Calibration Notes

- **Approximately 55% of audited specimens include blockquotes**
  - Svelte (92 pts): Includes blockquote summarizing project purpose
  - Pydantic (90 pts): Includes blockquote introducing data validation library
  - Cursor (87 pts): Includes blockquote describing AI editor
  - NVIDIA llms.txt (24 pts): Lacks blockquote entirely; contributes to structural deficit
- Files with blockquotes consistently score 5–10 points higher in the structural dimension
- SOFT pass means W001 is emitted but does not prevent L1 classification

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
