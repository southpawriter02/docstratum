# DS-DC-W010: TOKEN_BUDGET_EXCEEDED

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-W010 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | W010 |
| **Severity** | WARNING |
| **Validation Level** | L3 — Best Practices |
| **Check ID** | SIZ-001 (v0.0.4a), DECISION-013 |
| **Provenance** | DECISION-013 (token budget tiers); v0.0.4a size checks; 3-tier budget system (Standard/Comprehensive/Extended) |

## Message

> File exceeds the recommended token budget for its tier.

## Remediation

> Trim content to stay within the tier's token budget.

## Description

Token budgets represent a constraint on file size that improves usability, performance, and cognitive load for readers. The 3-tier budget system (Standard/Comprehensive/Extended) ensures that files remain digestible while allowing appropriate growth for different content types. Exceeding a tier's token budget suggests that content could be split into multiple files, condensed, or better organized.

Files that exceed their tier budget are harder to search, slower to load in some contexts, and may overwhelm readers with information density. Staying within budget encourages focused, intentional content while still allowing sufficient depth.

### When This Code Fires

W010 fires when a file's token count exceeds the recommended budget for its assigned tier. The 3-tier system defines specific token limits: Standard, Comprehensive, and Extended. W010 fires when the file's measured token count is above the threshold for its declared tier.

### When This Code Does NOT Fire

W010 does not fire when a file stays within its tier's token budget, or when a file's complexity legitimately requires an exception (documented and approved). It also does not fire for files in the Extended tier operating at the maximum budgeted size.

## Triggering Criteria

- **DS-VC-CON-012**: (Token Budget Respected)

Emitted by DS-VC-CON-012 when file token count exceeds the recommended budget for its tier.
## Related Anti-Patterns

**DS-AP-STRAT-002: Monolith Monster** — When a file significantly exceeds its token budget, combining content that should be split across multiple focused files, creating a bloated, unwieldy document.

## Related Diagnostic Codes

**DS-DC-E008: (E008 error — absolute 100K limit)** — E008 is a hard error that fires when an absolute maximum token limit (100K) is exceeded, indicating a critical problem. W010 is a softer warning that fires when tier-specific budgets are exceeded, allowing for intentional exceptions. E008 is blocking; W010 is advisory.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
