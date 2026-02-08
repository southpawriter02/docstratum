"""Tests for ecosystem-level models (ecosystem.py) - v0.0.7 ecosystem pivot.

Tests all 6 new ecosystem models:
    1. LinkRelationship (from docstratum.schema.parsed)
    2. EcosystemHealthDimension
    3. FileRelationship
    4. EcosystemFile
    5. EcosystemScore
    6. DocumentEcosystem

Also tests backward compatibility:
    - ParsedLink ecosystem extension fields (FR-073)
    - ValidationDiagnostic cross-file context fields (v0.0.7)
"""

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from docstratum.schema import (
    DocumentEcosystem,
    DocumentType,
    EcosystemFile,
    EcosystemHealthDimension,
    EcosystemScore,
    FileRelationship,
    LinkRelationship,
    QualityGrade,
)
from docstratum.schema.ecosystem import _generate_uuid
from docstratum.schema.parsed import ParsedLink, ParsedLlmsTxt
from docstratum.schema.quality import DimensionScore, QualityDimension, QualityScore
from docstratum.schema.validation import (
    ValidationDiagnostic,
    ValidationLevel,
    ValidationResult,
)
from docstratum.schema.diagnostics import DiagnosticCode, Severity


# ── LinkRelationship (from docstratum.schema.parsed) ────────────────────


@pytest.mark.unit
def test_link_relationship_members():
    """Verify LinkRelationship has exactly 5 members with correct string values."""
    assert len(LinkRelationship) == 5
    assert LinkRelationship.INDEXES == "indexes"
    assert LinkRelationship.AGGREGATES == "aggregates"
    assert LinkRelationship.REFERENCES == "references"
    assert LinkRelationship.EXTERNAL == "external"
    assert LinkRelationship.UNKNOWN == "unknown"


@pytest.mark.unit
def test_link_relationship_is_str_enum():
    """Verify LinkRelationship members are comparable to plain strings."""
    assert LinkRelationship.INDEXES == "indexes"
    assert LinkRelationship.UNKNOWN != "indexes"


@pytest.mark.unit
def test_link_relationship_importable_from_public_api():
    """Verify LinkRelationship is importable from docstratum.schema (public API)."""
    # This test verifies it's in __all__ and accessible
    from docstratum.schema import LinkRelationship as PublicLinkRelationship

    assert PublicLinkRelationship.INDEXES == "indexes"


# ── EcosystemHealthDimension ─────────────────────────────────────────────


@pytest.mark.unit
def test_ecosystem_health_dimension_members():
    """Verify EcosystemHealthDimension has exactly 5 members with correct values."""
    assert len(EcosystemHealthDimension) == 5
    assert EcosystemHealthDimension.COVERAGE == "coverage"
    assert EcosystemHealthDimension.CONSISTENCY == "consistency"
    assert EcosystemHealthDimension.COMPLETENESS == "completeness"
    assert EcosystemHealthDimension.TOKEN_EFFICIENCY == "token_efficiency"
    assert EcosystemHealthDimension.FRESHNESS == "freshness"


@pytest.mark.unit
def test_ecosystem_health_dimension_is_str_enum():
    """Verify EcosystemHealthDimension members are comparable to plain strings."""
    assert EcosystemHealthDimension.COVERAGE == "coverage"
    assert EcosystemHealthDimension.COMPLETENESS != "coverage"


@pytest.mark.unit
def test_ecosystem_health_dimension_importable_from_public_api():
    """Verify EcosystemHealthDimension is importable from docstratum.schema."""
    from docstratum.schema import EcosystemHealthDimension as PublicDimension

    assert PublicDimension.TOKEN_EFFICIENCY == "token_efficiency"


# ── FileRelationship ─────────────────────────────────────────────────────


@pytest.mark.unit
def test_file_relationship_creation_required_fields():
    """Verify construction with required fields and defaults."""
    # Arrange / Act
    rel = FileRelationship(
        source_file_id="file-1-uuid",
        relationship_type=LinkRelationship.INDEXES,
        target_url="docs/api-reference.md",
    )

    # Assert
    assert rel.source_file_id == "file-1-uuid"
    assert rel.relationship_type == LinkRelationship.INDEXES
    assert rel.target_url == "docs/api-reference.md"
    assert rel.target_file_id == ""
    assert rel.source_line is None
    assert rel.is_resolved is False


