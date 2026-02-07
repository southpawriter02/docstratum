"""Parsed document models for the DocStratum validation engine.

These models represent the PARSED structure of an llms.txt Markdown file —
what the parser (v0.3.1) produces after reading raw Markdown input.
They are the canonical in-memory representation of an llms.txt file.

The parser follows the "permissive input, strict output" principle (v0.0.1a):
    - Missing blockquotes → warning, not error (55% real-world compliance)
    - Relative URLs → info-level note with resolution hint
    - Partial results returned with diagnostic annotations

ABNF grammar reference (v0.0.1a):
    llms-txt   = title CRLF description CRLF *section
    title      = "#" SP title-text CRLF
    description = ">" SP desc-text CRLF
    section    = "##" SP section-name CRLF *entry
    entry      = "-" SP "[" link-title "](" url ")" [": " desc] CRLF
"""

import logging
from datetime import datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ParsedBlockquote(BaseModel):
    """The blockquote description immediately following the H1 title.

    In the ABNF grammar, this maps to the ``description`` rule.
    Empirical data: only 55% of real-world files include this (v0.0.2 enrichment).
    Missing blockquotes generate W001, not an error.

    Attributes:
        text: The blockquote text content (without the '>' prefix).
        line_number: Line number where the blockquote starts (1-indexed).
        raw: The original raw text including the '>' prefix.
    """

    text: str = Field(
        description="Cleaned blockquote text (without '>' prefix, stripped).",
    )
    line_number: int = Field(
        ge=1,
        description="Line number in the source file (1-indexed).",
    )
    raw: str = Field(
        default="",
        description="Original raw text including '>' prefix.",
    )


class ParsedLink(BaseModel):
    """A single link entry within an H2 section.

    In the ABNF grammar, this maps to the ``entry`` rule:
        entry = "-" SP "[" link-title "](" url ")" [": " desc] CRLF

    Attributes:
        title: The link text (content within square brackets).
        url: The URL (content within parentheses).
        description: Optional description after the link (content after ': ').
        line_number: Line number in the source file.
        is_valid_url: Whether the URL appears well-formed (syntactic check only).
    """

    title: str = Field(
        description="Link text from [title](url) format.",
    )
    url: str = Field(
        description="URL from [title](url) format. May be relative or absolute.",
    )
    description: str | None = Field(
        default=None,
        description="Optional description text after ': ' delimiter.",
    )
    line_number: int = Field(
        ge=1,
        description="Line number in the source file (1-indexed).",
    )
    is_valid_url: bool = Field(
        default=True,
        description="Whether the URL passes basic syntactic validation.",
    )


class ParsedSection(BaseModel):
    """An H2 section within the llms.txt file.

    In the ABNF grammar, this maps to the ``section`` rule:
        section = "##" SP section-name CRLF *entry

    Each section may contain links (the standard format), freeform content
    (common in real-world files), or both.

    Attributes:
        name: The section header text (content after '## ').
        links: List of parsed link entries within this section.
        raw_content: The full raw text content of the section (between this H2 and the next).
        line_number: Line number of the H2 header.
        canonical_name: The matched canonical section name, if any.
        estimated_tokens: Approximate token count for this section's content.
    """

    name: str = Field(
        description="Section header text (without '## ' prefix).",
    )
    links: list[ParsedLink] = Field(
        default_factory=list,
        description="Link entries found within this section.",
    )
    raw_content: str = Field(
        default="",
        description="Full raw text of the section (headers, links, prose, code blocks).",
    )
    line_number: int = Field(
        ge=1,
        description="Line number of the H2 header (1-indexed).",
    )
    canonical_name: str | None = Field(
        default=None,
        description="Matched canonical section name, or None if non-canonical.",
    )
    estimated_tokens: int = Field(
        default=0,
        ge=0,
        description="Approximate token count (len(raw_content) / 4 heuristic).",
    )

    @property
    def link_count(self) -> int:
        """Number of links in this section."""
        return len(self.links)

    @property
    def has_code_examples(self) -> bool:
        """Whether this section contains fenced code blocks."""
        return "```" in self.raw_content


class ParsedLlmsTxt(BaseModel):
    """Root model representing a fully parsed llms.txt Markdown file.

    This is the primary output of the parser (v0.3.1) and the primary
    input to the validator (v0.2.4) and quality scorer.

    The model preserves the original file structure while providing
    typed access to all components. It does NOT enforce validity —
    that is the validator's job. A ParsedLlmsTxt can represent
    a partially conformant or even broken file.

    Attributes:
        title: The H1 title text (without '# ' prefix).
        title_line: Line number of the H1 title.
        blockquote: The parsed blockquote description (may be None if missing).
        sections: List of H2 sections in document order.
        raw_content: The complete raw file content (for re-serialization).
        source_filename: Original filename for provenance.
        parsed_at: Timestamp of parsing.

    Example:
        doc = ParsedLlmsTxt(
            title="Stripe Documentation",
            title_line=1,
            blockquote=ParsedBlockquote(text="Stripe API docs", line_number=2),
            sections=[
                ParsedSection(name="Docs", links=[...], line_number=4),
            ],
            raw_content="# Stripe Documentation\\n> Stripe API docs\\n...",
        )

    Traces to: FR-001 (base structure), FR-011 (round-trip serialization)
    """

    title: str | None = Field(
        default=None,
        description="H1 title text. None if no H1 found (triggers E001).",
    )
    title_line: int | None = Field(
        default=None,
        ge=1,
        description="Line number of the H1 title.",
    )
    blockquote: ParsedBlockquote | None = Field(
        default=None,
        description="Blockquote description. None if missing (triggers W001).",
    )
    sections: list[ParsedSection] = Field(
        default_factory=list,
        description="H2 sections in document order.",
    )
    raw_content: str = Field(
        default="",
        description="Complete raw file content for round-trip serialization.",
    )
    source_filename: str = Field(
        default="llms.txt",
        description="Original filename for provenance tracking.",
    )
    parsed_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when parsing completed.",
    )

    @property
    def section_count(self) -> int:
        """Total number of H2 sections."""
        return len(self.sections)

    @property
    def total_links(self) -> int:
        """Total number of links across all sections."""
        return sum(s.link_count for s in self.sections)

    @property
    def estimated_tokens(self) -> int:
        """Approximate total token count (heuristic: chars / 4)."""
        return len(self.raw_content) // 4

    @property
    def has_blockquote(self) -> bool:
        """Whether a blockquote description is present."""
        return self.blockquote is not None

    @property
    def section_names(self) -> list[str]:
        """List of section names in document order."""
        return [s.name for s in self.sections]
