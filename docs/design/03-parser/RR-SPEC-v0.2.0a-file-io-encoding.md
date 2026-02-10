# v0.2.0a — File I/O & Encoding Detection

> **Version:** v0.2.0a
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.0-core-parser.md](RR-SPEC-v0.2.0-core-parser.md)
> **Grounding:** [v0.0.1a §Edge Cases Category D](../01-research/RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md) (D1–D5), [v0.0.4a §4](../01-research/) (File Format Requirements)
> **Module:** `src/docstratum/parser/io.py`
> **Tests:** `tests/test_parser_io.py`

---

## 1. Purpose

Read a file from disk (or accept raw string/bytes input), detect encoding characteristics, normalize line endings for internal processing, and produce a file-level metadata bundle. This is the first stage of the parser pipeline — it converts raw I/O into clean decoded text that the tokenizer can consume.

---

## 2. Interface Contract

### 2.1 `read_file(path: str) -> tuple[str, FileMetadata]`

```python
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
```

### 2.2 `read_string(content: str) -> tuple[str, FileMetadata]`

```python
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
```

### 2.3 `read_bytes(data: bytes) -> tuple[str, FileMetadata]`

```python
def read_bytes(data: bytes) -> tuple[str, FileMetadata]:
    """Decode raw bytes with encoding detection.

    Same logic as read_file() but accepts bytes directly.
    Useful for in-memory processing where the file has already been read.

    Args:
        data: Raw file bytes.

    Returns:
        A tuple of (decoded string, FileMetadata).
    """
```

---

## 3. FileMetadata Model

```python
from pydantic import BaseModel, Field


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
        decoding_error: If UTF-8 decoding failed, a description of the error. None on success.

    Traces to:
        v0.0.1a §Edge Cases D1–D5
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
```

---

## 4. Behavior Specification

### 4.1 Encoding Detection & Decoding

```
1. Read raw bytes from file
2. Check for UTF-8 BOM (0xEF 0xBB 0xBF) at start:
   ├── Found → Strip BOM, set has_bom=True, set encoding='utf-8-bom'
   └── Not found → Continue
3. Scan for null bytes (0x00):
   ├── Found → Set has_null_bytes=True (likely binary)
   └── Not found → Continue
4. Attempt UTF-8 decode:
   ├── Success → Set encoding='utf-8' (or 'utf-8-bom' if BOM was found)
   └── Failure (UnicodeDecodeError) →
       ├── Record decoding_error with exception message
       ├── Attempt Latin-1 fallback (always succeeds, since Latin-1 maps all 256 byte values)
       └── Set encoding='latin-1'
5. Record byte_count = len(raw_bytes)
```

### 4.2 Line Ending Detection

After decoding to a string (but **before** normalization):

```python
def _detect_line_endings(text: str) -> str:
    """Detect the dominant line ending style.

    Scans the text for CRLF (\\r\\n), CR-only (\\r), and LF-only (\\n).
    Returns the dominant style. If both CRLF and LF/CR are present, returns 'mixed'.

    Decision logic:
        - Count occurrences of \\r\\n (CRLF)
        - Count occurrences of \\n not preceded by \\r (LF-only)
        - Count occurrences of \\r not followed by \\n (CR-only)
        - If only one type present → return that type
        - If multiple types present → return 'mixed'
        - If no line endings at all → return 'lf' (single-line file, default)
    """
```

### 4.3 Line Ending Normalization

After detection, normalize **all** line endings to LF (`\n`):

```python
normalized = text.replace('\r\n', '\n').replace('\r', '\n')
```

The original `raw_content` on `ParsedLlmsTxt` preserves the pre-normalization text for round-trip fidelity. However, all internal tokenization operates on the LF-normalized version.

> **Design Decision:** Normalize in two passes (`\r\n` → `\n` first, then `\r` → `\n`) to avoid double-conversion. Doing `\r` → `\n` first would turn `\r\n` into `\n\n`.

### 4.4 Empty and Binary Files

| Scenario                  | Behavior                                                                                                                                           |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Empty file (0 bytes)      | Return `("", FileMetadata(byte_count=0, encoding='utf-8'))`                                                                                        |
| File with only whitespace | Return the whitespace string with metadata — parser treats this as an empty document                                                               |
| Binary file (null bytes)  | Record `has_null_bytes=True`, attempt decode anyway. The resulting string may contain `\x00` characters — the validator decides how to handle this |
| File not found            | Raise `FileNotFoundError` (do not catch — let the caller handle)                                                                                   |
| Permission error          | Raise `PermissionError` (do not catch)                                                                                                             |

