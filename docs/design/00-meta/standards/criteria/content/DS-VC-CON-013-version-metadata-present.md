# DS-VC-CON-013: Version Metadata Present

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-013 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L3-07 |
| **Dimension** | Content (50%) |
| **Level** | L3 — Best Practices |
| **Weight** | 3 / 50 content points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Measurable (pattern matching) |
| **Provenance** | v0.0.1b Gap #2 (metadata); v0.0.4c AP-CONT-009 (Versionless Drift); practical principle: agents need to know if content is current and aligned with a specific product version |

## Description

This criterion verifies that the llms.txt file contains version information or a date stamp indicating when the content was last updated or what version of the product it documents. Version metadata is crucial for understanding the currency and applicability of the content. Without it, readers cannot assess whether the documentation reflects the current state of the product or is potentially stale.

The llms.txt specification itself contains no requirement for versioning, yet it is one of the most critical metadata gaps identified in v0.0.1b. Version information can appear in multiple forms: explicit version strings (e.g., "v1.2.3"), version labels (e.g., "version: 2.0"), ISO date stamps (e.g., "2026-02-08"), natural language references (e.g., "Last updated: February 2026"), or links to changelog resources.

v0.0.4c analysis of the anti-pattern AP-CONT-009 (Versionless Drift) found that files without version metadata are indistinguishable from outdated content, leading to confusion and misuse by both human readers and LLM agents.

## Pass Condition

The file contains at least one recognizable version indicator:

```python
VERSION_PATTERNS = [
    r'v\d+\.\d+',                          # v1.2, v2.0.1, etc.
    r'version\s*[:=]\s*\S+',               # version: 1.0, version=2.3
    r'\d{4}-\d{2}-\d{2}',                  # ISO date: YYYY-MM-DD
    r'last.?updated',                      # "Last updated: ..." (case-insensitive)
    r'changelog',                           # Reference to changelog
]

has_version = any(
    re.search(pattern, content, re.IGNORECASE)
    for pattern in VERSION_PATTERNS
)

assert has_version
```

The criterion is deliberately permissive: any of the patterns suffices. Files with version strings, date stamps, or changelog references all pass. The goal is to ensure that some temporal or versioning context exists.

## Fail Condition

No version string, date stamp, changelog reference, or last-updated indicator is found anywhere in the file. Failing scenarios include:

- File contains no references to versions, dates, or update timing
- File has only release notes or changelog links but no version identifier for the documented product itself
- Metadata about the documentation itself (e.g., "This llms.txt was created by...") but no product version or date

W007 fires once per file when no version metadata is detected.

## Emitted Diagnostics

- **DS-DC-W007** (WARNING): No version or last-updated metadata found; readers cannot assess content currency

## Related Anti-Patterns

- **DS-AP-CONT-009** (Versionless Drift): Documentation contains no version or date metadata, making it impossible to assess whether content is current or stale, leading to potential misapplication of outdated APIs or features.

## Related Criteria

- **DS-VC-APD-001** (LLM Instructions Section): LLM instructions sections often include version and date context to help agents understand the scope and temporal boundaries of the documented system.
- **DS-VC-CON-008** (Canonical Section Names): Version information may appear in dedicated sections or in metadata areas of the file.

## Calibration Notes

v0.0.1b identified version metadata as Gap #2 in the llms.txt specification. The spec is silent on versioning, yet v0.0.4c analysis shows that agents urgently need to know whether content is current. v0.0.2d audit found that approximately 40% of audited files lack any version indicator, correlating strongly with lower quality scores and reported user confusion about staleness.

Top-scoring specimens include version context:
- **Svelte**: Includes version references and date stamps
- **Pydantic**: Contains version identifiers and changelog references

The criterion's pattern-based approach is intentionally flexible to accommodate natural variations: "v1.2", "version 2.0", "Last updated 2026-02-08", or even a link to a changelog all satisfy the requirement.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
