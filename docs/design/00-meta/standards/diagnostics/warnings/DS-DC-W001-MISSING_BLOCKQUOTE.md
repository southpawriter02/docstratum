# DS-DC-W001: MISSING_BLOCKQUOTE

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W001 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | W001 |
| **Severity** | WARNING |
| **Validation Level** | L1 — Structurally Valid |
| **Check ID** | STR-002 (v0.0.4a) |
| **Provenance** | Official llms.txt spec ("expected" section); v0.0.2c audit: 55% real-world compliance |

## Message

> No blockquote description found after the H1 title.

## Remediation

> Add a '> description' blockquote immediately after the H1 title.

## Description

This diagnostic fires when the parser finds no blockquote (`>`) element following the H1 title. The llms.txt specification describes the blockquote as an "expected" section — it provides a one-line summary of the project that AI agents use for quick context identification.

### Why This Is a WARNING, Not an ERROR

The blockquote is described as "expected" in the spec, but the v0.0.2 real-world audit found only **55% compliance** across 24 audited implementations. This means nearly half of published llms.txt files lack blockquotes. Treating absence as an ERROR would fail almost half the real-world ecosystem. Instead, it is a WARNING that degrades the quality score without blocking level progression.

This distinction is architecturally significant: it demonstrates the difference between a HARD pass (failure blocks progression) and a SOFT pass (failure emits a warning but doesn't block). Blockquote presence is a SOFT pass criterion in DS-VC-STR-003.

### When This Code Fires

- File has an H1 title but no blockquote (`>`) on any line between the H1 and the first H2
- File has a blockquote that appears after the first H2 section (wrong position)

### When This Code Does NOT Fire

- File has `> ` on a line immediately following the H1 → no diagnostic
- File has no H1 → DS-DC-E001 fires instead; W001 is not evaluated

## Triggering Criteria

- **DS-VC-STR-003**: (Blockquote Present)

Emitted by DS-VC-STR-003 when no blockquote is found after the H1 title. SOFT pass — does not block L1 progression.
## Related Anti-Patterns

- None directly. Blockquote absence is not classified as an anti-pattern because it is too common in the current ecosystem to warrant that label.

## Related Diagnostic Codes

- **DS-DC-E001** (NO_H1_TITLE): If E001 fires (no H1), W001 is never checked. Blockquote presence requires an H1 as an anchor point.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase A example file |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