@pytest.mark.unit
def test_file_relationship_creation_all_fields():
    """Verify construction with all fields explicitly set."""
    # Arrange / Act
    rel = FileRelationship(
        source_file_id="abc-123",
        target_file_id="def-456",
        relationship_type=LinkRelationship.REFERENCES,
        source_line=42,
        target_url="../other-page.md",
        is_resolved=True,
    )

    # Assert
    assert rel.source_file_id == "abc-123"
    assert rel.target_file_id == "def-456"
    assert rel.relationship_type == LinkRelationship.REFERENCES
    assert rel.source_line == 42
    assert rel.target_url == "../other-page.md"
    assert rel.is_resolved is True


@pytest.mark.unit
def test_file_relationship_external_link():
    """Verify construction of external relationship."""
    rel = FileRelationship(
        source_file_id="index-uuid",
        relationship_type=LinkRelationship.EXTERNAL,
        target_url="https://github.com/example/repo",
        is_resolved=False,  # External links are not resolved within ecosystem
    )

    assert rel.relationship_type == LinkRelationship.EXTERNAL
    assert rel.target_file_id == ""
    assert rel.is_resolved is False


@pytest.mark.unit
def test_file_relationship_rejects_invalid_source_line():
    """Verify source_line enforces ge=1 constraint."""
    with pytest.raises(ValidationError):
        FileRelationship(
            source_file_id="file-1",
            relationship_type=LinkRelationship.INDEXES,
            target_url="docs/page.md",
            source_line=0,
        )


@pytest.mark.unit
def test_file_relationship_importable_from_public_api():
    """Verify FileRelationship is importable from docstratum.schema."""
    from docstratum.schema import FileRelationship as PublicFileRel

    rel = PublicFileRel(
        source_file_id="s1",
        relationship_type=LinkRelationship.INDEXES,
        target_url="url",
    )
    assert rel.is_resolved is False


# ── EcosystemFile ───────────────────────────────────────────────────────


@pytest.mark.unit
def test_ecosystem_file_creation_minimal():
    """Verify construction with only required file_path field."""
    # Arrange / Act
    eco_file = EcosystemFile(file_path="llms.txt")

    # Assert
    assert eco_file.file_path == "llms.txt"
    assert eco_file.file_type == DocumentType.UNKNOWN
    assert eco_file.classification is None
    assert eco_file.parsed is None
    assert eco_file.validation is None
    assert eco_file.quality is None
    assert eco_file.relationships == []


@pytest.mark.unit
def test_ecosystem_file_auto_generated_id():
    """Verify file_id is auto-generated and valid UUID string."""
    eco_file = EcosystemFile(file_path="docs/api.md")

    # Assert ID is a non-empty string
    assert isinstance(eco_file.file_id, str)
    assert len(eco_file.file_id) > 0

    # Assert ID is valid UUID format
    try:
        UUID(eco_file.file_id)
    except ValueError:
        pytest.fail(f"file_id is not a valid UUID: {eco_file.file_id}")


@pytest.mark.unit
def test_ecosystem_file_unique_ids():
    """Verify each EcosystemFile gets a unique file_id."""
    file1 = EcosystemFile(file_path="docs/page1.md")
    file2 = EcosystemFile(file_path="docs/page2.md")

    assert file1.file_id != file2.file_id


@pytest.mark.unit
def test_ecosystem_file_with_document_type():
    """Verify file_type field is stored correctly."""
    eco_file = EcosystemFile(
        file_path="llms.txt",
        file_type=DocumentType.TYPE_1_INDEX,
    )

    assert eco_file.file_type == DocumentType.TYPE_1_INDEX


@pytest.mark.unit
def test_ecosystem_file_with_parsed_content():
    """Verify parsed field accepts ParsedLlmsTxt (backward compat)."""
    parsed = ParsedLlmsTxt(
        title="Test Project",
        description="Test description",
        sections=[],
    )

    eco_file = EcosystemFile(
        file_path="llms.txt",
        parsed=parsed,
    )

    assert eco_file.parsed is parsed
    assert eco_file.parsed.title == "Test Project"


