# DS-DC-E007: EMPTY_FILE

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-E007 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | E007 |
| **Severity** | ERROR |
| **Validation Level** | L0 — Parseable |
| **Check ID** | CHECK-001 (v0.0.4c Ghost File anti-pattern) |
| **Provenance** | v0.0.4c anti-patterns catalog; v0.0.2b audit data |

## Message

> File is empty or contains only whitespace.

## Remediation

> Add content to the file. At minimum: H1 title, blockquote, one H2 section.

## Description

This error fires when a file contains no meaningful content — either it is completely empty or contains only whitespace characters (spaces, tabs, blank lines). An empty file represents the "Ghost File" anti-pattern and provides no value to the ecosystem. Every file should have at least a title (H1) and some structural content.

The minimum remediation is to add an H1 heading (the required document title), a blockquote block (for metadata or context), and at least one H2 section with content. This ensures the file serves a defined purpose in the documentation ecosystem.

### When This Code Fires

- The file contains zero bytes (truly empty).
- The file contains only whitespace characters with no text content.
- This is a Phase C L0 check performed early in the validation pipeline (L0-02).

### When This Code Does NOT Fire

- The file contains at least one non-whitespace character of meaningful content.
- The file has an H1 title and additional structural elements.

## Triggering Criteria

L0 pipeline prerequisite gate — no formal VC criterion file. Related to DS-VC-STR-008 (No Critical Anti-Patterns) via DS-AP-CRIT-001 (Ghost File). L0-02 (Non-Empty Content) check documented in DS-VL-L0-PARSEABLE.md.
## Related Anti-Patterns

- DS-AP-CRIT-001 (Ghost File) — this diagnostic IS the Ghost File detection mechanism

## Related Diagnostic Codes

- DS-DC-E001 (if a file is empty, E007 fires first at L0; E001 is never reached because the file fails L0 validation)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
