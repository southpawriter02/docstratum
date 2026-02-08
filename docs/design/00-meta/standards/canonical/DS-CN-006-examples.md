# DS-CN-006: Examples

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-006 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Canonical Name** | Examples |
| **Position** | 6 |
| **Enum Value** | `CanonicalSectionName.EXAMPLES` |
| **Alias Count** | 4 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects; DECISION-002 |

## Description

"Examples" is the sixth canonical section in the recommended 10-step ordering sequence. This section provides practical code examples and usage patterns demonstrating how to accomplish common tasks and integrate the project into real-world workflows.

Examples maps directly to Layer 3 (Few-Shot Bank) in the 3-layer architecture defined in DECISION-002. Examples appears in approximately **54% of projects** in the v0.0.2c audit and demonstrates the strongest correlation with quality metrics (r ≈ 0.65). Well-designed Examples sections dramatically improve user success rates and reduce support burden for both human teams and AI agents.

## Recognized Aliases

The following alternative names are normalized to "Examples" by the validator:

| Alias | Source |
|-------|--------|
| `usage` | Focus on usage patterns |
| `use cases` | Common business-oriented terminology |
| `tutorials` | Emphasizes step-by-step instruction |
| `recipes` | Connotes practical, reusable solutions |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **6** — Examples should be the sixth H2 section, appearing after API Reference and before Configuration. This positions practical patterns immediately following specification details.

**Rationale:** The sequencing of Core Concepts → API Reference → Examples creates a cognitive flow from theory to specification to practice. This ordering mirrors effective learning progression and allows users to apply abstract concepts and specifications to concrete problems. For AI agents, examples serve as training data for few-shot learning, making their position after reference documentation critical for prompt engineering effectiveness.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. Examples is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether canonical sections appear in the recommended order.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
