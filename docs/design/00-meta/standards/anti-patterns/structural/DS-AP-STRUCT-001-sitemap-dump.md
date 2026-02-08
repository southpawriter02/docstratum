# DS-AP-STRUCT-001: Sitemap Dump

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-STRUCT-001 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-STRUCT-001 |
| **Category** | Structural |
| **Check ID** | CHECK-005 |
| **Severity Impact** | Reduce structural dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Entire sitemap dumped as flat link list with no organization. File is just hundreds of URLs with no categorization, no H2 sections, no descriptions — a raw export from a sitemap generator. This anti-pattern presents a wall of URLs to LLM agents, providing no navigational structure or semantic organization, making it impossible for systems to understand the purpose or hierarchy of linked resources.

## Detection Logic

```python
def detect_sitemap_dump(file_content):
    """
    Detects if a markdown file is a sitemap dump.
    
    Triggers if:
    - File has ≥50 links AND ≤1 H2 section, OR
    - link_count / section_count > 30
    """
    import re
    
    # Count markdown links [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, file_content)
    link_count = len(links)
    
    # Count H2 sections
    h2_pattern = r'^## '
    h2_sections = len(re.findall(h2_pattern, file_content, re.MULTILINE))
    
    # Condition 1: ≥50 links but ≤1 H2 section
    if link_count >= 50 and h2_sections <= 1:
        return True, f"Sitemap dump detected: {link_count} links, {h2_sections} H2 sections"
    
    # Condition 2: link_count / section_count > 30
    if h2_sections > 0 and (link_count / h2_sections) > 30:
        return True, f"Sitemap dump detected: {link_count} links / {h2_sections} sections = {link_count/h2_sections:.1f}"
    
    return False, "No sitemap dump pattern detected"
```

## Example (Synthetic)

```markdown
# Sitemap

- [Home](/)
- [About](/about)
- [Services](/services)
- [Blog](/blog/post-1)
- [Blog](/blog/post-2)
- [Blog](/blog/post-3)
- [Contact](/contact)
- [Products](/products/item-1)
- [Products](/products/item-2)
- [Products](/products/item-3)
- [Products](/products/item-4)
- [FAQ](/faq)
- [Terms](/terms)
- [Privacy](/privacy)
- [Careers](/careers)
- [Support](/support)
- [Documentation](/docs/intro)
- [Documentation](/docs/install)
- [Documentation](/docs/api)
- [Documentation](/docs/examples)
... [40+ more raw URLs with no H2 structure]
```

## Remediation

1. **Identify logical groupings**: Analyze the URL list and group related pages by functional area (e.g., Blog, Products, Documentation, Legal, Support).
2. **Create H2 sections**: Introduce meaningful H2 headers for each grouping.
3. **Add descriptive context**: Under each H2, provide a brief description of the section's purpose before listing links.
4. **Organize hierarchically**: Use H3 or nested lists for sub-categories within sections.
5. **Link descriptions**: Replace bare URLs with descriptive link text that explains what each link contains.

**Remediated Example:**

```markdown
# Sitemap

## Getting Started
Quick access to essential pages.
- [Home](/) — Main landing page
- [About](/about) — Company overview
- [Contact](/contact) — Contact information

## Products & Services
Browse our offerings and solutions.
- [Services](/services) — Full service catalog
- [Products](/products) — Product listing
  - [Item 1](/products/item-1)
  - [Item 2](/products/item-2)

## Documentation
Technical guides and resources.
- [Introduction](/docs/intro)
- [Installation](/docs/install)
- [API Reference](/docs/api)
- [Examples](/docs/examples)

## Legal & Support
- [FAQ](/faq)
- [Terms of Service](/terms)
- [Privacy Policy](/privacy)
- [Support](/support)

## Company
- [Careers](/careers)
```

## Affected Criteria

- **DS-VC-STR-009**: No Structural Anti-Patterns — Sitemap dumps violate the structural integrity requirement
- **DS-VC-STR-004**: H2 Section Structure — Files must have organized sections with H2 headers

## Emitted Diagnostics

Scored through structural dimension evaluation. No specific diagnostic codes emitted; severity is reflected in overall structural score reduction.

## Related Anti-Patterns

- **DS-AP-STRAT-001** (Automation Obsession) — Sitemap dumps are typically auto-generated from sitemap.xml exports without human curation

## Change History

| Version | Date | Description |
|---------|------|-------------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
