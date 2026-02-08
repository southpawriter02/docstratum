# DS-DD-008: Example IDs Linked to Concepts

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-008 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Decision ID** | DECISION-008 |
| **Date Decided** | 2026-02-01 (v0.0.4d) |
| **Impact Area** | Content Enrichment (`enrichment.py` → `FewShotExample.concept_ids`; deferred to v0.3.x) |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**Few-shot examples are linked to documentation concepts via schema-based ID references defined in YAML frontmatter. The `FewShotExample.concept_ids` field in the enrichment schema establishes these links, enabling automated discovery and filtering of examples by concept.**

## Context

Documentation often includes examples to illustrate concepts (e.g., "Show me an example of authentication flow"). The challenge is connecting examples to the specific concepts they demonstrate, so that:
1. **Automated Discovery**: Tools can answer "What examples demonstrate AUTH-001?" without manual lookup
2. **Filtering**: Examples can be filtered by concept, difficulty level, and language
3. **Validation**: Systems can verify that all referenced concepts actually exist
4. **Reuse**: Examples can be indexed and reused across multiple documentation sets

Early prototyping showed that loose, human-readable connections (like embedding concept names in comments) don't scale — they can't be reliably parsed and tend to drift out of sync as documentation evolves.

This decision applies to v0.3.x enrichment layer (deferred from v0.1.x). The schema definition is finalized now to inform future content structure design.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| File-Based Organization | Simple structure; examples in a folder named `AUTH-001-examples/` immediately shows which concept they're for | Breaks when a single example applies to multiple concepts; scalability issues with cross-cutting examples; inflexible; doesn't support metadata filtering |
| Tagged in Markdown Body | Flexible; concept links live inline with example text; no separate metadata file | Fragile — easy to forget tags; parsing is unreliable; difficult to validate at scale; not machine-friendly; no structured filtering support |
| **Schema-Based Linking (Chosen)** | YAML frontmatter provides structured metadata; Pydantic schema enables validation; concept IDs are explicit and queryable; supports filtering by difficulty, language, and other dimensions; enables automated example discovery | Requires examples to have explicit YAML frontmatter; small learning curve for content authors; centralized metadata can be harder to edit in bulk |
| Separate Relationship File | All example-to-concept links in one place; easy to review all mappings at once | Requires separate synchronization logic; links can get out of sync with examples; centralized updates are error-prone; harder for example authors to understand which concepts they're teaching |

## Rationale

Schema-based linking was selected because it provides the best balance of **automation capability, validation, and author clarity**. By anchoring example metadata in YAML frontmatter (following the pattern established by many documentation systems), the schema becomes enforceable:

```yaml
---
example_id: EX-AUTH-001-001
title: Basic Bearer Token Authentication
concepts:
  - AUTH-001
  - AUTH-002
difficulty: beginner
language: python
---
# Example content starts here
```

This structure enables:
1. **Programmatic Validation**: Pydantic can verify that every concept_id references a valid concept in the registry
2. **Rich Filtering**: Tools can answer "Show beginner-level Python examples for AUTH-001" — a multi-dimensional query
3. **Centralized Metadata**: All example metadata is co-located with the example content, so changes don't require separate synchronization
4. **Clear Authorship Intent**: The example author explicitly declares which concepts the example demonstrates, preventing ambiguity

## Impact on ASoT

This decision impacts the Content Enrichment validation criteria, **deferred to v0.3.x** (not yet defined in the current ASoT). When the enrichment layer is implemented, the following criteria are anticipated:

- **DS-VC-ENR-001** *(planned — v0.3.x)* (Example Presence): Examples must include YAML frontmatter with concept links
- **DS-VC-ENR-002** *(planned — v0.3.x)* (Concept Reference Validity): All concept_ids in FewShotExample.concept_ids must reference valid concepts in the concept registry
- **DS-VC-ENR-003** *(planned — v0.3.x)* (Example Discoverability): Example indices can be generated programmatically using concept_ids, enabling automated "related examples" sections
- **DS-VC-ENR-004** *(planned — v0.3.x)* (Metadata Completeness): Examples must include difficulty and language fields for filtering

The enrichment pipeline (v0.3.x+) will use the `FewShotExample.concept_ids` array to organize and present examples contextually. Any system that needs to find examples by concept will query this field.

## Constraints Imposed

1. **Unique Example IDs**: Every example must have a globally unique `example_id`. Convention: `EX-{concept_id}-{sequence}` (e.g., `EX-AUTH-001-001`, `EX-AUTH-001-002`).
2. **Mandatory Concept References**: Each example must list at least one concept ID in `concept_ids`. Examples with zero concepts are invalid.
3. **Valid Concept IDs**: Every concept ID in `concept_ids` must exist in the active concept registry. References to non-existent concepts trigger validation errors.
4. **Frontmatter Location**: YAML frontmatter must appear at the top of the example file (lines 1–N before the first non-YAML line).
5. **Schema Compliance**: Examples must conform to the `FewShotExample` Pydantic model. Missing required fields trigger validation errors.
6. **No Dangling Examples**: All examples must be registered in the enrichment index. Orphaned example files (not indexed) emit a warning.

## Related Decisions

- **DS-DD-004** (Concept ID format — the IDs referenced in concept_ids must conform to this format)
- **DS-DD-006** (Pydantic schema for FewShotExample defined in `enrichment.py` using BaseModel)
- **DS-DD-009** (Validation pipeline includes concept_ids validation against concept registry)
- **DS-DD-012** (Canonical section names — "Examples" section structure integrates with concept linking)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
