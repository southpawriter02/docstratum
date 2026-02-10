# v0.2.0c — Model Population

> **Version:** v0.2.0c
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.0-core-parser.md](RR-SPEC-v0.2.0-core-parser.md)
> **Grounding:** [v0.0.1a §Reference Parser Phases 1-5](../01-research/RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md) (lines 222–354), [v0.0.1a §Edge Cases A1-C10](../01-research/RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md) (lines 369–412)
> **Depends On:** v0.2.0b (token stream), v0.1.2b (`ParsedLlmsTxt`, `ParsedSection`, `ParsedLink`, `ParsedBlockquote`)
> **Module:** `src/docstratum/parser/populator.py`
> **Tests:** `tests/test_parser_populator.py`

---

## 1. Purpose

Walk the token stream produced by v0.2.0b and populate a `ParsedLlmsTxt` instance field by field. This is the semantic interpretation layer — it knows that an H1 token is the document title, that BLOCKQUOTE tokens after H1 form the description, and that LINK_ENTRY tokens inside H2 sections become `ParsedLink` objects.

The populator follows a **5-phase** sequential walk of the token stream, mirroring the reference parser in v0.0.1a:

1. **H1 Title** — Extract the title text.
2. **Blockquote Description** — Collect `>` lines into `ParsedBlockquote`.
3. **Body Content** — Consume non-H2 text between blockquote and first section.
4. **Sections & Links** — Build `ParsedSection` / `ParsedLink` trees.
5. **Assembly** — Set `raw_content`, `source_filename`, `parsed_at`.

---

## 2. Interface Contract

### 2.1 `populate(tokens, raw_content, source_filename) -> ParsedLlmsTxt`

```python
def populate(
    tokens: list[Token],
    *,
    raw_content: str = "",
    source_filename: str = "llms.txt",
) -> ParsedLlmsTxt:
    """Populate a ParsedLlmsTxt model from a token stream.

    Walks the tokens through 5 phases: H1 extraction, blockquote
    extraction, body consumption, section/link building, and final
    assembly. Produces a fully populated model with safe defaults
    for any missing elements.

    Args:
        tokens: Ordered list of Token instances from tokenize().
        raw_content: Complete original file text (set as-is on ParsedLlmsTxt.raw_content).
        source_filename: Value for ParsedLlmsTxt.source_filename.

    Returns:
        A ParsedLlmsTxt instance. Always non-None.

    Example:
        >>> from docstratum.parser.tokenizer import tokenize
        >>> tokens = tokenize("# My App\\n> A tool for X\\n## API\\n- [Auth](https://api.com/auth): Authentication\\n")
        >>> doc = populate(tokens, raw_content="...", source_filename="llms.txt")
        >>> doc.title
        'My App'
        >>> doc.blockquote.text
        'A tool for X'
        >>> doc.sections[0].name
        'API'
        >>> doc.sections[0].links[0].title
        'Auth'
    """
```

---

## 3. Phase Specification

### Phase 1: H1 Title Extraction

```
Walk:   Advance past leading BLANK tokens.
Match:  First H1 token → extract title text by stripping "# " prefix.
Store:  ParsedLlmsTxt.title = stripped text
        ParsedLlmsTxt.title_line = token.line_number
Miss:   If no H1 token found before H2 or end-of-stream:
        ParsedLlmsTxt.title = None
        ParsedLlmsTxt.title_line = None
        (Validator will emit E001 — parser does not.)
Note:   Only the FIRST H1 is consumed. Subsequent H1 tokens are
        treated as TEXT in the section phase (logged at DEBUG level).
```

**Title Stripping Logic:**

```python
title = token.raw_text.removeprefix("# ").strip()
```

### Phase 2: Blockquote Extraction

```
Walk:   Skip BLANK tokens.
Match:  Consecutive BLOCKQUOTE tokens → collect text.
Store:  ParsedBlockquote(
            text = joined text with newlines,
            line_number = first blockquote token's line_number,
            raw = joined raw_text with newlines
        )
        ParsedLlmsTxt.blockquote = blockquote instance
Miss:   If next non-BLANK token is not BLOCKQUOTE:
        ParsedLlmsTxt.blockquote = None
        (Validator will emit W001 — parser does not.)
```

