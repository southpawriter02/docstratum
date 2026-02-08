# DS-CS-001: Svelte — Exemplary

| Field | Value |
|-------|-------|
| **DS Identifier** | DS-CS-001 |
| **Status** | RATIFIED |
| **ASoT Version** | 1.0.0 |
| **Project** | Svelte |
| **Expected Total Score** | 92 |
| **Expected Grade** | Exemplary (90–100) |
| **Source URL** | https://svelte.dev/llms.txt |
| **Captured Date** | 2026-02-06 (v0.0.4b calibration) |
| **Provenance** | v0.0.4b §11.3 Gold Standard Calibration; v0.0.2c specimen analysis |

## Description

Svelte's llms.txt file is the highest-scoring specimen in the DocStratum calibration set. It represents the **Exemplary** tier — a file that not only follows the specification and community best practices but is actively optimized for LLM consumption. It serves as the primary reference point for "what a near-perfect llms.txt file looks like."

## Expected Per-Dimension Scores

| Dimension | Expected Points | Max Points | Percentage |
|-----------|----------------|------------|------------|
| Structural | ~28.5 | 30 | ~95% |
| Content | ~46.0 | 50 | ~92% |
| Anti-Pattern | ~17.5 | 20 | ~88% |
| **Total** | **~92** | **100** | **92%** |

## Per-Criterion Pass/Fail Expectations

### L0 Parseable Prerequisites

> **Note:** L0 criteria files will be defined in Phase C. All calibration specimens are expected to pass L0 — files that cannot be parsed are not published. Svelte passes all five L0 checks (valid UTF-8, non-empty, valid Markdown, ~4,200 tokens, LF endings).

### Structural Criteria

| DS Identifier | Expected Result | Notes |
|---------------|----------------|-------|
| DS-VC-STR-001 | PASS | H1 "Svelte" present |
| DS-VC-STR-002 | PASS | Only one H1 (no duplicates) |
| DS-VC-STR-003 | PASS | Blockquote present with meaningful description |
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
| DS-VC-CON-004 | PASS | All sections have content |
| DS-VC-CON-005 | PASS | No duplicate section names |
| DS-VC-CON-006 | PASS | Blockquote is substantive |
| DS-VC-CON-007 | PASS | Descriptions are unique (not formulaic) |
| DS-VC-CON-008 | SOFT FAIL | Some sections use non-canonical names |
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
| DS-VC-APD-008 | SOFT FAIL | Some jargon without definitions |

## Self-Test Usage

When the pipeline runs its calibration self-test (Stage 3 of the self-validation loop), it processes Svelte's llms.txt and compares:

1. `|actual_total - 92| <= tolerance` (default tolerance: ±3 points)
2. `actual_grade == QualityGrade.EXEMPLARY`
3. No critical anti-patterns detected

If any comparison fails, the pipeline reports a calibration drift warning.

## Staleness Risk

Svelte's llms.txt may change after the capture date. If the file is significantly modified, the expected scores may no longer be accurate. Re-validation should occur quarterly or when a calibration self-test fails.

## Change History

| ASoT Version | Date | Change |
|--------------|------|--------|
| 0.0.0-scaffold | 2026-02-08 | Initial draft — Phase A example file |
| 1.0.0 | 2026-02-08 | Phase E ratification — status DRAFT→RATIFIED, version 0.0.0-scaffold→1.0.0 |
