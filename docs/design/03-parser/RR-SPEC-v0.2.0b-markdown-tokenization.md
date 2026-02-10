# v0.2.0b — Markdown Tokenization

> **Version:** v0.2.0b
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.0-core-parser.md](RR-SPEC-v0.2.0-core-parser.md)
> **Grounding:** [v0.0.1a §ABNF Grammar](../01-research/RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md) (lines 74–127), [v0.0.1a §Reference Parser](../01-research/RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md) (Phases 1–4)
> **Depends On:** v0.2.0a (decoded, LF-normalized string)
> **Modules:** `src/docstratum/parser/tokens.py`, `src/docstratum/parser/tokenizer.py`
> **Tests:** `tests/test_parser_tokenizer.py`

---

## 1. Purpose

Take the decoded, LF-normalized string from v0.2.0a and break it into an ordered sequence of structural tokens. Each token represents one logical line: a heading, a blockquote line, a link entry, a code fence boundary, a blank line, or plain text. The tokenizer does not interpret semantics — it classifies lines by their syntactic prefix.

---

## 2. Token Definitions

### 2.1 `TokenType` Enum

```python
from enum import StrEnum


class TokenType(StrEnum):
    """Structural token types recognized by the llms.txt tokenizer.

    These map directly to the ABNF grammar productions in v0.0.1a:
        H1         → h1-title
        H2         → h2-title (file-list-section header)
        H3_PLUS    → Not in grammar (treated as prose, per edge case A7)
        BLOCKQUOTE → blockquote-line
        LINK_ENTRY → file-entry
        CODE_FENCE → Not in grammar (fenced code block delimiter)
        BLANK      → blank-line
        TEXT       → content-line / paragraph
    """

    H1 = "h1"
    H2 = "h2"
    H3_PLUS = "h3_plus"
    BLOCKQUOTE = "blockquote"
    LINK_ENTRY = "link_entry"
    CODE_FENCE = "code_fence"
    BLANK = "blank"
    TEXT = "text"
```

### 2.2 `Token` Model

```python
from pydantic import BaseModel, Field


class Token(BaseModel):
    """A single tokenized line from an llms.txt file.

    Attributes:
        token_type: The structural classification of this line.
        line_number: 1-indexed line number in the original file.
        raw_text: The complete original line text (no prefix stripping).

    Example:
        >>> token = Token(token_type=TokenType.H1, line_number=1, raw_text="# My Project")
        >>> token.token_type
        <TokenType.H1: 'h1'>
    """

    token_type: TokenType = Field(description="Structural classification of this line.")
    line_number: int = Field(ge=1, description="1-indexed line number in the source file.")
    raw_text: str = Field(description="Complete original line text.")
```

---

## 3. Interface Contract

### 3.1 `tokenize(content: str) -> list[Token]`

```python
def tokenize(content: str) -> list[Token]:
    """Tokenize a decoded llms.txt string into structural tokens.

    Scans the content line by line, classifying each line based on
    its prefix pattern. Lines within fenced code blocks are always
    classified as TEXT regardless of their content.

    Args:
        content: Decoded, LF-normalized Markdown content (from v0.2.0a).

    Returns:
        An ordered list of Token instances, one per line.
        Empty content returns an empty list.

    Example:
        >>> tokens = tokenize("# Title\\n> Desc\\n## Docs\\n- [Foo](https://foo.com)\\n")
        >>> [t.token_type for t in tokens]
        [<TokenType.H1>, <TokenType.BLOCKQUOTE>, <TokenType.H2>, <TokenType.LINK_ENTRY>]
    """
```

---

## 4. Classification Rules

Each line is classified by **prefix matching** in priority order. The first matching rule wins.

| Priority | Pattern                                | TokenType    | ABNF Reference        |
| -------- | -------------------------------------- | ------------ | --------------------- |
| 1        | Inside fenced code block               | `TEXT`       | (override — see §4.1) |
| 2        | ` ``` ` at line start                  | `CODE_FENCE` | Edge case A9          |
| 3        | `# ` at line start (exactly one `#`)   | `H1`         | `h1-title`            |
| 4        | `## ` at line start (exactly two `#`s) | `H2`         | `h2-title`            |
| 5        | `### ` or more at line start           | `H3_PLUS`    | Edge case A7          |
| 6        | `> ` at line start                     | `BLOCKQUOTE` | `blockquote-line`     |
| 7        | `- [` at line start                    | `LINK_ENTRY` | `file-entry`          |
| 8        | Empty or whitespace-only               | `BLANK`      | `blank-line`          |
| 9        | Everything else                        | `TEXT`       | `content-line`        |

