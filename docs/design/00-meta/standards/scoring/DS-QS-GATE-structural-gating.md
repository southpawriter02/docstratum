# DS-QS-GATE: Structural Gating Rule

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-QS-GATE |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Element Type** | Gating Rule |
| **Source Code** | `quality.py` → `DimensionScore.is_gated` |
| **Provenance** | DECISION-016; v0.0.3b anti-pattern severity classification |

## Description

The Structural Gating Rule is a critical enforcement mechanism in the quality scoring pipeline. When **any of the four critical anti-patterns** are detected (Ghost File, Structure Chaos, Encoding Disaster, or Link Void), the entire composite quality score is automatically capped at 29, ensuring that the file receives no higher than a CRITICAL grade regardless of how well it performs on individual content or anti-pattern dimensions.

The gating rule embodies the principle that **fundamentally broken files are not "adequate" regardless of their content**. A file that is unparseable, structurally incoherent, or has 80%+ broken links is not fit for use, even if the small amount of parseable content is of high quality.

## Specification

### Trigger Conditions

The gating rule is triggered (activated) when ANY of the following critical anti-patterns is detected:

| Anti-Pattern ID | Code | Description | Detection Criteria |
|-----------------|------|-------------|-------------------|
| **AP-CRIT-001** | `GHOST_FILE` | File is empty, unreadable, or not valid Markdown | File size < 100 bytes OR not parseable as Markdown OR contains no readable text |
| **AP-CRIT-002** | `STRUCTURE_CHAOS` | Heading structure is completely broken | No valid heading hierarchy; multiple H1s; severe nesting errors (H1 → H3+); >50% of headings malformed |
| **AP-CRIT-003** | `ENCODING_DISASTER` | File contains invalid UTF-8 or encoding errors | File contains non-UTF-8 bytes; characters fail decoding; BOM markers cause issues |
| **AP-CRIT-004** | `LINK_VOID` | 80% or more of links are broken | 80%+ of markdown links fail validation; return 404; point to missing anchors; have invalid syntax |

### Effect on Score

**Before Gating Applied:**
```
Structural Dimension: 25 points (out of 30)
Content Dimension: 45 points (out of 50)
Anti-Pattern Dimension: 18 points (out of 20)
Composite Score: 25 + 45 + 18 = 88 (STRONG grade)
```

**After Gating Applied:**
```
Composite Score: min(88, 29) = 29 (CRITICAL grade)
is_gated: True
```

The gating rule forces the composite score down to 29, ensuring the file receives a CRITICAL grade.

### Boundary Behavior

- **If composite score ≤ 29:** Gating has no effect (score already in CRITICAL range)
- **If composite score > 29:** Gating reduces score to 29
- **If critical anti-pattern detected:** `is_gated` flag is set to `True` on the Structural Dimension

### Score Cap Value

**Cap Value:** 29 [CALIBRATION-NEEDED]

This cap value was chosen because:
1. It is the maximum score that still maps to the CRITICAL grade (0–29)
2. It ensures gated files are never classified above CRITICAL
3. It creates a clear "safety barrier" below the NEEDS_WORK threshold (30+)

## Implementation Reference

### Code Location
`src/docstratum/quality.py`:
- `DimensionScore.is_gated` boolean flag
- `CompositeScore.apply_gating()` method
- `QualityGrade.from_score()` integration

### Scoring Pipeline Integration

The gating rule is applied **after** all three dimensions are calculated but **before** the final grade is assigned:

```
1. Calculate Structural Dimension Score (0-30)
   ↓
2. Calculate Content Dimension Score (0-50)
   ↓
3. Calculate Anti-Pattern Dimension Score (0-20)
   ↓
4. Sum Composite Score: STR + CON + APD = 0-100
   ↓
5. GATING CHECKPOINT: Detect critical anti-patterns
   ↓
   IF (any critical pattern detected):
      Set Structural.is_gated = True
      Composite Score = min(Composite Score, 29)
   ↓
6. Assign Grade using QualityGrade.from_score()
   ↓
7. Return CompositeScore with grade and gating flag
```

### Python Interface

```python
from docstratum.quality import CompositeScore, DimensionScore, QualityDimension

# After calculating dimensions
structural = DimensionScore(
    dimension=QualityDimension.STRUCTURAL,
    earned_points=25,
    max_points=30,
    is_gated=False  # Will be set to True if critical pattern detected
)

content = DimensionScore(
    dimension=QualityDimension.CONTENT,
    earned_points=45,
    max_points=50
)

anti_pattern = DimensionScore(
    dimension=QualityDimension.ANTI_PATTERN,
    earned_points=18,
    max_points=20
)

# Create composite and apply gating
composite = CompositeScore(
    dimensions=[structural, content, anti_pattern]
)

# Detect critical patterns (internally)
if detect_critical_anti_patterns(document):
    structural.is_gated = True
    composite.apply_gating(cap_value=29)

# Grade is assigned based on gated score
final_grade = composite.grade  # Will be CRITICAL if gated
```

### Detection Logic

