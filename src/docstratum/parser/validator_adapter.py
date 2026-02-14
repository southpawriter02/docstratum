"""SingleFileValidator protocol implementation for the parser phase.

Adapts the v0.2.0 parser and v0.2.1 enrichment modules into the
``SingleFileValidator`` interface required by the ecosystem pipeline's
Stage 2 (``PerFileStage``).

At v0.2.2d, only ``parse()`` and ``classify()`` are fully functional.
``validate()`` and ``score()`` return stub results because the validation
engine (v0.3.x) and quality scorer (v0.4.x) are not yet implemented.

Implements v0.2.2d.

Example:
    >>> from docstratum.parser.validator_adapter import ParserAdapter
    >>> from docstratum.pipeline.per_file import PerFileStage
    >>> adapter = ParserAdapter()
    >>> stage = PerFileStage(validator=adapter)
    >>> # Now the pipeline's Stage 2 will use the real parser

Research basis:
    v0.1.4a (SingleFileValidator protocol)
    v0.1.4b (PerFileStage)

Traces to:
    FR-080 (per-file validation within ecosystem)
"""

from __future__ import annotations

import logging
import re

from docstratum.parser.classifier import classify_document
from docstratum.parser.io import FileMetadata, read_string
from docstratum.parser.metadata import extract_metadata
from docstratum.parser.populator import populate
from docstratum.parser.section_matcher import match_canonical_sections
from docstratum.parser.tokenizer import tokenize
from docstratum.schema.classification import DocumentClassification
from docstratum.schema.parsed import ParsedLlmsTxt
from docstratum.schema.quality import (
    DimensionScore,
    QualityDimension,
    QualityGrade,
    QualityScore,
)
from docstratum.schema.validation import ValidationLevel, ValidationResult

logger = logging.getLogger(__name__)

