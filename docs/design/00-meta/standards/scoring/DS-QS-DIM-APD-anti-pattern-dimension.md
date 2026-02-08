# DS-QS-DIM-APD: Anti-Pattern Detection Dimension

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-QS-DIM-APD |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Element Type** | Quality Dimension |
| **Source Code** | `quality.py` → `QualityDimension.ANTI_PATTERN` |
| **Provenance** | DECISION-014; DECISION-016; v0.0.3a anti-pattern taxonomy |

## Description

The Anti-Pattern Detection Dimension measures the absence of quality anti-patterns — common documentation problems that degrade utility. Unlike the Structural and Content dimensions (which add points for positive attributes), the Anti-Pattern Dimension is **deduction-based**: files start with a perfect score of 20 points and lose points for each detected anti-pattern.

This dimension reflects the principle that avoiding bad practices is as important as implementing good ones. Critical anti-patterns (e.g., files that are unparseable or have broken links) trigger the gating mechanism that caps the total score. Other anti-patterns trigger proportional deductions based on severity.

The Anti-Pattern Dimension contributes **20 points (20% of total weight)** to the composite quality score.

## Specification

### Weight and Scoring
- **Maximum Points:** 20
- **Weight Percentage:** 20% [CALIBRATION-NEEDED]
- **Scoring Model:** Deduction-based (starts at max, loses points per detected pattern)
- **Dimension ID:** `QualityDimension.ANTI_PATTERN`

### Anti-Pattern Registry

The Anti-Pattern Dimension monitors **28 documented anti-patterns** across **5 severity categories**:

#### Critical Patterns (4 patterns)
These patterns indicate fundamental document failure. Each triggers gating (score capped at 29) and causes large deductions:

| Anti-Pattern ID | Code | Points Lost | Description |
|-----------------|------|-------------|-------------|
| AP-CRIT-001 | `GHOST_FILE` | 20 | File is empty, unreadable, or not valid Markdown — effectively unparseable |
| AP-CRIT-002 | `STRUCTURE_CHAOS` | 20 | Heading structure is completely broken — no valid hierarchy, multiple H1s, severe nesting errors |
| AP-CRIT-003 | `ENCODING_DISASTER` | 20 | File contains invalid UTF-8 or other encoding errors that prevent parsing |
| AP-CRIT-004 | `LINK_VOID` | 20 | 80% or more of links are broken (404s, invalid syntax, pointing to missing anchors) |

#### Structural Patterns (5 patterns)
These patterns indicate structural quality issues. Each causes moderate deductions:

| Anti-Pattern ID | Code | Points Lost | Description |
|-----------------|------|-------------|-------------|
| AP-STRUC-001 | `NO_HEADINGS` | 4 | Document has no heading structure — all content appears as paragraphs |
| AP-STRUC-002 | `EXCESSIVE_NESTING` | 3 | Heading hierarchy goes beyond H4 (more than 4 levels deep) |
| AP-STRUC-003 | `ORPHAN_SECTIONS` | 2 | Sections exist without relationship to document structure (malformed markdown) |
| AP-STRUC-004 | `UNBALANCED_SECTIONS` | 2 | Some sections are extremely long (10,000+ words) while others are stubs |
| AP-STRUC-005 | `METADATA_MISSING` | 1 | Front matter or metadata table is absent or incomplete |

#### Content Patterns (9 patterns)
These patterns indicate missing or low-quality content. Each causes small to moderate deductions:

| Anti-Pattern ID | Code | Points Lost | Description |
|-----------------|------|-------------|-------------|
| AP-CONT-001 | `NO_CODE_EXAMPLES` | 3 | Document contains no code examples or runnable samples |
| AP-CONT-002 | `NO_API_DOCS` | 2 | API functions/endpoints are undocumented or mention-only |
| AP-CONT-003 | `VAGUE_EXPLANATIONS` | 2 | Explanations use jargon without definition; unclear to target audience |
| AP-CONT-004 | `NO_QUICK_START` | 2 | No getting-started section; setup process must be inferred |
| AP-CONT-005 | `NO_ERROR_HANDLING` | 1 | No documentation of common errors or troubleshooting |
| AP-CONT-006 | `OUTDATED_INFO` | 2 | Documentation references outdated versions or deprecated features without warnings |
| AP-CONT-007 | `NO_RELATED_LINKS` | 1 | Related documentation is not linked or referenced |
| AP-CONT-008 | `MISSING_EXAMPLES` | 2 | Examples are present but are trivial, toy code, or not realistic |
| AP-CONT-009 | `NO_CONFIG_GUIDANCE` | 1 | Configuration options are listed but not explained; no setup guidance |

#### Strategic Patterns (4 patterns)
These patterns indicate misalignment with documentation strategy. Each causes minor deductions:

