"""Tests for parsed document models (parsed.py)."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from docstratum.schema.parsed import (
    ParsedBlockquote,
    ParsedLink,
    ParsedLlmsTxt,
    ParsedSection,
)

# ── ParsedBlockquote ─────────────────────────────────────────────────


@pytest.mark.unit
def test_parsed_blockquote_creation():
    """Verify construction with required fields and default for raw."""
    # Arrange / Act
    bq = ParsedBlockquote(text="API documentation for Stripe", line_number=2)

    # Assert
    assert bq.text == "API documentation for Stripe"
    assert bq.line_number == 2
    assert bq.raw == ""


@pytest.mark.unit
def test_parsed_blockquote_with_raw():
    """Verify raw field stores original text including '>' prefix."""
    bq = ParsedBlockquote(
        text="API docs",
        line_number=2,
        raw="> API docs",
    )

    assert bq.raw == "> API docs"


@pytest.mark.unit
def test_parsed_blockquote_rejects_invalid_line_number():
    """Verify line_number enforces ge=1 constraint."""
    with pytest.raises(ValidationError):
        ParsedBlockquote(text="test", line_number=0)


# ── ParsedLink ───────────────────────────────────────────────────────


@pytest.mark.unit
def test_parsed_link_creation():
    """Verify construction with required fields and defaults."""
    # Arrange / Act
    link = ParsedLink(
        title="Getting Started",
        url="https://example.com/start",
        line_number=5,
    )

    # Assert
    assert link.title == "Getting Started"
    assert link.url == "https://example.com/start"
    assert link.description is None
    assert link.line_number == 5
    assert link.is_valid_url is True


@pytest.mark.unit
def test_parsed_link_with_description():
    """Verify optional description field is stored."""
    link = ParsedLink(
        title="API Ref",
        url="https://example.com/api",
        description="Complete API reference documentation",
        line_number=10,
    )

    assert link.description == "Complete API reference documentation"


@pytest.mark.unit
def test_parsed_link_rejects_invalid_line_number():
    """Verify line_number enforces ge=1 constraint."""
    with pytest.raises(ValidationError):
        ParsedLink(title="Test", url="https://example.com", line_number=0)


# ── ParsedSection ────────────────────────────────────────────────────


@pytest.mark.unit
def test_parsed_section_creation():
    """Verify construction with required fields and defaults."""
    # Arrange / Act
    section = ParsedSection(name="Docs", line_number=4)

    # Assert
    assert section.name == "Docs"
    assert section.links == []
    assert section.raw_content == ""
    assert section.line_number == 4
    assert section.canonical_name is None
    assert section.estimated_tokens == 0


@pytest.mark.unit
def test_parsed_section_link_count_empty():
    """Verify link_count returns 0 when no links present."""
    section = ParsedSection(name="Docs", line_number=4)

    assert section.link_count == 0


@pytest.mark.unit
def test_parsed_section_link_count_with_links():
    """Verify link_count returns correct count with multiple links."""
    links = [
        ParsedLink(title=f"Link {i}", url=f"https://example.com/{i}", line_number=i)
        for i in range(1, 4)
    ]
    section = ParsedSection(name="Docs", links=links, line_number=4)

    assert section.link_count == 3


@pytest.mark.unit
def test_parsed_section_has_code_examples_true():
    """Verify has_code_examples detects fenced code blocks."""
    section = ParsedSection(
        name="Examples",
        raw_content='```python\nprint("hello")\n```',
        line_number=10,
    )

    assert section.has_code_examples is True


@pytest.mark.unit
def test_parsed_section_has_code_examples_false():
    """Verify has_code_examples returns False without code blocks."""
    section = ParsedSection(
        name="Docs",
        raw_content="Just some plain text content here.",
        line_number=4,
    )

    assert section.has_code_examples is False


# ── ParsedLlmsTxt ───────────────────────────────────────────────────


@pytest.mark.unit
def test_parsed_llms_txt_creation_minimal():
    """Verify construction with all defaults (empty/broken document)."""
    # Arrange / Act
    doc = ParsedLlmsTxt()

    # Assert
    assert doc.title is None
    assert doc.title_line is None
    assert doc.blockquote is None
    assert doc.sections == []
    assert doc.raw_content == ""
    assert doc.source_filename == "llms.txt"
    assert isinstance(doc.parsed_at, datetime)


@pytest.mark.unit
def test_parsed_llms_txt_creation_full():
    """Verify full construction with nested models."""
    # Arrange
    bq = ParsedBlockquote(text="Stripe API docs", line_number=2)
    link = ParsedLink(
        title="Auth Guide",
        url="https://stripe.com/docs/auth",
        description="Authentication guide",
        line_number=5,
    )
    section = ParsedSection(name="Docs", links=[link], line_number=4)
    raw = "# Stripe Documentation\n> Stripe API docs\n\n## Docs\n"

    # Act
    doc = ParsedLlmsTxt(
        title="Stripe Documentation",
        title_line=1,
        blockquote=bq,
        sections=[section],
        raw_content=raw,
        source_filename="stripe-llms.txt",
    )

    # Assert
    assert doc.title == "Stripe Documentation"
    assert doc.title_line == 1
    assert doc.blockquote is bq
    assert len(doc.sections) == 1
    assert doc.sections[0].name == "Docs"
    assert doc.source_filename == "stripe-llms.txt"


@pytest.mark.unit
def test_parsed_llms_txt_section_count():
    """Exit Criterion 4: section_count returns len(sections)."""
    doc_empty = ParsedLlmsTxt()
    doc_three = ParsedLlmsTxt(
        sections=[
            ParsedSection(name="A", line_number=1),
            ParsedSection(name="B", line_number=5),
            ParsedSection(name="C", line_number=10),
        ]
    )

    assert doc_empty.section_count == 0
    assert doc_three.section_count == 3


@pytest.mark.unit
def test_parsed_llms_txt_total_links():
    """Exit Criterion 4: total_links sums link_count across all sections."""
    # Arrange — section with 2 links, section with 0, section with 3
    links_a = [
        ParsedLink(title=f"L{i}", url=f"https://a.com/{i}", line_number=i)
        for i in range(1, 3)
    ]
    links_c = [
        ParsedLink(title=f"L{i}", url=f"https://c.com/{i}", line_number=i)
        for i in range(1, 4)
    ]
    doc = ParsedLlmsTxt(
        sections=[
            ParsedSection(name="A", links=links_a, line_number=1),
            ParsedSection(name="B", line_number=5),
            ParsedSection(name="C", links=links_c, line_number=10),
        ]
    )

    # Act / Assert
    assert doc.total_links == 5


@pytest.mark.unit
def test_parsed_llms_txt_estimated_tokens():
    """Exit Criterion 4: estimated_tokens returns len(raw_content) // 4."""
    # 100 chars → 25 tokens
    raw = "x" * 100
    doc = ParsedLlmsTxt(raw_content=raw)

    assert doc.estimated_tokens == 25


