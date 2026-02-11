"""Tests for the parser I/O module (v0.2.0a).

Tests cover file reading, encoding detection, BOM handling, null byte
detection, line ending detection/normalization, and edge cases.
See RR-META-testing-standards for naming conventions and fixture patterns.
"""

import pytest

from docstratum.parser.io import FileMetadata, read_bytes, read_file, read_string


class TestReadFile:
    """Tests for read_file() — file-based I/O with encoding detection."""

    def test_read_file_utf8_file_returns_content_and_metadata(self, tmp_path):
        """Verify that a clean UTF-8 file is decoded correctly."""
        # Arrange
        f = tmp_path / "clean.txt"
        f.write_text("# Title\n> Description\n", encoding="utf-8")

        # Act
        content, meta = read_file(str(f))

        # Assert
        assert content == "# Title\n> Description\n"
        assert meta.encoding == "utf-8"
        assert meta.has_bom is False
        assert meta.has_null_bytes is False

    def test_read_file_utf8_bom_file_strips_bom(self, tmp_path):
        """Verify that UTF-8 BOM is stripped and metadata flags it (D1)."""
        # Arrange
        bom = b"\xef\xbb\xbf"
        f = tmp_path / "bom.txt"
        f.write_bytes(bom + b"# Title\n")

        # Act
        content, meta = read_file(str(f))

        # Assert
        assert content == "# Title\n"
        assert not content.startswith("\ufeff")  # BOM character should be gone
        assert meta.encoding == "utf-8-bom"
        assert meta.has_bom is True

    def test_read_file_latin1_fallback_decodes_with_latin1(self, tmp_path):
        """Verify Latin-1 fallback when UTF-8 decoding fails (D2)."""
        # Arrange — Latin-1 bytes that are not valid UTF-8
        latin1_bytes = "caf\xe9 na\xefve \xfc".encode("latin-1")
        f = tmp_path / "latin1.txt"
        f.write_bytes(latin1_bytes)

        # Act
        content, meta = read_file(str(f))

        # Assert
        assert meta.encoding == "latin-1"
        assert meta.decoding_error is not None
        assert "café" in content or "caf" in content  # Latin-1 decoded

    def test_read_file_null_bytes_detected(self, tmp_path):
        """Verify null byte detection for likely binary files (D3)."""
        # Arrange
        f = tmp_path / "binary.txt"
        f.write_bytes(b"# Title\x00\nContent\n")

        # Act
        content, meta = read_file(str(f))

        # Assert
        assert meta.has_null_bytes is True
        assert "\x00" in content  # Null byte preserved in decoded content

    def test_read_file_crlf_normalized_to_lf(self, tmp_path):
        """Verify CRLF line endings are normalized to LF (D4)."""
        # Arrange
        f = tmp_path / "crlf.txt"
        f.write_bytes(b"line1\r\nline2\r\nline3\r\n")

        # Act
        content, meta = read_file(str(f))

        # Assert
        assert "\r" not in content
        assert content == "line1\nline2\nline3\n"
        assert meta.line_ending_style == "crlf"

    def test_read_file_cr_normalized_to_lf(self, tmp_path):
        """Verify CR-only line endings are normalized to LF (D5)."""
        # Arrange
        f = tmp_path / "cr.txt"
        f.write_bytes(b"line1\rline2\rline3\r")

        # Act
        content, meta = read_file(str(f))

        # Assert
        assert "\r" not in content
        assert content == "line1\nline2\nline3\n"
        assert meta.line_ending_style == "cr"

    def test_read_file_empty_file_returns_empty_string(self, tmp_path):
        """Verify empty file returns empty string with zero byte count."""
        # Arrange
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")

        # Act
        content, meta = read_file(str(f))

        # Assert
        assert content == ""
        assert meta.byte_count == 0
        assert meta.encoding == "utf-8"

    def test_read_file_whitespace_only_returns_string(self, tmp_path):
        """Verify whitespace-only file is returned as-is with metadata."""
        # Arrange
        f = tmp_path / "whitespace.txt"
        f.write_text("\n\n  \n", encoding="utf-8")

        # Act
        content, meta = read_file(str(f))

        # Assert
        assert content == "\n\n  \n"
        assert meta.byte_count > 0
        assert meta.line_count > 0

    def test_read_file_not_found_raises_error(self):
        """Verify FileNotFoundError propagates for non-existent files."""
        # Act / Assert
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/path/to/file.txt")

    def test_read_file_line_count_matches(self, tmp_path):
        """Verify line_count matches the actual number of lines."""
        # Arrange
        f = tmp_path / "multiline.txt"
        f.write_text("line1\nline2\nline3\n", encoding="utf-8")

        # Act
        content, meta = read_file(str(f))

        # Assert — 3 lines of text + trailing newline = 4 lines
        # (count of \n + 1, where trailing \n means last "line" is empty)
        assert meta.line_count == content.count("\n") + 1


