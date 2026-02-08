# DS-DC-W007: MISSING_VERSION_METADATA

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W007 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | W007 |
| **Severity** | WARNING |
| **Validation Level** | L3 — Best Practices |
| **Check ID** | CNT-015 (v0.0.4b) |
| **Provenance** | v0.0.4b content checks; staleness detection research |

## Message

> No version or last-updated metadata found in the file.

## Remediation

> Add version metadata (e.g., 'Last updated: 2026-02-06').

## Description

Version metadata and last-updated timestamps provide critical context for readers about the recency and applicability of documentation. Without this information, readers cannot assess whether content is current, stable, or likely to change. Staleness detection research shows that files with explicit version metadata are perceived as more trustworthy and are more likely to be maintained.

Version metadata serves multiple purposes: it signals to readers when content was last reviewed, it helps maintain ecosystem coherence when referenced from other documents, and it informs maintenance tools about which files may need refresh. Files without version markers become opaque regarding their status and reliability.

### When This Code Fires

W007 fires when a file contains no discernible version or last-updated metadata. This includes files that lack any timestamp, version number, or explicit update marker in frontmatter, header comments, or visible content.

### When This Code Does NOT Fire

W007 does not fire when a file includes explicit version metadata, such as a "Last updated" date, a version number in a metadata block, or a change history table. System-generated files that use a unified versioning scheme may also be exempt if that scheme is documented.

## Triggering Criteria

- **DS-VC-CON-013**: (Version Metadata Present)

Emitted by DS-VC-CON-013 when no version string, date stamp, or changelog reference is found.
## Related Anti-Patterns

**DS-AP-CONT-009: Versionless Drift** — Documentation that lacks version markers and gradually becomes stale and unreliable without clear indication of its age or maintenance status.

## Related Diagnostic Codes

**DS-DC-W016: (ecosystem-level version inconsistency)** — W007 checks for missing per-file version metadata, while W016 checks for consistency of version metadata across the ecosystem. W007 is file-level; W016 is ecosystem-level.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
