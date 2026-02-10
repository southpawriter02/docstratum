# v0.2.0d — Token Estimation

> **Version:** v0.2.0d
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.0-core-parser.md](RR-SPEC-v0.2.0-core-parser.md)
> **Grounding:** [v0.0.1a §Grammar Notes](../01-research/RR-SPEC-v0.0.1a-formal-grammar-and-parsing-rules.md) (line 130, implicit token estimation), v0.1.2b `ParsedSection.estimated_tokens` field definition
> **Depends On:** v0.2.0c (`ParsedLlmsTxt` with populated sections)
> **Module:** Inline in `src/docstratum/parser/populator.py` (end of Phase 5)
> **Tests:** Inline in `tests/test_parser_populator.py`

---

## 1. Purpose

Set the `estimated_tokens` field on every `ParsedSection` in the model. This is the final step of the parser pipeline — it takes the fully populated `ParsedLlmsTxt` and annotates each section with an approximate token count based on a simple character-division heuristic.

This sub-part is intentionally minimal. Token estimation is a single-line operation per section, but it merits its own specification because:

1. The heuristic is a design decision that downstream consumers (quality scorer, token budget validation) depend on.
2. The same heuristic must be consistent between section-level and document-level estimates.
3. The `estimated_tokens` property on `ParsedLlmsTxt` uses a different calculation path (computed property on `raw_content`) that must be validated for consistency.

---

## 2. The Heuristic

### 2.1 Formula

```python
estimated_tokens = len(section.raw_content) // 4
```

This is the **characters ÷ 4** heuristic, which is the industry-standard rough estimate for English text tokenization. It produces results within ~20% of actual BPE tokenizer output for English prose.

### 2.2 Why ÷ 4?

| Method                   | Tokens per 1000 chars | Accuracy | Latency           |
| ------------------------ | --------------------- | -------- | ----------------- |
| Characters ÷ 4           | ~250                  | ±20%     | O(1) per section  |
| Characters ÷ 3.5         | ~286                  | ±15%     | O(1) per section  |
| `tiktoken` (cl100k)      | exact                 | 100%     | ~5ms per section  |
| `transformers` tokenizer | exact                 | 100%     | ~10ms per section |

DocStratum uses ÷ 4 because:

- **No external dependency** — `tiktoken` requires a ~5 MB data file and is model-specific.
- **Consistent with `ParsedLlmsTxt.estimated_tokens`** — that property already uses `len(self.raw_content) // 4`.
- **Good enough** for token budget tier assignment — the `TokenBudgetTier` thresholds in `constants.py` have sufficient range (1,500–500,000) that a ±20% estimate doesn't cause misclassification.
- **Replaceable** — if accuracy becomes important in a future version, the heuristic can be swapped without model changes (the field is just an `int`).

### 2.3 What Gets Counted

The `raw_content` on `ParsedSection` includes:

| Content Type                              | Included in `raw_content`?        | Counted?            |
| ----------------------------------------- | --------------------------------- | ------------------- |
| Link entry lines (`- [Title](URL): desc`) | ✅                                | ✅                  |
| Prose text lines                          | ✅                                | ✅                  |
| Fenced code blocks (including delimiters) | ✅                                | ✅                  |
| H3+ sub-headers                           | ✅                                | ✅                  |
| Blank lines                               | ✅                                | ✅ (minimal impact) |
| The H2 header itself                      | ❌ (not in section `raw_content`) | ❌                  |

### 2.4 Document-Level vs. Section-Level Consistency

| Level              | Formula                         | Source Data                                                    |
| ------------------ | ------------------------------- | -------------------------------------------------------------- |
| **Section-level**  | `len(section.raw_content) // 4` | Each section's content (excludes H2 header)                    |
| **Document-level** | `len(doc.raw_content) // 4`     | Complete file text (includes H1, blockquote, H2 headers, body) |

> The sum of section-level estimates will always be **less than** the document-level estimate because the document includes the H1 title, blockquote, body content, and H2 header lines that are excluded from individual section `raw_content`.

---

## 3. Implementation

Token estimation is applied as a final step within `populate()` or as a post-processing function:

