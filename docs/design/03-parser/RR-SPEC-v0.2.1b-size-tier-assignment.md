# v0.2.1b — Size Tier Assignment

> **Version:** v0.2.1b
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.2.1-classification-metadata.md](RR-SPEC-v0.2.1-classification-metadata.md)
> **Grounding:** `classification.py` (`SizeTier`), `constants.py` (`TOKEN_BUDGET_TIERS`, `TOKEN_ZONE_*` thresholds), DECISION-013
> **Depends On:** v0.2.0d (token estimation), v0.2.1a (document type)
> **Module:** `src/docstratum/parser/classifier.py` (same module as v0.2.1a)
> **Tests:** `tests/test_parser_classifier.py`

---

## 1. Purpose

Assign a `SizeTier` value and assemble the complete `DocumentClassification` model. This sub-part is separated from v0.2.1a because the tier thresholds have a calibration concern: the gap between the `// 4` parser heuristic and the `/ 3.3` research heuristic (v0.0.4a §5.3) could shift tier boundaries by up to 20%. This spec documents the calibration decision.

---

## 2. Interface Contract

### 2.1 `assign_size_tier(estimated_tokens: int) -> SizeTier`

```python
def assign_size_tier(estimated_tokens: int) -> SizeTier:
    """Assign a SizeTier based on estimated token count.

    Thresholds are derived from DECISION-013 and the SizeTier enum:
        MINIMAL:       < 1,500 tokens
        STANDARD:      1,500 – 4,499 tokens
        COMPREHENSIVE: 4,500 – 11,999 tokens
        FULL:          12,000 – 49,999 tokens
        OVERSIZED:     ≥ 50,000 tokens

    Boundary convention: inclusive lower bound, exclusive upper bound.
    (e.g., exactly 4,500 tokens → COMPREHENSIVE, not STANDARD)

    Args:
        estimated_tokens: Approximate token count from ParsedLlmsTxt.estimated_tokens.

    Returns:
        A SizeTier enum value.

    Example:
        >>> assign_size_tier(3000)
        <SizeTier.STANDARD: 'standard'>
        >>> assign_size_tier(4500)
        <SizeTier.COMPREHENSIVE: 'comprehensive'>
        >>> assign_size_tier(0)
        <SizeTier.MINIMAL: 'minimal'>
    """
```

### 2.2 `classify_document(doc, file_meta) -> DocumentClassification`

```python
def classify_document(
    doc: ParsedLlmsTxt,
    file_meta: FileMetadata,
) -> DocumentClassification:
    """Classify and tier a parsed document.

    Combines document type classification (v0.2.1a) and size tier
    assignment (v0.2.1b) into a single DocumentClassification output.

    Args:
        doc: Parsed document from v0.2.0.
        file_meta: File metadata from v0.2.0a.

    Returns:
        A fully populated DocumentClassification instance.

    Example:
        >>> classification = classify_document(doc, meta)
        >>> classification.document_type
        <DocumentType.TYPE_1_INDEX: 'type_1_index'>
        >>> classification.size_tier
        <SizeTier.COMPREHENSIVE: 'comprehensive'>
        >>> classification.size_bytes
        19456
        >>> classification.estimated_tokens
        4864
    """
    document_type = classify_document_type(doc, file_meta)
    estimated_tokens = doc.estimated_tokens
    size_tier = assign_size_tier(estimated_tokens)

    return DocumentClassification(
        document_type=document_type,
        size_bytes=file_meta.byte_count,
        estimated_tokens=estimated_tokens,
        size_tier=size_tier,
        filename=doc.source_filename,
    )
```

---

## 3. Tier Threshold Specification

### 3.1 Boundary Table

| SizeTier      | Min Tokens (inclusive) | Max Tokens (exclusive) | Source                                            |
| ------------- | ---------------------- | ---------------------- | ------------------------------------------------- |
| MINIMAL       | 0                      | 1,500                  | Below `TOKEN_BUDGET_TIERS["standard"].min_tokens` |
| STANDARD      | 1,500                  | 4,500                  | `TOKEN_BUDGET_TIERS["standard"]`                  |
| COMPREHENSIVE | 4,500                  | 12,000                 | `TOKEN_BUDGET_TIERS["comprehensive"]`             |
| FULL          | 12,000                 | 50,000                 | `TOKEN_BUDGET_TIERS["full"]`                      |
| OVERSIZED     | 50,000                 | ∞                      | Above `TOKEN_BUDGET_TIERS["full"].max_tokens`     |

### 3.2 Implementation

```python
def assign_size_tier(estimated_tokens: int) -> SizeTier:
    """Assign size tier based on token count thresholds."""
    if estimated_tokens < 1_500:
        return SizeTier.MINIMAL
    if estimated_tokens < 4_500:
        return SizeTier.STANDARD
    if estimated_tokens < 12_000:
        return SizeTier.COMPREHENSIVE
    if estimated_tokens < 50_000:
        return SizeTier.FULL
    return SizeTier.OVERSIZED
```

### 3.3 Calibration Decision

The scope doc (RR-SCOPE-v0.2.x-parser.md) identified a potential calibration issue:

