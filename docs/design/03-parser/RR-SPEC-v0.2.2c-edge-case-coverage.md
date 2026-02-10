# v0.2.2c — Edge Case Coverage

> **Version:** v0.2.2c
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.2-parser-testing-calibration.md](RR-SPEC-v0.2.2-parser-testing-calibration.md)
> **Grounding:** v0.0.1a §Edge Cases (A1–A10, B1–B8, C1–C10, D1–D5)
> **Depends On:** v0.2.0 (core parser), v0.2.1 (enrichment)
> **Tests:** `tests/test_parser_edge_cases.py`

---

## 1. Purpose

Implement test cases for all 33 edge cases documented in v0.0.1a §Edge Cases. Each test verifies that the parser produces the expected structural model for an adversarial or unusual input — not that diagnostic codes are emitted. The test file is organized by category (A: Structural, B: Link Format, C: Content, D: Encoding).

---

## 2. Category A — Structural Edge Cases (10)

### A1 — Empty File

**Input:** `""` (0 bytes)

**Expected:**

- `title`: `None`
- `sections`: `[]`
- `blockquote`: `None`
- Classification: `UNKNOWN`

---

### A2 — Blank-Only File

**Input:** `"\n\n   \n\n"` (whitespace and newlines only)

**Expected:**

- `title`: `None`
- `sections`: `[]`
- No crash

---

### A3 — No H1

**Input:**

```markdown
## Section One

- [Link](https://example.com)
```

**Expected:**

- `title`: `None`
- `sections`: 1 section named `"Section One"`
- Section contains 1 link

---

### A4 — Multiple H1

**Input:**

```markdown
# First Title

## Section

- [Link](https://example.com)

# Second Title
```

**Expected:**

- `title`: `"First Title"` (first H1 captured)
- `sections`: 1 section
- `raw_content` contains both H1 lines
- Classification: `TYPE_2_FULL` (multiple H1s)

---

### A5 — H2 Before H1

**Input:**

```markdown
## Orphan Section

- [Link](https://example.com)

# Late Title

## Normal Section

- [Link2](https://example.com/2)
```

**Expected:**

- `title`: `"Late Title"` (first H1 found)
- Orphan section: parser behavior depends on implementation — may be captured as section before title or discarded. Spec requires documenting which behavior is chosen.

---

### A6 — No H2 Sections

**Input:**

```markdown
# Title Only

> Just a description, no sections.
```

**Expected:**

- `title`: `"Title Only"`
- `blockquote.text`: `"Just a description, no sections."`
- `sections`: `[]`

---

### A7 — H3+ Headers

**Input:**

```markdown
# Title

## Section

### Subsection

#### Deep

- [Link](https://example.com)
```

**Expected:**

- `title`: `"Title"`
- `sections`: 1 section named `"Section"`
- H3 and H4 lines appear in section `raw_content` as TEXT tokens (not parsed as section headers)

---

### A8 — Empty H2 Section

**Input:**

```markdown
# Title

## Empty Section

## Non-Empty Section

- [Link](https://example.com)
```

**Expected:**

- `sections`: 2 sections
- `sections[0].name`: `"Empty Section"`, `sections[0].links`: `[]`
- `sections[1].name`: `"Non-Empty Section"`, `sections[1].links`: 1 link

---

### A9 — Fenced Code Blocks

**Input:**

````markdown
# Title

## Code Section

```markdown
# This is NOT a title

## This is NOT a section

- [Not a link](https://not-parsed.com)
```

