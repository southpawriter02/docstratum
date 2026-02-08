# DS-DC-E004: INVALID_LINE_ENDINGS

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-E004 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | E004 |
| **Severity** | ERROR |
| **Validation Level** | L0 — Parseable |
| **Check ID** | ENC-002 (v0.0.4a) |
| **Provenance** | CommonMark spec; Unix convention; v0.0.4a structural checks |

## Message

> File uses non-LF line endings (CR or CRLF detected).

## Remediation

> Convert line endings to LF (Unix-style). Most editors have this option.

## Description

This error fires when a file uses CR (carriage return, `\r`) or CRLF (carriage return + line feed, `\r\n`) line endings instead of the required LF (line feed, `\n`) format. LF is the Unix/Linux standard and is required for reliable Markdown parsing and cross-platform compatibility. Files with mixed or non-LF line endings can cause parsing errors and inconsistent behavior.

Most modern editors (VS Code, Sublime Text, etc.) display the current line ending format in the status bar and allow one-click conversion to LF.

### When This Code Fires

- The file contains one or more lines terminated with `\r` or `\r\n` instead of `\n`.
- This is a Phase C L0 check performed early in the validation pipeline (L0-05).

### When This Code Does NOT Fire

- All lines in the file use LF (`\n`) as the line terminator.
- The file ends without a trailing newline (which is acceptable).

## Triggering Criteria

L0 pipeline prerequisite gate — no formal VC criterion file. L0-05 (Line Feed Normalization) check documented in DS-VL-L0-PARSEABLE.md.
## Related Anti-Patterns

- DS-AP-CRIT-003 (Encoding Disaster)

## Related Diagnostic Codes

- DS-DC-E003 (sibling encoding check: E004 validates line endings; E003 validates character encoding)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
