# v0.3.2d — Blockquote Quality

> **Version:** v0.3.2d
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.2-l2-content-quality.md](RR-SPEC-v0.3.2-l2-content-quality.md)
> **Grounding:** DS-VC-CON-006 (Substantive Blockquote, 3 pts SOFT), v0.0.2c audit (blockquotes <20 chars correlate with lowest-quality files)
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.blockquote`, `ParsedLlmsTxt.title`), v0.3.1a (L1 blockquote presence — W001)
> **Module:** `src/docstratum/validation/checks/l2_blockquote_quality.py`
> **Tests:** `tests/test_validation_l2_blockquote_quality.py`

---

## 1. Purpose

Verify that the blockquote (the one-line project description after the H1 title) is **substantive** — not trivially short, not a mere repetition of the title, and not placeholder text. While v0.3.1a (W001) checks that a blockquote _exists_, v0.3.2d checks that it _means something_.

### 1.1 Relationship to v0.3.1a (W001)

```
v0.3.1a (L1): Does a blockquote exist?               → W001 if missing
v0.3.2d (L2): If it exists, is it substantive?        → W012 if trivial
```

These are level-separated concerns:

- L1 (structural): The slot is filled.
- L2 (content): The content in the slot is useful.

If the blockquote is missing (W001 fired at L1), v0.3.2d skips — there's nothing to evaluate. v0.3.2d only runs when `parsed.blockquote is not None`.

### 1.2 Diagnostic Code Gap

> [!IMPORTANT]
> DS-VC-CON-006 has "no standalone diagnostic code." The CON-006 spec states: _"None — this is an informational criterion."_ However, detecting a trivial blockquote without telling the user is opaque.
>
> **Decision:** Introduce **W012 (TRIVIAL_BLOCKQUOTE)** as a new WARNING code. This makes blockquote quality failures explicit and provides actionable remediation.

---

## 2. Diagnostic Code

| Code | Severity | Criterion     | Message                                                            | Remediation                                                                                             |
| ---- | -------- | ------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| W012 | WARNING  | DS-VC-CON-006 | Blockquote is trivially short or merely repeats the project title. | Write a substantive 1-line project description (≥20 characters) that adds information beyond the title. |

### 2.1 Schema Addition

This code must be added to `diagnostics.py`:

```python
# ── [v0.3.2d] Blockquote quality diagnostic ──────────────────
W012_TRIVIAL_BLOCKQUOTE = (
    "W012",
    """Blockquote is trivially short or merely repeats the project title.
    Maps to: DS-VC-CON-006 (Substantive Blockquote). Severity: WARNING.
    Note: v0.0.2c audit: blockquotes <20 chars correlate with lowest-quality files.
    Remediation: Write a substantive 1-line project description (≥20 chars).""",
)
```

---

## 3. Check Logic

```python
"""L2 blockquote quality check.

Verifies that the blockquote is substantive — not trivially short
and not merely repeating the H1 title.

Implements v0.3.2d. Criterion: DS-VC-CON-006.
"""

from difflib import SequenceMatcher


# ── Thresholds ──────────────────────────────────────────────
MIN_BLOCKQUOTE_LENGTH = 20
"""Minimum character count for a substantive blockquote.

Derived from v0.0.2c audit: blockquotes <20 chars correlate with
lowest-quality files (bottom quartile). Examples of good passes:
- "Cybernetically enhanced web apps" (32 chars, Svelte)
- "Data validation using Python type annotations" (46 chars, Pydantic)
"""

