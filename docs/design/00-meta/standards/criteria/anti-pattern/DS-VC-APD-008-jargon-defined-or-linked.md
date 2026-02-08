# DS-VC-APD-008: Jargon Defined or Linked

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-APD-008 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L4-08 |
| **Dimension** | Anti-Pattern Detection (20%) |
| **Level** | L4 — Exemplary |
| **Weight** | 2 / 20 anti-pattern points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Partially measurable |
| **Provenance** | v0.0.4c AP-CONT-003 (Jargon Jungle); v0.0.1b Gap #7; practical: undefined jargon degrades LLM comprehension |

## Description

This criterion checks that domain-specific terms appearing in the file are accompanied by definitions, links, or references to a glossary. It is the complement to APD-002 (Concept Definitions), which checks for the **presence** of a concept-definition structure. APD-008 checks that **specific jargon terms** used throughout the file are connected to definitions.

Domain-specific terminology is inevitable in technical documentation. The issue is not the presence of jargon itself, but the absence of accessibility for readers unfamiliar with it. Undefined jargon forces consuming agents to either guess at meanings (leading to errors) or fail at tasks that depend on precise terminology.

This criterion uses heuristic pattern matching to identify potential jargon candidates and flag those that lack nearby definitions, links, or glossary entries. Jargon detection is inherently imperfect — the validator cannot know which terms are "domain-specific" without a domain model — but high-confidence signals include:

- Acronyms without expansions (e.g., "API" without "Application Programming Interface")
- Capitalized multi-word terms without definitions (e.g., "GraphQL Schema" introduced without explanation)
- Rare or specialized vocabulary flagged by the Jargon Jungle anti-pattern (AP-CONT-003)
- Terms appearing in a domain-specific glossary

## Pass Condition

Domain-specific terms are accompanied by definitions or links:

```python
# Identify potential jargon candidates (heuristic)
potential_jargon = identify_jargon_candidates(content)
# High-confidence candidates: acronyms, capitalized multi-word terms,
# uncommon words flagged as specialized vocabulary
# [CALIBRATION-NEEDED: jargon detection heuristic, "standard dictionary" baseline]

for term in potential_jargon:
    # Check for nearby definition (e.g., "X is...", "X refers to...")
    has_definition = has_nearby_definition(term, content)
    # [CALIBRATION-NEEDED: proximity threshold for "nearby"]

    # Check for link to definition (e.g., [GraphQL](url) or [[GraphQL]])
    has_link = has_link_to_definition(term, content)

    # Check for term in a dedicated Glossary or Concepts section
    has_concepts_section = term_in_concepts_section(term, content)

    # At least one of the three must be true
    assert has_definition or has_link or has_concepts_section

# If no jargon candidates were detected, also pass
# (the file may not use specialized terminology)
```

**Note:** Jargon detection is inherently heuristic. The validator may produce false positives (flagging well-known terms) and false negatives (missing obscure jargon). The implementation should err on the side of caution to avoid over-flagging. [CALIBRATION-NEEDED: refinement of detection sensitivity].

## Fail Condition

Domain-specific terms appear without any nearby definition, link, or glossary entry:

- Terms like "GraphQL", "REST", "webhook", or other domain-specific concepts are used without explanation
- Acronyms appear without expansion (e.g., "CRUD" used without first explaining "Create, Read, Update, Delete")
- Specialized vocabulary is introduced casually without any reference or definition
- The file shows evidence of the Jargon Jungle anti-pattern (AP-CONT-003): heavy use of unexplained terminology

**Gate behavior:** This is a SOFT criterion at L4. Failure reduces the Anti-Pattern Detection score but does not block progression.

## Emitted Diagnostics

- **DS-DC-I007** (INFO): Emitted when domain-specific jargon without definition is detected. Lists specific terms that lack definitions and suggests adding definitions or links to expand their meaning.

## Related Anti-Patterns

- **DS-AP-CONT-003** (Jargon Jungle): Heavy use of domain-specific jargon without definitions. APD-008 directly counters this anti-pattern by ensuring that specific jargon terms are connected to definitions.

## Related Criteria

- **DS-VC-APD-002** (Concept Definitions): Complementary check. APD-002 verifies the **presence** of a concept-definition structure (e.g., a "Glossary" or "Core Concepts" section). APD-008 verifies that **specific jargon terms** used in the file are connected to definitions. Together, they ensure comprehensive coverage: APD-002 checks for the infrastructure, APD-008 checks for connectivity.

## Calibration Notes

Jargon detection is inherently heuristic and context-dependent. The validator cannot know which terms are "domain-specific" without a domain model. The v0.0.4c anti-pattern catalog identifies several high-confidence detection signals:

- **Acronyms**: Expansion should appear near the first use (e.g., "REST (Representational State Transfer)")
- **Capitalized multi-word terms**: May indicate domain-specific concepts (e.g., "GraphQL Schema", "OAuth Token")
- **Rare or uncommon vocabulary**: Compared against a dictionary baseline or frequency analysis

The v0.0.2c audit found:

- **Files with explicit Glossary or Concepts sections (25%)**: Nearly always pass APD-008 (connectivity to definitions is explicit)
- **Files with inline definitions (33%)**: Mostly pass, but may have scattered unexplained jargon
- **Files with undefined jargon (42%)**: Exhibit the Jargon Jungle anti-pattern and fail APD-008

Top-scoring specimens (Svelte, Pydantic) show consistent patterns: jargon is either defined inline, placed in a Glossary, or hyperlinked to external resources. This criterion rewards that discipline.

**Implementation note for future versions:** Future versions may incorporate LLM-assisted evaluation to improve jargon detection accuracy. An LLM can assess whether a term requires definition based on context and audience understanding, reducing false negatives and false positives compared to pattern-matching approaches.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C exemplary criterion |
