# v0.3.0g — Link Format Validation (Syntactic)

> **Version:** v0.3.0g
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.0-l0-parseable-gate.md](RR-SPEC-v0.3.0-l0-parseable-gate.md)
> **Grounding:** v0.0.4a §LNK-001, §LNK-002, DiagnosticCode.E006_BROKEN_LINKS
> **Depends On:** v0.2.0 (`ParsedLlmsTxt.sections`, `ParsedLink.url`, `ParsedLink.is_valid_url`)
> **Module:** `src/docstratum/validation/checks/l0_link_format.py`
> **Tests:** `tests/test_validation_l0_link_format.py`

---

## 1. Purpose

Detect links with syntactically malformed or empty URLs. This is **syntactic** validation only — it verifies that each `[text](url)` pattern contains a parseable URL string. URL reachability (does the URL respond with HTTP 200?) is a separate L2 check (v0.3.2b).

E006 can fire multiple times per file — once per broken link. A file with >80% broken links triggers the "Link Void" critical anti-pattern (AP-CRIT-004), detected in v0.3.4a.

---

## 2. Diagnostic Code

| Code | Severity | Message                                               | Remediation                                                                                       |
| ---- | -------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| E006 | ERROR    | Broken link: URL is empty or syntactically malformed. | Fix the URL. Ensure it uses a valid scheme (https://, http://) or is a well-formed relative path. |

---

## 3. Check Logic

```python
"""L0 link format validation check.

Verifies that all links have syntactically valid, non-empty URLs.
Emits one E006 per malformed link. Does NOT check URL reachability.

Implements v0.3.0g.
"""


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
) -> list[ValidationDiagnostic]:
    """Check that all links have valid URL syntax.

    Iterates over every ParsedLink in every ParsedSection and checks:
    1. URL is not empty
    2. is_valid_url flag is True (set by v0.2.0 parser)

    Args:
        parsed: The parsed file model with sections and links.
        classification: Not used by this check.
        file_meta: Not used by this check.

    Returns:
        List of E006 diagnostics, one per broken link.
    """
    diagnostics: list[ValidationDiagnostic] = []

    for section in parsed.sections:
        for link in section.links:
            if not link.url or not link.is_valid_url:
                diagnostics.append(
                    ValidationDiagnostic(
                        code=DiagnosticCode.E006_BROKEN_LINKS,
                        severity=Severity.ERROR,
                        message=DiagnosticCode.E006_BROKEN_LINKS.message,
                        remediation=DiagnosticCode.E006_BROKEN_LINKS.remediation,
                        level=ValidationLevel.L0_PARSEABLE,
                        check_id="LNK-001",
                        line_number=link.line_number,
                        context=(
                            f"Link: [{link.title}]({link.url or '<empty>'})"
                        ),
                    )
                )

    return diagnostics
```

### 3.1 What Constitutes a "Broken" Link at L0

| Scenario                 | `url`                  | `is_valid_url` | E006?                   |
| ------------------------ | ---------------------- | -------------- | ----------------------- |
| Valid absolute URL       | `https://example.com`  | `True`         | No                      |
| Valid relative URL       | `/docs/api`            | `True`         | No                      |
| Empty URL                | `""`                   | `False`        | Yes                     |
| No URL (None)            | `None`                 | `False`        | Yes                     |
| Malformed URL            | `not a url at all`     | `False`        | Yes                     |
| URL with spaces          | `https://example .com` | `False`        | Yes                     |
| Bare URL (no `[text]()`) | Not a link             | —              | Not extracted by parser |

### 3.2 Distinction from v0.3.2b (URL Reachability)

| Check                | Level | What It Verifies                    | Network?       |
| -------------------- | ----- | ----------------------------------- | -------------- |
| v0.3.0g (this check) | L0    | Can the URL string be parsed?       | No             |
| v0.3.2b              | L2    | Does the URL respond with HTTP 2xx? | Yes (optional) |

Both checks emit E006, but with different `context` strings:

- v0.3.0g: `"Link: [Title](<empty>)"` — syntactic issue
- v0.3.2b: `"HTTP 404 for https://example.com/deleted"` — reachability issue

### 3.3 Anti-Pattern Integration

If the ratio of broken links to total links exceeds 80%, the "Link Void" anti-pattern (AP-CRIT-004) is triggered. This detection happens in v0.3.4a, not in this check — this check simply emits the individual E006 diagnostics.

```
E006 count / total links > 0.80  →  AP-CRIT-004 (Link Void)
```

---

## 4. Acceptance Criteria

- [ ] `check()` returns empty list when all links have valid URLs.
- [ ] `check()` returns E006 for each link with empty URL.
- [ ] `check()` returns E006 for each link with `is_valid_url=False`.
- [ ] Multiple broken links produce multiple E006 diagnostics (one per link).
- [ ] E006 diagnostic includes `line_number` of the broken link.
- [ ] E006 diagnostic `context` shows the link title and URL.
- [ ] No network access performed (syntactic only).
- [ ] Links across multiple sections all checked.
- [ ] Files with zero links produce zero diagnostics (no links = no broken links).

---

## 5. Test Plan

### `tests/test_validation_l0_link_format.py`

| Test                             | Input                                    | Expected                  |
| -------------------------------- | ---------------------------------------- | ------------------------- |
| `test_all_valid_links_pass`      | 3 links, all `is_valid_url=True`         | `[]`                      |
| `test_empty_url_fails`           | 1 link with `url=""`                     | `[E006]`                  |
| `test_none_url_fails`            | 1 link with `url=None`                   | `[E006]`                  |
| `test_invalid_url_fails`         | 1 link with `is_valid_url=False`         | `[E006]`                  |
| `test_multiple_broken_links`     | 3 broken links across 2 sections         | 3 × E006 diagnostics      |
| `test_mixed_valid_invalid`       | 2 valid + 1 invalid                      | 1 × E006                  |
| `test_no_links_passes`           | File with sections but no links          | `[]`                      |
| `test_e006_includes_line_number` | Link at line 5 with `is_valid_url=False` | E006 with `line_number=5` |

---

## 6. Design Decisions

| Decision                    | Choice    | Rationale                                                                      |
| --------------------------- | --------- | ------------------------------------------------------------------------------ |
| One E006 per broken link    | Yes       | Allows counting for AP-CRIT-004 threshold and per-link remediation             |
| `is_valid_url` from parser  | Read-only | The parser (v0.2.0b) sets this flag; the validator does not re-validate        |
| Empty URL treated as broken | Yes       | `[text]()` is syntactically valid Markdown but semantically broken             |
| No network check            | Yes       | This is L0 (syntactic). Network checks are L2 (v0.3.2b)                        |
| Relative URLs not flagged   | Yes       | Relative URLs are syntactically valid; I004 (INFO) at L2 handles observability |
