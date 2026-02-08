# DS-AP-CRIT-004: Link Void

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CRIT-004 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-CRIT-004 |
| **Category** | Critical |
| **Check ID** | CHECK-004 (v0.0.4c) |
| **Severity Impact** | Gate structural score at 29 — total quality score capped regardless of other dimensions |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog; v0.0.4a §LNK-002 |

## Description

All or most links are broken, empty, or malformed. An llms.txt file's primary purpose is to direct LLM agents to documentation pages via links. If >80% of links are non-functional, the file is essentially useless as a navigation index.

## Detection Logic

```python
def detect_link_void(file_content: str) -> bool:
    """
    Detect broken, empty, or malformed links.
    
    Returns True if broken_count / total_links > 0.8
    
    Checks:
    1. URL is non-empty
    2. URL is well-formed (valid URI syntax)
    3. URL resolves (HTTP 200/301/302)
    """
    import re
    import requests
    
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', file_content)
    
    if len(links) == 0:
        return False
    
    broken_count = 0
    
    for text, url in links:
        # Check if URL is empty
        if not url or url.strip() == '':
            broken_count += 1
            continue
        
        # Check if URL is well-formed
        if not is_valid_uri(url):
            broken_count += 1
            continue
        
        # Check if URL resolves
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code not in [200, 301, 302]:
                broken_count += 1
        except requests.RequestException:
            broken_count += 1
    
    broken_ratio = broken_count / len(links)
    return broken_ratio > 0.80

def is_valid_uri(url: str) -> bool:
    """Validate URI format."""
    uri_regex = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(uri_regex, url))
```

## Example (Synthetic)

```markdown
## Documentation Links

- [Feature Overview](https://docs.example.com/features) — Returns 404
- [API Reference](https://docs.example.com/api) — Returns 404
- [Tutorial](https://docs.example.com/tutorial) — Returns 404
- [Guide](https://docs.example.com/guide) — Returns 404
- [FAQ](https://docs.example.com/faq) — Returns 404
- [Support]() — Empty URL
- [Contact](not-a-url) — Malformed
- [Home](https://docs.example.com/home) — Returns 404
- [Examples](https://docs.example.com/examples) — Returns 404
- [Changelog](https://docs.example.com/changelog) — Returns 404
```

9 out of 10 links are broken or malformed — triggers Link Void.

## Remediation

1. Verify all URLs resolve:
   ```bash
   curl -I https://example.com/page
   ```

2. Remove broken links or update to correct URLs

3. Replace with absolute URLs where possible instead of relative paths

4. Test links regularly with automated link checking tools:
   ```bash
   markdown-link-check file.md
   ```

5. Keep a maintenance schedule for periodic link audits

## Affected Criteria

- DS-VC-STR-008 (No Critical Anti-Patterns)
- DS-VC-STR-005 (Link Format Compliance)
- DS-VC-CON-002 (URL Resolvability)

## Emitted Diagnostics

- **DS-DC-E006**: BROKEN_LINKS — >80% of links non-functional

## Related Anti-Patterns

- DS-AP-CONT-004 (Link Desert — links exist but lack descriptions vs links that don't work)
- DS-AP-ECO-002 (Phantom Links — ecosystem-level version of broken links)

## Change History

| ASoT Version | Date | Change |
|---|---|---|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
