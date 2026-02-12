"""Tests for the parser populator module (v0.2.0c/d).

Tests cover the 5-phase population walk: H1 extraction, blockquote
collection, body consumption, section/link building, assembly, and
token estimation.
See RR-META-testing-standards for naming conventions and fixture patterns.
"""

from datetime import datetime

from docstratum.parser.populator import populate
from docstratum.parser.tokens import Token, TokenType

# ── Helpers ──────────────────────────────────────────────────────────


def _tok(token_type: TokenType, line: int, raw: str) -> Token:
    """Shorthand for creating Token instances in tests."""
    return Token(token_type=token_type, line_number=line, raw_text=raw)


# ── Empty & Minimal ─────────────────────────────────────────────────


class TestEmptyAndMinimal:
    """Tests for empty/minimal token streams."""

    def test_empty_tokens(self):
        """Verify empty token list produces default ParsedLlmsTxt."""
        # Act
        doc = populate([])

        # Assert
        assert doc.title is None
        assert doc.sections == []

    def test_h1_only(self):
        """Verify single H1 token produces title with no sections."""
        # Arrange
        tokens = [_tok(TokenType.H1, 1, "# Title")]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.title == "Title"
        assert doc.title_line == 1
        assert doc.sections == []
        assert doc.blockquote is None


# ── Blockquote ───────────────────────────────────────────────────────


