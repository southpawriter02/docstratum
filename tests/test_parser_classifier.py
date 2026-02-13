"""Tests for the parser classifier module (v0.2.1a/b).

Tests cover the document type classification decision tree: null byte
detection, empty/unparseable files, filename conventions, size threshold,
H1 count, link density fallback, size tier assignment, and full
DocumentClassification assembly.
See RR-META-testing-standards for naming conventions and fixture patterns.
"""

import copy

from docstratum.parser.classifier import (
    assign_size_tier,
    classify_document,
    classify_document_type,
)
from docstratum.parser.io import FileMetadata
from docstratum.schema.classification import DocumentType, SizeTier
from docstratum.schema.parsed import ParsedLink, ParsedLlmsTxt, ParsedSection

# ── Helpers ──────────────────────────────────────────────────────────


def _make_doc(
    *,
    title: str | None = "Test",
    sections: list[ParsedSection] | None = None,
    raw_content: str = "",
    source_filename: str = "llms.txt",
) -> ParsedLlmsTxt:
    """Create a ParsedLlmsTxt with sensible defaults for testing."""
    doc = ParsedLlmsTxt()
    doc.title = title
    doc.sections = sections if sections is not None else []
    doc.raw_content = raw_content
    doc.source_filename = source_filename
    return doc


def _make_meta(
    *,
    byte_count: int = 100,
    has_null_bytes: bool = False,
) -> FileMetadata:
    """Create a FileMetadata with sensible defaults for testing."""
    return FileMetadata(byte_count=byte_count, has_null_bytes=has_null_bytes)


def _make_section(
    name: str = "Docs",
    *,
    links: list[ParsedLink] | None = None,
    raw_content: str = "",
    line_number: int = 1,
) -> ParsedSection:
    """Create a ParsedSection with optional links and raw_content."""
    section = ParsedSection(name=name, line_number=line_number)
    section.links = links if links is not None else []
    section.raw_content = raw_content
    return section


def _make_link(
    title: str = "Link",
    url: str = "https://example.com",
    line_number: int = 1,
) -> ParsedLink:
    """Create a minimal ParsedLink."""
    return ParsedLink(title=title, url=url, line_number=line_number)


# ── UNKNOWN Classification ──────────────────────────────────────────


class TestClassifyUnknown:
    """Tests for UNKNOWN classification (steps 1-2 of decision tree)."""

    def test_classify_empty_file(self):
        """Verify empty file (no title, no sections) returns UNKNOWN."""
        # Arrange
        doc = _make_doc(title=None, sections=[])
        meta = _make_meta(byte_count=0)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.UNKNOWN

    def test_classify_null_bytes(self):
        """Verify file with null bytes returns UNKNOWN regardless of content."""
        # Arrange
        doc = _make_doc(title="Title", sections=[_make_section()])
        meta = _make_meta(has_null_bytes=True, byte_count=500)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.UNKNOWN


# ── TYPE_1_INDEX Classification ─────────────────────────────────────


class TestClassifyType1:
    """Tests for TYPE_1_INDEX classification."""

    def test_classify_type1_minimal(self):
        """Verify minimal doc with 1 H1, 1 section, 1 link returns TYPE_1_INDEX."""
        # Arrange
        section = _make_section(links=[_make_link()])
        doc = _make_doc(
            title="My App",
            sections=[section],
            raw_content="# My App\n## Docs\n- [Link](https://example.com)\n",
        )
        meta = _make_meta(byte_count=200)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_1_INDEX

    def test_classify_type1_large(self):
        """Verify large doc under threshold with 1 H1 returns TYPE_1_INDEX."""
        # Arrange
        sections = [
            _make_section(f"Section {i}", links=[_make_link()]) for i in range(20)
        ]
        doc = _make_doc(
            title="Big Index",
            sections=sections,
            raw_content="# Big Index\n" + "## Section\n- [L](https://x.com)\n" * 20,
        )
        meta = _make_meta(byte_count=200_000)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_1_INDEX

    def test_classify_no_links_sparse(self):
        """Verify doc with 1 section, 0 links, no prose returns TYPE_1_INDEX."""
        # Arrange
        section = _make_section(raw_content="")
        doc = _make_doc(
            title="Sparse",
            sections=[section],
            raw_content="# Sparse\n## Docs\n",
        )
        meta = _make_meta(byte_count=50)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_1_INDEX


# ── TYPE_2_FULL Classification ──────────────────────────────────────


