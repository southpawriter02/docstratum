# DS-CN-004: Core Concepts

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-004 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Canonical Name** | Core Concepts |
| **Position** | 4 |
| **Enum Value** | `CanonicalSectionName.CORE_CONCEPTS` |
| **Alias Count** | 3 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects |

## Description

"Core Concepts" is the fourth canonical section in the recommended 10-step ordering sequence. This section defines the project's foundational mental models and key abstractions that users must understand to use the project effectively.

Core Concepts maps directly to Layer 2 (Concept Map) in the 3-layer architecture defined in DECISION-002. This section appears in approximately **40% of projects** in the v0.0.2c audit. Well-articulated Core Concepts sections enable both human developers and AI agents to understand the semantic domain and reasoning framework required for productive engagement with the project.

## Recognized Aliases

The following alternative names are normalized to "Core Concepts" by the validator:

| Alias | Source |
|-------|--------|
| `concepts` | Abbreviated form |
| `key concepts` | Emphasizes importance of foundational ideas |
| `fundamentals` | Focus on fundamental principles |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **4** — Core Concepts should be the fourth H2 section, appearing after Getting Started but before API Reference. This positions conceptual grounding before detailed API documentation.

**Rationale:** Users benefit from understanding foundational concepts before diving into specific API details or usage patterns. This ordering respects Bloom's taxonomy by placing conceptual understanding before application and reference knowledge. For AI agents, semantic grounding improves accuracy and relevance of downstream task execution.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. Core Concepts is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether canonical sections appear in the recommended order.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
