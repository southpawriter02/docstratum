# DS-DD-014: Content Quality as Primary Scoring Weight

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-DD-014 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Decision ID** | DECISION-014 |
| **Date Decided** | 2026-02-06 (v0.0.4d) |
| **Impact Area** | Quality Scoring (DS-QS-DIM-*) |
| **Provenance** | v0.0.4b §Content Best Practices; v0.0.2c pattern analysis (code examples r ≈ 0.65) |

## Decision

**The Content dimension receives 50% (50 points) of the composite quality score, making it the primary scoring weight. Structural receives 30% (30 points) and Anti-Pattern Detection receives 20% (20 points).**

## Context

During the v0.0.4b best practices synthesis, the research team needed to determine how to weight the three quality dimensions against each other. The core question was: "What matters most for an llms.txt file's utility to an LLM agent?"

## Alternatives Considered

| Option | Weighting | Rationale For | Rationale Against |
|--------|-----------|---------------|-------------------|
| **Equal weighting** | 33/33/33 | Simple; no bias | Ignores empirical evidence that dimensions contribute unequally to quality |
| **Structure-first** | 50/30/20 | Structure is the gating factor | Structure is necessary but not sufficient — a perfectly structured empty file scores high |
| **Content-first** (CHOSEN) | 30/50/20 | Empirical evidence: code examples (r ≈ 0.65), descriptions, and section names are the strongest quality predictors | Requires robust content analysis heuristics |
| **Anti-pattern-first** | 20/30/50 | Absence of bad patterns is highly correlated with quality | Negative scoring alone doesn't reward excellence |

## Rationale

The content-first weighting was chosen based on three converging lines of evidence:

1. **Correlation analysis (v0.0.2c):** The presence of code examples has the strongest correlation with overall file quality (r ≈ 0.65). Code examples are a content feature, not a structural one.
2. **Gold standard calibration (v0.0.4b):** Svelte (92) and Pydantic (90) score highest specifically because of rich content — comprehensive descriptions, well-annotated code blocks, and meaningful section organization. Their structural compliance is necessary but not what distinguishes them from lower-scoring files.
3. **Consumer perspective (DECISION-015):** The target consumer is an AI coding assistant via MCP. These agents benefit most from content richness (code examples they can learn from, descriptions they can reason about) rather than from structural compliance alone.

## Impact on ASoT

This decision directly determines:

- **DS-QS-DIM-STR** (Structural Dimension): Weight = 30 points / 100
- **DS-QS-DIM-CON** (Content Dimension): Weight = 50 points / 100
- **DS-QS-DIM-APD** (Anti-Pattern Dimension): Weight = 20 points / 100
- **Integrity assertions IA-011, IA-012, IA-013:** These verify the weight sums at pipeline startup

## Constraints Imposed

1. Any change to dimension weights requires an ASoT **MAJOR** version bump (it changes scoring outcomes for all files).
2. The sum of all three dimension weights MUST equal exactly 100.
3. Individual criterion weights within a dimension must sum to the dimension total.

## Related Decisions

- **DS-DD-013** (Token Budget Tiers): Token budgets interact with content scoring — files that exceed their tier budget are penalized in the content dimension.
- **DS-DD-015** (MCP as Target Consumer): The consumer target influenced the content-first weighting rationale.
- **DS-DD-016** (Four-Category Anti-Patterns): Anti-pattern severity categories determine deduction magnitudes within the 20-point anti-pattern dimension.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase A example file |
