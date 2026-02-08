# DS-DC-W015: INCONSISTENT_PROJECT_NAME

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-W015 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | W015 |
| Severity | WARNING |
| Validation Level | Ecosystem-level (cross-file validation) |
| Check ID | v0.0.7 §5.2 |
| Provenance | v0.0.7 §5.2 (Ecosystem-Level Warning Codes) |

## Message

> H1 title differs between files in the ecosystem.

## Remediation

> Ensure all files use the same project name in their H1 title.

## Description

This ecosystem-level diagnostic identifies instances where documentation files within the same project use different project names in their primary H1 titles. The H1 title is the top-level identity statement for a documentation file; inconsistency across files signals identity drift and undermines reader confidence in the coherence of the documentation ecosystem. Readers should encounter the same project name consistently, reinforcing the project's unified identity.

The validation engine scans all files and extracts their H1 titles, then compares the project name portion across the ecosystem. If File A declares itself as "Project Alpha v2.0" and File B declares itself as "Alpha v2.0" or "The Alpha Project," this diagnostic fires. While minor stylistic variations (articles, capitalization) may be tolerated in some contexts, substantive differences in project naming indicate a documentation maintenance issue.

**When This Code Fires:** Files in the ecosystem have H1 titles containing different project names (e.g., "MyApp" vs. "My Application" vs. "MyApp Project"), despite being part of the same documented project.

**When This Code Does NOT Fire:** All files consistently use the same project name in their H1 titles, or the ecosystem contains only a single file and thus has no basis for comparison.

## Triggering Criteria

Cross-file diagnostic — includes source_files and title variations context. Ecosystem codes do not have per-file VC criterion; this code fires during ecosystem validation (Stage 4) when identity consistency checks occur across the entire documentation set.

## Related Anti-Patterns

None directly.

## Related Diagnostic Codes

- DS-DC-W016 (inconsistent versioning) — sibling concern: version numbers drift across files
- DS-DC-E001 (H1 title requirement) — per-file requirement that an H1 title exists

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
