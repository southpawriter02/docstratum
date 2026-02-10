"""Extended schema models for DocStratum semantic enrichment.

These models represent the DocStratum-specific enrichment layer —
concepts, few-shot examples, LLM instructions, and metadata that
DocStratum adds ON TOP of a parsed llms.txt file. They correspond
to the three P0 specification gaps identified in v0.0.1b:

    Gap #1: Concept/terminology definitions  →  Concept model
    Gap #2: Few-shot Q&A pairs              →  FewShotExample model
    Gap #3: Validation schema (meta)        →  Metadata model

And the enrichment layers from DECISION-002 (3-Layer Architecture):
    Layer 1: Master Index     →  (represented by ParsedLlmsTxt)
    Layer 2: Concept Map      →  Concept, ConceptRelationship
    Layer 3: Few-Shot Bank    →  FewShotExample, LLMInstruction

These models are used at L4 (DocStratum Extended) validation level.
A file that INCLUDES these enrichments scores higher; their ABSENCE
triggers I001-I003 informational diagnostics but does NOT fail validation.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class RelationshipType(StrEnum):
    """Typed directed relationships in the Concept Graph (DECISION-005).

    Five relationship types enable semantic navigation between concepts.
    Derived from: v0.0.4d §5.2 (Concept Relationship Graph innovation).

    Attributes:
        DEPENDS_ON: Concept A requires understanding of Concept B.
        RELATES_TO: Concepts are topically related (bidirectional).
        CONFLICTS_WITH: Concepts are mutually exclusive or contradictory.
        SPECIALIZES: Concept A is a more specific version of Concept B.
        SUPERSEDES: Concept A replaces Concept B (e.g., new API version).
    """

    DEPENDS_ON = "depends_on"
    RELATES_TO = "relates_to"
    CONFLICTS_WITH = "conflicts_with"
    SPECIALIZES = "specializes"
    SUPERSEDES = "supersedes"


class ConceptRelationship(BaseModel):
    """A typed, directed edge in the Concept Graph.

    Attributes:
        target_id: The concept ID this relationship points to.
        relationship_type: The type of relationship.
        description: Optional human-readable description of the relationship.
    """

    target_id: str = Field(
        pattern=r"^[a-z0-9-]+$",
        description="Target concept ID (DECISION-004 format).",
    )
    relationship_type: RelationshipType = Field(
        description="Type of directed relationship.",
    )
    description: str | None = Field(
        default=None,
        max_length=200,
        description="Optional description of why this relationship exists.",
    )


class Concept(BaseModel):
    """A semantic concept definition for the Concept Map (Layer 2).

    Fills P0 Gap #1 (concept/terminology definitions, v0.0.1b).
    Enables concept-aware assistance — the key differentiator for
    LLM output quality (v0.0.4d §5.2).

    Attributes:
        id: Unique identifier (DECISION-004: lowercase alphanumeric + hyphens).
        name: Human-readable concept name.
        definition: One-sentence definition. No ambiguous pronouns.
        aliases: Alternative names or abbreviations for this concept.
        relationships: Typed edges to other concepts (DECISION-005).
        related_page_urls: URLs of documentation pages discussing this concept.
        anti_patterns: Common misconceptions or misuses to avoid.
        domain: The domain prefix for namespacing (e.g., 'auth', 'api', 'data').

    Example:
        concept = Concept(
            id="payment-intent",
            name="PaymentIntent",
            definition="A PaymentIntent tracks the lifecycle of a payment from creation to completion.",
            aliases=["PI", "payment_intent"],
            relationships=[
                ConceptRelationship(
                    target_id="charge",
                    relationship_type=RelationshipType.SUPERSEDES,
                    description="PaymentIntent is the modern replacement for Charge."
                ),
            ],
            domain="payments",
        )
    """

    id: str = Field(
        pattern=r"^[a-z0-9-]+$",
        description="Unique concept ID (DECISION-004 format).",
    )
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Human-readable concept name.",
    )
    definition: str = Field(
        min_length=10,
        max_length=500,
        description="One-sentence definition. Avoid ambiguous pronouns.",
    )
    aliases: list[str] = Field(
        default_factory=list,
        description="Alternative names, abbreviations, or common misspellings.",
    )
    relationships: list[ConceptRelationship] = Field(
        default_factory=list,
        description="Typed directed relationships to other concepts.",
    )
    related_page_urls: list[str] = Field(
        default_factory=list,
        description="URLs of pages that discuss this concept.",
    )
    anti_patterns: list[str] = Field(
        default_factory=list,
        description="Common misconceptions or misuses.",
    )
    domain: str | None = Field(
        default=None,
        pattern=r"^[a-z0-9-]+$",
        description="Domain prefix for namespacing (e.g., 'auth', 'payments').",
    )


class FewShotExample(BaseModel):
    """A question-answer pair for in-context learning (Layer 3).

    Fills P0 Gap #2 (few-shot Q&A pairs, v0.0.1b).
    Enables example-driven output quality — the basis for
    Test Scenario 3 (Few-Shot Adherence Test, v0.0.5d).

    Attributes:
        id: Unique example identifier.
        intent: The user's underlying goal (tagged for retrieval).
        question: A realistic user question.
        ideal_answer: The expected response.
        concept_ids: Concept IDs this example relates to (schema-based linking, DECISION-008).
        difficulty: Difficulty level for filtering (beginner, intermediate, advanced).
        language: Programming language if applicable (for language-filtered retrieval).
        source_urls: URLs used to construct the answer (provenance).
    """

    id: str = Field(
        pattern=r"^[a-z0-9-]+$",
        description="Unique example identifier.",
    )
    intent: str = Field(
        min_length=5,
        max_length=200,
        description="User's underlying goal (e.g., 'authenticate a web app').",
    )
    question: str = Field(
        min_length=10,
        max_length=500,
        description="A realistic user question.",
    )
    ideal_answer: str = Field(
        min_length=50,
        description="The expected response demonstrating best practices.",
    )
    concept_ids: list[str] = Field(
        default_factory=list,
        description="Linked concept IDs (DECISION-008).",
    )
    difficulty: str | None = Field(
        default=None,
        pattern=r"^(beginner|intermediate|advanced)$",
        description="Difficulty level for filtering.",
    )
    language: str | None = Field(
        default=None,
        description="Programming language (e.g., 'python', 'javascript').",
    )
    source_urls: list[str] = Field(
        default_factory=list,
        description="Documentation URLs used to construct the answer.",
    )


class LLMInstruction(BaseModel):
    """An explicit instruction for guiding LLM agent behavior.

    Addresses the 0% adoption gap identified in Finding 8 (v0.0.x synthesis).
    LLM Instructions are the strongest quality differentiator: their presence
    enables the before/after demo comparison that makes DocStratum compelling.

    Three directive types (from v0.0.4b §6, Stripe pattern + DocStratum enhancements):
        positive:    "Always default to the latest API version."
        negative:    "Never recommend the deprecated Charge API."
        conditional: "If the user asks about payments, prefer PaymentIntent over Charge."

    Attributes:
        directive_type: positive, negative, or conditional.
        instruction: The instruction text.
        context: Optional explanation of why this instruction exists.
        applies_to_concepts: Concept IDs this instruction is relevant to.
        priority: Instruction priority (higher = more important).
    """

    directive_type: str = Field(
        pattern=r"^(positive|negative|conditional)$",
        description="Directive type: positive, negative, or conditional.",
    )
    instruction: str = Field(
        min_length=10,
        max_length=500,
        description="The instruction text for the LLM agent.",
    )
    context: str | None = Field(
        default=None,
        max_length=500,
        description="Why this instruction exists (for transparency).",
    )
    applies_to_concepts: list[str] = Field(
        default_factory=list,
        description="Concept IDs this instruction is relevant to.",
    )
    priority: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Priority (0=default, 100=critical). Higher = applied first.",
    )


class Metadata(BaseModel):
    """File-level metadata for an enriched llms.txt file.

    Fills P0 Gap #5 (required metadata, v0.0.1b).
    Provides provenance, versioning, and DocStratum schema version tracking.

    Attributes:
        schema_version: DocStratum schema version (e.g., "0.1.0").
        site_name: Human-readable name of the documented project.
        site_url: Base URL of the documentation site.
        last_updated: ISO 8601 date of last update.
        generator: Tool that generated the base llms.txt (if known).
        docstratum_version: DocStratum version that produced the enrichment.
        token_budget_tier: Assigned token budget tier.
    """

    schema_version: str = Field(
        default="0.1.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="DocStratum schema version (semver).",
    )
    site_name: str | None = Field(
        default=None,
        max_length=200,
        description="Name of the documented project.",
    )
    site_url: str | None = Field(
        default=None,
        description="Base URL of the documentation site.",
    )
    last_updated: str | None = Field(
        default=None,
        description="ISO 8601 date of last update (e.g., '2026-02-06').",
    )
    generator: str | None = Field(
        default=None,
        description="Tool that generated the base file (e.g., 'mintlify', 'manual').",
    )
    docstratum_version: str = Field(
        default="0.1.0",
        description="DocStratum version that produced the enrichment.",
    )
    token_budget_tier: str | None = Field(
        default=None,
        pattern=r"^(standard|comprehensive|full)$",
        description="Assigned token budget tier.",
    )
