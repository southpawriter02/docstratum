# DS-QS-DIM-APD: Anti-Pattern Detection Dimension

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-QS-DIM-APD |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Element Type** | Quality Dimension |
| **Source Code** | `quality.py` → `QualityDimension.ANTI_PATTERN` |
| **Provenance** | DECISION-014; DECISION-016; v0.0.3a anti-pattern taxonomy |

## Description

The Anti-Pattern Detection Dimension measures documentation quality from the perspective of LLM optimization and anti-pattern avoidance. It uses a **criterion-based (additive) model** with 8 validation criteria (APD-001 through APD-008), each earning points for positive attributes or confirmed absence of problems.

This dimension addresses two complementary concerns: (1) the presence of LLM-specific content enhancements (instructions, concept definitions, few-shot examples) and (2) the absence of documented anti-patterns across content, strategic, and ecosystem categories. Critical anti-patterns additionally trigger the gating mechanism (via DS-QS-GATE) that caps the total composite score at 29, regardless of this dimension's score.

The Anti-Pattern Detection Dimension contributes **20 points (20% of total weight)** to the composite quality score.

## Specification

### Weight and Scoring
- **Maximum Points:** 20
- **Weight Percentage:** 20%
- **Scoring Model:** Criterion-based (additive — points earned for positive attributes)
- **Dimension ID:** `QualityDimension.ANTI_PATTERN`

### Constituent Criteria

The Anti-Pattern Detection Dimension is scored through 8 validation criteria, all at Level 4 (Exemplary):

| Criterion | Points | Level | Pass | Description |
|-----------|--------|-------|------|-------------|
| DS-VC-APD-001 | 3 | L4 | SOFT | LLM Instructions Section — explicit machine-facing instructions present (15–23% improvement) |
| DS-VC-APD-002 | 3 | L4 | SOFT | Concept Definitions — authoritative terminology section present (12–18% improvement) |
| DS-VC-APD-003 | 3 | L4 | SOFT | Few-Shot Examples — structured pedagogical examples included (25–40% improvement) |
| DS-VC-APD-004 | 3 | L4 | SOFT | No Content Anti-Patterns — free of 9 content-level anti-patterns (AP-CONT-001–009) |
| DS-VC-APD-005 | 2 | L4 | SOFT | No Strategic Anti-Patterns — free of 4 strategic anti-patterns (AP-STRAT-001–004) |
| DS-VC-APD-006 | 2 | L4 | SOFT | Token-Optimized Structure — no section exceeds 40% of total token budget |
| DS-VC-APD-007 | 2 | L4 | SOFT | Relative URL Minimization — ≥90% of URLs are absolute (MCP consumption context) |
| DS-VC-APD-008 | 2 | L4 | SOFT | Jargon Defined or Linked — domain-specific terms have definitions or links |

**Total L4 Points:** 20 (APD-001 through APD-008)
**Total Dimension Points:** 20

### Underlying Anti-Pattern Registry

The 28 documented anti-patterns (across 5 severity categories) are defined in individual standard files (DS-AP-*) and referenced by the criteria above. APD-004 evaluates the 9 content anti-patterns; APD-005 evaluates the 4 strategic anti-patterns. Critical and structural anti-patterns are evaluated by criteria in the Structural Dimension (DS-VC-STR-008 and DS-VC-STR-009 respectively). Ecosystem anti-patterns are evaluated by the Ecosystem Health dimensions (DS-EH-*).

The full registry comprises: 4 critical (AP-CRIT-001–004), 5 structural (AP-STRUCT-001–005), 9 content (AP-CONT-001–009), 4 strategic (AP-STRAT-001–004), and 6 ecosystem (AP-ECO-001–006) patterns.

### Scoring Mechanism

Each criterion contributes its point value based on how completely the documentation satisfies the criterion:
- Full compliance → full points
- Partial compliance → proportional points
- No compliance → 0 points

The sum of all criterion points (out of 20) becomes the Anti-Pattern Detection Dimension score.

**Gating Interaction:** Critical anti-patterns (AP-CRIT-001 through AP-CRIT-004) are evaluated by DS-VC-STR-008 in the Structural Dimension but trigger gating via DS-QS-GATE, capping the total composite score at 29 regardless of this dimension's score.

