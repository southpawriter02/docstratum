# DS-DC-E009: NO_INDEX_FILE

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-E009 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | E009 |
| **Severity** | ERROR |
| **Validation Level** | Ecosystem-level |
| **Check ID** | v0.0.7 §5.1 |
| **Provenance** | v0.0.7 §5.1 (Ecosystem-Level Error Codes) |

## Message

> Ecosystem has no llms.txt file (the required root).

## Remediation

> Create an llms.txt file in the project root with an H1 title and section links.

## Description

This error fires at the ecosystem level when a project or documentation tree lacks an llms.txt file in its root directory. The llms.txt file serves as the entry point and index for the entire ecosystem, providing structure and discoverability for all contained files. Without it, the ecosystem is fragmented and lacks a clear root or navigation structure.

The llms.txt file must contain at least an H1 title describing the project and section headers (H2 or lower) with links to major content files. This root index enables readers, tools, and LLMs to understand the ecosystem's organization at a glance.

### When This Code Fires

- A validation scan is run on a project or directory tree.
- No file named exactly "llms.txt" exists in the root of the scanned ecosystem.
- This is an ecosystem-level check performed after all individual file validation completes.

### When This Code Does NOT Fire

- An llms.txt file exists at the root of the ecosystem.
- The file contains valid Markdown with an H1 title and appropriate section structure.

## Triggering Criteria

Ecosystem-level diagnostic — no per-file VC criterion. Fires during ecosystem validation (Stage 4) when no llms.txt index file is found.
## Related Anti-Patterns

- DS-AP-ECO-001 (Index Island)

## Related Diagnostic Codes

- DS-DC-E010 (sibling ecosystem-level error: E009 checks for the existence of the index file itself; E010 checks for orphaned files)
- DS-DC-I010 (single-file ecosystem: informational code indicating a minimal but valid one-file ecosystem)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
