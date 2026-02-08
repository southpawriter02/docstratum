# DS-DC-W014: AGGREGATE_INCOMPLETE

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W014 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | W014 |
| **Severity** | WARNING |
| **Validation Level** | Ecosystem-level (cross-file validation) |
| **Check ID** | v0.0.7 §5.2 |
| **Provenance** | v0.0.7 §5.2 (Ecosystem-Level Warning Codes) |

## Message

> llms-full.txt does not contain content from all files referenced in the index.

## Remediation

> Regenerate llms-full.txt to include content from all ecosystem files.

## Description

This ecosystem-level diagnostic fires when the llms-full.txt aggregate file exists but is incomplete — it does not include content from all files that the index explicitly references or that exist in the documentation ecosystem. An incomplete aggregate breaks the contract between the ecosystem and consuming systems; callers expect llms-full.txt to be comprehensive, and missing content creates the risk of incomplete context or incorrect decisions based on partial information.

The validation process compares the set of files referenced in the index against the content actually present in llms-full.txt. If any referenced file is missing from the aggregate, or if the ecosystem contains files not included in the index but still part of the project, this diagnostic fires. This is distinct from W013 (missing aggregate) because the file exists — it simply needs to be regenerated to achieve completeness.

**When This Code Fires:** The llms-full.txt file exists in the ecosystem, but when validated against the index and file inventory, it is missing content from one or more documented files or contains outdated versions of existing files.

**When This Code Does NOT Fire:** The llms-full.txt file contains complete and current content from all files in the ecosystem index, or no llms-full.txt file exists (separate concern captured by W013).

## Triggering Criteria

Ecosystem-level diagnostic — no per-file VC criterion. Fires during ecosystem validation (Stage 4) when llms-full.txt is incomplete.
## Related Anti-Patterns

- DS-AP-ECO-003 (Shadow Aggregate) — ecosystem-level pattern of incomplete or stale aggregates

## Related Diagnostic Codes

- DS-DC-W013 (missing aggregate) — inverse scenario: no llms-full.txt exists at all

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
