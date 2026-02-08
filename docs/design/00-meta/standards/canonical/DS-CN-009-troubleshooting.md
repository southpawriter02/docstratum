# DS-CN-009: Troubleshooting

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-009 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Canonical Name** | Troubleshooting |
| **Position** | 9 |
| **Enum Value** | `CanonicalSectionName.TROUBLESHOOTING` |
| **Alias Count** | 3 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects |

## Description

"Troubleshooting" is the ninth canonical section in the recommended 10-step ordering sequence. This section documents common problems users encounter, their root causes, and step-by-step solutions for resolving issues. Troubleshooting documentation is critical for reducing support load and enabling users to self-serve problem resolution.

Troubleshooting appears in approximately **52% of projects** in the v0.0.2c audit. Well-structured troubleshooting sections significantly reduce user frustration and support tickets. This section enables both human users and AI agents to diagnose and resolve issues efficiently.

## Recognized Aliases

The following alternative names are normalized to "Troubleshooting" by the validator:

| Alias | Source |
|-------|--------|
| `debugging` | Focus on diagnostic techniques |
| `common issues` | Emphasizes frequency of problems |
| `known issues` | Emphasizes known and acknowledged problems |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **9** — Troubleshooting should be the ninth H2 section, appearing after Advanced Topics and before FAQ. This positions problem-solving strategies before frequently asked questions.

**Rationale:** Users encountering problems benefit from comprehensive troubleshooting guidance that connects symptoms to root causes and solutions. Positioning Troubleshooting near the end of the main sequence ensures users have encountered the project thoroughly enough to understand complex diagnostics. Placing it before FAQ allows specific solutions to precede general questions, supporting structured problem-solving before FAQ-style browsing.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. Troubleshooting is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether canonical sections appear in the recommended order.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
