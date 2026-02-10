# v0.3.2b — URL Validation

> **Version:** v0.3.2b
> **Document Type:** Design Specification (sub-part)
> **Status:** DRAFT
> **Created:** 2026-02-10
> **Parent:** [RR-SPEC-v0.3.2-l2-content-quality.md](RR-SPEC-v0.3.2-l2-content-quality.md)
> **Grounding:** DS-VC-CON-002 (URL Resolvability, 4 pts SOFT), v0.0.4a §LNK-002, AP-CRIT-004 (Link Void)
> **Depends On:** v0.2.0 (`ParsedLink.url`, `ParsedLink.is_valid_url`), v0.3.0g (L0 syntactic URL validation), v0.3.1d (L1 link text check)
> **Module:** `src/docstratum/validation/checks/l2_url_validation.py`
> **Tests:** `tests/test_validation_l2_url_validation.py`

---

## 1. Purpose

Verify that linked URLs are reachable — that they resolve to accessible pages when accessed via HTTP. Broken links are a leading cause of documentation decay (v0.0.4c AP-CRIT-004, Link Void) and erode user trust.

### 1.1 Layered URL Checking

URL validation spans three pipeline levels, each with a distinct focus:

| Layer       | Level  | Check                | What It Catches           | Code     |
| ----------- | ------ | -------------------- | ------------------------- | -------- |
| v0.3.0g     | L0     | Syntactic URL format | Empty/malformed URL slots | E006     |
| v0.3.1d     | L1     | Link text presence   | Empty link text `[](url)` | E006     |
| **v0.3.2b** | **L2** | **URL reachability** | **HTTP 4xx, DNS failure** | **E006** |

All three share E006 but at different levels and with different context strings.

### 1.2 The Configuration Flag

> [!IMPORTANT]
> URL reachability is **opt-in**, gated behind `check_urls: bool` (default: `false`).
>
> When `check_urls=false` (default), v0.3.2b emits **zero diagnostics** and returns immediately. This is the expected behavior for offline validation, CI pipelines prioritizing speed, and environments without external network access.
>
> When `check_urls=true`, every syntactically valid URL is checked via HTTP. This introduces latency (up to `url_timeout` × N_unique_urls seconds) but provides the most thorough validation.

---

## 2. Diagnostic Code

| Code | Severity | Criterion     | Message                                              | Remediation                                                                  |
| ---- | -------- | ------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------- |
| E006 | ERROR    | DS-VC-CON-002 | Section contains links with empty or malformed URLs. | Fix or remove links with empty href values. Ensure all URLs are well-formed. |

> The message is the existing E006 message. The `context` field differentiates the specific sub-issue. At L2, the context indicates an HTTP failure rather than a syntactic issue.

---

## 3. Check Logic

```python
"""L2 URL reachability check.

Optionally resolves all URLs via HTTP HEAD to detect broken links.
Gated behind check_urls flag (default: false).

Implements v0.3.2b. Criterion: DS-VC-CON-002.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


def check(
    parsed: "ParsedLlmsTxt",
    classification: "DocumentClassification",
    file_meta: "FileMetadata",
    *,
    check_urls: bool = False,
    url_timeout: float = 5.0,
) -> list[ValidationDiagnostic]:
    """Check URL reachability for all links.

    When check_urls=false (default), returns immediately with no
    diagnostics. When check_urls=true, sends HTTP HEAD requests to
    each unique URL and reports failures.

    Args:
        parsed: The parsed file model with sections and links.
        classification: Not used by this check.
        file_meta: Not used by this check.
        check_urls: Whether to perform HTTP resolution. Default false.
        url_timeout: Timeout in seconds per URL. Default 5.0.

    Returns:
        List of E006 diagnostics, one per unreachable URL.
    """
    if not check_urls:
        return []

    diagnostics: list[ValidationDiagnostic] = []

    # Collect unique URLs and their first-occurrence metadata
    url_registry: dict[str, _UrlMeta] = {}
    for section in parsed.sections:
        for link in section.links:
            if link.url and link.url not in url_registry:
                url_registry[link.url] = _UrlMeta(
                    url=link.url,
                    line_number=link.line_number,
                    title=link.title or "",
                )

    # Resolve each unique URL
    for url, meta in url_registry.items():
        result = _resolve_url(url, timeout=url_timeout)
        if result.should_report:
            diagnostics.append(
                ValidationDiagnostic(
                    code=DiagnosticCode.E006_BROKEN_LINKS,
                    severity=Severity.ERROR,
                    message=DiagnosticCode.E006_BROKEN_LINKS.message,
                    remediation=DiagnosticCode.E006_BROKEN_LINKS.remediation,
                    level=ValidationLevel.L2_CONTENT,
                    check_id="LNK-002",
                    line_number=meta.line_number,
                    context=(
                        f"URL '{url}' returned HTTP {result.status_code}. "
                        f"Link: [{meta.title}]({url})."
                    ),
                )
            )

    return diagnostics
```

