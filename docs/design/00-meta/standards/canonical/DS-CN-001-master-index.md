# DS-CN-001: Master Index

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-001 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Canonical Name** | Master Index |
| **Position** | 1 (first in canonical ordering) |
| **Enum Value** | `CanonicalSectionName.MASTER_INDEX` |
| **Alias Count** | 5 |
| **Provenance** | DECISION-012; v0.0.2c frequency analysis of 450+ projects; DECISION-010 |

## Description

"Master Index" is the first canonical section name in the recommended 10-step ordering sequence. It serves as the navigation entry point within an llms.txt file — a table-of-contents-like section that links to the most important resources, helping AI agents quickly orient themselves.

The Master Index is one of the most impactful structural elements identified in the research. Files containing a Master Index achieve an **87% LLM task success rate** compared to **31%** for files without one (v0.0.2d finding). This dramatic difference is why DS-VC-CON-009 (Master Index Present) is a dedicated validation criterion.

## Recognized Aliases

The following alternative names are normalized to "Master Index" by the validator:

| Alias | Source |
|-------|--------|
| `table of contents` | Common web convention |
| `toc` | Common abbreviation |
| `index` | Generic navigation term |
| `docs` | Most common real-world usage (v0.0.2c) |
| `documentation` | Expanded form of "docs" |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

Position **1** — the Master Index should be the first H2 section in the file. This positioning is checked by DS-VC-STR-008 (Canonical Section Ordering) and deviations trigger DS-DC-W008 (SECTION_ORDER_NON_CANONICAL).

**Rationale:** The Master Index appears first because it serves as the navigation entry point. An AI agent encountering the file for the first time should find orientation links before diving into content. Placing it first also means it will be included even in heavily truncated context windows.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. The Master Index is one of the 11 names checked.
- **DS-VC-CON-009** (Master Index Present): Specifically checks for the presence of a Master Index section.
- **DS-VC-STR-008** (Canonical Section Ordering): Checks whether the Master Index appears in position 1.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.
- **DS-DC-W009** (NO_MASTER_INDEX): Fires when no Master Index section is found.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase A example file |
