# DS-CN-011: Optional

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CN-011 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Canonical Name** | Optional |
| **Position** | No fixed position (always last) |
| **Enum Value** | `CanonicalSectionName.OPTIONAL` |
| **Alias Count** | 3 |
| **Provenance** | DECISION-012; DECISION-011; v0.0.2c frequency analysis of 450+ projects |

## Description

"Optional" is the eleventh canonical section name, serving as a designation for supplementary content that is not required for core project usage. Unlike the first ten canonical sections which should appear in a specific order, Optional content must be explicitly marked per DECISION-011 and is always positioned after all core canonical sections, regardless of physical order.

Optional content includes appendices, extras, supplementary references, and non-essential material. The Optional designation enables validation tools to distinguish between core documentation and supplementary resources, supporting intelligent content prioritization in context-limited scenarios (e.g., truncated prompts for AI agents).

## Recognized Aliases

> **DocStratum Extension:** Alias support is a DocStratum extension not present in the reference implementation. The canonical Python parser (`miniparse.py` in `AnswerDotAI/llms-txt`) matches the section name `'Optional'` exactly, with case-sensitive comparison (`k != 'Optional'`). It does not recognize alternative names. DocStratum's alias normalization is a usability extension that allows documentation authors to use conventional names like "Appendix" while still receiving Optional-section treatment in validation and context generation. See `DS-AUDIT-extension-labeling.md` for the full extension classification.

The following alternative names are normalized to "Optional" by the validator:

| Alias | Source | `spec_origin` |
|-------|--------|---------------|
| `supplementary` | Emphasizes non-essential supporting role | `EXT` |
| `appendix` | Traditional documentation convention | `EXT` |
| `extras` | Colloquial term for additional material | `EXT` |

These aliases are defined in `SECTION_NAME_ALIASES` in `src/docstratum/schema/constants.py`.

## Canonical Position

**No fixed position** — Optional sections are always placed after all numbered canonical sections (1-10), regardless of their physical position in the document. This distinctive positioning rule is documented in DS-DD-011 and enforced by DS-VC-STR-007.

**Rationale:** Optional sections serve a different role than core canonical sections. They are supplementary rather than progressive. By placing all Optional content after the canonical sequence, documentation ensures that context-limited readers (especially AI agents with restricted token windows) encounter core content before supplementary material. This positioning maximizes utility in truncated contexts while preserving access to supplementary content for full-context readers. The "always last" rule applies regardless of the section's appearance in the document source.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Checks whether section names match canonical names or aliases. Optional is one of the 11 names checked.
- **DS-VC-STR-007** (Canonical Section Ordering): Checks whether optional sections are positioned after core canonical sections.
- **DS-DD-011** (Optional Content): Defines how Optional sections must be explicitly marked per DECISION-011.

## Related Diagnostic Codes

- **DS-DC-W002** (NON_CANONICAL_SECTION_NAME): Fires when a section name doesn't match any canonical name or alias.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.4 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
| 1.1.0 | 2026-02-16 | Extension Labeling Audit (Story 2.5a): Added `spec_origin` classifications to alias table. Added DocStratum Extension callout noting that alias support diverges from the reference parser's exact case-sensitive matching. Cross-referenced DS-AUDIT-extension-labeling.md. |
