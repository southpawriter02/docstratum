# DS-VL-L3: Best Practices

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-VL-L3 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Level Number** | 3 |
| **Level Name** | Best Practices |
| **Enum Value** | `ValidationLevel.L3_BEST_PRACTICES` |
| **Question Answered** | "Does this file follow recommended documentation patterns?" |
| **Provenance** | v0.0.6 §3.4 (L3 Best Practice Checks); v0.0.4a §6 canonical ordering; v0.0.4b content best practices; v0.0.4c anti-pattern catalog; DECISION-010, DECISION-012, DECISION-013 |

## Description

Level 3 evaluates adherence to documentation best practices that go beyond basic structural and content correctness. After L2 confirms meaningful content exists, L3 asks: does this file follow the patterns that distinguish good documentation from great documentation? Does it use canonical section names? Does it include a Master Index for navigation? Are code examples present and properly annotated? Is the token budget respected?

L3 is the "quality differentiator" level. Files that reach L3 demonstrate intentional documentation design — they are not just structurally valid and content-complete, but thoughtfully organized following patterns derived from empirical analysis of 450+ llms.txt files (v0.0.2c). The best-performing files in the v0.0.2c audit (Svelte, Pydantic, Vercel SDK) all satisfy L3 criteria.

L3 also includes three Structural dimension criteria (STR-007 through STR-009) that validate structural best practices: canonical section ordering, absence of critical anti-patterns, and absence of structural anti-patterns. This cross-dimension presence reflects the fact that some best practices are structural in nature.

## Criteria at This Level

**Structural Dimension Criteria at L3:**

| DS Identifier | Platinum ID | Name | Weight | Dimension | Pass Type |
|---------------|-------------|------|--------|-----------|-----------|
| DS-VC-STR-007 | L3-06 | Canonical Section Ordering | 3/30 | Structural | SOFT |
| DS-VC-STR-008 | L3-09 | No Critical Anti-Patterns | 3/30 | Structural | HARD |
| DS-VC-STR-009 | L3-10 | No Structural Anti-Patterns | 2/30 | Structural | SOFT |

**Content Dimension Criteria at L3:**

| DS Identifier | Platinum ID | Name | Weight | Dimension | Pass Type |
|---------------|-------------|------|--------|-----------|-----------|
| DS-VC-CON-008 | L3-01 | Canonical Section Names | 5/50 | Content | SOFT |
| DS-VC-CON-009 | L3-02 | Master Index Present | 5/50 | Content | SOFT |
| DS-VC-CON-010 | L3-03 | Code Examples Present | 5/50 | Content | SOFT |
| DS-VC-CON-011 | L3-04 | Code Language Specifiers | 3/50 | Content | SOFT |
| DS-VC-CON-012 | L3-05 | Token Budget Respected | 4/50 | Content | SOFT |
| DS-VC-CON-013 | L3-07 | Version Metadata Present | 3/50 | Content | SOFT |

**Weight totals at this level:**

