# DS-QS-GRADE: Quality Grade Thresholds

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-QS-GRADE |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Element Type** | Grade Thresholds |
| **Source Code** | `quality.py` → `QualityGrade.from_score()` |
| **Provenance** | DECISION-014; v0.0.3b gold standard calibration |

## Description

The Quality Grade Thresholds define how numeric quality scores (0–100) are converted into human-readable quality grades. The grading system uses five tiers aligned with the ASoT content levels (L0 through L4), calibrated against real-world "gold standard" documentation specimens from widely-used open-source projects.

Each grade threshold is set based on empirical data from v0.0.3b calibration, in which leading documentation projects were scored and their grades were validated against qualitative assessment. The thresholds ensure that exemplary documentation (Svelte, Pydantic, Vercel SDK) scores in the EXEMPLARY band (90+), while clearly inadequate documentation scores appropriately low.

## Specification

### Grade Scale

| Grade | Score Range | ASoT Level | Description | Numeric Threshold |
|-------|-------|-----------|-------------|-------------------|
| **EXEMPLARY** | 90–100 | L4 (DocStratum Extended) | Documentation exceeds best practices; highly optimized for LLM and developer consumption; rich content with excellent organization | ≥ 90 [CALIBRATION-NEEDED] |
| **STRONG** | 70–89 | L3 (Best Practices) | Documentation meets best practices; well-structured, comprehensive content, good examples and guidance | ≥ 70 [CALIBRATION-NEEDED] |
| **ADEQUATE** | 50–69 | L2 (Content Quality) | Documentation is functional; basic content present, though could be more complete or better organized | ≥ 50 [CALIBRATION-NEEDED] |
| **NEEDS_WORK** | 30–49 | L1 (Structural) | Documentation has significant gaps or organizational issues; basic structure present but content is sparse | ≥ 30 [CALIBRATION-NEEDED] |
| **CRITICAL** | 0–29 | L0 (Parseable Only) | Documentation has fundamental problems; unparseable, severely broken structure, or missing critical content | < 30 [CALIBRATION-NEEDED] |

### Calculation Method

The grade is determined by a simple threshold comparison on the composite quality score:

```python
if score >= 90:
    grade = QualityGrade.EXEMPLARY
elif score >= 70:
    grade = QualityGrade.STRONG
elif score >= 50:
    grade = QualityGrade.ADEQUATE
elif score >= 30:
    grade = QualityGrade.NEEDS_WORK
else:  # score < 30
    grade = QualityGrade.CRITICAL
```

No interpolation or weighting is applied at the grading stage; the final composite score determines the grade directly.

### Grade Alignment with ASoT Levels

The five grades map directly to the ASoT (Algorithm of Service Tiers) content levels:

| Grade | ASoT Level | Definition |
|-------|-----------|-----------|
| EXEMPLARY | L4 | Extended best practices; LLM-optimized; goes beyond minimum requirements |
| STRONG | L3 | Comprehensive best practices; meets all major requirements, well-executed |
| ADEQUATE | L2 | Core content quality; functional, but not optimized or comprehensive |
| NEEDS_WORK | L1 | Structural foundations present; content gaps or organizational issues |
| CRITICAL | L0 | Parseable only; fundamental failures; not fit for use |

## Calibration Reference

### Gold Standard Specimens

Thresholds were calibrated v0.0.3b against leading open-source projects scored by human raters:

| Project | Domain | Calibrated Score | Grade | Notes |
|---------|--------|-----|------|-------|
| **Svelte** | Web framework docs | 92 | EXEMPLARY | Exemplary: comprehensive, LLM-friendly structure, excellent examples |
| **Pydantic** | Python validation library | 90 | EXEMPLARY | Exemplary: API docs, error guidance, validation examples |
| **Vercel SDK** | JavaScript/TypeScript SDK | 90 | EXEMPLARY | Exemplary: quick starts, API reference, interactive examples |
| **Shadcn UI** | React component library | 89 | STRONG | Strong: well-organized, code examples, but less LLM-optimized |
| **Cursor** | AI coding assistant | 42 | NEEDS_WORK | Significant gaps: sparse API docs, minimal examples, poor organization |
| **NVIDIA** | GPU computing platform | 24 | CRITICAL | Critical: scattered documentation, broken links, no clear structure |

### Boundary Justification

- **90 threshold (EXEMPLARY):** Svelte, Pydantic, and Vercel SDK all score at or above 90. These represent the gold standard: comprehensive, well-structured, rich with examples and guidance. Documentation at this level is not just correct but exceptional.

- **70 threshold (STRONG):** Shadcn UI scores at 89 (just below EXEMPLARY). The 70 threshold captures the gap between "meets best practices" (70+) and "functional but with gaps" (50–69).

- **50 threshold (ADEQUATE):** This marks the transition from "serviceable" (50+) to "problematic" (<50). Documentation at 50+ has meaningful content but may lack depth, organization, or examples.

- **30 threshold (NEEDS_WORK):** Cursor scores at 42, representing documentation with significant gaps and organizational issues but still parseable. The 30 threshold separates this from CRITICAL (fundamentally broken).

- **0 threshold (CRITICAL):** NVIDIA scores at 24, representing severely broken documentation. Score of 0–29 indicates files that are not fit for use (unparseable, no links, no structure).