### Severity Model

The underlying 28 anti-patterns follow a four-tier severity model per DECISION-016. While the criterion-based scoring model is additive, the severity tiers determine which criteria evaluate which anti-patterns:
1. **Critical (4 patterns):** Evaluated by DS-VC-STR-008; trigger gating (score cap at 29)
2. **Structural (5 patterns):** Evaluated by DS-VC-STR-009
3. **Content (9 patterns):** Evaluated by DS-VC-APD-004
4. **Strategic (4 patterns):** Evaluated by DS-VC-APD-005

## Implementation Reference

### Code Location
`src/docstratum/quality.py` → `QualityDimension.ANTI_PATTERN` enum value and anti-pattern detection functions

### Scoring Pipeline
1. **Criterion Evaluation Phase:** Each criterion (APD-001 through APD-008) is evaluated against the document
2. **Point Aggregation:** Points are accumulated from all L4 criteria
3. **Dimensional Score:** Aggregated points (out of 20) form the Anti-Pattern Detection Dimension score
4. **Gating Check:** Critical anti-pattern gating is handled separately by DS-VC-STR-008 and DS-QS-GATE

### Python Interface
```python
from docstratum.quality import QualityDimension, DimensionScore

# During scoring
dimension_score = DimensionScore(
    dimension=QualityDimension.ANTI_PATTERN,
    earned_points=16,  # Earned across APD-001 through APD-008
    max_points=20,
    is_gated=False  # Gating handled by structural dimension
)

# Retrieve
apd_score = composite_score.dimensions[QualityDimension.ANTI_PATTERN].earned_points
```

## Related Standards

### Quality Criteria
- **DS-VC-APD-001** through **DS-VC-APD-008:** All anti-pattern detection validation criteria

### Anti-Pattern Specifications
- **DS-AP-CRIT-001** through **DS-AP-CRIT-004:** Critical anti-patterns (gating triggers, evaluated by DS-VC-STR-008)
- **DS-AP-STRUCT-001** through **DS-AP-STRUCT-005:** Structural anti-patterns (evaluated by DS-VC-STR-009)
- **DS-AP-CONT-001** through **DS-AP-CONT-009:** Content anti-patterns (evaluated by DS-VC-APD-004)
- **DS-AP-STRAT-001** through **DS-AP-STRAT-004:** Strategic anti-patterns (evaluated by DS-VC-APD-005)
- **DS-AP-ECO-001** through **DS-AP-ECO-006:** Ecosystem anti-patterns (evaluated by DS-EH-* dimensions)

### Dimensions
- **DS-QS-DIM-STR:** Structural Dimension (30% weight, complementary)
- **DS-QS-DIM-CON:** Content Dimension (50% weight, complementary)

### Thresholds and Gating
- **DS-QS-GRADE:** Quality Grade Thresholds (converts composite score to grade letter)
- **DS-QS-GATE:** Structural Gating Rule (critical patterns cap total score at 29)

### Decisions
- **DECISION-014:** Anti-Pattern Dimension receives 20% weight
- **DECISION-016:** Four-tier severity classification for anti-patterns; critical patterns trigger gating

## Rationale

The Anti-Pattern Detection Dimension uses a criterion-based (additive) model rather than a deduction model to maintain consistency with the Structural and Content dimensions. All three dimensions use the same "earn points for meeting criteria" approach, making the composite score calculation uniform and predictable.

The 8 APD criteria split into two tiers: the "core four" (APD-001 through APD-004, 3 points each) address LLM-specific content enhancements and aggregate anti-pattern checks; the "supporting four" (APD-005 through APD-008, 2 points each) address secondary optimization concerns. This 3/3/3/3/2/2/2/2 distribution reflects the empirical evidence: LLM instructions, concept definitions, and few-shot examples show the strongest improvement signals (15–40%), while token optimization and URL strategy show more context-dependent benefits.

The 20% weight for Anti-Patterns positions this dimension as the differentiator between STRONG and EXEMPLARY grades. A file that excels in Structural (30) and Content (50) earns up to 80 points — enough for STRONG but not EXEMPLARY. The APD dimension's 20 points provide the path to the 90+ threshold required for EXEMPLARY, ensuring that only files with genuine LLM optimization reach the highest grade.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.5 |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
