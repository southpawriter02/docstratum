# DS-DC-W013: MISSING_AGGREGATE

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-W013 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | W013 |
| Severity | WARNING |
| Validation Level | Ecosystem-level (cross-file validation) |
| Check ID | v0.0.7 §5.2 |
| Provenance | v0.0.7 §5.2 (Ecosystem-Level Warning Codes) |

## Message

> Index file token count suggests a project large enough to benefit from llms-full.txt, but none exists.

## Remediation

> Create an llms-full.txt file containing the full content of all documentation pages.

## Description

This ecosystem-level diagnostic identifies projects that have grown large enough (>4,500 tokens in the index file, per DECISION-013 Comprehensive tier) to warrant an aggregate document for LLM consumption, but no llms-full.txt file currently exists. The aggregate file serves as a machine-readable, token-efficient summary of the entire documentation ecosystem, enabling AI systems to process the full project context in a single read operation.

The token threshold of 4,500 tokens in the index file indicates that the project has reached Comprehensive tier complexity, making it a candidate for aggregation. Without an llms-full.txt file, external systems and AI agents must parse individual documentation files or construct the aggregate themselves, creating inefficiency and potential inconsistency. This diagnostic alerts maintainers that the time has come to create the aggregate file.

**When This Code Fires:** The index file (llms.txt or equivalent) exceeds 4,500 tokens in total content, but no llms-full.txt file exists in the documentation ecosystem.

**When This Code Does NOT Fire:** The project is below the 4,500-token threshold, or an llms-full.txt file already exists regardless of project size.

## Triggering Criteria

Cross-file diagnostic — includes ecosystem-wide token count and file inventory context. Ecosystem codes do not have per-file VC criterion; this code fires during ecosystem validation (Stage 4) when size and completeness checks occur across the entire documentation set.

## Related Anti-Patterns

None directly.

## Related Diagnostic Codes

- DS-DC-W014 (aggregate incomplete) — inverse scenario: llms-full.txt exists but does not contain all ecosystem files

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
