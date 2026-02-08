# DS-DC-I001: NO_LLM_INSTRUCTIONS

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-I001 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | I001 |
| **Severity** | INFO |
| **Validation Level** | L4 — DocStratum Extended |
| **Check ID** | CNT-010 (v0.0.4b) |
| **Provenance** | v0.0.0 Stripe LLM Instructions Pattern; v0.0.4d DECISION-002 (3-Layer Architecture); v0.0.2c audit: 0% current adoption |

## Message

> No LLM Instructions section found.

## Remediation

> Add an LLM Instructions section with positive/negative directives.

## Description

This diagnostic fires when the parser finds no section matching "LLM Instructions" (or recognized aliases: "Instructions", "Agent Instructions") in the file. The LLM Instructions section is the strongest quality differentiator identified in DocStratum's research — it explicitly tells AI agents how to use the documentation, what to prioritize, and what to avoid.

### Why This Is INFO, Not WARNING

As of the v0.0.2 audit, **0% of real-world implementations** include an LLM Instructions section. This is an entirely novel concept introduced by the Stripe pattern analysis (v0.0.0) and formalized in DocStratum's 3-Layer Architecture (DECISION-002). Marking it as a WARNING would penalize every existing file for missing something the community hasn't adopted yet. Instead, it appears as an INFO-level suggestion — non-blocking and non-scoring — that highlights the single most impactful improvement a file author could make.

### When This Code Fires

- No H2 section name matches "LLM Instructions" or any alias in `SECTION_NAME_ALIASES`
- File has an "Instructions" section but it contains installation instructions, not LLM-facing directives (false positive risk — the validator checks section name only, not content)

### When This Code Does NOT Fire

- File contains `## LLM Instructions` → no diagnostic
- File contains `## Instructions` (alias match) → no diagnostic
- File contains `## Agent Instructions` (alias match) → no diagnostic

## Triggering Criteria

- **DS-VC-APD-001** (LLM Instructions Section): This diagnostic is emitted when criterion DS-VC-APD-001 detects the absence of an LLM Instructions section.

## Related Anti-Patterns

- **DS-AP-CONT-008** (Silent Agent): A file with no LLM-facing guidance despite being an AI documentation file. The presence of I001 is effectively a detection signal for the Silent Agent anti-pattern.

## Related Diagnostic Codes

- **DS-DC-I008** (NO_INSTRUCTION_FILE): Ecosystem-level variant — fires when the entire ecosystem (not just one file) lacks LLM instructions. I001 is per-file; I008 is per-ecosystem.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase A example file |
