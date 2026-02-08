# DS-CN-005: API Reference

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-005 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Canonical Name** | API Reference |
| **Position** | 5 |
| **Enum Value** | `CanonicalSectionName.API_REFERENCE` |
| **Alias Count** | 3 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects; DECISION-003 |

## Description

"API Reference" is the fifth canonical section in the recommended 10-step ordering sequence. This section provides complete endpoint documentation, parameter specifications, response formats, and usage examples for all public APIs exposed by the project.

API Reference appears in approximately **61% of projects** in the v0.0.2c audit, making it one of the more commonly included sections. This section explicitly supports GitHub Flavored Markdown table usage as documented in DECISION-003, enabling clear, structured presentation of endpoint specifications and parameter matrices.

## Recognized Aliases

The following alternative names are normalized to "API Reference" by the validator:

| Alias | Source |
|-------|--------|
| `api` | Abbreviated form |
| `reference` | Generic reference terminology |
| `endpoints` | Focus on REST or service endpoints |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **5** — API Reference should be the fifth H2 section, appearing after Core Concepts and before Examples. This positions detailed specification before practical usage patterns.

**Rationale:** API Reference serves as the authoritative specification document. Positioning it after conceptual grounding (Core Concepts) but before practical examples (Examples) enables users to understand both the "why" (concepts) and the "how" (examples) surrounding API capabilities. This ordering supports efficient reference lookup while maintaining semantic context.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. API Reference is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether canonical sections appear in the recommended order.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
