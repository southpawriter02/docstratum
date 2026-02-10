# v0.2.0 — Core Parser

> **Version:** v0.2.0
> **Document Type:** Design Specification (scope overview with sub-part breakdown)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Last Updated:** 2026-02-10
> **Parent:** [RR-SCOPE-v0.2.x-parser.md](RR-SCOPE-v0.2.x-parser.md)
> **Research Basis:** [v0.0.1a](../01-research/RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md) (ABNF grammar, reference parser, 33 edge cases)
> **Consumes:** [v0.1.2a](../02-foundation/RR-SPEC-v0.1.2a-diagnostic-infrastructure.md) (`DiagnosticCode`, `constants.py`), [v0.1.2b](../02-foundation/RR-SPEC-v0.1.2b-document-models.md) (`ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`, `ParsedBlockquote`)
> **Consumed By:** v0.2.1 (Classification & Metadata), v0.3.x (Validation Engine)

---

## 1. Purpose

v0.2.0 implements the **core parser** — the component that reads a raw `llms.txt` Markdown file and transforms it into a fully populated `ParsedLlmsTxt` Pydantic model. This is the first runtime logic in the DocStratum validator. Everything downstream depends on the fidelity of this model.

The parser follows the **"permissive input, strict output"** principle (v0.0.1a): it accepts malformed, partial, or non-conformant files and extracts as much structure as possible. It never rejects a file outright — it always returns a `ParsedLlmsTxt`, even for empty or binary inputs.

### 1.1 User Stories

| ID       | As a...             | I want to...                                                                   | So that...                                                                               |
| -------- | ------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| US-020-1 | CLI user            | Pass a file path to the parser and get a `ParsedLlmsTxt` back                  | I can inspect the parsed structure before validation                                     |
| US-020-2 | Pipeline consumer   | Call `parse(content)` with a raw string and get the same result as from a file | I can parse in-memory content without a filesystem                                       |
| US-020-3 | Validator developer | Rely on the parser to populate all fields or set them to `None`/empty          | I can write validation rules that check field presence without worrying about exceptions |
| US-020-4 | Debugging developer | See line numbers on every parsed element                                       | I can trace parser output back to specific lines in the source file                      |

---

## 2. Architecture

### 2.1 Module Structure

```
src/docstratum/parser/
├── __init__.py        # Public API: parse_file(), parse_string()
├── io.py              # v0.2.0a — File I/O & encoding detection
├── tokenizer.py       # v0.2.0b — Markdown tokenization
├── populator.py       # v0.2.0c — Model population from token stream
└── tokens.py          # v0.2.0b — Token type definitions
```

### 2.2 Data Flow

```
                   ┌──────────────┐
                   │  File Path   │
                   │  or String   │
                   └──────┬───────┘
                          │
                   ┌──────▼───────┐
                   │  v0.2.0a     │
                   │  File I/O &  │──── FileMetadata
                   │  Encoding    │     (encoding, line endings,
                   └──────┬───────┘      BOM, null bytes, byte count)
                          │
                   decoded string
                   (LF-normalized)
                          │
                   ┌──────▼───────┐
                   │  v0.2.0b     │
                   │  Tokenizer   │──── list[Token]
                   │              │     (H1, H2, BLOCKQUOTE,
                   └──────┬───────┘      LINK_ENTRY, CODE_FENCE,
                          │              BLANK, TEXT)
                   token stream
                          │
                   ┌──────▼───────┐
                   │  v0.2.0c     │
                   │  Populator   │──── ParsedLlmsTxt
                   │  (5 phases)  │     (fully populated or
                   └──────┬───────┘      safely empty)
                          │
                   ┌──────▼───────┐
                   │  v0.2.0d     │
                   │  Token Est.  │──── ParsedLlmsTxt
                   │  (in-place)  │     (.estimated_tokens set
                   └──────────────┘      on each ParsedSection)
```

### 2.3 Decision Tree: Parser Behavior

```
Input received
├── File path?
│   ├── File exists?
│   │   ├── YES → Read as bytes → attempt UTF-8 decode
│   │   │   ├── UTF-8 success → decoded string, encoding=UTF-8
│   │   │   └── UTF-8 failure → Latin-1 fallback, encoding=UNKNOWN
│   │   └── NO → return empty ParsedLlmsTxt, metadata.error="file_not_found"
│   └── (continue to tokenization)
├── Raw string?
│   └── Use directly, encoding=UTF-8 (assumed), no file metadata
└── Raw bytes?
    └── Attempt UTF-8 decode → same as file path branch
```

