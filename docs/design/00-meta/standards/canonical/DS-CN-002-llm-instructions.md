# DS-CN-002: LLM Instructions

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-002 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Canonical Name** | LLM Instructions |
| **Position** | 2 |
| **Enum Value** | `CanonicalSectionName.LLM_INSTRUCTIONS` |
| **Alias Count** | 2 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects |

## Description

"LLM Instructions" is the second canonical section in the recommended 10-step ordering sequence. This section provides explicit instructions for LLM/AI agents consuming the documentation, telling them how to use the file, what to prioritize, and how to format responses.

This is a forward-looking section unique to DocStratum's vision of documentation-as-interface-for-AI. The section enables documentation authors to directly communicate context, constraints, and formatting expectations to AI agents in a standardized way. Though currently only ~0% ecosystem adoption in the v0.0.2c audit, this section represents a critical emerging practice as AI-native documentation becomes standard.

## Recognized Aliases

The following alternative names are normalized to "LLM Instructions" by the validator:

| Alias | Source |
|-------|--------|
| `instructions` | Generic/abbreviated form |
| `agent instructions` | Explicit agent-focused terminology |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **2** — LLM Instructions should be the second H2 section in the file, immediately following Master Index. This positioning prioritizes AI-agent context before consuming any project content.

**Rationale:** By placing LLM Instructions second, documentation authors establish behavioral constraints and usage expectations early in the agent's reading sequence. This ensures that agent-specific guidance is available before the agent consumes substantive content sections. This ordering supports the AI-first documentation paradigm that DocStratum advocates.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. LLM Instructions is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether canonical sections appear in the recommended order.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
