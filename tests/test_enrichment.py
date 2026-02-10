"""Tests for enrichment models (enrichment.py).

Exit Criteria (from v0.1.2d spec):
    - All enrichment models importable
    - Concept.id rejects non-DECISION-004-format strings
    - FewShotExample.question enforces min_length=10
    - LLMInstruction.directive_type accepts only positive/negative/conditional
    - Metadata.schema_version enforces semver pattern
"""

import pytest
from pydantic import ValidationError

from docstratum.schema.enrichment import (
    Concept,
    ConceptRelationship,
    FewShotExample,
    LLMInstruction,
    Metadata,
    RelationshipType,
)

# ── RelationshipType ─────────────────────────────────────────────────


@pytest.mark.unit
def test_relationship_type_values():
    """Verify RelationshipType has exactly 5 members with correct string values."""
    assert len(RelationshipType) == 5
    assert RelationshipType.DEPENDS_ON == "depends_on"
    assert RelationshipType.RELATES_TO == "relates_to"
    assert RelationshipType.CONFLICTS_WITH == "conflicts_with"
    assert RelationshipType.SPECIALIZES == "specializes"
    assert RelationshipType.SUPERSEDES == "supersedes"


# ── ConceptRelationship ──────────────────────────────────────────────


def _make_concept_relationship(
    target_id: str = "auth-token",
    relationship_type: RelationshipType = RelationshipType.DEPENDS_ON,
    description: str | None = None,
) -> ConceptRelationship:
    """Helper to create a ConceptRelationship with sensible defaults."""
    return ConceptRelationship(
        target_id=target_id,
        relationship_type=relationship_type,
        description=description,
    )


@pytest.mark.unit
def test_concept_relationship_creation():
    """Verify ConceptRelationship construction with all fields."""
    rel = _make_concept_relationship(description="Token depends on auth flow.")

    assert rel.target_id == "auth-token"
    assert rel.relationship_type == RelationshipType.DEPENDS_ON
    assert rel.description == "Token depends on auth flow."


@pytest.mark.unit
def test_concept_relationship_optional_description():
    """Verify description defaults to None."""
    rel = _make_concept_relationship()

    assert rel.description is None


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad_id",
    [
        "InvalidId",
        "has spaces",
        "under_score",
        "UPPER",
        "special!char",
        "",
    ],
)
def test_concept_relationship_rejects_invalid_target_id(bad_id: str):
    """Exit Criterion: target_id rejects non-DECISION-004 format strings."""
    with pytest.raises(ValidationError):
        _make_concept_relationship(target_id=bad_id)


@pytest.mark.unit
def test_concept_relationship_description_max_length():
    """Verify description enforces max_length=200."""
    with pytest.raises(ValidationError):
        _make_concept_relationship(description="x" * 201)


# ── Concept ──────────────────────────────────────────────────────────


def _make_concept(
    concept_id: str = "payment-intent",
    name: str = "PaymentIntent",
    definition: str = "A PaymentIntent tracks the lifecycle of a payment from creation to completion.",
    **kwargs,
) -> Concept:
    """Helper to create a Concept with sensible defaults."""
    return Concept(id=concept_id, name=name, definition=definition, **kwargs)


@pytest.mark.unit
def test_concept_creation():
    """Verify Concept construction with required fields and defaults."""
    concept = _make_concept()

    assert concept.id == "payment-intent"
    assert concept.name == "PaymentIntent"
    assert len(concept.definition) >= 10
    assert concept.aliases == []
    assert concept.relationships == []
    assert concept.related_page_urls == []
    assert concept.anti_patterns == []
    assert concept.domain is None


@pytest.mark.unit
def test_concept_full_construction():
    """Verify Concept with all optional fields populated."""
    rel = _make_concept_relationship(
        target_id="charge",
        relationship_type=RelationshipType.SUPERSEDES,
        description="PaymentIntent replaces Charge.",
    )
    concept = _make_concept(
        aliases=["PI", "payment_intent"],
        relationships=[rel],
        related_page_urls=["https://docs.example.com/payments"],
        anti_patterns=["Do not use the deprecated Charge API."],
        domain="payments",
    )

    assert concept.aliases == ["PI", "payment_intent"]
    assert len(concept.relationships) == 1
    assert concept.relationships[0].target_id == "charge"
    assert concept.domain == "payments"


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad_id",
    [
        "InvalidId",
        "has spaces",
        "UPPER",
        "",
    ],
)
def test_concept_rejects_invalid_id(bad_id: str):
    """Exit Criterion: Concept.id rejects non-DECISION-004 format strings."""
    with pytest.raises(ValidationError):
        _make_concept(concept_id=bad_id)