@pytest.mark.unit
def test_ecosystem_file_with_validation_result():
    """Verify validation field accepts ValidationResult (backward compat)."""
    val_result = ValidationResult(
        level_achieved=ValidationLevel.L1_STRUCTURAL,
        diagnostics=[],
    )

    eco_file = EcosystemFile(
        file_path="llms.txt",
        validation=val_result,
    )

    assert eco_file.validation is val_result


@pytest.mark.unit
def test_ecosystem_file_with_quality_score():
    """Verify quality field accepts QualityScore (backward compat)."""
    quality = QualityScore(
        total_score=85.0,
        grade=QualityGrade.STRONG,
        dimensions={},
    )

    eco_file = EcosystemFile(
        file_path="llms.txt",
        quality=quality,
    )

    assert eco_file.quality is quality
    assert eco_file.quality.total_score == 85.0


@pytest.mark.unit
def test_ecosystem_file_with_relationships():
    """Verify relationships list can be populated."""
    rel = FileRelationship(
        source_file_id="f1",
        relationship_type=LinkRelationship.INDEXES,
        target_url="docs/page.md",
    )

    eco_file = EcosystemFile(
        file_path="llms.txt",
        relationships=[rel],
    )

    assert len(eco_file.relationships) == 1
    assert eco_file.relationships[0].target_url == "docs/page.md"


@pytest.mark.unit
def test_ecosystem_file_importable_from_public_api():
    """Verify EcosystemFile is importable from docstratum.schema."""
    from docstratum.schema import EcosystemFile as PublicEcoFile

    file = PublicEcoFile(file_path="test.md")
    assert file.file_path == "test.md"


# ── EcosystemScore ──────────────────────────────────────────────────────


@pytest.mark.unit
def test_ecosystem_score_creation_required_fields():
    """Verify construction with required fields and defaults."""
    # Arrange / Act
    score = EcosystemScore(
        total_score=75.5,
        grade=QualityGrade.STRONG,
        file_count=5,
        relationship_count=12,
        broken_relationships=3,
    )

    # Assert
    assert score.total_score == 75.5
    assert score.grade == QualityGrade.STRONG
    assert score.file_count == 5
    assert score.relationship_count == 12
    assert score.broken_relationships == 3
    assert score.dimensions == {}
    assert score.per_file_scores == {}


@pytest.mark.unit
def test_ecosystem_score_creation_with_dimensions():
    """Verify construction with dimension breakdown."""
    dim_score = DimensionScore(
        dimension=QualityDimension.STRUCTURAL,
        points=25.0,
        max_points=30.0,
        checks_passed=18,
        checks_failed=2,
        checks_total=20,
    )

    score = EcosystemScore(
        total_score=80.0,
        grade=QualityGrade.STRONG,
        file_count=3,
        relationship_count=8,
        broken_relationships=1,
        dimensions={EcosystemHealthDimension.COMPLETENESS: dim_score},
    )

    assert len(score.dimensions) == 1
    assert score.dimensions[EcosystemHealthDimension.COMPLETENESS] is dim_score


@pytest.mark.unit
def test_ecosystem_score_creation_with_per_file_scores():
    """Verify per_file_scores mapping is stored."""
    file_score = QualityScore(
        total_score=90.0,
        grade=QualityGrade.EXEMPLARY,
        dimensions={},
    )

    score = EcosystemScore(
        total_score=88.0,
        grade=QualityGrade.STRONG,
        file_count=1,
        relationship_count=0,
        broken_relationships=0,
        per_file_scores={"file-uuid-123": file_score},
    )

    assert "file-uuid-123" in score.per_file_scores
    assert score.per_file_scores["file-uuid-123"].total_score == 90.0


@pytest.mark.unit
def test_ecosystem_score_rejects_negative_file_count():
    """Verify file_count enforces ge=0 constraint."""
    with pytest.raises(ValidationError):
        EcosystemScore(
            total_score=80.0,
            grade=QualityGrade.STRONG,
            file_count=-1,
            relationship_count=0,
            broken_relationships=0,
        )


