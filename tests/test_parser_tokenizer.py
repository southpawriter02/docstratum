"""Tests for the parser tokenizer module (v0.2.0b).

Tests cover token type classification, code fence state tracking,
line number preservation, priority ordering, and edge cases.
See RR-META-testing-standards for naming conventions and fixture patterns.
"""

from docstratum.parser.tokenizer import tokenize
from docstratum.parser.tokens import TokenType


class TestTokenClassification:
    """Tests for individual token type classification."""

    def test_h1_token(self):
        """Verify '# Title' is classified as H1."""
        # Act
        tokens = tokenize("# Title")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.H1
        assert tokens[0].raw_text == "# Title"

    def test_h2_token(self):
        """Verify '## Section' is classified as H2."""
        # Act
        tokens = tokenize("## Section")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.H2

    def test_h3_token(self):
        """Verify '### Sub' is classified as H3_PLUS (A7)."""
        # Act
        tokens = tokenize("### Sub")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.H3_PLUS

    def test_h4_token(self):
        """Verify '#### Deep' is classified as H3_PLUS (A7)."""
        # Act
        tokens = tokenize("#### Deep")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.H3_PLUS

    def test_blockquote_token(self):
        """Verify '> Description' is classified as BLOCKQUOTE."""
        # Act
        tokens = tokenize("> Description")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.BLOCKQUOTE

    def test_bare_blockquote(self):
        """Verify bare '>' without trailing space is BLOCKQUOTE (C2)."""
        # Act
        tokens = tokenize(">")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.BLOCKQUOTE

    def test_link_entry_token(self):
        """Verify '- [Foo](url): Desc' is classified as LINK_ENTRY."""
        # Act
        tokens = tokenize("- [Foo](https://foo.com): Description")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.LINK_ENTRY

    def test_link_no_desc_token(self):
        """Verify '- [Foo](url)' without description is LINK_ENTRY."""
        # Act
        tokens = tokenize("- [Foo](https://foo.com)")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.LINK_ENTRY

    def test_bare_url_is_text(self):
        """Verify '- https://foo.com' (bare URL, B8) is TEXT, not LINK_ENTRY."""
        # Act
        tokens = tokenize("- https://foo.com")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.TEXT

    def test_inline_link_is_text(self):
        """Verify '[Foo](url)' without '- ' prefix (B7) is TEXT."""
        # Act
        tokens = tokenize("[Foo](https://foo.com)")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.TEXT

    def test_blank_line(self):
        """Verify empty string line is classified as BLANK."""
        # Arrange — single blank line (no trailing newline artifact)
        tokens = tokenize("\n")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.BLANK

    def test_whitespace_line(self):
        """Verify whitespace-only line is classified as BLANK."""
        # Act
        tokens = tokenize("   ")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.BLANK

    def test_text_line(self):
        """Verify plain text line is classified as TEXT."""
        # Act
        tokens = tokenize("Just some text.")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.TEXT


class TestCodeFenceState:
    """Tests for code fence state machine behavior."""

    def test_code_fence_toggle(self):
        """Verify code block produces CODE_FENCE, TEXT, CODE_FENCE (A9)."""
        # Arrange
        content = "```python\n# not H1\n```"

        # Act
        tokens = tokenize(content)

        # Assert
        assert len(tokens) == 3
        assert tokens[0].token_type == TokenType.CODE_FENCE
        assert tokens[1].token_type == TokenType.TEXT
        assert tokens[2].token_type == TokenType.CODE_FENCE

    def test_code_block_suppresses_h1(self):
        """Verify '# Title' inside code block is TEXT, not H1 (A9)."""
        # Arrange
        content = "```\n# Title\n```"

        # Act
        tokens = tokenize(content)

        # Assert
        assert tokens[1].token_type == TokenType.TEXT
        assert tokens[1].raw_text == "# Title"

    def test_code_block_suppresses_link(self):
        """Verify '- [F](url)' inside code block is TEXT, not LINK_ENTRY."""
        # Arrange
        content = "```\n- [F](url)\n```"

        # Act
        tokens = tokenize(content)

        # Assert
        assert tokens[1].token_type == TokenType.TEXT

    def test_unclosed_code_fence(self):
        """Verify unclosed code fence keeps remaining lines as TEXT."""
        # Arrange
        content = "```python\n# still code"

        # Act
        tokens = tokenize(content)

        # Assert
        assert len(tokens) == 2
        assert tokens[0].token_type == TokenType.CODE_FENCE
        assert tokens[1].token_type == TokenType.TEXT


class TestPriorityAndEdgeCases:
    """Tests for classification priority order and edge cases."""

    def test_priority_order_h2_before_h1(self):
        """Verify '## Section' is H2, not H1 (§4.2 priority check)."""
        # Act
        tokens = tokenize("## Section")

        # Assert — should be H2, NOT H1 (which would match if # checked first)
        assert tokens[0].token_type == TokenType.H2

    def test_tab_indented_heading(self):
        """Verify tab-indented heading is TEXT (C7)."""
        # Act
        tokens = tokenize("\t# Title")

        # Assert
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.TEXT

    def test_empty_content(self):
        """Verify empty content returns empty list."""
        # Act
        tokens = tokenize("")

        # Assert
        assert tokens == []


class TestLineNumbers:
    """Tests for line number tracking."""

    def test_line_numbers_correct(self):
        """Verify 5-line document produces tokens with line_number 1-5."""
        # Arrange
        content = "# Title\n> Desc\n\n## Docs\n- [Foo](https://foo.com)"

        # Act
        tokens = tokenize(content)

        # Assert
        assert len(tokens) == 5
        assert [t.line_number for t in tokens] == [1, 2, 3, 4, 5]


class TestFullDocument:
    """Tests for complete document tokenization."""

    def test_full_document(self):
        """Verify minimal valid llms.txt tokenizes correctly."""
        # Arrange
        content = (
            "# My Project\n"
            "\n"
            "> A cool project for doing things.\n"
            "\n"
            "## Docs\n"
            "- [Getting Started](https://example.com/start): How to begin\n"
            "- [API Reference](https://example.com/api): Full API docs\n"
        )

        # Act
        tokens = tokenize(content)

        # Assert
        expected_types = [
            TokenType.H1,
            TokenType.BLANK,
            TokenType.BLOCKQUOTE,
            TokenType.BLANK,
            TokenType.H2,
            TokenType.LINK_ENTRY,
            TokenType.LINK_ENTRY,
        ]
        assert [t.token_type for t in tokens] == expected_types

    def test_raw_text_preserved(self):
        """Verify raw_text is preserved without modification (AC §7.9)."""
        # Arrange
        content = "# Title\n> Description with  extra   spaces\n"

        # Act
        tokens = tokenize(content)

        # Assert
        assert tokens[0].raw_text == "# Title"
        assert tokens[1].raw_text == "> Description with  extra   spaces"