---

## 3. Sub-Part Breakdown

v0.2.0 is divided into 4 sub-parts that form a strict sequential pipeline:

| Sub-Part                                            | Title                         | Input                               | Output                                    | Module                                                    |
| --------------------------------------------------- | ----------------------------- | ----------------------------------- | ----------------------------------------- | --------------------------------------------------------- |
| [v0.2.0a](RR-SPEC-v0.2.0a-file-io-encoding.md)      | File I/O & Encoding Detection | File path, raw string, or raw bytes | Decoded string + `FileMetadata`           | `parser/io.py`                                            |
| [v0.2.0b](RR-SPEC-v0.2.0b-markdown-tokenization.md) | Markdown Tokenization         | Decoded string                      | `list[Token]`                             | `parser/tokenizer.py`, `parser/tokens.py`                 |
| [v0.2.0c](RR-SPEC-v0.2.0c-model-population.md)      | Model Population              | Token stream + source filename      | `ParsedLlmsTxt`                           | `parser/populator.py`                                     |
| [v0.2.0d](RR-SPEC-v0.2.0d-token-estimation.md)      | Token Estimation              | `ParsedLlmsTxt` (from 0c)           | Same instance with `estimated_tokens` set | (inline in `parser/populator.py` or `parser/__init__.py`) |

### Dependency Chain

```
v0.2.0a → v0.2.0b → v0.2.0c → v0.2.0d
```

There is no parallelization within v0.2.0. Each sub-part produces output consumed by the next.

---

## 4. Public API

```python
# src/docstratum/parser/__init__.py

from docstratum.parser.io import FileMetadata, read_file, read_string
from docstratum.parser.tokenizer import tokenize
from docstratum.parser.populator import populate
from docstratum.schema.parsed import ParsedLlmsTxt


def parse_file(
    file_path: str,
    *,
    source_filename: str | None = None,
) -> tuple[ParsedLlmsTxt, FileMetadata]:
    """Parse an llms.txt file from disk.

    Args:
        file_path: Absolute or relative path to the .txt/.md file.
        source_filename: Override for the source_filename field.
                         Defaults to the basename of file_path.

    Returns:
        A tuple of (ParsedLlmsTxt, FileMetadata).
        The ParsedLlmsTxt is always returned — even for empty or
        binary files, it will contain safe defaults.

    Example:
        >>> doc, meta = parse_file("examples/svelte-llms.txt")
        >>> doc.title
        'Svelte'
        >>> doc.section_count
        7
        >>> meta.encoding
        'utf-8'
    """
    content, metadata = read_file(file_path)
    tokens = tokenize(content)
    filename = source_filename or _basename(file_path)
    doc = populate(tokens, raw_content=content, source_filename=filename)
    return doc, metadata


def parse_string(
    content: str,
    *,
    source_filename: str = "llms.txt",
) -> ParsedLlmsTxt:
    """Parse an llms.txt file from a raw string.

    Args:
        content: The raw Markdown content.
        source_filename: Value for the source_filename field.

    Returns:
        A fully populated ParsedLlmsTxt instance.

    Example:
        >>> doc = parse_string("# My Project\\n> A description\\n## Docs\\n")
        >>> doc.title
        'My Project'
        >>> doc.has_blockquote
        True
    """
    tokens = tokenize(content)
    return populate(tokens, raw_content=content, source_filename=source_filename)
```

### 4.1 API Design Decisions

| Decision                           | Choice                                 | Rationale                                                                                                                                                              |
| ---------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Two entry points                   | `parse_file()` and `parse_string()`    | File I/O adds metadata (encoding, BOM, line endings) that string input doesn't have. Separate functions make the contract explicit.                                    |
| `FileMetadata` returned separately | Not embedded in `ParsedLlmsTxt`        | The `ParsedLlmsTxt` model is defined in v0.1.2b and must not be modified. File metadata is parser-specific context that the validator consumes via a separate channel. |
| No exceptions for malformed input  | Always returns `ParsedLlmsTxt`         | Matches the "permissive input" principle. The validator decides what constitutes an error.                                                                             |
| `source_filename` overridable      | Keyword argument with sensible default | Ecosystem pipeline may need to set this to a relative path within the ecosystem root.                                                                                  |

