# DS-CS-003: Vercel AI SDK — Exemplary

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CS-003 |
| **Status** | DRAFT |
| **ASoT Version** | 0.0.0-scaffold |
| **Project** | Vercel AI SDK |
| **Expected Total Score** | 90 |
| **Expected Grade** | Exemplary (90–100) |
| **Source URL** | https://sdk.vercel.ai/llms.txt |
| **Captured Date** | 2026-02-06 (v0.0.4b calibration) |
| **Provenance** | v0.0.4b §11.3 Gold Standard Calibration; v0.0.2c specimen analysis |

## Description

Vercel AI SDK's llms.txt file ties with Pydantic at the **Exemplary threshold of 90 points**. It demonstrates well-organized framework-specific documentation with strong technical clarity and practical integration guidance. This specimen serves as a second calibration point at the Exemplary boundary, confirming that the ≥90 threshold correctly identifies excellent documentation without variation in scoring methodology. The file balances comprehensive API reference with clear, actionable examples.

## Expected Per-Dimension Scores

| Dimension | Expected Points | Max Points | Percentage |
|-----------|----------------|------------|------------|
| Structural | ~27 | 30 | ~90% |
| Content | ~45 | 50 | ~90% |
| Anti-Pattern | ~18 | 20 | ~90% |
| **Total** | **~90** | **100** | **90%** |

## Per-Criterion Pass/Fail Expectations

### L0 Parseable Prerequisites

> **Note:** L0 criteria files will be defined in Phase C. All calibration specimens are expected to pass L0 — files that cannot be parsed are not published. Vercel AI SDK passes all five L0 checks (valid UTF-8, non-empty, valid Markdown, proper token range, LF endings).

### Structural Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-STR-001 | PASS | H1 "Vercel AI SDK" present |
| DS-VC-STR-002 | PASS | Only one H1 (no duplicates) |
| DS-VC-STR-003 | PASS | Blockquote present with framework overview |
| DS-VC-STR-004 | PASS | All sections use H2 |
| DS-VC-STR-005 | PASS | All links use valid Markdown format |
| DS-VC-STR-006 | PASS | No heading violations |
| DS-VC-STR-007 | PASS | Sections follow canonical ordering |
| DS-VC-STR-008 | PASS | No critical anti-patterns detected |
| DS-VC-STR-009 | PASS | No structural anti-patterns detected |

### Content Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-CON-001 | PASS | Links have descriptions |
| DS-VC-CON-002 | PASS | URLs resolve (at capture date) |
| DS-VC-CON-003 | PASS | No placeholder content |
| DS-VC-CON-004 | PASS | All sections have substantive content |
| DS-VC-CON-005 | PASS | No duplicate section names |
| DS-VC-CON-006 | PASS | Blockquote is substantive |
| DS-VC-CON-007 | PASS | Descriptions are unique and specific |
| DS-VC-CON-008 | PASS | Section names follow canonical format |
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
| DS-VC-APD-006 | PASS | Well-balanced token distribution |
| DS-VC-APD-007 | PASS | Primarily absolute URLs |
| DS-VC-APD-008 | PASS | Jargon is defined in context |

## Self-Test Usage

When the pipeline runs its calibration self-test (Stage 3 of the self-validation loop), it processes Vercel AI SDK's llms.txt and compares:

1. `|actual_total - 90| <= tolerance` (default tolerance: ±3 points)
2. `actual_grade == QualityGrade.EXEMPLARY`
3. No critical anti-patterns detected

If any comparison fails, the pipeline reports a calibration drift warning. Vercel AI SDK provides independent confirmation that the Exemplary boundary is correctly calibrated.

## Staleness Risk

Vercel AI SDK's llms.txt may evolve as the framework develops and new features are released. The core structure should remain stable, but content additions are expected. Re-validation should occur quarterly or when a calibration self-test fails. Moderate risk of minor score drift due to active framework development.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase D.7 |