**Blockquote Text Stripping:**

```python
# For each BLOCKQUOTE token:
if token.raw_text == ">":
    text_line = ""  # bare > with no content
elif token.raw_text.startswith("> "):
    text_line = token.raw_text[2:]  # strip "> " prefix
else:
    text_line = token.raw_text[1:]  # strip ">" (no space after)
```

### Phase 3: Body Content Consumption

```
Walk:   Continue from current position.
Match:  All tokens that are NOT H2 → collect as body content.
Stop:   When an H2 token is encountered (do not consume it).
Store:  Body content is appended to raw_content implicitly (already
        in raw_content from the full file text). No explicit ParsedLlmsTxt
        field for body content — it exists between the blockquote and
        first section in raw_content.
Note:   Code fences within the body are consumed normally.
        H1 tokens in the body are treated as text (logged at DEBUG).
```

### Phase 4: Section & Link Building

This is the main phase — it builds the `ParsedSection` and `ParsedLink` tree.

```
Initialize: current_section = None
            in_code_block = False

Walk: Continue through remaining tokens.

For each token:
    ┌── H2 token:
    │   Create new ParsedSection(
    │       name = token.raw_text.removeprefix("## ").strip(),
    │       line_number = token.line_number,
    │       raw_content = ""  (will accumulate)
    │   )
    │   Set current_section = new section
    │   Append to ParsedLlmsTxt.sections
    │
    ├── CODE_FENCE token (while current_section is not None):
    │   Toggle in_code_block state.
    │   Append token.raw_text to current_section.raw_content.
    │
    ├── LINK_ENTRY token (while current_section is not None AND not in_code_block):
    │   Parse the link entry text → ParsedLink (see §3.1 below)
    │   Append to current_section.links
    │   Append token.raw_text to current_section.raw_content
    │
    ├── Any other token (while current_section is not None):
    │   Append token.raw_text to current_section.raw_content
    │
    └── Any token before first H2:
        Skip (body content, already handled in Phase 3).
```

#### 3.1 Link Entry Parsing

The tokenizer only checked the `- [` prefix. The populator performs full regex parsing:

```python
import re

LINK_PATTERN = re.compile(
    r'^- \[([^\]]*)\]\(([^)]*)\)(?::\s*(.*))?$'
)

def _parse_link_entry(token: Token) -> ParsedLink | None:
    """Parse a LINK_ENTRY token into a ParsedLink.

    Returns:
        ParsedLink if the regex matches, None if the line is
        malformed (starts with '- [' but doesn't complete the pattern).

    Regex groups:
        group(1) = link title (content within [])
        group(2) = URL (content within ())
        group(3) = description (content after ": "), or None
    """
    match = LINK_PATTERN.match(token.raw_text)
    if not match:
        # Malformed link entry — tokenizer flagged it as LINK_ENTRY
        # based on prefix, but full pattern doesn't match.
        # Return None; the populator treats this as TEXT content.
        return None

    title = match.group(1).strip()
    url = match.group(2).strip()
    description = match.group(3).strip() if match.group(3) else None

    return ParsedLink(
        title=title,
        url=url,
        description=description,
        line_number=token.line_number,
        is_valid_url=_is_syntactically_valid_url(url),
    )
```

#### 3.2 URL Syntactic Validation

```python
from urllib.parse import urlparse

def _is_syntactically_valid_url(url: str) -> bool:
    """Check if a URL is syntactically valid (not reachable).

    Rules:
        - Must have a scheme (http, https, ftp, etc.) OR start with / or ./
        - Empty strings → False
        - "not a url" → False
        - "https://example.com" → True
        - "/docs/page" → True (relative URL)
        - "./local/file.md" → True (relative path)

    This is a SYNTACTIC check only. URL reachability is v0.3.2b.
    """
    if not url:
        return False

    # Relative URLs are valid
    if url.startswith("/") or url.startswith("./") or url.startswith("../"):
        return True

    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)
```