| Anti-Pattern ID | Code | Points Lost | Description |
|-----------------|------|-------------|-------------|
| AP-STRAT-001 | `NO_MASTER_INDEX` | 2 | Master Index or table of contents is missing |
| AP-STRAT-002 | `WEAK_POSITIONING` | 1 | Document doesn't explain what problem it solves or for whom |
| AP-STRAT-003 | `NON_CANONICAL_SECTIONS` | 1 | Document doesn't follow canonical section naming or ordering |
| AP-STRAT-004 | `NOT_LLM_OPTIMIZED` | 1 | Content structure doesn't account for token limits or LLM reading patterns |

#### Ecosystem Patterns (6 patterns)
These patterns indicate poor integration with documentation ecosystem. Each causes minimal deductions:

| Anti-Pattern ID | Code | Points Lost | Description |
|-----------------|------|-------------|-------------|
| AP-ECO-001 | `ORPHANED_DOCS` | 1 | Document is not referenced from any index or parent page |
| AP-ECO-002 | `BROKEN_CROSS_REFS` | 1 | Cross-references to other docs are broken or outdated |
| AP-ECO-003 | `VERSION_MISMATCH` | 1 | Documentation version doesn't match software version |
| AP-ECO-004 | `NO_CHANGELOG` | 1 | Change history is missing or never updated |
| AP-ECO-005 | `MISSING_LICENSE` | 0 | No license information (informational, not scored) |
| AP-ECO-006 | `NO_MAINTAINER_INFO` | 0 | No contact or maintenance information (informational, not scored) |

### Scoring Mechanism

**Starting Score:** 20 points (perfect anti-pattern score)

**Calculation:** For each detected anti-pattern, subtract the points listed in the registry:
```
anti_pattern_score = 20 - sum(points_lost for each detected pattern)
anti_pattern_score = max(0, anti_pattern_score)  # Never below 0
```

**Gating Trigger:** If ANY critical pattern (AP-CRIT-001 through AP-CRIT-004) is detected, set `DimensionScore.is_gated = True` and the total composite score is capped at 29 (ensuring CRITICAL grade).

**Multiple Patterns:** Multiple deductions stack. A file could have:
- 1 Critical pattern (20 points lost, gated) + 2 Structural patterns (5 points lost) = score of −5 (capped at 0, but gating still applies)
- 3 Content patterns (6 points lost) = score of 14 points

### Severity Model

Deductions follow a four-tier severity model per DECISION-016:
1. **Critical (Level 1):** 20 points — fundamental document failure
2. **High (Level 2):** 3–4 points — structural quality severely impacted
3. **Medium (Level 3):** 1–2 points — content or ecosystem quality affected
4. **Low (Level 4):** 0 points — informational only, not scored

## Implementation Reference

### Code Location
`src/docstratum/quality.py` → `QualityDimension.ANTI_PATTERN` enum value and anti-pattern detection functions

### Scoring Pipeline
1. **Pattern Detection Phase:** Document is scanned for each of the 28 anti-patterns
2. **Severity Classification:** Detected patterns are classified by severity tier
3. **Deduction Aggregation:** Points are subtracted based on detected patterns
4. **Gating Check:** If critical patterns detected, `is_gated = True`
5. **Dimensional Score:** Final anti-pattern score (20 or less, minimum 0)

### Python Interface
```python
from docstratum.quality import QualityDimension, DimensionScore, AntiPattern

# During scoring
dimension_score = DimensionScore(
    dimension=QualityDimension.ANTI_PATTERN,
    earned_points=14,  # 20 - 6 deductions
    max_points=20,
    is_gated=False  # True if critical pattern detected
)

# Detected patterns
detected = [
    AntiPattern.NO_CODE_EXAMPLES,  # -3
    AntiPattern.VAGUE_EXPLANATIONS,  # -2
    AntiPattern.NO_RELATED_LINKS,  # -1
]
```

## Related Standards

### Anti-Pattern Specifications
- **DS-AP-CRIT-001** through **DS-AP-CRIT-004:** Critical anti-patterns (gating triggers)
- **DS-AP-STRUC-001** through **DS-AP-STRUC-005:** Structural anti-patterns
- **DS-AP-CONT-001** through **DS-AP-CONT-009:** Content anti-patterns
- **DS-AP-STRAT-001** through **DS-AP-STRAT-004:** Strategic anti-patterns
- **DS-AP-ECO-001** through **DS-AP-ECO-006:** Ecosystem anti-patterns

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

The Anti-Pattern Dimension is deduction-based (rather than additive) because avoiding common problems is fundamentally different from achieving excellence. A file that avoids all major pitfalls should not be penalized for not being exceptional. This model reflects the principle: "start with a good baseline (20 points), lose points only for detected problems."

The 20% weight for Anti-Patterns is positioned as a quality floor: files that avoid critical mistakes score reasonably well on this dimension, but files with critical patterns are immediately gated to ensure they never achieve a higher grade. This creates a safety mechanism that complements the positive weighting of Structural and Content.

The severity-weighted deduction model (DECISION-016) ensures that critical failures (unparseable files) have equal weight to major content gaps, while minor ecosystem issues don't drag down the score disproportionately.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.5 |
