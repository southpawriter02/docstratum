"""Tests for document classification models (classification.py)."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from docstratum.schema.classification import (
    DocumentClassification,
    DocumentType,
    SizeTier,
)


@pytest.mark.unit
def test_document_type_values():
    """Verify DocumentType has exactly 5 members with correct string values."""
    assert len(DocumentType) == 5
    assert DocumentType.TYPE_1_INDEX == "type_1_index"
    assert DocumentType.TYPE_2_FULL == "type_2_full"
    assert DocumentType.UNKNOWN == "unknown"
    assert DocumentType.TYPE_3_CONTENT_PAGE == "type_3_content_page"
    assert DocumentType.TYPE_4_INSTRUCTIONS == "type_4_instructions"


@pytest.mark.unit
def test_document_type_is_str_enum():
    """Verify DocumentType members are comparable to plain strings."""
    assert isinstance(DocumentType.TYPE_1_INDEX, str)
    assert DocumentType.TYPE_1_INDEX == "type_1_index"


@pytest.mark.unit
def test_size_tier_values():
    """Verify SizeTier has exactly 5 members with correct string values."""
    assert len(SizeTier) == 5
    assert SizeTier.MINIMAL == "minimal"
    assert SizeTier.STANDARD == "standard"
    assert SizeTier.COMPREHENSIVE == "comprehensive"
    assert SizeTier.FULL == "full"
    assert SizeTier.OVERSIZED == "oversized"


@pytest.mark.unit
def test_size_tier_is_str_enum():
    """Verify SizeTier members are comparable to plain strings."""
    assert isinstance(SizeTier.MINIMAL, str)
    assert SizeTier.OVERSIZED == "oversized"


@pytest.mark.unit
def test_document_classification_type_boundary_bytes():
    """Exit Criterion 3: TYPE_BOUNDARY_BYTES == 256_000."""
    assert DocumentClassification.TYPE_BOUNDARY_BYTES == 256_000


@pytest.mark.unit
def test_document_classification_creation_defaults():
    """Verify default values for optional fields."""
    # Arrange / Act
    classification = DocumentClassification(
        document_type=DocumentType.TYPE_1_INDEX,
        size_bytes=1024,
        estimated_tokens=256,
        size_tier=SizeTier.MINIMAL,
    )

    # Assert
    assert classification.filename == "llms.txt"
    assert isinstance(classification.classified_at, datetime)


@pytest.mark.unit
def test_document_classification_creation_all_fields():
    """Verify all fields round-trip correctly when explicitly set."""
    # Arrange
    ts = datetime(2026, 2, 6, 12, 0, 0)

    # Act
    classification = DocumentClassification(
        document_type=DocumentType.TYPE_2_FULL,
        size_bytes=2_000_000,
        estimated_tokens=500_000,
        size_tier=SizeTier.OVERSIZED,
        filename="llms-full.txt",
        classified_at=ts,
    )

    # Assert
    assert classification.document_type == DocumentType.TYPE_2_FULL
    assert classification.size_bytes == 2_000_000
    assert classification.estimated_tokens == 500_000
    assert classification.size_tier == SizeTier.OVERSIZED
    assert classification.filename == "llms-full.txt"
    assert classification.classified_at == ts


@pytest.mark.unit
def test_document_classification_rejects_negative_size_bytes():
    """Verify size_bytes enforces ge=0 constraint."""
    with pytest.raises(ValidationError):
        DocumentClassification(
            document_type=DocumentType.TYPE_1_INDEX,
            size_bytes=-1,
            estimated_tokens=0,
            size_tier=SizeTier.MINIMAL,
        )


@pytest.mark.unit
def test_document_classification_rejects_negative_tokens():
    """Verify estimated_tokens enforces ge=0 constraint."""
    with pytest.raises(ValidationError):
        DocumentClassification(
            document_type=DocumentType.TYPE_1_INDEX,
            size_bytes=0,
            estimated_tokens=-1,
            size_tier=SizeTier.MINIMAL,
        )


@pytest.mark.unit
def test_classification_importable_from_schema():
    """Exit Criterion 1: All classification models importable from public API."""
    from docstratum import schema

    assert schema.DocumentType is DocumentType
    assert schema.SizeTier is SizeTier
    assert schema.DocumentClassification is DocumentClassification
