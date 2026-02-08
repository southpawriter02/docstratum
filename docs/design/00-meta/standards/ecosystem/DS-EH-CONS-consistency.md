# DS-EH-CONS: Consistency

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-EH-CONS |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Dimension** | Consistency |
| **Enum Value** | `EcosystemHealthDimension.CONSISTENCY` |
| **Source Code** | `ecosystem.py` → `EcosystemHealthDimension.CONSISTENCY = "consistency"` |
| **Provenance** | v0.0.7 §4.3 (EcosystemScore — Aggregate Health) |

## Description

Consistency measures whether all files in the ecosystem agree with each other on fundamental metadata: project name, version references, and terminology. An inconsistent ecosystem creates confusion for both humans and AI systems.

When different files present conflicting information (e.g., one file states "Project v2.0" while another says "v1.8"), LLMs become uncertain about which source to trust. This uncertainty propagates through all downstream reasoning. Inconsistent terminology across files also fragments semantic understanding — if one file calls a feature "Authentication" while another calls it "Access Control," the LLM must spend reasoning capacity disambiguating rather than helping users.

Consistency is detected through automated checks that identify W015 (INCONSISTENT_PROJECT_NAME) and W016 (INCONSISTENT_VERSIONING) violations across all ecosystem files.

## Measurement

Consistency is calculated through pairwise agreement checks across all files:

```
consistency_score = (consistent_checks / total_checks) × dimension_weight
```

Where:
- `consistent_checks` = Number of pairwise file comparisons that pass (project names match, versions agree, terminology consistent)
- `total_checks` = Total number of pairwise comparisons performed
- `dimension_weight` = Weighting factor applied to this dimension [CALIBRATION-NEEDED]

Checks performed:
1. **Project Name Consistency:** All references to project name in all files match
2. **Version Consistency:** All version references across files refer to the same version
3. **Terminology Consistency:** Key terms used consistently across files (may require semantic analysis)

A score of 1.0 indicates perfect consistency across all files. Any mismatch lowers the score.

## Why Consistency Matters for LLMs

- **Trust and Authority:** LLMs rely on consistent information to establish confidence in answers. When sources conflict, model responses become hedged, uncertain, and unhelpful.
- **Reduced Conflicting Guidance:** Users reading an LLM response derived from inconsistent sources receive contradictory advice (e.g., "The project is v2.0... actually v1.8..."). This undermines user confidence.
- **Semantic Coherence:** LLMs reason best when terminology is stable. Inconsistent terminology forces the model to perform translation between naming schemes, increasing error rates.
- **Version Accuracy:** Version inconsistency is particularly critical. LLMs must confidently state which version of the project users are working with. Inconsistent versioning can lead to out-of-date advice or API mismatches.

## Related Anti-Patterns

- **DS-AP-ECO-003** (Shadow Aggregate): The aggregate file (llms.txt) doesn't match the content of individual files, creating master-to-detail inconsistency
- **DS-AP-ECO-004** (Duplicate Ecosystem): Multiple llms.txt files or conflicting ecosystem definitions create competing sources of truth

## Related Diagnostic Codes

- **DS-DC-W015** (INCONSISTENT_PROJECT_NAME): Project name differs across files
- **DS-DC-W016** (INCONSISTENT_VERSIONING): Version references diverge across files

## Implementation Reference

Consistency checking in `ecosystem.py`:
- Load all `EcosystemFile` objects
- Extract `project_name`, `version`, and `terminology_map` from each
- Perform pairwise comparisons between all files
- Count matches vs. mismatches
- Generate diagnostics for each mismatch (W015, W016)
- Aggregate into consistency proportion


## Naming Reconciliation (D-DEC-03)

> **§7.7 Decision D-DEC-03:** The v0.0.7 research document and the `ecosystem.py` source code use different naming for the five ecosystem health dimensions. Per D-DEC-03, the code naming is authoritative (it was implemented after v0.0.7 and may have evolved the naming for good reasons), but both names are documented for traceability.

| v0.0.7 Name | Code Name | Resolution |
|-------------|-----------|------------|
| Coherence | `EcosystemHealthDimension.CONSISTENCY` | Renamed |

**Full v0.0.7 ↔ Code mapping:**

| v0.0.7 | Code | Change |
|--------|------|--------|
| Coverage | COVERAGE | Unchanged |
| Coherence | CONSISTENCY | Renamed (clarity) |
| Completeness | COMPLETENESS | Unchanged |
| Consistency | FRESHNESS | Renamed (disambiguation) |
| Capability | TOKEN_EFFICIENCY | Renamed (measurability) |

**This dimension:** Renamed from v0.0.7 'Coherence' to 'Consistency'. The v0.0.7 research used 'Coherence' to describe agreement between files on project name, version, and terminology. During implementation, 'Consistency' was chosen because it directly maps to the diagnostic checks (W015 INCONSISTENT_PROJECT_NAME, W016 INCONSISTENT_VERSIONING) and is more intuitive for developers: 'Are files consistent with each other?' is clearer than 'Are files coherent with each other?'

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.6 |
