# DS-DC-W006: FORMULAIC_DESCRIPTIONS

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-W006 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | W006 |
| Severity | WARNING |
| Validation Level | L2 — Content Quality |
| Check ID | CNT-005 (v0.0.4b), CHECK-015 (v0.0.4c) |
| Provenance | v0.0.4b content checks; v0.0.4c anti-patterns; v0.0.2c audit data |

## Message

> Multiple sections use identical or near-identical description patterns.

## Remediation

> Write unique, specific descriptions for each section.

## Description

Formulaic descriptions signal copy-paste authoring and reduce content quality by failing to distinguish between distinct concepts. When identical description patterns appear across multiple sections, readers receive no meaningful differentiation and may wonder if the sections themselves are redundant. This pattern often emerges from templates applied mechanically without adaptation to context.

Each section's description should convey its unique purpose, scope, and relevance. While consistency in structure is valuable, consistency should not come at the cost of content specificity. Audit data shows that formulaic descriptions correlate with lower user engagement and comprehension.

### When This Code Fires

W006 fires when multiple sections or entries use identical or near-identical descriptions, suggesting that the descriptions were copied with minimal or no adaptation. This includes exact matches, as well as descriptions that differ only in inconsequential words (e.g., "This section covers X" repeated multiple times with only the value of X changing).

### When This Code Does NOT Fire

W006 does not fire when each section has a unique, specific description that contextualizes its content, even if the descriptions follow a consistent structural pattern. It also does not fire for list items where identical descriptions are legitimately appropriate (e.g., repeating the same type constraint for similar parameters).

## Triggering Criterion

**DS-VC-CON-007: No Formulaic Descriptions**

Each section must have a unique, specific description that contextualizes its content and purpose. This criterion validates that descriptions are not mechanically repeated across sections.

## Related Anti-Patterns

**DS-AP-CONT-007: Formulaic Description** — Descriptions that follow a rigid pattern or are copied from a template without adaptation to the specific section's content.

## Related Diagnostic Codes

**DS-DC-W003: LINK_MISSING_DESCRIPTION** — Both W003 and W006 address description quality: W003 detects entirely missing descriptions, while W006 detects descriptions that are present but lack specificity and uniqueness.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
