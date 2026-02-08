# DS-VC-APD-007: Relative URL Minimization

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-APD-007 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L4-07 |
| **Dimension** | Anti-Pattern Detection (20%) |
| **Level** | L4 — Exemplary |
| **Weight** | 2 / 20 anti-pattern points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | Practical: MCP-based consumption often strips base URL context; relative URLs break when file is consumed outside web context; v0.0.4a link checks |

## Description

This criterion checks that the file minimizes use of relative URLs in favor of absolute URLs. The rationale is pragmatic and delivery-model-dependent.

The dominant consumption model for llms.txt files as of 2026 is through Model Context Protocol (MCP) integration, where AI coding assistants and agents read file content without retained base URL context. In this consumption model, relative URLs (e.g., `./docs/guide.md`, `../other/page`, or even bare anchors like `#section`) become unresolvable — the agent has no way to compute the full path.

Absolute URLs (beginning with `http://` or `https://`) are resolution-independent. An agent reading an absolute URL can follow it directly without knowledge of the original document's location. This makes absolute URLs the preferred choice for AI-consumable documentation.

Relative URLs are sometimes acceptable (e.g., fragment anchors like `#section-name` that link within the same document), but they should be minimized. A small number of relative URLs (e.g., up to 10%) may be tolerated, but files with heavy reliance on relative URLs risk breakage when consumed via MCP or other non-web contexts.

## Pass Condition

All or nearly all URLs are absolute (begin with `http://` or `https://`):

```python
# Extract all URLs from the content
import re
url_pattern = r'(?:https?://\S+|[./][^\s\)]+\.(?:md|html|pdf|txt)|\#\w+)'
urls = re.findall(url_pattern, content)

# Classify URLs as absolute or relative
absolute_urls = [u for u in urls if u.startswith(('http://', 'https://'))]
relative_urls = [u for u in urls if not u.startswith(('http://', 'https://'))]

if urls:
    relative_ratio = len(relative_urls) / len(urls)
    # Allow up to 10% relative URLs (anchors, etc.)
    assert relative_ratio <= 0.10  # [CALIBRATION-NEEDED: 10% threshold]
```

A small number of relative URLs (e.g., anchors like `#section`) or internal links within the same document may be acceptable. The threshold allows up to 10% relative URLs to account for this flexibility.

## Fail Condition

More than 10% of URLs are relative:

- Paths like `./doc.md`, `../other/page`, or `docs/guide.md` without a scheme
- URLs missing the `http://` or `https://` scheme (except for fragment anchors and relative paths that may be acceptable in small numbers)
- Heavy reliance on relative URLs that would break when the file is consumed outside its web context

**Gate behavior:** This is a SOFT criterion at L4. Failure reduces the Anti-Pattern Detection score but does not block progression.

## Emitted Diagnostics

- **DS-DC-I004** (INFO): Emitted when relative URLs are detected. Suggests converting them to absolute URLs for better portability. The message indicates that relative URLs may not resolve when the file is consumed outside its original web context.

## Related Anti-Patterns

No specific anti-pattern is directly named for relative URL issues, but the concern overlaps with general link quality and portability concerns.

## Related Criteria

- **DS-VC-STR-005** (Link Format Compliance): Checks that links follow Markdown syntax conventions (`[text](url)` format). APD-007 checks URL scheme; STR-005 checks syntactic correctness.
- **DS-VC-CON-002** (URL Resolvability): Checks that URLs are valid and resolvable. Relative URLs may not resolve without base URL context, failing this criterion.

## Calibration Notes

Relative URL issues are a practical concern specific to MCP-based consumption. When an AI coding assistant reads an llms.txt file through the MCP protocol, it receives the file content but typically not the base URL or navigation context of the original web server. In this scenario, relative URLs become unresolvable.

The v0.0.4a link checks found that:
- **Most published llms.txt files (>90%)** use absolute URLs exclusively
- **Relative URLs are rare** in production llms.txt implementations
- **When they do occur**, they are typically anchor links (`#section`) or references to sibling files that are unlikely to be available in the consuming context

The 10% threshold is conservative and accounts for the small number of intra-document anchors and internal links that may be present. Files with more than 10% relative URLs are likely to exhibit breakage when consumed via MCP or other non-web delivery mechanisms.

This criterion rewards files that are portable and robust across consumption models — a key design goal for AI-consumable documentation.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C exemplary criterion |
