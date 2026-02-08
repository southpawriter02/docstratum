# DS-DC-I010: ECOSYSTEM_SINGLE_FILE

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-I010 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | I010 |
| **Severity** | INFO |
| **Validation Level** | Ecosystem-level (cross-file validation) |
| **Check ID** | v0.0.7 §5.3 |
| **Provenance** | v0.0.7 §5.3 (Ecosystem-Level Informational Codes) |

## Message

> The entire ecosystem consists of just llms.txt with no companion files.

## Remediation

> Consider adding llms-full.txt and individual content pages for deeper coverage.

## Description

This informational code indicates that the documentation ecosystem consists of only a single file—the `llms.txt` index—with no companion files, supplementary content pages, or modular documentation structure. While a single-file approach can be legitimate for minimal ecosystems or getting-started documentation, it limits scalability, navigation, and context management.

A single-file ecosystem necessarily consolidates all content into one document, which may exceed reasonable size limits and complicates selective consumption by readers and agents. This is particularly challenging in token-limited AI agent environments where consumers need to select relevant subsections. Adding an `llms-full.txt` companion and individual content pages enables modular consumption, improved discoverability, and better scaling as documentation grows.

**When This Code Fires:**
- Only `llms.txt` exists in the ecosystem root.
- No companion files (e.g., `llms-full.txt`, individual content pages) are present.
- The ecosystem structure is minimal (single-file only).

**When This Code Does NOT Fire:**
- Multiple ecosystem files exist (index, full, content pages).
- Companion or supplementary files are present alongside the primary index.

## Triggering Criteria

Ecosystem-level diagnostic — no per-file VC criterion. Fires during ecosystem validation (Stage 4) when the ecosystem consists of just llms.txt with no additional files.
## Related Anti-Patterns

None directly identified.

## Related Diagnostic Codes

- **DS-DC-E009** (NO_INDEX_FILE): Complementary observation; E009 fires when no index file exists, I010 fires when only an index file exists.
- **DS-DC-W013** (MISSING_AGGREGATE): Related concept; W013 flags missing aggregates for large projects.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
