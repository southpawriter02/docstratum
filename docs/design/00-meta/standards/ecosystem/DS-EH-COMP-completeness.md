# DS-EH-COMP: Completeness

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-EH-COMP |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Dimension** | Completeness |
| **Enum Value** | `EcosystemHealthDimension.COMPLETENESS` |
| **Source Code** | `ecosystem.py` → `EcosystemHealthDimension.COMPLETENESS = "completeness"` |
| **Provenance** | v0.0.7 §4.3 (EcosystemScore — Aggregate Health); uses `EcosystemScore.resolution_rate` |

## Description

Completeness measures whether every promise (hyperlink and cross-reference) in the ecosystem's index actually leads to accessible, healthy, parseable content. This dimension answers the question: "Does every link work, and does the referenced content exist?"

A complete ecosystem has a resolution rate of 100% — every link in llms.txt or index files resolves to a file that exists, is parseable, and is healthy according to validation criteria. When links are broken (resolution rate <100%), the ecosystem feels fragmented to LLMs. The model must either refuse to follow broken links or admit that referenced content is unavailable, diminishing the ecosystem's perceived comprehensiveness.

This dimension is NOT about having every possible piece of content — it's about honoring every explicit commitment made in the index. If a file is indexed, it must exist and be accessible.

## Measurement

Completeness is calculated as the link resolution rate:

```
completeness_score = (resolved_relationships / total_relationships) × dimension_weight
```

Where:
- `resolved_relationships` = Count of cross-file relationships (links, includes, references) that successfully resolve to accessible content
- `total_relationships` = Total number of cross-file relationships declared in the ecosystem index (llms.txt, navmaps, etc.)
- `dimension_weight` = Weighting factor applied to this dimension [CALIBRATION-NEEDED]

This value maps directly to the `EcosystemScore.resolution_rate` property (a value between 0.0 and 1.0).

A completeness score of 1.0 indicates zero broken links. A score of 0.85 means 15% of referenced relationships are broken.

## Why Completeness Matters for LLMs

- **Trust in References:** LLMs are trained to follow references and cite sources. When cited sources don't exist or can't be accessed, the model's credibility deteriorates.
- **Navigation Coherence:** LLMs guide users through ecosystems via links and cross-references. Broken links create dead ends, forcing the model to either backtrack or admit information is unavailable.
- **Reduced Hallucination Risk:** When LLMs encounter a broken link in the index, they cannot verify what the referenced content actually says. To provide helpful guidance, they may invent or infer content, increasing hallucination risk.
- **User Experience:** From a user perspective, a broken link means "the ecosystem promised this content but doesn't deliver." Completeness ensures every ecosystem promise is kept.

## Related Anti-Patterns

- **DS-AP-ECO-002** (Phantom Links): More than 30% of links are broken, creating widespread dead ends
- **DS-AP-CRIT-004** (Link Void): More than 80% of links are broken; critical severity indicating a severely degraded ecosystem

## Related Diagnostic Codes

- **DS-DC-W012** (BROKEN_CROSS_FILE_LINK): Individual broken link detected
- **DS-DC-E006** (BROKEN_LINKS): Aggregate report of broken links exceeding thresholds

## Implementation Reference

Completeness calculation in `ecosystem.py`:
- Parse the ecosystem index (llms.txt, navmaps, or equivalent)
- Extract all declared relationships (file includes, section links, references)
- For each relationship, attempt to resolve the target file
- Check that target file exists, is parseable, and passes health validation
- Count successful vs. failed resolutions
- Divide by total relationships to obtain resolution_rate
- Apply dimension weighting


## Naming Reconciliation (D-DEC-03)

> **§7.7 Decision D-DEC-03:** The v0.0.7 research document and the `ecosystem.py` source code use different naming for the five ecosystem health dimensions. Per D-DEC-03, the code naming is authoritative (it was implemented after v0.0.7 and may have evolved the naming for good reasons), but both names are documented for traceability.

| v0.0.7 Name | Code Name | Resolution |
|-------------|-----------|------------|
| Completeness | `EcosystemHealthDimension.COMPLETENESS` | Unchanged |

**Full v0.0.7 ↔ Code mapping:**

| v0.0.7 | Code | Change |
|--------|------|--------|
| Coverage | COVERAGE | Unchanged |
| Coherence | CONSISTENCY | Renamed (clarity) |
| Completeness | COMPLETENESS | Unchanged |
| Consistency | FRESHNESS | Renamed (disambiguation) |
| Capability | TOKEN_EFFICIENCY | Renamed (measurability) |

**This dimension:** Unchanged from v0.0.7. Both the research document and the code use 'Completeness' to measure whether every link in the index resolves to accessible, healthy content.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.6 |