| Heuristic          | Formula           | 10,000 chars → | Source                           |
| ------------------ | ----------------- | -------------- | -------------------------------- |
| Parser (current)   | `len(text) // 4`  | 2,500 tokens   | `ParsedSection.estimated_tokens` |
| Research (v0.0.4a) | `len(text) / 3.3` | 3,030 tokens   | v0.0.4a §5.3                     |

**Decision:** Use `// 4` (the parser's heuristic) for tier assignment. Rationale:

1. **Consistency** — the `estimated_tokens` value on `ParsedLlmsTxt` and `ParsedSection` already uses `// 4`. Using a different heuristic for tier assignment would create confusing mismatches.
2. **Conservative** — `// 4` produces lower estimates than `/ 3.3`, meaning files are assigned to smaller tiers. This is conservative: it is less likely to trigger an OVERSIZED warning on a file that is actually within budget.
3. **Simplicity** — Integer division is simpler and faster than float division + cast.
4. **Tier ranges are wide** — The tier boundaries (1,500 / 4,500 / 12,000 / 50,000) are spaced far enough apart that a ±20% estimation error rarely crosses a boundary. A file would need to be within 300 tokens of a boundary for the heuristic difference to matter.

If future analysis reveals that the `// 4` heuristic causes systematic misclassification, the heuristic can be updated in both `ParsedSection.estimated_tokens` and `assign_size_tier()` simultaneously.

---

## 4. DocumentClassification Assembly

The `classify_document()` function combines v0.2.1a and v0.2.1b into a single `DocumentClassification`:

| Field              | Source                                     |
| ------------------ | ------------------------------------------ |
| `document_type`    | `classify_document_type()` (v0.2.1a)       |
| `size_bytes`       | `file_meta.byte_count`                     |
| `estimated_tokens` | `doc.estimated_tokens` (computed property) |
| `size_tier`        | `assign_size_tier(estimated_tokens)`       |
| `filename`         | `doc.source_filename`                      |
| `classified_at`    | `datetime.now()` (Pydantic default)        |

---

## 5. Edge Cases

| Scenario                    | `estimated_tokens` | `SizeTier`               |
| --------------------------- | ------------------ | ------------------------ |
| Empty file (0 bytes)        | 0                  | MINIMAL                  |
| Single-line file (20 chars) | 5                  | MINIMAL                  |
| Exactly 1,500 tokens        | 1,500              | STANDARD (≥ lower bound) |
| Exactly 4,499 tokens        | 4,499              | STANDARD (< upper bound) |
| Exactly 4,500 tokens        | 4,500              | COMPREHENSIVE            |
| Exactly 49,999 tokens       | 49,999             | FULL                     |
| Exactly 50,000 tokens       | 50,000             | OVERSIZED                |
| 25 MB file (~6.25M tokens)  | 6,250,000          | OVERSIZED                |

---

## 6. Acceptance Criteria

- [ ] `assign_size_tier()` returns the correct `SizeTier` for all 5 tiers.
- [ ] Boundary values follow inclusive-lower, exclusive-upper convention.
- [ ] `classify_document()` populates all 6 fields of `DocumentClassification`.
- [ ] `estimated_tokens` is sourced from `doc.estimated_tokens`.
- [ ] `size_bytes` is sourced from `file_meta.byte_count`.
- [ ] `classified_at` is a `datetime` instance.
- [ ] Tier assignment uses `// 4` heuristic (consistent with parser).
- [ ] No diagnostics emitted.
- [ ] Google-style docstrings; module references "Implements v0.2.1b".

---

## 7. Test Plan

### `tests/test_parser_classifier.py` (v0.2.1b section)

| Test                                        | Input Tokens               | Expected Tier                                     |
| ------------------------------------------- | -------------------------- | ------------------------------------------------- |
| `test_tier_minimal_zero`                    | 0                          | MINIMAL                                           |
| `test_tier_minimal_1499`                    | 1,499                      | MINIMAL                                           |
| `test_tier_standard_1500`                   | 1,500                      | STANDARD                                          |
| `test_tier_standard_4499`                   | 4,499                      | STANDARD                                          |
| `test_tier_comprehensive_4500`              | 4,500                      | COMPREHENSIVE                                     |
| `test_tier_comprehensive_11999`             | 11,999                     | COMPREHENSIVE                                     |
| `test_tier_full_12000`                      | 12,000                     | FULL                                              |
| `test_tier_full_49999`                      | 49,999                     | FULL                                              |
| `test_tier_oversized_50000`                 | 50,000                     | OVERSIZED                                         |
| `test_tier_oversized_very_large`            | 1,000,000                  | OVERSIZED                                         |
| `test_classify_document_all_fields`         | Valid doc + meta           | All 6 DocumentClassification fields populated     |
| `test_classify_document_uses_parser_tokens` | doc with raw_content       | `estimated_tokens` matches `doc.estimated_tokens` |
| `test_classify_document_uses_file_bytes`    | meta with byte_count=5000  | `size_bytes=5000`                                 |
| `test_classify_document_sets_filename`      | source_filename="test.txt" | `filename="test.txt"`                             |
