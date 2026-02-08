# DS-AP-CONT-005: Outdated Oracle

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-AP-CONT-005 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Registry ID** | AP-CONT-005 |
| **Category** | Content |
| **Check ID** | CHECK-014 |
| **Severity Impact** | Reduce content dimension score |
| **Provenance** | v0.0.4c §Anti-Patterns Catalog |

## Description

Documentation content references deprecated, removed, or sunset features; links to APIs no longer maintained; cites obsolete version numbers. This anti-pattern misleads both human users and LLM agents into attempting to use functionality that no longer exists. The damage is compounded when agents provide stale guidance based on outdated documentation.

## Detection Logic

```python
def detect_outdated_oracle(content, file_version=None):
    """
    Identify content referencing deprecated or outdated information.
    
    Algorithm:
    1. Search for deprecation keywords: "deprecated", "removed", "sunset", "legacy", "obsolete"
    2. Extract version numbers from content (semver pattern: v\d+\.\d+)
    3. Extract file version from metadata/frontmatter
    4. For each version reference in content:
       a. Compare to file version
       b. If content_version << file_version (2+ major versions back), flag as stale
    5. Check links for 404 indicators or sunset notices in URL
    6. Trigger if deprecation keyword appears near link OR version mismatch detected
    
    Returns: (triggered, deprecation_instances, stale_versions)
    """
    import re
    
    deprecation_keywords = r'\b(deprecated|removed|sunset|legacy|obsolete|discontinued)\b'
    version_pattern = r'v?(\d+)\.(\d+)'
    
    deprecation_matches = re.findall(deprecation_keywords, content, re.IGNORECASE)
    version_matches = re.findall(version_pattern, content)
    
    stale_versions = []
    if file_version:
        file_major, file_minor = map(int, file_version.split('.')[:2])
        for content_major, content_minor in version_matches:
            content_major, content_minor = int(content_major), int(content_minor)
            if file_major - content_major >= 2:
                stale_versions.append(f"v{content_major}.{content_minor}")
    
    triggered = len(deprecation_matches) > 0 or len(stale_versions) > 0
    return triggered, deprecation_matches, stale_versions
```

## Example (Synthetic)

```markdown
## Legacy Authentication (Deprecated)

The old OAuth 1.0 authentication method is now deprecated. Use OAuth 2.0 instead.

Refer to the [v1.2 API docs](https://api.example.com/v1.2/auth) for legacy implementations.

The `Config::Deprecated::LegacyMode` flag was removed in v4.0.
```

Multiple red flags: explicit "Deprecated" and "removed" keywords, reference to v1.2 API in a v4.0 codebase, and a sunset feature flag. Agents reading this might accidentally follow deprecated patterns.

## Remediation

1. Identify and flag all content referencing deprecated features
2. Create a separate "Legacy" or "Deprecated" section if backward compatibility guidance is necessary
3. Prominently warn that content references EOL features
4. Update links to point to current versions of APIs/features
5. Remove content about features that are fully sunset unless historical context is essential
6. Implement CI checks to detect deprecation keywords and flag content for manual review
7. Establish a documentation refresh cadence aligned with release cycles

## Affected Criteria

- DS-VC-APD-004 (Content must reflect current product state)

## Emitted Diagnostics

None specific; reported via manual review process.

## Related Anti-Patterns

- DS-AP-CONT-009 (Versionless Drift — absence of version metadata makes staleness undetectable)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.2 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