### 3.1 URL Resolution Rules

```python
class _UrlResolutionResult:
    """Result of resolving a single URL."""
    status_code: int | None
    error: str | None
    should_report: bool


def _resolve_url(url: str, *, timeout: float = 5.0) -> _UrlResolutionResult:
    """Resolve a single URL via HTTP HEAD (with GET fallback).

    Resolution rules:
    - HTTP 2xx → pass (should_report=False)
    - HTTP 3xx → follow redirect (up to 3 hops), evaluate final status
    - HTTP 4xx → report as broken (should_report=True)
    - HTTP 405  → retry with GET (some servers reject HEAD)
    - HTTP 5xx → skip (server error, not a documentation problem)
    - Timeout  → skip (transient network issue)
    - DNS failure → skip (transient or internal network URL)
    - HTTP 401/403/429 → skip (auth-gated or rate-limited)
    """
```

### 3.2 HTTP Status Classification

| Status Range       | Action                         | should_report           | Rationale                                  |
| ------------------ | ------------------------------ | ----------------------- | ------------------------------------------ |
| 2xx                | Pass                           | `False`                 | URL is reachable                           |
| 301, 302, 307, 308 | Follow redirect (up to 3 hops) | Depends on final status | Permanent or temporary redirect            |
| 401, 403           | Skip                           | `False`                 | Auth-gated — not a documentation problem   |
| 404, 410           | Report                         | `True`                  | Page removed or never existed              |
| 405                | Retry with GET                 | —                       | Some servers reject HEAD                   |
| 429                | Skip                           | `False`                 | Rate-limited — transient                   |
| 5xx                | Skip                           | `False`                 | Server error — not a documentation problem |
| Timeout            | Skip                           | `False`                 | Transient network issue                    |
| DNS failure        | Skip                           | `False`                 | Transient or internal network              |
| Connection error   | Skip                           | `False`                 | Transient network issue                    |

### 3.3 Decision: URL Caching

URLs are deduplicated within a single validation run. If the same URL appears in multiple sections, it is resolved only once. The diagnostic is attached to the **first occurrence** of the URL.

```python
# URL deduplication is handled by the url_registry dict:
# - Key: URL string
# - Value: metadata from first occurrence (line_number, title)
# Subsequent occurrences are silently skipped.
```

### 3.4 Decision: Dependency on `httpx`

v0.3.2b requires an HTTP client. The recommended library is `httpx` (modern, async-capable, timeout-aware). It is an **optional dependency** — if `httpx` is not installed and `check_urls=true`, the check should raise a clear error:

```python
try:
    import httpx
except ImportError:
    raise ImportError(
        "httpx is required for URL validation (check_urls=true). "
        "Install it with: pip install docstratum[url-check]"
    ) from None
```

### 3.5 Decision: No Parallel Resolution (v0.3.2b)

