# DS-CS-004: Shadcn UI — Strong

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CS-004 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Project** | Shadcn UI |
| **Expected Total Score** | 89 |
| **Expected Grade** | Strong (70–89) |
| **Source URL** | https://ui.shadcn.com/llms.txt |
| **Captured Date** | 2026-02-06 (v0.0.4b calibration) |
| **Provenance** | v0.0.4b §11.3 Gold Standard Calibration; v0.0.2c specimen analysis |

## Description

Shadcn UI's llms.txt scores 89 points — exactly **1 point below the Exemplary threshold**. It represents the **upper boundary of the Strong tier** and serves as a critical validation specimen. The file demonstrates excellent content quality with clear component documentation and practical usage examples, but falls short of Exemplary due to minor structural imperfections or subtle anti-pattern presence. This specimen is essential for confirming that the 89→90 threshold correctly distinguishes Strong from Exemplary without false negatives.

## Expected Per-Dimension Scores

| Dimension | Expected Points | Max Points | Percentage |
|-----------|----------------|------------|------------|
| Structural | ~26 | 30 | ~87% |
| Content | ~44 | 50 | ~88% |
| Anti-Pattern | ~19 | 20 | ~95% |
| **Total** | **~89** | **100** | **89%** |

## Per-Criterion Pass/Fail Expectations

### L0 Parseable Prerequisites

> **Note:** L0 criteria files will be defined in Phase C. All calibration specimens are expected to pass L0 — files that cannot be parsed are not published. Shadcn UI passes all five L0 checks (valid UTF-8, non-empty, valid Markdown, proper token range, LF endings).

### Structural Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-STR-001 | PASS | H1 "Shadcn UI" present |
| DS-VC-STR-002 | PASS | Only one H1 (no duplicates) |
| DS-VC-STR-003 | PASS | Blockquote present with project description |
| DS-VC-STR-004 | SOFT FAIL | Some sections use non-canonical H2 naming |
| DS-VC-STR-005 | PASS | All links use valid Markdown format |
| DS-VC-STR-006 | PASS | No heading violations |
| DS-VC-STR-007 | SOFT FAIL | Minor section ordering deviations |
| DS-VC-STR-008 | PASS | No critical anti-patterns detected |
| DS-VC-STR-009 | PASS | No structural anti-patterns detected |

### Content Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-CON-001 | PASS | Links have descriptions |
| DS-VC-CON-002 | PASS | URLs resolve (at capture date) |
| DS-VC-CON-003 | PASS | No placeholder content |
| DS-VC-CON-004 | PASS | All sections have content |
| DS-VC-CON-005 | PASS | No duplicate section names |
| DS-VC-CON-006 | PASS | Blockquote is substantive |
| DS-VC-CON-007 | SOFT FAIL | Some component descriptions are formulaic |
| DS-VC-CON-008 | PASS | Section names generally follow canonical format |
| DS-VC-CON-009 | PASS | Has a Master Index equivalent |
| DS-VC-CON-010 | PASS | Contains code examples |
| DS-VC-CON-011 | PASS | Code blocks have language specifiers |
| DS-VC-CON-012 | PASS | Within Standard token budget tier |
| DS-VC-CON-013 | SOFT FAIL | No explicit version metadata |

### Anti-Pattern Detection Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-APD-001 | FAIL (INFO) | No LLM Instructions section (0% ecosystem adoption) |
| DS-VC-APD-002 | FAIL (INFO) | No structured concept definitions |
| DS-VC-APD-003 | FAIL (INFO) | No few-shot examples |
| DS-VC-APD-004 | PASS | No content anti-patterns detected |
| DS-VC-APD-005 | PASS | No strategic anti-patterns detected |
| DS-VC-APD-006 | PASS | Balanced token distribution |
| DS-VC-APD-007 | PASS | Primarily absolute URLs |
| DS-VC-APD-008 | PASS | Jargon is adequately defined |

## Self-Test Usage

When the pipeline runs its calibration self-test (Stage 3 of the self-validation loop), it processes Shadcn UI's llms.txt and compares:

1. `|actual_total - 89| <= tolerance` (default tolerance: ±3 points)
2. `actual_grade == QualityGrade.STRONG`
3. No critical anti-patterns detected

If any comparison fails, the pipeline reports a calibration drift warning. Shadcn UI serves as the upper-bound validator for the Strong tier and confirms the grade boundary at 89→90.

## Staleness Risk

Shadcn UI's llms.txt may change as the component library evolves and new components are added. The file structure should remain relatively stable, but incremental content updates are expected. Re-validation should occur quarterly or when a calibration self-test fails. Moderate risk of minor score drift due to component library expansion.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.7 |
