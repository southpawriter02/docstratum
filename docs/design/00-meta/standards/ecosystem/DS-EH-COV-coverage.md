# DS-EH-COV: Coverage

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-EH-COV |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Dimension** | Coverage |
| **Enum Value** | `EcosystemHealthDimension.COVERAGE` |
| **Source Code** | `ecosystem.py` → `EcosystemHealthDimension.COVERAGE = "coverage"` |
| **Provenance** | v0.0.7 §4.3 (EcosystemScore — Aggregate Health) |

## Description

Coverage measures whether the ecosystem addresses all necessary documentation areas by tracking representation across the 11 canonical section categories (from `CanonicalSectionName`). A high coverage score indicates that the documentation ecosystem comprehensively covers all standard topics: Getting Started, API Reference, Examples, Core Concepts, Troubleshooting, and others.

This dimension is critical for LLM consumption because incomplete coverage creates knowledge gaps. When an LLM encounters a project with poor coverage (e.g., a complete API Reference but no Examples or Getting Started section), it cannot provide complete guidance to users and must resort to speculation or hallucination. The presence of all canonical topic areas ensures that LLMs can deliver comprehensive, well-grounded assistance across the full user journey.

**Coverage requirement:** At least one file in the ecosystem must address each canonical section category. This does NOT require every section in every file — only that the topic is covered somewhere in the ecosystem.

## Measurement

Coverage is calculated as the proportion of canonical section categories represented across all ecosystem files:

```
coverage_score = (covered_categories / 11 canonical categories) × dimension_weight
```

Where:
- `covered_categories` = Count of unique `CanonicalSectionName` values found across all files in the ecosystem
- `11 canonical categories` = The complete set of canonical section names (Getting Started, API Reference, Examples, Core Concepts, Troubleshooting, FAQ, Architecture, Installation, Best Practices, Changelog, Contributing)
- `dimension_weight` = Weighting factor applied to this dimension

A coverage score of 1.0 indicates all 11 canonical categories are represented. A score of 0.73 means 8 out of 11 categories are present.

## Why Coverage Matters for LLMs

- **Knowledge Completeness:** LLMs perform best when they have access to multiple perspectives on a topic. Coverage ensures the model can access Getting Started (user onboarding), API Reference (technical details), and Examples (practical application).
- **User Journey Support:** Different users approach documentation differently. Some need Examples first, others prefer API Reference. Full coverage ensures the LLM can route users to their preferred learning style.
- **Reduced Hallucination:** When critical sections are missing, LLMs fill gaps with inferred information, increasing error rates. Complete coverage reduces this risk.
- **Ecosystem Maturity Signal:** High coverage correlates with project maturity and documentation quality. Projects with all 11 canonical topics typically have more thoughtful, organized documentation.

## Related Anti-Patterns

- **DS-AP-ECO-001** (Index Island): Index links to nothing, reducing effective coverage of the ecosystem
- **DS-AP-ECO-006** (Orphan Nursery): Content exists in files but isn't linked or indexed, creating false low coverage measurements

## Related Diagnostic Codes

- **DS-DC-I009** (CONTENT_COVERAGE_GAP): Fires when coverage falls below thresholds (e.g., <7/11 categories)

## Implementation Reference

Coverage calculation maps to ecosystem analysis in `ecosystem.py`:
- Iterate over all `EcosystemFile` objects
- Extract `canonical_sections` from each file's metadata
- Collect unique `CanonicalSectionName` enum values
- Divide by 11 to obtain proportion
- Apply dimension weighting


## Naming Reconciliation (D-DEC-03)

> **§7.7 Decision D-DEC-03:** The v0.0.7 research document and the `ecosystem.py` source code use different naming for the five ecosystem health dimensions. Per D-DEC-03, the code naming is authoritative (it was implemented after v0.0.7 and may have evolved the naming for good reasons), but both names are documented for traceability.

| v0.0.7 Name | Code Name | Resolution |
|-------------|-----------|------------|
| Coverage | `EcosystemHealthDimension.COVERAGE` | Unchanged |

**Full v0.0.7 ↔ Code mapping:**

| v0.0.7 | Code | Change |
|--------|------|--------|
| Coverage | COVERAGE | Unchanged |
| Coherence | CONSISTENCY | Renamed (clarity) |
| Completeness | COMPLETENESS | Unchanged |
| Consistency | FRESHNESS | Renamed (disambiguation) |
| Capability | TOKEN_EFFICIENCY | Renamed (measurability) |

**This dimension:** Unchanged from v0.0.7. Both the research document and the code use 'Coverage' to describe the proportion of canonical section categories represented across the ecosystem.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.6 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
