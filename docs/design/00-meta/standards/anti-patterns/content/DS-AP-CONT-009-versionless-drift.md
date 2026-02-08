# DS-AP-CONT-009: Versionless Drift

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CONT-009 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-CONT-009 |
| **Category** | Content |
| **Check ID** | CHECK-021 |
| **Severity Impact** | Reduce content dimension score |
| **Provenance** | v0.0.4c; v0.0.1b Gap #2 |

## Description

Documentation lacks version or date metadata, making it impossible for readers or LLM agents to assess content freshness or applicability. Without temporal anchors, agents cannot determine whether content is current, deprecated, or applies to a specific product version. This anti-pattern is especially damaging in rapidly evolving projects where a guide written for v2.0 may be completely incorrect for v4.0.

## Detection Logic

```python
def detect_versionless_drift(content):
    """
    Identify files lacking version or date metadata.
    
    Algorithm:
    1. Search first 500 characters and blockquotes for version patterns:
       - Semantic versioning: v\d+\.\d+\.\d+
       - Major.minor: v\d+\.\d+
       - ISO dates: \d{4}-\d{2}-\d{2}
       - "version:" or "Version:" keyword
       - "last updated:" or "Last Updated:" keyword
       - "as of" patterns
    2. If no pattern found in early content or blockquote, trigger
    3. Acceptable patterns:
       - Blockquote: "> Version 2.1 | Last updated 2025-01-15"
       - Frontmatter: "version: 0.4.2"
       - First section: "As of v2.0, ..."
    
    Returns: (triggered, patterns_found, first_500_chars)
    """
    import re
    
    version_patterns = [
        r'\bv\d+\.\d+\.\d+\b',           # Semantic version
        r'\bv\d+\.\d+\b',                # Major.minor
        r'\b\d{4}-\d{2}-\d{2}\b',        # ISO date
        r'\b(version|Version):\s*[\d.]+', # version: keyword
        r'(?i)last\s+updated:',          # last updated keyword
        r'(?i)as\s+of\s+',               # as of pattern
    ]
    
    first_500 = content[:500]
    blockquote_section = '\n'.join([line for line in content.split('\n') if line.startswith('>')])[:500]
    search_text = first_500 + blockquote_section
    
    patterns_found = []
    for pattern in version_patterns:
        if re.search(pattern, search_text):
            match = re.search(pattern, search_text)
            patterns_found.append(match.group(0))
    
    triggered = len(patterns_found) == 0 and len(content.strip()) > 100
    return triggered, patterns_found, first_500
```

## Example (Synthetic)

```markdown
# Configuration Reference

## Environment Variables

The system reads configuration from the following environment variables:

- `DATABASE_URL`: Connection string for the primary database
- `CACHE_TTL`: Time-to-live in seconds (default: 3600)
- `API_KEY`: Authentication token for external services
```

No metadata indicating when this was written, what version it applies to, or when it was last updated. An agent reading this in 2026 cannot determine if these variables still apply or have been renamed/removed.

## Remediation

1. Add version and date metadata in documentation header or blockquote:
   ```markdown
   > **Version:** 2.1.0 | **Last Updated:** 2025-06-15 | **Applies to:** v2.0+
   ```

2. Include version information in frontmatter (if using static site generators):
   ```yaml
   ---
   version: 2.1.0
   last_updated: 2025-06-15
   applies_to: v2.0+
   ---
   ```

3. State version applicability early in technical docs:
   ```markdown
   # Configuration Reference (v2.0+)
   
   This guide applies to versions 2.0 and later. For v1.x, see [Legacy Configuration](...)
   ```

4. Establish a documentation update cadence and refresh version numbers with each product release
5. Implement CI checks to ensure all technical docs contain version metadata
6. Consider adding "last verified" dates for examples and code snippets

## Affected Criteria

- DS-VC-APD-004 (Content must include temporal context)
- DS-VC-CON-013 (Version Metadata Present — version information must be explicitly stated)

## Emitted Diagnostics

- DS-DC-W007 (MISSING_VERSION_METADATA — warning for undated or unversioned content)

## Related Anti-Patterns

- DS-AP-CONT-005 (Outdated Oracle — stale content becomes undetectable without version markers)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