@pytest.mark.unit
def test_concept_definition_min_length():
    """Verify definition enforces min_length=10."""
    with pytest.raises(ValidationError):
        _make_concept(definition="Too short")


@pytest.mark.unit
def test_concept_definition_max_length():
    """Verify definition enforces max_length=500."""
    with pytest.raises(ValidationError):
        _make_concept(definition="x" * 501)


@pytest.mark.unit
def test_concept_name_max_length():
    """Verify name enforces max_length=100."""
    with pytest.raises(ValidationError):
        _make_concept(name="x" * 101)


@pytest.mark.unit
def test_concept_name_min_length():
    """Verify name enforces min_length=1."""
    with pytest.raises(ValidationError):
        _make_concept(name="")


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad_domain",
    ["Invalid", "has spaces", "UPPER"],
)
def test_concept_rejects_invalid_domain(bad_domain: str):
    """Verify domain enforces DECISION-004 pattern."""
    with pytest.raises(ValidationError):
        _make_concept(domain=bad_domain)


# ── FewShotExample ───────────────────────────────────────────────────


def _make_few_shot_example(
    example_id: str = "auth-web-app-001",
    intent: str = "Authenticate a web application",
    question: str = "How do I authenticate a web app with OAuth2?",
    ideal_answer: str = (
        "To authenticate a web app with OAuth2, you need to register your"
        " application, obtain client credentials, and implement the"
        " authorization code flow."
    ),
    **kwargs,
) -> FewShotExample:
    """Helper to create a FewShotExample with sensible defaults."""
    return FewShotExample(
        id=example_id,
        intent=intent,
        question=question,
        ideal_answer=ideal_answer,
        **kwargs,
    )


@pytest.mark.unit
def test_few_shot_example_creation():
    """Verify FewShotExample construction with required fields and defaults."""
    example = _make_few_shot_example()

    assert example.id == "auth-web-app-001"
    assert example.intent == "Authenticate a web application"
    assert len(example.question) >= 10
    assert len(example.ideal_answer) >= 50
    assert example.concept_ids == []
    assert example.difficulty is None
    assert example.language is None
    assert example.source_urls == []


@pytest.mark.unit
def test_few_shot_example_full_construction():
    """Verify FewShotExample with all optional fields populated."""
    example = _make_few_shot_example(
        concept_ids=["oauth2", "web-auth"],
        difficulty="intermediate",
        language="python",
        source_urls=["https://docs.example.com/auth"],
    )

    assert example.concept_ids == ["oauth2", "web-auth"]
    assert example.difficulty == "intermediate"
    assert example.language == "python"
    assert len(example.source_urls) == 1


@pytest.mark.unit
def test_few_shot_example_rejects_invalid_id():
    """Verify id enforces DECISION-004 pattern."""
    with pytest.raises(ValidationError):
        _make_few_shot_example(example_id="Invalid ID!")


@pytest.mark.unit
def test_few_shot_example_question_min_length():
    """Exit Criterion: FewShotExample.question enforces min_length=10."""
    with pytest.raises(ValidationError):
        _make_few_shot_example(question="Too short")


@pytest.mark.unit
def test_few_shot_example_ideal_answer_min_length():
    """Verify ideal_answer enforces min_length=50."""
    with pytest.raises(ValidationError):
        _make_few_shot_example(ideal_answer="Too short to be a real answer.")


@pytest.mark.unit
@pytest.mark.parametrize("valid_difficulty", ["beginner", "intermediate", "advanced"])
def test_few_shot_example_valid_difficulty(valid_difficulty: str):
    """Verify difficulty accepts all three valid values."""
    example = _make_few_shot_example(difficulty=valid_difficulty)

    assert example.difficulty == valid_difficulty


@pytest.mark.unit
def test_few_shot_example_rejects_invalid_difficulty():
    """Verify difficulty rejects invalid values."""
    with pytest.raises(ValidationError):
        _make_few_shot_example(difficulty="expert")


# ── LLMInstruction ───────────────────────────────────────────────────


def _make_llm_instruction(
    directive_type: str = "positive",
    instruction: str = "Always default to the latest API version.",
    **kwargs,
) -> LLMInstruction:
    """Helper to create an LLMInstruction with sensible defaults."""
    return LLMInstruction(
        directive_type=directive_type,
        instruction=instruction,
        **kwargs,
    )


@pytest.mark.unit
def test_llm_instruction_creation():
    """Verify LLMInstruction construction with required fields and defaults."""
    instr = _make_llm_instruction()

    assert instr.directive_type == "positive"
    assert instr.instruction == "Always default to the latest API version."
    assert instr.context is None
    assert instr.applies_to_concepts == []
    assert instr.priority == 0