### Phase 5: Final Assembly

```python
doc.raw_content = raw_content
doc.source_filename = source_filename
doc.parsed_at = datetime.now()
```

No further transformations. The model is complete.

---

## 4. Decision Tree: Token → Model Mapping

```
Token Stream
│
├── Leading BLANK tokens → skipped
│
├── First H1 → ParsedLlmsTxt.title, .title_line
│   │
│   ├── BLANK → skipped
│   │
│   ├── BLOCKQUOTE sequence → ParsedLlmsTxt.blockquote
│   │
│   ├── Non-H2 tokens → body content (consumed, not stored separately)
│   │
│   └── H2 → starts ParsedSection
│       │
│       ├── LINK_ENTRY → ParsedSection.links[] (via regex parsing)
│       │
│       ├── CODE_FENCE → toggle code block state; content added to raw_content
│       │
│       ├── H3_PLUS, TEXT, BLANK, BLOCKQUOTE → section.raw_content
│       │
│       └── Another H2 → close current section, start new one
│
├── No H1 found → title=None, title_line=None
│
├── No BLOCKQUOTE → blockquote=None
│
└── No H2 → sections=[]
```

---

## 5. Edge Cases

| ID  | Scenario                              | Populator Behavior                                                                |
| --- | ------------------------------------- | --------------------------------------------------------------------------------- |
| A1  | Empty token stream                    | `ParsedLlmsTxt(title=None, sections=[], raw_content="")`                          |
| A2  | Only BLANK tokens                     | Same as A1                                                                        |
| A3  | No H1 token                           | `title=None`, `title_line=None`, sections still parsed                            |
| A4  | Multiple H1 tokens                    | First H1 consumed as title; subsequent H1 tokens treated as TEXT within sections  |
| A5  | H2 before H1                          | H2 tokens before H1 are consumed in Phase 3 (body); sections start after H1       |
| A6  | H2 tokens but no LINK_ENTRY tokens    | Sections created with empty `links=[]`, content in `raw_content`                  |
| A8  | H2 followed immediately by another H2 | First section has empty `links=[]` and empty `raw_content=""`                     |
| B1  | `- [Title](url` (malformed)           | `_parse_link_entry()` returns `None`; line added to `section.raw_content` as text |
| B2  | `- [Title]()` (empty URL)             | Link created with `url=""`, `is_valid_url=False`                                  |
| B6  | `- [](URL)` (empty title)             | Link created with `title=""`                                                      |
| C1  | Multi-line blockquote                 | All consecutive BLOCKQUOTE tokens joined with `\n`                                |
| C4  | Unicode in titles/descriptions        | Passed through unchanged; no ASCII restriction                                    |

---

## 6. Acceptance Criteria

- [ ] Empty token stream → `ParsedLlmsTxt(title=None, sections=[], raw_content="")`.
- [ ] H1 token extracts `title` and `title_line` correctly.
- [ ] BLOCKQUOTE tokens after H1 populate `blockquote.text`, `blockquote.line_number`, and `blockquote.raw`.
- [ ] Multi-line blockquotes join with `\n` in `text`, preserve `> ` in `raw`.
- [ ] Missing blockquote → `blockquote=None`.
- [ ] H2 tokens create `ParsedSection` instances with correct `name` and `line_number`.
- [ ] LINK_ENTRY tokens inside sections create `ParsedLink` with `title`, `url`, `description`, `line_number`, `is_valid_url`.
- [ ] Malformed link entries (regex fails) are treated as text, not added to `links`.
- [ ] `is_valid_url` returns `True` for `https://`, `http://`, and relative URLs.
- [ ] `is_valid_url` returns `False` for empty strings and non-URL text.
- [ ] `raw_content` on each `ParsedSection` accumulates all non-H2 content lines.
- [ ] `raw_content` on `ParsedLlmsTxt` is set to the full original file text.
- [ ] `source_filename` is set to the provided value.
- [ ] `parsed_at` is set to a datetime.
- [ ] Code fence state toggles correctly — links inside code blocks are treated as text.
- [ ] No `DiagnosticCode` instances emitted.
- [ ] Google-style docstrings on all public functions.
- [ ] Module docstring references "Implements v0.2.0c".

