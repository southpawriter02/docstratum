# DS-DD-004: Concept ID Format (lowercase alphanumeric + hyphens)

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-004 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-004 |
| **Date Decided** | 2026-01-20 (v0.0.4d) |
| **Impact Area** | Content Enrichment (`enrichment.py` → `Concept.id` uses `^[a-z0-9-]+$`) |
| **Provenance** | v0.0.4d §Differentiators and Decision Log |

## Decision

**Concept IDs use a domain-prefixed format (e.g., AUTH-001, DB-042, API-017) with lowercase alphanumeric characters and hyphens only. The `Concept.id` field validates against the regex pattern `^[a-z0-9-]+$`. Concept IDs are immutable once assigned.**

## Context

In a 3-layer architecture (Layer 2: Concept Map), concepts must be uniquely and reliably referenced throughout the documentation and across different layers. Concept IDs serve as stable anchors for relationships, examples, and index entries. This is a *very high reversibility cost* decision — once deployed, changing concept ID formats would break all existing references, require bulk migration, and potentially invalidate years of accumulated metadata and links.

The decision required balancing several constraints: human readability (authors should understand what AUTH-001 refers to), machine parseability (strict validation rules), semantic meaning (the ID should carry information), stability (IDs should remain valid across years and versions), and scalability (format must support hundreds or thousands of concepts across multiple domains).

## Alternatives Considered

| Option | Rationale For | Rationale Against |
|--------|---------------|-------------------|
| Numeric Only (001, 002, ..., 999) | Simple, no special characters, easy to generate sequentially | No semantic meaning, hard to reason about (what is 342?), poor discoverability, no domain grouping, all concepts in a single namespace creates conflicts |
| UUID (550e8400-e29b-41d4-a716-446655440000) | Guaranteed globally unique, collision-free, standards-based | Not human-readable, impossible to memorize, poor for documentation (author cannot guess UUID format), overkill for single-project scope |
| Semantic Full Names (AUTHENTICATION, DATABASE_CONNECTION_POOLING, API_RATE_LIMITING) | Self-documenting, no lookup needed, human-readable | Too long (breaks line width in documentation), fragile if concept gets renamed (API_RATE_LIMITING → API_THROTTLING breaks references), too many underscores, hard to type in search/navigation |
| **Domain-Based (AUTH-001, DB-042, API-017)** | **Semantic grouping (AUTH domain covers all authentication-related concepts), human-readable at a glance (AUTH-001 is "the first authentication concept"), stable across renames (rename concept without changing ID), supports ~1000 concepts per domain (three-digit suffix), easy to type and search, discoverable by pattern, natural ordering within domain.** | **Requires upfront domain planning, authors must assign domains correctly, collision risk within domain if numbering is uncoordinated, slightly more parsing logic than pure numeric.** |

## Rationale

The domain-based format (e.g., AUTH-001, DB-042, API-017) was chosen for several compelling reasons:

**1. Semantic Grouping:** The domain prefix groups related concepts. When a reader sees AUTH-001, AUTH-002, AUTH-015, they immediately understand these are authentication concepts. A flat numeric sequence (001, 002, ..., 999) provides no such signal. Domain grouping improves cognitive load and documentation navigation.

**2. Human Readability:** Short, pronounceable identifiers are far more useful in documentation than UUIDs. An author can write "see AUTH-001 for authentication details" and readers recognize the concept class without lookup. This supports both human reading and LLM navigation.

**3. Immutability with Flexibility:** Unlike semantic full names, domain-based IDs decouple the concept name from the ID. If a concept is renamed from "Database Connection Pooling" to "Connection Pool Management," the ID remains DB-042. This is critical for long-term stability and reference integrity.

**4. Scalability:** Each domain can support ~1000 concepts (001-999). For most projects, this is sufficient. If a domain exceeds 1000 concepts, new sub-domains can be created (e.g., AUTH-OAUTH-001, AUTH-SAML-001).

**5. Parsing and Validation:** The regex `^[a-z0-9-]+$` is simple to validate, fast to parse, and unambiguous. No risk of collision with other naming schemes (UUIDs, semantic names, numeric IDs).

**6. Lowercase Standard:** Lowercase-only (no uppercase) prevents case-sensitivity bugs and maintains consistency. Tooling cannot accidentally create AUTH-001 and auth-001 as distinct concepts.

## Impact on ASoT

1. **Schema Enforcement:** The `Concept.id` field in the enrichment model is defined as:
   ```python
   id: str  # regex: ^[a-z0-9-]+$, e.g., auth-001, db-042, api-017
   ```
   Validators reject any concept with an ID that doesn't match this pattern.

2. **Relationship Binding:** Typed relationships (from DS-DD-005) reference concepts by ID. The validator checks that all referenced concept IDs exist in Layer 2.

3. **Index Cross-Reference:** Layer 1 (Master Index) entries must link to Layer 2 concepts by ID. The validator ensures no orphaned index entries.

4. **Few-Shot Examples:** Layer 3 examples reference concepts by ID. Validators check that all examples reference existing concepts.

5. **Canonical Mapping:** The `ConceptMap` model maintains a `concepts_by_id` dictionary for O(1) lookup during validation and navigation.

6. **Import/Export:** Any tool that imports llms.txt must preserve concept IDs exactly. Export tools must ensure IDs are never modified or reordered.

## Constraints Imposed

1. **Immutability:** Once a concept is assigned an ID, that ID is permanent. Changing a concept ID is considered a breaking change and requires major version bump.

2. **Pattern Enforcement:** All concept IDs must match `^[a-z0-9-]+$`. No uppercase, no underscores (use hyphens instead), no special characters, no spaces.

3. **Uniqueness Within Project:** Each concept ID must be unique within a single llms.txt document. The validator checks for duplicates and rejects documents with duplicate IDs.

4. **Domain Coordination:** Authors submitting concepts must agree on domain assignments. A project-wide domain list (AUTH, DB, API, CLI, SECURITY, etc.) should be established early. Adding new domains requires coordination.

5. **Documentation Requirements:** Every concept must have an ID. Layer 2 cannot have anonymous concepts. IDs must be present in the Concept model before concepts can be used in relationships or examples.

6. **Backward Compatibility:** Existing concept IDs must never change. If a domain structure is refactored (e.g., splitting AUTH into AUTH and OAUTH), old IDs must remain valid; new concepts use new IDs.

## Related Decisions

- **DS-DD-005:** Typed Directed Relationships — Relationships reference concepts using these IDs
- **DS-DD-002:** 3-Layer Architecture — Layer 2 Concept Map uses these IDs as the primary key
- **DS-DD-004:** (this decision) — foundational to the semantic web of concepts

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.3 |
