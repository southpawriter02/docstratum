# v0.3.0e — Size Limit Enforcement

> **Version:** v0.3.0e
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.0-l0-parseable-gate.md](RR-SPEC-v0.3.0-l0-parseable-gate.md)
> **Grounding:** v0.0.4a §SIZ-003, v0.0.4c §CHECK-003 (Monolith Monster), constants.py `TOKEN_ZONES`, DiagnosticCode.E008_EXCEEDS_SIZE_LIMIT
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.estimated_tokens`), v0.1.2a (`TOKEN_ZONES`)
> **Module:** `src/docstratum/validation/checks/l0_size_limit.py`
> **Tests:** `tests/test_validation_l0_size_limit.py`

---

## 1. Purpose

Reject files exceeding the hard token limit of 100,000 tokens — the "Monolith Monster" anti-pattern threshold (AP-STRAT-002). Files this large cannot be consumed as a single unit by any current LLM context window and represent a fundamental failure of the documentation approach.

---

## 2. Diagnostic Code

| Code | Severity | Message                                | Remediation                                                                                                            |
| ---- | -------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| E008 | ERROR    | File exceeds 100,000 token hard limit. | Split the file into smaller documents (e.g., one per API section). Consider using the `llms-full.txt` + index pattern. |

---

## 3. Check Logic

```python
"""L0 size limit enforcement check.

Rejects files exceeding 100,000 tokens (the DEGRADATION zone from TOKEN_ZONES).
Maps to the Monolith Monster anti-pattern (AP-STRAT-002 / CHECK-003).

Implements v0.3.0e.
"""

from docstratum.schema.constants import TOKEN_ZONES


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check whether the file exceeds the hard token limit.

    The threshold is TOKEN_ZONES["DEGRADATION"] (100,000 tokens).
    Uses the ÷4 heuristic estimate from ParsedLlmsTxt.estimated_tokens.

    Args:
        parsed: The parsed file model with estimated_tokens.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        Empty list if within limit, or [E008] if exceeded.
    """
    diagnostics: list[ValidationDiagnostic] = []

    hard_limit = TOKEN_ZONES["DEGRADATION"]  # 100,000

    if parsed.estimated_tokens > hard_limit:
        diagnostics.append(
            ValidationDiagnostic(
                code=DiagnosticCode.E008_EXCEEDS_SIZE_LIMIT,
                severity=Severity.ERROR,
                message=DiagnosticCode.E008_EXCEEDS_SIZE_LIMIT.message,
                remediation=DiagnosticCode.E008_EXCEEDS_SIZE_LIMIT.remediation,
                level=ValidationLevel.L0_PARSEABLE,
                check_id="CHECK-003",
                context=(
                    f"Estimated tokens: {parsed.estimated_tokens:,}. "
                    f"Hard limit: {hard_limit:,}. "
                    f"Consider splitting into multiple files."
                ),
            )
        )

    return diagnostics
```

### 3.1 Distinction from W010 (Token Budget Exceeded)

| Code | Level | Threshold                                      | Purpose                                                 |
| ---- | ----- | ---------------------------------------------- | ------------------------------------------------------- |
| E008 | L0    | 100,000 tokens (DEGRADATION zone)              | Hard gate — file is too large for any LLM               |
| W010 | L3    | Tier-specific budget (4,500 / 12,000 / 50,000) | Advisory — file exceeds recommended budget for its tier |

E008 is a structural gate. W010 is a best-practices advisory. A file with 60,000 tokens would trigger W010 (exceeds FULL tier budget of 50,000) but NOT E008 (below 100K hard limit).

---

## 4. Acceptance Criteria

- [ ] `check()` returns empty list for files under 100K tokens.
- [ ] `check()` returns E008 for files over 100K tokens.
- [ ] `check()` returns empty list for files at exactly 100K tokens (boundary: `> 100_000`, not `>=`).
- [ ] E008 diagnostic includes actual token count and hard limit in `context`.
- [ ] Hard limit sourced from `TOKEN_ZONES["DEGRADATION"]`, not hardcoded.

---

## 5. Test Plan

### `tests/test_validation_l0_size_limit.py`

| Test                           | Input (`estimated_tokens`) | Expected                                            |
| ------------------------------ | -------------------------- | --------------------------------------------------- |
| `test_small_file_passes`       | `500`                      | `[]`                                                |
| `test_large_file_passes`       | `99_999`                   | `[]`                                                |
| `test_boundary_at_limit`       | `100_000`                  | `[]` (not exceeded)                                 |
| `test_over_limit_fails`        | `100_001`                  | `[E008]`                                            |
| `test_context_includes_counts` | `150_000`                  | E008 `context` contains `"150,000"` and `"100,000"` |
