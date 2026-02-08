# DS-DC-W016: INCONSISTENT_VERSIONING

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W016 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | W016 |
| **Severity** | WARNING |
| **Validation Level** | Ecosystem-level (cross-file validation) |
| **Check ID** | v0.0.7 §5.2 |
| **Provenance** | v0.0.7 §5.2 (Ecosystem-Level Warning Codes) |

## Message

> Version metadata differs between files (e.g., one says v2.1, another says v2.0).

## Remediation

> Update all files to reflect the current version number.

## Description

This ecosystem-level diagnostic fires when version metadata in the documentation differs across files. A documentation ecosystem should present a unified version number; when files report different versions, it suggests that some files have not been updated during a release cycle, or that version information has drifted over time. This creates ambiguity about the true current version and can mislead users about which version of the project the documentation describes.

Version inconsistency is a form of identity drift (companion to W015, which addresses project name inconsistency). The validation engine extracts version information from file metadata, headers, or explicit version fields and compares them across the ecosystem. If some files claim v2.1 and others claim v2.0, or if some files omit version information entirely, this diagnostic alerts maintainers to the inconsistency.

**When This Code Fires:** Files in the ecosystem declare different version numbers (e.g., one states v2.1, another states v2.0), or some files lack version information while others include it, indicating incomplete version alignment.

**When This Code Does NOT Fire:** All files consistently declare the same version number, or all files are intentionally version-agnostic (a rare and typically undesirable state).

## Triggering Criteria

Ecosystem-level diagnostic — no per-file VC criterion. Fires during ecosystem validation (Stage 4) when version metadata differs between files.
## Related Anti-Patterns

- DS-AP-CONT-009 (Versionless Drift) — broader pattern of version information degradation across content

## Related Diagnostic Codes

- DS-DC-W007 (per-file missing version) — detects when a single file lacks version information
- DS-DC-W015 (inconsistent project name) — sibling concern: project name consistency across files

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