MAX_TITLE_SIMILARITY = 0.80
"""Maximum allowed similarity between blockquote and H1 title.

A blockquote that merely repeats the title (e.g., H1 = "MyProject",
blockquote = "> MyProject is MyProject") provides no additional
information. Uses SequenceMatcher ratio (0 = different, 1 = identical).
"""


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check blockquote substance.

    Two independent quality checks:
    1. Length ≥ 20 characters (after stripping)
    2. Similarity with H1 title < 80%

    If both conditions fail, only one W012 is emitted (with context
    covering both issues). If only one fails, W012 has context for
    that specific issue.

    Args:
        parsed: The parsed file model.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        List containing 0 or 1 W012 diagnostic.
    """
    # If no blockquote exists, vacuously pass (W001 handles existence)
    if parsed.blockquote is None:
        return []

    text = parsed.blockquote.strip()

    # Edge case: blockquote exists but is empty/whitespace
    # (This should not happen if L1 passed, but handle defensively)
    if not text:
        return [
            _make_diagnostic(
                line_number=_blockquote_line(parsed),
                context="Blockquote is empty (zero characters after stripping).",
            )
        ]

    issues: list[str] = []

    # Check 1: Minimum length
    if len(text) < MIN_BLOCKQUOTE_LENGTH:
        issues.append(
            f"Blockquote is {len(text)} characters "
            f"(minimum: {MIN_BLOCKQUOTE_LENGTH})."
        )

    # Check 2: Title similarity
    title = parsed.title.strip() if parsed.title else ""
    if title:
        similarity = SequenceMatcher(
            None, text.lower(), title.lower()
        ).ratio()
        if similarity >= MAX_TITLE_SIMILARITY:
            issues.append(
                f"Blockquote is {similarity:.0%} similar to the H1 title "
                f"'{title}' (maximum: {MAX_TITLE_SIMILARITY:.0%})."
            )

    if issues:
        return [
            _make_diagnostic(
                line_number=_blockquote_line(parsed),
                context=" ".join(issues),
            )
        ]

    return []


def _make_diagnostic(
    *, line_number: int, context: str
) -> "ValidationDiagnostic":
    """Construct a W012 diagnostic."""
    return ValidationDiagnostic(
        code=DiagnosticCode.W012_TRIVIAL_BLOCKQUOTE,
        severity=Severity.WARNING,
        message=DiagnosticCode.W012_TRIVIAL_BLOCKQUOTE.message,
        remediation=DiagnosticCode.W012_TRIVIAL_BLOCKQUOTE.remediation,
        level=ValidationLevel.L2_CONTENT,
        check_id="CNT-006",
        line_number=line_number,
        context=context,
    )


def _blockquote_line(parsed: "ParsedLlmsTxt") -> int:
    """Return the line number of the blockquote.

    Uses title_line + 1 (blockquote follows H1). Falls back to
    line 2 if title_line is not available.
    """
    if hasattr(parsed, "title_line") and parsed.title_line:
        return parsed.title_line + 1
    return 2
```

### 3.1 Decision: Two Checks, One Diagnostic

If both checks fail (too short AND too similar), only **one W012** is emitted with a combined context:

```
"Blockquote is 12 characters (minimum: 20). Blockquote is 95% similar
to the H1 title 'MyProject' (maximum: 80%)."
```

This avoids diagnostic noise. The user gets one actionable warning covering all the issues.

### 3.2 Decision: Threshold Sources

| Threshold                     | Value                                                                                               | Source |
| ----------------------------- | --------------------------------------------------------------------------------------------------- | ------ |
| `MIN_BLOCKQUOTE_LENGTH` = 20  | CON-006 spec: "blockquotes under 20 characters correlate with lowest-quality files" (v0.0.2c audit) |
| `MAX_TITLE_SIMILARITY` = 0.80 | CON-006 spec: "similarity < 0.8"                                                                    |

Both are provisional. The CON-006 spec explicitly notes they should be "refined against the 11 empirical specimens."

### 3.3 Decision: No Placeholder Detection

Placeholder detection (e.g., "TBD" in the blockquote) is handled by v0.3.2a's placeholder pattern constants, which could theoretically be applied to blockquote text. However, v0.3.2d focuses on _length and originality_, not _content patterns_. If placeholder detection for blockquotes is needed, it should be a future extension using the shared `PLACEHOLDER_PATTERNS` constant.

---

## 4. Acceptance Criteria

- [ ] `check()` returns `[]` when `parsed.blockquote is None` (vacuous pass).
- [ ] `check()` returns W012 when blockquote is <20 characters.
- [ ] `check()` returns W012 when blockquote is ≥80% similar to title.
- [ ] `check()` returns W012 with combined context when both checks fail.
- [ ] `check()` returns `[]` when blockquote is ≥20 chars and <80% similar to title.
- [ ] W012 uses `severity=WARNING`, `level=L2_CONTENT`, `check_id="CNT-006"`.
- [ ] `diagnostics.py` updated with W012_TRIVIAL_BLOCKQUOTE code.
- [ ] Empty blockquote (whitespace only) emits W012.

---

## 5. Test Plan

### `tests/test_validation_l2_blockquote_quality.py`

| Test                                 | Input                                                                    | Expected                       |
| ------------------------------------ | ------------------------------------------------------------------------ | ------------------------------ |
| `test_no_blockquote_passes`          | `blockquote=None`                                                        | `[]`                           |
| `test_substantive_blockquote_passes` | "Cybernetically enhanced web apps" (32 chars)                            | `[]`                           |
| `test_short_blockquote_warns`        | "A library" (9 chars)                                                    | `[W012]`                       |
| `test_title_repetition_warns`        | Title = "MyProject", blockquote = "MyProject description" (>80% similar) | `[W012]`                       |
| `test_both_short_and_repetitive`     | Title = "Foo", blockquote = "Foo"                                        | `[W012]` with combined context |
| `test_empty_blockquote_warns`        | `blockquote="   "`                                                       | `[W012]`                       |
| `test_exactly_20_chars_passes`       | "01234567890123456789" (20 chars)                                        | `[]`                           |
| `test_exactly_19_chars_warns`        | "0123456789012345678" (19 chars)                                         | `[W012]`                       |
| `test_dissimilar_short_only_length`  | Title = "ProjectX", blockquote = "A tool" (6 chars, dissimilar)          | `[W012]` context = length only |

---

## 6. Design Decisions

| Decision                               | Choice | Rationale                                                                         |
| -------------------------------------- | ------ | --------------------------------------------------------------------------------- |
| W012 as new code (not enhanced W001)   | Yes    | W001 = existence (L1). W012 = quality (L2). Different levels, different concerns. |
| Single W012 per file                   | Yes    | One blockquote → at most one quality diagnostic.                                  |
| Combined context for multiple failures | Yes    | Reduces diagnostic noise. One actionable warning.                                 |
| SequenceMatcher for similarity         | Yes    | Stdlib, no dependency. CON-006 suggests "approximate string matching."            |
| No placeholder detection in v0.3.2d    | Yes    | Placeholder patterns handled by v0.3.2a constants. Avoids duplication.            |
| Vacuous pass if no blockquote          | Yes    | W001 already fired at L1. Don't double-report.                                    |
