# DS-DC-W012: BROKEN_CROSS_FILE_LINK

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-W012 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | W012 |
| Severity | WARNING |
| Validation Level | Ecosystem-level (cross-file validation) |
| Check ID | v0.0.7 §5.2 |
| Provenance | v0.0.7 §5.2 (Ecosystem-Level Warning Codes) |

## Message

> A link in one file references another file that doesn't exist or is unreachable.

## Remediation

> Fix the broken link URL or create the missing target file.

## Description

This ecosystem-level diagnostic fires when the validation engine detects a hyperlink in one documentation file that references another file which either does not exist or is unreachable within the project structure. Cross-file links are fundamental to maintaining a coherent documentation ecosystem; broken links fragment the narrative and create dead ends for readers.

The validation process scans all internal links (those using relative paths or file references) and verifies that the target files exist and are accessible. This diagnostic captures cases where the link target has been deleted, moved, or renamed without updating the referring document. Unlike per-file broken link detection (DS-DC-E006), this code specifically focuses on the ecosystem-wide consistency of cross-file references.

**When This Code Fires:** The validation engine finds a link in file A that points to file B, but file B does not exist in the documented file structure, or the path resolution fails at the ecosystem level.

**When This Code Does NOT Fire:** All cross-file links resolve successfully to existing files within the project, or links are external (pointing outside the documentation ecosystem).

## Triggering Criteria

Cross-file diagnostic — includes `source_file` and `related_file` context. Ecosystem codes do not have per-file VC criterion; this code fires during ecosystem validation (Stage 4) when structural integrity checks occur across the entire documentation set.

## Related Anti-Patterns

- DS-AP-ECO-002 (Phantom Links) — ecosystem-level pattern of broken or non-existent references

## Related Diagnostic Codes

- DS-DC-E006 (per-file broken links) — detects broken links within a single file
- DS-DC-E010 (orphaned files) — inverse problem: files that exist but are never referenced

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