@pytest.mark.unit
def test_ecosystem_score_rejects_negative_relationship_count():
    """Verify relationship_count enforces ge=0 constraint."""
    with pytest.raises(ValidationError):
        EcosystemScore(
            total_score=80.0,
            grade=QualityGrade.STRONG,
            file_count=0,
            relationship_count=-1,
            broken_relationships=0,
        )


@pytest.mark.unit
def test_ecosystem_score_rejects_negative_broken_relationships():
    """Verify broken_relationships enforces ge=0 constraint."""
    with pytest.raises(ValidationError):
        EcosystemScore(
            total_score=80.0,
            grade=QualityGrade.STRONG,
            file_count=0,
            relationship_count=0,
            broken_relationships=-1,
        )


@pytest.mark.unit
def test_ecosystem_score_rejects_score_below_range():
    """Verify total_score enforces ge=0 constraint."""
    with pytest.raises(ValidationError):
        EcosystemScore(
            total_score=-0.1,
            grade=QualityGrade.CRITICAL,
            file_count=0,
            relationship_count=0,
            broken_relationships=0,
        )


@pytest.mark.unit
def test_ecosystem_score_rejects_score_above_range():
    """Verify total_score enforces le=100 constraint."""
    with pytest.raises(ValidationError):
        EcosystemScore(
            total_score=100.1,
            grade=QualityGrade.EXEMPLARY,
            file_count=0,
            relationship_count=0,
            broken_relationships=0,
        )


@pytest.mark.unit
def test_ecosystem_score_resolution_rate_zero_relationships():
    """Verify resolution_rate returns 100% with zero relationships (vacuous truth)."""
    # Arrange / Act
    score = EcosystemScore(
        total_score=100.0,
        grade=QualityGrade.EXEMPLARY,
        file_count=1,
        relationship_count=0,
        broken_relationships=0,
    )

    # Assert
    assert score.resolution_rate == 100.0


@pytest.mark.unit
def test_ecosystem_score_resolution_rate_all_resolved():
    """Verify resolution_rate is 100% when all relationships resolve."""
    score = EcosystemScore(
        total_score=95.0,
        grade=QualityGrade.EXEMPLARY,
        file_count=5,
        relationship_count=10,
        broken_relationships=0,
    )

    assert score.resolution_rate == 100.0


@pytest.mark.unit
def test_ecosystem_score_resolution_rate_partial_resolution():
    """Verify resolution_rate computes correct percentage."""
    score = EcosystemScore(
        total_score=70.0,
        grade=QualityGrade.STRONG,
        file_count=5,
        relationship_count=20,
        broken_relationships=5,  # 15 resolved, 5 broken
    )

    assert score.resolution_rate == pytest.approx(75.0)


@pytest.mark.unit
def test_ecosystem_score_resolution_rate_all_broken():
    """Verify resolution_rate is 0% when all relationships are broken."""
    score = EcosystemScore(
        total_score=20.0,
        grade=QualityGrade.CRITICAL,
        file_count=5,
        relationship_count=8,
        broken_relationships=8,
    )

    assert score.resolution_rate == 0.0


@pytest.mark.unit
def test_ecosystem_score_has_scored_at_timestamp():
    """Verify scored_at timestamp defaults to current time."""
    before = datetime.now()
    score = EcosystemScore(
        total_score=80.0,
        grade=QualityGrade.STRONG,
        file_count=0,
        relationship_count=0,
        broken_relationships=0,
    )
    after = datetime.now()

    assert before <= score.scored_at <= after


@pytest.mark.unit
def test_ecosystem_score_importable_from_public_api():
    """Verify EcosystemScore is importable from docstratum.schema."""
    from docstratum.schema import EcosystemScore as PublicScore

    score = PublicScore(
        total_score=50.0,
        grade=QualityGrade.ADEQUATE,
        file_count=0,
        relationship_count=0,
        broken_relationships=0,
    )
    assert score.total_score == 50.0


# ── DocumentEcosystem ────────────────────────────────────────────────────


