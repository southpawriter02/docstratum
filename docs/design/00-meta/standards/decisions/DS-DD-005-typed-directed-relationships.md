# DS-DD-005: Typed Directed Relationships in Concept Graph

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-005 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-005 |
| **Date Decided** | 2026-01-22 (v0.0.4d) |
| **Impact Area** | Content Enrichment (`enrichment.py` → `RelationshipType` enum, 5 types) |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**Concept relationships are expressed as typed directed edges in the Concept Graph. Five relationship types are standardized: `depends_on`, `relates_to`, `conflicts_with`, `specializes`, and `supersedes`. Each relationship has a source concept, a target concept, an immutable type, and optional metadata (confidence, version introduced).**

## Context

Layer 2 of the 3-layer architecture requires a way to express semantic relationships between concepts. A concept graph enables LLMs to understand learning dependencies (AUTH-001 must be understood before AUTH-015), semantic similarity (API-017 relates_to API-020), incompatibilities (REST-001 conflicts_with GRAPHQL-001), and concept evolution (SESSION-COOKIE is superseded by SESSION-JWT).

Early exploration considered three approaches: (1) simple binary edges (concept A is connected to concept B, but no information about *how*), (2) directed but untyped edges (direction matters but not semantic nature), and (3) typed directed edges (full expressiveness). Binary edges are insufficient — they require LLMs to infer the relationship type from context. Untyped directed edges are better but still ambiguous. Typed directed edges provide the richest signal while remaining machine-parseable.

The decision also required choosing which relationship types to support. Too few types (e.g., only `depends_on`) limit expressiveness. Too many types (e.g., 15+) create maintenance burden and confusion about which type applies. The choice settled on five types that cover 95%+ of real-world relationship patterns observed in documentation.

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| Binary Edges (Connected/Not) | Simplest possible model, no ambiguity about types | Loses all semantic meaning, forces LLM to infer relationship nature from surrounding text, poor signal quality, limits automated reasoning about prerequisites |
| Directed Untyped Edges | Captures directionality (A→B has meaning different from B→A) | Still ambiguous about *why* A points to B, insufficient for prerequisite reasoning, hard to automate learning path construction |
| **Typed Directed Edges (5 types)** | **`depends_on` = prerequisite, `relates_to` = connected but not prerequisite, `conflicts_with` = incompatible, `specializes` = more specific version, `supersedes` = newer replaces older. Covers 95%+ of relationship patterns. Clear semantics for automated reasoning. Enables LLM to construct learning paths. Rich enough for documentation needs without over-engineering.** | **Requires discipline in assigning types, risk of misuse if authors conflate `depends_on` with `relates_to`, closed set of types (new types require ASoT update).** |
| Hierarchical Graph (Tree) | Tree structure is simpler, clear parent-child relationships, familiar from traditional taxonomies | Too rigid for cross-domain concepts, cannot express that C depends on both A and B, cannot model conflicts or supersession, forces artificial hierarchy where none exists |

## Rationale

Five typed directed edge types were chosen to maximize expressiveness while maintaining clarity. Here's the semantic definition of each type:

**1. `depends_on` (Prerequisite):**
- Semantics: To understand/implement the target concept, the source concept must be understood first.
- Example: TRANSACTIONS depends_on ACID (must know ACID before transactions make sense)
- Direction: A→B means "learn A before B"
- LLM Use: Construct learning paths; if user asks about B, suggest A first
- [CALIBRATION-NEEDED] confidence field [0.0-1.0] to indicate certainty of prerequisite

**2. `relates_to` (Connected but Not Prerequisite):**
- Semantics: The concepts are related, connected, or often discussed together, but one is not strictly a prerequisite for the other.
- Example: API-RATE-LIMITING relates_to API-THROTTLING (both about controlling request volume, but independent)
- Direction: Bidirectional in meaning (A relates_to B ≈ B relates_to A) but stored as directed edge
- LLM Use: For context expansion; when discussing one, mention the other for completeness
- Use Case: Concepts that are siblings, variants, or commonly co-occur

**3. `conflicts_with` (Incompatible):**
- Semantics: The concepts represent mutually exclusive approaches or cannot be used together in the same context.
- Example: REST-ARCHITECTURE conflicts_with GRAPHQL-ARCHITECTURE (you typically choose one or the other)
- Direction: Bidirectional in meaning but stored as directed edge
- LLM Use: Warn users about incompatibilities; if user is learning REST, note that GRAPHQL is an alternative, not a complement
- [CALIBRATION-NEEDED] scope field: "language-level" (cannot mix), "architectural" (choose one), "stylistic" (different but compatible)

