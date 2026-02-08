# DS-AP-CONT-007: Formulaic Description

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CONT-007 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Registry ID** | AP-CONT-007 |
| **Category** | Content |
| **Check ID** | CHECK-019 |
| **Severity Impact** | Reduce content dimension score |
| **Provenance** | v0.0.4c; v0.0.4b §CNT-005; v0.0.2b auto-generation patterns |

## Description

Link descriptions follow rigid, templated patterns indicating automated generation (common with documentation tools like Mintlify). Links are described with identical formulaic phrases: "Learn about X", "Guide to Y", "Overview of Z". This anti-pattern suggests low human curation and provides minimal additional context beyond the link destination itself. LLM agents cannot distinguish between sections based on description uniqueness.

## Detection Logic

```python
def detect_formulaic_description(content):
    """
    Identify link descriptions matching template patterns.
    
    Algorithm:
    1. Extract all markdown link descriptions: [description](url)
    2. For each description, apply template regex patterns:
       - "^(Learn|Guide|Overview|Introduction|Understand|Explore) (about|to|for|of|in) "
       - "^[A-Z][a-z]+ (documentation|guide|tutorial|reference|manual)$"
    3. Count matches against total links
    4. Calculate formulaic_ratio = matching_descriptions / total_descriptions
    5. If formulaic_ratio > 0.50 (50%), trigger anti-pattern
    
    Returns: (triggered, formulaic_ratio, matching_descriptions)
    """
    import re
    
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(link_pattern, content)
    
    if not matches:
        return False, 0.0, []
    
    template_patterns = [
        r'^(Learn|Guide|Overview|Introduction|Understand|Explore)\s+(about|to|for|of|in)\s+',
        r'^[A-Z][a-z]+\s+(documentation|guide|tutorial|reference|manual)$'
    ]
    
    formulaic_descriptions = []
    for description, url in matches:
        desc_stripped = description.strip()
        for pattern in template_patterns:
            if re.match(pattern, desc_stripped):
                formulaic_descriptions.append(desc_stripped)
                break
    
    ratio = len(formulaic_descriptions) / len(matches) if matches else 0.0
    return ratio > 0.50, ratio, formulaic_descriptions
```

## Example (Synthetic)

```markdown
## Documentation

- [Learn about authentication](https://docs.example.com/auth)
- [Learn about configuration](https://docs.example.com/config)
- [Learn about deployment](https://docs.example.com/deploy)
- [Overview of the API](https://api.example.com/docs)
- [Guide to error handling](https://docs.example.com/errors)
```

4 out of 5 links use formulaic descriptions. The descriptions add no unique context; a reader cannot distinguish sections without visiting each link.

## Remediation

1. Write unique, descriptive link text that explains the specific content or purpose
2. Avoid generic template phrases; instead, convey what problem the link solves
3. Example improvements:
   - "Learn about authentication" → "JWT-based authentication implementation"
   - "Overview of the API" → "RESTful API endpoints and request/response formats"
4. Have humans review all link descriptions to ensure uniqueness and clarity
5. Implement CI checks to detect common template patterns and flag for review
6. For generated documentation, post-process links to inject contextual descriptions

## Affected Criteria

- DS-VC-APD-004 (Content must be curated and human-authored)
- DS-VC-CON-007 (No Formulaic Descriptions — link text must be unique and descriptive)

## Emitted Diagnostics

- DS-DC-W006 (FORMULAIC_DESCRIPTIONS — warning for templated link text)

## Related Anti-Patterns

- DS-AP-STRAT-001 (Automation Obsession — over-reliance on automated tools produces formulaic output)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