@pytest.mark.unit
def test_llm_instruction_full_construction():
    """Verify LLMInstruction with all optional fields populated."""
    instr = _make_llm_instruction(
        directive_type="conditional",
        instruction="If the user asks about payments, prefer PaymentIntent over Charge.",
        context="Charge API is deprecated since 2023.",
        applies_to_concepts=["payment-intent", "charge"],
        priority=90,
    )

    assert instr.directive_type == "conditional"
    assert instr.context == "Charge API is deprecated since 2023."
    assert instr.applies_to_concepts == ["payment-intent", "charge"]
    assert instr.priority == 90


@pytest.mark.unit
@pytest.mark.parametrize("valid_type", ["positive", "negative", "conditional"])
def test_llm_instruction_valid_directive_types(valid_type: str):
    """Exit Criterion: directive_type accepts only positive/negative/conditional."""
    instr = _make_llm_instruction(directive_type=valid_type)

    assert instr.directive_type == valid_type


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad_type",
    ["POSITIVE", "neutral", "maybe", ""],
)
def test_llm_instruction_rejects_invalid_directive_type(bad_type: str):
    """Exit Criterion: directive_type rejects invalid values."""
    with pytest.raises(ValidationError):
        _make_llm_instruction(directive_type=bad_type)


@pytest.mark.unit
def test_llm_instruction_priority_min():
    """Verify priority enforces ge=0."""
    with pytest.raises(ValidationError):
        _make_llm_instruction(priority=-1)


@pytest.mark.unit
def test_llm_instruction_priority_max():
    """Verify priority enforces le=100."""
    with pytest.raises(ValidationError):
        _make_llm_instruction(priority=101)


@pytest.mark.unit
def test_llm_instruction_priority_boundaries():
    """Verify priority accepts boundary values 0 and 100."""
    assert _make_llm_instruction(priority=0).priority == 0
    assert _make_llm_instruction(priority=100).priority == 100


# ── Metadata ─────────────────────────────────────────────────────────


@pytest.mark.unit
def test_metadata_defaults():
    """Verify Metadata construction with all defaults."""
    meta = Metadata()

    assert meta.schema_version == "0.1.0"
    assert meta.site_name is None
    assert meta.site_url is None
    assert meta.last_updated is None
    assert meta.generator is None
    assert meta.docstratum_version == "0.1.0"
    assert meta.token_budget_tier is None


@pytest.mark.unit
def test_metadata_full_construction():
    """Verify Metadata with all fields populated."""
    meta = Metadata(
        schema_version="1.2.3",
        site_name="Stripe Docs",
        site_url="https://docs.stripe.com",
        last_updated="2026-02-06",
        generator="mintlify",
        docstratum_version="0.2.0",
        token_budget_tier="comprehensive",
    )

    assert meta.schema_version == "1.2.3"
    assert meta.site_name == "Stripe Docs"
    assert meta.site_url == "https://docs.stripe.com"
    assert meta.last_updated == "2026-02-06"
    assert meta.generator == "mintlify"
    assert meta.docstratum_version == "0.2.0"
    assert meta.token_budget_tier == "comprehensive"


@pytest.mark.unit
def test_metadata_schema_version_rejects_non_semver():
    """Exit Criterion: schema_version enforces semver pattern."""
    with pytest.raises(ValidationError):
        Metadata(schema_version="1.0")

    with pytest.raises(ValidationError):
        Metadata(schema_version="not-a-version")

    with pytest.raises(ValidationError):
        Metadata(schema_version="v1.0.0")


@pytest.mark.unit
@pytest.mark.parametrize("valid_tier", ["standard", "comprehensive", "full"])
def test_metadata_valid_token_budget_tiers(valid_tier: str):
    """Verify token_budget_tier accepts all three valid values."""
    meta = Metadata(token_budget_tier=valid_tier)

    assert meta.token_budget_tier == valid_tier


@pytest.mark.unit
def test_metadata_rejects_invalid_token_budget_tier():
    """Verify token_budget_tier rejects invalid values."""
    with pytest.raises(ValidationError):
        Metadata(token_budget_tier="premium")


# ── Public API ───────────────────────────────────────────────────────


@pytest.mark.unit
def test_enrichment_models_importable_from_schema():
    """Exit Criterion: All enrichment models importable from public API."""
    from docstratum import schema

    assert schema.RelationshipType is RelationshipType
    assert schema.ConceptRelationship is ConceptRelationship
    assert schema.Concept is Concept
    assert schema.FewShotExample is FewShotExample
    assert schema.LLMInstruction is LLMInstruction
    assert schema.Metadata is Metadata