- Structural: 8 of 30 points (completing the structural dimension alongside L1's 22 points)
- Content: 25 of 50 points (completing the content dimension alongside L2's 25 points)
- Combined: 33 points across 9 criteria

**Pass Type breakdown:** 1 HARD (STR-008: No Critical Anti-Patterns), 8 SOFT. The single HARD criterion at L3 reflects the severity of critical anti-patterns — if any of the 4 critical anti-patterns (Ghost File, Structure Chaos, Encoding Disaster, Link Void) are detected, the structural gating rule caps the total score at 29.

> **Note on L3-08:** Platinum Standard criterion L3-08 ("Optional section used appropriately") was excluded per decision C-DEC-04. It is INFO-only and partially measurable, does not contribute to the 100-point score, and does not have a VC file. See DS-DC-I006 (OPTIONAL_SECTIONS_UNMARKED) for the informational diagnostic.

## Entry Conditions

L2 must be evaluated. All L1 HARD criteria must pass (L0 and L1 are prerequisites):

1. L0: File is parseable (valid encoding, non-empty, valid Markdown, within token limit, LF endings)
2. L1: File has structural skeleton (H1, no duplicate H1, H2 sections, valid links)
3. L2: Content quality criteria have been evaluated (SOFT failures permitted)

## Exit Criteria

L3 exit is gated by one HARD criterion and influenced by eight SOFT criteria:

**HARD gate (must pass):**

1. No critical anti-patterns detected (DS-VC-STR-008) — checks for AP-CRIT-001 through AP-CRIT-004

**SOFT criteria (evaluated, reduce score if failed):**

2. Sections use canonical names from the 11-name vocabulary — DS-VC-CON-008
3. A Master Index / Table of Contents section exists — DS-VC-CON-009
4. Code examples are present for technical projects — DS-VC-CON-010
5. Code blocks specify a language identifier — DS-VC-CON-011
6. File token count is within budget tier limits — DS-VC-CON-012
7. Version or date metadata is present — DS-VC-CON-013
8. Sections follow the canonical 10-step ordering — DS-VC-STR-007
9. No structural anti-patterns detected — DS-VC-STR-009

If the HARD gate fails (critical anti-pattern detected), the structural gating rule fires and the total score is capped at 29 regardless of other criteria.

## Diagnostic Codes at This Level

| DS Identifier | Severity | Fires When | Triggering Criterion |
|---------------|----------|------------|---------------------|
| DS-DC-W002 | WARNING | Section name is not one of the 11 canonical names | DS-VC-CON-008 |
| DS-DC-W008 | WARNING | Sections are not in canonical order | DS-VC-STR-007 |
| DS-DC-W009 | WARNING | No Master Index / Table of Contents section | DS-VC-CON-009 |
| DS-DC-W004 | WARNING | No code examples found | DS-VC-CON-010 |
| DS-DC-W005 | WARNING | Code blocks lack language specifiers | DS-VC-CON-011 |
| DS-DC-W010 | WARNING | File exceeds token budget for its tier | DS-VC-CON-012 |
| DS-DC-W007 | WARNING | No version or date metadata found | DS-VC-CON-013 |
| DS-DC-I006 | INFO | Optional sections not marked as such | N/A (excluded L3-08) |

> **Note:** DS-VC-STR-008 (No Critical Anti-Patterns) and DS-VC-STR-009 (No Structural Anti-Patterns) trigger diagnostic codes from the anti-pattern detection system rather than unique L3-specific codes. Critical anti-pattern detection triggers E003/E004/E005/E007/E008 level codes or structural scoring adjustments.

## Scoring Impact

L3 criteria complete both the **Structural dimension** (30 points) and the **Content dimension** (50 points):

- **Structural:** L3 adds 8 points to L1's 22 points, completing the 30-point structural total. The canonical ordering and anti-pattern checks ensure the file's structure follows established patterns.
- **Content:** L3 adds 25 points to L2's 25 points, completing the 50-point content total. The highest-weighted L3 content criteria are Canonical Section Names (5), Master Index Present (5), and Code Examples Present (5) — reflecting empirical evidence that these three features are the strongest predictors of documentation quality (v0.0.2c).

Key scoring insight: **Code Examples Present** (5 points) is one of the highest-weighted criteria across all dimensions because the v0.0.2c empirical audit found it has the strongest correlation with overall quality (r ~ 0.65). Projects with code examples scored on average 23 points higher than those without.

## Relationship to Other Levels

```
L0 (Parseable)
  └─► L1 (Structural)
       └─► L2 (Content Quality)
            └─► L3 (Best Practices) ← YOU ARE HERE
                 └─► L4 (DocStratum Extended) — requires L3 evaluation
```

L3 is the "quality gate" between adequate documentation and excellent documentation. Files achieving L3 are in the **STRONG** grade range (70–89 points), which means they follow established patterns and provide genuine value to LLM agents. The EXEMPLARY grade (90+) requires L4 features (LLM-specific optimizations).

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.1 |
