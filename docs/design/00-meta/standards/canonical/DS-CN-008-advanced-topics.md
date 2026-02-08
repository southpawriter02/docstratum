# DS-CN-008: Advanced Topics

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-008 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Canonical Name** | Advanced Topics |
| **Position** | 8 |
| **Enum Value** | `CanonicalSectionName.ADVANCED_TOPICS` |
| **Alias Count** | 2 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects |

## Description

"Advanced Topics" is the eighth canonical section in the recommended 10-step ordering sequence. This section provides deep-dive content for experienced users, including implementation details, internal architecture, performance optimization techniques, and other sophisticated concepts that require foundational knowledge to understand effectively.

Advanced Topics appears in approximately **42% of projects** in the v0.0.2c audit. This section serves as the bridge between user-facing documentation and implementation-level knowledge, enabling expert users and contributors to understand project internals and unlock advanced capabilities.

## Recognized Aliases

The following alternative names are normalized to "Advanced Topics" by the validator:

| Alias | Source |
|-------|--------|
| `advanced` | Abbreviated form |
| `internals` | Focus on internal implementation details |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **8** — Advanced Topics should be the eighth H2 section, appearing after Configuration and before Troubleshooting. This positions sophisticated content after core usage but before problem-solving.

**Rationale:** Advanced Topics assumes foundational understanding of the project. Positioning it after Configuration ensures readers have mastered basic and intermediate concepts. Placing it before Troubleshooting allows advanced users to understand internal mechanisms before diagnosing complex issues. This ordering supports progressive complexity and prevents cognitive overload for new users.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. Advanced Topics is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether canonical sections appear in the recommended order.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