---

## 7. Test Plan

### `tests/test_parser_populator.py`

| Test                               | Input Tokens                              | Expected Output                                                   |
| ---------------------------------- | ----------------------------------------- | ----------------------------------------------------------------- |
| `test_empty_tokens`                | `[]`                                      | `title=None`, `sections=[]`                                       |
| `test_h1_only`                     | `[H1("# Title")]`                         | `title="Title"`, `title_line=1`, `sections=[]`, `blockquote=None` |
| `test_h1_and_blockquote`           | `[H1, BLANK, BLOCKQUOTE]`                 | `title="..."`, `blockquote.text="..."`                            |
| `test_multiline_blockquote`        | `[H1, BQ, BQ, BQ]`                        | `blockquote.text` contains 3 lines joined by `\n`                 |
| `test_blockquote_raw_preserved`    | `[H1, BQ("> Hello")]`                     | `blockquote.raw=""> Hello""`, `blockquote.text="Hello"`           |
| `test_bare_blockquote`             | `[H1, BQ(">")]`                           | `blockquote.text=""`                                              |
| `test_no_blockquote`               | `[H1, BLANK, H2]`                         | `blockquote=None`                                                 |
| `test_single_section`              | `[H1, H2("## Docs")]`                     | `sections[0].name="Docs"`, `sections[0].line_number=2`            |
| `test_multiple_sections`           | `[H1, H2, LINK, H2, LINK]`                | 2 sections, each with 1 link                                      |
| `test_link_with_description`       | `[H2, LINK("- [T](u): desc")]`            | `links[0].title="T"`, `.url="u"`, `.description="desc"`           |
| `test_link_without_description`    | `[H2, LINK("- [T](u)")]`                  | `.description=None`                                               |
| `test_link_empty_url`              | `[H2, LINK("- [T]()")]`                   | `.url=""`, `.is_valid_url=False`                                  |
| `test_link_empty_title`            | `[H2, LINK("- [](u)")]`                   | `.title=""`                                                       |
| `test_malformed_link_becomes_text` | `[H2, LINK("- [T](url")]`                 | `links=[]`, text in `raw_content`                                 |
| `test_url_validation_absolute`     | URL `"https://x.com"`                     | `is_valid_url=True`                                               |
| `test_url_validation_relative`     | URL `"/docs/page"`                        | `is_valid_url=True`                                               |
| `test_url_validation_dotrelative`  | URL `"./page.md"`                         | `is_valid_url=True`                                               |
| `test_url_validation_invalid`      | URL `"not a url"`                         | `is_valid_url=False`                                              |
| `test_url_validation_empty`        | URL `""`                                  | `is_valid_url=False`                                              |
| `test_body_content_consumed`       | `[H1, TEXT, TEXT, H2]`                    | Body text not stored separately; 1 section created                |
| `test_h3_in_section`               | `[H2, H3_PLUS, LINK]`                     | `H3_PLUS` in `raw_content`, link in `links`                       |
| `test_code_fence_suppresses_links` | `[H2, CODE_FENCE, LINK, CODE_FENCE]`      | `links=[]` (link is inside code block)                            |
| `test_empty_section`               | `[H2, H2]`                                | First section has `links=[]`, `raw_content=""`                    |
| `test_source_filename_set`         | Any tokens + `source_filename="test.txt"` | `doc.source_filename="test.txt"`                                  |
| `test_raw_content_passthrough`     | Any tokens + `raw_content="..."`          | `doc.raw_content="..."`                                           |
| `test_parsed_at_set`               | Any tokens                                | `doc.parsed_at` is a `datetime` instance                          |
