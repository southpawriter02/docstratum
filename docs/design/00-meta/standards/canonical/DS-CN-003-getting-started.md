# DS-CN-003: Getting Started

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-003 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Canonical Name** | Getting Started |
| **Position** | 3 |
| **Enum Value** | `CanonicalSectionName.GETTING_STARTED` |
| **Alias Count** | 4 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects |

## Description

"Getting Started" is the third canonical section in the recommended 10-step ordering sequence. This section serves as the entry point for new users, containing installation instructions, first-use steps, and quick examples that enable rapid onboarding.

Getting Started demonstrates exceptional adoption: **78% frequency** in the v0.0.2c audit of 450+ projects. This high prevalence reflects its critical role in user success. Well-structured Getting Started sections dramatically reduce initial friction and support both human developers and AI agents in quickly becoming productive with the project.

## Recognized Aliases

The following alternative names are normalized to "Getting Started" by the validator:

| Alias | Source |
|-------|--------|
| `quickstart` | Common abbreviated convention |
| `quick start` | Spaced variant of quickstart |
| `installation` | Focus on setup step |
| `setup` | Generic setup terminology |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **3** — Getting Started should be the third H2 section, following Master Index and LLM Instructions. This positions practical onboarding before deeper conceptual or reference content.

**Rationale:** New users (human or AI) benefit most from immediate, actionable steps. Positioning Getting Started third ensures users encounter navigation and agent guidance before engaging with installation and setup. This ordering supports the principle that friction-to-first-success should be minimized in documentation architecture.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. Getting Started is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether canonical sections appear in the recommended order.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