### 4.1 Code Fence State Machine

The tokenizer maintains a boolean `in_code_block` state:

````python
in_code_block = False

for line_number, line in enumerate(lines, start=1):
    if line.startswith("```"):
        if in_code_block:
            # Closing fence
            tokens.append(Token(token_type=TokenType.CODE_FENCE, ...))
            in_code_block = False
        else:
            # Opening fence (may have language identifier: ```python)
            tokens.append(Token(token_type=TokenType.CODE_FENCE, ...))
            in_code_block = True
        continue

    if in_code_block:
        # All content inside code block is TEXT — never classified as H1, H2, etc.
        tokens.append(Token(token_type=TokenType.TEXT, ...))
        continue

    # Normal classification continues...
````

**Why this matters:** Without code fence tracking, a `# Heading` inside a code example would be misclassified as an H1 token, producing a corrupt parse. Real-world specimens (AI SDK, Claude full) contain extensive code blocks.

### 4.2 H1 vs H2 vs H3+ Disambiguation

```python
if line.startswith("### ") or line.startswith("####"):
    # H3 or deeper — treated as prose, not sections
    token_type = TokenType.H3_PLUS
elif line.startswith("## "):
    token_type = TokenType.H2
elif line.startswith("# "):
    # Must NOT match "## " — the elif chain handles this
    token_type = TokenType.H1
```

**Critical:** The check order is `###` → `##` → `#`. Checking `#` first would match `## Section` as H1 (since `## ` starts with `# `).

### 4.3 Link Entry Recognition

A line is classified as `LINK_ENTRY` if it starts with `- [`. This is a **prefix-only check** — the tokenizer does not parse the full `[title](url)` syntax. Full link parsing happens in v0.2.0c (Model Population).

```python
if line.startswith("- ["):
    token_type = TokenType.LINK_ENTRY
```

Lines like `- https://example.com` (bare URLs, edge case B8) are classified as `TEXT`, not `LINK_ENTRY`. The Cursor specimen's bare URL format is intentionally not recognized as a link entry at the tokenization stage.

### 4.4 Blockquote Recognition

```python
if line.startswith("> ") or line == ">":
    token_type = TokenType.BLOCKQUOTE
```

Bare `>` (without trailing space) is accepted for multi-line blockquotes with empty continuation lines (edge case C2).

---

## 5. Design Decisions

| Decision                        | Choice       | Rationale                                                                                                                                     |
| ------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Line scanner vs. AST parser     | Line scanner | The `llms.txt` format is a constrained Markdown subset. Full AST parsing (mistletoe) adds dependency weight without benefit for this grammar. |
| `Token` as Pydantic model       | Yes          | Consistent with the project's convention. Small memory cost is acceptable for file sizes up to 25 MB.                                         |
| `raw_text` preserved unstripped | Yes          | The populator (v0.2.0c) needs the raw text to strip prefixes selectively. Stripping at tokenization would lose information.                   |
| `H3_PLUS` as single type        | Yes          | The parser treats `###`, `####`, `#####` identically — all are prose content within an H2 section. No need to distinguish depth.              |
| Bare `>` accepted as blockquote | Yes          | Multi-line blockquotes in the wild sometimes have empty `>` lines between paragraphs.                                                         |

---

## 6. Edge Cases

| ID  | Scenario                               | Tokenizer Behavior                                                 |
| --- | -------------------------------------- | ------------------------------------------------------------------ |
| A7  | `### Sub-heading` inside H2 section    | `H3_PLUS` token (treated as prose by populator)                    |
| A9  | ` ```python ` code fence with language | `CODE_FENCE` token; language identifier ignored at this stage      |
| A9  | `# Title` inside code block            | `TEXT` token (code fence state prevents H1 classification)         |
| B7  | `[Title](URL)` without `- ` prefix     | `TEXT` token (not `LINK_ENTRY`)                                    |
| B8  | `- https://example.com` (bare URL)     | `TEXT` token (does not start with `- [`)                           |
| C2  | `>` without trailing space             | `BLOCKQUOTE` token                                                 |
| C5  | Very long line (>10,000 chars)         | Token created normally; line length is not the tokenizer's concern |
| C7  | Tab-indented `\t# Title`               | `TEXT` token (leading tab prevents `# ` prefix match)              |
| —   | Empty content                          | `[]` (empty token list)                                            |
| —   | Single blank line                      | `[Token(BLANK, 1, "")]`                                            |

