# DS-DC-I003: NO_FEW_SHOT_EXAMPLES

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DC-I003 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Code** | I003 |
| **Severity** | INFO |
| **Validation Level** | L4 — DocStratum Extended |
| **Check ID** | v0.0.1b Gap #2 (P0) |
| **Provenance** | v0.0.1b Gap Analysis (P0 priority); few-shot prompting research |

## Message

> No few-shot Q&A examples found.

## Remediation

> Add intent-tagged Q&A pairs linked to concepts.

## Description

This informational code indicates that the document lacks few-shot exemplars—question-and-answer pairs that demonstrate expected behavior, usage patterns, or problem-solving approaches. Few-shot examples are a high-value component of the Annotation & Provenance Domain (APD) that enable both human readers and AI agents to understand domain-specific reasoning by example.

Few-shot examples significantly improve LLM agent performance by providing concrete instantiations of abstract concepts. Rather than relying solely on textual description, examples show practitioners and AI agents *how* to apply concepts in realistic scenarios. The absence of few-shot examples reduces learnability and increases the risk of misinterpretation or inconsistent application.

**When This Code Fires:**
- The document has no dedicated few-shot section or example Q&A pairs.
- No intent-tagged examples linked to concepts or use cases are present.

**When This Code Does NOT Fire:**
- The document includes a structured few-shot section with intent-tagged Q&A pairs.
- Examples are embedded throughout the document and clearly linked to concepts.

## Triggering Criteria

- **DS-VC-APD-003**: (Few-shot Examples)

Emitted by DS-VC-APD-003 when no few-shot Q&A examples are found in the file.
## Related Anti-Patterns

None directly identified.

## Related Diagnostic Codes

- **DS-DC-I001** (NO_LLM_INSTRUCTIONS): Sibling L4 feature code; both address missing structural metadata.
- **DS-DC-I002** (NO_CONCEPT_DEFINITIONS): Concept definitions complement and contextualize few-shot examples.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase B |
| 0.0.0-scaffold | 2026-02-08 | Phase C backfill — added VC cross-references to Triggering Criteria section |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
