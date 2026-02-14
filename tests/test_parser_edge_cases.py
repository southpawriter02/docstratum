"""Edge case tests for the DocStratum parser.

Tests all 33 edge cases from v0.0.1a §Edge Cases (A1-A10, B1-B8,
C1-C10, D1-D5), organized by category. Each test verifies that the
parser produces the expected structural model for adversarial or
unusual input.

Tests focus on parser model output, NOT diagnostic codes or quality
scores. Ambiguous behaviors (A5, B7, C4, C6) have their chosen
interpretation documented in test docstrings.

Implements:
    docs/design/03-parser/RR-SPEC-v0.2.2c-edge-case-coverage.md

Grounding:
    v0.0.1a §Edge Cases (A1-A10, B1-B8, C1-C10, D1-D5)

See also:
    docs/design/00-meta/RR-META-testing-standards.md
"""

from docstratum.parser import (
    classify_document,
    populate,
    read_bytes,
    read_string,
    tokenize,
)
from docstratum.schema.classification import DocumentType


class TestCategoryAStructural:
    """A1-A10: Structural edge cases.

    Tests for empty files, missing/multiple H1 headings, out-of-order
    headers, H3+ depth, empty sections, fenced code blocks, and large
    documents.
    """

    def test_A1_empty_file(self):  # noqa: N802
        """A1: Empty file produces empty model with UNKNOWN classification.

        Edge case ID: A1
        Grounding: v0.0.1a §Edge Cases A1
        """
        # Arrange
        content, file_meta = read_string("")

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")
        classification = classify_document(doc, file_meta)

        # Assert
        assert doc.title is None
        assert doc.title_line is None
        assert doc.blockquote is None
        assert doc.sections == []
        assert doc.estimated_tokens == 0
        assert classification.document_type == DocumentType.UNKNOWN

    def test_A2_blank_only_file(self):  # noqa: N802
        """A2: Blank-only file produces empty model without crash.

        Edge case ID: A2
        Grounding: v0.0.1a §Edge Cases A2
        """
        # Arrange
        content, _file_meta = read_string("\n\n   \n\n")

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title is None
        assert doc.sections == []

    def test_A3_no_h1(self):  # noqa: N802
        """A3: Document without H1 produces title=None with sections.

        Edge case ID: A3
        Grounding: v0.0.1a §Edge Cases A3
        """
        # Arrange
        input_text = "## Section One\n\n- [Link](https://example.com)\n"
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title is None
        assert len(doc.sections) == 1
        assert doc.sections[0].name == "Section One"
        assert len(doc.sections[0].links) == 1
        assert doc.sections[0].links[0].url == "https://example.com"

    def test_A4_multiple_h1(self):  # noqa: N802
        """A4: Multiple H1 headings — first captured, rest treated as text.

        Edge case ID: A4
        Grounding: v0.0.1a §Edge Cases A4

        Parser behavior: Phase 1 captures the first H1 as title. The
        second H1 appears later in the section body as raw text. The
        classifier detects multiple H1s via ``_count_h1_headings()``
        and classifies as TYPE_2_FULL.
        """
        # Arrange
        input_text = (
            "# First Title\n"
            "\n"
            "## Section\n"
            "\n"
            "- [Link](https://example.com)\n"
            "\n"
            "# Second Title\n"
        )
        content, file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")
        classification = classify_document(doc, file_meta)

        # Assert
        assert doc.title == "First Title"
        assert len(doc.sections) == 1
        assert "# Second Title" in doc.raw_content
        assert classification.document_type == DocumentType.TYPE_2_FULL

    def test_A5_h2_before_h1(self):  # noqa: N802
        """A5: H2 before H1 — orphan section processed, late H1 NOT captured.

        Edge case ID: A5
        Grounding: v0.0.1a §Edge Cases A5

        DOCUMENTED AMBIGUITY: Spec allows multiple interpretations for
        this ordering. Our parser's behavior: Phase 1 skips leading blanks
        and checks for H1. Since the first non-blank token is H2 (not H1),
        title remains None. Phase 3 finds the H2 immediately and exits.
        Phase 4 processes all H2 sections. The late ``# Late Title`` is
        encountered in Phase 4 but only H2 tokens start new sections —
        H1 tokens become text content within the current section.
        """
        # Arrange
        input_text = (
            "## Orphan Section\n"
            "\n"
            "- [Link](https://example.com)\n"
            "\n"
            "# Late Title\n"
            "\n"
            "## Normal Section\n"
            "\n"
            "- [Link2](https://example.com/2)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title is None
        assert len(doc.sections) == 2
        assert doc.sections[0].name == "Orphan Section"
        assert doc.sections[1].name == "Normal Section"
        # Late H1 appears as text inside the first section's raw_content
        assert "# Late Title" in doc.sections[0].raw_content

    def test_A6_no_h2_sections(self):  # noqa: N802
        """A6: Title and blockquote only — no H2 sections.

        Edge case ID: A6
        Grounding: v0.0.1a §Edge Cases A6
        """
        # Arrange
        input_text = "# Title Only\n\n> Just a description, no sections.\n"
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title == "Title Only"
        assert doc.blockquote is not None
        assert doc.blockquote.text == "Just a description, no sections."
        assert doc.sections == []

    def test_A7_h3_plus_headers(self):  # noqa: N802
        """A7: H3 and H4 headers treated as TEXT within sections.

        Edge case ID: A7
        Grounding: v0.0.1a §Edge Cases A7

        H3+ lines are tokenized as H3_PLUS but the populator treats
        them as general content — they appear in ``raw_content`` and
        do not create new sections.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Section\n"
            "\n"
            "### Subsection\n"
            "\n"
            "#### Deep\n"
            "\n"
            "- [Link](https://example.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title == "Title"
        assert len(doc.sections) == 1
        assert doc.sections[0].name == "Section"
        assert "### Subsection" in doc.sections[0].raw_content
        assert "#### Deep" in doc.sections[0].raw_content
        assert len(doc.sections[0].links) == 1

    def test_A8_empty_h2_section(self):  # noqa: N802
        """A8: Empty H2 section followed by non-empty section.

        Edge case ID: A8
        Grounding: v0.0.1a §Edge Cases A8
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Empty Section\n"
            "\n"
            "## Non-Empty Section\n"
            "\n"
            "- [Link](https://example.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections) == 2
        assert doc.sections[0].name == "Empty Section"
        assert doc.sections[0].links == []
        assert doc.sections[1].name == "Non-Empty Section"
        assert len(doc.sections[1].links) == 1

    def test_A9_fenced_code_blocks(self):  # noqa: N802
        """A9: Content inside code fences NOT parsed as structure.

        Edge case ID: A9
        Grounding: v0.0.1a §Edge Cases A9

        The tokenizer classifies lines inside ````` blocks as TEXT
        regardless of their content. The populator also tracks code
        fence state and suppresses link extraction inside blocks.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Code Section\n"
            "\n"
            "```markdown\n"
            "# This is NOT a title\n"
            "\n"
            "## This is NOT a section\n"
            "\n"
            "- [Not a link](https://not-parsed.com)\n"
            "```\n"
            "\n"
            "- [Real Link](https://real.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title == "Title"
        assert len(doc.sections) == 1
        assert doc.sections[0].name == "Code Section"
        assert len(doc.sections[0].links) == 1
        assert doc.sections[0].links[0].title == "Real Link"
        assert "# This is NOT a title" in doc.sections[0].raw_content

    def test_A10_type2_full_document(self):  # noqa: N802
        """A10: Large document (>256 KB) classified as TYPE_2_FULL.

        Edge case ID: A10
        Grounding: v0.0.1a §Edge Cases A10

        Document generated programmatically to exceed the
        ``TYPE_BOUNDARY_BYTES`` threshold (256,000 bytes). The
        classifier detects the size and assigns TYPE_2_FULL.
        """
        # Arrange — generate document exceeding 256,000 bytes
        lines = ["# Large Document\n"]
        for i in range(500):
            lines.append(f"\n## Section {i}\n")
            for j in range(10):
                lines.append(
                    f"- [Link {i}-{j}](https://example.com/{i}/{j})"
                    f": Description for link {i}-{j}\n"
                )
        input_text = "\n".join(lines)
        content, file_meta = read_string(input_text)

        # Verify the generated document exceeds the threshold
        assert file_meta.byte_count > 256_000

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")
        classification = classify_document(doc, file_meta)

        # Assert
        assert classification.document_type == DocumentType.TYPE_2_FULL
        assert doc.title == "Large Document"
        assert len(doc.sections) > 0


class TestCategoryBLinkFormat:
    """B1-B8: Link format edge cases.

    Tests for malformed links, empty URLs/titles, relative URLs,
    duplicate URLs, non-list-item links, and bare URLs.
    """

    def test_B1_missing_closing_paren(self):  # noqa: N802
        """B1: Malformed link (missing closing paren) not extracted.

        Edge case ID: B1
        Grounding: v0.0.1a §Edge Cases B1

        The tokenizer flags the line as LINK_ENTRY (prefix ``- [``),
        but ``_parse_link_entry()`` fails the full regex match and
        returns None. The line is added to ``raw_content`` as text.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Links\n"
            "\n"
            "- [Broken](https://example.com\n"
            "- [Good](https://example.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 1
        assert doc.sections[0].links[0].title == "Good"
        assert "- [Broken](https://example.com" in doc.sections[0].raw_content

    def test_B2_empty_url(self):  # noqa: N802
        """B2: Link with empty URL extracted with url=''.

        Edge case ID: B2
        Grounding: v0.0.1a §Edge Cases B2

        The regex matches ``- [Empty]()`` — URL group captures empty
        string. ``_is_syntactically_valid_url("")`` returns False.
        """
        # Arrange
        input_text = "# Title\n\n## Links\n\n- [Empty]()\n"
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 1
        link = doc.sections[0].links[0]
        assert link.title == "Empty"
        assert link.url == ""
        assert link.is_valid_url is False

    def test_B3_relative_url(self):  # noqa: N802
        """B3: Relative URLs preserved as-is and marked valid.

        Edge case ID: B3
        Grounding: v0.0.1a §Edge Cases B3

        ``_is_syntactically_valid_url()`` accepts URLs starting with
        ``/``, ``./``, or ``../`` as valid relative paths.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Links\n"
            "\n"
            "- [Relative](/docs/api)\n"
            "- [Dotted](./local.md)\n"
            "- [Parent](../parent.md)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 3
        assert doc.sections[0].links[0].url == "/docs/api"
        assert doc.sections[0].links[0].is_valid_url is True
        assert doc.sections[0].links[1].url == "./local.md"
        assert doc.sections[0].links[1].is_valid_url is True
        assert doc.sections[0].links[2].url == "../parent.md"
        assert doc.sections[0].links[2].is_valid_url is True

    def test_B4_malformed_url(self):  # noqa: N802
        """B4: Malformed URL extracted but marked invalid.

        Edge case ID: B4
        Grounding: v0.0.1a §Edge Cases B4

        The parser does not validate URL format — that is the
        validator's job (v0.3.x). Both links are extracted; the
        malformed URL has ``is_valid_url=False``.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Links\n"
            "\n"
            "- [Bad](not a url at all)\n"
            "- [Good](https://example.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 2
        assert doc.sections[0].links[0].url == "not a url at all"
        assert doc.sections[0].links[0].is_valid_url is False
        assert doc.sections[0].links[1].is_valid_url is True

    def test_B5_duplicate_urls(self):  # noqa: N802
        """B5: Duplicate URLs both extracted (no deduplication).

        Edge case ID: B5
        Grounding: v0.0.1a §Edge Cases B5
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Links\n"
            "\n"
            "- [Link A](https://example.com)\n"
            "- [Link B](https://example.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 2
        assert doc.sections[0].links[0].url == doc.sections[0].links[1].url
        assert doc.sections[0].links[0].title == "Link A"
        assert doc.sections[0].links[1].title == "Link B"

    def test_B6_empty_title(self):  # noqa: N802
        """B6: Link with empty title extracted with title=''.

        Edge case ID: B6
        Grounding: v0.0.1a §Edge Cases B6

        The regex captures an empty string for the title group.
        ``match.group(1).strip()`` yields ``""``, not None.
        """
        # Arrange
        input_text = "# Title\n\n## Links\n\n- [](https://example.com)\n"
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 1
        assert doc.sections[0].links[0].title == ""
        assert doc.sections[0].links[0].url == "https://example.com"

    def test_B7_non_list_links(self):  # noqa: N802
        """B7: Non-list-item links NOT extracted (STRICT behavior).

        Edge case ID: B7
        Grounding: v0.0.1a §Edge Cases B7

        DOCUMENTED AMBIGUITY: The spec allows STRICT or PERMISSIVE
        interpretation. Our parser uses STRICT: only lines starting
        with ``- [`` are classified as LINK_ENTRY by the tokenizer.
        Lines like ``[Bare Link](url)`` without the ``- `` prefix
        are classified as TEXT and never reach ``_parse_link_entry()``.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Links\n"
            "\n"
            "[Bare Link](https://example.com)\n"
            "\n"
            "Not a list item: [Inline](https://inline.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 0
        assert "[Bare Link](https://example.com)" in doc.sections[0].raw_content

    def test_B8_bare_urls(self):  # noqa: N802
        """B8: Bare URLs (no Markdown link syntax) not extracted.

        Edge case ID: B8
        Grounding: v0.0.1a §Edge Cases B8

        Lines like ``- https://bare-url.com`` lack the ``[text](url)``
        pattern. The tokenizer does not classify them as LINK_ENTRY
        (no ``- [`` prefix), so they appear as TEXT.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Links\n"
            "\n"
            "- https://bare-url.com\n"
            "- <https://angle-bracket.com>\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 0
        assert "https://bare-url.com" in doc.sections[0].raw_content


class TestCategoryCContent:
    """C1-C10: Content edge cases.

    Tests for multiline blockquotes, Unicode, long lines, mixed
    indentation, trailing whitespace, nested lists, optional
    descriptions, consecutive blank lines, HTML comments, and
    mixed prose/link content.
    """

    def test_C1_multiline_blockquote(self):  # noqa: N802
        """C1: Multiline blockquote joined with newlines, ``>`` stripped.

        Edge case ID: C1
        Grounding: v0.0.1a §Edge Cases C1

        Consecutive BLOCKQUOTE tokens are collected in Phase 2.
        The ``> `` prefix is stripped; lines joined with ``\\n``.
        Inline Markdown formatting is preserved as raw text.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "> Line 1 of the blockquote.\n"
            "> Line 2 of the blockquote.\n"
            "> Line 3 with **bold** and _italic_.\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.blockquote is not None
        expected = (
            "Line 1 of the blockquote.\n"
            "Line 2 of the blockquote.\n"
            "Line 3 with **bold** and _italic_."
        )
        assert doc.blockquote.text == expected

    def test_C2_unicode_content(self):  # noqa: N802
        """C2: Unicode content preserved throughout parsing.

        Edge case ID: C2
        Grounding: v0.0.1a §Edge Cases C2 (mapped from C4 in the spec)
        """
        # Arrange
        input_text = (
            "# \u65e5\u672c\u8a9e\u30d7\u30ed\u30b8\u30a7\u30af\u30c8\n"
            "\n"
            "> \u3053\u308c\u306f\u65e5\u672c\u8a9e\u306e\u8aac\u660e\u3067\u3059\u3002\n"
            "\n"
            "## \u30c9\u30ad\u30e5\u30e1\u30f3\u30c8\n"
            "\n"
            "- [API \u30ea\u30d5\u30a1\u30ec\u30f3\u30b9](https://example.com/api)"
            ": API \u306e\u5b8c\u5168\u306a\u30c9\u30ad\u30e5\u30e1\u30f3\u30c8\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title == "\u65e5\u672c\u8a9e\u30d7\u30ed\u30b8\u30a7\u30af\u30c8"
        assert doc.blockquote is not None
        assert (
            doc.blockquote.text
            == "\u3053\u308c\u306f\u65e5\u672c\u8a9e\u306e\u8aac\u660e\u3067\u3059\u3002"
        )
        assert doc.sections[0].name == "\u30c9\u30ad\u30e5\u30e1\u30f3\u30c8"
        assert (
            doc.sections[0].links[0].title == "API \u30ea\u30d5\u30a1\u30ec\u30f3\u30b9"
        )
        assert (
            doc.sections[0].links[0].description
            == "API \u306e\u5b8c\u5168\u306a\u30c9\u30ad\u30e5\u30e1\u30f3\u30c8"
        )

    def test_C3_long_lines(self):  # noqa: N802
        """C3: Lines exceeding 10,000 characters handled without truncation.

        Edge case ID: C3
        Grounding: v0.0.1a §Edge Cases C3 (mapped from C5 in the spec)
        """
        # Arrange
        long_line = "a" * 10_001
        input_text = f"# Title\n\n## Section\n\n{long_line}\n"
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert long_line in doc.sections[0].raw_content
        assert len(doc.sections[0].raw_content) >= 10_001

    def test_C4_mixed_indentation(self):  # noqa: N802
        """C4: Indented list items NOT extracted as links.

        Edge case ID: C4
        Grounding: v0.0.1a §Edge Cases C4 (mapped from C7 in the spec)

        DOCUMENTED AMBIGUITY: The spec allows either stripping leading
        whitespace or strict prefix matching. Our parser uses STRICT:
        the tokenizer checks for exact ``- [`` prefix. Lines like
        ``  - [Link]`` start with spaces, not ``- [``, so they are
        classified as TEXT.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Section\n"
            "\n"
            "- [Link 1](https://a.com)\n"
            "  - [Link 2](https://b.com)\n"
            "    - [Link 3](https://c.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert — only top-level link extracted
        assert len(doc.sections[0].links) == 1
        assert doc.sections[0].links[0].title == "Link 1"

    def test_C5_trailing_whitespace(self):  # noqa: N802
        """C5: Trailing whitespace stripped from titles, sections, URLs.

        Edge case ID: C5
        Grounding: v0.0.1a §Edge Cases C5 (mapped from C8 in the spec)

        The populator calls ``.removeprefix().strip()`` on H1/H2 text
        and ``.strip()`` on regex groups for URLs and descriptions.
        """
        # Arrange
        input_text = (
            "# Title   \n"
            "\n"
            "## Section  \n"
            "\n"
            "- [Link](https://example.com   ): Description  \n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title == "Title"
        assert doc.sections[0].name == "Section"
        assert doc.sections[0].links[0].url == "https://example.com"
        assert doc.sections[0].links[0].description == "Description"

    def test_C6_nested_lists(self):  # noqa: N802
        """C6: Nested list items NOT extracted as links (same as C4).

        Edge case ID: C6
        Grounding: v0.0.1a §Edge Cases C6 (mapped from C9 in the spec)

        DOCUMENTED AMBIGUITY: Same STRICT behavior as C4. Only
        top-level ``- [text](url)`` entries are extracted. Indented
        sub-items are TEXT.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Section\n"
            "\n"
            "- [Top Level](https://a.com)\n"
            "  - Sub-item text\n"
            "  - [Nested Link](https://b.com)\n"
            "    - Deep sub-item\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert — only top-level link extracted
        assert len(doc.sections[0].links) == 1
        assert doc.sections[0].links[0].title == "Top Level"

    def test_C7_entries_without_descriptions(self):  # noqa: N802
        """C7: Links without descriptions have description=None.

        Edge case ID: C7
        Grounding: v0.0.1a §Edge Cases C7 (mapped from C10 in the spec)

        Descriptions are optional per the grammar. The regex group(3)
        is None when no ``: description`` suffix is present.
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Section\n"
            "\n"
            "- [No Description](https://example.com)\n"
            "- [Has Description](https://example.com/2): This has a description\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 2
        assert doc.sections[0].links[0].description is None
        assert doc.sections[0].links[1].description == "This has a description"

    def test_C8_consecutive_blank_lines(self):  # noqa: N802
        """C8: Consecutive blank lines do not affect structural extraction.

        Edge case ID: C8
        Grounding: v0.0.1a §Edge Cases C8
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "\n"
            "\n"
            "> Description\n"
            "\n"
            "\n"
            "## Section\n"
            "\n"
            "\n"
            "- [Link](https://example.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title == "Title"
        assert doc.blockquote is not None
        assert doc.blockquote.text == "Description"
        assert len(doc.sections) == 1
        assert len(doc.sections[0].links) == 1

    def test_C9_html_comments(self):  # noqa: N802
        """C9: HTML comments treated as TEXT, no structural impact.

        Edge case ID: C9
        Grounding: v0.0.1a §Edge Cases C9
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "<!-- This is a comment -->\n"
            "\n"
            "## Section\n"
            "\n"
            "- [Link](https://example.com)\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert doc.title == "Title"
        assert len(doc.sections) == 1
        assert len(doc.sections[0].links) == 1
        assert "<!-- This is a comment -->" in doc.raw_content

    def test_C10_mixed_content_in_sections(self):  # noqa: N802
        """C10: Links extracted from sections containing prose content.

        Edge case ID: C10
        Grounding: v0.0.1a §Edge Cases C10
        """
        # Arrange
        input_text = (
            "# Title\n"
            "\n"
            "## Section\n"
            "\n"
            "Some prose paragraph before the links.\n"
            "\n"
            "More prose with **bold** text.\n"
            "\n"
            "- [Link 1](https://a.com): Description\n"
            "- [Link 2](https://b.com): Description\n"
            "\n"
            "Trailing prose after the links.\n"
        )
        content, _file_meta = read_string(input_text)

        # Act
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert len(doc.sections[0].links) == 2
        assert "Some prose paragraph" in doc.sections[0].raw_content
        assert "More prose with **bold** text." in doc.sections[0].raw_content
        assert "Trailing prose after the links." in doc.sections[0].raw_content


class TestCategoryDEncoding:
    """D1-D5: Encoding edge cases.

    Tests for UTF-8 BOM, non-UTF-8 encoding fallback, null bytes,
    Windows CRLF line endings, and legacy Mac CR-only line endings.
    """

    def test_D1_utf8_bom(self):  # noqa: N802
        """D1: UTF-8 BOM stripped by read_bytes(), parsing proceeds normally.

        Edge case ID: D1
        Grounding: v0.0.1a §Edge Cases D1

        The 3-byte BOM (``\\xEF\\xBB\\xBF``) is detected and stripped
        before decoding. The title on the first line is not corrupted.
        """
        # Arrange
        bom = b"\xef\xbb\xbf"
        raw_bytes = bom + b"# Title\n\n## Section\n\n- [Link](https://example.com)\n"

        # Act
        content, file_meta = read_bytes(raw_bytes)
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert file_meta.has_bom is True
        assert file_meta.encoding == "utf-8-bom"
        assert doc.title == "Title"
        assert "\ufeff" not in content
        assert len(doc.sections) == 1
        assert len(doc.sections[0].links) == 1

    def test_D2_non_utf8_encoding(self):  # noqa: N802
        """D2: Non-UTF-8 (Latin-1) decoded via fallback.

        Edge case ID: D2
        Grounding: v0.0.1a §Edge Cases D2

        ``read_bytes()`` attempts UTF-8 first. When that fails (bytes
        ``\\xe9`` and ``\\xef`` are invalid UTF-8 sequences), it falls
        back to Latin-1 which always succeeds.
        """
        # Arrange — bytes that are valid Latin-1 but invalid UTF-8
        raw_bytes = "# Caf\xe9\n\n## Na\xefve\n".encode("latin-1")

        # Act
        content, file_meta = read_bytes(raw_bytes)
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert file_meta.encoding == "latin-1"
        assert file_meta.decoding_error is not None
        assert doc.title is not None

    def test_D3_null_bytes(self):  # noqa: N802
        """D3: Null bytes detected, classified as UNKNOWN.

        Edge case ID: D3
        Grounding: v0.0.1a §Edge Cases D3

        ``read_bytes()`` scans for ``\\x00`` and sets
        ``has_null_bytes=True``. The classifier treats null-byte
        files as binary → ``UNKNOWN``.
        """
        # Arrange
        raw_bytes = b"# Title\x00\n\n## Section\n"

        # Act
        content, file_meta = read_bytes(raw_bytes)
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")
        classification = classify_document(doc, file_meta)

        # Assert
        assert file_meta.has_null_bytes is True
        assert classification.document_type == DocumentType.UNKNOWN

    def test_D4_windows_crlf(self):  # noqa: N802
        """D4: CRLF line endings normalized to LF.

        Edge case ID: D4
        Grounding: v0.0.1a §Edge Cases D4

        ``read_string()`` detects CRLF and normalizes to LF.
        Structure extracted identically to an LF-only version.
        """
        # Arrange
        input_text = (
            "# Title\r\n\r\n## Section\r\n\r\n- [Link](https://example.com)\r\n"
        )

        # Act
        content, file_meta = read_string(input_text)
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert "\r" not in content
        assert file_meta.line_ending_style == "crlf"
        assert doc.title == "Title"
        assert len(doc.sections) == 1
        assert len(doc.sections[0].links) == 1

    def test_D5_mac_cr_only(self):  # noqa: N802
        """D5: CR-only line endings normalized to LF.

        Edge case ID: D5
        Grounding: v0.0.1a §Edge Cases D5

        ``read_string()`` detects CR-only and normalizes to LF.
        Structure extracted identically to an LF-only version.
        """
        # Arrange
        input_text = "# Title\r\r## Section\r\r- [Link](https://example.com)\r"

        # Act
        content, file_meta = read_string(input_text)
        tokens = tokenize(content)
        doc = populate(tokens, raw_content=content, source_filename="edge_case.txt")

        # Assert
        assert "\r" not in content
        assert file_meta.line_ending_style == "cr"
        assert doc.title == "Title"
        assert len(doc.sections) == 1
        assert len(doc.sections[0].links) == 1
