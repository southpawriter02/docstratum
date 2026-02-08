# DS-VC-CON-007: No Formulaic Descriptions

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VC-CON-007 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Platinum ID** | L2-07 |
| **Dimension** | Content (50%) |
| **Level** | L2 — Content Quality |
| **Weight** | 3 / 50 content points |
| **Pass Type** | SOFT |
| **Measurability** | Heuristic |
| **Provenance** | v0.0.4c AP-CONT-007 (Formulaic Description); v0.0.2b: auto-generated files often produce identical patterns |

## Description

This criterion detects when link descriptions follow identical boilerplate patterns, a strong signal of auto-generated content. Human-curated documentation typically shows varied and contextual descriptions; auto-generated or template-driven documentation often produces repetitive patterns like "Documentation for {feature}" with only the feature name changing.

Formulaic descriptions are a symptom of the "Automation Obsession" anti-pattern (AP-STRAT-001), where documentation is generated without human review and curation. They reduce the utility of descriptions, since readers derive little additional context from repeated phrases.

This criterion uses heuristic string similarity analysis rather than exact pattern matching, making it capable of detecting near-identical descriptions even with minor variations.

## Pass Condition

Descriptions show sufficient variation across the file. When 5 or more distinct descriptions exist, pairwise string similarity should not exceed a threshold:

```python
descriptions = extract_all_link_descriptions(content)
if len(descriptions) >= 5:
    # Compute pairwise similarities using Levenshtein or Jaro-Winkler
    similarities = [
        similarity(a, b)
        for a, b in combinations(descriptions, 2)
    ]
    avg_similarity = mean(similarities)
    assert avg_similarity < 0.80  #
# Files with <5 descriptions pass vacuously (insufficient data for pattern detection)
```

The 80% similarity threshold and 5-description minimum should be refined against the 11 empirical specimens.

## Fail Condition

Average pairwise similarity exceeds 80% across 5 or more descriptions. This typically indicates auto-generated content where descriptions follow a rigid template (e.g., "Documentation for {feature}" repeated with different feature names).

- **W006** fires when formulaic patterns are detected, signaling that human curation is needed.
- Files with fewer than 5 descriptions are insufficient for pattern analysis and pass vacuously (a file with 3 links cannot be reliably assessed for formulaic patterns).

## Emitted Diagnostics

- **DS-DC-W006** (WARNING): Sections use identical description patterns. Fires when formulaic patterns are detected across descriptions.

## Related Anti-Patterns

- **DS-AP-CONT-007** (Formulaic Description): Auto-generated descriptions with identical patterns, typically created by documentation generators (e.g., Mintlify) without human review.

## Related Criteria

- **DS-VC-CON-001** (Non-empty Descriptions): Descriptions must exist before they can be checked for variety. CON-001 enforces existence; CON-007 enforces substantive variation.
- **DS-VC-APD-005** (No Strategic Anti-Patterns): Automation Obsession (AP-STRAT-001) often correlates with formulaic descriptions, as auto-generation tools lack the judgment to vary descriptions based on context.

## Calibration Notes

Formulaic descriptions are a strong signal of auto-generation without human curation. The v0.0.2b audit found this pattern predominantly in Mintlify-generated files, where the generator produces identical templates.

Calibration thresholds:
- **80% similarity threshold:** Provisional. A higher threshold (e.g., 85%) would be more lenient; a lower threshold (e.g., 75%) more strict.
- **5-description minimum:** Ensures sufficient sample size for statistical meaning. Files with 3–4 descriptions are ambiguous.

Once Phase C scores all 11 empirical specimens, refine these thresholds to better distinguish human-curated from auto-generated documentation.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase C |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
