# DS-DD-002: 3-Layer Architecture

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-002 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-002 |
| **Date Decided** | 2026-01-15 (v0.0.4d) |
| **Impact Area** | Content Structure (v0.3.x schema models in `enrichment.py`) |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**Documentation in llms.txt follows a mandatory 3-layer architecture: (Layer 1) Master Index for navigation and quick reference, (Layer 2) Concept Map for semantic relationships and learning dependencies, and (Layer 3) Few-Shot Bank for practical examples and implementation patterns. This layering is foundational to ASoT scoring and validation.**

## Context

Complex technical documentation is difficult for LLMs to consume efficiently when presented as a flat or monolithic structure. Analysis of v0.0.2 audits found that projects with 5-20 core concepts benefit most from a progressive disclosure model. A single flat document wastes context tokens on navigation when the reader seeks specific concepts. A two-layer model conflates two distinct concerns: how to *navigate* documentation (Layer 1) versus the semantic *relationships* between concepts (Layer 2).

The 3-layer architecture emerged from observing successful documentation patterns in high-performing llms.txt implementations. It separates concerns cleanly: navigation/discovery, concept semantics, and practical grounding. Each layer is independently consumable and serves a distinct LLM workflow.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| Single File (Flat) | Maximum simplicity, no coordination overhead | Wastes context tokens on navigation, poor concept discoverability, difficult for LLMs to extract semantic relationships, doesn't scale beyond 5 core concepts |
| 2-Layer (Index + Examples) | Simpler than 3-layer, still adds structure | Conflates navigation with semantics, lacks explicit concept graph, cannot express learning dependencies, weaker signal for concept importance |
| **3-Layer (chosen)** | **Layer 1 (Master Index): quick navigation and overview. Layer 2 (Concept Map): semantic relationships, learning prerequisites, concept dependencies. Layer 3 (Few-Shot Bank): practical examples and implementation patterns. Progressive disclosure, independent layer consumption, clear separation of concerns.** | **Higher implementation complexity, requires coordination between layers, more maintenance surface area.** |
| 4-Layer (Index + Graph + Examples + Appendices) | Comprehensive, maximum granularity | Over-engineering for most projects, significant maintenance burden, diminishing returns in LLM usability, hard to coordinate four independent structures |

## Rationale

The 3-layer model was chosen because it optimizes for both human and LLM comprehension without over-specifying. Here's why each layer matters:

**Layer 1 (Master Index):** LLMs need a way to *navigate* large documentation spaces. A well-structured index (table of contents, quick-reference tables, feature matrix) lets the LLM rapidly identify relevant sections. This layer answers: "Where do I find information about X?"

**Layer 2 (Concept Map):** This layer models *semantic knowledge*. Concepts are atomic units (AUTH-001: Authentication, DB-042: Connection Pooling, API-017: Rate Limiting). The concept map includes definitions, relationships (`depends_on`, `conflicts_with`, etc.), and learning prerequisites. This layer answers: "What does concept X mean, what does it depend on, and how does it relate to Y?"

**Layer 3 (Few-Shot Bank):** Practical examples ground abstract concepts. Code snippets, configuration examples, and edge-case walkthroughs provide concrete grounding. This layer answers: "How do I actually use concept X in practice?"

The 3-layer approach provides a sweet spot: richer than a flat structure, simpler than 4+ layers, and directly aligned with how LLMs perform best (navigation → semantics → grounding).

## Impact on ASoT

1. **Schema Requirements:** The v0.3.x `enrichment.py` schema models must explicitly represent all three layers:
   - `MasterIndex` model with sections and cross-references
   - `ConceptMap` model with `Concept` nodes and typed `Relationship` edges
   - `FewShotBank` model with example categories and implementations

2. **Scoring Criteria:** ASoT scoring must validate:
   - Layer 1 completeness: All major concepts have index entries
   - Layer 2 quality: Concept definitions are precise, relationships are accurate
   - Layer 3 coverage: Every concept has at least one practical example

3. **Validation Rules:** Validators check:
   - No concept appears in Layer 2 without a Layer 1 index entry (forward reference)
   - All Layer 3 examples reference defined concepts from Layer 2
   - No "orphaned" layers (e.g., examples about concepts not in the map)

4. **Navigation and Modular Consumption:** Each layer is independently extractable for MCP tool calls (e.g., "fetch the concept map," "fetch examples for AUTH concepts").

## Constraints Imposed

1. **Mandatory Structure:** Every llms.txt compliant with ASoT must include all three layers. Projects cannot opt out or merge layers.

2. **Layer Independence:** Layers must be independently consumable. A reader should be able to understand Layer 2 (Concept Map) without reading Layer 1 (Index), though Layer 1 improves discovery.

3. **Cross-Layer Consistency:** If a concept is in Layer 2, it must have an index entry in Layer 1. If an example in Layer 3 uses a concept, that concept must exist in Layer 2.

4. **Metadata Tracking:** Each layer must include metadata about coverage (e.g., "Layer 3 covers 92% of Layer 2 concepts").

## Related Decisions

- **DS-DD-015:** MCP Target for Modular Consumption — Layer 1/2/3 map directly to MCP tool calls for fetching index, concept map, and examples
- **DS-DD-001:** Markdown Format — 3-layer structure is expressed in Markdown headings and sections
- **DS-DD-004:** Concept ID Format — Layer 2 concepts use domain-based IDs (e.g., AUTH-001)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
