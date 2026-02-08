# DS-DC-I009: CONTENT_COVERAGE_GAP

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-I009 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | I009 |
| Severity | INFO |
| Validation Level | Ecosystem-level (cross-file validation) |
| Check ID | v0.0.7 §5.3 |
| Provenance | v0.0.7 §5.3 (Ecosystem-Level Informational Codes) |

## Message

> The index references section categories for which no detailed content page exists.

## Remediation

> Create content pages for the missing section categories.

## Description

This informational code indicates that the primary index file (e.g., `llms.txt`) references or outlines section categories that do not have corresponding detailed content pages in the ecosystem. This gap represents incomplete coverage of the documented ecosystem structure and can leave readers and agents with orphaned references—pointers to content that is promised but not delivered.

A content coverage gap suggests either aspirational documentation planning (where sections are outlined but not yet written) or unintentional incompleteness (where referenced content was removed or never created). Identifying and resolving these gaps ensures that the index accurately reflects the actual ecosystem contents and prevents confusion or broken expectations.

**When This Code Fires:**
- The index file references section categories (e.g., "See Advanced Topics") without corresponding pages.
- TOC entries point to content that does not exist in the ecosystem.
- Structure is outlined but detailed pages are missing.

**When This Code Does NOT Fire:**
- All section categories referenced in the index have corresponding content pages.
- The index accurately reflects the ecosystem structure.

## Triggering Criterion

Ecosystem validation stage (no per-file VC criterion).

## Related Anti-Patterns

None directly identified.

## Related Diagnostic Codes

- **DS-DC-E010** (ORPHANED_FILES): Inverse problem; E010 fires for files unreferenced by the index, I009 fires for referenced categories without files.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
