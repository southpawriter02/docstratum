# DS-DC-E003: INVALID_ENCODING

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-E003 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | E003 |
| Severity | ERROR |
| Validation Level | L0 — Parseable |
| Check ID | ENC-001 (v0.0.4a) |
| Provenance | CommonMark spec (UTF-8 requirement); v0.0.1a formal grammar |

## Message

> File is not valid UTF-8 encoding.

## Remediation

> Convert the file to UTF-8 encoding. Remove any BOM markers.

## Description

This error fires when the file contains bytes that do not conform to the UTF-8 standard. UTF-8 is the required encoding for all DocStratum documents per the CommonMark specification and modern web standards. Files with other encodings (such as UTF-16, ISO-8859-1, or legacy code pages) cannot be reliably parsed and cause interoperability issues.

BOM (Byte Order Mark) markers, though technically UTF-8 compatible, should be removed for consistency. Most modern editors can convert file encoding and strip BOM markers automatically.

### When This Code Fires

- The byte stream of the file is read and fails UTF-8 decoding validation.
- This is a Phase C L0 check performed early in the validation pipeline (L0-01).

### When This Code Does NOT Fire

- The file is a valid UTF-8 encoded text file with no BOM markers.
- All byte sequences in the file follow the UTF-8 specification.

## Triggering Criteria

L0 criterion (Phase C) — L0-01

## Related Anti-Patterns

- DS-AP-CRIT-003 (Encoding Disaster)

## Related Diagnostic Codes

- DS-DC-E004 (sibling encoding check: E003 validates character encoding; E004 validates line ending format)

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
