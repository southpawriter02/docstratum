# DS-DC-W017: REDUNDANT_CONTENT

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W017 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | W017 |
| **Severity** | WARNING |
| **Validation Level** | Ecosystem-level (cross-file validation) |
| **Check ID** | v0.0.7 §5.2 |
| **Provenance** | v0.0.7 §5.2 (Ecosystem-Level Warning Codes) |

## Message

> Significant content duplication between files (>60% overlap) beyond expected index-to-full duplication.

## Remediation

> Refactor duplicated content into a single source and cross-reference.

## Description

This ecosystem-level diagnostic identifies cases where multiple files contain substantially duplicated content — more than 60% overlap — beyond what is naturally expected when an index file (llms.txt) is duplicated into a comprehensive aggregate (llms-full.txt). Content duplication wastes space, creates maintenance burdens (changes must be made in multiple places), and risks divergence (different files gradually showing different versions of the same content).

The validation engine performs textual analysis on file pairs, computing similarity scores based on shared phrases, sections, and logical structure. A 60% overlap threshold is chosen to capture significant duplication while excluding minor commonalities (e.g., a shared disclaimer or footer appearing in all files). The validation explicitly excludes the expected duplication between llms.txt and llms-full.txt, which is by design; this code targets unintended duplication.

**When This Code Fires:** Two or more files in the ecosystem share more than 60% of their content, and this duplication is not the expected pairing between an index file and its comprehensive aggregate.

**When This Code Does NOT Fire:** Content is distributed across distinct files with minimal overlap (below 60%), or the detected overlap is the intended duplication between an index and aggregate file.

## Triggering Criteria

Ecosystem-level diagnostic — no per-file VC criterion. Fires during ecosystem validation (Stage 4) when significant content duplication is detected between files.
## Related Anti-Patterns

None directly.

## Related Diagnostic Codes

- DS-DC-W018 (unbalanced token distribution) — sibling concern: W017 addresses duplication, W018 addresses imbalance in content distribution

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
