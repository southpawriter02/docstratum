# DS-VC-APD-002: Concept Definitions

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-APD-002 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L4-02 |
| **Dimension** | Anti-Pattern Detection (20%) |
| **Level** | L4 — Exemplary |
| **Weight** | 3 / 20 anti-pattern points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Heuristic |
| **Provenance** | v0.0.1b Gap #7; v0.0.4d DECISION-002 Layer 2 (Concept Map); v0.0.4c AP-CONT-003 (Jargon Jungle) |

## Description

This criterion checks that the file defines key concepts, terms, and domain-specific vocabulary. Concept definitions are the second layer of semantic enrichment in the v0.0.4d 3-Layer Architecture (DECISION-002). They provide foundational knowledge that allows consuming agents to understand and reason about the project correctly.

Without concept definitions, files frequently devolve into jargon jungles — they use domain-specific terminology without explanation, forcing consuming agents to either guess at meanings or fail at tasks that depend on precise terminology. This criterion rewards files that explicitly define their key terms.

A concept definition section can take multiple forms:
- A "Core Concepts" or "Concepts" section with definition paragraphs
- A "Glossary" with term-definition pairs
- Inline definitions ("X is...", "X refers to...")
- A "Fundamentals" section explaining key ideas
- A "Key Terms" section with structured definitions

The measurability is heuristic — the validator searches for recognizable definition patterns rather than performing deep semantic analysis. Heuristic detection may produce false negatives (missing subtle definitions) or false positives (flagging non-definitions), but it serves as an effective proxy for the presence of concept-definition content.

## Pass Condition

The file contains at least one recognizable concept definition pattern:

```python
DEFINITION_PATTERNS = [
    r'\b\w+\s+is\s+(?:a|an|the)\b',        # "X is a/an/the..."
    r'\b\w+\s+refers?\s+to\b',              # "X refers to..."
    r'(?i)## (?:concepts?|glossary|terms|definitions)',  # Dedicated section header
    r'(?i)\*\*\w+\*\*\s*[-:–]\s*',          # **Term** - definition format
]
has_definitions = any(
    re.search(p, content)
    for p in DEFINITION_PATTERNS
)

# Also check for a dedicated Core Concepts section with content
h2_sections = parse_h2_headings(content)
has_concepts_section = any(
    s.name.lower() in {
        'core concepts', 'concepts', 'key concepts',
        'fundamentals', 'glossary', 'terms', 'definitions'
    }
    and len(s.children) > 0  # Section has substantive content
    for s in h2_sections
)

assert has_definitions or has_concepts_section
```

**Note:** Detection of definition patterns is heuristic. The validator may not catch all definition types. [CALIBRATION-NEEDED: refinement of pattern list and detection sensitivity].

## Fail Condition

The file contains **no** recognizable concept definitions:

- No section with names like "Core Concepts", "Glossary", "Key Terms", etc.
- No inline definition patterns detected ("X is...", "X refers to...")
- File uses domain-specific terminology throughout without any explanatory text
- All sections are lists, commands, or procedural instructions with no definitional content

**Gate behavior:** This is a SOFT criterion at L4. Failure reduces the Anti-Pattern Detection score but does not block progression.

## Emitted Diagnostics

- **DS-DC-I002** (INFO): Emitted when no structured concept definitions are found. Suggests adding a "Core Concepts" or "Glossary" section.

## Related Anti-Patterns

- **DS-AP-CONT-003** (Jargon Jungle): Heavy use of domain-specific jargon without definitions. APD-002 directly counters this anti-pattern.

## Related Criteria

- **DS-VC-APD-008** (Jargon Defined or Linked): Complementary check. APD-002 verifies the **presence** of a concept-definition structure. APD-008 verifies that **specific jargon terms** used in the file are connected to definitions. Together, they ensure that domain terminology is both defined and linked to actual content.
- **DS-VC-APD-001** (LLM Instructions Section): Instructions often reference concepts that should be defined elsewhere for clarity.

## Calibration Notes

Concept definitions are rare in current llms.txt implementations. The v0.0.1b Gap #7 identified missing concept definitions as a critical semantic gap. The v0.0.4d 3-Layer Architecture (DECISION-002) places concept mapping as Layer 2 of semantic enrichment — higher priority than examples but foundational to their utility.

In the v0.0.2c audit:
- **14 files (58%)** contained no recognizable concept definitions
- **6 files (25%)** had implicit definitions scattered throughout
- **4 files (17%)** had explicit "Concepts", "Glossary", or "Core Concepts" sections
- Files with explicit concept definitions consistently scored higher in LLM task completion evaluations (average improvement: 12–18%)

Top-scoring specimens (Svelte 92, Pydantic 90) both include explicit "Concepts" or "Fundamentals" sections. This is a forward-looking criterion that rewards emerging best practices in AI-consumable documentation.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C exemplary criterion |
