# DS-QS-DIM-CON: Content Dimension

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-QS-DIM-CON |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Element Type** | Quality Dimension |
| **Source Code** | `quality.py` → `QualityDimension.CONTENT` |
| **Provenance** | DECISION-014; DECISION-015; v0.0.2c correlation analysis |

## Description

The Content Dimension measures the substantive value and utility of documentation for AI agents and developers. It evaluates the presence and quality of code examples, completeness of API coverage, clarity of explanations, practical value of guidance, presence of key structural elements (like the Master Index), and alignment with LLM-oriented documentation best practices.

This is the **primary scoring dimension** per DECISION-014, reflecting empirical findings that content quality is the strongest predictor of overall documentation utility. Notably, code examples show the highest correlation with quality outcomes (r ≈ 0.65 from v0.0.2c analysis across 450+ projects).

The Content Dimension is assessed across two levels:
- **L2 (Content Quality Foundations):** Criteria CON-001 through CON-007 (25 points) — presence of key content elements
- **L3 (Advanced Content Patterns):** Criteria CON-008 through CON-013 (25 points) — depth, completeness, and LLM-specific optimizations

The Content Dimension contributes **50 points (50% of total weight)** to the composite quality score.

## Specification

### Weight and Scoring
- **Maximum Points:** 50
- **Weight Percentage:** 50% [CALIBRATION-NEEDED]
- **Scoring Model:** Graduated (criterion weights reflect empirical quality predictors)
- **Dimension ID:** `QualityDimension.CONTENT`
- **Primary Strength:** Code examples (r ≈ 0.65)

### Constituent Criteria

| Criterion | Points | Level | Description |
|-----------|--------|-------|-------------|
| DS-VC-CON-001 | 4 | L2 | Code examples present — at least one executable example included |
| DS-VC-CON-002 | 4 | L2 | API/Function coverage — key API endpoints or functions documented |
| DS-VC-CON-003 | 3 | L2 | Quick start provided — getting-started section with copy-paste ready code |
| DS-VC-CON-004 | 3 | L2 | Configuration guidance — instructions for common setup scenarios |
| DS-VC-CON-005 | 4 | L2 | Error handling documentation — common errors and solutions |
| DS-VC-CON-006 | 4 | L2 | Type/parameter documentation — function signatures or schema definitions |
| DS-VC-CON-007 | 3 | L2 | Conceptual clarity — explanations are accessible to target audience |
| DS-VC-CON-008 | 4 | L3 | Master Index present — table of contents / navigation hub included |
| DS-VC-CON-009 | 4 | L3 | Related resources linked — cross-references to other documentation |
| DS-VC-CON-010 | 4 | L3 | Real-world use cases — practical examples beyond toy code |
| DS-VC-CON-011 | 3 | L3 | Performance/efficiency notes — guidance on optimization or trade-offs |
| DS-VC-CON-012 | 3 | L3 | Deprecation warnings — documentation of deprecated features |
| DS-VC-CON-013 | 3 | L3 | LLM-optimized structure — content formatted for AI agent consumption |

**Total L2 Points:** 25
**Total L3 Points:** 25
**Total Dimension Points:** 50

### Scoring Mechanism

Each criterion contributes its point value based on how completely the documentation satisfies the criterion:
- Full compliance → full points
- Partial compliance → proportional points (e.g., code examples present but minimal = 50% of CON-001 points)
- No compliance → 0 points

The sum of all criterion points (out of 50) becomes the Content Dimension score.

### Empirical Calibration

The Content Dimension weighting is based on empirical correlation analysis from v0.0.2c (450+ project sample):
- **Code examples:** r ≈ 0.65 (strongest single predictor)
- **Master Index:** 87% LLM task success vs. 31% without
- **API coverage:** r ≈ 0.48
- **Quick start:** r ≈ 0.42

These findings support the 50% weight for Content and the 4-point allocation to CON-001 (code examples).

## Implementation Reference

### Code Location
`src/docstratum/quality.py` → `QualityDimension.CONTENT` enum value and `DimensionScore.content_score` attribute

### Scoring Pipeline
1. **Criterion Evaluation Phase:** Each criterion (CON-001 through CON-013) is evaluated against the document
2. **Empirical Weight Application:** Criteria are weighted according to correlation coefficients from v0.0.2c analysis
3. **Point Aggregation:** Points are accumulated from all L2 and L3 criteria
4. **Dimensional Score:** Aggregated points (out of 50) form the Content Dimension score
5. **Audience Adaptation:** Per DECISION-015, "quality content" may be reinterpreted based on target consumer (e.g., MCP agents vs. human developers)

### Python Interface
```python
from docstratum.quality import QualityDimension, DimensionScore

# During scoring
dimension_score = DimensionScore(
    dimension=QualityDimension.CONTENT,
    earned_points=40,
    max_points=50,
    is_gated=False
)

# Retrieve
content_score = composite_score.dimensions[QualityDimension.CONTENT].earned_points
```

## Related Standards

### Quality Criteria
- **DS-VC-CON-001** through **DS-VC-CON-013:** All content validation criteria
- **DS-VC-STR-008:** Canonical Section Ordering (intersects with Master Index — CON-008)
- **DS-VC-CON-009:** Master Index Present (dedicated criterion for this critical element)

### Dimensions
- **DS-QS-DIM-STR:** Structural Dimension (30% weight, complementary)
- **DS-QS-DIM-APD:** Anti-Pattern Detection Dimension (20% weight, complementary)

### Thresholds and Gating
- **DS-QS-GRADE:** Quality Grade Thresholds (converts composite score to grade letter)
- **DS-QS-GATE:** Structural Gating Rule (does not directly affect Content Dimension scoring, but affects total)

### Decisions
- **DECISION-014:** Content Dimension receives 50% weight as primary quality driver
- **DECISION-015:** MCP target consumer influences what "quality content" means; content criteria may be adapted for different audiences
- **DECISION-012:** Canonical section importance, especially Master Index

## Rationale

Content is the primary dimension (50% weight) because empirical analysis consistently shows that the presence and quality of substantive documentation drives utility outcomes. A structurally perfect file with no real content is useless. Conversely, a file with minor structural issues but rich content is often more valuable than one with flawless structure and minimal substance.

The 50% weight for Content is justified by:
1. **Empirical correlation:** Code examples (r ≈ 0.65) are the strongest single quality predictor
2. **LLM task success:** Master Index presence correlates with 87% vs. 31% success rates
3. **Audience alignment:** Developers and AI agents both prioritize what information a file contains over how perfectly formatted it is
4. **Strategic direction:** DECISION-014 explicitly positions Content as the primary dimension

Criterion weights are calibrated to reflect empirical findings, with heavier point allocations to the strongest predictors (code examples: 4 points, Master Index: 4 points, API coverage: 4 points).

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.5 |
