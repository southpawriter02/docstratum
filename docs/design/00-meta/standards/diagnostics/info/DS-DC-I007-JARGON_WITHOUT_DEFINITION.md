# DS-DC-I007: JARGON_WITHOUT_DEFINITION

| Field | Value |
|-------|-------|
| DS Identifier | DS-DC-I007 |
| Status | DRAFT |
| ASoT Version | 0.0.0-scaffold |
| Code | I007 |
| Severity | INFO |
| Validation Level | L4 — DocStratum Extended |
| Check ID | CNT-014 (v0.0.4b) |
| Provenance | v0.0.4b content checks; LLM comprehension research |

## Message

> Domain-specific jargon used without inline definition.

## Remediation

> Define jargon inline or link to a concept definition.

## Description

This informational code indicates that the document uses domain-specific jargon or technical terminology without providing inline definitions or explicit links to concept definitions. While domain experts may intuitively understand specialized terms, new practitioners and AI agents require clear, accessible definitions to comprehend the material accurately.

Undefined jargon creates comprehension barriers and undermines document clarity. The solution is straightforward: either provide inline definitions (e.g., "Type 2 Full (comprehensive single-file documents exceeding 250 KB)") or link to structured concept definitions in the Annotation & Provenance Domain. Either approach ensures that unfamiliar terms are immediately clarified, improving readability and reducing cognitive load.

**When This Code Fires:**
- Domain-specific terms appear without inline explanation.
- No link to a concept definition is provided for the term.
- Readers encountering the term for the first time would struggle to understand it.

**When This Code Does NOT Fire:**
- Jargon is defined inline within the sentence or paragraph where it appears.
- Terms are linked to explicit concept definitions (e.g., via cross-reference or glossary).

## Triggering Criterion

**DS-VC-APD-008** (Jargon Defined or Linked): Domain jargon must be defined inline or linked to concept definitions.

## Related Anti-Patterns

**DS-AP-CONT-003** (Jargon Jungle): Excessive undefined jargon is the core anti-pattern; this diagnostic identifies individual instances.

## Related Diagnostic Codes

- **DS-DC-I002** (NO_CONCEPT_DEFINITIONS): Structured concept definitions would resolve jargon definition issues.

## Change History

| Version | Date | Notes |
|---------|------|-------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