# ── Frontmatter stripping ────────────────────────────────────────────
# The tokenizer does not understand YAML frontmatter delimiters (``---``).
# This regex strips the leading frontmatter block so the tokenizer
# receives only the Markdown body. The same pattern is used in
# test_parser_fixtures.py and test_parser_specimens.py.
_FRONTMATTER_RE = re.compile(r"\A\s*---\n.*?\n---\n?", re.DOTALL)


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter block from content for tokenization.

    Args:
        content: Raw or LF-normalized Markdown content.

    Returns:
        Content with leading ``---`` ... ``---`` block removed.
    """
    return _FRONTMATTER_RE.sub("", content, count=1)


class ParserAdapter:
    """Adapter implementing SingleFileValidator using the v0.2.0-v0.2.1 parser.

    This adapter wires the parser and enrichment modules into the
    protocol contract that the ecosystem pipeline expects. It is
    stateless across independent file-processing cycles, though it
    caches intermediate results (``FileMetadata``, ``Metadata``) from
    the most recent ``parse()`` call for use by ``classify()``.

    Example:
        >>> adapter = ParserAdapter()
        >>> parsed = adapter.parse("# Title\\n", "test.txt")
        >>> parsed.title
        'Title'

    Traces to: FR-080 (per-file validation within ecosystem)
    """

    def __init__(self) -> None:
        """Initialize the adapter with empty caches."""
        self._last_file_meta: FileMetadata | None = None
        self._last_metadata = None

    def parse(self, content: str, filename: str) -> ParsedLlmsTxt:
        """Parse raw content into a fully enriched structured model.

        Calls the full parser pipeline: read_string → strip frontmatter →
        tokenize → populate. Then applies enrichment: canonical section
        matching and metadata extraction.

        Args:
            content: Raw text content of the file.
            filename: The file's basename (e.g., "llms.txt").

        Returns:
            A fully populated ParsedLlmsTxt instance with canonical
            section names matched.
        """
        # Step 1: I/O layer — normalize line endings, compute FileMetadata
        normalized, file_meta = read_string(content)
        self._last_file_meta = file_meta

        # Step 2: Strip YAML frontmatter (tokenizer cannot handle ``---``)
        body = _strip_frontmatter(normalized)

        # Step 3: Tokenize
        tokens = tokenize(body)

        # Step 4: Populate the model
        doc = populate(tokens, raw_content=normalized, source_filename=filename)

        # Step 5: Enrichment — canonical section matching (v0.2.1c)
        match_canonical_sections(doc)

        # Step 6: Enrichment — metadata extraction (v0.2.1d)
        # ParsedLlmsTxt does not have a metadata field; the result is
        # stashed for potential future use when the model is extended.
        # TODO (v0.3.x): Store metadata on ParsedLlmsTxt when field is added.
        self._last_metadata = extract_metadata(normalized)

        logger.info(
            "Parsed %s: title=%s, sections=%d, links=%d",
            filename,
            doc.title,
            doc.section_count,
            doc.total_links,
        )

        return doc

    def classify(self, parsed: ParsedLlmsTxt) -> DocumentClassification:
        """Classify a parsed document by type and size.

        Uses the ``FileMetadata`` cached from the most recent ``parse()``
        call. If ``classify()`` is called independently (without a prior
        ``parse()``), reconstructs a minimal ``FileMetadata`` from the
        parsed document's ``raw_content``.

        Args:
            parsed: The parsed representation from ``parse()``.

        Returns:
            DocumentClassification with document_type and size_tier.
        """
        # Prefer cached FileMetadata from parse(); reconstruct if unavailable.
        # Reconstruction loses line_ending_style and has_bom but provides
        # accurate byte_count, which is what classify_document needs.
        file_meta = self._last_file_meta
        if file_meta is None:
            file_meta = FileMetadata(
                byte_count=len(parsed.raw_content.encode("utf-8")),
                encoding="utf-8",
            )

        classification = classify_document(parsed, file_meta)

        logger.info(
            "Classified %s: type=%s, tier=%s",
            parsed.source_filename,
            classification.document_type,
            classification.size_tier,
        )

        return classification

    def validate(
        self,
        parsed: ParsedLlmsTxt,
        classification: DocumentClassification,
    ) -> ValidationResult:
        """Stub: Return an empty validation result.

        The validation engine (v0.3.x) is not yet implemented.
        This stub allows the pipeline to complete without errors.

        Args:
            parsed: The parsed file content.
            classification: The file's classification.

        Returns:
            A ValidationResult with L0_PARSEABLE level and no diagnostics.
        """
        logger.info(
            "Validation stub for %s (v0.3.x not yet implemented)",
            parsed.source_filename,
        )
        return ValidationResult(
            level_achieved=ValidationLevel.L0_PARSEABLE,
            diagnostics=[],
        )

    def score(self, result: ValidationResult) -> QualityScore:
        """Stub: Return a zero quality score.

        The quality scorer (v0.4.x) is not yet implemented.
        This stub allows the pipeline to complete without errors.

        Args:
            result: The validation result.

        Returns:
            A QualityScore with total_score=0 and CRITICAL grade.
        """
        logger.info(
            "Scoring stub for %s (v0.4.x not yet implemented)",
            result.source_filename,
        )
        return QualityScore(
            total_score=0,
            grade=QualityGrade.CRITICAL,
            dimensions={
                QualityDimension.STRUCTURAL: DimensionScore(
                    dimension=QualityDimension.STRUCTURAL,
                    points=0,
                    max_points=30,
                    checks_passed=0,
                    checks_failed=0,
                    checks_total=0,
                ),
                QualityDimension.CONTENT: DimensionScore(
                    dimension=QualityDimension.CONTENT,
                    points=0,
                    max_points=50,
                    checks_passed=0,
                    checks_failed=0,
                    checks_total=0,
                ),
                QualityDimension.ANTI_PATTERN: DimensionScore(
                    dimension=QualityDimension.ANTI_PATTERN,
                    points=0,
                    max_points=20,
                    checks_passed=0,
                    checks_failed=0,
                    checks_total=0,
                ),
            },
        )