```python
def _estimate_section_tokens(doc: ParsedLlmsTxt) -> None:
    """Set estimated_tokens on each ParsedSection.

    Mutates the sections in place. Uses the characters ÷ 4 heuristic
    consistent with ParsedLlmsTxt.estimated_tokens.

    Args:
        doc: The fully populated ParsedLlmsTxt (after Phases 1–5 of v0.2.0c).
    """
    for section in doc.sections:
        section.estimated_tokens = len(section.raw_content) // 4
```

### 3.1 Integration with `populate()`

```python
def populate(tokens, *, raw_content="", source_filename="llms.txt") -> ParsedLlmsTxt:
    doc = ParsedLlmsTxt()

    # ... Phases 1-5 ...

    # v0.2.0d — Token estimation
    _estimate_section_tokens(doc)

    return doc
```

---

## 4. Edge Cases

| Scenario                                              | `raw_content`                | `estimated_tokens`    |
| ----------------------------------------------------- | ---------------------------- | --------------------- |
| Empty section (H2 immediately followed by another H2) | `""`                         | `0`                   |
| Section with only blank lines                         | `"\n\n\n"`                   | `0` (3 chars ÷ 4 = 0) |
| Section with a single short link                      | `"- [T](u)\n"` (10 chars)    | `2`                   |
| Section with 1,000 chars of prose                     | `"a" * 1000`                 | `250`                 |
| Section with code block (2,000 chars)                 | 2,000 chars including fences | `500`                 |
| Very large section (100,000 chars)                    | 100K chars                   | `25,000`              |

---

## 5. Acceptance Criteria

- [ ] Every `ParsedSection` in the output has `estimated_tokens >= 0`.
- [ ] `estimated_tokens` equals `len(section.raw_content) // 4`.
- [ ] An empty section (no content) has `estimated_tokens == 0`.
- [ ] The document-level `ParsedLlmsTxt.estimated_tokens` (computed property) is always ≥ the sum of section-level estimates.
- [ ] Token estimation does not depend on any external tokenizer library.
- [ ] No `DiagnosticCode` instances emitted.

---

## 6. Test Plan

Token estimation tests are included in `tests/test_parser_populator.py` (not a separate file, since the function is small):

| Test                                     | Input                                          | Expected                                                                |
| ---------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------- |
| `test_section_token_estimate_empty`      | Section `raw_content=""`                       | `estimated_tokens=0`                                                    |
| `test_section_token_estimate_short`      | Section `raw_content="Hello world"` (11 chars) | `estimated_tokens=2`                                                    |
| `test_section_token_estimate_1000_chars` | 1,000 chars                                    | `estimated_tokens=250`                                                  |
| `test_section_token_estimate_rounddown`  | 7 chars                                        | `estimated_tokens=1` (7 ÷ 4 = 1.75, floor to 1)                         |
| `test_document_tokens_gte_section_sum`   | Multi-section doc                              | `doc.estimated_tokens >= sum(s.estimated_tokens for s in doc.sections)` |
| `test_all_sections_have_tokens_set`      | 3-section doc                                  | All 3 sections have `estimated_tokens` set as non-negative integers     |

---

## 7. Dependencies

| Dependency                                | Status                | Impact                                                                   |
| ----------------------------------------- | --------------------- | ------------------------------------------------------------------------ |
| `ParsedSection.estimated_tokens` field    | ✅ Defined in v0.1.2b | Field with `default=0, ge=0` — ready to populate                         |
| `ParsedLlmsTxt.estimated_tokens` property | ✅ Defined in v0.1.2b | Computed property (`len(raw_content) // 4`) — no populator action needed |
| `TokenBudgetTier` thresholds              | ✅ Defined in v0.1.2a | Consumer of token estimates — not used by parser                         |
| `tiktoken` or other tokenizer             | ❌ Not used           | Future enhancement if ±20% accuracy is insufficient                      |

---

## 8. Limitations

| Limitation                                           | Impact                                                                                  | When Addressed                                     |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------- |
| ÷ 4 heuristic underestimates code-heavy content      | Code tokens are shorter (keywords, symbols), so actual token count may be 30–50% higher | If needed, v0.5.x could add a code-aware heuristic |
| Non-English text may have different char/token ratio | CJK characters may be 1 token each (÷ 1, not ÷ 4)                                       | If internationalization becomes a priority         |
| H2 header text excluded from section estimate        | Minor — section names are typically <50 chars                                           | Not planned for correction                         |
