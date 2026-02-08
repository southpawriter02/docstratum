# DS-VC-STR-002: Single H1 Only

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-002 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L1-02 |
| **Dimension** | Structural (30%) |
| **Level** | L1 — Structurally Valid |
| **Weight** | 3 / 30 structural points [CALIBRATION-NEEDED] |
| **Pass Type** | HARD |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.1a ABNF grammar: `llms-txt = h1-title ...`; official spec implies single title; v0.0.2c audit: 100% of valid specimens use single H1 |

## Description

This criterion enforces that the llms.txt file contains **exactly one** H1 heading, not multiple. While DS-VC-STR-001 verifies that at least one H1 is present, this criterion prevents the ambiguity and structural confusion that arises when multiple H1 headings appear in a single file.

Multiple H1 headings violate the llms.txt specification's implicit contract: the H1 title should uniquely identify the project or product being documented. When multiple H1s are present, AI agents face ambiguity about which title to treat as the canonical project name, leading to degraded consumption experience. In the v0.0.2 audit of 24 real-world implementations, 100% of structurally valid specimens contained exactly one H1. The small fraction of files exhibiting multiple H1s were invariably auto-generated or poorly formatted documents.

This criterion is typically encountered in conjunction with STR-001: together they form the "exactly one H1" requirement. A file passes L1 Structurally Valid only if both are satisfied.

## Pass Condition

The file contains **exactly one** line that starts with `# ` (H1 Markdown heading):

```python
h1_headings = [line for line in lines if line.startswith("# ")]
assert len(h1_headings) == 1
```

This combines with DS-VC-STR-001 (at least one H1) to enforce the strict "exactly one H1" invariant. A file with zero H1s fails STR-001; a file with two or more H1s fails STR-002.

## Fail Condition

The file contains **zero or more than one** H1 headings:

- Zero H1s: Covered by DS-VC-STR-001 failure
- Two or more H1s: Multiple lines starting with `# ` followed by non-whitespace content
- Common causes:
  - Copy-paste from multiple source files (e.g., concatenating two projects' READMEs)
  - Auto-generated headers where each section is mistakenly given an H1 instead of an H2
  - Using H1 as a section divider rather than reserving it for the project title
  - Markdown export from tools that produce multiple H1s for top-level items

## Emitted Diagnostics

- **DS-DC-E002** (ERROR): Emitted when two or more H1 headings are detected in the file

## Related Anti-Patterns

- **DS-AP-CRIT-002** (Structure Chaos): Chaotic file structure (no clear organization) may include multiple H1s used inconsistently as pseudo-section dividers.

## Related Criteria

- **DS-VC-STR-001** (H1 Title Present): Checks for at least one H1. Together with STR-002, they enforce "exactly one H1."
- **DS-VC-STR-004** (H2 Section Structure): Sections should use H2 headings, not additional H1s. This criterion prevents misuse of H1 for section organization.
- **DS-VC-CON-008** (Canonical Section Names): Once structure is verified (single H1, H2 sections), this checks section naming conventions.

## Calibration Notes

- All 6 calibration specimens pass (single H1 each): Svelte, Pydantic, Cursor, FastAPI, Django, Flask
- Multiple H1 is rare (~2%) in published llms.txt files
- When observed, it correlates strongly with auto-generated or hastily concatenated files
- NVIDIA's llms.txt (score 24) has a single H1, so this criterion does not explain its lower overall score

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