@pytest.mark.unit
def test_parsed_llms_txt_has_blockquote():
    """Exit Criterion 4: has_blockquote reflects blockquote presence."""
    doc_without = ParsedLlmsTxt()
    doc_with = ParsedLlmsTxt(
        blockquote=ParsedBlockquote(text="Description", line_number=2)
    )

    assert doc_without.has_blockquote is False
    assert doc_with.has_blockquote is True


@pytest.mark.unit
def test_parsed_llms_txt_section_names():
    """Exit Criterion 4: section_names returns names in document order."""
    doc = ParsedLlmsTxt(
        sections=[
            ParsedSection(name="Docs", line_number=4),
            ParsedSection(name="API Reference", line_number=10),
            ParsedSection(name="Examples", line_number=20),
        ]
    )

    assert doc.section_names == ["Docs", "API Reference", "Examples"]


@pytest.mark.unit
def test_parsed_llms_txt_section_names_empty():
    """Verify section_names returns empty list when no sections."""
    doc = ParsedLlmsTxt()

    assert doc.section_names == []


@pytest.mark.unit
def test_parsed_models_importable_from_schema():
    """Exit Criterion 2: All parsed models importable from public API."""
    from docstratum import schema

    assert schema.ParsedBlockquote is ParsedBlockquote
    assert schema.ParsedLink is ParsedLink
    assert schema.ParsedSection is ParsedSection
    assert schema.ParsedLlmsTxt is ParsedLlmsTxt