### Empirical Validation

Thresholds were validated by:
1. Scoring 12 real-world projects using the three-dimension model
2. Comparing calculated scores to qualitative assessments by documentation experts
3. Verifying that thresholds correctly classify projects into intended grade bands
4. Ensuring gating rule (capped at 29 for critical anti-patterns) aligns with CRITICAL grade

## Implementation Reference

### Code Location
`src/docstratum/quality.py` → `QualityGrade` enum and `QualityGrade.from_score(score: int) -> QualityGrade` method

### Scoring Pipeline Integration
1. **Dimension Scoring:** Structural (0–30) + Content (0–50) + Anti-Pattern (0–20) = Composite (0–100)
2. **Gating Check:** If critical anti-pattern detected, composite capped at 29
3. **Grade Assignment:** Use `QualityGrade.from_score()` to map composite score to grade
4. **Output:** Grade is returned as `QualityGrade` enum value

### Python Interface
```python
from docstratum.quality import QualityGrade, CompositeScore

# After calculating composite score
composite_score = 85
grade = QualityGrade.from_score(composite_score)
# Returns: QualityGrade.STRONG

# Grade can be accessed as enum
print(grade.name)  # "STRONG"
print(grade.value)  # 3 (enum ordinal)

# Grade has human-readable properties
print(grade.description)  # "Meets best practices; comprehensive content..."
print(grade.level)  # "L3 (Best Practices)"
```

### Boundary Behavior

The `from_score()` method uses **inclusive lower bounds** (≥) for all thresholds:
- Score 90–100 → EXEMPLARY
- Score 70–89 → STRONG
- Score 50–69 → ADEQUATE
- Score 30–49 → NEEDS_WORK
- Score 0–29 → CRITICAL

This means a score of exactly 90 is EXEMPLARY, 70 is STRONG, etc.

## Related Standards

### Scoring Dimensions
- **DS-QS-DIM-STR:** Structural Dimension (contributes 0–30 points)
- **DS-QS-DIM-CON:** Content Dimension (contributes 0–50 points)
- **DS-QS-DIM-APD:** Anti-Pattern Dimension (contributes 0–20 points)

### Gating and Enforcement
- **DS-QS-GATE:** Structural Gating Rule (caps composite score at 29 if critical anti-patterns detected)

### Validation Criteria
- **DS-VC-STR-001** through **DS-VC-STR-009:** Structural criteria feed into Structural Dimension
- **DS-VC-CON-001** through **DS-VC-CON-013:** Content criteria feed into Content Dimension
- **DS-AP-CRIT-001** through **DS-AP-CRIT-004:** Critical patterns trigger gating

### Decisions
- **DECISION-014:** Three-dimension weight model (30% Structural, 50% Content, 20% Anti-Pattern)
- **DECISION-016:** Critical anti-pattern severity and gating mechanism

## Grade Interpretation Guide

### EXEMPLARY (90–100)
**What it means:** Gold-standard documentation. Comprehensive, well-organized, rich with examples and guidance. Optimized for both human developers and LLM agents.

**Real-world examples:** Svelte, Pydantic, Vercel SDK

**What to expect:**
- Code examples integrated throughout
- Complete API reference with examples for every function/endpoint
- Master Index or clear navigation
- Error handling and troubleshooting guide
- Quick-start guide and advanced tutorials
- Performance/efficiency notes
- Well-structured canonical sections
- LLM-optimized formatting (short paragraphs, code blocks, etc.)

### STRONG (70–89)
**What it means:** Best practices met. Well-structured documentation with good content coverage. May lack some advanced optimizations but is comprehensive and useful.

**Real-world examples:** Shadcn UI

**What to expect:**
- Code examples present and relevant
- API documentation complete, though possibly less thorough than EXEMPLARY
- Clear structure with proper headings and navigation
- Getting-started guide
- Some examples of error handling or advanced usage
- Good organization, though not necessarily LLM-optimized

### ADEQUATE (50–69)
**What it means:** Functional documentation. Core content is present, but organization or completeness could be improved. Usable, but not optimized.

**What to expect:**
- Basic code examples
- API listed, though explanations may be sparse
- Some structural organization, though heading hierarchy may be inconsistent
- Getting-started exists but may be minimal
- Content is present but could be more complete
- Organization is acceptable but not best-practice

### NEEDS_WORK (30–49)
**What it means:** Significant gaps. Documentation exists and is parseable, but has organizational issues or sparse content. Requires effort to use.

**Real-world examples:** Cursor (42)

**What to expect:**
- Minimal code examples
- API partially documented or vague explanations
- Weak heading structure or unclear organization
- Limited or missing quick-start guide
- Sparse content; requires inference to use
- May have outdated or deprecated information

### CRITICAL (0–29)
**What it means:** Fundamental problems. Documentation is not fit for use. May be unparseable, have no structure, or have extensive broken links.

**Real-world examples:** NVIDIA (24)

**What to expect:**
- Unparseable files or severe encoding errors
- Heading structure missing or completely broken
- 80%+ of links broken
- Little to no code examples
- No clear structure or navigation
- May trigger gating rule (critical anti-patterns detected)

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.5; calibrated thresholds from v0.0.3b gold standard specimens |
