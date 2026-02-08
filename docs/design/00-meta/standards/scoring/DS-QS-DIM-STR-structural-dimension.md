# DS-QS-DIM-STR: Structural Dimension

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-QS-DIM-STR |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Element Type** | Quality Dimension |
| **Source Code** | `quality.py` → `QualityDimension.STRUCTURAL` |
| **Provenance** | DECISION-014; v0.0.4b §Content Best Practices |

## Description

The Structural Dimension measures how well-formed the documentation file is as a Markdown document. It evaluates structural compliance including proper heading hierarchy, link formatting, blockquotes, canonical section structure, and foundational formatting standards. A file with strong structural scores is parseable, navigable, and follows DocStratum best practices in its layout and organization.

This dimension is assessed across two levels:
- **L1 (Structural Foundations):** Criteria STR-001 through STR-006 (22 points) — basic Markdown well-formedness and heading structure
- **L3 (Best Practices):** Criteria STR-007 through STR-009 (8 points) — advanced structural patterns and canonical compliance

The Structural Dimension contributes **30 points (30% of total weight)** to the composite quality score.

## Specification

### Weight and Scoring
- **Maximum Points:** 30
- **Weight Percentage:** 30%
- **Scoring Model:** Graduated (not binary pass/fail)
- **Dimension ID:** `QualityDimension.STRUCTURAL`

### Constituent Criteria

| Criterion | Points | Level | Pass | Description |
|-----------|--------|-------|------|-------------|
| DS-VC-STR-001 | 5 | L1 | HARD | H1 Title Present — document begins with exactly one H1 heading |
| DS-VC-STR-002 | 3 | L1 | HARD | Single H1 Only — no duplicate H1 headings anywhere in the document |
| DS-VC-STR-003 | 3 | L1 | SOFT | Blockquote Present — description blockquote appears after H1 |
| DS-VC-STR-004 | 4 | L1 | HARD | H2 Section Structure — content organized into H2-delimited sections |
| DS-VC-STR-005 | 4 | L1 | HARD | Link Format Compliance — all links use proper Markdown `[text](url)` syntax |
| DS-VC-STR-006 | 3 | L1 | SOFT | No Heading Violations — heading levels follow proper nesting hierarchy |
| DS-VC-STR-007 | 3 | L3 | SOFT | Canonical Section Ordering — required sections appear in canonical position order |
| DS-VC-STR-008 | 3 | L3 | HARD | No Critical Anti-Patterns — none of the 4 critical anti-patterns detected |
| DS-VC-STR-009 | 2 | L3 | SOFT | No Structural Anti-Patterns — none of the 5 structural anti-patterns detected |

**Total L1 Points:** 22 (STR-001 through STR-006)
**Total L3 Points:** 8 (STR-007 through STR-009)
**Total Dimension Points:** 30

### Scoring Mechanism

Each criterion contributes its point value to the structural dimension score. A file earns points on each criterion based on how well it satisfies that criterion's requirements:
- Full compliance → full points
- Partial compliance → proportional points (e.g., 80% compliance = 80% of criterion points)
- No compliance → 0 points

The sum of all criterion points (out of 30) becomes the Structural Dimension score.

### Gating Interaction

The Structural Dimension interacts with the gating rule: critical anti-patterns (Ghost File, Structure Chaos, Encoding Disaster, Link Void) will cap the total composite score at 29, even if the Structural Dimension itself scores high. This ensures that files with fundamental structural failures never achieve a grade above CRITICAL.

## Implementation Reference

### Code Location
`src/docstratum/quality.py` → `QualityDimension.STRUCTURAL` enum value and `DimensionScore.structural_score` attribute

### Scoring Pipeline
1. **Criterion Evaluation Phase:** Each criterion (STR-001 through STR-009) is evaluated against the document
2. **Point Aggregation:** Points are accumulated from all L1 and L3 criteria
3. **Dimensional Score:** Aggregated points (out of 30) form the Structural Dimension score
4. **Gating Check:** If any critical anti-pattern is detected, the entire composite score is capped at 29 via `DimensionScore.is_gated = True`

### Python Interface
```python
from docstratum.quality import QualityDimension, DimensionScore

# During scoring
dimension_score = DimensionScore(
    dimension=QualityDimension.STRUCTURAL,
    earned_points=25,
    max_points=30,
    is_gated=False  # True if critical anti-pattern detected
)

# Retrieve
structural_score = composite_score.dimensions[QualityDimension.STRUCTURAL].earned_points
```

## Related Standards

### Quality Criteria
- **DS-VC-STR-001** through **DS-VC-STR-009:** All structural validation criteria
- **DS-VC-CON-008:** Canonical Section Names (relates to STR-007)
- **DS-VC-CON-009:** Master Index Presence (relates to STR-007)

### Dimensions
- **DS-QS-DIM-CON:** Content Dimension (50% weight, complementary)
- **DS-QS-DIM-APD:** Anti-Pattern Detection Dimension (20% weight, complementary)

### Thresholds and Gating
- **DS-QS-GRADE:** Quality Grade Thresholds (converts composite score to grade letter)
- **DS-QS-GATE:** Structural Gating Rule (caps score at 29 if critical anti-patterns detected)

### Decisions
- **DECISION-014:** Content quality receives 30% structural weight (vs. legacy 50%)
- **DECISION-012:** Canonical section ordering importance
- **DECISION-010:** Frequency analysis baseline for structural patterns

## Rationale

The Structural Dimension is weighted at 30% because well-formed Markdown is a necessary but not sufficient condition for quality documentation. A file can be perfectly structured but contain no useful content. However, a file that is not well-structured is unreadable and unusable, even if it contains valuable information.

Empirical analysis (v0.0.2c–v0.0.4b) shows that structural failures correlate strongly with low overall quality scores, but do not independently predict utility to LLM consumers. The 30% weight reflects this: structural problems are serious (capped at 29 if critical), but content quality is the primary driver of overall quality.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.5 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
