"""Tests for synthetic parser fixtures (v0.2.2a).

End-to-end parser pipeline tests for 5 hand-crafted fixtures at
conformance levels L0 through L4. Each test calls the full pipeline:
read_file → tokenize → populate → classify_document → match_canonical_sections
→ extract_metadata.

Acceptance criteria: all 5 fixtures parse correctly, no external network
access required, assertions verify expected model fields at each tier.

See:
    - docs/design/03-parser/RR-SPEC-v0.2.2a-synthetic-test-fixtures.md
    - docs/design/00-meta/RR-META-testing-standards.md
"""

import re
from pathlib import Path

from docstratum.parser import (
    classify_document,
    extract_metadata,
    match_canonical_sections,
    populate,
    read_file,
    tokenize,
)
from docstratum.schema.classification import DocumentType

# ── Fixture directory ────────────────────────────────────────────────────
SYNTHETIC_DIR = Path(__file__).parent / "fixtures" / "parser" / "synthetic"

# ── Frontmatter stripping ────────────────────────────────────────────────
_FRONTMATTER_RE = re.compile(r"\A\s*---\n.*?\n---\n?", re.DOTALL)


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter block from content for tokenization.

    The tokenizer does not understand YAML frontmatter delimiters.
    This helper strips the leading ``---`` block so that the
    tokenizer receives only the Markdown body.
    """
    return _FRONTMATTER_RE.sub("", content, count=1)


class TestSyntheticFixtures:
    """End-to-end parser pipeline tests for synthetic fixtures (v0.2.2a)."""

    def test_parse_L0_fail_empty_file_returns_empty_model(self):  # noqa: N802
        """L0: empty file produces mostly-empty ParsedLlmsTxt.

        An empty file (0 bytes) should yield title=None, no sections,
        no blockquote, estimated_tokens=0, and classification UNKNOWN.

        Grounding: v0.2.2a §2.1 (L0 — Fail Fixture)
        """
        # Arrange
        fixture_path = SYNTHETIC_DIR / "L0_fail.txt"

        # Act — full pipeline on empty file
        content, file_meta = read_file(str(fixture_path))
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="L0_fail.txt")
        classification = classify_document(doc, file_meta)
        match_canonical_sections(doc)
        metadata = extract_metadata(content)

        # Assert — empty model
        assert doc.title is None
        assert doc.title_line is None
        assert doc.blockquote is None
        assert doc.sections == []
        assert doc.estimated_tokens == 0
        assert classification.document_type == DocumentType.UNKNOWN
        assert metadata is None

    def test_parse_L1_minimal_returns_title_and_one_section(self):  # noqa: N802
        """L1: minimal file produces title + 1 section + 1 link.

        The section "Docs" should alias-match to canonical name
        "Master Index" via SECTION_NAME_ALIASES.

        Grounding: v0.2.2a §2.2 (L1 — Minimal Fixture)
        """
        # Arrange
        fixture_path = SYNTHETIC_DIR / "L1_minimal.txt"

        # Act — full pipeline
        content, file_meta = read_file(str(fixture_path))
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="L1_minimal.txt")
        classification = classify_document(doc, file_meta)
        match_canonical_sections(doc)
        metadata = extract_metadata(content)

        # Assert — title
        assert doc.title == "My Project"
        assert doc.title_line == 1

        # Assert — no blockquote
        assert doc.blockquote is None

        # Assert — 1 section with alias match
        assert len(doc.sections) == 1
        assert doc.sections[0].name == "Docs"
        assert doc.sections[0].canonical_name == "Master Index"

        # Assert — 1 link
        assert len(doc.sections[0].links) == 1
        assert doc.sections[0].links[0].title == "Home"
        assert doc.sections[0].links[0].url == "https://example.com"
        assert doc.sections[0].links[0].description is None

        # Assert — tokens > 0
        assert doc.estimated_tokens > 0

        # Assert — classification and metadata
        assert classification.document_type == DocumentType.TYPE_1_INDEX
        assert metadata is None

    def test_parse_L2_content_returns_blockquote_and_three_sections(self):  # noqa: N802
        """L2: well-structured file with blockquote, 3 sections, 7 described links.

        All links should have descriptions. Canonical section names should
        match directly (Getting Started, API Reference, Examples).

        Grounding: v0.2.2a §2.3 (L2 — Content Quality Fixture)
        """
        # Arrange
        fixture_path = SYNTHETIC_DIR / "L2_content.txt"

        # Act — full pipeline
        content, file_meta = read_file(str(fixture_path))
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="L2_content.txt")
        classification = classify_document(doc, file_meta)
        match_canonical_sections(doc)
        metadata = extract_metadata(content)

        # Assert — title
        assert doc.title == "Acme Framework"

        # Assert — blockquote present
        assert doc.blockquote is not None
        assert "modern web development toolkit" in doc.blockquote.text

        # Assert — 3 sections
        assert len(doc.sections) == 3
        assert doc.sections[0].name == "Getting Started"
        assert doc.sections[0].canonical_name == "Getting Started"
        assert doc.sections[1].name == "API Reference"
        assert doc.sections[1].canonical_name == "API Reference"
        assert doc.sections[2].name == "Examples"
        assert doc.sections[2].canonical_name == "Examples"

        # Assert — link counts per section
        assert len(doc.sections[0].links) == 2
        assert len(doc.sections[1].links) == 3
        assert len(doc.sections[2].links) == 2

        # Assert — total 7 links, all with descriptions
        assert doc.total_links == 7
        for section in doc.sections:
            for link in section.links:
                assert (
                    link.description is not None
                ), f"Link '{link.title}' in '{section.name}' missing description"

        # Assert — classification and metadata
        assert classification.document_type == DocumentType.TYPE_1_INDEX
        assert metadata is None

    def test_parse_L3_best_practices_returns_seven_canonical_sections(  # noqa: N802
        self,
    ):
        """L3: best-practices file with 7 sections, all canonically named.

        All section names should resolve to canonical names. All links
        should have descriptions. Blockquote should be present.

        Grounding: v0.2.2a §2.4 (L3 — Best Practices Fixture)
        """
        # Arrange
        fixture_path = SYNTHETIC_DIR / "L3_best_practices.txt"

        # Act — full pipeline
        content, file_meta = read_file(str(fixture_path))
        tokens = tokenize(content)
        doc = populate(
            tokens, raw_content=content, source_filename="L3_best_practices.txt"
        )
        classification = classify_document(doc, file_meta)
        match_canonical_sections(doc)
        metadata = extract_metadata(content)

        # Assert — title
        assert doc.title is not None
        assert "Acme Framework" in doc.title

        # Assert — blockquote present
        assert doc.blockquote is not None

        # Assert — 7 sections
        assert len(doc.sections) == 7

        # Assert — expected canonical names
        expected_canonical = [
            "Master Index",
            "LLM Instructions",
            "Getting Started",
            "API Reference",
            "Examples",
            "Configuration",
            "Troubleshooting",
        ]
        actual_canonical = [s.canonical_name for s in doc.sections]
        assert actual_canonical == expected_canonical

        # Assert — all links have descriptions
        for section in doc.sections:
            for link in section.links:
                assert (
                    link.description is not None
                ), f"Link '{link.title}' in '{section.name}' missing description"

        # Assert — classification and metadata
        assert classification.document_type == DocumentType.TYPE_1_INDEX
        assert metadata is None

    def test_parse_L4_extended_returns_metadata_with_seven_fields(self):  # noqa: N802
        """L4: DocStratum-extended file with YAML frontmatter and 5 sections.

        Metadata should be extracted with all 7 recognized fields.
        generator should be "docstratum", token_budget_tier "comprehensive".

        Grounding: v0.2.2a §2.5 (L4 — Extended Fixture)
        """
        # Arrange
        fixture_path = SYNTHETIC_DIR / "L4_extended.txt"

        # Act — full pipeline (strip frontmatter for tokenizer)
        content, file_meta = read_file(str(fixture_path))
        body = _strip_frontmatter(content)
        tokens = tokenize(body)
        doc = populate(tokens, raw_content=content, source_filename="L4_extended.txt")
        classification = classify_document(doc, file_meta)
        match_canonical_sections(doc)
        metadata = extract_metadata(content)

        # Assert — title
        assert doc.title is not None
        assert "Acme Framework" in doc.title

        # Assert — blockquote present
        assert doc.blockquote is not None

        # Assert — 5 sections
        assert len(doc.sections) == 5

        # Assert — canonical section matches
        expected_canonical = [
            "Master Index",
            "Getting Started",
            "API Reference",
            "Examples",
            "FAQ",
        ]
        actual_canonical = [s.canonical_name for s in doc.sections]
        assert actual_canonical == expected_canonical

        # Assert — metadata extracted with all 7 fields
        assert metadata is not None
        assert metadata.schema_version == "0.2.0"
        assert metadata.site_name == "Acme Framework"
        assert metadata.site_url == "https://acme.dev"
        assert metadata.last_updated == "2026-01-15"
        assert metadata.generator == "docstratum"
        assert metadata.docstratum_version == "0.2.2"
        assert metadata.token_budget_tier == "comprehensive"

        # Assert — classification
        assert classification.document_type == DocumentType.TYPE_1_INDEX
