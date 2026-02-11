"""File I/O and encoding detection for the DocStratum parser.

Implements v0.2.0a: reads a file from disk (or accepts raw string/bytes),
detects encoding characteristics, normalizes line endings for internal
processing, and produces a ``FileMetadata`` bundle that downstream
phases (tokenizer, model population) and the validator (v0.3.x) can inspect.

This is the first stage of the parser pipeline. It converts raw I/O into
clean, LF-normalized text that the tokenizer (v0.2.0b) can consume.

Classes:
    FileMetadata: Pydantic model capturing file-level encoding metadata.

Functions:
    read_file: Read a file from disk and return decoded content with metadata.
    read_string: Wrap a raw string with metadata for pipeline compatibility.
    read_bytes: Decode raw bytes with full encoding detection.

Related:
    - src/docstratum/schema/parsed.py: ParsedLlmsTxt model (populated downstream)
    - docs/design/03-parser/RR-SPEC-v0.2.0a-file-io-encoding.md: Design spec

Research basis:
    v0.0.1a §Edge Cases Category D (D1-D5)
    v0.0.4a §4 (File Format Requirements: UTF-8 only, LF only, no BOM)
"""

from __future__ import annotations

import logging
import re

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FileMetadata(BaseModel):
    """File-level metadata produced by the I/O layer.

    This model captures information about the raw file that the
    validator (v0.3.x) needs to emit encoding/format diagnostics
    (E003, E004, I005). The parser produces this metadata but does
    NOT interpret it as pass/fail.

    Attributes:
        byte_count: Raw file size in bytes (before decoding).
        encoding: Detected encoding ('utf-8', 'utf-8-bom', 'latin-1', 'unknown').
        has_bom: Whether a UTF-8 BOM was detected and stripped.
        has_null_bytes: Whether null bytes (0x00) were found (likely binary).
        line_ending_style: Dominant line ending ('lf', 'crlf', 'cr', 'mixed').
        line_count: Number of lines in the decoded content.
        decoding_error: If UTF-8 decoding failed, a description of the error.
            None on success.

    Example:
        >>> meta = FileMetadata(byte_count=1024, encoding="utf-8", line_count=42)
        >>> meta.has_bom
        False
        >>> meta.line_ending_style
        'lf'

    Traces to:
        v0.0.1a §Edge Cases D1-D5
        v0.0.4a §4 (File Format Requirements: UTF-8 only, LF only, no BOM)
    """

    byte_count: int = Field(ge=0, description="Raw file size in bytes.")
    encoding: str = Field(
        default="utf-8",
        description="Detected encoding: 'utf-8', 'utf-8-bom', 'latin-1', or 'unknown'.",
    )
    has_bom: bool = Field(
        default=False,
        description="Whether a UTF-8 BOM (0xEF 0xBB 0xBF) was detected and stripped.",
    )
    has_null_bytes: bool = Field(
        default=False,
        description="Whether null bytes (0x00) were found (likely binary file).",
    )
    line_ending_style: str = Field(
        default="lf",
        description="Dominant line ending: 'lf', 'crlf', 'cr', or 'mixed'.",
    )
    line_count: int = Field(
        ge=0,
        default=0,
        description="Number of lines in the decoded content.",
    )
    decoding_error: str | None = Field(
        default=None,
        description="Description of UTF-8 decoding failure, if any.",
    )


# ── UTF-8 BOM byte sequence ──────────────────────────────────────────
# Some Windows editors prepend this 3-byte sequence to UTF-8 files.
# The spec requires detecting and stripping it (v0.0.1a edge case D1).
_UTF8_BOM = b"\xef\xbb\xbf"


def _detect_line_endings(text: str) -> str:
    """Detect the dominant line ending style in decoded text.

    Scans the text for CRLF (``\\r\\n``), CR-only (``\\r``), and
    LF-only (``\\n``). Returns the dominant style. If multiple types
    are present, returns ``'mixed'``.

    The detection runs on the pre-normalization string so that
    original line endings are visible.

    Args:
        text: Decoded string content (before LF normalization).

    Returns:
        One of ``'lf'``, ``'crlf'``, ``'cr'``, or ``'mixed'``.
        Returns ``'lf'`` for single-line files with no line endings
        (the default per spec §4.2).

    Example:
        >>> _detect_line_endings("line1\\r\\nline2\\r\\n")
        'crlf'
        >>> _detect_line_endings("line1\\nline2\\n")
        'lf'
    """
    # Count CRLF first, then account for lone CR and lone LF.
    # Using regex to avoid double-counting \r\n as both \r and \n.
    crlf_count = len(re.findall(r"\r\n", text))
    # CR-only: \r NOT followed by \n
    cr_count = len(re.findall(r"\r(?!\n)", text))
    # LF-only: \n NOT preceded by \r
    lf_count = len(re.findall(r"(?<!\r)\n", text))

    types_present = []
    if crlf_count > 0:
        types_present.append("crlf")
    if lf_count > 0:
        types_present.append("lf")
    if cr_count > 0:
        types_present.append("cr")

    if len(types_present) == 0:
        # No line endings at all → single-line file, default to 'lf'
        return "lf"
    if len(types_present) == 1:
        return types_present[0]
    # Multiple types present → mixed
    return "mixed"