class TestBlockquote:
    """Tests for blockquote extraction (Phase 2)."""

    def test_h1_and_blockquote(self):
        """Verify H1 + BLANK + BLOCKQUOTE sets blockquote.text."""
        # Arrange
        tokens = [
            _tok(TokenType.H1, 1, "# Title"),
            _tok(TokenType.BLANK, 2, ""),
            _tok(TokenType.BLOCKQUOTE, 3, "> A description"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.title == "Title"
        assert doc.blockquote is not None
        assert doc.blockquote.text == "A description"

    def test_multiline_blockquote(self):
        """Verify consecutive BLOCKQUOTE tokens join with newline."""
        # Arrange
        tokens = [
            _tok(TokenType.H1, 1, "# Title"),
            _tok(TokenType.BLOCKQUOTE, 2, "> Line one"),
            _tok(TokenType.BLOCKQUOTE, 3, "> Line two"),
            _tok(TokenType.BLOCKQUOTE, 4, "> Line three"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.blockquote is not None
        assert doc.blockquote.text == "Line one\nLine two\nLine three"

    def test_blockquote_raw_preserved(self):
        """Verify blockquote.raw preserves original '> ' prefix."""
        # Arrange
        tokens = [
            _tok(TokenType.H1, 1, "# Title"),
            _tok(TokenType.BLOCKQUOTE, 2, "> Hello"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.blockquote is not None
        assert doc.blockquote.raw == "> Hello"
        assert doc.blockquote.text == "Hello"

    def test_bare_blockquote(self):
        """Verify bare '>' produces empty text (edge case C2)."""
        # Arrange
        tokens = [
            _tok(TokenType.H1, 1, "# Title"),
            _tok(TokenType.BLOCKQUOTE, 2, ">"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.blockquote is not None
        assert doc.blockquote.text == ""

    def test_no_blockquote(self):
        """Verify missing blockquote sets blockquote=None."""
        # Arrange
        tokens = [
            _tok(TokenType.H1, 1, "# Title"),
            _tok(TokenType.BLANK, 2, ""),
            _tok(TokenType.H2, 3, "## Docs"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.blockquote is None


# ── Sections ─────────────────────────────────────────────────────────


class TestSections:
    """Tests for section building (Phase 4)."""

    def test_single_section(self):
        """Verify H2 creates a section with correct name and line_number."""
        # Arrange
        tokens = [
            _tok(TokenType.H1, 1, "# Title"),
            _tok(TokenType.H2, 2, "## Docs"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert len(doc.sections) == 1
        assert doc.sections[0].name == "Docs"
        assert doc.sections[0].line_number == 2

    def test_multiple_sections(self):
        """Verify multiple H2 tokens produce multiple sections."""
        # Arrange
        tokens = [
            _tok(TokenType.H1, 1, "# Title"),
            _tok(TokenType.H2, 2, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 3, "- [A](https://a.com): A desc"),
            _tok(TokenType.H2, 4, "## API"),
            _tok(TokenType.LINK_ENTRY, 5, "- [B](https://b.com): B desc"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert len(doc.sections) == 2
        assert doc.sections[0].name == "Docs"
        assert len(doc.sections[0].links) == 1
        assert doc.sections[1].name == "API"
        assert len(doc.sections[1].links) == 1

    def test_empty_section(self):
        """Verify H2 followed by H2 creates first section with empty links."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## First"),
            _tok(TokenType.H2, 2, "## Second"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert len(doc.sections) == 2
        assert doc.sections[0].links == []
        assert doc.sections[0].raw_content == ""

    def test_body_content_consumed(self):
        """Verify body TEXT tokens before H2 are consumed silently."""
        # Arrange
        tokens = [
            _tok(TokenType.H1, 1, "# Title"),
            _tok(TokenType.TEXT, 2, "Some body text"),
            _tok(TokenType.TEXT, 3, "More body text"),
            _tok(TokenType.H2, 4, "## Docs"),
        ]

        # Act
        doc = populate(tokens)

        # Assert -- body text consumed, 1 section created
        assert len(doc.sections) == 1
        assert doc.sections[0].name == "Docs"

    def test_h3_in_section(self):
        """Verify H3_PLUS tokens go into section raw_content, not sections list."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.H3_PLUS, 2, "### Subsection"),
            _tok(TokenType.LINK_ENTRY, 3, "- [A](https://a.com): Desc"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert len(doc.sections) == 1
        assert "### Subsection" in doc.sections[0].raw_content
        assert len(doc.sections[0].links) == 1


# ── Links ────────────────────────────────────────────────────────────


class TestLinks:
    """Tests for link entry parsing within sections."""

    def test_link_with_description(self):
        """Verify link with ': desc' extracts title, url, and description."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [Title](https://url.com): A description"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        link = doc.sections[0].links[0]
        assert link.title == "Title"
        assert link.url == "https://url.com"
        assert link.description == "A description"

    def test_link_without_description(self):
        """Verify link without description has description=None."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [Title](https://url.com)"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].links[0].description is None

    def test_link_empty_url(self):
        """Verify empty URL sets url='' and is_valid_url=False."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [Title]()"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        link = doc.sections[0].links[0]
        assert link.url == ""
        assert link.is_valid_url is False

    def test_link_empty_title(self):
        """Verify empty title sets title=''."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [](https://url.com)"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].links[0].title == ""

    def test_malformed_link_becomes_text(self):
        """Verify malformed link entry (regex fails) is not added to links."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [Title](url"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].links == []
        assert "- [Title](url" in doc.sections[0].raw_content

    def test_code_fence_suppresses_links(self):
        """Verify LINK_ENTRY inside code fence is not parsed as link."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.CODE_FENCE, 2, "```"),
            _tok(TokenType.LINK_ENTRY, 3, "- [F](https://url.com)"),
            _tok(TokenType.CODE_FENCE, 4, "```"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].links == []


# ── URL Validation ───────────────────────────────────────────────────


class TestUrlValidation:
    """Tests for _is_syntactically_valid_url via link parsing."""

    def test_url_validation_absolute(self):
        """Verify https:// URL is valid."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [T](https://x.com)"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].links[0].is_valid_url is True

    def test_url_validation_relative(self):
        """Verify /docs/page relative URL is valid."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [T](/docs/page)"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].links[0].is_valid_url is True

    def test_url_validation_dotrelative(self):
        """Verify ./page.md relative URL is valid."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [T](./page.md)"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].links[0].is_valid_url is True

    def test_url_validation_invalid(self):
        """Verify 'not a url' is invalid."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [T](not a url)"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].links[0].is_valid_url is False

    def test_url_validation_empty(self):
        """Verify empty string URL is invalid."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 2, "- [T]()"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].links[0].is_valid_url is False


# ── Assembly ─────────────────────────────────────────────────────────


class TestAssembly:
    """Tests for final assembly (Phase 5)."""

    def test_source_filename_set(self):
        """Verify source_filename is set from parameter."""
        # Act
        doc = populate([], source_filename="test.txt")

        # Assert
        assert doc.source_filename == "test.txt"

    def test_raw_content_passthrough(self):
        """Verify raw_content is passed through unchanged."""
        # Act
        doc = populate([], raw_content="# Title\n> Desc\n")

        # Assert
        assert doc.raw_content == "# Title\n> Desc\n"

    def test_parsed_at_set(self):
        """Verify parsed_at is a datetime instance."""
        # Act
        doc = populate([])

        # Assert
        assert isinstance(doc.parsed_at, datetime)


# ── Token Estimation (v0.2.0d) ──────────────────────────────────────


class TestTokenEstimation:
    """Tests for per-section token estimation (v0.2.0d)."""

    def test_section_token_estimate_empty(self):
        """Verify empty section raw_content produces estimated_tokens=0."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## First"),
            _tok(TokenType.H2, 2, "## Second"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].estimated_tokens == 0

    def test_section_token_estimate_short(self):
        """Verify 11 chars produces estimated_tokens=2 (11 // 4 = 2)."""
        # Arrange -- "Hello world" is 11 chars
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.TEXT, 2, "Hello world"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].estimated_tokens == 2

    def test_section_token_estimate_1000_chars(self):
        """Verify 1000 chars produces estimated_tokens=250."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.TEXT, 2, "a" * 1000),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].estimated_tokens == 250

    def test_section_token_estimate_rounddown(self):
        """Verify 7 chars floors to estimated_tokens=1 (7 // 4 = 1)."""
        # Arrange -- "abcdefg" is 7 chars
        tokens = [
            _tok(TokenType.H2, 1, "## Docs"),
            _tok(TokenType.TEXT, 2, "abcdefg"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert doc.sections[0].estimated_tokens == 1

    def test_document_tokens_gte_section_sum(self):
        """Verify doc.estimated_tokens >= sum of section estimates."""
        # Arrange
        raw = "# Title\n> Desc\n## Docs\n- [A](https://a.com): A\n## API\n- [B](https://b.com): B\n"
        tokens = [
            _tok(TokenType.H1, 1, "# Title"),
            _tok(TokenType.BLOCKQUOTE, 2, "> Desc"),
            _tok(TokenType.H2, 3, "## Docs"),
            _tok(TokenType.LINK_ENTRY, 4, "- [A](https://a.com): A"),
            _tok(TokenType.H2, 5, "## API"),
            _tok(TokenType.LINK_ENTRY, 6, "- [B](https://b.com): B"),
        ]

        # Act
        doc = populate(tokens, raw_content=raw)

        # Assert
        section_sum = sum(s.estimated_tokens for s in doc.sections)
        assert doc.estimated_tokens >= section_sum

    def test_all_sections_have_tokens_set(self):
        """Verify all sections have non-negative estimated_tokens."""
        # Arrange
        tokens = [
            _tok(TokenType.H2, 1, "## A"),
            _tok(TokenType.TEXT, 2, "Some content"),
            _tok(TokenType.H2, 3, "## B"),
            _tok(TokenType.TEXT, 4, "More content here"),
            _tok(TokenType.H2, 5, "## C"),
        ]

        # Act
        doc = populate(tokens)

        # Assert
        assert len(doc.sections) == 3
        for section in doc.sections:
            assert section.estimated_tokens >= 0