class TestReadString:
    """Tests for read_string() — string wrapping with metadata."""

    def test_read_string_normalizes_line_endings(self):
        """Verify CRLF in strings is normalized to LF."""
        # Arrange
        raw = "# Title\r\n> Description\r\n"

        # Act
        content, meta = read_string(raw)

        # Assert
        assert "\r" not in content
        assert content == "# Title\n> Description\n"
        assert meta.line_ending_style == "crlf"

    def test_read_string_metadata_defaults(self):
        """Verify string metadata has expected defaults."""
        # Arrange
        raw = "Hello, world!"

        # Act
        _content, meta = read_string(raw)

        # Assert
        assert meta.encoding == "utf-8"
        assert meta.has_bom is False
        assert meta.has_null_bytes is False
        assert meta.byte_count == len(raw.encode("utf-8"))


class TestReadBytes:
    """Tests for read_bytes() — raw byte decoding with encoding detection."""

    def test_read_bytes_utf8_decodes_correctly(self):
        """Verify clean UTF-8 bytes are decoded successfully."""
        # Arrange
        data = b"# Hello\n> World\n"

        # Act
        content, meta = read_bytes(data)

        # Assert
        assert content == "# Hello\n> World\n"
        assert meta.encoding == "utf-8"


class TestLineEndingDetection:
    """Tests for line ending detection logic across all styles."""

    def test_detect_lf_endings_returns_lf(self):
        """Verify LF-only files are detected correctly."""
        # Arrange
        data = b"line1\nline2\nline3\n"

        # Act
        _, meta = read_bytes(data)

        # Assert
        assert meta.line_ending_style == "lf"

    def test_detect_crlf_endings_returns_crlf(self):
        """Verify CRLF-only files are detected correctly."""
        # Arrange
        data = b"line1\r\nline2\r\nline3\r\n"

        # Act
        _, meta = read_bytes(data)

        # Assert
        assert meta.line_ending_style == "crlf"

    def test_detect_cr_endings_returns_cr(self):
        """Verify CR-only files are detected correctly (classic Mac)."""
        # Arrange
        data = b"line1\rline2\rline3\r"

        # Act
        _, meta = read_bytes(data)

        # Assert
        assert meta.line_ending_style == "cr"

    def test_detect_mixed_endings_returns_mixed(self):
        """Verify mixed CRLF and LF files are detected correctly."""
        # Arrange — contains both \r\n and \n
        data = b"line1\r\nline2\nline3\r\n"

        # Act
        _, meta = read_bytes(data)

        # Assert
        assert meta.line_ending_style == "mixed"


class TestFileMetadataModel:
    """Tests for the FileMetadata Pydantic model itself."""

    def test_file_metadata_is_pydantic_model(self):
        """Verify FileMetadata is a Pydantic BaseModel with validation."""
        # Arrange / Act
        meta = FileMetadata(byte_count=100)

        # Assert
        assert meta.byte_count == 100
        assert meta.encoding == "utf-8"
        assert meta.has_bom is False
        assert meta.has_null_bytes is False
        assert meta.line_ending_style == "lf"
        assert meta.line_count == 0
        assert meta.decoding_error is None

    def test_file_metadata_rejects_negative_byte_count(self):
        """Verify byte_count field constraint ge=0."""
        with pytest.raises(ValueError):
            FileMetadata(byte_count=-1)
