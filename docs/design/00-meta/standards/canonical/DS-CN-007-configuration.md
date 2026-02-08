# DS-CN-007: Configuration

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-007 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Canonical Name** | Configuration |
| **Position** | 7 |
| **Enum Value** | `CanonicalSectionName.CONFIGURATION` |
| **Alias Count** | 3 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects |

## Description

"Configuration" is the seventh canonical section in the recommended 10-step ordering sequence. This section documents configuration options, environment variables, settings, and customization parameters that users can modify to adapt the project to their environment and requirements.

Configuration appears in approximately **58% of projects** in the v0.0.2c audit. Configuration documentation is critical for reducing setup friction and enabling users to troubleshoot environment-specific issues. Clear configuration documentation supports both manual setup and automated provisioning workflows.

## Recognized Aliases

The following alternative names are normalized to "Configuration" by the validator:

| Alias | Source |
|-------|--------|
| `config` | Abbreviated form |
| `settings` | Focus on user-adjustable parameters |
| `options` | Generic terminology for customizable features |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **7** — Configuration should be the seventh H2 section, appearing after Examples and before Advanced Topics. This positions practical customization after basic usage patterns.

**Rationale:** Users typically need to understand basic usage before tuning configuration for their specific environment. Positioning Configuration after Examples ensures users have working examples before diving into environment-specific tuning. This ordering supports a natural progression from "make it work" (Getting Started, Examples) to "make it work for me" (Configuration).

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. Configuration is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether canonical sections appear in the recommended order.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
