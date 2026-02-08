# DS-CN-010: FAQ

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-010 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Canonical Name** | FAQ |
| **Position** | 10 |
| **Enum Value** | `CanonicalSectionName.FAQ` |
| **Alias Count** | 1 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects |

## Description

"FAQ" is the tenth canonical section in the recommended 10-step ordering sequence. This section presents frequently asked questions and their answers, organized by topic or concern. FAQ sections serve as both navigation aids and common-question resolution tools, enabling users to quickly find answers to questions that have been asked repeatedly by the community.

FAQ appears in approximately **45% of projects** in the v0.0.2c audit. FAQ sections represent a terminal position in the canonical ordering sequence, representing the final "browse and discover" section before supplementary or optional content. Effective FAQ sections aggregate community questions and reduce duplicate support inquiries.

## Recognized Aliases

The following alternative names are normalized to "FAQ" by the validator:

| Alias | Source |
|-------|--------|
| `frequently asked questions` | Expanded form of FAQ acronym |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **10** (terminal) — FAQ should be the tenth H2 section, appearing after Troubleshooting and before any Optional sections. This is the final position in the canonical 10-step sequence.

**Rationale:** FAQ represents the terminal, browsable section of canonical documentation. It serves as a safety net for questions not addressed in structured sections above it. Positioning FAQ at the end of the canonical sequence allows users to progress through structured learning (Concepts, Examples) and structured problem-solving (Troubleshooting) before encountering open-ended question browsing. This ordering respects goal-directed navigation while providing exploratory browsing at the conclusion.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. FAQ is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether canonical sections appear in the recommended order.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