@pytest.mark.unit
def test_document_ecosystem_creation_minimal():
    """Verify construction with only required root_file."""
    # Arrange
    root_file = EcosystemFile(
        file_path="llms.txt",
        file_type=DocumentType.TYPE_1_INDEX,
    )

    # Act
    eco = DocumentEcosystem(root_file=root_file)

    # Assert
    assert eco.root_file is root_file
    assert eco.project_name == "Unknown Project"
    assert eco.files == []
    assert eco.relationships == []
    assert eco.ecosystem_score is None


@pytest.mark.unit
def test_document_ecosystem_auto_generated_id():
    """Verify ecosystem_id is auto-generated and valid UUID string."""
    root_file = EcosystemFile(file_path="llms.txt")

    eco = DocumentEcosystem(root_file=root_file)

    assert isinstance(eco.ecosystem_id, str)
    assert len(eco.ecosystem_id) > 0
    try:
        UUID(eco.ecosystem_id)
    except ValueError:
        pytest.fail(f"ecosystem_id is not a valid UUID: {eco.ecosystem_id}")


@pytest.mark.unit
def test_document_ecosystem_unique_ids():
    """Verify each DocumentEcosystem gets a unique ecosystem_id."""
    root1 = EcosystemFile(file_path="llms.txt")
    root2 = EcosystemFile(file_path="llms.txt")

    eco1 = DocumentEcosystem(root_file=root1)
    eco2 = DocumentEcosystem(root_file=root2)

    assert eco1.ecosystem_id != eco2.ecosystem_id


@pytest.mark.unit
def test_document_ecosystem_with_project_name():
    """Verify project_name field is stored correctly."""
    root_file = EcosystemFile(file_path="llms.txt")

    eco = DocumentEcosystem(
        project_name="Stripe API",
        root_file=root_file,
    )

    assert eco.project_name == "Stripe API"


@pytest.mark.unit
def test_document_ecosystem_with_files():
    """Verify files list is populated correctly."""
    root_file = EcosystemFile(
        file_path="llms.txt",
        file_type=DocumentType.TYPE_1_INDEX,
    )
    page1 = EcosystemFile(
        file_path="docs/api.md",
        file_type=DocumentType.TYPE_3_CONTENT_PAGE,
    )
    page2 = EcosystemFile(
        file_path="docs/guide.md",
        file_type=DocumentType.TYPE_3_CONTENT_PAGE,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        files=[root_file, page1, page2],
    )

    assert len(eco.files) == 3
    assert eco.files[0] is root_file


@pytest.mark.unit
def test_document_ecosystem_with_relationships():
    """Verify relationships list is populated correctly."""
    root_file = EcosystemFile(file_path="llms.txt")

    rel1 = FileRelationship(
        source_file_id="f1",
        relationship_type=LinkRelationship.INDEXES,
        target_url="docs/api.md",
        is_resolved=True,
    )
    rel2 = FileRelationship(
        source_file_id="f1",
        relationship_type=LinkRelationship.INDEXES,
        target_url="docs/guide.md",
        is_resolved=False,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        relationships=[rel1, rel2],
    )

    assert len(eco.relationships) == 2
    assert eco.relationships[0].is_resolved is True
    assert eco.relationships[1].is_resolved is False


@pytest.mark.unit
def test_document_ecosystem_with_ecosystem_score():
    """Verify ecosystem_score field is stored correctly."""
    root_file = EcosystemFile(file_path="llms.txt")

    score = EcosystemScore(
        total_score=85.0,
        grade=QualityGrade.STRONG,
        file_count=3,
        relationship_count=5,
        broken_relationships=1,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        ecosystem_score=score,
    )

    assert eco.ecosystem_score is score
    assert eco.ecosystem_score.total_score == 85.0


@pytest.mark.unit
def test_document_ecosystem_discovered_at_timestamp():
    """Verify discovered_at defaults to current time."""
    before = datetime.now()
    root_file = EcosystemFile(file_path="llms.txt")
    eco = DocumentEcosystem(root_file=root_file)
    after = datetime.now()

    assert before <= eco.discovered_at <= after


# ── DocumentEcosystem Computed Properties ────────────────────────────────


