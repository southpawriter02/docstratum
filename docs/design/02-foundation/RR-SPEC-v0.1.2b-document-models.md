# v0.1.2b — Document Models: Classification and Parsed Structure

> **Phase:** Foundation (v0.1.x)
> **Status:** DRAFT — Realigned to validation-engine pivot (2026-02-06)
> **Parent:** [v0.1.2 — Schema Definition](RR-SPEC-v0.1.2-schema-definition.md)
> **Goal:** Define the input-side models that represent what a parsed llms.txt file IS — document type classification (`classification.py`) and the parsed Markdown structure (`parsed.py`).
> **Traces to:** FR-001, FR-011 (v0.0.5a); Finding 4 (bimodal distribution); DECISION-001, -013 (v0.0.4d); v0.0.1a (ABNF grammar)

---

## Why This Sub-Part Exists

These two files represent the **input side** of the validation pipeline. Before the engine can validate or score a file, it must first classify it (Type 1 Index vs. Type 2 Full) and parse it into a typed model hierarchy. `classification.py` runs first (the "triage" step), and `parsed.py` represents the parser's output (what gets fed into the validator).

Both models follow the "permissive input, strict output" principle from v0.0.1a — a `ParsedLlmsTxt` can represent a broken or partially conformant file. Validity enforcement is the validator's job (v0.2.4), not the parser's.

---

## File 3: `src/docstratum/schema/classification.py` — Document Type Classification

**Traces to:** Finding 4 (bimodal distribution), v0.0.1a enrichment (Type 1 vs. Type 2), DECISION-013 (token budget tiers)

```python
"""Document type classification models for the DocStratum validation engine.

The research (v0.0.1a enrichment) established that llms.txt files fall into
two distinct types with a bimodal distribution and no overlap zone:

    Type 1 Index: Curated link catalogs (1.1 KB – 225 KB, 80–100% conformance)
    Type 2 Full: Inline documentation dumps (1.3 MB – 25 MB, 5–15% conformance)

The ~250 KB boundary serves as the classification heuristic threshold.
Classification happens BEFORE validation because different document types
receive different validation rule sets.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DocumentType(StrEnum):
    """Document type classification.

    Based on the bimodal distribution observed across 11 specimens (v0.0.1a).
    No specimens exist in the 225 KB – 1.3 MB range, confirming a natural boundary.

    Attributes:
        TYPE_1_INDEX: Curated link catalog following the spec's intended format.
                      Receives full ABNF-based structural validation.
        TYPE_2_FULL: Inline documentation dump (llms-full.txt convention).
                     Receives size-appropriate diagnostics only.
        UNKNOWN: Classification could not be determined (e.g., empty file).
    """

    TYPE_1_INDEX = "type_1_index"
    TYPE_2_FULL = "type_2_full"
    UNKNOWN = "unknown"


class SizeTier(StrEnum):
    """Token budget size tier (DECISION-013).

    Files are assigned to tiers based on estimated token count.
    Each tier has recommended token budgets and file strategies.

    Attributes:
        MINIMAL: Under 1,500 tokens. Very small files (stubs, placeholders).
        STANDARD: 1,500–4,500 tokens. Small projects, <100 pages.
        COMPREHENSIVE: 4,500–12,000 tokens. Medium projects, 100–500 pages.
        FULL: 12,000–50,000 tokens. Large projects, 500+ pages.
        OVERSIZED: Over 50,000 tokens. Exceeds recommended limits.
    """

    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    FULL = "full"
    OVERSIZED = "oversized"


class DocumentClassification(BaseModel):
    """Result of classifying an llms.txt file before validation.

    The classifier runs first in the pipeline, determining which
    validation rules to apply and which token budget tier to enforce.

    Attributes:
        document_type: Type 1 Index or Type 2 Full (or Unknown).
        size_bytes: Raw file size in bytes.
        estimated_tokens: Approximate token count (bytes / 4 heuristic).
        size_tier: Assigned token budget tier.
        filename: Original filename (for display/logging).
        classified_at: Timestamp of classification.

    Example:
        classification = DocumentClassification(
            document_type=DocumentType.TYPE_1_INDEX,
            size_bytes=19_456,
            estimated_tokens=4_864,
            size_tier=SizeTier.COMPREHENSIVE,
            filename="llms.txt",
        )
    """

    document_type: DocumentType = Field(
        description="Whether this file is a Type 1 Index or Type 2 Full document."
    )
    size_bytes: int = Field(ge=0, description="Raw file size in bytes.")
    estimated_tokens: int = Field(
        ge=0,
        description="Approximate token count. Heuristic: bytes / 4.",
    )
    size_tier: SizeTier = Field(
        description="Token budget tier based on estimated token count.",
    )
    filename: str = Field(
        default="llms.txt",
        description="Original filename for logging and display.",
    )
    classified_at: datetime = Field(
        default_factory=datetime.now,
        description="When classification was performed.",
    )

    # ── Classification boundaries ────────────────────────────────────
    # These are class-level constants used by the classifier logic
    # (implemented in v0.3.1, but defined here for schema reference).

    TYPE_BOUNDARY_BYTES: int = 256_000  # ~250 KB — the bimodal gap
    """Byte threshold separating Type 1 from Type 2.
    Files above this are classified as Type 2 Full.
    Derived from: largest Type 1 specimen = Cloudflare at 225 KB;
    smallest Type 2 specimen = Vercel AI SDK at 1.3 MB.
    """
```

