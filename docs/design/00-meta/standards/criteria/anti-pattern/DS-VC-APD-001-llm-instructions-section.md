# DS-VC-APD-001: LLM Instructions Section

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-APD-001 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L4-01 |
| **Dimension** | Anti-Pattern Detection (20%) |
| **Level** | L4 — Exemplary |
| **Weight** | 3 / 20 anti-pattern points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.0 Stripe LLM Instructions Pattern; v0.0.4d DECISION-002 (3-Layer Architecture); Stripe's implementation demonstrated measurable improvement in agent task completion |

## Description

This criterion checks that the llms.txt file contains an explicit section addressing AI agents directly. The section tells agents how to use the documentation, what to prioritize, and what to avoid. This is a DocStratum innovation — the criterion recognizes that AI-consumable documentation has a unique audience with distinct needs, and explicit LLM-facing guidance measurably improves agent task completion.

The LLM Instructions section serves as a contract between the documentation author and the consuming agent. It may establish priorities (e.g., "Use the API Reference for authoritative details"), clarify scope (e.g., "This is a conceptual overview, not a complete reference"), define agent responsibilities (e.g., "Always check for deprecation notices"), or prohibit certain behaviors (e.g., "Do not infer undocumented APIs").

The v0.0.0 Stripe pattern (referenced in v0.0.4d DECISION-002 Layer 1) demonstrated that explicit LLM instructions correlate with measurably higher agent task completion rates. Most current llms.txt implementations lack this section entirely. Only the most advanced implementations — and DocStratum's own gold standard specimens — include structured LLM-facing content.

The measurability of this criterion is straightforward: it checks only for the **presence** of a recognizable section name (e.g., "LLM Instructions", "Instructions for Agents", "Agent Guidelines"). The section's **content** quality is evaluated by other criteria (APD-001 through APD-008 and the content dimension).

## Pass Condition

The file contains a section recognizable as LLM instructions:

```python
llm_instruction_names = {
    'llm instructions', 'instructions', 'agent instructions',
    'for ai agents', 'ai guidelines', 'guidelines for agents'
}
h2_sections = parse_h2_headings(content)
has_llm_section = any(
    s.name.lower() in llm_instruction_names
    for s in h2_sections
)
assert has_llm_section
```

The section should contain directive content (imperative sentences, "do/don't" patterns), but the primary check is **name-based**. If the section is named appropriately, it passes. The presence of valid directive content within the section is encouraged but not required for this criterion (though it is evaluated by broader content-quality criteria).

## Fail Condition

The file contains **no** section with an LLM-instructions-like name. Failure conditions include:

- No H2 heading matches any variant of "LLM Instructions", "Instructions", "Agent Guidelines", etc.
- File has an "Instructions" section that addresses end users rather than AI agents (e.g., "Instructions for Installing"), which should not match
- The file addresses AI agents only in passing (e.g., a single sentence in a "Purpose" section) without a dedicated section

**Gate behavior:** This is a SOFT criterion at L4. Failure reduces the Anti-Pattern Detection score but does not block progression. The diagnostic is informational.

## Emitted Diagnostics

- **DS-DC-I001** (INFO): Emitted when no LLM Instructions section is found. Suggests adding a section to guide consuming agents.

## Related Anti-Patterns

- **DS-AP-CONT-008** (Silent Agent): File provides no LLM-facing guidance despite being an AI documentation file. APD-001 directly counters this anti-pattern.

## Related Criteria

- **DS-VC-CON-008** (Canonical Section Names): "LLM Instructions" is one of the 11 canonical section names defined in the content dimension. APD-001 verifies its presence; CON-008 verifies naming compliance across all sections.
- **DS-VC-APD-002** (Concept Definitions): LLM instructions often reference key concepts that should be defined elsewhere in the file.

## Calibration Notes

The v0.0.0 Stripe pattern demonstrated that explicit LLM instructions measurably improve agent task completion. This is a DocStratum innovation — no other documentation validator checks specifically for LLM-facing content.

In the v0.0.2c audit of 24 specimens:
- **12 files (50%)** entirely lacked any LLM-facing section
- **8 files (33%)** had implicit agent guidance (scattered throughout without a dedicated section)
- **4 files (17%)** had explicit LLM Instructions sections
- All files with explicit LLM Instructions sections scored higher on agent task completion tests (average improvement: 15–23%)

Top-scoring specimens (Svelte, Pydantic) both include explicit instructions for AI agents. This criterion rewards that best practice.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C exemplary criterion |
