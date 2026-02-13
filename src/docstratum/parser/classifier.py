"""Document type classifier for the DocStratum parser.

Implements v0.2.1a: inspects a parsed document and its file metadata to
determine which ``DocumentType`` it belongs to. Classification is the
first enrichment step -- the validator uses the document type to select
which rule set to apply.

The classifier uses a multi-signal decision tree based on empirical
findings from 11 real-world specimens (v0.0.1a section 6):

    1. Null byte detection (binary files)
    2. Empty/unparseable detection
    3. Filename conventions (llms-full.*, llms-instructions.*)
    4. File size threshold (TYPE_BOUNDARY_BYTES = 256,000)
    5. H1 heading count (>1 implies Type 2 Full)
    6. Link density (fallback heuristic)

Functions:
    classify_document_type: Classify a parsed document into a DocumentType.

Related:
    - src/docstratum/schema/classification.py: DocumentType enum, TYPE_BOUNDARY_BYTES
    - src/docstratum/parser/populator.py: Produces the ParsedLlmsTxt input
    - docs/design/03-parser/RR-SPEC-v0.2.1a-document-type-classification.md: Design spec

Research basis:
    v0.0.1a section 6 Empirical Validation (lines 496-592)
"""

from __future__ import annotations

import logging
import os

from docstratum.parser.io import FileMetadata
from docstratum.schema.classification import DocumentClassification, DocumentType
from docstratum.schema.parsed import ParsedLlmsTxt

logger = logging.getLogger(__name__)


def _count_h1_headings(raw_content: str) -> int:
    """Count H1 headings in raw content.

    Counts lines that start with '# ' (single hash + space).
    Lines starting with '## ' or '### ' are NOT counted.
    Lines inside code fences are NOT counted.

    Args:
        raw_content: The complete raw file text.

    Returns:
        Number of H1 headings found.
    """
    count = 0
    in_code_block = False
    for line in raw_content.splitlines():
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block and line.startswith("# ") and not line.startswith("## "):
            count += 1
    return count


def _classify_by_filename(filename: str) -> DocumentType | None:
    """Classify document type based on filename conventions.

    Recognized patterns:
        llms-full.txt, llms-full.md     -> TYPE_2_FULL
        llms-instructions.txt           -> TYPE_4_INSTRUCTIONS

    Args:
        filename: The source filename (may include path components).

    Returns:
        DocumentType if filename matches a pattern, None otherwise.
    """
    basename = os.path.basename(filename).lower()
    name_without_ext = os.path.splitext(basename)[0]

    if name_without_ext == "llms-full":
        return DocumentType.TYPE_2_FULL
    if name_without_ext == "llms-instructions":
        return DocumentType.TYPE_4_INSTRUCTIONS

    return None


def classify_document_type(
    doc: ParsedLlmsTxt,
    file_meta: FileMetadata,
) -> DocumentType:
    """Classify a parsed document into a DocumentType.

    Uses a multi-signal heuristic based on empirical findings from
    11 real-world specimens (v0.0.1a section 6):
    - File size (byte count)
    - H1 header count (inferred from raw content)
    - Filename conventions
    - Content patterns

    The classifier does NOT modify the ParsedLlmsTxt instance.

    Args:
        doc: Parsed document from v0.2.0.
        file_meta: File metadata from v0.2.0a.

    Returns:
        A DocumentType enum value.

    Example:
        >>> from docstratum.parser.io import FileMetadata
        >>> from docstratum.schema.parsed import ParsedLlmsTxt, ParsedSection
        >>> doc = ParsedLlmsTxt(title="My App", sections=[ParsedSection(name="Docs")])
        >>> doc.raw_content = "# My App"
        >>> meta = FileMetadata(byte_count=50)
        >>> classify_document_type(doc, meta)
        <DocumentType.TYPE_1_INDEX: 'type_1_index'>
    """
    # Step 1: Binary file detection
    if file_meta.has_null_bytes:
        logger.info("Classified as UNKNOWN: null bytes detected")
        return DocumentType.UNKNOWN

    # Step 2: Empty/unparseable detection
    if doc.title is None and doc.sections == []:
        logger.info("Classified as UNKNOWN: no title and no sections")
        return DocumentType.UNKNOWN

    # Step 3: Filename conventions (strongest signal)
    filename_type = _classify_by_filename(doc.source_filename)
    if filename_type is not None:
        logger.info(
            "Classified as %s by filename convention: %s",
            filename_type.value,
            doc.source_filename,
        )
        return filename_type

    # Step 4: File size threshold
    if file_meta.byte_count > DocumentClassification.TYPE_BOUNDARY_BYTES:
        logger.info(
            "Classified as TYPE_2_FULL: byte_count %s > %s",
            file_meta.byte_count,
            DocumentClassification.TYPE_BOUNDARY_BYTES,
        )
        return DocumentType.TYPE_2_FULL

    # Step 5: H1 count (multiple H1s = documentation dump)
    h1_count = _count_h1_headings(doc.raw_content)
    if h1_count > 1:
        logger.info(
            "Classified as TYPE_2_FULL: %s H1 headings found",
            h1_count,
        )
        return DocumentType.TYPE_2_FULL

    # Step 6: Link density (fallback)
    has_links = any(len(s.links) > 0 for s in doc.sections)
    if has_links:
        logger.info("Classified as TYPE_1_INDEX: sections with links found")
        return DocumentType.TYPE_1_INDEX

    # Check for prose-heavy content (sections with content but no links)
    has_prose = any(s.raw_content.strip() for s in doc.sections)
    if has_prose:
        logger.info("Classified as TYPE_2_FULL: prose content without links")
        return DocumentType.TYPE_2_FULL

    # Default: structurally conformant but sparse
    logger.info("Classified as TYPE_1_INDEX: default (sparse but conformant)")
    return DocumentType.TYPE_1_INDEX
