# DS-VC-STR-009: No Structural Anti-Patterns

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-STR-009 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Platinum ID** | L3-10 |
| **Dimension** | Structural (30%) |
| **Level** | L3 — Best Practices |
| **Weight** | 2 / 30 structural points [CALIBRATION-NEEDED] |
| **Pass Type** | SOFT |
| **Measurability** | Fully measurable |
| **Provenance** | v0.0.4c anti-pattern catalog; 5 structural anti-patterns with heuristic detection rules |

## Description

This criterion is a composite gate that aggregates detection of five structural anti-patterns, each representing a quality degradation within the structural dimension. Unlike the critical anti-patterns (DS-VC-STR-008), these structural anti-patterns are less severe and do not catastrophically impair document quality. However, their presence indicates organizational weaknesses that reduce the file's overall structural score.

The five structural anti-patterns are:

1. **DS-AP-STRUCT-001** (Sitemap Dump): File is primarily a list of links with minimal descriptive text (>80% of non-heading content is link syntax).
2. **DS-AP-STRUCT-002** (Orphaned Sections): Sections exist with no content or only empty subsection headings (section text ratio <5%).
3. **DS-AP-STRUCT-003** (Duplicate Identity): Multiple sections have identical or near-identical names (Levenshtein distance <2 for section names).
4. **DS-AP-STRUCT-004** (Section Shuffle): Canonical sections appear out of prescribed order.
5. **DS-AP-STRUCT-005** (Naming Nebula): Section names are vague, non-descriptive, or inconsistent in style (heuristic: <50% of sections use canonical names).

This is a SOFT criterion at L3. Detection of structural anti-patterns reduces the structural dimension score but does not prevent grade progression. Files with structural anti-patterns remain valid at L1 and L2, but miss L3 (Best Practices) and higher classifications.

## Pass Condition

None of the 5 structural anti-patterns are detected:

```python
structural_patterns = [
    DS_AP_STRUCT_001,  # Sitemap Dump
    DS_AP_STRUCT_002,  # Orphaned Sections
    DS_AP_STRUCT_003,  # Duplicate Identity
    DS_AP_STRUCT_004,  # Section Shuffle
    DS_AP_STRUCT_005,  # Naming Nebula
]

for pattern in structural_patterns:
    assert not pattern.detected(file_content), f"{pattern.name} detected — STR-009 reduced score"
```

Each anti-pattern has its own detection heuristic, defined in the anti-pattern registry. This criterion aggregates those detections into a composite gate.

## Fail Condition

Any one or more of the 5 structural anti-patterns is detected:

- **Sitemap Dump:** >80% of non-heading, non-blockquote content consists of Markdown link syntax
- **Orphaned Sections:** One or more sections have <5% substantive content text (e.g., section contains only an H3 subheading with no text below)
- **Duplicate Identity:** Two or more section names have a Levenshtein distance <2 (e.g., "Getting Started" and "Getting Starte" — likely typo or copy-paste error)
- **Section Shuffle:** Canonical sections appear out of prescribed order (same detection as DS-VC-STR-007; note: STR-007 is HARD at L3, STR-009 aggregates it as a SOFT component)
- **Naming Nebula:** <50% of section names appear in the canonical section list; many sections use generic names ("Details", "Info", "Settings" without project-specific context)

SOFT failure — reduces structural score but does not block L1, L2, or L3 classification.

## Emitted Diagnostics

- **No standalone diagnostic code:** Individual anti-pattern detections emit their own findings. This criterion aggregates the structural anti-pattern detection results for composite scoring purposes.

## Related Anti-Patterns

- **DS-AP-STRUCT-001** (Sitemap Dump): Detected via link density heuristic
- **DS-AP-STRUCT-002** (Orphaned Sections): Detected via content ratio per section
- **DS-AP-STRUCT-003** (Duplicate Identity): Detected via Levenshtein distance comparison of section names
- **DS-AP-STRUCT-004** (Section Shuffle): Detected via ordinal comparison against `CANONICAL_SECTION_ORDER`
- **DS-AP-STRUCT-005** (Naming Nebula): Detected via canonical name ratio and naming consistency heuristics

## Related Criteria

- **DS-VC-STR-008** (No Critical Anti-Patterns): The critical-severity counterpart; gates on 4 critical anti-patterns (more severe than structural).
- **DS-VC-CON-004** (Non-empty Sections): Overlaps with Orphaned Sections detection; checks that sections contain substantive content.
- **DS-VC-CON-005** (No Duplicate Sections): Overlaps with Duplicate Identity; checks for exact duplicates.
- **DS-VC-CON-008** (Canonical Section Names): Overlaps with Naming Nebula; checks that sections use canonical names.
- **DS-VC-STR-007** (Canonical Section Ordering): Overlaps with Section Shuffle; STR-007 is HARD, STR-009 includes it as SOFT.

## Calibration Notes

- **Structural anti-patterns are moderately common in auto-generated files (~40% of audited auto-generated files exhibit ≥1 structural anti-pattern)**
- **Sitemap Dump (AP-STRUCT-001):** Most frequently observed; ~20% of audited files meet the >80% link density threshold. Typically observed in API link aggregators or repository indexes.
- **Orphaned Sections (AP-STRUCT-002):** ~15% of audited files contain at least one empty section; often result from incomplete migration or stub documentation.
- **Duplicate Identity (AP-STRUCT-003):** Rare (~2%); typically typos or merge artifacts.
- **Section Shuffle (AP-STRUCT-004):** ~10% of audited files exhibit canonical ordering violations (also counted in DS-VC-STR-007).
- **Naming Nebula (AP-STRUCT-005):** ~25% of audited files have <50% canonical section names, especially in custom or domain-specific documentation.
- **Top-scoring specimens (Svelte 92, Pydantic 90):** Free of structural anti-patterns
- **Example: auto-generated Flask docs (score 35):** Triggers AP-STRUCT-001 (Sitemap Dump) — file is primarily an API index with minimal narrative
- SOFT pass means structural anti-pattern detection reduces the structural dimension score but does not prevent classification at any level

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
