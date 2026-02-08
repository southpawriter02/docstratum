# DS-DC-E008: EXCEEDS_SIZE_LIMIT

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-E008 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | E008 |
| **Severity** | ERROR |
| **Validation Level** | L0 — Parseable |
| **Check ID** | SIZ-003 (v0.0.4a), CHECK-003 (v0.0.4c Monolith Monster) |
| **Provenance** | v0.0.4a size checks; DECISION-013 (token budget tiers); v0.0.4c anti-patterns |

## Message

> File exceeds the maximum recommended size (>100K tokens).

## Remediation

> Decompose into a tiered file strategy (index + full + per-section files).

## Description

This error fires when a single file exceeds the practical size limit of 100K tokens (roughly 300K–400K characters depending on language). Files of this size exceed the context window of most LLMs and become unwieldy for readers, reviewers, and downstream systems. This violates the "Monolith Monster" anti-pattern check.

The solution is to decompose the file into a tiered strategy: create an index file that summarizes and links to more granular per-section or per-subsystem files. This allows readers and systems to navigate the documentation more efficiently while keeping individual files within reasonable cognitive and computational bounds.

### When This Code Fires

- The file's token count (as measured by a standard tokenizer) exceeds 100,000 tokens.
- This is a Phase C L0 check performed early in the validation pipeline (L0-04).

### When This Code Does NOT Fire

- The file contains fewer than 100,000 tokens.
- The file is properly decomposed into multiple smaller files with cross-references.

## Triggering Criteria

L0 pipeline prerequisite gate — no formal VC criterion file. Related to DS-VC-CON-012 (Token Budget Respected) which checks tier compliance at L3. L0-04 (Under Maximum Token Limit) check documented in DS-VL-L0-PARSEABLE.md.
## Related Anti-Patterns

- DS-AP-STRAT-002 (Monolith Monster) — file too large for any single context window

## Related Diagnostic Codes

- DS-DC-W010 (token budget warning: W010 fires when a file exceeds recommended tier thresholds; E008 fires for absolute hard limit)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
