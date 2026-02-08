# DS-AP-CONT-004: Link Desert

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CONT-004 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-CONT-004 |
| **Category** | Content |
| **Check ID** | CHECK-013 |
| **Severity Impact** | Reduce content dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Links appear in documentation but lack meaningful descriptions, presenting as bare URLs or single-word text. LLM agents receive no context about what each link leads to, forcing them to either make assumptions or halt processing. This anti-pattern degrades the utility of reference documentation and prevents agents from making informed navigation decisions.

## Detection Logic

```python
def detect_link_desert(content):
    """
    Identify links with missing or inadequate descriptions.
    
    Algorithm:
    1. Extract all markdown links: [description](url)
    2. For each link:
       a. Extract description text
       b. Check if description is empty
       c. Check if description == URL (bare link)
       d. Check if description length < 5 chars
    3. Calculate bare_link_ratio = bare_links / total_links
    4. If bare_link_ratio > 0.30 (30%), trigger anti-pattern
    
    Returns: (triggered, bare_link_ratio, list of bare_links)
    """
    import re
    
    link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(link_pattern, content)
    
    if not matches:
        return False, 0.0, []
    
    bare_links = []
    for description, url in matches:
        desc_stripped = description.strip()
        if (not desc_stripped or 
            desc_stripped == url or 
            len(desc_stripped) < 5):
            bare_links.append((desc_stripped, url))
    
    ratio = len(bare_links) / len(matches)
    return ratio > 0.30, ratio, bare_links
```

## Example (Synthetic)

```markdown
## Resources

- https://example.com/docs
- [](https://api.example.com)
- [link](https://github.com/example/repo)
- http://blog.example.com/tutorials
- [see](https://docs.example.com/guide)
```

Out of 5 links, 3 have inadequate descriptions (bare URL, empty description, or single word). The bare_link_ratio is 0.60 (60%), triggering the anti-pattern.

## Remediation

1. Provide descriptive link text that explains the destination: `[Setting up authentication](https://docs.example.com/auth)`
2. Avoid single-word descriptors like "link" or "here" — use specific context
3. Make link text scannable: readers should understand the link's purpose without clicking
4. Test documentation with LLM agents to ensure link context is clear
5. Implement CI checks to flag links with descriptions shorter than 5 characters

## Affected Criteria

- DS-VC-APD-004 (Content must be scannable and navigable)
- DS-VC-CON-001 (Non-Empty Link Descriptions — link descriptions must be substantive)

## Emitted Diagnostics

- DS-DC-W003 (LINK_MISSING_DESCRIPTION — warning for bare or inadequate link text)

## Related Anti-Patterns

- DS-AP-CRIT-004 (Link Void — broken links vs undescribed links; both render navigation useless)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
