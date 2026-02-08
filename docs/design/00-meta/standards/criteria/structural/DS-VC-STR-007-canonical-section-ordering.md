# DS-VC-STR-007: Canonical Section Ordering

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-007 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L3-06 |
| **Dimension** | Structural (30%) |
| **Level** | L3 — Best Practices |
| **Weight** | 3 / 30 structural points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4a CHECK-STR-008; v0.0.2c: consistent ordering correlates with higher structural scores |

## Description

This criterion verifies that canonical llms.txt sections, when present, follow a recommended ordinal sequence. The llms.txt specification defines a set of standard section names (Master Index, LLM Instructions, Getting Started, Core Concepts, API Reference, Examples, Configuration, Advanced Topics, Troubleshooting, FAQ, Optional). While files need not include all canonical sections, those that do should follow a logical, consistent order to facilitate navigation and consumption.

Canonical section ordering serves multiple purposes: it aids human readability by establishing a familiar document structure, it enables AI agents to locate key sections through position-based heuristics, and it signals document professionalism and care. In the v0.0.2 audit, files that followed canonical ordering consistently scored higher (typically 5–15 points more) in the structural dimension than files with shuffled sections. However, ordering is not a hard requirement; documents that deviate may still be valid if the content is well-organized.

This is a SOFT, L3 (Best Practices) criterion. Files that violate canonical ordering still pass L1 and L2 but receive reduced L3 points.

## Pass Condition

Canonical sections that appear in the file follow the prescribed ordinal sequence:

```python
CANONICAL_SECTION_ORDER = [
    "Master Index", "LLM Instructions", "Getting Started",
    "Core Concepts", "API Reference", "Examples", "Configuration",
    "Advanced Topics", "Troubleshooting", "FAQ", "Optional"
]

file_sections = extract_section_names(file_content)
canonical_sections_in_file = [s for s in file_sections if s in CANONICAL_SECTION_ORDER]
section_indices = [CANONICAL_SECTION_ORDER.index(s) for s in canonical_sections_in_file]

# Check that indices are monotonically increasing
assert section_indices == sorted(section_indices), "Sections must follow canonical order"
```

Non-canonical section names are ignored for ordering purposes. A file with only 3 canonical sections ("Getting Started", "API Reference", "Examples") in that order passes; one with the same sections out of order ("Examples", "Getting Started", "API Reference") fails.

## Fail Condition

Two or more canonical sections appear in an order that contradicts the canonical sequence:

- "Advanced Topics" appears before "Getting Started"
- "Examples" precedes "Core Concepts"
- "Troubleshooting" before "API Reference"
- Non-canonical sections interspersed between canonical sections do not trigger failure; only the relative order of canonical sections matters

Common causes:
- Documents written incrementally, with later sections added without re-organizing earlier ones
- Copy-pasted content from multiple sources with different structural conventions
- Auto-generated documentation that assembles sections in source-file order rather than logical order

## Emitted Diagnostics

- **DS-DC-W008** (WARNING): Emitted when canonical sections do not follow the prescribed ordering

## Related Anti-Patterns

- **DS-AP-STRUCT-004** (Section Shuffle): Sections in illogical order, leading to poor navigation and reduced usability.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): Sections must use canonical names to be evaluated for ordering. STR-007 checks ordinal sequence; CON-008 checks naming.
- **DS-VC-STR-004** (H2 Section Structure): Ordering applies to H2-level sections, which are established by STR-004.
- **DS-VC-CON-007** (Mandatory Sections): Checks that required sections (e.g., Master Index, LLM Instructions) are present; ordering is a secondary concern.

## Calibration Notes

- **Top-scoring specimens follow canonical ordering:**
  - Svelte (92 pts): Sections in canonical order (Master Index → LLM Instructions → Getting Started → ...)
  - Pydantic (90 pts): Canonical order (LLM Instructions → Core Concepts → API Reference → ...)
  - Cursor (87 pts): Canonical order with minor deviations in optional sections
- **Lower-scoring specimens often violate ordering:**
  - NVIDIA llms.txt (24 pts): Sections shuffled (Examples before API Reference)
- **Correlation:** Files with canonical ordering score 5–15 points higher on structural dimension than those with shuffled sections
- W008 is emitted for ordering violations but does not block L1 or L2 progression; only L3 (Best Practices) classification is affected

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