---

## 5. Edge Cases (from v0.0.1a Category D)

| ID  | Scenario              | What `read_file` Does                    | `FileMetadata` Values                        |
| --- | --------------------- | ---------------------------------------- | -------------------------------------------- |
| D1  | UTF-8 with BOM        | Strip 3-byte BOM, decode as UTF-8        | `encoding='utf-8-bom'`, `has_bom=True`       |
| D2  | Non-UTF-8 (Latin-1)   | UTF-8 decode fails, fallback to Latin-1  | `encoding='latin-1'`, `decoding_error="..."` |
| D3  | Null bytes in file    | Record null byte presence, decode anyway | `has_null_bytes=True`                        |
| D4  | Windows CRLF (`\r\n`) | Detect as CRLF, normalize to LF          | `line_ending_style='crlf'`                   |
| D5  | Classic Mac CR (`\r`) | Detect as CR, normalize to LF            | `line_ending_style='cr'`                     |

---

## 6. Acceptance Criteria

- [ ] `read_file()` reads a UTF-8 file and returns `(str, FileMetadata)`.
- [ ] `read_file()` strips UTF-8 BOM and sets `has_bom=True`.
- [ ] `read_file()` falls back to Latin-1 on UTF-8 decode failure.
- [ ] `read_file()` detects null bytes and sets `has_null_bytes=True`.
- [ ] `read_file()` correctly identifies `lf`, `crlf`, `cr`, and `mixed` line endings.
- [ ] `read_file()` normalizes all line endings to `\n` in the returned string.
- [ ] `read_string()` normalizes line endings and returns accurate metadata.
- [ ] `read_bytes()` performs full encoding detection on raw bytes.
- [ ] Empty files return `("", FileMetadata(byte_count=0))`.
- [ ] `FileNotFoundError` and `PermissionError` propagate without catching.
- [ ] `FileMetadata` is a Pydantic `BaseModel` with all fields validated.
- [ ] No `DiagnosticCode` instances are referenced or emitted.
- [ ] Google-style docstrings on all public functions.
- [ ] Module docstring references "Implements v0.2.0a".

---

## 7. Test Plan

### `tests/test_parser_io.py`

| Test                          | Input                                   | Expected                                                                |
| ----------------------------- | --------------------------------------- | ----------------------------------------------------------------------- |
| `test_read_utf8_file`         | A clean UTF-8 file                      | Content decoded, `encoding='utf-8'`                                     |
| `test_read_utf8_bom_file`     | UTF-8 file with BOM prefix              | BOM stripped, `encoding='utf-8-bom'`, `has_bom=True`                    |
| `test_read_latin1_fallback`   | Latin-1 encoded file with `é`, `ñ`, `ü` | Content decoded via Latin-1, `encoding='latin-1'`, `decoding_error` set |
| `test_read_null_bytes`        | File with embedded `\x00`               | `has_null_bytes=True`, content includes null as decoded                 |
| `test_detect_lf_endings`      | File with `\n` only                     | `line_ending_style='lf'`                                                |
| `test_detect_crlf_endings`    | File with `\r\n` only                   | `line_ending_style='crlf'`                                              |
| `test_detect_cr_endings`      | File with `\r` only                     | `line_ending_style='cr'`                                                |
| `test_detect_mixed_endings`   | File with both `\r\n` and `\n`          | `line_ending_style='mixed'`                                             |
| `test_normalize_crlf_to_lf`   | File with `\r\n`                        | Returned string contains only `\n`                                      |
| `test_normalize_cr_to_lf`     | File with `\r`                          | Returned string contains only `\n`                                      |
| `test_empty_file`             | 0-byte file                             | `("", FileMetadata(byte_count=0))`                                      |
| `test_whitespace_only_file`   | `"\n\n  \n"`                            | String returned as-is, metadata populated                               |
| `test_file_not_found`         | Non-existent path                       | `FileNotFoundError` raised                                              |
| `test_read_string_normalizes` | `"# Title\r\n"`                         | `\r\n` → `\n`, `line_ending_style='crlf'`                               |
| `test_read_string_metadata`   | Any string                              | `encoding='utf-8'`, `has_bom=False`, byte count computed                |
| `test_line_count`             | Multi-line file                         | `line_count` matches actual line count                                  |