def _normalize_line_endings(text: str) -> str:
    """Normalize all line endings to LF (``\\n``).

    Two-pass replacement per spec §4.3 design decision:
    ``\\r\\n`` → ``\\n`` first, then ``\\r`` → ``\\n``. Doing
    ``\\r`` → ``\\n`` first would turn ``\\r\\n`` into ``\\n\\n``.

    Args:
        text: Decoded string with original line endings.

    Returns:
        String with all line endings replaced by ``\\n``.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_file(path: str) -> tuple[str, FileMetadata]:
    """Read a file from disk and return decoded content with metadata.

    The file is read as raw bytes, then decoded to a Python string.
    Encoding detection, BOM handling, and line ending normalization
    happen during this step.

    Args:
        path: Absolute or relative path to the file.

    Returns:
        A tuple of:
        - str: Decoded, LF-normalized file content.
        - FileMetadata: Encoding, line endings, BOM, null bytes, byte count.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.

    Example:
        >>> content, meta = read_file("examples/svelte-llms.txt")
        >>> meta.encoding
        'utf-8'
        >>> meta.has_bom
        False
        >>> meta.line_ending_style
        'lf'
        >>> len(content) > 0
        True
    """
    logger.info("Loading file from %s", path)

    # Let FileNotFoundError and PermissionError propagate naturally
    with open(path, "rb") as f:
        raw_bytes = f.read()

    content, metadata = read_bytes(raw_bytes)
    logger.info("Loaded %d bytes from %s", metadata.byte_count, path)
    return content, metadata


def read_string(content: str) -> tuple[str, FileMetadata]:
    """Wrap a raw string with minimal metadata for pipeline compatibility.

    No encoding detection is performed (strings are already decoded).
    Line endings are normalized to LF.

    Args:
        content: Raw Markdown content.

    Returns:
        A tuple of:
        - str: LF-normalized content.
        - FileMetadata: Byte count computed from UTF-8 encoding of the string.
                       encoding='utf-8', has_bom=False, has_null_bytes=False.

    Example:
        >>> content, meta = read_string("# Title\\r\\n> Description\\r\\n")
        >>> '\\r' not in content  # CRLF normalized to LF
        True
        >>> meta.line_ending_style
        'crlf'
    """
    # Compute byte count from UTF-8 encoding of the original string
    byte_count = len(content.encode("utf-8"))

    # Detect line endings before normalization
    line_ending_style = _detect_line_endings(content)

    # Normalize line endings to LF
    normalized = _normalize_line_endings(content)

    # Compute line count from normalized content
    line_count = normalized.count("\n") + 1 if normalized else 0

    metadata = FileMetadata(
        byte_count=byte_count,
        encoding="utf-8",
        has_bom=False,
        has_null_bytes=False,
        line_ending_style=line_ending_style,
        line_count=line_count,
    )

    return normalized, metadata


def read_bytes(data: bytes) -> tuple[str, FileMetadata]:
    """Decode raw bytes with encoding detection.

    Same logic as ``read_file()`` but accepts bytes directly.
    Useful for in-memory processing where the file has already been read.

    Performs the full encoding detection pipeline:
    1. Check for UTF-8 BOM → strip if found
    2. Scan for null bytes
    3. Attempt UTF-8 decode → fallback to Latin-1 on failure
    4. Detect line ending style (before normalization)
    5. Normalize all line endings to LF
    6. Compute line count

    Args:
        data: Raw file bytes.

    Returns:
        A tuple of (decoded string, FileMetadata).

    Example:
        >>> content, meta = read_bytes(b"# Title\\n> Desc\\n")
        >>> meta.encoding
        'utf-8'
        >>> meta.line_count
        3
    """
    byte_count = len(data)

    # -- Handle empty input --
    if byte_count == 0:
        logger.debug("Empty input (0 bytes)")
        return "", FileMetadata(byte_count=0, encoding="utf-8", line_count=0)

    has_bom = False
    has_null_bytes = False
    encoding = "utf-8"
    decoding_error: str | None = None

    # -- Step 1: Check for UTF-8 BOM (0xEF 0xBB 0xBF) --
    if data.startswith(_UTF8_BOM):
        has_bom = True
        encoding = "utf-8-bom"
        data = data[3:]  # Strip the 3-byte BOM prefix
        logger.debug("UTF-8 BOM detected and stripped")

    # -- Step 2: Scan for null bytes (0x00) --
    if b"\x00" in data:
        has_null_bytes = True
        logger.debug("Null bytes detected (likely binary file)")

    # -- Step 3: Attempt UTF-8 decode, fallback to Latin-1 --
    try:
        text = data.decode("utf-8")
        logger.debug("Detected encoding %s", encoding)
    except UnicodeDecodeError as e:
        # Latin-1 always succeeds (maps all 256 byte values)
        # per v0.0.1a edge case D2
        decoding_error = str(e)
        text = data.decode("latin-1")
        encoding = "latin-1"
        logger.debug("UTF-8 decode failed, fell back to Latin-1: %s", decoding_error)

    logger.debug("Detected encoding %s", encoding)

    # -- Step 4: Detect line endings (before normalization) --
    line_ending_style = _detect_line_endings(text)
    logger.debug("Detected line endings %s", line_ending_style)

    # -- Step 5: Normalize line endings to LF --
    normalized = _normalize_line_endings(text)

    # -- Step 6: Compute line count --
    line_count = normalized.count("\n") + 1 if normalized else 0

    metadata = FileMetadata(
        byte_count=byte_count,
        encoding=encoding,
        has_bom=has_bom,
        has_null_bytes=has_null_bytes,
        line_ending_style=line_ending_style,
        line_count=line_count,
        decoding_error=decoding_error,
    )

    return normalized, metadata