- [Real Link](https://real.com)
````

**Expected:**

- `title`: `"Title"`
- `sections`: 1 section named `"Code Section"`
- `sections[0].links`: 1 link (`"Real Link"`) — code block content NOT parsed as links
- Code block content appears in `raw_content`

---

### A10 — Type 2 Full Document

**Input:** A document > 256,000 bytes (generated programmatically in test setup).

**Expected:**

- Classification: `TYPE_2_FULL`
- Parser completes without memory errors
- Title extracted if present

---

## 3. Category B — Link Format Edge Cases (8)

### B1 — Missing Closing Parenthesis

**Input:**

```markdown
# Title

## Links

- [Broken](https://example.com
- [Good](https://example.com)
```

**Expected:**

- `sections[0].links`: 1 link (`"Good"`) — malformed link not extracted
- Malformed line appears as TEXT in `raw_content`

---

### B2 — Empty URL

**Input:**

```markdown
# Title

## Links

- [Empty]()
```

**Expected:**

- `sections[0].links`: 1 link with `url=""` (URL is empty but syntactically valid)

---

### B3 — Relative URL

**Input:**

```markdown
# Title

## Links

- [Relative](/docs/api)
- [Dotted](./local.md)
- [Parent](../parent.md)
```

**Expected:**

- 3 links extracted, all with relative URLs preserved as-is
- `is_relative_url`: `True` (if LinkRelationship tracks this) or URLs stored verbatim

---

### B4 — Malformed URL

**Input:**

```markdown
# Title

## Links

- [Bad](not a url at all)
- [Good](https://example.com)
```

**Expected:**

- Both extracted as links (parser does not validate URL format; that's the validator's job)
- `sections[0].links`: 2 links

---

### B5 — Duplicate URLs

**Input:**

```markdown
# Title

## Links

- [Link A](https://example.com)
- [Link B](https://example.com)
```

**Expected:**

- 2 links extracted (both with same URL but different titles)
- Parser does not deduplicate

---

### B6 — Empty Title

**Input:**

```markdown
# Title

## Links

- [](https://example.com)
```

**Expected:**

- 1 link with `title=""` (empty string, not `None`)

---

### B7 — Non-List Links

**Input:**

```markdown
# Title

## Links

[Bare Link](https://example.com)

Not a list item: [Inline](https://inline.com)
```

**Expected:**

- Parser behavior depends on implementation:
  - **Strict:** Only `- [text](url)` pattern parsed → 0 links
  - **Permissive:** Any `[text](url)` pattern parsed → 2 links
- Spec requires documenting which behavior is chosen. Scope doc implies list-item format is the expected pattern.

---

### B8 — Bare URLs

**Input:**

```markdown
# Title

## Links

- https://bare-url.com
- <https://angle-bracket.com>
```

**Expected:**

- 0 links extracted (no `[text](url)` pattern)
- Lines appear as TEXT in `raw_content`

---

## 4. Category C — Content Edge Cases (10)

### C1 — Multiline Blockquote

**Input:**

```markdown
# Title

> Line 1 of the blockquote.
> Line 2 of the blockquote.
> Line 3 with **bold** and _italic_.
```

**Expected:**

- `blockquote.text`: All 3 lines joined, `>` prefix stripped
- Markdown formatting in blockquote preserved as raw text

---

### C2 — Unicode Content

**Input:**

```markdown
# 日本語プロジェクト

> これは日本語の説明です。

## ドキュメント

- [API リファレンス](https://example.com/api): API の完全なドキュメント
```

**Expected:**

- `title`: `"日本語プロジェクト"`
- All Unicode content preserved throughout
- Link title and description contain Japanese text

---

### C3 — Long Lines

**Input:** A document with a line exceeding 10,000 characters.

**Expected:**

- Parser handles without truncation or crash
- Content preserved in `raw_content`

---

### C4 — Mixed Indentation

**Input:**

```markdown
# Title

## Section

- [Link 1](https://a.com)
  - [Link 2](https://b.com)
    - [Link 3](https://c.com)
  - [Tab Link](https://d.com)
```

**Expected:**

- All 4 links extracted (parser strips leading whitespace/indentation for link detection)
- Or: only top-level list items extracted (depends on link regex). Spec requires documenting behavior.

---

### C5 — Trailing Whitespace

**Input:** Lines with trailing spaces and tabs.

**Expected:**

- No effect on parsing
- Titles, section names, and URLs trimmed appropriately

---

### C6 — Nested Lists

**Input:**

```markdown
# Title

## Section

- [Top Level](https://a.com)
  - Sub-item text
  - [Nested Link](https://b.com)
    - Deep sub-item
```

**Expected:**

- At minimum, top-level link extracted
- Nested link extraction depends on implementation (see C4)

---

### C7 — Entries Without Descriptions

**Input:**

```markdown
# Title

## Section

- [No Description](https://example.com)
- [Has Description](https://example.com/2): This has a description
```

**Expected:**

- 2 links
- `links[0].description`: `None`
- `links[1].description`: `"This has a description"`

---

### C8 — Consecutive Blank Lines

**Input:**

```markdown
# Title

> Description

## Section

- [Link](https://example.com)
```

**Expected:**

- Blank lines do not affect structural extraction
- Title, blockquote, section, and link all parsed correctly

---

### C9 — HTML Comments

**Input:**

```markdown
# Title

<!-- This is a comment -->

## Section

- [Link](https://example.com)
```

**Expected:**

- HTML comment appears as TEXT in `raw_content`
- Does not affect structural parsing

---

### C10 — Mixed Content in Sections

**Input:**

```markdown
# Title

## Section

Some prose paragraph before the links.

More prose with **bold** text.

- [Link 1](https://a.com): Description
- [Link 2](https://b.com): Description

Trailing prose after the links.
```

**Expected:**

- 2 links extracted from section
- Prose content appears in section's `raw_content`
- Links extracted regardless of surrounding prose

---

## 5. Category D — Encoding Edge Cases (5)

### D1 — UTF-8 BOM

**Input:** File beginning with `\xEF\xBB\xBF` (UTF-8 BOM).

**Expected:**

- BOM stripped by `read_file()` (v0.2.0a)
- Parsing proceeds normally
- Title extracted correctly (BOM does not corrupt first line)

---

### D2 — Non-UTF-8 Encoding

**Input:** File encoded as Latin-1 (ISO-8859-1).

**Expected:**

- `read_file()` falls back to Latin-1 (v0.2.0a)
- Content decoded and parsed
- No crash

---

### D3 — Null Bytes

**Input:** File containing `\x00` bytes.

**Expected:**

- `FileMetadata.has_null_bytes`: `True`
- Classification: `UNKNOWN`
- Parser may extract partial structure or return empty model

---

### D4 — Windows CRLF

**Input:** File using `\r\n` line endings.

**Expected:**

- Line splitting handles CRLF
- All structure extracted identically to LF-only version

---

### D5 — Mac CR-Only

**Input:** File using `\r` line endings (legacy Mac format).

**Expected:**

- Line splitting handles CR
- All structure extracted identically to LF-only version

---

## 6. Acceptance Criteria

- [ ] 33 test cases implemented in `tests/test_parser_edge_cases.py`.
- [ ] Category A (10 tests): All structural edge cases covered.
- [ ] Category B (8 tests): All link format edge cases covered.
- [ ] Category C (10 tests): All content edge cases covered.
- [ ] Category D (5 tests): All encoding edge cases covered.
- [ ] Each test documents its edge case ID (A1, B3, etc.) in the docstring.
- [ ] Tests verify parser model output, NOT diagnostic codes or quality scores.
- [ ] Ambiguous behaviors (A5, B7, C4, C6) have their chosen behavior documented.
- [ ] No external network access.

---

## 7. Test Plan

### `tests/test_parser_edge_cases.py`

```python
"""Edge case tests for the DocStratum parser.

Tests all 33 edge cases from v0.0.1a §Edge Cases,
organized by category.

Implements v0.2.2c.
"""


class TestCategoryA_Structural:
    """A1–A10: Structural edge cases."""

    def test_A1_empty_file(self): ...
    def test_A2_blank_only_file(self): ...
    def test_A3_no_h1(self): ...
    def test_A4_multiple_h1(self): ...
    def test_A5_h2_before_h1(self): ...
    def test_A6_no_h2_sections(self): ...
    def test_A7_h3_plus_headers(self): ...
    def test_A8_empty_h2_section(self): ...
    def test_A9_fenced_code_blocks(self): ...
    def test_A10_type2_full_document(self): ...


class TestCategoryB_LinkFormat:
    """B1–B8: Link format edge cases."""

    def test_B1_missing_closing_paren(self): ...
    def test_B2_empty_url(self): ...
    def test_B3_relative_url(self): ...
    def test_B4_malformed_url(self): ...
    def test_B5_duplicate_urls(self): ...
    def test_B6_empty_title(self): ...
    def test_B7_non_list_links(self): ...
    def test_B8_bare_urls(self): ...


class TestCategoryC_Content:
    """C1–C10: Content edge cases."""

    def test_C1_multiline_blockquote(self): ...
    def test_C2_unicode_content(self): ...
    def test_C3_long_lines(self): ...
    def test_C4_mixed_indentation(self): ...
    def test_C5_trailing_whitespace(self): ...
    def test_C6_nested_lists(self): ...
    def test_C7_entries_without_descriptions(self): ...
    def test_C8_consecutive_blank_lines(self): ...
    def test_C9_html_comments(self): ...
    def test_C10_mixed_content_in_sections(self): ...


class TestCategoryD_Encoding:
    """D1–D5: Encoding edge cases."""

    def test_D1_utf8_bom(self): ...
    def test_D2_non_utf8_encoding(self): ...
    def test_D3_null_bytes(self): ...
    def test_D4_windows_crlf(self): ...
    def test_D5_mac_cr_only(self): ...
```

---

## 8. Design Decisions

| Decision                               | Choice | Rationale                                                                                                              |
| -------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------- |
| Inline test data, not fixture files    | Yes    | Edge case inputs are small (1–10 lines). Inline `parse_string()` calls are more readable than separate files.          |
| Class-per-category organization        | Yes    | Groups related tests for discovery and reporting.                                                                      |
| Edge case ID in docstring              | Yes    | Traceability back to v0.0.1a spec.                                                                                     |
| Ambiguous behaviors documented in test | Yes    | Where the spec allows multiple valid interpretations (A5, B7, C4), the test documents which interpretation was chosen. |
| A10 uses generated data                | Yes    | A 256 KB fixture file committed to git is wasteful. Generate it programmatically in `setUp()`.                         |