class TestClassifyType2:
    """Tests for TYPE_2_FULL classification."""

    def test_classify_type2_by_size(self):
        """Verify file > TYPE_BOUNDARY_BYTES returns TYPE_2_FULL."""
        # Arrange
        doc = _make_doc(
            title="Big Doc",
            sections=[_make_section()],
            raw_content="# Big Doc\n## Docs\n",
        )
        meta = _make_meta(byte_count=300_000)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_2_FULL

    def test_classify_type2_by_h1_count(self):
        """Verify file with 3 H1 headings returns TYPE_2_FULL."""
        # Arrange
        raw = "# Title One\n## Docs\n# Title Two\n## More\n# Title Three\n"
        doc = _make_doc(
            title="Title One",
            sections=[_make_section()],
            raw_content=raw,
        )
        meta = _make_meta(byte_count=500)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_2_FULL

    def test_classify_type2_by_filename(self):
        """Verify filename 'llms-full.txt' returns TYPE_2_FULL regardless of size."""
        # Arrange
        doc = _make_doc(
            title="Small",
            sections=[_make_section()],
            raw_content="# Small\n## Docs\n",
            source_filename="llms-full.txt",
        )
        meta = _make_meta(byte_count=50)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_2_FULL

    def test_classify_boundary_exact(self):
        """Verify byte_count=256,000 exactly returns TYPE_1_INDEX (<=)."""
        # Arrange
        doc = _make_doc(
            title="Boundary",
            sections=[_make_section(links=[_make_link()])],
            raw_content="# Boundary\n## Docs\n- [L](https://x.com)\n",
        )
        meta = _make_meta(byte_count=256_000)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_1_INDEX

    def test_classify_boundary_plus_one(self):
        """Verify byte_count=256,001 returns TYPE_2_FULL (>)."""
        # Arrange
        doc = _make_doc(
            title="Over",
            sections=[_make_section()],
            raw_content="# Over\n## Docs\n",
        )
        meta = _make_meta(byte_count=256_001)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_2_FULL


# ── TYPE_4_INSTRUCTIONS Classification ──────────────────────────────


class TestClassifyType4:
    """Tests for TYPE_4_INSTRUCTIONS classification."""

    def test_classify_type4_by_filename(self):
        """Verify filename 'llms-instructions.txt' returns TYPE_4_INSTRUCTIONS."""
        # Arrange
        doc = _make_doc(
            title="Instructions",
            sections=[_make_section()],
            raw_content="# Instructions\n## Setup\n",
            source_filename="llms-instructions.txt",
        )
        meta = _make_meta(byte_count=100)

        # Act
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_4_INSTRUCTIONS


# ── H1 Counting ────────────────────────────────────────────────────


class TestH1Counting:
    """Tests for _count_h1_headings helper via classify_document_type."""

    def test_h1_count_with_code_blocks(self):
        """Verify H1 inside code fence is NOT counted."""
        # Arrange -- one real H1, one inside code fence
        raw = "# Real Title\n```\n# Not a Title\n```\n## Section\n"
        doc = _make_doc(
            title="Real Title",
            sections=[_make_section(links=[_make_link()])],
            raw_content=raw,
        )
        meta = _make_meta(byte_count=100)

        # Act -- with only 1 real H1, should be TYPE_1_INDEX (not TYPE_2_FULL)
        result = classify_document_type(doc, meta)

        # Assert
        assert result == DocumentType.TYPE_1_INDEX

    def test_h1_count_ignores_h2(self):
        """Verify '## Section' is NOT counted as H1."""
        # Arrange -- H2 lines should not trigger >1 H1 check
        raw = "# Title\n## Section One\n## Section Two\n## Section Three\n"
        doc = _make_doc(
            title="Title",
            sections=[
                _make_section("Section One", links=[_make_link()]),
                _make_section("Section Two"),
                _make_section("Section Three"),
            ],
            raw_content=raw,
        )
        meta = _make_meta(byte_count=100)

        # Act
        result = classify_document_type(doc, meta)

        # Assert -- should NOT be TYPE_2_FULL despite many headings
        assert result == DocumentType.TYPE_1_INDEX


# ── Immutability ────────────────────────────────────────────────────


class TestImmutability:
    """Tests that classify_document_type does not modify inputs."""

    def test_does_not_modify_doc(self):
        """Verify doc instance is unchanged after classification."""
        # Arrange
        section = _make_section(links=[_make_link()])
        doc = _make_doc(
            title="Immutable",
            sections=[section],
            raw_content="# Immutable\n## Docs\n- [L](https://x.com)\n",
        )
        doc_copy = copy.deepcopy(doc)
        meta = _make_meta(byte_count=100)

        # Act
        classify_document_type(doc, meta)

        # Assert -- all fields should be identical
        assert doc.title == doc_copy.title
        assert len(doc.sections) == len(doc_copy.sections)
        assert doc.raw_content == doc_copy.raw_content
        assert doc.source_filename == doc_copy.source_filename


