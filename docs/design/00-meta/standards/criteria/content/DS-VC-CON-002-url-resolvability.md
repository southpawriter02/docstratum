# DS-VC-CON-002: URL Resolvability

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-002 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L2-02 |
| **Dimension** | Content (50%) |
| **Level** | L2 — Content Quality |
| **Weight** | 4 / 50 content points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Measurable with caveats |
| **Provenance** | Official spec implicit (links should be usable); v0.0.4c AP-CRIT-004 (Link Void); practical: broken links degrade trust |

## Description

This criterion verifies that URLs referenced in links are resolvable — that is, they return valid HTTP responses when accessed. Broken links are a leading cause of documentation decay and erode user trust. When a reader encounters a broken link, it signals that the documentation is outdated or poorly maintained.

URL resolvability is measurable but comes with caveats. Some URLs may be behind authentication gates (returning 403), rate-limited (returning 429), or restricted to internal networks. The criterion must account for these real-world scenarios to avoid false positives.

The measurement is performed via HTTP HEAD request to minimize bandwidth usage, with a timeout threshold to prevent hanging on unresponsive servers. Files may optionally skip URL checks for offline validation (`--skip-url-checks` flag) when network access is unavailable or restricted.

## Pass Condition

URLs resolve to HTTP 200 (success) or 3xx (redirect) when accessed via HEAD request:

```python
urls = extract_all_urls_from_links(content)
resolvable_urls = [
    url for url in urls
    if request_head(url, timeout=10).status_code in (200, 301, 302, 307, 308)
]
resolution_ratio = len(resolvable_urls) / len(urls) if urls else 1.0
assert resolution_ratio >= 0.5  # [CALIBRATION-NEEDED]
```

**Exclusions from failure count:**
- HTTP 403 (Forbidden) — auth-gated URLs
- HTTP 429 (Too Many Requests) — rate-limited responses
- HTTP 401 (Unauthorized) — authentication required
- Internal network URLs (e.g., `http://localhost`, `http://192.168.x.x`)
- Timeout (10 seconds per URL)

These are counted as "not counted in failure" rather than as "successful," preserving the resolution ratio denominator but preventing false negatives.

## Fail Condition

More than 50% of links return HTTP 4xx or 5xx errors (other than 403, 401, 429) or timeout. The criterion also fails if **all** links are broken, which triggers the anti-pattern **DS-AP-CRIT-004** (Link Void) at critical severity.

- E006 fires for each broken/malformed link individually, enabling granular diagnostics.
- Malformed URLs (e.g., spaces, invalid characters) are treated as failures.

## Emitted Diagnostics

- **DS-DC-E006** (ERROR): Links with empty, malformed, or unreachable URLs. Fires per broken link.

## Related Anti-Patterns

- **DS-AP-CRIT-004** (Link Void): All or nearly all links broken or malformed. This is a critical-severity anti-pattern signaling severe documentation decay.

## Related Criteria

- **DS-VC-STR-005** (Link Format Compliance): Checks Markdown link syntax correctness (e.g., `[text](url)`); DS-VC-CON-002 checks that the resolved URL is actually reachable.
- **DS-VC-CON-001** (Non-empty Descriptions): Addresses link description quality; CON-002 addresses link destination validity.

## Calibration Notes

URL resolution is environment-dependent. Some specimens have links valid on corporate networks but failing externally. The validator should support a `--skip-url-checks` flag for offline or fast-path validation.

Threshold [CALIBRATION-NEEDED]: The 50% resolution ratio is provisional and should be calibrated against the 11 empirical specimens once Phase C scoring is complete. Early analysis suggests files with <50% resolution are typically in the bottom quartile of overall quality.

Timeout considerations: A 10-second timeout per URL prevents the validator from hanging on unresponsive servers. For large files with many links, total validation time can be substantial — consider parallel HEAD requests where bandwidth permits.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