v0.3.2b resolves URLs sequentially for simplicity. Parallel resolution (async) is deferred to a future optimization pass. For a file with 50 unique URLs at 5s timeout, worst case is ~250 seconds. This is acceptable for an opt-in feature.

---

## 4. Acceptance Criteria

- [ ] `check()` returns `[]` when `check_urls=false` (default).
- [ ] `check()` returns E006 per unreachable URL when `check_urls=true`.
- [ ] HTTP 2xx → no diagnostic.
- [ ] HTTP 3xx → follows redirects (up to 3), evaluates final status.
- [ ] HTTP 404 → E006.
- [ ] HTTP 5xx → skipped (no diagnostic).
- [ ] HTTP 401/403 → skipped.
- [ ] HTTP 429 → skipped.
- [ ] Timeout → skipped.
- [ ] DNS failure → skipped.
- [ ] Duplicate URLs resolved only once.
- [ ] E006 uses `level=L2_CONTENT`, `check_id="LNK-002"`.
- [ ] `url_timeout` is configurable (default 5.0 seconds).
- [ ] Missing `httpx` raises `ImportError` when `check_urls=true`.

---

## 5. Test Plan

### `tests/test_validation_l2_url_validation.py`

All HTTP-dependent tests use **mocked responses** (via `httpx.MockTransport` or `respx`).

| Test                                  | Input                         | Expected                     |
| ------------------------------------- | ----------------------------- | ---------------------------- |
| `test_check_urls_false_returns_empty` | `check_urls=false`, any links | `[]`                         |
| `test_check_urls_true_all_200_passes` | All URLs return 200           | `[]`                         |
| `test_404_emits_e006`                 | URL returns 404               | `[E006]`                     |
| `test_410_emits_e006`                 | URL returns 410               | `[E006]`                     |
| `test_301_redirect_followed`          | URL returns 301 → 200         | `[]`                         |
| `test_301_redirect_to_404`            | URL returns 301 → 404         | `[E006]`                     |
| `test_500_skipped`                    | URL returns 500               | `[]`                         |
| `test_403_skipped`                    | URL returns 403               | `[]`                         |
| `test_429_skipped`                    | URL returns 429               | `[]`                         |
| `test_timeout_skipped`                | URL times out                 | `[]`                         |
| `test_dns_failure_skipped`            | DNS resolution fails          | `[]`                         |
| `test_duplicate_urls_resolved_once`   | Same URL in 2 sections        | 1 resolution, 1 or 0 E006    |
| `test_e006_level_is_l2`               | Broken URL                    | E006 with `level=L2_CONTENT` |
| `test_e006_context_shows_status`      | URL returns 404               | Context contains "HTTP 404"  |

---

## 6. Design Decisions

| Decision                              | Choice | Rationale                                                                                  |
| ------------------------------------- | ------ | ------------------------------------------------------------------------------------------ |
| Opt-in via `check_urls=false` default | Yes    | Network dependency, latency, false negatives. Speed is the default priority.               |
| ERROR severity for E006 at L2         | Yes    | Broken URLs are a HARD failure. But gated behind flag so default config has no ERRORs.     |
| Reuse E006 (not new code)             | Yes    | Same diagnostic family as syntactic link failures — already covers "broken links."         |
| HEAD with GET fallback                | Yes    | HEAD is lightweight; GET catches servers that reject HEAD (405).                           |
| Skip 401/403/429/5xx/timeout          | Yes    | These are transient or auth-gated — not documentation quality issues.                      |
| Sequential resolution (no async)      | Yes    | Simplicity for v0.3.2b. Async deferred to future optimization.                             |
| `httpx` as optional dependency        | Yes    | URL checking is opt-in; the core library shouldn't require HTTP dependencies.              |
| URL deduplication per run             | Yes    | Same URL in multiple sections → one HTTP call. Avoids redundant network and rate-limiting. |