# ── Size Tier Assignment (v0.2.1b) ──────────────────────────────────


class TestSizeTierAssignment:
    """Tests for assign_size_tier (v0.2.1b)."""

    def test_tier_minimal_zero(self):
        """Verify 0 tokens -> MINIMAL."""
        assert assign_size_tier(0) == SizeTier.MINIMAL

    def test_tier_minimal_1499(self):
        """Verify 1,499 tokens -> MINIMAL (< 1,500)."""
        assert assign_size_tier(1_499) == SizeTier.MINIMAL

    def test_tier_standard_1500(self):
        """Verify 1,500 tokens -> STANDARD (inclusive lower bound)."""
        assert assign_size_tier(1_500) == SizeTier.STANDARD

    def test_tier_standard_4499(self):
        """Verify 4,499 tokens -> STANDARD (< 4,500)."""
        assert assign_size_tier(4_499) == SizeTier.STANDARD

    def test_tier_comprehensive_4500(self):
        """Verify 4,500 tokens -> COMPREHENSIVE (inclusive lower bound)."""
        assert assign_size_tier(4_500) == SizeTier.COMPREHENSIVE

    def test_tier_comprehensive_11999(self):
        """Verify 11,999 tokens -> COMPREHENSIVE (< 12,000)."""
        assert assign_size_tier(11_999) == SizeTier.COMPREHENSIVE

    def test_tier_full_12000(self):
        """Verify 12,000 tokens -> FULL (inclusive lower bound)."""
        assert assign_size_tier(12_000) == SizeTier.FULL

    def test_tier_full_49999(self):
        """Verify 49,999 tokens -> FULL (< 50,000)."""
        assert assign_size_tier(49_999) == SizeTier.FULL

    def test_tier_oversized_50000(self):
        """Verify 50,000 tokens -> OVERSIZED (inclusive lower bound)."""
        assert assign_size_tier(50_000) == SizeTier.OVERSIZED

    def test_tier_oversized_very_large(self):
        """Verify 1,000,000 tokens -> OVERSIZED."""
        assert assign_size_tier(1_000_000) == SizeTier.OVERSIZED


# ── DocumentClassification Assembly (v0.2.1b) ──────────────────────


class TestClassifyDocument:
    """Tests for classify_document (v0.2.1b)."""

    def test_classify_document_all_fields(self):
        """Verify all 6 DocumentClassification fields are populated."""
        # Arrange
        section = _make_section(links=[_make_link()])
        doc = _make_doc(
            title="My App",
            sections=[section],
            raw_content="# My App\n## Docs\n- [L](https://x.com)\n",
            source_filename="llms.txt",
        )
        meta = _make_meta(byte_count=5_000)

        # Act
        result = classify_document(doc, meta)

        # Assert
        assert result.document_type == DocumentType.TYPE_1_INDEX
        assert result.size_bytes == 5_000
        assert result.estimated_tokens == doc.estimated_tokens
        assert result.size_tier is not None
        assert result.filename == "llms.txt"
        assert result.classified_at is not None

    def test_classify_document_uses_parser_tokens(self):
        """Verify estimated_tokens matches doc.estimated_tokens."""
        # Arrange
        raw = "a" * 400  # 400 chars -> 100 tokens via // 4
        doc = _make_doc(
            title="Tokens",
            sections=[_make_section(raw_content=raw)],
            raw_content="# Tokens\n" + raw,
        )
        meta = _make_meta(byte_count=500)

        # Act
        result = classify_document(doc, meta)

        # Assert
        assert result.estimated_tokens == doc.estimated_tokens

    def test_classify_document_uses_file_bytes(self):
        """Verify size_bytes comes from file_meta.byte_count."""
        # Arrange
        doc = _make_doc(
            title="Bytes",
            sections=[_make_section(links=[_make_link()])],
            raw_content="# Bytes\n## Docs\n- [L](https://x.com)\n",
        )
        meta = _make_meta(byte_count=5_000)

        # Act
        result = classify_document(doc, meta)

        # Assert
        assert result.size_bytes == 5_000

    def test_classify_document_sets_filename(self):
        """Verify filename comes from doc.source_filename."""
        # Arrange
        doc = _make_doc(
            title="Named",
            sections=[_make_section(links=[_make_link()])],
            raw_content="# Named\n## Docs\n- [L](https://x.com)\n",
            source_filename="test.txt",
        )
        meta = _make_meta(byte_count=100)

        # Act
        result = classify_document(doc, meta)

        # Assert
        assert result.filename == "test.txt"