Critical patterns are detected during the Anti-Pattern Dimension scoring phase:

```python
def detect_critical_patterns(document) -> List[CriticalPattern]:
    critical = []

    if is_ghost_file(document):
        critical.append(CriticalPattern.GHOST_FILE)

    if has_structure_chaos(document):
        critical.append(CriticalPattern.STRUCTURE_CHAOS)

    if has_encoding_disaster(document):
        critical.append(CriticalPattern.ENCODING_DISASTER)

    if has_link_void(document):
        critical.append(CriticalPattern.LINK_VOID)

    return critical
```

## Related Standards

### Critical Anti-Patterns
- **DS-AP-CRIT-001:** Ghost File (empty, unreadable, or unparseable)
- **DS-AP-CRIT-002:** Structure Chaos (broken heading hierarchy)
- **DS-AP-CRIT-003:** Encoding Disaster (invalid UTF-8, encoding errors)
- **DS-AP-CRIT-004:** Link Void (80%+ broken links)

### Quality Dimensions
- **DS-QS-DIM-STR:** Structural Dimension (gating flag stored here)
- **DS-QS-DIM-CON:** Content Dimension (not directly affected, but composite score is)
- **DS-QS-DIM-APD:** Anti-Pattern Dimension (detects critical patterns)

### Grading
- **DS-QS-GRADE:** Quality Grade Thresholds (CRITICAL grade = 0–29)

### Decisions
- **DECISION-016:** Four-tier severity classification; critical patterns trigger gating
- **DECISION-014:** Three-dimension scoring model; gating rule is external enforcement

## Rationale and Philosophy

### Why Gating Matters

Documentation scoring must balance two principles:
1. **Measuring quality holistically** (all three dimensions weighted fairly)
2. **Enforcing safety thresholds** (fundamentally broken files never score high)

Without gating, a file could theoretically score very high on content (e.g., "this file has great code examples, even though it's not parseable"). Gating prevents this logical inconsistency.

### The Four Critical Patterns

The four critical patterns were chosen because they represent **document-level failures** that render the file unusable:

- **Ghost File:** If the file can't be read or parsed, nothing in it is accessible
- **Structure Chaos:** Without structure, content cannot be navigated or understood
- **Encoding Disaster:** If the file can't be decoded, it might as well not exist
- **Link Void:** If almost all links are broken, the file is a "void" — disconnected from the ecosystem

Each represents a **different axis of failure** that, alone, makes the document unfit for use.

### Why Cap at 29?

The cap value of 29 was chosen to align with grade thresholds:
- CRITICAL grade is defined as 0–29
- NEEDS_WORK grade is defined as 30–49
- Capping at 29 ensures gated files are never classified as NEEDS_WORK or higher

This creates a clear, unambiguous boundary: if a file is fundamentally broken, it is CRITICAL. There is no intermediate grade.

### Proportionality Note

The gating rule is **non-proportional**: detecting one critical pattern causes the same cap as detecting all four. This is intentional. The principle is: "If the file is fundamentally broken in any way, cap it." The specific number of critical patterns doesn't matter; one is enough to disqualify.

## Example Scenarios

### Scenario 1: Gating Triggered (LINK_VOID)

File analysis:
- Structural score: 28/30 (well-formed Markdown, good structure)
- Content score: 48/50 (comprehensive API docs, great examples)
- Anti-Pattern score: 15/20 (a few minor issues, but no critical patterns... except...)
- Link analysis: 85% of links are broken → **LINK_VOID** detected
- `is_gated`: True
- Composite before gating: 28 + 48 + 15 = 91 (EXEMPLARY)
- Composite after gating: min(91, 29) = 29 (CRITICAL)
- Final grade: **CRITICAL** (despite excellent content and structure)

**Rationale:** Even though the file has great content, 85% of its links are broken. Users following the links will fail. The file is not fit for use.

### Scenario 2: Gating NOT Triggered (No Critical Patterns)

File analysis:
- Structural score: 20/30 (some organizational issues)
- Content score: 35/50 (minimal examples, sparse API docs)
- Anti-Pattern score: 16/20 (some minor issues: no master index, no quick start)
- No critical patterns detected
- `is_gated`: False
- Composite score: 20 + 35 + 16 = 71 (STRONG)
- Final grade: **STRONG** (gating not applied)

**Rationale:** The file has problems, but they are not fundamental. It is usable, despite its shortcomings.

### Scenario 3: Already in CRITICAL Range

File analysis:
- Structural score: 5/30 (severe structural issues)
- Content score: 10/50 (almost no content)
- Anti-Pattern score: 8/20 (multiple deductions)
- STRUCTURE_CHAOS detected → **is_gated**: True
- Composite before gating: 5 + 10 + 8 = 23 (already CRITICAL)
- Composite after gating: min(23, 29) = 23 (unchanged)
- Final grade: **CRITICAL**

**Rationale:** Gating had no effect because the score was already below the cap. The file is CRITICAL for multiple reasons.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.5; four critical patterns defined per DECISION-016 |
