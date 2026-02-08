# DS-DC-I002: NO_CONCEPT_DEFINITIONS

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-I002 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | I002 |
| Severity | INFO |
| Validation Level | L4 — DocStratum Extended |
| Check ID | CNT-013 (v0.0.4b) |
| Provenance | v0.0.4b content checks; v0.0.0 Stripe pattern; 3-Layer Architecture (DECISION-002) |

## Message

> No structured concept definitions found.

## Remediation

> Add concept definitions with IDs, relationships, and aliases.

## Description

This informational code indicates that the document lacks structured concept definitions—that is, formal entries defining key domain concepts with associated metadata such as IDs, relationships, and aliases. Concept definitions are part of the Annotation & Provenance Domain (APD) layer and serve as a reference foundation for jargon clarity and semantic consistency.

When structured concept definitions are absent, readers and AI agents may struggle to understand domain-specific terminology consistently. This becomes especially problematic in technical documentation where precise definitions prevent misinterpretation. Concept definitions enable downstream features like jargon linking (DS-DC-I007) and improve overall document coherence.

**When This Code Fires:**
- The document has no formal `Concepts` section or equivalent structure with IDed, related concepts.
- No aliases or cross-references for key domain terms are present.

**When This Code Does NOT Fire:**
- The document includes a structured `Concepts` section with at least concept ID, description, and relationship fields.
- Concept definitions are linked in an external, related document that is explicitly referenced.

## Triggering Criterion

**DS-VC-APD-002** (Concept Definitions): The document must include structured concept definitions.

## Related Anti-Patterns

**DS-AP-CONT-003** (Jargon Jungle): Lack of structured concept definitions is a root cause of the Jargon Jungle anti-pattern, where domain jargon proliferates without clear, unified definitions.

## Related Diagnostic Codes

- **DS-DC-I007** (JARGON_WITHOUT_DEFINITION): Jargon without definitions; concept definitions would resolve this issue.
- **DS-DC-I001** (NO_LLM_INSTRUCTIONS): Sibling L4 feature code; both address missing structural metadata.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