---

## File 4: `src/docstratum/schema/parsed.py` — Parsed Document Models

**Traces to:** FR-001 (Pydantic models for base llms.txt structure), v0.0.1a (ABNF grammar), DECISION-001 (Markdown format)

```python
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

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ParsedBlockquote(BaseModel):
    """The blockquote description immediately following the H1 title.

    In the ABNF grammar, this maps to the `description` rule.
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

    In the ABNF grammar, this maps to the `entry` rule:
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
    description: Optional[str] = Field(
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

    In the ABNF grammar, this maps to the `section` rule:
        section = "##" SP section-name CRLF *entry

    Each section may contain links (the standard format), freeform content
    (common in real-world files), or both.

    Attributes:
        name: The section header text (content after '## ').
        links: List of parsed link entries within this section.
        raw_content: The full raw text content of the section (between this H2 and the next).
        line_number: Line number of the H2 header.
        canonical_name: The matched canonical section name, if any.
        link_count: Number of links in this section (computed).
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
    canonical_name: Optional[str] = Field(
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

    title: Optional[str] = Field(
        default=None,
        description="H1 title text. None if no H1 found (triggers E001).",
    )
    title_line: Optional[int] = Field(
        default=None,
        ge=1,
        description="Line number of the H1 title.",
    )
    blockquote: Optional[ParsedBlockquote] = Field(
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
```

---

## Design Decisions Applied

| ID | Decision | How Applied in v0.1.2b |
|----|----------|----------------------|
| DECISION-001 | Markdown over JSON/YAML | `ParsedLlmsTxt` models parsed Markdown, not YAML structures |
| DECISION-013 | Token Budget Tiers | `SizeTier` enum maps to tier definitions in constants.py |

---

## Exit Criteria

- [ ] `DocumentType`, `SizeTier`, and `DocumentClassification` importable
- [ ] `ParsedBlockquote`, `ParsedLink`, `ParsedSection`, `ParsedLlmsTxt` importable
- [ ] `DocumentClassification.TYPE_BOUNDARY_BYTES == 256_000`
- [ ] `ParsedLlmsTxt` computed properties (`section_count`, `total_links`, `estimated_tokens`, `has_blockquote`, `section_names`) work correctly
- [ ] `black --check src/docstratum/schema/classification.py src/docstratum/schema/parsed.py` passes
- [ ] `ruff check src/docstratum/schema/classification.py src/docstratum/schema/parsed.py` passes