@pytest.mark.unit
def test_document_ecosystem_file_count():
    """Exit Criterion: file_count property returns len(files)."""
    root_file = EcosystemFile(file_path="llms.txt")
    page1 = EcosystemFile(file_path="docs/api.md")
    page2 = EcosystemFile(file_path="docs/guide.md")

    eco = DocumentEcosystem(
        root_file=root_file,
        files=[root_file, page1, page2],
    )

    assert eco.file_count == 3
    assert eco.file_count == len(eco.files)


@pytest.mark.unit
def test_document_ecosystem_index_file():
    """Exit Criterion: index_file property returns root_file."""
    root_file = EcosystemFile(
        file_path="llms.txt",
        file_type=DocumentType.TYPE_1_INDEX,
    )

    eco = DocumentEcosystem(root_file=root_file)

    assert eco.index_file is root_file


@pytest.mark.unit
def test_document_ecosystem_aggregate_file_present():
    """Exit Criterion: aggregate_file returns first TYPE_2_FULL file."""
    root_file = EcosystemFile(file_path="llms.txt")
    full_file = EcosystemFile(
        file_path="llms-full.txt",
        file_type=DocumentType.TYPE_2_FULL,
    )
    page = EcosystemFile(
        file_path="docs/api.md",
        file_type=DocumentType.TYPE_3_CONTENT_PAGE,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        files=[root_file, page, full_file],
    )

    assert eco.aggregate_file is full_file
    assert eco.aggregate_file.file_type == DocumentType.TYPE_2_FULL


@pytest.mark.unit
def test_document_ecosystem_aggregate_file_absent():
    """Verify aggregate_file returns None when no TYPE_2_FULL file exists."""
    root_file = EcosystemFile(file_path="llms.txt")
    page = EcosystemFile(
        file_path="docs/api.md",
        file_type=DocumentType.TYPE_3_CONTENT_PAGE,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        files=[root_file, page],
    )

    assert eco.aggregate_file is None


@pytest.mark.unit
def test_document_ecosystem_content_pages():
    """Exit Criterion: content_pages returns all TYPE_3_CONTENT_PAGE files."""
    root_file = EcosystemFile(file_path="llms.txt")
    page1 = EcosystemFile(
        file_path="docs/api.md",
        file_type=DocumentType.TYPE_3_CONTENT_PAGE,
    )
    page2 = EcosystemFile(
        file_path="docs/guide.md",
        file_type=DocumentType.TYPE_3_CONTENT_PAGE,
    )
    full_file = EcosystemFile(
        file_path="llms-full.txt",
        file_type=DocumentType.TYPE_2_FULL,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        files=[root_file, page1, page2, full_file],
    )

    content = eco.content_pages
    assert len(content) == 2
    assert page1 in content
    assert page2 in content
    assert full_file not in content


@pytest.mark.unit
def test_document_ecosystem_content_pages_empty():
    """Verify content_pages returns empty list when no content pages exist."""
    root_file = EcosystemFile(file_path="llms.txt")

    eco = DocumentEcosystem(root_file=root_file, files=[root_file])

    assert eco.content_pages == []


@pytest.mark.unit
def test_document_ecosystem_instruction_file_present():
    """Exit Criterion: instruction_file returns first TYPE_4_INSTRUCTIONS file."""
    root_file = EcosystemFile(file_path="llms.txt")
    instr_file = EcosystemFile(
        file_path="llms-instructions.txt",
        file_type=DocumentType.TYPE_4_INSTRUCTIONS,
    )
    page = EcosystemFile(
        file_path="docs/api.md",
        file_type=DocumentType.TYPE_3_CONTENT_PAGE,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        files=[root_file, page, instr_file],
    )

    assert eco.instruction_file is instr_file
    assert eco.instruction_file.file_type == DocumentType.TYPE_4_INSTRUCTIONS


@pytest.mark.unit
def test_document_ecosystem_instruction_file_absent():
    """Verify instruction_file returns None when no TYPE_4_INSTRUCTIONS file exists."""
    root_file = EcosystemFile(file_path="llms.txt")
    page = EcosystemFile(
        file_path="docs/api.md",
        file_type=DocumentType.TYPE_3_CONTENT_PAGE,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        files=[root_file, page],
    )

    assert eco.instruction_file is None


