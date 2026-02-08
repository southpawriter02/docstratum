# DS-EH-FRESH: Freshness

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-EH-FRESH |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Dimension** | Freshness |
| **Enum Value** | `EcosystemHealthDimension.FRESHNESS` |
| **Source Code** | `ecosystem.py` → `EcosystemHealthDimension.FRESHNESS = "freshness"` |
| **Provenance** | v0.0.7 §4.3 (EcosystemScore — Aggregate Health) |

## Description

Freshness measures whether all files in the ecosystem are synchronized to the same version. A fresh ecosystem has zero version drift — the index references v2.0, all content pages describe v2.0, and all examples use v2.0 APIs.

When version drift occurs (the index references v2.0 but content pages describe v1.x), LLMs cannot provide coherent guidance. The model may combine information from different versions, advising users on APIs that don't exist in their installed version, or recommending deprecated patterns. This creates user confusion and support burden.

Freshness also considers file recency: all ecosystem files should be updated in the same release cycle. Files updated months ago alongside files updated yesterday signal version misalignment or partial updates.

## Measurement

Freshness is calculated through version consistency and temporal synchronization:

```
freshness_score = (1 - normalized_version_drift) × temporal_recency_factor × dimension_weight
```

Where:
- `normalized_version_drift` = Maximum version difference between any two files, normalized (0 = no drift, 1 = major version divergence)
- `temporal_recency_factor` = Adjustment based on last-modified timestamps (1 = all updated recently, <1 = staggered updates)
- `dimension_weight` = Weighting factor applied to this dimension [CALIBRATION-NEEDED]

**Perfect freshness:** `max_version_drift = 0` (all files reference the same version)

Measurement components:
1. **Version String Analysis:** Extract version metadata from all files; compare major.minor.patch versions
2. **Timestamp Analysis:** Examine last-modified dates; files updated within the same release cycle score higher
3. **Drift Penalty:** Penalize multi-version gaps (v1.x vs. v2.x is worse than v2.0 vs. v2.1)

A score of 1.0 indicates perfect synchronization — all files at the same version, updated simultaneously. A score of 0.5 indicates moderate drift (some version inconsistency, delayed updates).

## Why Freshness Matters for LLMs

- **Version-Specific Guidance:** Users ask "How do I do X in my version?" LLMs must know the user's version and provide version-appropriate guidance. Version drift forces the model to guess or hedge ("This might work in older versions...").
- **API Accuracy:** APIs change between versions. If the index describes v2.0 but the API Reference documents v1.8, LLMs will give incorrect API signatures and deprecated patterns.
- **User Frustration:** A user following "v2.0 Getting Started" documentation lands in a codebase using v1.x patterns. Code examples don't match, APIs are different, or missing. This erodes user trust in the ecosystem.
- **Stale Content Signal:** Files updated months ago signal that the ecosystem is not actively maintained. LLMs should de-weight or flag content from stale files to avoid propagating outdated patterns.

## Related Anti-Patterns

- **DS-AP-CONT-005** (Outdated Oracle): Deprecated references and stale patterns within individual files create version inconsistency at file level
- **DS-AP-CONT-009** (Versionless Drift): Files lack explicit version metadata, making version drift undetectable

## Related Diagnostic Codes

- **DS-DC-W016** (INCONSISTENT_VERSIONING): Version references diverge across files
- **DS-DC-W007** (MISSING_VERSION_METADATA): Files lack version information, preventing freshness measurement

## Implementation Reference

Freshness calculation in `ecosystem.py`:
- Iterate over all `EcosystemFile` objects
- Extract version metadata from each file (via front matter, metadata fields, or content parsing)
- Identify all unique versions present
- Calculate maximum version distance between any two files
- Normalize version distance (semver parsing)
- Extract last-modified timestamps
- Calculate temporal synchronization (files updated within X days score higher)
- Combine drift + recency into freshness score
- Generate diagnostics:
  - W016 if versions diverge beyond minor-version tolerance
  - W007 if version metadata is missing or unparseable

Example freshness scenarios:
```
Scenario A (Fresh):
- index.md: v2.1.0
- api-reference.md: v2.1.0
- examples.md: v2.1.0
- Last updated: 2026-02-05, 2026-02-04, 2026-02-06
Result: Freshness = 1.0 (perfect sync)

Scenario B (Stale):
- index.md: v2.1.0
- api-reference.md: v2.0.5
- examples.md: v1.9.0
- Last updated: 2026-02-01, 2025-11-10, 2025-08-20
Result: Freshness = 0.3 (severe drift, old files)

Scenario C (Acceptable):
- index.md: v2.1.0
- api-reference.md: v2.1.0
- examples.md: v2.0.9
- Last updated: 2026-02-05, 2026-02-04, 2026-01-30
Result: Freshness = 0.75 (minor drift, recent updates)
```


## Naming Reconciliation (D-DEC-03)

> **§7.7 Decision D-DEC-03:** The v0.0.7 research document and the `ecosystem.py` source code use different naming for the five ecosystem health dimensions. Per D-DEC-03, the code naming is authoritative (it was implemented after v0.0.7 and may have evolved the naming for good reasons), but both names are documented for traceability.

| v0.0.7 Name | Code Name | Resolution |
|-------------|-----------|------------|
| Consistency | `EcosystemHealthDimension.FRESHNESS` | Renamed |

**Full v0.0.7 ↔ Code mapping:**

| v0.0.7 | Code | Change |
|--------|------|--------|
| Coverage | COVERAGE | Unchanged |
| Coherence | CONSISTENCY | Renamed (clarity) |
| Completeness | COMPLETENESS | Unchanged |
| Consistency | FRESHNESS | Renamed (disambiguation) |
| Capability | TOKEN_EFFICIENCY | Renamed (measurability) |

**This dimension:** Renamed from v0.0.7 'Consistency' to 'Freshness'. In v0.0.7, 'Consistency' referred to temporal alignment — whether all files are in sync version-wise. However, this name conflicted with what is now the CONSISTENCY dimension (file-to-file agreement on names and terms, originally v0.0.7 'Coherence'). During implementation, the temporal dimension was renamed to 'Freshness' to resolve the naming collision and better communicate the concept: 'Are all files fresh and up-to-date?' maps directly to the W016 (INCONSISTENT_VERSIONING) diagnostic.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.6 |