---

## 7. Acceptance Criteria

- [ ] `tokenize()` returns one `Token` per line, preserving document order.
- [ ] H1, H2, H3+, BLOCKQUOTE, LINK_ENTRY, CODE_FENCE, BLANK, and TEXT types are all correctly classified.
- [ ] Lines inside fenced code blocks are always classified as `TEXT`.
- [ ] `### ` is classified as `H3_PLUS`, not `H2` or `H1`.
- [ ] `- [` prefix triggers `LINK_ENTRY`; `- https://` does not.
- [ ] `>` and `> ` both trigger `BLOCKQUOTE`.
- [ ] Empty content returns an empty list.
- [ ] Line numbers are 1-indexed and monotonically increasing.
- [ ] `raw_text` is preserved without modification (no stripping).
- [ ] No `DiagnosticCode` instances emitted.
- [ ] Google-style docstrings on all public functions and classes.
- [ ] Module docstring references "Implements v0.2.0b".

---

## 8. Test Plan

### `tests/test_parser_tokenizer.py`

| Test                               | Input                              | Expected Tokens                                       |
| ---------------------------------- | ---------------------------------- | ----------------------------------------------------- |
| `test_h1_token`                    | `"# Title"`                        | `[H1]`                                                |
| `test_h2_token`                    | `"## Section"`                     | `[H2]`                                                |
| `test_h3_token`                    | `"### Sub"`                        | `[H3_PLUS]`                                           |
| `test_h4_token`                    | `"#### Deep"`                      | `[H3_PLUS]`                                           |
| `test_blockquote_token`            | `"> Description"`                  | `[BLOCKQUOTE]`                                        |
| `test_bare_blockquote`             | `">"`                              | `[BLOCKQUOTE]`                                        |
| `test_link_entry_token`            | `"- [Foo](https://foo.com): Desc"` | `[LINK_ENTRY]`                                        |
| `test_link_no_desc_token`          | `"- [Foo](https://foo.com)"`       | `[LINK_ENTRY]`                                        |
| `test_bare_url_is_text`            | `"- https://foo.com"`              | `[TEXT]`                                              |
| `test_inline_link_is_text`         | `"[Foo](https://foo.com)"`         | `[TEXT]`                                              |
| `test_code_fence_toggle`           | `"```python\n# not H1\n```"`       | `[CODE_FENCE, TEXT, CODE_FENCE]`                      |
| `test_blank_line`                  | `""`                               | `[BLANK]`                                             |
| `test_whitespace_line`             | `"   "`                            | `[BLANK]`                                             |
| `test_text_line`                   | `"Just some text."`                | `[TEXT]`                                              |
| `test_full_document`               | Minimal valid `llms.txt`           | `[H1, BLANK, BLOCKQUOTE, BLANK, H2, LINK_ENTRY, ...]` |
| `test_empty_content`               | `""`                               | `[]`                                                  |
| `test_priority_order_h2_before_h1` | `"## Section"`                     | `[H2]` not `[H1]`                                     |
| `test_code_block_suppresses_h1`    | `"```\n# Title\n```"`              | `[CODE_FENCE, TEXT, CODE_FENCE]`                      |
| `test_code_block_suppresses_link`  | `"```\n- [F](url)\n```"`           | `[CODE_FENCE, TEXT, CODE_FENCE]`                      |
| `test_line_numbers_correct`        | 5-line document                    | Tokens have `line_number` 1, 2, 3, 4, 5               |
| `test_tab_indented_heading`        | `"\t# Title"`                      | `[TEXT]` (tab prevents match)                         |
| `test_unclosed_code_fence`         | `"```python\n# still code"`        | `[CODE_FENCE, TEXT]` (remains in code block state)    |
