# DS-VC-STR-001: H1 Title Present

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-001 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Platinum ID** | L1-01 |
| **Dimension** | Structural (30%) |
| **Level** | L1 — Structurally Valid |
| **Weight** | 5 / 30 structural points |
| **Pass Type** | HARD |
| **Measurability** | Fully measurable |
| **Provenance** | Official llms.txt spec §1 ("The file should begin with an H1"); v0.0.1a ABNF grammar (`llms-txt = h1-title ...`); v0.0.2c audit: 100% of valid specimens use single H1 |

## Description

This criterion checks that the llms.txt file contains at least one H1 (`#`) Markdown heading. The H1 title is the only element explicitly **required** by the llms.txt specification — it identifies the project or product that the file documents. Without it, AI agents have no way to determine what the documentation pertains to, making the file effectively useless for automated consumption.

In the v0.0.2 audit of 24 real-world implementations, 100% of structurally valid specimens included an H1 title. This makes it the most universally adopted element of the specification and the most fundamental structural requirement after parseability (L0) itself.

## Pass Condition

The file contains **at least one** line that starts with `# ` (H1 Markdown heading):

```python
h1_headings = [line for line in lines if line.startswith("# ")]
assert len(h1_headings) >= 1
```

Note: This criterion checks only for the **presence** of an H1. The requirement that there be **exactly one** H1 (no duplicates) is a separate criterion (DS-VC-STR-002).

## Fail Condition

The file contains **zero** H1 headings:

- No line starts with `# ` followed by non-whitespace content
- File starts with H2 (`##`) or lower heading level without a preceding H1
- File contains only body text, links, or blockquotes with no headings at all

**Gate behavior:** This is a HARD criterion at L1. Failure means the file does not pass L1 — Structurally Valid.

## Emitted Diagnostics

- **DS-DC-E001** (ERROR): Emitted when zero H1 headings are found in the file

## Related Anti-Patterns

- **DS-AP-CRIT-002** (Structure Chaos): Files lacking any recognizable Markdown structure (no headers, no sections) will necessarily lack an H1 title.

## Related Criteria

- **DS-VC-STR-002** (Single H1 Only): Checks that there is at most one H1. Together, STR-001 and STR-002 enforce the spec's requirement of "exactly one H1."
- **DS-VC-STR-003** (Blockquote Present): The next structural check after the H1 — verifies the project description blockquote.

## Calibration Notes

- **DS-CS-001 (Svelte):** PASSES — has H1 "Svelte"
- **DS-CS-002 (Pydantic):** PASSES — has H1 "Pydantic"
- **DS-CS-005 (Cursor):** PASSES — has H1 present
- All 6 calibration specimens pass this criterion. H1 absence is extremely rare in published llms.txt files.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase A example file |
| 0.0.0-scaffold | 2026-02-08 | Reverted from compound "Parseable Prerequisites" (L0-01 through L0-05) to atomic "H1 Title Present" (L1-01) per Phase A audit finding CRITICAL-001 (Path A resolution). L0 criteria deferred to Phase C. |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