@pytest.mark.unit
def test_document_ecosystem_is_single_file_true():
    """Exit Criterion: is_single_file returns True with 0 or 1 files."""
    root_file = EcosystemFile(file_path="llms.txt")

    # Single file in list
    eco1 = DocumentEcosystem(root_file=root_file, files=[root_file])
    assert eco1.is_single_file is True

    # Empty files list
    eco2 = DocumentEcosystem(root_file=root_file, files=[])
    assert eco2.is_single_file is True


@pytest.mark.unit
def test_document_ecosystem_is_single_file_false():
    """Verify is_single_file returns False when ecosystem has multiple files."""
    root_file = EcosystemFile(file_path="llms.txt")
    page = EcosystemFile(file_path="docs/api.md")

    eco = DocumentEcosystem(
        root_file=root_file,
        files=[root_file, page],
    )

    assert eco.is_single_file is False


@pytest.mark.unit
def test_document_ecosystem_resolved_relationship_count():
    """Exit Criterion: resolved_relationship_count counts is_resolved=True."""
    root_file = EcosystemFile(file_path="llms.txt")

    rel1 = FileRelationship(
        source_file_id="f1",
        relationship_type=LinkRelationship.INDEXES,
        target_url="docs/api.md",
        is_resolved=True,
    )
    rel2 = FileRelationship(
        source_file_id="f1",
        relationship_type=LinkRelationship.INDEXES,
        target_url="docs/guide.md",
        is_resolved=True,
    )
    rel3 = FileRelationship(
        source_file_id="f1",
        relationship_type=LinkRelationship.INDEXES,
        target_url="docs/missing.md",
        is_resolved=False,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        relationships=[rel1, rel2, rel3],
    )

    assert eco.resolved_relationship_count == 2


@pytest.mark.unit
def test_document_ecosystem_broken_relationship_count():
    """Exit Criterion: broken_relationship_count counts is_resolved=False."""
    root_file = EcosystemFile(file_path="llms.txt")

    rel1 = FileRelationship(
        source_file_id="f1",
        relationship_type=LinkRelationship.INDEXES,
        target_url="docs/api.md",
        is_resolved=True,
    )
    rel2 = FileRelationship(
        source_file_id="f1",
        relationship_type=LinkRelationship.INDEXES,
        target_url="docs/missing.md",
        is_resolved=False,
    )
    rel3 = FileRelationship(
        source_file_id="f1",
        relationship_type=LinkRelationship.EXTERNAL,
        target_url="https://external.com",
        is_resolved=False,
    )

    eco = DocumentEcosystem(
        root_file=root_file,
        relationships=[rel1, rel2, rel3],
    )

    assert eco.broken_relationship_count == 2


@pytest.mark.unit
def test_document_ecosystem_importable_from_public_api():
    """Verify DocumentEcosystem is importable from docstratum.schema."""
    from docstratum.schema import DocumentEcosystem as PublicEco

    root = PublicEco(root_file=EcosystemFile(file_path="llms.txt"))
    assert root.project_name == "Unknown Project"


# ── ParsedLink Backward Compatibility (FR-073) ───────────────────────────


@pytest.mark.unit
def test_parsed_link_backward_compat_no_ecosystem_fields():
    """Exit Criterion: ParsedLink without ecosystem fields works identically to pre-pivot."""
    # Arrange / Act - construct without ecosystem fields (pre-pivot style)
    link = ParsedLink(
        title="Getting Started",
        url="https://example.com/start",
        line_number=5,
    )

    # Assert - defaults are safe for single-file mode
    assert link.title == "Getting Started"
    assert link.url == "https://example.com/start"
    assert link.line_number == 5
    assert link.relationship == LinkRelationship.UNKNOWN
    assert link.resolves_to is None
    assert link.target_file_type is None


