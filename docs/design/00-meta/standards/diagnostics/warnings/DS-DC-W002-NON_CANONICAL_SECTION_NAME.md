# DS-DC-W002: NON_CANONICAL_SECTION_NAME

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W002 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | W002 |
| **Severity** | WARNING |
| **Validation Level** | L3 — Best Practices |
| **Check ID** | NAM-001 (v0.0.4a) |
| **Provenance** | v0.0.4a naming checks; DECISION-012 (11 canonical names); v0.0.2c frequency analysis |

## Message

> Section name does not match any of the 11 canonical names.

## Remediation

> Use canonical names where possible (see CanonicalSectionName enum).

## Description

Section names play a critical role in maintaining consistency across the documentation ecosystem. The 11 canonical section names represent the result of extensive frequency analysis and best-practice assessment, ensuring that readers can navigate and locate information predictably. When a section uses a non-canonical name, it introduces cognitive friction and makes the documentation less discoverable.

The canonical naming system (defined in DECISION-012) ensures that similar content uses identical headings across different files. This standardization allows for consistent tooling, cross-referencing, and user expectations. Non-canonical names may still convey useful information, but they undermine the ecosystem's structural integrity.

### When This Code Fires

W002 fires when a section heading appears that does not match one of the 11 canonical names defined in the CanonicalSectionName enum. This includes variations in capitalization, word order, or alternative terminology that semantically maps to a canonical concept.

### When This Code Does NOT Fire

W002 does not fire when a section uses an exact match to one of the 11 canonical names, or when the file is explicitly exempt from canonical naming (e.g., specialized domain files with justified deviations).

## Triggering Criteria

- **DS-VC-CON-008**: (Canonical Section Names)

Emitted by DS-VC-CON-008 when an H2 section name does not match any of the 11 canonical names or 32 recognized aliases.
## Related Anti-Patterns

**DS-AP-STRUCT-005: Naming Nebula** — Non-canonical names proliferate when no consistent naming policy is enforced, leading to fragmentation and reduced discoverability.

## Related Diagnostic Codes

**DS-DC-W009: NO_MASTER_INDEX** — Related in that W002 checks individual section names, while W009 checks for the presence of the Master Index section (a critical canonical component).

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
