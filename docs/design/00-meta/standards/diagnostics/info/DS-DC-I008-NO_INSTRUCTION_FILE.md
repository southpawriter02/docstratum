# DS-DC-I008: NO_INSTRUCTION_FILE

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-I008 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Code** | I008 |
| **Severity** | INFO |
| **Validation Level** | Ecosystem-level (cross-file validation) |
| **Check ID** | v0.0.7 §5.3 |
| **Provenance** | v0.0.7 §5.3 (Ecosystem-Level Informational Codes) |

## Message

> No llms-instructions.txt or LLM Instructions section exists in the ecosystem.

## Remediation

> Add an LLM Instructions section to llms.txt or create a dedicated llms-instructions.txt file.

## Description

This informational code indicates that the documentation ecosystem lacks formal LLM instructions—either as a dedicated `llms-instructions.txt` file or as a structured section within the primary `llms.txt` index. LLM instructions provide ecosystem-level guidance to AI agents, clarifying intent, scope, conventions, and constraints that apply across the entire documentation ecosystem.

Without explicit LLM instructions, AI agents must infer intent and boundaries from context alone, increasing the risk of misinterpretation or out-of-scope behavior. A dedicated instructions file (or section) acts as a meta-layer that sets expectations and constraints for agent behavior, enabling more reliable and predictable system interactions. This is the ecosystem-level variant of DS-DC-I001 (per-file missing instructions).

**When This Code Fires:**
- No `llms-instructions.txt` file exists in the ecosystem root.
- The primary `llms.txt` file contains no `LLM Instructions` section.
- Agent guidance is absent at the ecosystem level.

**When This Code Does NOT Fire:**
- A dedicated `llms-instructions.txt` file exists and is referenced by `llms.txt`.
- The `llms.txt` file includes a structured `LLM Instructions` section.

## Triggering Criteria

Ecosystem-level diagnostic — no per-file VC criterion. Fires during ecosystem validation (Stage 4) when no llms-instructions.txt file or LLM Instructions section exists.
## Related Anti-Patterns

**DS-AP-CONT-008** (Silent Agent): Ecosystem-level variant; lack of LLM instructions creates unpredictable agent behavior.

## Related Diagnostic Codes

- **DS-DC-I001** (NO_LLM_INSTRUCTIONS): Per-file variant; I001 fires for missing per-file instructions, I008 fires for ecosystem-wide missing instructions.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
