# DS-DC-E002: MULTIPLE_H1

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-E002 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | E002 |
| Severity | ERROR |
| Validation Level | L1 — Structurally Valid |
| Check ID | STR-001 (v0.0.4a) |
| Provenance | llms.txt spec §1; v0.0.1a ABNF grammar; v0.0.2c audit |

## Message

> Multiple H1 titles found. The spec requires exactly one H1.

## Remediation

> Remove all but the first H1 title. Use H2 for section headers.

## Description

This error fires when a document contains more than one H1 (top-level) heading. The DocStratum specification requires exactly one H1 per document to establish a single, clear semantic root. Multiple H1s violate this structural requirement and create ambiguity about the document's primary topic.

The H1 serves as the document's title and metadata anchor. All other sections should use H2 and lower heading levels. If you have multiple logical sections that each feel like they should be H1, consider whether they should be separate files instead.

### When This Code Fires

- The parser encounters two or more lines beginning with a single `#` (H1 syntax).
- The file is being validated at L1 (Structurally Valid) stage and has passed L0 (Parseable).

### When This Code Does NOT Fire

- The file contains exactly one H1 at the beginning.
- All other section headers use H2 (`##`) or deeper levels.
- The file uses no heading syntax (though this would trigger E007 if the file is otherwise empty).

## Triggering Criteria

DS-VC-STR-002 (Single H1 Only)

## Related Anti-Patterns

None directly.

## Related Diagnostic Codes

- DS-DC-E001 (mutual exclusion: E001 fires when zero H1s found; E002 fires when multiple H1s found; exactly one H1 passes all checks)

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