---

## 5. Models Consumed (Not Modified)

The parser populates instances of these models defined in v0.1.2b. It does **not** add, remove, or modify any fields.

| Model              | Fields Parser Populates                                                                        | Fields Left as Default                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `ParsedLlmsTxt`    | `title`, `title_line`, `blockquote`, `sections`, `raw_content`, `source_filename`, `parsed_at` | None — all fields populated                                               |
| `ParsedSection`    | `name`, `links`, `raw_content`, `line_number`                                                  | `canonical_name` (v0.2.1c), `estimated_tokens` (v0.2.0d sets this)        |
| `ParsedLink`       | `title`, `url`, `description`, `line_number`, `is_valid_url`                                   | `relationship` (UNKNOWN), `resolves_to` (None), `target_file_type` (None) |
| `ParsedBlockquote` | `text`, `line_number`, `raw`                                                                   | None — all fields populated                                               |

### 5.1 New Models Introduced by v0.2.0

| Model          | Module             | Purpose                                                                                          |
| -------------- | ------------------ | ------------------------------------------------------------------------------------------------ |
| `FileMetadata` | `parser/io.py`     | Encoding, line endings, BOM, null bytes, byte count — file-level metadata not in `ParsedLlmsTxt` |
| `Token`        | `parser/tokens.py` | Tagged line with type, line number, and raw content                                              |
| `TokenType`    | `parser/tokens.py` | Enum: `H1`, `H2`, `H3_PLUS`, `BLOCKQUOTE`, `LINK_ENTRY`, `CODE_FENCE`, `BLANK`, `TEXT`           |

> **Note:** These models are internal to the parser module. They are not exported from `docstratum.schema` and are not part of the public schema API.

---

## 6. Workflows

### 6.1 Single-File Parse Workflow

```
1. User invokes: doc, meta = parse_file("path/to/llms.txt")
2. io.read_file() reads bytes, detects encoding, normalizes line endings
3. tokenizer.tokenize() scans lines into Token stream
4. populator.populate() walks tokens through 5 phases:
   Phase 1: H1 title extraction
   Phase 2: Blockquote extraction
   Phase 3: Body content consumption
   Phase 4: Section & link extraction
   Phase 5: Final assembly (raw_content, parsed_at, source_filename)
5. Token estimation: estimated_tokens set on each ParsedSection
6. Return (ParsedLlmsTxt, FileMetadata)
```

### 6.2 Pipeline Integration Workflow (v0.2.2d)

```
1. EcosystemPipeline Stage 2 calls SingleFileValidator.validate(path, content)
2. SingleFileValidator delegates to parse_string(content, source_filename=path)
3. ParsedLlmsTxt stored on EcosystemFile for downstream stages
4. No ValidationResult or QualityScore yet — those come in v0.3.x / v0.4.x
```

---

## 7. Acceptance Criteria

### 7.1 Functional

- [ ] `parse_file()` accepts a file path and returns `(ParsedLlmsTxt, FileMetadata)`.
- [ ] `parse_string()` accepts a raw string and returns `ParsedLlmsTxt`.
- [ ] Empty files produce `ParsedLlmsTxt(title=None, sections=[], raw_content="")`.
- [ ] Files with only an H1 produce `ParsedLlmsTxt(title="...", sections=[])`.
- [ ] Multi-section files populate all `ParsedSection` instances with correct `line_number` values.
- [ ] Link entries are parsed with `title`, `url`, `description` (or `None`), and `is_valid_url`.
- [ ] Fenced code blocks do not produce false H1/H2/link tokens.
- [ ] Blockquote text is stripped of `> ` prefixes; `raw` field preserves them.
- [ ] `estimated_tokens` is set on every `ParsedSection` (via v0.2.0d).
- [ ] `raw_content` on `ParsedLlmsTxt` contains the complete original file text.

### 7.2 Non-Functional

- [ ] No new fields added to any v0.1.2 Pydantic model.
- [ ] No `DiagnosticCode` instances emitted by the parser.
- [ ] `pytest --cov=docstratum.parser --cov-fail-under=85` passes.
- [ ] `black --check` and `ruff check` pass on all new code.
- [ ] All functions have Google-style docstrings.
- [ ] Module-level docstrings reference the spec version (e.g., "Implements v0.2.0a").

