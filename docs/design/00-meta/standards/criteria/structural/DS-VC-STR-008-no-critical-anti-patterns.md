# DS-VC-STR-008: No Critical Anti-Patterns

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-008 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L3-09 |
| **Dimension** | Structural (30%) |
| **Level** | L3 — Best Practices |
| **Weight** | 3 / 30 structural points [CALIBRATION-NEEDED] |
| **Pass Type** | HARD |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4c anti-pattern catalog with severity classification; DECISION-016 (anti-pattern categories) |

## Description

This criterion is a composite gate that prevents files exhibiting any of the four critical anti-patterns from advancing beyond L2 (Even Better). Critical anti-patterns represent severe structural or content degradations that render the document unsuitable for reliable AI consumption. The four critical anti-patterns are:

1. **DS-AP-CRIT-001** (Ghost File): File appears valid structurally but is completely empty of substantive content (e.g., all headings, no text; all links, no descriptions).
2. **DS-AP-CRIT-002** (Structure Chaos): Complete absence of recognizable structure (no headings, no sections, random text organization).
3. **DS-AP-CRIT-003** (Encoding Disaster): File contains severe encoding errors, corruption, or un-decodable byte sequences that prevent reliable parsing.
4. **DS-AP-CRIT-004** (Link Void): All or nearly all links are broken, malformed, or unresolvable (>90% link failure rate).

When any critical anti-pattern is detected, the file is barred from achieving ADEQUATE grade or above. Per DECISION-016, critical anti-patterns cap the total quality score at 29 (on a 100-point scale). This ensures that documents with catastrophic structural or content failures are clearly flagged for human review before being served to AI agents.

This is a HARD criterion at L3. Detection of even one critical anti-pattern results in failure. Unlike SOFT criteria, HARD failure prevents grade progression.

## Pass Condition

None of the 4 critical anti-patterns are detected:

```python
critical_patterns = [
    DS_AP_CRIT_001,  # Ghost File
    DS_AP_CRIT_002,  # Structure Chaos
    DS_AP_CRIT_003,  # Encoding Disaster
    DS_AP_CRIT_004,  # Link Void
]

for pattern in critical_patterns:
    assert not pattern.detected(file_content), f"{pattern.name} detected — fails STR-008"
```

Each individual anti-pattern has its own detection logic, defined in the anti-pattern registry. This criterion aggregates those detections into a single composite gate.

## Fail Condition

Any one or more of the four critical anti-patterns is detected:

- Ghost File detected: File has structure (H1, H2 sections) but all sections are empty; <10% of file is non-whitespace, non-heading text
- Structure Chaos detected: File lacks any recognizable heading hierarchy; <5% of content is organized into sections
- Encoding Disaster detected: File contains un-decodable byte sequences or severe character corruption (≥1% invalid UTF-8 sequences)
- Link Void detected: >90% of links in the file are broken, malformed, or unresolvable

HARD failure — prevents ADEQUATE classification and caps total score at 29 points.

## Emitted Diagnostics

- **No standalone diagnostic code:** Individual anti-pattern detections emit their own diagnostics (e.g., DS-DC-CRIT-001, DS-DC-CRIT-002, etc.). This criterion acts as a structural gate based on the detection results of those patterns.

## Related Anti-Patterns

- **DS-AP-CRIT-001** (Ghost File): Detected via heuristic: `content_ratio = non_whitespace_text / total_content < 0.10`
- **DS-AP-CRIT-002** (Structure Chaos): Detected via heading density: `heading_ratio = heading_count / content_lines < 0.05`
- **DS-AP-CRIT-003** (Encoding Disaster): Detected via byte-level analysis: `invalid_utf8_ratio > 0.01`
- **DS-AP-CRIT-004** (Link Void): Detected via link resolution: `broken_link_ratio > 0.90`

## Related Criteria

- **DS-VC-STR-009** (No Structural Anti-Patterns): The structural-severity counterpart; STR-009 gates on 5 structural anti-patterns (less severe than critical).
- **DS-VC-APD-004** (No Content Anti-Patterns): The content-severity counterpart; gates on 4 content anti-patterns.
- **DS-VC-STR-001** through **DS-VC-STR-007**: Foundational structural criteria; STR-008 is a quality gate above the base structural level.

## Calibration Notes

- **NVIDIA llms.txt (score 24):** Triggers AP-CRIT-002 (Structure Chaos) and AP-CRIT-004 (Link Void); score capped at 29 by DECISION-016
- **Example: auto-generated stub file (score 15):** Triggers AP-CRIT-001 (Ghost File); empty sections with no content
- **Top-scoring specimens (Svelte 92, Pydantic 90):** Free of all critical anti-patterns
- **Critical anti-patterns are binary gates:** Detection of even one anti-pattern results in immediate HARD failure of this criterion

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
