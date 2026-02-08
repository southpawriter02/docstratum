# DS-DC-E010: ORPHANED_ECOSYSTEM_FILE

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-E010 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | E010 |
| Severity | ERROR |
| Validation Level | Ecosystem-level |
| Check ID | v0.0.7 §5.1 |
| Provenance | v0.0.7 §5.1 (Ecosystem-Level Error Codes) |

## Message

> A file in the ecosystem is not referenced by any other file.

## Remediation

> Add a link to this file from llms.txt or from another content page.

## Description

This error fires at the ecosystem level when a file exists in the project tree but is not referenced by any other file — not from llms.txt, not from index pages, and not from content pages. Such "orphaned" files represent dead code and create cognitive overhead. Every file in the ecosystem should be intentionally linked from at least one other file to establish its role and context.

The remediation is straightforward: add a link to the orphaned file from llms.txt (the primary index) or from a relevant content page. This establishes the file's place in the information architecture and makes it discoverable to readers and tools.

### When This Code Fires

- An ecosystem-level validation scan identifies a file with no incoming references.
- No other file in the ecosystem contains a link pointing to this file.
- This is an ecosystem-level check performed after all individual file validation completes.

### When This Code Does NOT Fire

- The file is referenced by at least one other file in the ecosystem (via link, include, or reference).
- The file is explicitly marked as internal/private and excluded from the ecosystem check (Phase D feature).

## Triggering Criteria

Ecosystem validation stage (no per-file VC criterion — this is a cross-file check)

## Related Anti-Patterns

- DS-AP-ECO-006 (Orphan Nursery)

## Related Diagnostic Codes

- DS-DC-E009 (sibling ecosystem-level error: E009 checks for existence of the root index; E010 checks for unreferenced files)
- DS-DC-W012 (broken cross-file links — related but different: W012 fires when a link exists but the target is broken; E010 fires when no link to the file exists at all)

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
