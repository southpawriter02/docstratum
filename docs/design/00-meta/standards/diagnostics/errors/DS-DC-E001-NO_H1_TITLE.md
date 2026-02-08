# DS-DC-E001: NO_H1_TITLE

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-E001 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | E001 |
| **Severity** | ERROR |
| **Validation Level** | L1 — Structurally Valid |
| **Check ID** | STR-001 (v0.0.4a) |
| **Provenance** | Official llms.txt spec §1 ("The file should begin with an H1"); v0.0.1a ABNF grammar (`llms-txt = h1-title ...`); v0.0.2c audit: 100% of valid specimens use single H1 |

## Message

> No H1 title found. Every llms.txt file MUST begin with exactly one H1 title.

## Remediation

> Add a single '# Title' as the first line of the file.

## Description

This diagnostic fires when the Markdown parser finds zero H1 (`#`) headings in the file. The H1 title is the only element explicitly **required** by the llms.txt specification — it identifies the project or product that the file documents. Without it, AI agents have no way to identify what the documentation pertains to.

In the v0.0.2 audit of 24 real-world implementations, 100% of structurally valid specimens included an H1 title. This is the most universally adopted element of the specification.

### When This Code Fires

- File contains no line starting with `# ` (H1 Markdown heading)
- File starts with H2 (`##`) or other heading level without a preceding H1
- File contains only body text with no headings at all

### When This Code Does NOT Fire

- File has exactly one H1 → no diagnostic
- File has multiple H1s → DS-DC-E002 fires instead (different diagnostic)
- File is empty → DS-DC-E007 fires first (L0 gate prevents reaching this check)

## Triggering Criteria

- **DS-VC-STR-001**: (H1 Title Present)

Emitted by DS-VC-STR-001 when zero H1 headings are found.
## Related Anti-Patterns

- **DS-AP-CRIT-002** (Structure Chaos): Files lacking recognizable Markdown structure (no headers, no sections) will also trigger this code.

## Related Diagnostic Codes

- **DS-DC-E002** (MULTIPLE_H1): Mutually exclusive — E001 fires when there are zero H1s, E002 fires when there are two or more. They cannot both fire for the same file.
- **DS-DC-E007** (EMPTY_FILE): E007 fires at L0 before E001 can be checked at L1. If the file is empty, E001 is never evaluated.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase A example file |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