### 7.3 CHANGELOG Entry Template

```markdown
## [0.2.0] - YYYY-MM-DD

**Core Parser — Markdown → ParsedLlmsTxt structural extraction.**

### Added

#### Parser Module (`src/docstratum/parser/`)

- `parser/io.py` — File I/O with UTF-8 encoding detection, BOM stripping, line ending normalization, null byte scanning, and Latin-1 fallback (v0.2.0a)
- `parser/tokens.py` — `TokenType` enum (H1, H2, H3_PLUS, BLOCKQUOTE, LINK_ENTRY, CODE_FENCE, BLANK, TEXT) and `Token` dataclass (v0.2.0b)
- `parser/tokenizer.py` — Line-by-line Markdown tokenizer with code block state tracking (v0.2.0b)
- `parser/populator.py` — 5-phase model population: H1 title → blockquote → body → sections/links → assembly (v0.2.0c)
- `parser/__init__.py` — Public API: `parse_file()` → `(ParsedLlmsTxt, FileMetadata)`, `parse_string()` → `ParsedLlmsTxt` (v0.2.0)
- Estimated token counts populated on each `ParsedSection` via `len(raw_content) // 4` heuristic (v0.2.0d)

#### Tests (`tests/`)

- `tests/test_parser_io.py` — Encoding detection, BOM handling, line ending normalization, null byte detection (v0.2.0a)
- `tests/test_parser_tokenizer.py` — Token type assignment, code block state, line number tracking (v0.2.0b)
- `tests/test_parser_populator.py` — 5-phase population, empty files, partial files, multi-section documents (v0.2.0c)
- `tests/test_parser_integration.py` — End-to-end parse_file() and parse_string() tests (v0.2.0)
```

---

## 8. Dependencies

### 8.1 Internal (v0.1.x Schema)

| Module                  | What v0.2.0 Uses                                                                       |
| ----------------------- | -------------------------------------------------------------------------------------- |
| `schema/parsed.py`      | `ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`, `ParsedBlockquote`, `LinkRelationship` |
| `schema/constants.py`   | `CanonicalSectionName` (for future v0.2.1c, not used in v0.2.0)                        |
| `schema/diagnostics.py` | **Not used** — parser does not emit diagnostics                                        |

### 8.2 External (PyPI)

| Package    | Used By        | Purpose                         |
| ---------- | -------------- | ------------------------------- |
| `pydantic` | `parser/io.py` | `FileMetadata` model definition |

> **Note on mistletoe:** The roadmap (v0.2.0b) suggests using mistletoe (DECISION-003). The scope doc permits either a purpose-built line scanner or mistletoe. **v0.2.0b specifies a line scanner** because the `llms.txt` format is a constrained Markdown subset that does not require full AST parsing. If implementation reveals that a full parser is needed (e.g., for nested code blocks), the decision should be documented in the v0.2.0b spec's implementation notes.

### 8.3 Limitations

| Limitation                           | Reason                                | When Addressed |
| ------------------------------------ | ------------------------------------- | -------------- |
| No URL reachability checks           | Parser does syntactic validation only | v0.3.2b        |
| No canonical section matching        | Post-parse enrichment                 | v0.2.1c        |
| No document type classification      | Post-parse enrichment                 | v0.2.1a        |
| No metadata/frontmatter extraction   | Post-parse enrichment                 | v0.2.1d        |
| No diagnostic code emission          | Parser surfaces facts, not judgments  | v0.3.x         |
| 6 calibration specimens not included | Test fixtures, not parser logic       | v0.2.2b        |

---

## 9. Sub-Part Specifications

Each sub-part has its own detailed design specification:

- [v0.2.0a — File I/O & Encoding Detection](RR-SPEC-v0.2.0a-file-io-encoding.md)
- [v0.2.0b — Markdown Tokenization](RR-SPEC-v0.2.0b-markdown-tokenization.md)
- [v0.2.0c — Model Population](RR-SPEC-v0.2.0c-model-population.md)
- [v0.2.0d — Token Estimation](RR-SPEC-v0.2.0d-token-estimation.md)