@pytest.mark.unit
def test_parsed_link_backward_compat_with_ecosystem_fields():
    """Exit Criterion: ParsedLink with ecosystem fields persists through serialization."""
    # Arrange
    link = ParsedLink(
        title="API Reference",
        url="docs/api.md",
        line_number=10,
        relationship=LinkRelationship.INDEXES,
        resolves_to="docs/api.md",
        target_file_type="type_3_content_page",
    )

    # Act - serialize and deserialize
    serialized = link.model_dump()
    deserialized = ParsedLink.model_validate(serialized)

    # Assert - ecosystem fields persist
    assert deserialized.relationship == LinkRelationship.INDEXES
    assert deserialized.resolves_to == "docs/api.md"
    assert deserialized.target_file_type == "type_3_content_page"


@pytest.mark.unit
def test_parsed_link_defaults_to_unknown_relationship():
    """Verify relationship defaults to UNKNOWN in single-file mode."""
    link = ParsedLink(
        title="Test",
        url="https://example.com",
        line_number=1,
    )

    assert link.relationship == LinkRelationship.UNKNOWN


# ── ValidationDiagnostic Cross-File Context (v0.0.7) ──────────────────


@pytest.mark.unit
def test_validation_diagnostic_backward_compat_no_source_file():
    """Exit Criterion: ValidationDiagnostic without source/related_file works (backward compat)."""
    # Arrange / Act
    diag = ValidationDiagnostic(
        code=DiagnosticCode.E001_NO_H1_TITLE,
        severity=Severity.ERROR,
        message="No H1 title found.",
        level=ValidationLevel.L1_STRUCTURAL,
    )

    # Assert - ecosystem fields are None (backward compatible)
    assert diag.source_file is None
    assert diag.related_file is None


@pytest.mark.unit
def test_validation_diagnostic_with_source_file_field():
    """Exit Criterion: ValidationDiagnostic with source_file persists through serialization."""
    # Arrange
    diag = ValidationDiagnostic(
        code=DiagnosticCode.W001_MISSING_BLOCKQUOTE,
        severity=Severity.WARNING,
        message="No blockquote found.",
        level=ValidationLevel.L1_STRUCTURAL,
        source_file="llms.txt",
    )

    # Act - serialize and deserialize
    serialized = diag.model_dump()
    deserialized = ValidationDiagnostic.model_validate(serialized)

    # Assert - source_file persists
    assert deserialized.source_file == "llms.txt"


@pytest.mark.unit
def test_validation_diagnostic_with_related_file_field():
    """Verify related_file persists through serialization."""
    diag = ValidationDiagnostic(
        code=DiagnosticCode.E001_NO_H1_TITLE,
        severity=Severity.ERROR,
        message="Missing target file.",
        level=ValidationLevel.L1_STRUCTURAL,
        related_file="docs/api.md",
    )

    serialized = diag.model_dump()
    deserialized = ValidationDiagnostic.model_validate(serialized)

    assert deserialized.related_file == "docs/api.md"


@pytest.mark.unit
def test_validation_diagnostic_with_both_cross_file_fields():
    """Verify source_file and related_file both persist through serialization."""
    diag = ValidationDiagnostic(
        code=DiagnosticCode.E001_NO_H1_TITLE,
        severity=Severity.ERROR,
        message="Broken cross-file link.",
        level=ValidationLevel.L1_STRUCTURAL,
        source_file="llms.txt",
        related_file="docs/missing.md",
    )

    serialized = diag.model_dump()
    deserialized = ValidationDiagnostic.model_validate(serialized)

    assert deserialized.source_file == "llms.txt"
    assert deserialized.related_file == "docs/missing.md"


# ── UUID Generation Helper ───────────────────────────────────────────────


@pytest.mark.unit
def test_generate_uuid_returns_valid_uuid_string():
    """Verify _generate_uuid returns a valid UUID4 string."""
    uuid_str = _generate_uuid()

    assert isinstance(uuid_str, str)
    assert len(uuid_str) > 0

    try:
        UUID(uuid_str)
    except ValueError:
        pytest.fail(f"_generate_uuid returned invalid UUID: {uuid_str}")


@pytest.mark.unit
def test_generate_uuid_uniqueness():
    """Verify _generate_uuid produces unique values across calls."""
    uuid1 = _generate_uuid()
    uuid2 = _generate_uuid()
    uuid3 = _generate_uuid()

    assert uuid1 != uuid2
    assert uuid2 != uuid3
    assert uuid1 != uuid3
