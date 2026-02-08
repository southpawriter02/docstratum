# DS-DC-I006: OPTIONAL_SECTIONS_UNMARKED

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-I006 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | I006 |
| **Severity** | INFO |
| **Validation Level** | L4 — DocStratum Extended |
| **Check ID** | DECISION-011 (v0.0.4d) |
| **Provenance** | DECISION-011 (Optional Section Reserved Word); v0.0.4d design decisions |

## Message

> Optional sections not explicitly marked with token estimates.

## Remediation

> Mark optional sections so consumers can skip them to save context.

## Description

This informational code indicates that the document contains sections that could reasonably be skipped by certain readers or agents, but these sections are not explicitly marked as optional or accompanied by token estimates. Marking optional sections enables consumers—particularly AI agents with limited token budgets—to make informed decisions about which content to load or skip.

Optional sections typically include appendices, deep-dive examples, historical context, or supplementary material that enriches understanding but is not essential for core functionality. By explicitly marking these sections with the `optional` reserved word and providing token estimates, authors help consumers allocate their limited context windows more effectively and improve overall user experience.

**When This Code Fires:**
- The document contains sections that could reasonably be optional (appendices, supplementary content).
- These sections lack explicit `optional` markup or token estimate annotations.

**When This Code Does NOT Fire:**
- Optional sections are marked with the `optional` reserved word.
- Token estimates are provided for skippable content.

## Triggering Criteria

Informational observation — no per-file VC criterion. Per C-DEC-04, L3-08 (Optional section used appropriately) is included as INFO-only and does not affect scoring.
## Related Anti-Patterns

None directly identified.

## Related Diagnostic Codes

- **DS-DC-W010** (TOKEN_BUDGET_WARNING): Related concept of token management and context optimization.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
