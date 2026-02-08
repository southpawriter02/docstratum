# DS-DC-W018: UNBALANCED_TOKEN_DISTRIBUTION

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W018 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | W018 |
| **Severity** | WARNING |
| **Validation Level** | Ecosystem-level (cross-file validation) |
| **Check ID** | v0.0.7 §5.2 |
| **Provenance** | v0.0.7 §5.2 (Ecosystem-Level Warning Codes) |

## Message

> One file consumes >70% of total ecosystem tokens while others are near-empty.

## Remediation

> Distribute content more evenly across files or consolidate into fewer files.

## Description

This ecosystem-level diagnostic identifies imbalanced token distribution across documentation files. When a single file consumes more than 70% of the total tokens in the ecosystem while others are near-empty, it suggests that the file organization does not match the actual information structure of the project. Such imbalance often indicates that content has not been properly split into logical units, or that some files serve only as stubs or containers for navigation.

Well-organized documentation distributes content proportionally across files, with each file having a distinct purpose and substantial contribution. When one file dominates the ecosystem by token count, navigation becomes inefficient, readers struggle to find specific topics, and the file becomes difficult to maintain. This diagnostic encourages maintainers to reconsider their file structure: either split the large file into smaller topical units or consolidate the smaller files if they are truly insubstantial.

**When This Code Fires:** The ecosystem contains at least two files (to allow for comparison), and one file accounts for more than 70% of the total token count, while at least one other file is near-empty (e.g., <5% of the ecosystem tokens).

**When This Code Does NOT Fire:** Token distribution is reasonably balanced (no single file exceeds 70% of the total), or the ecosystem contains only a single file.

## Triggering Criteria

Ecosystem-level diagnostic — no per-file VC criterion. Related to DS-VC-APD-006 (Token-optimized Structure) at the per-file level. Fires during ecosystem validation when one file consumes >70% of total ecosystem tokens.
## Related Anti-Patterns

- DS-AP-ECO-005 (Token Black Hole) — ecosystem-level pattern of extreme token concentration in a single file

## Related Diagnostic Codes

- DS-DC-W017 (redundant content) — sibling concern: W017 addresses unintended duplication, W018 addresses imbalance
- DS-DC-E008 (absolute file size limit) — per-file constraint on maximum file size
- DS-DC-W010 (per-file token budget) — per-file guidance on token allocation

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