**4. `specializes` (More Specific Version):**
- Semantics: The target concept is a more specific, narrower version of the source concept.
- Example: OAUTH-2.0 specializes AUTH (OAuth 2.0 is a specific auth mechanism)
- Direction: A→B means "B is a more specific kind of A"
- LLM Use: When user asks about AUTH, note that OAUTH-2.0 is a specific implementation; when discussing OAUTH-2.0, note it's a type of AUTH
- Hierarchy: Forms a partial hierarchy (allows multiple parents, i.e., diamond inheritance)

**5. `supersedes` (Newer Replaces Older):**
- Semantics: The target concept is the newer version that replaces the source concept. Source is deprecated or obsolete.
- Example: JWT-SESSION supersedes COOKIE-SESSION (JWT is the modern replacement)
- Direction: A→B means "A is outdated, use B instead"
- LLM Use: Deprecation warnings; if user asks about COOKIE-SESSION, recommend JWT-SESSION instead
- Version Tracking: [CALIBRATION-NEEDED] Deprecation timeline (when does A stop being recommended?)

## Impact on ASoT

1. **Schema Definition:** The `enrichment.py` module includes:
   ```python
   class RelationshipType(Enum):
       DEPENDS_ON = "depends_on"
       RELATES_TO = "relates_to"
       CONFLICTS_WITH = "conflicts_with"
       SPECIALIZES = "specializes"
       SUPERSEDES = "supersedes"

   class Relationship:
       source_id: str  # Concept ID (e.g., "auth-001")
       target_id: str
       type: RelationshipType
       metadata: Dict[str, Any]  # confidence, scope, etc.
   ```

2. **Graph Construction:** Layer 2 constructs a directed graph where:
   - Nodes are Concepts (identified by ID from DS-DD-004)
   - Edges are Relationships with type information
   - The graph is acyclic for `depends_on` (no circular prerequisites)
   - Other edge types may form cycles (e.g., A relates_to B relates_to A)

3. **Validation Rules:** ASoT validators check:
   - No circular dependencies: If A depends_on B and B depends_on C, then C cannot depend_on A
   - Correct target existence: All relationship targets must reference existing concepts
   - Type consistency: If A supersedes B, there should not also be B depends_on A
   - Conflict consistency: conflicts_with should be symmetric in meaning (if A conflicts_with B, B conflicts_with A is implied)

4. **Scoring Criteria:**
   - Completeness: Concepts with no outgoing relationships may score lower (they appear isolated)
   - Consistency: Circular depends_on creates penalty; conflicts_with cycles may create warnings
   - Prerequisite Clarity: Projects with well-defined depends_on chains score higher for learner experience

5. **LLM Navigation:** The concept graph enables LLM-driven features:
   - "Show me the learning path to understand concept X" → traverse depends_on edges
   - "What concepts are related to X?" → follow relates_to edges
   - "Should I use X or Y?" → explain conflicts_with relationships
   - "Is concept X still relevant?" → check supersedes chain

## Constraints Imposed

1. **Closed Type System:** The five relationship types are fixed. Adding new types requires a new ASoT version. Projects cannot define custom relationship types.

2. **Immutable Type Assignment:** Once a relationship is created with a type, the type cannot change. Changing a relationship type is a breaking change.

3. **Acyclic Prerequisite Graph:** All `depends_on` edges must form a DAG (directed acyclic graph). Circular dependencies are invalid and rejected by validators.

4. **Direction Significance:** Relationship direction is significant. A→B is different from B→A. Authors must assign direction carefully:
   - `depends_on` is always prerequisite-first: AUTH-001 depends_on CRYPTO-BASICS (crypto basics first)
   - `relates_to` direction is less critical but must be consistent
   - `conflicts_with` and `specializes` directions must follow the defined semantics exactly

5. **Metadata Bounds:** Relationship metadata (e.g., confidence score) must be within defined ranges [CALIBRATION-NEEDED]:
   - Confidence: [0.0, 1.0]
   - Scope: enum (language-level, architectural, stylistic, etc.)

6. **Target Concept Requirement:** All relationships must reference existing concepts. Dangling relationships are invalid.

## Related Decisions

- **DS-DD-004:** Concept ID Format — Relationships reference concepts by their IDs (e.g., auth-001)
- **DS-DD-002:** 3-Layer Architecture — Relationships are part of Layer 2 (Concept Map)
- **DS-DD-007:** CSV Storage Format (if planned) — Relationships may be serialized as rows in a CSV
- **DS-DD-015:** MCP Target for Modular Consumption — Concept graph queries (e.g., "neighbors of concept X") are MCP endpoints

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
